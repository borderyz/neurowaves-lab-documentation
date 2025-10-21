# sanity_single_channel_check.py
# Run a sanity single-channel trigger count check for an NYUAD-KIT MEG dataset.

import argparse
import os
import sys
from pathlib import Path
import json
import yaml
import pandas as pd
import numpy as np

import mne
from mne_bids import find_matching_paths, get_entity_vals

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

def _glyph(ok: bool) -> str:
    """Windows-safe status glyph."""
    enc = (sys.stdout.encoding or "").lower()
    if "utf" in enc:
        return "✅" if ok else "❌"
    return "OK" if ok else "FAIL"

# -------------------------------
# Pulse detector (robust thresholds + metrics)
# -------------------------------
def detect_pulses_on_channel(
    raw, ch_name,
    absolute_floor=0.3,
    mad_mult=12.0,
    hysteresis_frac=0.8,
    min_width_ms=3.0,
    min_distance_ms=6.0,
    baseline_s=None,
    baseline_q=0.7,      # use only lower tail (<= quantile) for baseline
    min_baseline_n=256   # minimum samples required in baseline pool
):
    """
    Detect digital-like trigger pulses on a single MNE Raw channel using
    trimmed (lower-tail) robust thresholding, hysteresis, and debouncing.

    Returns:
      pulses_idx (np.ndarray): start sample indices of accepted pulses.
      thr_hi (float): high threshold.
      thr_lo (float): low threshold (hysteresis).
      pulse_metrics (list[dict]): one dict per pulse with:
         - start (int): start sample
         - end (int): end sample (first sample below thr_lo)
         - width_samp (int)
         - width_ms (float)
         - amp_max (float): max |amplitude| within [start:end)
         - amp_mean (float): mean |amplitude| within [start:end)
    """
    sfreq = raw.info['sfreq']
    min_width_samp = max(1, int(round((min_width_ms / 1000.0) * sfreq)))
    min_distance_samp = max(1, int(round((min_distance_ms / 1000.0) * sfreq)))

    pick = mne.pick_channels(raw.ch_names, [ch_name])
    if len(pick) == 0:
        raise ValueError(f"Channel '{ch_name}' not found in raw.")
    x = raw.get_data(picks=pick, reject_by_annotation='omit')[0]

    # Threshold estimation segment
    if baseline_s is not None:
        start_s, stop_s = baseline_s
        start = max(0, int(round(start_s * sfreq)))
        stop  = min(len(x), int(round(stop_s * sfreq)))
        xb = x[start:stop] if stop > start else x
    else:
        xb = x

    # Lower-tail robust baseline
    ax = np.abs(xb)
    if ax.size == 0:
        raise RuntimeError("Empty data segment for threshold estimation.")
    baseline_q = float(baseline_q)
    baseline_q = 0.99 if baseline_q > 0.99 else (0.01 if baseline_q < 0.01 else baseline_q)
    qv = np.quantile(ax, baseline_q)
    pool = ax[ax <= qv]
    if pool.size < min_baseline_n:
        qv2 = np.quantile(ax, 0.9)
        pool = ax[ax <= qv2]
        if pool.size < min_baseline_n:
            pool = ax  # last resort

    med = np.median(pool)
    mad = np.median(np.abs(pool - med)) + 1e-12

    thr_hi = max(absolute_floor, med + mad_mult * mad)
    thr_lo = hysteresis_frac * thr_hi

    # Hysteretic detection + per-pulse metrics
    pulses = []
    metrics = []
    i = 1
    n = x.size
    last_accept = -10**9

    while i < n:
        if x[i - 1] < thr_hi <= x[i]:
            start_i = i
            while i < n and x[i] >= thr_lo:
                i += 1
            end_i = i  # first sample below thr_lo
            width = end_i - start_i
            if width >= min_width_samp and (start_i - last_accept) >= min_distance_samp:
                pulses.append(start_i)
                last_accept = start_i

                seg = np.abs(x[start_i:end_i]) if end_i > start_i else np.empty(0, dtype=float)
                amp_max = float(np.max(seg)) if seg.size else 0.0
                amp_mean = float(np.mean(seg)) if seg.size else 0.0
                width_ms = (width / sfreq) * 1000.0

                metrics.append({
                    "start": int(start_i),
                    "end": int(end_i),
                    "width_samp": int(width),
                    "width_ms": float(width_ms),
                    "amp_max": amp_max,
                    "amp_mean": amp_mean,
                })
        else:
            i += 1

    return np.asarray(pulses, dtype=int), float(thr_hi), float(thr_lo), metrics


# -------------------------------
# Pairing helpers
# -------------------------------

def _entities_exact_match(candidate, scope):
    """
    Return True iff the candidate's entities match the scope *exactly*:
      - If scope[k] is None -> candidate must NOT have that entity.
      - If scope[k] has a value -> candidate must have the same value.
    """
    ents = (getattr(candidate, "entities", None) or {})
    for k in ("subject", "session", "task", "acquisition", "run"):
        want = scope.get(k)
        have = ents.get(k)
        if want is None:
            if have is not None:
                return False
        else:
            if have != want:
                return False
    return True


def _first_matching_path_exact(*, subjects, sessions, tasks, acquisitions, runs, extensions):
    """
    Find the first file whose entities match the query *exactly*.
    Unlike passing None to find_matching_paths (which means 'no filtering'),
    this enforces that missing entities remain missing.
    """
    cands = find_matching_paths(
        bids_root,
        datatypes=C.DATATYPE,
        subjects=subjects,
        sessions=sessions,
        tasks=tasks,
        acquisitions=acquisitions,
        runs=runs,
        extensions=extensions,
        suffixes="events",
    )
    if not cands:
        return None

    scope = dict(subject=subjects, session=sessions, task=tasks,
                 acquisition=acquisitions, run=runs)

    for cand in cands:
        if _entities_exact_match(cand, scope):
            return cand.fpath
    return None





def resolve_events_pair_with_joint_fallback(raw_match):
    e = raw_match.entities or {}
    subj = e.get("subject")
    sess = e.get("session")
    task = e.get("task")
    run  = e.get("run")
    acq  = e.get("acquisition")

    scopes = [
        dict(subject=subj, session=sess, task=task, run=run, acquisition=acq),           # exact
        dict(subject=subj, session=sess, task=task, run=None, acquisition=None),         # drop run/acq
        dict(subject=subj, session=sess, task=None, run=None, acquisition=None),         # subject(/session) only
        dict(subject=None, session=None, task=None, run=None, acquisition=None),         # dataset root
    ]

    for scope in scopes:
        tbl = _first_matching_path_exact(
            subjects=scope["subject"], sessions=scope["session"],
            tasks=scope["task"], acquisitions=scope["acquisition"],
            runs=scope["run"], extensions=tuple(C.EVENTS_EXTENSIONS),
        )
        if not tbl:
            continue

        js = _first_matching_path_exact(
            subjects=scope["subject"], sessions=scope["session"],
            tasks=scope["task"], acquisitions=scope["acquisition"],
            runs=scope["run"], extensions=tuple(C.METADATA_EXTENSIONS),
        )
        if not js:
            # Require a *paired* JSON at the *same* scope
            continue

        return tbl, js, scope

    return None, None, None




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

        # Resolve a PAIRED table+json with safe fallback
        events_table_path, events_json_path, scope = resolve_events_pair_with_joint_fallback(raw_match)

        if not events_json_path:
            print(f"⚠️  No suitable events JSON (paired) for: {raw_path} — skipping.")
            summary_records.append({
                "subject": sub, "file": raw_path, "pass": False,
                "comments": "Missing/invalid events JSON (no paired scope)"
            })
            continue

        if not events_table_path:
            print(f"⚠️  Single-channel requires events table, but none found (paired) for: {raw_path}")
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
            print(f"ℹ️  TriggerMode='{trigger_mode}' → not single_channel; skipping run.")
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
            f"Events: {events_table_path}",
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
