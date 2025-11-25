# tests/test_pipelines_kit_mne.py
import os
import sys
from pathlib import Path
import runpy
import subprocess
import pandas as pd
import yaml
from unittest.mock import patch
import mne

from pipeline.box_storage.box_utilities import ensure_dataset_present


def test_sanity_check_pipeline():
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "1-kit_count_sanity_check_single_channel.py"
    config_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "pipeline_config_files" / "config_template.yml"

    # Load config to get project + MEG_DATA location
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f) or {}
    proj = cfg.get("project", {}) or {}
    project_name = proj.get("name")
    assert project_name, "project.name missing in config_template.yml"
    root_env = proj.get("root_env", "MEG_DATA")

    meg_data_root_str = os.getenv(root_env)
    assert meg_data_root_str, f"{root_env} environment variable not set"
    meg_data_root = Path(meg_data_root_str)

    # Ensure dataset exists locally or fetch from Box
    bids_root = ensure_dataset_present(project_name, meg_data_root)

    # Run the sanity script
    result = subprocess.run(
        [sys.executable, str(script_path), "--config", str(config_path)],
        capture_output=True, text=True, check=False,
    )
    # Do not assert specific stdout; print for debugging only
    print("\n====== STDOUT ======\n", result.stdout)
    print("\n====== STDERR ======\n", result.stderr)
    assert result.returncode == 0, f"Script failed with exit code {result.returncode}"

    # Summary CSV presence
    # Updated to match script name folder
    summary_csv = bids_root / "derivatives" / "1-kit_count_sanity_check_single_channel" / "sanity_check_overview.csv"
    assert summary_csv.exists(), f"Summary CSV not found at {summary_csv}"

    # Validate summary contents
    df = pd.read_csv(summary_csv)
    assert not df.empty, "Summary CSV is empty"

    # Subjects included/excluded (no rows for test2)
    subjects = set(df["subject"].unique())
    assert subjects == {"test1", "test3"}, f"Unexpected subjects in summary: {subjects}"
    assert not df["file"].str.contains("sub-test2").any(), "Found entries for sub-test2 despite no MEG files"

    # All runs passed with full matches
    assert df["pass"].all(), "Some sanity checks failed unexpectedly"
    assert df["counts_match"].all(), "Unexpected count mismatch"
    assert df["row_order_match"].all(), "Unexpected order mismatch"

    # Each run should have 400 events
    assert (df["csv_events"] == 400).all(), "csv_events not equal to 400 for all runs"
    assert (df["detected_events"] == 400).all(), "detected_events not equal to 400 for all runs"

    # Ensure both tasks present for both subjects (falsepositive and 400events)
    for sub in ("test1", "test3"):
        files = df.loc[df["subject"] == sub, "file"]
        assert (files.str.contains("task-400events").any() and
                files.str.contains("task-falsepositive").any()), f"Missing expected tasks for sub-{sub}"

    print("\n✅ Sanity check pipeline test passed with expected multi-subject behavior!")


def test_kit2fiff_pipeline():
    """
    End-to-end test for KIT to FIF conversion:
      - Ensures dataset is present (local or via Box).
      - Runs the script with the template YAML.
      - Verifies root summary CSV exists and contains expected rows.
      - Verifies expected FIF basenames per subject & task (proc/no-proc preserved).
      - Verifies per-subject logfiles exist and contain expected content.
    """
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "2-kit_con_to_fif.py"
    config_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "pipeline_config_files" / "config_template.yml"
    assert script_path.exists(), f"KIT2FIFF script not found at {script_path}"
    assert config_path.exists(), f"Config template not found at {config_path}"

    # Load config to locate BIDS
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    proj = cfg.get("project", {}) or {}
    project_name = proj.get("name")
    assert project_name, "project.name missing in config_template.yml"
    root_env = proj.get("root_env", "MEG_DATA")

    meg_data_root_str = os.getenv(root_env)
    assert meg_data_root_str, f"{root_env} environment variable not set"
    meg_data_root = Path(meg_data_root_str)

    # Ensure dataset present
    bids_root = ensure_dataset_present(project_name, meg_data_root)

    # Run the conversion script
    result = subprocess.run(
        [sys.executable, str(script_path), "--config", str(config_path)],
        capture_output=True, text=True, check=False,
    )
    print("\n====== STDOUT ======\n", result.stdout)
    print("\n====== STDERR ======\n", result.stderr)
    assert result.returncode == 0, f"kit2fiff script failed with exit code {result.returncode}"

    # Paths under derivatives/2-kit_con_to_fif
    kit2fiff_root = bids_root / "derivatives" / "2-kit_con_to_fif"
    summary_csv = kit2fiff_root / "kit2fiff_summary.csv"
    assert summary_csv.exists(), f"Summary CSV not found at {summary_csv}"

    # Read summary and validate structure/content
    df = pd.read_csv(summary_csv)
    assert not df.empty, "Summary CSV is empty"
    assert {"subject", "con_path", "mrk_paths", "hsp_path", "elp_points_edited", "fif_out", "status"}.issubset(df.columns), \
        "Summary CSV missing expected columns"

    # Expected subjects behavior from the sample run:
    # - test1: conversions succeed (3 FIFs)
    # - test2: no MEG files -> no rows
    # - test3: missing MRKs -> no rows
    subjects_in_summary = set(df["subject"].unique())
    assert "test1" in subjects_in_summary, "Expected rows for sub-test1"
    assert "test2" not in subjects_in_summary, "Unexpected rows for sub-test2 (should have no MEG files)"
    assert "test3" not in subjects_in_summary, "Unexpected rows for sub-test3 (missing MRKs should skip)"

    # For test1, we expect exactly 3 FIF outputs:
    df1 = df[df["subject"] == "test1"].copy()
    assert len(df1) == 3, f"Expected 3 FIF rows for sub-test1, got {len(df1)}"

    # Check output filenames preserve all relevant entities (proc/no-proc, task)
    fif_basenames = {Path(p).name for p in df1["fif_out"].tolist()}
    expected_basenames = {
        # unprocessed 400events
        "sub-test1_task-400events_desc-rawkit_meg_raw.fif",
        # processed 400events (CALM)
        "sub-test1_task-400events_proc-CALMnoisereduction_desc-rawkit_meg_raw.fif",
        # unprocessed falsepositive
        "sub-test1_task-falsepositive_desc-rawkit_meg_raw.fif",
    }
    missing = expected_basenames - fif_basenames
    assert not missing, f"Missing expected FIFs: {missing}"

    # Ensure the corresponding CONs were logged (at least the expected tasks show up)
    con_paths = " ".join(df1["con_path"].astype(str).tolist())
    assert "task-400events" in con_paths and "task-falsepositive" in con_paths, \
        "Expected CON tasks not reflected in summary"

    # Check subject logfile exists and has mapping lines
    sub_log = kit2fiff_root / "sub-test1" / "kit2fiff_log.txt"
    assert sub_log.exists(), f"Per-subject log not found at {sub_log}"
    log_txt = sub_log.read_text(encoding="utf-8")

    # Minimal mapping lines must appear for each FIF
    for base in expected_basenames:
        assert base in log_txt, f"Output FIF {base} not mentioned in subject log"
    for key in ("CON :", "MRK :", "HSP :", "ELP*:", "OUT :", "STATUS:"):
        assert key in log_txt, f"Subject log missing mapping key '{key}'"

    # Sanity: edited points path points into derivatives and ends with _edited.txt
    edited_points = set(df1["elp_points_edited"].astype(str))
    assert all("derivatives" in p and p.endswith("_edited.txt") for p in edited_points), \
        "Edited points paths look wrong"

    print("\n✅ KIT→FIFF pipeline test passed (distinct outputs per proc/no-proc; logs & summary validated).")


def test_compute_events_single_channel_pipeline():
    """
    End-to-end test for building MNE events from single-channel triggers:
      - Ensures dataset is present (local or via Box).
      - Runs the script with the template YAML.
      - Verifies root index CSV exists and contains expected rows.
      - Verifies expected .eve/.tsv basenames per subject & task (proc/no-proc preserved).
      - Verifies n_events = 400 for every output and files are readable.
    """
    repo_root = Path(__file__).resolve().parents[1]

    # Script path: prefer kit_compute_events_single_channel.py; fallback to kit_make_events_from_triggers.py
    script_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "5-kit_compute_events_single_channel.py"
    if not script_path.exists():
        script_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "kit_make_events_from_triggers.py"
    assert script_path.exists(), f"Events script not found at {script_path}"

    config_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "pipeline_config_files" / "config_template.yml"
    assert config_path.exists(), f"Config template not found at {config_path}"

    # Load config to locate BIDS
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    proj = cfg.get("project", {}) or {}
    project_name = proj.get("name")
    assert project_name, "project.name missing in config_template.yml"
    root_env = proj.get("root_env", "MEG_DATA")

    meg_data_root_str = os.getenv(root_env)
    assert meg_data_root_str, f"{root_env} environment variable not set"
    meg_data_root = Path(meg_data_root_str)

    # Ensure dataset present
    bids_root = ensure_dataset_present(project_name, meg_data_root)

    # Run the events script (default desc=autopulses)
    result = subprocess.run(
        [sys.executable, str(script_path), "--config", str(config_path)],
        capture_output=True, text=True, check=False,
    )
    print("\n====== STDOUT ======\n", result.stdout)
    print("\n====== STDERR ======\n", result.stderr)
    assert result.returncode == 0, f"Events script failed with exit code {result.returncode}"

    # Index CSV under derivatives/5-kit_compute_events_single_channel
    deriv_root = bids_root / "derivatives" / "5-kit_compute_events_single_channel"
    index_csv = deriv_root / "auto_events_index.csv"
    assert index_csv.exists(), f"Events index CSV not found at {index_csv}"

    # Read and validate
    df = pd.read_csv(index_csv)
    assert not df.empty, "Events index CSV is empty"
    assert {"subject", "file", "events_eve", "detail_tsv", "n_events"}.issubset(df.columns), \
        "Index CSV missing expected columns"

    # Expected subjects behavior from your sample run:
    # - test1: outputs exist (400events no-proc + 400events proc-CALM + falsepositive)
    # - test2: no MEG files -> no rows
    # - test3: outputs exist (400events + falsepositive)
    subs = set(df["subject"].dropna().astype(str))
    assert "test1" in subs, "Expected rows for sub-test1"
    assert "test3" in subs, "Expected rows for sub-test3"
    assert "test2" not in subs, "Unexpected rows for sub-test2 (should have no MEG files)"

    df1 = df[df["subject"] == "test1"].copy()
    df3 = df[df["subject"] == "test3"].copy()

    # Expected basenames
    expected_test1 = {
        "sub-test1_task-400events_desc-autopulses_events.eve",
        "sub-test1_task-400events_proc-CALMnoisereduction_desc-autopulses_events.eve",
        "sub-test1_task-falsepositive_desc-autopulses_events.eve",
    }
    expected_test3 = {
        "sub-test3_task-400events_desc-autopulses_events.eve",
        "sub-test3_task-falsepositive_desc-autopulses_events.eve",
    }

    got_test1 = {Path(p).name for p in df1["events_eve"].tolist()}
    got_test3 = {Path(p).name for p in df3["events_eve"].tolist()}

    missing1 = expected_test1 - got_test1
    missing3 = expected_test3 - got_test3
    assert not missing1, f"Missing expected test1 outputs: {missing1}"
    assert not missing3, f"Missing expected test3 outputs: {missing3}"

    # All outputs should have n_events == 400
    assert (df1["n_events"] == 400).all(), "test1: n_events not equal to 400 for all outputs"
    assert (df3["n_events"] == 400).all(), "test3: n_events not equal to 400 for all outputs"

    # Files exist and are readable; detail TSV has expected columns
    expected_detail_cols = {"sample", "onset_s", "channel_mne", "channel_kit", "event_id", "width_ms", "amp_max", "amp_mean"}

    for _, row in pd.concat([df1, df3]).iterrows():
        eve_path = Path(row["events_eve"])
        tsv_path = Path(row["detail_tsv"])
        assert eve_path.exists(), f"Missing .eve file: {eve_path}"
        assert tsv_path.exists(), f"Missing detail TSV: {tsv_path}"

        # Read .eve with MNE and confirm count
        events = mne.read_events(str(eve_path))
        assert events.shape[0] == int(row["n_events"]), f"Event count mismatch in {eve_path}"

        # Check TSV schema minimally
        tsv_df = pd.read_csv(tsv_path, sep="\t")
        assert expected_detail_cols.issubset(tsv_df.columns), f"Detail TSV missing columns: {tsv_path}"

    # Also ensure both tasks present per subject in index (sanity)
    for sub, tasks in [("test1", ("400events", "falsepositive")), ("test3", ("400events", "falsepositive"))]:
        files = df.loc[df["subject"] == sub, "file"].astype(str)
        assert all(any(f"task-{t}" in s for s in files) for t in tasks), f"Missing expected tasks for sub-{sub}"

    print("\n✅ Single-channel trigger → MNE events pipeline test passed (index, basenames, counts, files, schema).")