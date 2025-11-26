# kit_epochs_evoked_from_config.py
# Build epochs & evoked from FIFF and .eve (from triggers_to_events), configurable via YAML.
# Supports per-event-type epoch windows via epoching.windows in config.

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

DESC_EPOCHS = "epo"   # desc-epo in output epochs names
DESC_EVOKED = "evk"   # desc-evk in output evoked names

# ------------------------------- helpers -------------------------------
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
    ent = {}
    for m in _BIDS_ENTITY_RE.findall(name):
        token = next(t for t in m if t)
        k, v = token.split("-", 1)
        ent[{"sub": "subject", "ses": "session", "task": "task", "acq": "acq",
             "run": "run", "proc": "proc", "rec": "rec", "split": "split"}[k]] = v
    return ent

def _match_selection(entities: dict, sel: dict) -> bool:
    def ok(key, vals):
        if not vals:
            return True
        return str(entities.get(key)) in set(map(str, vals))
    return (
        ok("session", sel.get("sessions")) and
        ok("task",    sel.get("tasks")) and
        ok("run",     sel.get("runs")) and
        ok("split",   sel.get("splits")) and
        ok("proc",    sel.get("processings"))
    )

def _events_basename_from_entities(ent: dict, events_desc: str) -> str:
    # replicate triggers_to_events filename assembly (ordering & prefixes)
    key_order = ["subject", "session", "task", "acq", "run", "proc", "rec", "split"]
    prefix = {"subject": "sub", "session": "ses", "task": "task", "acq": "acq",
              "run": "run", "proc": "proc", "rec": "rec", "split": "split"}
    parts = []
    for k in key_order:
        v = ent.get(k)
        if v not in (None, "", "n/a"):
            parts.append(f"{prefix[k]}-{v}")
    parts.append(f"desc-{events_desc}_events")
    return "_".join(parts)

def _normalize_windows_dict(wins_cfg):
    """Return a dict {event_code_str: {'tmin': float, 'tmax': float, 'baseline': (a,b)|None}}"""
    if not wins_cfg:
        return {}
    out = {}
    for k, v in wins_cfg.items():
        code_str = str(k)
        tmin = float(v.get("tmin"))
        tmax = float(v.get("tmax"))
        bl = v.get("baseline", None)
        baseline = None if bl in (None, "", [], "null") else (float(bl[0]), float(bl[1]))
        out[code_str] = {"tmin": tmin, "tmax": tmax, "baseline": baseline}
    return out

# ------------------------------- main -------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Compute epochs and evoked from FIFF + .eve created by triggers_to_events; supports per-event windows."
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="pipeline_config_files/config_template.yml",
        help="Path to YAML config (default: pipeline_config_files/config_template.yml)"
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing epochs/evoked files."
    )
    args = parser.parse_args()

    cfg_path = Path(args.config).expanduser()
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")
    with open(cfg_path, "r") as f:
        CFG = yaml.safe_load(f) or {}
    print(f"Loaded config from: {cfg_path.resolve()}")

    # Project root
    proj = CFG.get("project", {}) or {}
    root_override = proj.get("root_override")
    if root_override:
        root = Path(root_override).expanduser()
    else:
        env_name = proj.get("root_env", "MEG_DATA")
        env_val = os.getenv(env_name)
        if not env_val:
            raise EnvironmentError(f"{env_name} is not set and project.root_override not provided.")
        root = Path(env_val)
    project_name = proj["name"]
    bids_root = str(root / project_name)
    print(f"Resolved BIDS root: {bids_root}")

    # Subject selection
    sub_cfg = CFG.get("subjects", {}) or {}
    include = sub_cfg.get("include") or []   # [] => all subjects found under derivatives
    exclude = set(sub_cfg.get("exclude") or [])

    # Optional BIDS selectors
    sel = CFG.get("bids_selection", {}) or {}

    # Events desc used when writing .eve
    events_cfg = CFG.get("events", {}) or {}
    events_desc = str(events_cfg.get("desc", "autopulses"))

    # Epoching parameters
    ep_cfg = CFG.get("epoching", {}) or {}
    # Global defaults (used when code not in windows)
    tmin_def = float(ep_cfg.get("tmin", -0.2))
    tmax_def = float(ep_cfg.get("tmax", 0.8))
    bl_def   = ep_cfg.get("baseline", [-0.2, 0.0])
    baseline_def = None if bl_def in (None, "", [], "null") else (float(bl_def[0]), float(bl_def[1]))
    preload = bool(ep_cfg.get("preload", True))
    decim = ep_cfg.get("decim", None)
    reject = ep_cfg.get("reject", None)
    flat = ep_cfg.get("flat", None)
    picks = ep_cfg.get("picks", None)  # e.g., ["meg"], ["mag"]

    # Per-event windows
    windows_cfg = _normalize_windows_dict(ep_cfg.get("windows", {}))

    # Input roots: prefer filtered → fallback to kit2fiff
    # Look for renamed folders first
    SRC_FILTERED = Path(bids_root) / "derivatives" / "4-kit_apply_filters"
    if not SRC_FILTERED.exists():
        SRC_FILTERED = Path(bids_root) / "derivatives" / "filtered_data"

    SRC_KIT2FIFF = Path(bids_root) / "derivatives" / "2-kit_con_to_fif"
    if not SRC_KIT2FIFF.exists():
        SRC_KIT2FIFF = Path(bids_root) / "derivatives" / "kit2fiff"

    # Events root
    EVE_ROOT = Path(bids_root) / "derivatives" / "5-kit_compute_events_single_channel"
    if not EVE_ROOT.exists():
        EVE_ROOT = Path(bids_root) / "derivatives" / "triggers_to_events"
    
    if not EVE_ROOT.exists():
        raise FileNotFoundError(f"Events derivatives not found: {EVE_ROOT}")

    # Output root
    script_name = Path(__file__).stem
    OUT_ROOT = Path(bids_root) / "derivatives" / script_name
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    # Save a copy of the config file with timestamp
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    config_save_path = OUT_ROOT / f"config_{timestamp_str}.yml"
    with open(config_save_path, 'w') as f:
        yaml.dump(CFG, f, default_flow_style=False)
    print(f"Saved copy of config to: {config_save_path}")

    # Discover subjects from available FIFFs
    sub_dirs = []
    if SRC_FILTERED.exists():
        sub_dirs += [p for p in SRC_FILTERED.glob("sub-*") if p.is_dir()]
    if SRC_KIT2FIFF.exists():
        sub_dirs += [p for p in SRC_KIT2FIFF.glob("sub-*") if p.is_dir()]
    subjects_all = sorted({p.name.replace("sub-", "") for p in sub_dirs})
    subjects = sorted(s for s in (include or subjects_all) if s not in exclude)
    print(f"Subjects to process ({len(subjects)}): {subjects}")

    summary_rows = []

    for sub in subjects:
        print("\n" + "=" * 70)
        print(f"Subject: {sub}")
        print("=" * 70)

        # Pick subject source (prefer filtered)
        sub_src = (SRC_FILTERED / f"sub-{sub}") if (SRC_FILTERED / f"sub-{sub}").exists() else (SRC_KIT2FIFF / f"sub-{sub}")
        if not sub_src.exists():
            print(f"No FIFFs found for sub-{sub}; skipping.")
            continue

        fif_files = sorted(sub_src.rglob("*.fif"))
        if not fif_files:
            print(f"No FIFF files under {sub_src}; skipping.")
            continue

        sub_out_root = OUT_ROOT / f"sub-{sub}"
        sub_log = sub_out_root / "epochs_evoked_log.txt"

        for fif_path in fif_files:
            base = fif_path.stem
            ent = _parse_entities_from_name(base)

            if not _match_selection(ent, sel):
                continue

            out_dir = sub_out_root
            eve_dir = EVE_ROOT / f"sub-{sub}"
            if ent.get("session"):
                out_dir = out_dir / f"ses-{ent['session']}"
                eve_dir = eve_dir / f"ses-{ent['session']}"
            out_dir.mkdir(parents=True, exist_ok=True)

            eve_base = _events_basename_from_entities(ent, events_desc)
            eve_path = eve_dir / f"{eve_base}.eve"
            if not eve_path.exists():
                print(f"Missing events file for {fif_path.name}: {eve_path.name} — skipping.")
                continue

            # Base output names (we'll add _ev<code> for epochs files when windows differ)
            ent_for_names = ent.copy()
            base_epochs_fname = build_fif_output_name_from_entities(ent_for_names, DESC_EPOCHS).replace(".fif", "_epo.fif")
            evoked_fname = build_fif_output_name_from_entities(ent_for_names, DESC_EVOKED).replace(".fif", "_ave.fif")
            evoked_out = out_dir / evoked_fname

            # Load raw and all events
            try:
                raw = mne.io.read_raw_fif(fif_path, preload=True, verbose=False)
                events_all = mne.read_events(str(eve_path))
            except Exception as e:
                print(f"Error loading inputs for {fif_path.name}: {e}")
                continue

            # Group by event code (3rd column)
            codes_present = np.unique(events_all[:, 2]).tolist()

            evokeds_for_file = []
            per_code_info = []

            for code in codes_present:
                code_str = str(int(code))

                # Window for this code
                if code_str in windows_cfg:
                    cfg = windows_cfg[code_str]
                    tmin = cfg["tmin"]; tmax = cfg["tmax"]; baseline = cfg["baseline"]
                else:
                    tmin = tmin_def; tmax = tmax_def; baseline = baseline_def

                # Select events for this code
                ev_code = events_all[events_all[:, 2] == code]

                if ev_code.size == 0:
                    continue

                # Build epochs for this event type
                try:
                    epochs = mne.Epochs(
                        raw,
                        ev_code,
                        event_id=None,  # event codes are embedded in events
                        tmin=tmin,
                        tmax=tmax,
                        baseline=baseline,
                        preload=True if preload else False,
                        picks=picks,
                        decim=decim,
                        reject=reject,
                        flat=flat,
                        verbose=False,
                    )
                    if baseline is not None:
                        epochs.apply_baseline()

                    # Average this condition
                    evk = epochs.average()
                    # Label it with the code in the comment so it's easy to spot later
                    evk.comment = f"code-{code_str}"

                    evokeds_for_file.append(evk)

                    # Save epochs per-condition (so mixed windows are allowed)
                    # Append _ev<code> before _epo.fif
                    epochs_fname = base_epochs_fname.replace("_epo.fif", f"_ev{code_str}_epo.fif")
                    epochs_out = out_dir / epochs_fname
                    if epochs_out.exists() and not args.overwrite:
                        print(f"  Exists → {epochs_out.name} (skip; use --overwrite)")
                    else:
                        epochs.save(str(epochs_out), overwrite=True)
                        print(f"✓ Saved epochs: {epochs_out}  (n={len(epochs)})")

                    per_code_info.append({
                        "code": code_str, "tmin": tmin, "tmax": tmax,
                        "baseline": "" if baseline is None else f"{baseline}",
                        "n_epochs": int(len(epochs)),
                        "epochs_out": str(epochs_out),
                    })

                except Exception as e:
                    print(f"Epoching failed for code {code_str} in {fif_path.name}: {e}")

            # Save all evokeds (one file containing multiple conditions)
            if evokeds_for_file:
                if evoked_out.exists() and not args.overwrite:
                    print(f"Exists → {evoked_out.name} (skip; use --overwrite)")
                else:
                    mne.write_evokeds(str(evoked_out), evokeds_for_file, overwrite=True)
                    print(f"Saved evoked: {evoked_out}  (n={len(evokeds_for_file)})")

            # Log & summary
            for info in per_code_info:
                row = {
                    "timestamp": _ts(),
                    "subject": ent.get("subject", sub),
                    "session": ent.get("session", ""),
                    "task": ent.get("task", ""),
                    "run": ent.get("run", ""),
                    "split": ent.get("split", ""),
                    "proc": ent.get("proc", ""),
                    "raw_in": str(fif_path),
                    "eve_in": str(eve_path),
                    "ev_code": info["code"],
                    "tmin": info["tmin"],
                    "tmax": info["tmax"],
                    "baseline": info["baseline"],
                    "n_epochs": info["n_epochs"],
                    "epochs_out": info["epochs_out"],
                    "evoked_out": str(evoked_out),
                }
                summary_rows.append(row)

                _append_subject_log(sub_log, [
                    f"[{row['timestamp']}] sub={row['subject']} ses={row['session']} run={row['run']} split={row['split']} code={row['ev_code']}",
                    f"  RAW : {row['raw_in']}",
                    f"  EVE : {row['eve_in']}",
                    f"  OUT : epochs={row['epochs_out']}  evoked={row['evoked_out']}",
                    f"  WIN : tmin={row['tmin']}, tmax={row['tmax']}, baseline={row['baseline']}",
                    f"  N   : epochs={row['n_epochs']}",
                    ""
                ])

            # free memory
            try:
                raw.close()
            except Exception:
                pass

    # Root summary
    summary_csv = OUT_ROOT / "epochs_evoked_summary.csv"
    if summary_rows:
        pd.DataFrame(summary_rows).to_csv(summary_csv, index=False)
        print(f"\nWrote summary table: {summary_csv}")
    else:
        print("\nNo epochs/evoked created; summary not written (no rows).")

    print("Done.")


if __name__ == "__main__":
    main()
