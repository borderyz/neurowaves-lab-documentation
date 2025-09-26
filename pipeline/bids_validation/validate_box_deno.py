"""
Validate BIDS datasets locally or from Box with minimal data transfer using the
Deno-based BIDS validator (jsr:@bids/validator).

Modes:
  1) Local: --root <dir>  → validate each immediate subfolder as a dataset root.
  2) Box:   --box-folder-id <id> (+ BOX_CLIENT_SDK_CONFIG or --box-config)
            → mirror to --work-dir (skip large/known-raws with placeholders),
              validate, write per-dataset JSONs, and upload as we go.

Prereqs (CI):
  - Install Deno (no Node/npm needed)
  - pip install "boxsdk[jwt]" pandas
"""


from __future__ import annotations
import argparse
import csv
import json
import logging
import os
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


# add near the top
from typing import Iterable




import shutil
import subprocess


def _append_summary_row(summary_csv: Path, row: dict, header: list[str]) -> None:
    """Append one row to the summary CSV, creating it with header if needed (atomic-ish)."""
    summary_csv.parent.mkdir(parents=True, exist_ok=True)
    exists = summary_csv.exists()

    # write/append
    with open(summary_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        if not exists:
            w.writeheader()
        w.writerow(row)


def _get_or_create_child_folder_cached(client: Client):
    """Return a closure get_or_create_child_folder(parent_id, name) with an in-memory cache."""
    folder_cache: dict[str, dict[str, str]] = {}

    def get_or_create_child_folder(parent_id: str, name: str) -> str:
        bucket = folder_cache.setdefault(parent_id, {})
        if name in bucket:
            return bucket[name]
        items = client.folder(parent_id).get_items(limit=1000, fields=["id", "name", "type"])
        for it in items:
            if it.type == "folder" and it.name == name:
                bucket[name] = it.id
                return it.id
        new_id = client.folder(parent_id).create_subfolder(name).id
        bucket[name] = new_id
        return new_id

    return get_or_create_child_folder

def iter_box_top_level_datasets(client: Client, root_folder_id: str, exclude: set[str] | None = None):
    """Yield (name, id) for each top-level folder under the Box root, honoring exclude (case-insensitive)."""
    exclude_norm = { (x or "").casefold() for x in (exclude or set()) }
    offset, limit = 0, 1000
    while True:
        items = client.folder(root_folder_id).get_items(limit=limit, offset=offset, fields=["id","name","type"])
        count = 0
        for it in items:
            count += 1
            if it.type == "folder":
                if it.name.casefold() in exclude_norm:
                    LOG.info("Skipping excluded dataset at Box root: %s", it.name)
                    continue
                yield it.name, it.id
        if count < limit:
            break
        offset += limit


def mirror_validate_upload_one_dataset(
    client: Client,
    box_dataset_id: str,
    box_dataset_name: str,
    work_dir: Path,
    dest_folder_id: str,
    skip_exts: tuple[str, ...],
    create_placeholders: bool,
    max_bytes: Optional[int],
    bidsignore_template: Optional[Path],
    get_or_create_child_folder,  # closure from _get_or_create_child_folder_cached
    summary_csv: Path,
    placeholder_size: int,
):
    # mirror only this dataset into work_dir/<dataset>
    local_ds = work_dir / box_dataset_name
    LOG.info("Mirroring single dataset: %s (%s) -> %s", box_dataset_name, box_dataset_id, local_ds)
    mirror_box_folder(
        client,
        box_dataset_id,
        local_ds,
        skip_exts=skip_exts,
        create_placeholders=create_placeholders,
        max_bytes=max_bytes,
        exclude_top_level=None,  # not used for nested walk
        placeholder_size=placeholder_size,  # ← new
            )

    # ensure .bidsignore, validate, write report
    ensure_bidsignore(local_ds, bidsignore_template)
    ok, report = run_validator(local_ds)
    per_ds_json = local_ds / "bids_validation_report.json"
    with open(per_ds_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    LOG.info("Wrote report: %s (ok=%s)", per_ds_json, ok)

    # upload JSON to Box/<dataset> immediately
    ds_box_id = get_or_create_child_folder(dest_folder_id, box_dataset_name)
    _upload_or_update_file(client, ds_box_id, per_ds_json, per_ds_json.name)

    # append & upload summary immediately
    row = {
        "dataset": box_dataset_name,
        "is_valid": ok,
        "n_errors": report["summary"]["n_errors"],
        "n_warnings": report["summary"]["n_warnings"],
        "report_path": str(per_ds_json),
    }
    _append_summary_row(summary_csv, row, ["dataset","is_valid","n_errors","n_warnings","report_path"])
    _upload_or_update_file(client, dest_folder_id, summary_csv, summary_csv.name)



def validate_and_upload_streaming(
    client: Client,
    work_dir: Path,
    dest_folder_id: str,
    exclude: list[str] | None = None,
    bidsignore_template: Optional[Path] = None,
) -> Path:
    """
    For each dataset dir under work_dir:
      - ensure .bidsignore from template
      - run validator
      - write per-dataset JSON
      - upload JSON immediately to Box/<dataset>/
      - append one row to root summary CSV
      - upload/update summary CSV immediately to Box root
    """
    exclude_norm = { (x or "").casefold() for x in (exclude or []) }
    header = ["dataset", "is_valid", "n_errors", "n_warnings", "report_path"]
    summary_csv = work_dir / "bids_validation_summary.csv"

    get_or_create = _get_or_create_child_folder_cached(client)

    # pre-cache the Deno validator once
    _ensure_deno_validator_cached()

    total = 0
    for ds in iter_immediate_subdirs(work_dir):
        if ds.name.casefold() in exclude_norm:
            LOG.info("Skipping excluded dataset: %s", ds.name)
            continue

        total += 1
        # 1) make sure .bidsignore is in place
        ensure_bidsignore(ds, bidsignore_template)

        # 2) validate
        ok, report = run_validator(ds)

        # 3) write JSON report
        per_ds_json = ds / "bids_validation_report.json"
        with open(per_ds_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        LOG.info("Wrote: %s (ok=%s)", per_ds_json, ok)

        # 4) upload JSON to Box/<dataset>/
        ds_box_id = get_or_create(dest_folder_id, ds.name)
        _upload_or_update_file(client, ds_box_id, per_ds_json, per_ds_json.name)

        # 5) append one row locally
        row = {
            "dataset": ds.name,
            "is_valid": ok,
            "n_errors": report["summary"]["n_errors"],
            "n_warnings": report["summary"]["n_warnings"],
            "report_path": str(per_ds_json),
        }
        _append_summary_row(summary_csv, row, header)

        # 6) upload/update the CSV at Box root right away
        _upload_or_update_file(client, dest_folder_id, summary_csv, summary_csv.name)

    LOG.info("Streaming validation complete. Summary CSV: %s (datasets=%d)", summary_csv, total)
    return summary_csv



def _ensure_deno_validator_cached() -> None:
    """Pre-cache the BIDS validator so deno run is faster for multiple datasets."""
    deno = shutil.which("deno")
    if not deno:
        raise RuntimeError("'deno' not found on PATH. Install Deno first.")
    # No permission flags needed for `deno cache`
    subprocess.run([deno, "cache", "jsr:@bids/validator"], check=True)

def _validator_cmd(ds: Path) -> list[str]:
    """Deno-only validator invocation."""
    deno = shutil.which("deno")
    if not deno:
        raise RuntimeError("'deno' not found on PATH. Install Deno first.")
    # Permissions: -E allow-env, -R allow-read, -W allow-write, -N allow-net
    return [deno, "run", "-ERWN", "jsr:@bids/validator", str(ds), "--json", "--no-color"]

def _split_issues(payload):
    """Return (errors, warnings) from multiple possible validator JSON shapes."""
    errors, warnings = [], []
    if isinstance(payload, dict):
        issues = payload.get("issues")
        if isinstance(issues, dict):
            errors = issues.get("errors") or []
            warnings = issues.get("warnings") or []
        elif isinstance(issues, list):
            for it in issues:
                if (it or {}).get("severity") == "error":
                    errors.append(it)
                else:
                    warnings.append(it)
        else:
            # older/newer shapes
            errors = payload.get("errors") or []
            warnings = payload.get("warnings") or []
    elif isinstance(payload, list):
        # whole payload is a list of issues
        for it in payload:
            if (it or {}).get("severity") == "error":
                errors.append(it)
            else:
                warnings.append(it)
    return errors, warnings

def run_validator(ds: Path) -> Tuple[bool, dict]:
    cmd = _validator_cmd(ds)
    LOG.info("Validating dataset: %s", ds)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    try:
        payload = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        payload = {"raw_stdout": stdout}

    version = (
        (payload.get("validator") or {}).get("version")
        or (payload.get("summary") or {}).get("validator", {}).get("version")
        or payload.get("version")
    )

    errors, warnings = _split_issues(payload)

    normalized = {
        "summary": {
            "dataset_path": str(ds),
            "bids_validator_version": version,
            "n_errors": len(errors),
            "n_warnings": len(warnings),
            "stderr": stderr or None,
            "is_valid": proc.returncode == 0,
            "validator_returncode": proc.returncode,
        },
        "issues": (errors or []) + (warnings or []),
        # keep full payload + raw streams for debugging
        "validator_raw": {
            "stdout": stdout[:200000],  # cap to avoid huge files
            "stderr": stderr[:200000],
            "parsed": payload,
        },
    }
    return proc.returncode == 0, normalized




def _read_nonempty_lines(p: Path) -> list[str]:
    return [ln.rstrip("\n") for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]

def ensure_bidsignore(ds: Path, template_path: Optional[Path]) -> None:
    """Ensure ds/.bidsignore contains all entries from template_path (append missing)."""
    if not template_path:
        return
    if not template_path.exists():
        LOG.warning("bidsignore template not found: %s", template_path)
        return

    target = ds / ".bidsignore"
    tpl_lines = _read_nonempty_lines(template_path)

    if not target.exists():
        target.write_text("\n".join(tpl_lines) + "\n", encoding="utf-8")
        LOG.info("Created .bidsignore in %s from template (%d line(s))", ds.name, len(tpl_lines))
        return

    have = set(_read_nonempty_lines(target))
    missing = [ln for ln in tpl_lines if ln not in have]
    if missing:
        with open(target, "a", encoding="utf-8") as f:
            f.write("\n# --- added by validate_box_deno.py ---\n")
            for ln in missing:
                f.write(ln + "\n")
        LOG.info("Updated .bidsignore in %s (+%d line(s))", ds.name, len(missing))



def _norm(s: str) -> str:
    return s.casefold()









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
                      exclude_top_level: Optional[set[str]] = None,
                      placeholder_size: int = 4096) -> None:

    exclude_top_level = { (x or "").casefold() for x in (exclude_top_level or set()) }

    out_dir.mkdir(parents=True, exist_ok=True)
    root_folder = client.folder(folder_id=folder_id).get()
    LOG.info("Mirroring Box folder '%s' (%s) into %s", root_folder.name, folder_id, out_dir)

    def _walk(fid: str, local: Path, depth: int):
        local.mkdir(parents=True, exist_ok=True)
        offset, limit = 0, 1000
        downloaded = 0
        placeholders = 0
        skipped = 0

        while True:
            items = client.folder(fid).get_items(
                limit=limit, offset=offset, fields=["id", "name", "type", "size"]
            )
            count = 0
            for item in items:
                count += 1
                if item.type == "file":
                    name = item.name
                    tgt = local / name
                    size = getattr(item, "size", None)
                    lname = name.lower()
                    skip_exts_lc = tuple(s.lower() for s in skip_exts)
                    skip_by_ext = any(lname.endswith(s) for s in skip_exts_lc)
                    skip_by_size = (max_bytes is not None and
                                    isinstance(size, int) and size > max_bytes)

                    if skip_by_ext or skip_by_size:
                        reason = "ext" if skip_by_ext else f"size>{max_bytes}"
                        if create_placeholders:
                            LOG.info("Placeholder for large/raw (%s): %s (%d bytes)", reason, tgt, placeholder_size)
                            tgt.parent.mkdir(parents=True, exist_ok=True)
                            if placeholder_size > 0:
                                # write deterministic, low-entropy bytes (not all-zero to avoid some heuristics)
                                chunk = (b"BIDS-PLACEHOLDER\n" * ((placeholder_size // 18) + 1))[:placeholder_size]
                                with open(tgt, "wb") as fh:
                                    fh.write(chunk)
                            else:
                                tgt.touch(exist_ok=True)  # legacy: 0-byte
                            placeholders += 1
                        else:
                            LOG.info("Skipping download (%s): %s", reason, tgt)
                            skipped += 1
                        continue

                    LOG.info("Downloading: %s", tgt)
                    tgt.parent.mkdir(parents=True, exist_ok=True)
                    with open(tgt, "wb") as fh:
                        client.file(item.id).download_to(fh)
                    downloaded += 1

                elif item.type == "folder":
                    # skip excluded top-level dataset folders
                    if depth == 0 and exclude_top_level and item.name.casefold() in exclude_top_level:
                        LOG.info("Skipping excluded dataset during mirror: %s", local / item.name)
                        continue
                    _walk(item.id, local / item.name, depth + 1)

            if count < limit:
                break
            offset += limit

        # brief per-folder summary
        if downloaded or placeholders or skipped:
            LOG.info("Mirror summary for %s  downloaded=%d  placeholders=%d  skipped=%d",
                     local, downloaded, placeholders, skipped)

    _walk(folder_id, out_dir, depth=0)




def upload_summary_and_per_dataset_reports(client: Client, work_dir: Path, dest_folder_id: str) -> None:
    """
    Uploads:
      - work_dir/bids_validation_summary.csv      -> Box root
      - work_dir/<dataset>/bids_validation_report.json -> Box/<dataset>/
    """
    folder_cache: dict[str, dict[str, str]] = {}  # parent_id -> {name: id}

    def get_or_create_child_folder(parent_id: str, name: str) -> str:
        bucket = folder_cache.setdefault(parent_id, {})
        if name in bucket:
            return bucket[name]
        items = client.folder(parent_id).get_items(limit=1000, fields=["id", "name", "type"])
        for it in items:
            if it.type == "folder" and it.name == name:
                bucket[name] = it.id
                return it.id
        new_id = client.folder(parent_id).create_subfolder(name).id
        bucket[name] = new_id
        return new_id

    # 1) summary
    summary_csv = work_dir / "bids_validation_summary.csv"
    _upload_or_update_file(client, dest_folder_id, summary_csv, summary_csv.name)

    # 2) per-dataset JSONs
    for ds in iter_immediate_subdirs(work_dir):
        report = ds / "bids_validation_report.json"
        if report.exists():
            ds_box_id = get_or_create_child_folder(dest_folder_id, ds.name)
            _upload_or_update_file(client, ds_box_id, report, report.name)





# ----------------------- Local validate (per-dataset JSON + root CSV) -----------------------

def validate_local_root(root: Path, exclude: list[str] | None = None, bidsignore_template: Optional[Path] = None) -> Path:
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

        # ensure .bidsignore exists/updated BEFORE running validator
        ensure_bidsignore(ds, bidsignore_template)

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



from boxsdk.exception import BoxAPIException

def _upload_or_update_file(client, parent_id: str, local_path: Path, fname: str) -> None:
    if not local_path.exists():
        LOG.info("Skip upload (missing): %s", local_path)
        return
    try:
        client.folder(parent_id).upload(str(local_path), file_name=fname)
        LOG.info("Uploaded: %s -> folder %s", fname, parent_id)
    except BoxAPIException as e:
        # Box sends 409 + code="item_name_in_use" if the name already exists
        if e.status == 409 and getattr(e, "code", "") == "item_name_in_use":
            items = client.folder(parent_id).get_items(limit=1000, fields=["id","name","type"])
            file_id = next((it.id for it in items if it.type == "file" and it.name == fname), None)
            if not file_id:
                raise  # unexpected; bubble up
            client.file(file_id).update_contents(str(local_path))
            LOG.info("Uploaded new version: %s -> folder %s", fname, parent_id)
        else:
            raise



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
    ap.add_argument("--max-bytes", type=int, default=2_000_000,
                    help="If a file is larger than this, do not download it (create placeholder instead).")
    ap.add_argument("--exclude-dataset", action="append", default=["kidlang"],
                    help="Dataset folder name(s) to exclude. Repeatable.")
    ap.add_argument("--skip-ext", action="append",
                    default=[".con", ".fif", ".mgz", ".nii", ".nii.gz", ".mat", ".mrk", ".ds", ".stc"],
                    help="File extensions to skip downloading (repeatable).")
    ap.add_argument("--bidsignore-template", type=Path, default=None,
                    help="Path to a .bidsignore template to apply to each dataset root.")

    # argparse (near your other args)
    ap.add_argument(
        "--placeholder-size",
        type=int,
        default=4096,  # 4 KiB sentinel; set 0 to keep old behavior
        help="Size in bytes for placeholder files (when skipping by ext/size). "
             "If 0, create 0-byte files. Default: 4096.",
    )

    args = ap.parse_args()

    # ---------- Local mode ----------
    if args.root:
        LOG.info("Running in LOCAL mode under %s", args.root)
        # (Optional) Pre-cache the Deno validator for speed in local runs:
        _ensure_deno_validator_cached()
        summary_csv = validate_local_root(
            args.root,
            exclude=args.exclude_dataset,
            bidsignore_template=args.bidsignore_template
        )
        LOG.info("Done. Summary: %s", summary_csv)
        return

    # ---------- Box mode ----------
    LOG.info("Running in BOX mode (folder %s)", args.box_folder_id)
    config_json_str = os.environ.get("BOX_CLIENT_SDK_CONFIG")
    client = _box_client_from_config(config_json_str, args.box_config)

    args.work_dir.mkdir(parents=True, exist_ok=True)

    # Pre-cache Deno validator once
    _ensure_deno_validator_cached()

    # Prepare helpers
    get_or_create = _get_or_create_child_folder_cached(client)
    summary_csv = args.work_dir / "bids_validation_summary.csv"

    # Stream: process one dataset at a time
    for ds_name, ds_id in iter_box_top_level_datasets(client, args.box_folder_id,
                                                      exclude=set(args.exclude_dataset or [])):
        mirror_validate_upload_one_dataset(
            client=client,
            box_dataset_id=ds_id,
            box_dataset_name=ds_name,
            work_dir=args.work_dir,
            dest_folder_id=args.box_folder_id,
            skip_exts=tuple(s.lower() for s in args.skip_ext),
            create_placeholders=(not args.no_con_placeholders),
            max_bytes=args.max_bytes,
            bidsignore_template=args.bidsignore_template,
            get_or_create_child_folder=get_or_create,
            summary_csv=summary_csv,
            placeholder_size=args.placeholder_size,  # ← new
        )

    LOG.info("All datasets processed in streaming mode. Latest summary: %s", summary_csv)


if __name__ == "__main__":
    main()
