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

# --- Box SDK imports (robust) ---
HAS_BOXSDK = True
try:
    from boxsdk import Client  # OK in v2/v3
    from boxsdk.auth.jwt_auth import JWTAuth  # canonical path for JWT auth
except Exception as e:
    HAS_BOXSDK = False
    Client = None  # type: ignore
    JWTAuth = None  # type: ignore





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
    if not HAS_BOXSDK or Client is None or JWTAuth is None:
        raise RuntimeError(
            "boxsdk not available or was shadowed. Ensure it is installed "
            "and no local module named 'boxsdk' shadows the package."
        )

def _box_client_from_config(config_json_str: Optional[str], config_path: Optional[Path]) -> Client:
    _require_boxsdk()

    if config_json_str:
        try:
            settings = json.loads(config_json_str)
        except json.JSONDecodeError as e:
            raise RuntimeError("BOX_CLIENT_SDK_CONFIG is not valid JSON") from e
    elif config_path:
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Box config file not found: {config_path}")
        settings = json.loads(Path(config_path).read_text(encoding="utf-8"))
    else:
        raise RuntimeError(
            "Box config not provided. Set BOX_CLIENT_SDK_CONFIG secret or pass --box-config"
        )

    # Sanity check a couple of keys we expect in JWT app config
    required_keys = ["boxAppSettings", "enterpriseID"]
    for k in required_keys:
        if k not in settings:
            raise RuntimeError(f"Box JWT config missing key: '{k}'")

    auth = JWTAuth.from_settings_dictionary(settings)  # type: ignore[attr-defined]
    client = Client(auth)
    _ = client.user(user_id="me").get()  # prime / validate token
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


def validate_local_root(root: Path, reports_dir: Path | None = None) -> None:
    """
    Validate each immediate subdir of `root` as a dataset.
    - Writes per-dataset JSON to <ds>/bids_validation_report.json
    - Writes a CSV summary to <root>/bids_validation_summary.csv
    """
    rows = []
    for ds in iter_immediate_subdirs(root):
        ok, report = run_validator(ds)
        per_ds_json = ds / "bids_validation_report.json"
        with open(per_ds_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        rows.append({
            "dataset": ds.name,
            "is_valid": ok,
            "n_errors": report["summary"]["n_errors"],
            "n_warnings": report["summary"]["n_warnings"],
            "report_path": str(per_ds_json),
        })
        LOG.info("Wrote: %s (ok=%s)", per_ds_json, ok)

    # write summary CSV next to datasets
    import csv
    summary_csv = root / "bids_validation_summary.csv"
    with open(summary_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["dataset","is_valid","n_errors","n_warnings","report_path"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    LOG.info("Summary CSV: %s (datasets=%d)", summary_csv, len(rows))


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


def upload_summary_and_per_dataset_reports(client: Client, work_dir: Path, dest_folder_id: str):
    """
    Uploads:
      - work_dir/bids_validation_summary.csv  -> Box root (dest_folder_id)
      - work_dir/<dataset>/bids_validation_report.json -> Box/<dataset>/
    Creates subfolders on Box if needed. Does NOT upload other files.
    """
    # Reuse a tiny inner helper to ensure subfolders exist
    def get_or_create_child_folder(parent_id: str, name: str) -> str:
        items = client.folder(parent_id).get_items(limit=1000, fields=["id", "name", "type"])
        for it in items:
            if it.type == "folder" and it.name == name:
                return it.id
        return client.folder(parent_id).create_subfolder(name).id

    # 1) Upload summary CSV to Box root
    summary_csv = work_dir / "bids_validation_summary.csv"
    if summary_csv.exists():
        try:
            client.folder(dest_folder_id).upload(str(summary_csv), file_name=summary_csv.name)
        except Exception as e:
            if "item_name_in_use" in str(e):
                # overwrite by new version
                items = client.folder(dest_folder_id).get_items(limit=1000, fields=["id","name","type"])
                file_id = next((it.id for it in items if it.type == "file" and it.name == summary_csv.name), None)
                if file_id:
                    client.file(file_id).update_contents(str(summary_csv))
                else:
                    raise
            else:
                raise

    # 2) Upload each per-dataset JSON into Box/<dataset>/
    for ds in iter_immediate_subdirs(work_dir):
        report = ds / "bids_validation_report.json"
        if not report.exists():
            continue
        ds_box_id = get_or_create_child_folder(dest_folder_id, ds.name)
        try:
            client.folder(ds_box_id).upload(str(report), file_name=report.name)
        except Exception as e:
            if "item_name_in_use" in str(e):
                items = client.folder(ds_box_id).get_items(limit=1000, fields=["id","name","type"])
                file_id = next((it.id for it in items if it.type == "file" and it.name == report.name), None)
                if file_id:
                    client.file(file_id).update_contents(str(report))
                else:
                    raise
            else:
                raise


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


    import sys, pkgutil
    LOG.info("Python: %s", sys.version)
    LOG.info("Sys.path: %s", sys.path)
    try:
        import boxsdk as _bx
        LOG.info("boxsdk module file: %s", getattr(_bx, "__file__", "unknown"))
    except Exception as e:
        LOG.warning("boxsdk import failed: %s", e)

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

    # --- after mirror_box_folder(...)

    # Validate each dataset root = immediate subfolder under work_dir
    rows = []
    for ds in iter_immediate_subdirs(args.work_dir):
        ok, report = run_validator(ds)
        per_ds_json = ds / "bids_validation_report.json"
        with open(per_ds_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        LOG.info("Wrote: %s (ok=%s)", per_ds_json, ok)
        rows.append({
            "dataset": ds.name,
            "is_valid": ok,
            "n_errors": report["summary"]["n_errors"],
            "n_warnings": report["summary"]["n_warnings"],
            "report_path": str(per_ds_json),
        })

    # summary CSV at the parent (work_dir)
    # Per-dataset JSONs + root CSV under work_dir
    summary_csv = validate_local_root(args.work_dir)

    # Upload summary + per-dataset logs (and nothing else)
    upload_summary_and_per_dataset_reports(client, args.work_dir, dest_folder_id=args.box_folder_id)
    LOG.info("Uploaded summary + per-dataset reports to Box folder %s", args.box_folder_id)

    # ---- Upload back to Box (optional) ----
    # 1) Upload the summary CSV to the root Box folder

    # (This will create/update 'bids_validation_summary.csv' in the Box folder.)

    # 2) If you also want per-dataset JSON uploaded in-place under the same Box folder,
    #    you can upload ONLY the matching files by reusing upload_folder_to_box, which
    #    mirrors folder structure and uploads files it sees. To avoid sending everything,
    #    do a small copy into a temp dir or write a filter-uploader. For now we leave JSON local.

    # Validate each dataset root = immediate subfolder under work_dir




if __name__ == "__main__":
    main()
