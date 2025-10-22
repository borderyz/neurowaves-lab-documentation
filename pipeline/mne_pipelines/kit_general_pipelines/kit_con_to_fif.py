# kit2fiff_from_config.py
# Convert KIT .con to .fif using a YAML config (generic across datasets).
# Output root is always: <BIDS_ROOT>/derivatives/kit2fiff/
# Ordering & pairing:
#   - .con grouped by run (if present), ordered by split (if present)
#   - .mrk ordered by acquisition (acq-XX) and paired per run-group:
#       group i → [mrk[i], mrk[i+1]] if available, else [mrk[i]]
#   - Never reuse a “way-before” MRK for later groups
#
# Robustness notes:
#   - Handles missing run and/or split (treated as 0 for ordering)
#   - Handles missing/short MRK lists (skips groups without MRKs)
#   - Session-aware HSP/ELP selection (per .con); falls back to subject-level if needed
#   - Edits (drops last 3 cols) and caches ELP “_edited.txt” per (sub, ses, source)
#   - YAML uses [] by default; [] / "" / {} / None → treated as not specified

import argparse
import os
from pathlib import Path
from collections import defaultdict
import yaml
import pandas as pd
import mne
from mne_bids import find_matching_paths, get_entity_vals

from pipeline.mne_pipelines.kit_general_pipelines.utilities import (
    NYUAD_KIT_CONSTANTS as C,
    bids_name_from_entities,
)

DESC_TAG = "rawkit"  # desc-rawkit in output filenames


# -------------------------------
# Helpers
# -------------------------------
def _safe_int(x, default=0):
    try:
        if x is None:
            return default
        return int(str(x))
    except Exception:
        return default


def _sort_by_entity(matches, entity_key):
    """Sort by a numeric entity (e.g., 'acquisition', 'run', 'split'). Missing or non-numeric -> 0."""
    return sorted(matches, key=lambda m: _safe_int(m.entities.get(entity_key), 0))


def _none_if_empty(x):
    """Treat [], {}, '', None as not specified -> return None; otherwise return x."""
    if x in (None, "", [], {}):
        return None
    return x


def _group_cons_by_run_then_split(con_matches):
    """
    Group CON matches into ordered groups for MRK pairing.
    Primary key: run (numeric). Within each run, order by split (numeric).
    If run is missing on all, collapse everything into run=0; still order by split (0 if missing).
    Returns: list of (run_number, [con_matches_sorted_by_split]).
    """
    any_run = any(m.entities.get("run") is not None for m in con_matches)
    buckets = defaultdict(list)
    for m in con_matches:
        run_val = _safe_int(m.entities.get("run"), 0 if any_run else 0)
        buckets[run_val].append(m)

    grouped = []
    for run_key in sorted(buckets.keys()):
        by_split = sorted(buckets[run_key], key=lambda m: _safe_int(m.entities.get("split"), 0))
        grouped.append((run_key, by_split))
    return grouped


def pair_mrks_to_con_groups(con_matches, mrk_matches):
    """
    Build MRK pairing per CON group using acq/run+split policy:
      - Order MRKs by acquisition number (acq).
      - Build CON groups by run; within each run, order by split.
      - Group i uses [mrk[i], mrk[i+1]] if both exist, else [mrk[i]] if only that exists,
        else [] (no MRK → skip).
    Returns:
      groups: list of (run_key, [con_items_sorted_by_split])
      per_group_mrks: list of lists of Paths (either [before, after] or [only])
    """
    groups = _group_cons_by_run_then_split(con_matches)
    mrks_sorted = _sort_by_entity(mrk_matches, "acquisition")
    mrk_paths = [Path(m.fpath) for m in mrks_sorted]

    per_group_mrks = []
    for i, _ in enumerate(groups):
        if i < len(mrk_paths):
            if (i + 1) < len(mrk_paths):
                per_group_mrks.append([mrk_paths[i], mrk_paths[i + 1]])  # before & after
            else:
                per_group_mrks.append([mrk_paths[i]])  # only before
        else:
            per_group_mrks.append([])  # none → skip group
    return groups, per_group_mrks


def write_edited_points(points_path: Path, out_dir: Path) -> Path:
    """
    Reads a headshape 'points' file, drops last 3 columns, writes an edited copy.
    Assumes first 3 lines are header comments (KIT convention).
    Returns the path to the edited file.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (points_path.stem + "_edited.txt")

    # Use whitespace sep; skip a typical 3-line header if present
    df = pd.read_csv(points_path, sep=r"\s+", skiprows=3, header=None, engine="python")
    # Safeguard: only drop if >= 6 cols
    if df.shape[1] >= 6:
        df = df.drop(df.columns[[3, 4, 5]], axis=1)
    df.to_csv(out_path, sep=" ", index=False, header=False)
    return out_path


def resolve_hsp_elp_for_entities(
    bids_root: str,
    sub: str,
    entities: dict,
    sessions=None,
    tasks=None,
    runs=None,
):
    """
    Find HSP (headshape) and ELP (digitizer points) for the given file's entities, preferring same session.
    Fallback order:
      1) match subject + this session (if present)
      2) match subject (no session constraint)
    Returns: (hsp_path: Path, points_path: Path) or (None, None) if not found
    """
    ses = entities.get("session")

    # First try session-specific
    head_matches = find_matching_paths(
        bids_root,
        datatypes=C.DATATYPE,
        subjects=sub,
        sessions=[ses] if ses else sessions,
        tasks=tasks,
        runs=runs,
        acquisitions=C.ACQ_LABEL_DIGITIZER_HEAD,
        extensions=tuple(C.HEADSHAPE_EXTENSIONS),
    )
    points_matches = find_matching_paths(
        bids_root,
        datatypes=C.DATATYPE,
        subjects=sub,
        sessions=[ses] if ses else sessions,
        tasks=tasks,
        runs=runs,
        acquisitions=C.ACQ_LABEL_DIGITIZER_POINTS,
        extensions=tuple(C.HEADSHAPE_EXTENSIONS),
    )

    if not head_matches or not points_matches:
        # Fallback: subject-level search without session filter
        head_matches = head_matches or find_matching_paths(
            bids_root,
            datatypes=C.DATATYPE,
            subjects=sub,
            acquisitions=C.ACQ_LABEL_DIGITIZER_HEAD,
            extensions=tuple(C.HEADSHAPE_EXTENSIONS),
        )
        points_matches = points_matches or find_matching_paths(
            bids_root,
            datatypes=C.DATATYPE,
            subjects=sub,
            acquisitions=C.ACQ_LABEL_DIGITIZER_POINTS,
            extensions=tuple(C.HEADSHAPE_EXTENSIONS),
        )

    if not head_matches or not points_matches:
        return None, None

    return Path(head_matches[0].fpath), Path(points_matches[0].fpath)


# -------------------------------
# Main
# -------------------------------
def main():
    # CLI
    parser = argparse.ArgumentParser(
        description="Create FIFF files from KIT data for a BIDS MEG dataset using a YAML config."
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

    # Subjects: empty include => ALL
    sub_cfg = CFG.get("subjects", {}) or {}
    include = sub_cfg.get("include") or []
    exclude = set(sub_cfg.get("exclude") or [])

    all_subjects = get_entity_vals(bids_root, entity_key="subject")
    subjects = sorted(s for s in (include or all_subjects) if s not in exclude)
    print(f"Subjects to process ({len(subjects)}): {subjects}")

    # Optional BIDS selections (empty arrays [] -> treated as None)
    sel = CFG.get("bids_selection", {}) or {}
    sessions    = _none_if_empty(sel.get("sessions"))
    tasks       = _none_if_empty(sel.get("tasks"))
    runs        = _none_if_empty(sel.get("runs"))
    splits      = _none_if_empty(sel.get("splits"))
    processings = _none_if_empty(sel.get("processings"))

    # Fixed derivatives location (BIDS): derivatives/kit2fiff
    DERIV_ROOT = Path(bids_root) / "derivatives" / "kit2fiff"
    DERIV_ROOT.mkdir(parents=True, exist_ok=True)

    # Cache for edited points so we don't rewrite per file unnecessarily
    edited_points_cache = {}  # key: (sub, session_or_None, original_points_path) -> edited_path

    # Main loop
    for sub in subjects:
        print("\n" + "=" * 70)
        print(f"Subject: {sub}")
        print("=" * 70)

        # Find KIT raw files (supports sessions/tasks/runs/splits/processings)
        raw_matches = find_matching_paths(
            bids_root,
            datatypes=C.DATATYPE,
            subjects=sub,
            sessions=sessions,
            tasks=tasks,
            runs=runs,
            splits=splits,  # may be None
            processings=tuple(processings) if processings else None,
            extensions=tuple(C.MEG_EXTENSIONS),
        )
        if not raw_matches:
            print(f"⚠️  No MEG files found for sub-{sub}.")
            continue

        # Pair MRKs per run-group (we fetch MRKs subject-wide; acq-order is global for this subject/session selection)
        mrk_matches = find_matching_paths(
            bids_root,
            datatypes=C.DATATYPE,
            subjects=sub,
            sessions=sessions,
            tasks=tasks,
            runs=runs,
            extensions=tuple(C.HEAD_POSITION_INDICATOR_EXTENSIONS),
        )

        if not mrk_matches:
            print(f"⚠️  Missing MRK files for sub-{sub}; skipping subject.")
            continue

        groups, per_group_mrks = pair_mrks_to_con_groups(raw_matches, mrk_matches)

        # Derivatives subject-level root
        sub_deriv_root = DERIV_ROOT / f"sub-{sub}"
        sub_deriv_root.mkdir(parents=True, exist_ok=True)

        for (run_key, con_list), mrk_for_group in zip(groups, per_group_mrks):
            if not mrk_for_group:
                run_label = f"{run_key:02d}"
                print(f"⚠️  No suitable MRK for run-{run_label}; skipping its {len(con_list)} file(s).")
                continue

            # Convert each CON in this run-group, in split order
            for raw_match in con_list:
                entities = raw_match.entities
                con_file = Path(raw_match.fpath)

                # Resolve HSP/ELP per-file entities (session-aware), with fallback
                hsp_path, points_path = resolve_hsp_elp_for_entities(
                    bids_root, sub, entities, sessions=sessions, tasks=tasks, runs=runs
                )
                if not hsp_path or not points_path:
                    print(f"⚠️  Missing headshape or points for {con_file}; skipping this file.")
                    continue

                # session folder if present
                run_deriv = sub_deriv_root
                ses = entities.get("session")
                if ses:
                    run_deriv = run_deriv / f"ses-{ses}"
                    run_deriv.mkdir(parents=True, exist_ok=True)

                # Make or reuse edited points (drop last 3 cols)
                cache_key = (sub, ses if ses else None, str(points_path))
                if cache_key in edited_points_cache:
                    edited_points_path = edited_points_cache[cache_key]
                else:
                    try:
                        edited_points_path = write_edited_points(points_path, run_deriv)
                        edited_points_cache[cache_key] = edited_points_path
                        print(f"Edited points saved: {edited_points_path}")
                    except Exception as e:
                        print(f"⚠️  Failed to create edited points for {con_file}: {e}")
                        continue

                print("\n--- Converting ---")
                print(f"CON: {con_file}")
                print(f"HSP: {hsp_path}")
                print(f"ELP: {edited_points_path}")
                print(f"MRK: {mrk_for_group}")

                raw = mne.io.read_raw_kit(
                    input_fname=str(con_file),
                    mrk=[str(p) for p in mrk_for_group],
                    elp=str(edited_points_path),
                    hsp=str(hsp_path),
                    preload=False,
                    verbose=False,
                )

                # Name includes run and split if present; desc fixed to DESC_TAG
                out_name = bids_name_from_entities(entities, f"desc-{DESC_TAG}", "_meg_raw.fif")
                out_path = run_deriv / out_name
                raw.save(str(out_path), overwrite=True)
                raw.close()
                print(f"✓ Saved FIFF: {out_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
