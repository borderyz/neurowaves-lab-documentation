# sanity_single_channel_check.py
# Run a sanity single-channel trigger count check for an NYUAD-KIT MEG dataset.

import argparse
import os
from pathlib import Path
import json
import yaml
import pandas as pd
import numpy as np

import mne
from mne_bids import find_matching_paths, get_entity_vals, BIDSPath

import matplotlib
matplotlib.use('TkAgg')

# Constants instance
from pipeline.mne_pipelines.kit_general_pipelines.utilities import NYUAD_KIT_CONSTANTS as C


# -------------------------------
# CLI: which config to use
# -------------------------------
parser = argparse.ArgumentParser(
    description="Run sanity single-channel trigger count check for MEG dataset."
)
parser.add_argument(
    "--config", "-c",
    type=str,
    default="pipeline_config_files/config_template.yml",
    help="Path to YAML config (default: pipeline_config_files/config_template.yml)"
)
args = parser.parse_args()

config_path = Path(args.config).expanduser()
if not config_path.exists():
    raise FileNotFoundError(f"Config file not found: {config_path}")

with open(config_path, "r") as f:
    CFG = yaml.safe_load(f) or {}

print(f"Loaded config from: {config_path.resolve()}")

# -------------------------------
# Resolve dataset root
# -------------------------------
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

# -------------------------------
# Subjects: empty include => ALL subjects in BIDS
# -------------------------------
sub_cfg = CFG.get("subjects", {}) or {}
include = sub_cfg.get("include") or []
exclude = set(sub_cfg.get("exclude") or [])

all_subjects = get_entity_vals(bids_root, entity_key="subject")
subjects = sorted(s for s in (include or all_subjects) if s not in exclude)
print(f"Subjects to process ({len(subjects)}): {subjects}")

# -------------------------------
# Optional BIDS selections
# -------------------------------
sel = CFG.get("bids_selection", {}) or {}
sessions = sel.get("sessions") or None
tasks    = sel.get("tasks") or None
runs     = sel.get("runs") or None

# -------------------------------
# Derivatives / logging setup
# -------------------------------
DERIV_ROOT = Path(bids_root) / "derivatives" / "sanity_check"
DERIV_ROOT.mkdir(parents=True, exist_ok=True)

def bids_name_from_entities(entities: dict, suffix: str, ext: str = "") -> str:
    parts = []
    if entities.get("subject"): parts.append(f"sub-{entities['subject']}")
    if entities.get("session"): parts.append(f"ses-{entities['session']}")
    if entities.get("task"): parts.append(f"task-{entities['task']}")
    if entities.get("run"): parts.append(f"run-{entities['run']}")
    if suffix: parts.append(suffix)
    name = "_".join(parts)
    return name + ext

def write_run_log(log_path: Path, text: str):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(text, encoding="utf-8")

# -------------------------------
# Pulse detector
# -------------------------------
def detect_pulses_on_channel(
    raw, ch_name,
    absolute_floor=0.3,
    mad_mult=12.0,
    hysteresis_frac=0.8,
    min_width_ms=3.0,
    min_distance_ms=6.0,
    baseline_s=None
):
    sfreq = raw.info['sfreq']
    min_width_samp = max(1, int(round((min_width_ms/1000.0)*sfreq)))
    min_distance_samp = max(1, int(round((min_distance_ms/1000.0)*sfreq)))

    pick = mne.pick_channels(raw.ch_names, [ch_name])
    x = raw.get_data(picks=pick, reject_by_annotation='omit')[0]

    xb = x
    if baseline_s is not None:
        start_s, stop_s = baseline_s
        start = max(0, int(round(start_s * sfreq)))
        stop  = min(len(x), int(round(stop_s * sfreq)))
        xb = x[start:stop] if stop > start else x

    ax = np.abs(xb)
    med = np.median(ax)
    mad = np.median(np.abs(ax - med)) + 1e-12
    thr_hi = max(absolute_floor, med + mad_mult * mad)
    thr_lo = hysteresis_frac * thr_hi

    pulses = []
    i = 1
    n = x.size
    last_accept = -10**9

    while i < n:
        if x[i-1] < thr_hi <= x[i]:
            start = i
            while i < n and x[i] >= thr_lo:
                i += 1
            width = i - start
            if width >= min_width_samp and (start - last_accept) >= min_distance_samp:
                pulses.append(start)
                last_accept = start
        else:
            i += 1

    return np.asarray(pulses, dtype=int), thr_hi, thr_lo

# -------------------------------
# Pairing helpers
# -------------------------------
def resolve_events_table_for_raw(raw_match):
    e = raw_match.entities
    candidates = find_matching_paths(
        bids_root,
        datatypes=C.DATATYPE,
        subjects=e.get("subject"),
        sessions=e.get("session"),
        tasks=e.get("task"),
        runs=e.get("run"),
        extensions=tuple(C.EVENTS_EXTENSIONS),
        suffixes="events",
    )
    if candidates:
        return candidates[0].fpath
    print(f"⚠️  No events table for raw: {raw_match.fpath}")
    return None

def resolve_events_json_with_inheritance(raw_match):
    e = raw_match.entities
    ladder = []
    cur = {k: e.get(k) for k in ("subject", "session", "task", "acquisition", "run")}
    ladder.append(dict(cur))
    for drop in ("run", "acquisition", "task", "session"):
        cur = dict(cur); cur[drop] = None
        ladder.append(dict(cur))
    ladder.append({"subject": e.get("subject"), "session": None, "task": None, "acquisition": None, "run": None})

    for ent in ladder:
        cands = find_matching_paths(
            bids_root,
            datatypes=C.DATATYPE,
            subjects=ent["subject"],
            sessions=ent["session"],
            tasks=ent["task"],
            acquisitions=ent["acquisition"],
            runs=ent["run"],
            extensions=tuple(C.METADATA_EXTENSIONS),
            suffixes="events",
        )
        if cands:
            return cands[0].fpath
    print(f"⚠️  No events JSON sidecar found (inheritance) for raw: {raw_match.fpath}")
    return None

# -------------------------------
# Main loop
# -------------------------------
summary_records = []

for sub in subjects:
    print("\n" + "="*70)
    print(f"Subject: {sub}")
    print("="*70)

    raw_matches = find_matching_paths(
        bids_root,
        datatypes=C.DATATYPE,
        subjects=sub,
        sessions=sessions,
        tasks=tasks,
        runs=runs,
        extensions=tuple(C.MEG_EXTENSIONS),
    )
    if not raw_matches:
        print(f"⚠️  No MEG files found for sub-{sub}.")
        continue

    for raw_match in raw_matches:
        entities = raw_match.entities
        raw_path = raw_match.fpath
        print(f"\n--- Processing: {raw_path}")

        # Resolve sidecars
        events_table_path = resolve_events_table_for_raw(raw_match)
        events_json_path  = resolve_events_json_with_inheritance(raw_match)

        # Get trigger mode
        trigger_mode = None
        if events_json_path and Path(events_json_path).exists():
            with open(events_json_path, "r") as jf:
                metadata_events = json.load(jf)
            trigger_mode = str(metadata_events.get("TriggerMode", "")).lower().replace("-", " ").strip()

        if not trigger_mode or "single" not in trigger_mode:
            print(f"ℹ️  TriggerMode='{trigger_mode}' → not single-channel; skipping run.")
            summary_records.append({
                "subject": sub, "file": raw_path, "pass": False,
                "comments": f"Skipped (TriggerMode={trigger_mode})"
            })
            continue

        print("Sanity check of data with single-channel trigger.")

        RAW_DATA = mne.io.read_raw_kit(raw_path, preload=False, verbose=False)
        sep = "\t" if str(events_table_path).lower().endswith(".tsv") else ","
        events_data = pd.read_csv(events_table_path, sep=sep)

        ok_channels = events_data["channel"].isin(C.trigger_channels_KIT).all()
        print(f"Events channel membership OK: {ok_channels}")

        # Detect pulses
        sfreq = RAW_DATA.info['sfreq']
        detected_rows, threshold_log = [], []
        for ch_mne in C.trigger_channels_MNE:
            if ch_mne not in RAW_DATA.ch_names:
                print(f"Warning: {ch_mne} missing; skipping.")
                continue
            pulses, thr_hi, thr_lo = detect_pulses_on_channel(
                RAW_DATA, ch_mne, baseline_s=(0.0, 10.0)
            )
            threshold_log.append({"channel_mne": ch_mne, "thr_hi": thr_hi, "thr_lo": thr_lo, "n": len(pulses)})
            for s in pulses:
                detected_rows.append({
                    "sample": s,
                    "onset": s / sfreq,
                    "channel_mne": ch_mne,
                    "channel": C.KIT_from_MNE[ch_mne],
                })

        detected_df = pd.DataFrame(detected_rows).sort_values("sample").reset_index(drop=True)
        thr_df = pd.DataFrame(threshold_log)
        print("\nThreshold summary per channel (hi/lo & detections):")
        print(thr_df)
        print(f"\nDetected {len(detected_df)} pulses total across 8 trigger channels.")

        # -----------------------------------------
        # Reference events (CSV row order as time)
        # -----------------------------------------
        events_ref = events_data.copy()
        # filter only KIT trigger channels; DO NOT compute/require 'sample'/'onset'; DO NOT sort
        events_ref = events_ref[events_ref["channel"].isin(C.trigger_channels_KIT)].copy()
        events_ref["channel_mne"] = events_ref["channel"].map(C.MNE_from_KIT)

        # -----------------------------
        # Compare
        # -----------------------------
        # 1) Counts per channel (unchanged)
        counts_ref = events_ref["channel"].value_counts().sort_index().reindex(C.trigger_channels_KIT, fill_value=0)
        counts_det = detected_df["channel"].value_counts().sort_index().reindex(C.trigger_channels_KIT, fill_value=0)
        counts_compare = pd.DataFrame({
            "csv_count": counts_ref, "detected_count": counts_det,
            "diff": counts_det - counts_ref
        })
        print("\n=== Count comparison per KIT channel (224–231) ===")
        print(counts_compare)

        # 2) Sequence check:
        # CSV row order (events_ref as-is) vs detected chronological order (detected_df sorted by sample)
        seq_ref_row = events_ref["channel"].to_numpy()  # preserve CSV row order
        seq_det_time = detected_df.sort_values("sample")["channel"].to_numpy()

        row_order_ok = (len(seq_ref_row) == len(seq_det_time)) and np.array_equal(seq_ref_row, seq_det_time)

        print("\n=== Sequence check (CSV row order vs detected chronological) ===")
        print(f"CSV events:      {len(seq_ref_row)}")
        print(f"Detected events: {len(seq_det_time)}")
        print("✅ Sequence matches exactly." if row_order_ok else "❌ Sequence mismatch (or different lengths).")

        # Final PASS/FAIL: both counts and row-order sequence must match
        counts_ok = (counts_compare["diff"] == 0).all()
        pass_flag = counts_ok and row_order_ok
        print(f"\n=== FINAL RESULT: {'PASS ✅' if pass_flag else 'FAIL ❌'} ===")

        # Save run log
        sub_dir = DERIV_ROOT / f"sub-{sub}"
        if entities.get("session"):
            sub_dir = sub_dir / f"ses-{entities['session']}"
        sub_dir.mkdir(parents=True, exist_ok=True)
        log_file = sub_dir / f"{bids_name_from_entities(entities, 'desc-sanitycheck', '_log.txt')}"
        log_text = "\n".join([
            f"Raw: {raw_path}",
            f"Events: {events_table_path}",
            f"TriggerMode: {trigger_mode}",
            "\nThresholds:\n" + thr_df.to_string(index=False),
            "\nCounts:\n" + counts_compare.to_string(),
            "\nSequence (CSV row order vs detected chronological): "
                f"CSV n={len(seq_ref_row)} | Detected n={len(seq_det_time)} | match={row_order_ok}",
            f"\nFinal result: {'PASS ✅' if pass_flag else 'FAIL ❌'}"
        ])
        write_run_log(log_file, log_text)

        summary_records.append({
            "subject": sub,
            "file": str(raw_path),
            "trigger_mode": trigger_mode,
            "csv_events": int(len(seq_ref_row)),
            "detected_events": int(len(seq_det_time)),
            "counts_match": bool(counts_ok),
            "row_order_match": bool(row_order_ok),
            "pass": bool(pass_flag),
            "log_file": str(log_file)
        })

# -------------------------------
# Root-level summary table
# -------------------------------
summary_df = pd.DataFrame(summary_records)
summary_out = DERIV_ROOT / "sanity_check_overview.csv"
summary_df.to_csv(summary_out, index=False)
print(f"\nWrote summary table: {summary_out}")
print("Done.")
