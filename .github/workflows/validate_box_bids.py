#!/usr/bin/env python3
"""
Validate BIDS datasets locally or from Box with minimal data transfer.

Modes:
  1) Local: provide --root to validate each immediate subfolder as a dataset root.
  2) Box:   provide --box-folder-id (and Box JWT config) to mirror a Box folder
             into --work-dir, skip .con files but create zero-byte placeholders,
             validate, then upload JSON reports back to the same Box folder.

Prereqs in CI:
  - npm install -g bids-validator
  - pip install boxsdk pandas

Box config:
  - Provide via env var BOX_CLIENT_SDK_CONFIG (full JSON) or --box-config path.

Usage:
  # Local mode
  python validate_box_bids.py --root /path/to/datasets --reports-dir reports

  # Box mode
  python validate_box_bids.py --box-folder-id 258911132863 --work-dir ./datasets --reports-dir reports
"""

from __future__ import annotations
import argparse
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Iterable, Optional, Tuple

# Optional import for Box mode (only needed if --box-folder-id is used)
try:
    from boxsdk import JWTAuth, Client
    HAS_BOXSDK = True
except Exception:
    HAS_BOXSDK = False

LOG = logging.getLogger("validate_box_bids")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_validator(ds: Path) -> Tuple[bool, dict]:
    """Run bids-validator on a dataset path and return (ok, normalized-json)."""
    cmd = ["bids-validator", str(ds), "--json", "--no-color"]
    LOG.info("Validating dataset: %s", ds)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    payload = {}
    try:
        payload = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        payload = {"raw_stdout": stdout}

    # Normalize a little
    issues = payload.get("issues", {})
    errors = issues.get("errors", []) if isinstance(issues, dict) else []
    warnings = issues.get("warnings", []) if isinstance(issues, dict) else []

    normalized = {
        "summary": {
            "dataset_path": str(ds),
            "bids_validator_version": payload.get("version"),
            "n_errors": len(errors),
            "n_warnings": len(warnings),
            "stderr": stderr or None,
            "is_valid": proc.returncode == 0,
            "validator_returncode": proc.returncode,
        },
        "issues": (errors or []) + (warnings or []),
    }
    return proc.returncode == 0, normalized


def iter_immediate_subdirs(root: Path) -> Iterable[Path]:
    for p in sorted(root.iterdir()):
        if p.is_dir():
            yield p


# -----------------------
# Box helpers (optional)
# -----------------------

def _require_boxsdk():
    if not HAS_BOXSDK:
        raise RuntimeError("boxsdk not installed. Run: pip install boxsdk")

def _box_client_from_config(config_json_str: Optional[str], config_path: Optional[Path]) -> Client:
    _require_boxsdk()
    if config_json_str:
        settings = json.loads(config_json_str)
        auth = JWTAuth.from_settings_dictionary(settings)
    elif config_path:
        auth = JWTAuth.from_settings_file(str(config_path))
    else:
        raise ValueError("Provide Box config via env BOX_CLIENT_SDK_CONFIG or --box-config")
    client = Client(auth)
    # prime access token
    _ = client.user(user_id="me").get()
    return client

def mirror_box_folder(client: Client, folder_id: str, out_dir: Path, skip_exts=(".con",), create_placeholders=True):
    """
    Recursively mirror Box folder -> local out_dir.
    Skip downloading files with extensions in skip_exts; if create_placeholders=True,
    create zero-byte files for skipped names (to satisfy BIDS existence checks).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    root_folder = client.folder(folder_id=folder_id).get()
    LOG.info("Mirroring Box folder '%s' (%s) into %s", root_folder.name, folder_id, out_dir)

    def _walk(fid: str, local: Path):
        local.mkdir(parents=True, exist_ok=True)
        # pagination
        offset = 0
        limit = 1000
        while True:
            items = client.folder(fid).get_items(limit=limit, offset=offset, fields=["id", "name", "type"])
            count = 0
            for item in items:
                count += 1
                if item.type == "file":
                    name = item.name
                    ext = Path(name).suffix.lower()
                    tgt = local / name
                    if ext in skip_exts:
                        LOG.info("Placeholder for large raw: %s", tgt)
                        if create_placeholders:
                            tgt.touch(exist_ok=True)  # zero-byte placeholder
                        # else: skip entirely
                    else:
                        LOG.info("Downloading: %s", tgt)
                        with open(tgt, "wb") as fh:
                            client.file(item.id).download_to(fh)
                elif item.type == "folder":
                    _walk(item.id, local / item.name)
            if count < limit:
                break
            offset += limit

    _walk(folder_id, out_dir)


def upload_folder_to_box(client: Client, local_dir: Path, dest_folder_id: str, overwrite=True):
    """
    Upload all files under local_dir to dest_folder_id (flat or nested mirrored structure).
    This simple uploader keeps directory structure by creating subfolders on demand.
    """
    def get_or_create_child_folder(parent_id: str, name: str) -> str:
        # search existing
        items = client.folder(parent_id).get_items(limit=1000, fields=["id", "name", "type"])
        for it in items:
            if it.type == "folder" and it.name == name:
                return it.id
        # create
        created = client.folder(parent_id).create_subfolder(name)
        return created.id

    for path in sorted(local_dir.rglob("*")):
        if path.is_file():
            rel = path.relative_to(local_dir)
            parts = rel.parts
            parent_id = dest_folder_id
            # walk/ensure folders
            for folder_name in parts[:-1]:
                parent_id = get_or_create_child_folder(parent_id, folder_name)
            fname = parts[-1]
            # try upload (handle overwrite by new version if exists)
            try:
                LOG.info("Uploading report: %s -> folder %s", rel, parent_id)
                client.folder(parent_id).upload(str(path), file_name=str(fname))
            except Exception as e:
                if overwrite and "item_name_in_use" in str(e):
                    # upload new version
                    # find the file id first
                    items = client.folder(parent_id).get_items(limit=1000, fields=["id","name","type"])
                    file_id = None
                    for it in items:
                        if it.type == "file" and it.name == fname:
                            file_id = it.id
                            break
                    if file_id:
                        LOG.info("Uploading new version for %s", rel)
                        client.file(file_id).update_contents(str(path))
                    else:
                        raise
                else:
                    raise


# -----------------------
# Main orchestration
# -----------------------

def validate_local_root(root: Path, reports_dir: Path) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    for ds in iter_immediate_subdirs(root):
        ok, report = run_validator(ds)
        out = reports_dir / f"{ds.name}_validation_report.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        LOG.info("Wrote: %s (ok=%s)", out, ok)

def main():
    ap = argparse.ArgumentParser(description="Validate BIDS datasets (local or Box).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--root", type=Path, help="Local root containing dataset subfolders")
    g.add_argument("--box-folder-id", type=str, help="Box folder ID to mirror & validate")

    ap.add_argument("--work-dir", type=Path, default=Path("datasets"),
                    help="Local workdir for mirrored datasets (Box mode)")
    ap.add_argument("--reports-dir", type=Path, default=Path("reports"),
                    help="Where to write JSON reports")
    ap.add_argument("--box-config", type=Path, default=None,
                    help="Path to Box JWT config JSON (alternative to env BOX_CLIENT_SDK_CONFIG)")
    ap.add_argument("--no-con-placeholders", action="store_true",
                    help="Do NOT create .con placeholders (skip .con files entirely)")
    ap.add_argument("--skip-ext", action="append", default=[".con"],
                    help="Extra file extensions to skip downloading (repeatable). Default: .con")
    args = ap.parse_args()

    if args.root:
        LOG.info("Running in LOCAL mode")
        validate_local_root(args.root, args.reports_dir)
        return

    # Box mode
    LOG.info("Running in BOX mode (folder %s)", args.box_folder_id)
    config_json_str = os.environ.get("BOX_CLIENT_SDK_CONFIG")
    client = _box_client_from_config(config_json_str, args.box_config)

    args.work_dir.mkdir(parents=True, exist_ok=True)
    mirror_box_folder(
        client,
        args.box_folder_id,
        args.work_dir,
        skip_exts=tuple(s.lower() for s in args.skip_ext),
        create_placeholders=(not args.no_con_placeholders),
    )

    # Validate each dataset root = immediate subfolder under work_dir
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    for ds in iter_immediate_subdirs(args.work_dir):
        ok, report = run_validator(ds)
        out = args.reports_dir / f"{ds.name}_validation_report.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        LOG.info("Wrote: %s (ok=%s)", out, ok)

    # Upload reports back to the same Box folder
    upload_folder_to_box(client, args.reports_dir, dest_folder_id=args.box_folder_id, overwrite=True)
    LOG.info("Uploaded reports to Box folder %s", args.box_folder_id)


if __name__ == "__main__":
    main()
