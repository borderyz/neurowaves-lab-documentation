# tests/test_pipelines_kit_mne.py
import os
import sys
from pathlib import Path
import runpy
import subprocess
import pandas as pd
import yaml
from unittest.mock import patch

from pipeline.box_storage.box_utilities import ensure_dataset_present


def test_sanity_check_pipeline():
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "kit_count_sanity_check_single_channel.py"
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
    summary_csv = bids_root / "derivatives" / "sanity_check" / "sanity_check_overview.csv"
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



def test_kit2fiff_conversion_pipeline():
    """
    End-to-end test for the KIT -> FIFF conversion script:
      - Ensures dataset is present (local or via Box).
      - Runs the conversion script with the template YAML.
      - Verifies root summary CSV exists and contains expected rows.
      - Verifies unique output FIFs per input (proc/no-proc preserved).
      - Verifies per-subject logfile contains the mapping lines.
    """
    repo_root = Path(__file__).resolve().parents[1]
    # Update script name/path if yours differs:
    script_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "kit_con_to_fif.py"
    config_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "pipeline_config_files" / "config_template.yml"

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

    # Paths under derivatives/kit2fiff
    kit2fiff_root = bids_root / "derivatives" / "kit2fiff"
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

def test_plot_triggers_runs_headless_without_gui(tmp_path, monkeypatch):
    """
    Executes kit_plot_stim_channels.py headlessly:
      - Ensures dataset present locally or downloads from Box.
      - Forces a non-interactive backend.
      - Patches Raw.plot to avoid opening a window (block=True in the script).
    """
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "kit_plot_stim_channels.py"

    # The script hardcodes:
    project_name = "script-testing-dataset"

    # Headless plotting: force non-GUI backend
    monkeypatch.setenv("MPLBACKEND", "Agg")

    # MEG_DATA root (provided by CI env; local users already have it)
    meg_data_root = os.getenv("MEG_DATA")
    assert meg_data_root, "MEG_DATA environment variable not set"
    meg_data_root = Path(meg_data_root)

    # Ensure dataset exists (local or Box)
    ensure_dataset_present(project_name, meg_data_root)

    # Patch mne Raw.plot to a no-op so the script doesn't block on GUI
    def _noop_plot(*args, **kwargs):
        return None

    with patch("mne.io.base.BaseRaw.plot", side_effect=_noop_plot):
        # Run the script as __main__ so its top-level code executes
        result = runpy.run_path(str(script_path), run_name="__main__")
        assert result is not None
