# This script serves as an example to run the sanity single-channel trigger count check for an MEG dataset obtained from NYUAD-KIT MEG system
# Hypothesis:
# - The dataset has triggers
# - Trigger events are coded on single channel of KIT system using channels 224-231
# - The analog signal is a single-frame pulse (typically lasting around 8.3 ms for 120Hz refresh rate screen)

import os
from pathlib import Path

import json
import pandas as pd

import mne
from mne.io import read_raw_kit
from mne_bids import (
    BIDSPath,
    find_matching_paths,
    get_entity_vals,
    make_report,
    print_dir_tree,
    read_raw_bids,
    get_datatypes
)

import matplotlib
matplotlib.use('TkAgg')


from pipeline.mne_pipelines.kit_general_pipelines.utilities import *

MEG_DATA_PATH = os.getenv("MEG_DATA")

# Convert to a Path object
if MEG_DATA_PATH:
    data_path = Path(MEG_DATA_PATH)
    print(f"Resolved path: {data_path.resolve()}")
else:
    raise EnvironmentError("MEG_DATA is not set.")


# Set the name of your dataset folder on NYU-BOX
PROJECT_NAME = "script-testing-dataset"

# Define the path to your dataset folder
# Using the `os` library ensure that this script is cross-platform (Linux, MacOS, Windows)
DATASET_PATH = os.path.join(MEG_DATA_PATH, PROJECT_NAME)

sub_id = "test1"

meg_data_file = find_matching_paths(DATASET_PATH,
                    datatypes=DATATYPE,
                    subjects=sub_id,
                    extensions=MEG_EXTENSIONS)

events_metadata_file = find_matching_paths(DATASET_PATH,
                                           datatypes=DATATYPE,
                                           subjects=sub_id,
                                           extensions=METADATA_EXTENSIONS,
                                           suffixes="events")

events_file = find_matching_paths(DATASET_PATH,
                    datatypes=DATATYPE,
                    subjects=sub_id,
                    extensions=EVENTS_EXTENSIONS,
                                      suffixes="events")


RAW_DATA = mne.io.read_raw_kit(meg_data_file[0], preload=False, verbose=False)

if len(events_metadata_file)==1:
    metadata_events = json.load(open(events_metadata_file[0].fpath))


events_data = pd.read_csv(events_file[0].fpath)

# TODO: if multiple events files are there, process them together with the corresponding .con files

if metadata_events["TriggerMode"]=="single_channel":
    print("Sanity check of data with single-channel trigger")

    ok = events_data["channel"].isin(trigger_channels_KIT).all()
    print(ok)

    counts = events_data["channel"].value_counts()



KIT_from_MNE = dict(zip(trigger_channels_MNE, trigger_channels_KIT))
MNE_from_KIT = dict(zip(trigger_channels_KIT, trigger_channels_MNE))

import numpy as np
import pandas as pd
import mne



KIT_from_MNE = dict(zip(trigger_channels_MNE, trigger_channels_KIT))
MNE_from_KIT = dict(zip(trigger_channels_KIT, trigger_channels_MNE))

# -----------------------------
# Robust per-channel pulse detector
# -----------------------------
def detect_pulses_on_channel(
    raw, ch_name,
    absolute_floor=0.3,      # <- minimal amplitude to be considered a real pulse (units = channel units)
    mad_mult=12.0,           # robust boost above baseline noise (used in addition to floor)
    hysteresis_frac=0.8,     # low threshold = hi * hysteresis_frac
    min_width_ms=3.0,        # min time above low threshold to accept a pulse
    min_distance_ms=6.0,     # refractory between pulses
    baseline_s=None          # optional (start_s, stop_s) for baseline estimation (e.g., first 5–10s)
):
    sfreq = raw.info['sfreq']
    min_width_samp = max(1, int(round((min_width_ms/1000.0)*sfreq)))
    min_distance_samp = max(1, int(round((min_distance_ms/1000.0)*sfreq)))

    pick = mne.pick_channels(raw.ch_names, [ch_name])
    if len(pick) != 1:
        raise ValueError(f"Channel {ch_name} not found.")
    x = raw.get_data(picks=pick, reject_by_annotation='omit')[0]

    # Use a baseline window if provided to estimate noise; else use the whole trace robustly
    if baseline_s is not None:
        start_s, stop_s = baseline_s
        start = max(0, int(round(start_s * sfreq)))
        stop  = min(len(x), int(round(stop_s * sfreq)))
        xb = x[start:stop] if stop > start else x
    else:
        xb = x

    # Robust noise-based high threshold
    ax = np.abs(xb)
    med = np.median(ax)
    mad = np.median(np.abs(ax - med)) + 1e-12
    thr_hi = max(absolute_floor, med + mad_mult * mad)  # <- floor ensures unused analog channels don't trigger
    thr_lo = hysteresis_frac * thr_hi

    pulses = []
    i = 1
    n = x.size
    last_accept = -10**9

    while i < n:
        # rising through high threshold
        if x[i-1] < thr_hi <= x[i]:
            start = i
            # stay above low threshold for width
            while i < n and x[i] >= thr_lo:
                i += 1
            width = i - start
            if width >= min_width_samp and (start - last_accept) >= min_distance_samp:
                pulses.append(start)
                last_accept = start
        else:
            i += 1

    return np.asarray(pulses, dtype=int), thr_hi, thr_lo

# -----------------------------
# Detect on ALL 8 channels, automatically handling "unused"
# -----------------------------
sfreq = RAW_DATA.info['sfreq']
detected_rows = []
threshold_log = []  # keep thresholds to inspect

# Optional: specify a baseline segment (e.g., first 10 s) to estimate noise more cleanly
BASELINE_WINDOW_S = (0.0, 10.0)  # set to None to use entire trace

for ch_mne in trigger_channels_MNE:
    if ch_mne not in RAW_DATA.ch_names:
        print(f"Warning: {ch_mne} missing; skipping.")
        continue

    pulses, thr_hi, thr_lo = detect_pulses_on_channel(
        RAW_DATA, ch_mne,
        absolute_floor=0.3,      # <-- tune this to your units; raise if you still see spurious counts
        mad_mult=12.0,
        hysteresis_frac=0.8,
        min_width_ms=3.0,
        min_distance_ms=6.0,
        baseline_s=BASELINE_WINDOW_S
    )
    threshold_log.append({"channel_mne": ch_mne, "thr_hi": float(thr_hi), "thr_lo": float(thr_lo), "n": int(len(pulses))})

    for s in pulses:
        detected_rows.append({
            "sample": int(s),
            "onset": float(s / sfreq),
            "channel_mne": ch_mne,
            "channel": KIT_from_MNE[ch_mne],
        })

detected_df = pd.DataFrame(detected_rows).sort_values("sample").reset_index(drop=True)
thr_df = pd.DataFrame(threshold_log)
print("\nThreshold summary per channel (hi/lo & detections):")
print(thr_df)

print(f"\nDetected {len(detected_df)} pulses total across 8 trigger channels.")

# -----------------------------
# Build the reference events from CSV
# -----------------------------
events_ref = events_data.copy()

# Require either sample or onset; compute sample if needed
if "sample" in events_ref.columns:
    events_ref["sample"] = events_ref["sample"].astype(int)
elif "onset" in events_ref.columns:
    events_ref["sample"] = np.round(events_ref["onset"].astype(float) * sfreq).astype(int)
else:
    raise ValueError("events CSV must include 'sample' or 'onset'.")

if "channel" not in events_ref.columns:
    raise ValueError("events CSV must include 'channel' (KIT codes).")

# Keep only the 8 trigger channels
events_ref = events_ref[events_ref["channel"].isin(trigger_channels_KIT)].copy()
events_ref["channel_mne"] = events_ref["channel"].map(MNE_from_KIT)
events_ref = events_ref.sort_values(["sample", "channel"]).reset_index(drop=True)

# -----------------------------
# CHECK #1: counts per channel (all 8)
# -----------------------------
counts_ref = events_ref["channel"].value_counts().sort_index().reindex(trigger_channels_KIT, fill_value=0)
counts_det = detected_df["channel"].value_counts().sort_index().reindex(trigger_channels_KIT, fill_value=0)

counts_compare = pd.DataFrame({
    "csv_count": counts_ref,
    "detected_count": counts_det,
    "diff": counts_det - counts_ref
})
print("\n=== Count comparison per KIT channel (224–231) ===")
print(counts_compare)

# -----------------------------
# CHECK #2: global order (time-ordered channel sequence)
# -----------------------------
seq_ref = events_ref.sort_values("sample")["channel"].to_numpy()
seq_det = detected_df.sort_values("sample")["channel"].to_numpy()

order_ok = (len(seq_ref) == len(seq_det)) and np.array_equal(seq_ref, seq_det)

print("\n=== Global order check ===")
print(f"CSV events:      {len(seq_ref)}")
print(f"Detected events: {len(seq_det)}")
print("✅ Order matches exactly." if order_ok else "❌ Order mismatch (or different lengths).")

# -----------------------------
# (Optional) jitter-tolerant matching, if small timing offsets are expected
# -----------------------------
# jitter_samp = int(round(0.004 * sfreq))  # +/- 4 ms
# csv_sorted = events_ref.sort_values("sample").reset_index(drop=True)
# det_sorted = detected_df.sort_values("sample").reset_index(drop=True)
# i = j = 0; matched = 0
# while i < len(csv_sorted) and j < len(det_sorted):
#     ds = det_sorted.loc[j, "sample"] - csv_sorted.loc[i, "sample"]
#     same_ch = det_sorted.loc[j, "channel"] == csv_sorted.loc[i, "channel"]
#     if abs(ds) <= jitter_samp and same_ch:
#         matched += 1; i += 1; j += 1
#     elif det_sorted.loc[j, "sample"] < csv_sorted.loc[i, "sample"] - jitter_samp:
#         j += 1
#     else:
#         i += 1
# print(f"\nMatched within tolerance: {matched}/{len(csv_sorted)}")







