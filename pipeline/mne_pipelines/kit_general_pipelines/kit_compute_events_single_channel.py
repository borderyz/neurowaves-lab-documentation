# kit_make_events_from_triggers.py
# Create MNE events (N x 3) from detected trigger pulses and save with mne.write_events

import argparse
import os
from pathlib import Path
import json
import numpy as np
import pandas as pd
import yaml
import mne
from mne_bids import find_matching_paths, get_entity_vals

from pipeline.mne_pipelines.kit_general_pipelines.utilities import (
    NYUAD_KIT_CONSTANTS as C,
    bids_name_from_entities,
    resolve_events_pair_with_joint_fallback,
    detect_pulses_on_channel,
)

parser = argparse.ArgumentParser(
    description="Build MNE events from detected single-channel trigger pulses."
)
parser.add_argument(
    "--config", "-c",
    type=str,
    default="pipeline_config_files/config_template.yml",
    help="Path to YAML config (default: pipeline_config_files/config_template.yml)"
)
parser.add_argument(
    "--desc", type=str, default="autopulses",
    help="BIDS 'desc' tag for outputs (default: 'autopulses')."
)
parser.add_argument(
    "--overwrite", action="store_true",
    help="Overwrite existing event files."
)
args = parser.parse_args()

# --- Load config / resolve BIDS root ---
config_path = Path(args.config).expanduser()
if not config_path.exists():
    raise FileNotFoundError(f"Config file not found: {config_path}")
with open(config_path, "r") as f:
    CFG = yaml.safe_load(f) or {}

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

# Subjects
sub_cfg = CFG.get("subjects", {}) or {}
include = sub_cfg.get("include") or []
exclude = set(sub_cfg.get("exclude") or [])
all_subjects = get_entity_vals(bids_root, entity_key="subject")
subjects = sorted(s for s in (include or all_subjects) if s not in exclude)
print(f"Subjects to process ({len(subjects)}): {subjects}")

# Optional filters
sel = CFG.get("bids_selection", {}) or {}
sessions = sel.get("sessions") or None
tasks    = sel.get("tasks") or None
runs     = sel.get("runs") or None

# Output root
DERIV_ROOT = Path(bids_root) / "derivatives" / "triggers_to_events"
DERIV_ROOT.mkdir(parents=True, exist_ok=True)

# Event ID mapping: use KIT channel number as event code (224..231)
KIT_EVENT_CODE = {kit: kit for kit in C.trigger_channels_KIT}

index_rows = []

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
        entities = raw_match.entities or {}
        raw_path = raw_match.fpath
        print(f"\n--- Processing: {raw_path}")

        # Use the *paired* selection (JSON+table) from your sanity checker
        tbl_path, json_path, scope = resolve_events_pair_with_joint_fallback(raw_match=raw_match,
                                                                             bids_root=bids_root)
        if not (tbl_path and json_path):
            print(f" Missing paired events files for {raw_path} — skipping.")
            continue

        with open(json_path, "r") as jf:
            meta = json.load(jf)
        trig_mode = str(meta.get("TriggerMode", "")).strip().lower().replace("-", "_").replace(" ", "_")
        if trig_mode != "single_channel":
            print(f" TriggerMode='{trig_mode}' → not single_channel; skipping.")
            continue

        raw = mne.io.read_raw_kit(raw_path, preload=False, verbose=False)
        sfreq = raw.info["sfreq"]

        # Detect pulses on each trigger channel and assemble events array
        events_list = []
        detail_rows = []

        for ch_mne in C.trigger_channels_MNE:
            if ch_mne not in raw.ch_names:
                print(f"Warning: {ch_mne} missing; skipping.")
                continue

            pulses, thr_hi, thr_lo, metrics = detect_pulses_on_channel(
                raw, ch_mne, baseline_s=(0.0, 10.0)
            )
            kit_ch = C.KIT_from_MNE[ch_mne]
            event_code = KIT_EVENT_CODE.get(kit_ch, 0)

            for m in metrics:
                smp = int(m["start"])
                events_list.append([smp, 0, int(event_code)])
                detail_rows.append({
                    "sample": smp,
                    "onset_s": smp / sfreq,
                    "channel_mne": ch_mne,
                    "channel_kit": kit_ch,
                    "event_id": int(event_code),
                    "width_ms": m["width_ms"],
                    "amp_max": m["amp_max"],
                    "amp_mean": m["amp_mean"],
                })

        if not events_list:
            print(f"  No pulses detected for {raw_path} — skipping output.")
            continue

        events = np.asarray(sorted(events_list, key=lambda r: r[0]), dtype=int)


        # --- Build a fully disambiguating entity set for the output basename
        out_entities = {k: v for k, v in (entities or {}).items() if v}

        def set_if(val, key):
            if val not in (None, "", "n/a"):
                out_entities[key] = val

        # Normalize BIDSPath attrs into canonical BIDS entity keys
        set_if(getattr(raw_match, "task", None),        "task")
        set_if(getattr(raw_match, "run", None),         "run")
        set_if(getattr(raw_match, "acquisition", None), "acq")    # acq-*
        set_if(getattr(raw_match, "processing", None),  "proc")   # proc-*
        set_if(getattr(raw_match, "split", None),       "split")  # split-*
        set_if(getattr(raw_match, "recording", None),   "rec")    # rec-*
        # Prefer "proc" over "processing" if both exist to avoid duplicates
        if "processing" in out_entities and "proc" in out_entities:
            out_entities.pop("processing", None)

        # --- Debug: show how we got here
        print("[DEBUG] raw_match.fpath:", raw_path)
        print("[DEBUG] raw_match fields:",
              "task=", getattr(raw_match, "task", None),
              "run=", getattr(raw_match, "run", None),
              "acq=", getattr(raw_match, "acquisition", None),
              "proc=", getattr(raw_match, "processing", None),
              "rec=", getattr(raw_match, "recording", None),
              "split=", getattr(raw_match, "split", None))
        print("[DEBUG] entities (original):", entities)
        print("[DEBUG] out_entities (used for naming):", out_entities)

        # --- Build basename manually (don’t rely on bids_name_from_entities)
        key_order = ["subject", "session", "task", "acq", "run", "proc", "rec", "split"]
        prefix = {
            "subject": "sub",
            "session": "ses",
            "task": "task",
            "acq": "acq",
            "run": "run",
            "proc": "proc",
            "rec": "rec",
            "split": "split",
        }
        parts = []
        for k in key_order:
            v = out_entities.get(k, None)
            if v not in (None, "", "n/a"):
                parts.append(f"{prefix[k]}-{v}")

        # Add desc + “events” tag to the basename (mirrors prior behavior)
        parts.append(f"desc-{args.desc}_events")
        base = "_".join(parts)

        # Output paths (BIDS-ish names in derivatives)
        out_dir = DERIV_ROOT / (f"sub-{entities.get('subject')}" if entities.get("subject") else "")
        if entities.get("session"):
            out_dir = out_dir / f"ses-{entities['session']}"
        out_dir.mkdir(parents=True, exist_ok=True)

        eve_path = out_dir / (base + ".eve")        # text events file
        tsv_path = out_dir / (base + "_detail.tsv") # optional richer table
        print("[DEBUG] output base:", base)
        print("[DEBUG] will write:", "eve=", eve_path, "tsv=", tsv_path)

        # Optional guard so re-runs don’t crash if you didn’t pass --overwrite
        if eve_path.exists() and not args.overwrite:
            print(f"  {eve_path.name} already exists — skipping (use --overwrite to replace).")
            continue

        # 1) Write the canonical MNE events file
        mne.write_events(str(eve_path), events, overwrite=args.overwrite)
        print(f"Wrote MNE events: {eve_path} (n={len(events)})")

        # 2) Rich TSV for auditability
        pd.DataFrame(detail_rows).sort_values("sample").to_csv(tsv_path, sep="\t", index=False)
        print(f"Wrote detail TSV: {tsv_path}")



        index_rows.append({
            "subject": entities.get("subject"),
            "file": str(raw_path),
            "events_eve": str(eve_path),
            "detail_tsv": str(tsv_path),
            "n_events": int(len(events)),
        })

# Write an index file
if index_rows:
    idx = pd.DataFrame(index_rows)
    idx_path = DERIV_ROOT / "auto_events_index.csv"
    idx.to_csv(idx_path, index=False)
    print(f"\nWrote events index: {idx_path}")
else:
    print("\nNo events were created.")
