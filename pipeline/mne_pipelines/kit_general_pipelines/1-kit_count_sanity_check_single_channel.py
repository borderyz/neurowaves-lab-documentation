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
from mne_bids import find_matching_paths, get_entity_vals

from pipeline.mne_pipelines.kit_general_pipelines.utilities import (
    NYUAD_KIT_CONSTANTS as C,
    detect_pulses_on_channel,
    resolve_events_pair_with_joint_fallback,
    _glyph,
    bids_name_from_entities,
    write_run_log )


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
# Subjects: empty include => ALL
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
# Derivatives / logging setup
# -------------------------------
script_name = Path(__file__).stem
DERIV_ROOT = Path(bids_root) / "derivatives" / script_name
DERIV_ROOT.mkdir(parents=True, exist_ok=True)

# Save a copy of the config file with timestamp
timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
# Import datetime if not already imported (it's not in the original imports)
from datetime import datetime
config_save_path = DERIV_ROOT / f"config_{timestamp_str}.yml"
with open(config_save_path, 'w') as f:
    yaml.dump(CFG, f, default_flow_style=False)
print(f"Saved copy of config to: {config_save_path}")







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
        print(f"No MEG files found for sub-{sub}.")
        continue

    for raw_match in raw_matches:
        entities = raw_match.entities
        raw_path = raw_match.fpath
        print(f"\n--- Processing: {raw_path}")

        # Resolve a PAIRED table+json with safe fallback
        events_table_path, events_json_path, scope = resolve_events_pair_with_joint_fallback(raw_match, bids_root)

        if not events_json_path:
            print(f"No suitable events JSON (paired) for: {raw_path} — skipping.")
            summary_records.append({
                "subject": sub, "file": raw_path, "pass": False,
                "comments": "Missing/invalid events JSON (no paired scope)"
            })
            continue

        if not events_table_path:
            print(f"Single-channel requires events table, but none found (paired) for: {raw_path}")
            summary_records.append({
                "subject": sub, "file": raw_path, "pass": False,
                "comments": "Missing events table (no paired scope)"
            })
            continue

        # Load TriggerMode from the EXACT SAME scope JSON
        with open(events_json_path, "r") as jf:
            metadata_events = json.load(jf)

        trigger_mode = str(metadata_events.get("TriggerMode", "")).strip().lower().replace("-", "_").replace(" ", "_")
        if trigger_mode != "single_channel":
            print(f"TriggerMode='{trigger_mode}' → not single_channel; skipping run.")
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

            pulses, thr_hi, thr_lo, metrics = detect_pulses_on_channel(
                RAW_DATA, ch_mne, baseline_s=(0.0, 10.0)
            )
            threshold_log.append({"channel_mne": ch_mne, "thr_hi": thr_hi, "thr_lo": thr_lo, "n": len(pulses)})

            for m in metrics:
                detected_rows.append({
                    "sample": m["start"],
                    "onset": m["start"] / sfreq,
                    "end_sample": m["end"],
                    "width_samp": m["width_samp"],
                    "width_ms": m["width_ms"],
                    "amp_max": m["amp_max"],
                    "amp_mean": m["amp_mean"],
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
        events_ref = events_ref[events_ref["channel"].isin(C.trigger_channels_KIT)].copy()
        events_ref["channel_mne"] = events_ref["channel"].map(C.MNE_from_KIT)

        # -----------------------------
        # Compare
        # -----------------------------
        # 1) Counts per channel
        counts_ref = events_ref["channel"].value_counts().sort_index().reindex(C.trigger_channels_KIT, fill_value=0)
        counts_det = detected_df["channel"].value_counts().sort_index().reindex(C.trigger_channels_KIT, fill_value=0)
        counts_compare = pd.DataFrame({
            "csv_count": counts_ref, "detected_count": counts_det,
            "diff": counts_det - counts_ref
        })
        print("\n=== Count comparison per KIT channel (224–231) ===")
        print(counts_compare)

        # 2) Sequence check (CSV row order vs detected chronological)
        seq_ref_row = events_ref["channel"].to_numpy()
        seq_det_time = detected_df.sort_values("sample")["channel"].to_numpy()
        row_order_ok = (len(seq_ref_row) == len(seq_det_time)) and np.array_equal(seq_ref_row, seq_det_time)

        print("\n=== Sequence check (CSV row order vs detected chronological) ===")
        print(f"CSV events:      {len(seq_ref_row)}")
        print(f"Detected events: {len(seq_det_time)}")
        print(f"{_glyph(row_order_ok)} Sequence matches exactly." if row_order_ok
              else f"{_glyph(False)} Sequence mismatch (or different lengths).")

        # Final PASS/FAIL: both counts and row-order sequence must match
        counts_ok = (counts_compare["diff"] == 0).all()
        pass_flag = counts_ok and row_order_ok
        print(f"\n=== FINAL RESULT: {'PASS ' + _glyph(True) if pass_flag else 'FAIL ' + _glyph(False)} ===")

        # -----------------------------
        # Per-channel & overall pulse stats (amplitude/width)
        # -----------------------------
        if not detected_df.empty:
            per_ch_stats = detected_df.groupby("channel").agg(
                n_pulses=("sample", "count"),
                amp_max_mean=("amp_max", "mean"),
                amp_max_var=("amp_max", "var"),
                amp_mean_mean=("amp_mean", "mean"),
                amp_mean_var=("amp_mean", "var"),
                width_ms_mean=("width_ms", "mean"),
                width_ms_var=("width_ms", "var"),
                width_ms_min=("width_ms", "min"),
                width_ms_max=("width_ms", "max"),
            ).reindex(C.trigger_channels_KIT, fill_value=0)
            overall_stats = detected_df.agg({
                "amp_max": ["mean", "var", "max"],
                "amp_mean": ["mean", "var"],
                "width_ms": ["mean", "var", "min", "max"],
            })
        else:
            per_ch_stats = pd.DataFrame(columns=[
                "n_pulses","amp_max_mean","amp_max_var","amp_mean_mean","amp_mean_var",
                "width_ms_mean","width_ms_var","width_ms_min","width_ms_max"
            ], index=C.trigger_channels_KIT)
            overall_stats = None

        # -----------------------------
        # Build logfile text
        # -----------------------------
        sub_dir = DERIV_ROOT / f"sub-{sub}"
        if entities.get("session"):
            sub_dir = sub_dir / f"ses-{entities['session']}"
        sub_dir.mkdir(parents=True, exist_ok=True)
        log_file = sub_dir / f"{bids_name_from_entities(entities, 'desc-sanitycheck', '_log.txt')}"

        log_lines = [
            f"Raw: {raw_path}",
            f"Events CSV: {events_table_path}",
            f"Events JSON: {events_json_path}",
            f"TriggerMode: {trigger_mode}",
            "",
            "[Thresholds per channel]",
            thr_df.to_string(index=False),
            "",
            "[Counts per KIT channel]",
            counts_compare.to_string(),
        ]

        if not counts_ok:
            correct_count_chs = counts_compare[counts_compare["diff"] == 0].index.tolist()
            incorrect_count_df = counts_compare[counts_compare["diff"] != 0].copy()
            log_lines += [
                "",
                "[Counts check details]",
                f"Correct count channels: {correct_count_chs if correct_count_chs else 'None'}",
            ]
            if not incorrect_count_df.empty:
                log_lines += [
                    "Incorrect count channels (csv_count / detected_count / diff):",
                    incorrect_count_df.to_string(),
                ]

        # Sequence section
        log_lines += [
            "",
            "[Sequence check: CSV row order vs detected chronological]",
            f"match={row_order_ok} | CSV n={len(seq_ref_row)} | Detected n={len(seq_det_time)}",
        ]
        if not row_order_ok:
            csv_seq_str = ", ".join(map(str, seq_ref_row.tolist()))
            det_seq_str = ", ".join(map(str, seq_det_time.tolist()))
            log_lines += [
                "CSV channel sequence (row order):",
                csv_seq_str,
                "Detected channel sequence (chronological):",
                det_seq_str,
            ]

        # Pulse stats
        log_lines += [
            "",
            "[Pulse amplitude & width stats per KIT channel]",
            per_ch_stats.round(6).to_string(),
        ]
        if overall_stats is not None:
            log_lines += [
                "",
                "[Overall pulse stats (all trigger channels combined)]",
                overall_stats.round(6).to_string(),
            ]

        # Final flag
        log_lines += [
            "",
            f"Final result: {'PASS ' + _glyph(True) if pass_flag else 'FAIL ' + _glyph(False)}"
        ]

        write_run_log(log_file, "\n".join(log_lines))

        # -----------------------------
        # Add to summary
        # -----------------------------
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
