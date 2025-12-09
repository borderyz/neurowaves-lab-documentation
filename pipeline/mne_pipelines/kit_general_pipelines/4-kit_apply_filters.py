# kit_filter_from_config.py
# Load FIFF from derivatives/kit2fiff, apply line-notch (C.LINE_FREQUENCY and harmonics) and band-pass,
# save to <BIDS_ROOT>/derivatives/filtered_data with desc-filtered_data.

import argparse
import os
from pathlib import Path
import re
from datetime import datetime
import yaml
import pandas as pd
import numpy as np
import mne

from pipeline.mne_pipelines.kit_general_pipelines.utilities import (
    NYUAD_KIT_CONSTANTS as C,
    build_fif_output_name_from_entities,
)

DESC_TAG = "filtered_data"  # desc-filtered_data in output filenames

# -------------------------------
# Helpers
# -------------------------------
def _ts():
    return datetime.now().isoformat(timespec="seconds")

def _append_subject_log(sub_log_path: Path, lines: list[str]):
    sub_log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(sub_log_path, "a", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln.rstrip() + "\n")

_BIDS_ENTITY_RE = re.compile(
    r"(sub-[^_]+)|"
    r"(ses-[^_]+)|"
    r"(task-[^_]+)|"
    r"(acq-[^_]+)|"
    r"(run-[^_]+)|"
    r"(proc-[^_]+)|"
    r"(rec-[^_]+)|"
    r"(split-[^_.]+)"
)

def _parse_entities_from_name(name: str) -> dict:
    """
    Parse BIDS-like key-value pairs from a base filename.
    Returns dict with keys among: subject, session, task, acq, run, proc, rec, split
    """
    ent = {}
    for m in _BIDS_ENTITY_RE.findall(name):
        token = next(t for t in m if t)  # pick the matched group
        key, val = token.split("-", 1)
        key_map = {
            "sub": "subject", "ses": "session", "task": "task", "acq": "acq",
            "run": "run", "proc": "proc", "rec": "rec", "split": "split"
        }
        ent[key_map[key]] = val
    return ent

def _safe_float(x, default=None):
    try:
        return float(x)
    except Exception:
        return default

def _compute_harmonics(line_freq: float, sfreq: float) -> np.ndarray:
    if line_freq is None or line_freq <= 0:
        return np.array([])
    nyq = sfreq / 2.0
    # Ensure strictly below Nyquist (minus small epsilon to be safe against float errors/notch width)
    kmax = int((nyq - 1e-5) // line_freq)
    # Limit to at most 3 harmonics (fundamental + 2 harmonics, or just first 3 multiples)
    # User requested "3 harmonics ... at most"
    if kmax > 3:
        kmax = 3
    if kmax <= 0:
        return np.array([])
    return np.array([k * line_freq for k in range(1, kmax + 1)], dtype=float)

def _match_selection(entities: dict, sel: dict) -> bool:
    """
    Apply optional selection filters (sessions/tasks/runs/splits/procs).
    If a selector list is None or empty -> no filter on that key.
    """
    def ok(key, vals):
        if not vals:
            return True
        v = entities.get(key)
        # Runs/splits/proc in filenames are strings; treat comparison as strings
        return v in set(map(str, vals))
    return (
        ok("session", sel.get("sessions")) and
        ok("task",    sel.get("tasks")) and
        ok("run",     sel.get("runs")) and
        ok("split",   sel.get("splits")) and
        ok("proc",    sel.get("processings"))
    )

# -------------------------------
# Main
# -------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Apply line-notch (C.LINE_FREQUENCY & harmonics) and band-pass to FIFFs created by kit2fiff."
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="pipeline_config_files/config_template.yml",
        help="Path to YAML config (default: pipeline_config_files/config_template.yml)"
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing filtered FIFF files."
    )
    args = parser.parse_args()

    cfg_path = Path(args.config).expanduser()
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")
    with open(cfg_path, "r") as f:
        CFG = yaml.safe_load(f) or {}
    print(f"Loaded config from: {cfg_path.resolve()}")

    # Resolve dataset root
    proj_cfg = CFG.get("project", {}) or {}
    root_override = proj_cfg.get("root_override")
    if root_override:
        root = Path(root_override).expanduser()
    else:
        root_env = proj_cfg.get("root_env", "MEG_DATA")
        env_val = os.getenv(root_env)
        if not env_val:
            raise EnvironmentError(f"{root_env} is not set and project.root_override not provided.")
        root = Path(env_val)

    project_name = proj_cfg["name"]
    bids_root = str(root / project_name)
    print(f"Resolved BIDS root: {bids_root}")

    # Subjects include/exclude
    sub_cfg = CFG.get("subjects", {}) or {}
    include = sub_cfg.get("include") or []   # [] -> ALL
    exclude = set(sub_cfg.get("exclude") or [])

    # Optional selection (sessions/tasks/runs/splits/processings)
    sel = CFG.get("bids_selection", {}) or {}

    # Filtering parameters (with defaults)
    filt_cfg = CFG.get("filters", {}) or {}
    notch_cfg = filt_cfg.get("notch", {}) or {}
    bp_cfg    = filt_cfg.get("bandpass", {}) or {}

    notch_enabled = bool(notch_cfg.get("enabled", True))
    custom_notch_freqs = notch_cfg.get("freqs")  # optional list; otherwise compute harmonics from C.LINE_FREQUENCY
    # (optional) width/other kwargs can be added if you want:
    notch_kwargs = notch_cfg.get("kwargs", {}) or {}

    l_freq = _safe_float(bp_cfg.get("l_freq", 1.0), 1.0)
    h_freq = _safe_float(bp_cfg.get("h_freq", 40.0), 40.0)
    bp_kwargs = bp_cfg.get("kwargs", {}) or {}  # allow method='fir', phase, fir_window, etc.

    # Inputs live here (output of kit2fiff)
    # Assuming kit2fiff script is named '2-kit_con_to_fif.py' -> derivatives/2-kit_con_to_fif
    # If the previous step used a different name, adjust accordingly.
    # We look for the folder that matches the kit2fiff script name.
    SRC_ROOT = Path(bids_root) / "derivatives" / "2-kit_con_to_fif"
    if not SRC_ROOT.exists():
        # Fallback for backward compatibility or if name differs
        SRC_ROOT_ALT = Path(bids_root) / "derivatives" / "kit2fiff"
        if SRC_ROOT_ALT.exists():
            SRC_ROOT = SRC_ROOT_ALT
        else:
            raise FileNotFoundError(f"Source derivatives not found: {SRC_ROOT} or {SRC_ROOT_ALT}")

    # Outputs go here
    script_name = Path(__file__).stem
    OUT_ROOT = Path(bids_root) / "derivatives" / script_name
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    # Save a copy of the config file with timestamp
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    config_save_path = OUT_ROOT / f"config_{timestamp_str}.yml"
    with open(config_save_path, 'w') as f:
        yaml.dump(CFG, f, default_flow_style=False)
    print(f"Saved copy of config to: {config_save_path}")

    # Root summary
    summary_rows = []

    # List all candidate FIFFs per subject
    # Subject list = subdirs in kit2fiff unless include is specified
    subjects_all = sorted(p.name.replace("sub-", "") for p in SRC_ROOT.glob("sub-*") if p.is_dir())
    subjects = sorted(s for s in (include or subjects_all) if s not in exclude)
    print(f"Subjects to process ({len(subjects)}): {subjects}")

    for sub in subjects:
        print("\n" + "=" * 70)
        print(f"Subject: {sub}")
        print("=" * 70)

        sub_src = SRC_ROOT / f"sub-{sub}"
        if not sub_src.exists():
            print(f"No kit2fiff outputs for sub-{sub}; skipping.")
            continue

        # Find all .fif files recursively under this subject
        fif_files = sorted(sub_src.rglob("*.fif"))
        if not fif_files:
            print(f"No FIFF files under {sub_src}; skipping.")
            continue

        # Per-subject log
        sub_out_root = OUT_ROOT / f"sub-{sub}"
        sub_log = sub_out_root / "filter_log.txt"

        for fif_path in fif_files:
            base = fif_path.stem
            ent = _parse_entities_from_name(base)

            # Apply selectors from YAML if provided
            if not _match_selection(ent, sel):
                continue

            # Determine output directory (mirror session structure if present)
            out_dir = sub_out_root
            if ent.get("session"):
                out_dir = out_dir / f"ses-{ent['session']}"
            out_dir.mkdir(parents=True, exist_ok=True)

            # Build output filename using entities and desc 'filtered_data'
            # If you have the helper, reuse it; else build minimal
            fname_out = build_fif_output_name_from_entities(ent, DESC_TAG)
            out_path = out_dir / fname_out

            if out_path.exists() and not args.overwrite:
                print(f"  Exists → {out_path.name} (skip; use --overwrite to replace)")
                continue

            print(f"\n--- Filtering ---")
            print(f"IN : {fif_path}")
            print(f"OUT: {out_path}")

            status = "success"
            err_msg = ""

            raw = mne.io.read_raw_fif(fif_path, preload=True, verbose=False)
            try:
                # Notch filter (line frequency + harmonics)
                if notch_enabled:
                    if custom_notch_freqs:
                        freqs = np.array(custom_notch_freqs, dtype=float)
                    else:
                        freqs = _compute_harmonics(float(C.LINE_FREQUENCY), float(raw.info["sfreq"]))
                    if freqs.size:
                        raw.notch_filter(freqs=freqs, verbose=False, **notch_kwargs)

            except Exception as e:
                status = "error"
                err_msg = str(e)
                print(f"Error notchfiltering {fif_path}: {e}")

            try:
                # Band-pass filter
                raw.filter(l_freq=l_freq, h_freq=h_freq, verbose=False, **bp_kwargs)

            except Exception as e:
                status = "error"
                err_msg = str(e)
                print(f"Error bandpassfiltering {fif_path}: {e}")

            # Save
            raw.save(out_path, overwrite=True)
            raw.close()
            print(f"Saved filtered FIFF: {out_path}")

            # Summary row
            summary_rows.append({
                "timestamp": _ts(),
                "subject": ent.get("subject", sub),
                "session": ent.get("session", ""),
                "task": ent.get("task", ""),
                "run": ent.get("run", ""),
                "split": ent.get("split", ""),
                "proc": ent.get("proc", ""),
                "in_fif": str(fif_path),
                "out_fif": str(out_path),
                "notch_enabled": notch_enabled,
                "line_freq": getattr(C, "LINE_FREQUENCY", None),
                "bandpass_l_freq": l_freq,
                "bandpass_h_freq": h_freq,
                "status": status,
                "error": err_msg,
            })

            # Append subject log
            log_lines = [
                f"[{summary_rows[-1]['timestamp']}] sub={summary_rows[-1]['subject']} "
                f"ses={summary_rows[-1]['session']} run={summary_rows[-1]['run']} split={summary_rows[-1]['split']}",
                f"  IN  : {fif_path}",
                f"  OUT : {out_path}",
                f"  NOTCH: {'on' if notch_enabled else 'off'}  (line={getattr(C, 'LINE_FREQUENCY', None)} Hz)",
                f"  BP  : {l_freq}-{h_freq} Hz",
                f"  STATUS: {status}{'  ERR: ' + err_msg if err_msg else ''}",
                "",
            ]
            _append_subject_log(sub_log, log_lines)

    # Root summary
    summary_csv = OUT_ROOT / "filter_summary.csv"
    if summary_rows:
        pd.DataFrame(summary_rows).to_csv(summary_csv, index=False)
        print(f"\nWrote summary table: {summary_csv}")
    else:
        print("\nNo files filtered; summary not created (no rows).")

    print("Done.")


if __name__ == "__main__":
    main()
