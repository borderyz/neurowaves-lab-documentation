#!/usr/bin/env python3
"""
Validate BIDS datasets locally or from Box with minimal data transfer.

Modes:
  1) Local: --root <dir>  → validate each immediate subfolder as a dataset root.
  2) Box:   --box-folder-id <id> (+ BOX_CLIENT_SDK_CONFIG or --box-config)
            → mirror to --work-dir (skip .con, optional placeholders),
              validate, write per-dataset JSONs + root CSV, upload both.

Prereqs (CI):
  - npm install -g bids-validator
  - pip install "boxsdk[jwt]" pandas
"""

from __future__ import annotations
import argparse
import csv
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Optional, Tuple

# --- Box SDK imports (robust) ---
HAS_BOXSDK = True
try:
    from boxsdk import Client  # OK in v2/v3
    from boxsdk.auth.jwt_auth import JWTAuth  # canonical path for JWT auth
except Exception:
    HAS_BOXSDK = False
    Client = None  # type: ignore
    JWTAuth = None  # type: ignore

LOG = logging.getLogger("validate_box_bids")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# keep our INFO, mute Box/requests noise
for _name in (
    "boxsdk",                      # Box SDK
    "boxsdk.network.default_network",
    "urllib3",                     # requests' HTTP layer
    "requests.packages.urllib3",
    "chardet.charsetprober",
):
    lg = logging.getLogger(_name)
    lg.setLevel(logging.WARNING)
    lg.propagate = False


def _norm(s: str) -> str:
    return s.casefold()

def _check_validator_available() -> None:
    exe = shutil.which("bids-validator")
    if not exe:
        raise RuntimeError(
            "bids-validator not found on PATH. Install with: npm install -g bids-validator"
        )




def run_validator(ds: Path) -> Tuple[bool, dict]:
    """Run bids-validator on a dataset path and return (ok, normalized-json)."""
    _check_validator_available()
    cmd = ["bids-validator", str(ds), "--json", "--no-color"]
    LOG.info("Validating dataset: %s", ds)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    try:
        payload = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        payload = {"raw_stdout": stdout}

    issues = payload.get("issues", {}) if isinstance(payload, dict) else {}
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


# ----------------------- Box helpers -----------------------

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
        p = Path(config_path)
        if not p.exists():
            raise FileNotFoundError(f"Box config file not found: {p}")
        settings = json.loads(p.read_text(encoding="utf-8"))
    else:
        raise RuntimeError("Provide Box config via BOX_CLIENT_SDK_CONFIG or --box-config")

    for k in ("boxAppSettings", "enterpriseID"):
        if k not in settings:
            raise RuntimeError(f"Box JWT config missing key: '{k}'")

    auth = JWTAuth.from_settings_dictionary(settings)
    client = Client(auth)
    _ = client.user(user_id="me").get()  # prime / validate token
    return client


def mirror_box_folder(client: Client, folder_id: str, out_dir: Path,
                      skip_exts=(".con",), create_placeholders=True,
                      max_bytes: int | None = None,
                      exclude_top_level: Optional[set[str]] = None) -> None:

    exclude_top_level = { _norm(x) for x in (exclude_top_level or set()) }


    out_dir.mkdir(parents=True, exist_ok=True)
    root_folder = client.folder(folder_id=folder_id).get()
    LOG.info("Mirroring Box folder '%s' (%s) into %s", root_folder.name, folder_id, out_dir)

    def _walk(fid: str, local: Path, depth: int):
        local.mkdir(parents=True, exist_ok=True)
        offset, limit = 0, 1000
        while True:
            items = client.folder(fid).get_items(
                limit=limit, offset=offset, fields=["id", "name", "type", "size"]
            )
            count = 0
            for item in items:
                count += 1
                if item.type == "file":
                    ...
                elif item.type == "folder":
                    # If we're at the Box root of the dataset tree, optionally skip
                    if depth == 0 and exclude_top_level and _norm(item.name) in exclude_top_level:
                        LOG.info("Skipping excluded dataset during mirror: %s", local / item.name)
                        continue
                    _walk(item.id, local / item.name, depth + 1)
            if count < limit:
                break
            offset += limit

    _walk(folder_id, out_dir, depth=0)



def upload_summary_and_per_dataset_reports(client: Client, work_dir: Path, dest_folder_id: str) -> None:
    """
    Uploads:
      - work_dir/bids_validation_summary.csv  -> Box root (dest_folder_id)
      - work_dir/<dataset>/bids_validation_report.json -> Box/<dataset>/
    Creates subfolders on Box if needed. Does NOT upload other files.
    """
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


# ----------------------- Local validate (per-dataset JSON + root CSV) -----------------------

def validate_local_root(root: Path, exclude: list[str] | None = None) -> Path:
    """
    Validate each immediate subdir of `root` as a dataset.
    - Writes per-dataset JSON to <ds>/bids_validation_report.json
    - Writes a CSV summary to <root>/bids_validation_summary.csv
    Returns the summary CSV path.
    """
    exclude_norm = {_norm(x) for x in (exclude or [])}
    rows = []
    for ds in iter_immediate_subdirs(root):
        if _norm(ds.name) in exclude_norm:
            LOG.info("Skipping excluded dataset: %s", ds.name)
            continue

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

    summary_csv = root / "bids_validation_summary.csv"
    with open(summary_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["dataset","is_valid","n_errors","n_warnings","report_path"])
        w.writeheader()
        w.writerows(rows)
    LOG.info("Summary CSV: %s (datasets=%d)", summary_csv, len(rows))
    return summary_csv



# ----------------------- Main -----------------------

def main():
    ap = argparse.ArgumentParser(description="Validate BIDS datasets (local or Box).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--root", type=Path, help="Local root containing dataset subfolders")
    g.add_argument("--box-folder-id", type=str, help="Box folder ID to mirror & validate")

    ap.add_argument("--work-dir", type=Path, default=Path("datasets"),
                    help="Local workdir for mirrored datasets (Box mode)")

    ap.add_argument("--box-config", type=Path, default=None,
                    help="Path to Box JWT config JSON (alternative to env BOX_CLIENT_SDK_CONFIG)")

    ap.add_argument("--no-con-placeholders", action="store_true",
                    help="Do NOT create .con placeholders (skip .con files entirely)")

    ap.add_argument(
        "--max-bytes",
        type=int,
        default=2_000_000,  # 5 MB default; tune as you like
        help="If a file is larger than this, do not download it (create placeholder instead).",
    )

    ap.add_argument(
        "--exclude-dataset",
        action="append",
        default=["kidlang"],
        help="Dataset folder name(s) to exclude from validation. "
             "Can be repeated, e.g. --exclude-dataset sub-01 --exclude-dataset sub-99"
    )

    ap.add_argument(
        "--skip-ext",
        action="append",
        default=[".con", ".fif", ".mgz", ".nii", ".nii.gz", ".mat", ".mrk", ".ds", ".stc"],
        help="Extra file extensions to skip downloading (repeatable).",
    )


    args = ap.parse_args()

    # Local mode
    if args.root:
        LOG.info("Running in LOCAL mode")
        summary_csv = validate_local_root(args.root, exclude=args.exclude_dataset)
        LOG.info("Done. Summary: %s", summary_csv)
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
        max_bytes=args.max_bytes,
        exclude_top_level=set(args.exclude_dataset or []),
    )

    # Per-dataset JSONs + root CSV under work_dir
    summary_csv = validate_local_root(args.work_dir, exclude=args.exclude_dataset)

    # Upload ONLY the summary CSV + per-dataset JSONs back to Box
    upload_summary_and_per_dataset_reports(client, args.work_dir, dest_folder_id=args.box_folder_id)
    LOG.info("Uploaded summary + per-dataset reports to Box folder %s", args.box_folder_id)


if __name__ == "__main__":
    main()
