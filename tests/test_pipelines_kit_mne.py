# tests/test_sanity_pipeline.py
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

    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f) or {}
    proj = cfg.get("project", {}) or {}
    project_name = proj.get("name")
    assert project_name, "project.name missing in config_template.yml"
    root_env = proj.get("root_env", "MEG_DATA")

    meg_data_root_str = os.getenv(root_env)
    assert meg_data_root_str, f"{root_env} environment variable not set"
    meg_data_root = Path(meg_data_root_str)

    bids_root = ensure_dataset_present(project_name, meg_data_root)

    result = subprocess.run(
        [sys.executable, str(script_path), "--config", str(config_path)],
        capture_output=True, text=True, check=False,
    )
    print("\n====== STDOUT ======\n", result.stdout)
    print("\n====== STDERR ======\n", result.stderr)
    assert result.returncode == 0, f"Script failed with exit code {result.returncode}"

    summary_csv = bids_root / "derivatives" / "sanity_check" / "sanity_check_overview.csv"
    assert summary_csv.exists(), f"Summary CSV not found at {summary_csv}"

    df = pd.read_csv(summary_csv)
    assert not df.empty, "Summary CSV is empty"
    assert df["pass"].all(), "Some sanity checks failed unexpectedly"
    assert df["counts_match"].all(), "Unexpected count mismatch"
    assert df["row_order_match"].all(), "Unexpected order mismatch"

    print("\n✅ Sanity check pipeline test passed successfully!")


def test_plot_triggers_runs_headless_without_gui(tmp_path, monkeypatch):
    """
    Executes plot_triggers.py headlessly:
      - Ensures dataset present locally or downloads from Box.
      - Forces a non-interactive backend.
      - Patches Raw.plot to avoid opening a window (block=True in script).
    """
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "kit_plot_stim_channels.py"

    # The script hardcodes:
    project_name = "script-testing-dataset"

    # MEG_DATA root (provided by CI env; local users already have it)
    meg_data_root = os.getenv("MEG_DATA")
    assert meg_data_root, "MEG_DATA environment variable not set"
    meg_data_root = Path(meg_data_root)

    # Ensure dataset exists (local or Box)
    ensure_dataset_present(project_name, meg_data_root)


    # Patch mne Raw.plot to a no-op so the script doesn't block on GUI
    # (The method lives on BaseRaw; accept any args/kwargs)
    def _noop_plot(*args, **kwargs):
        return None

    with patch("mne.io.base.BaseRaw.plot", side_effect=_noop_plot):
        # Run the script as __main__ so its top-level code executes
        result = runpy.run_path(str(script_path), run_name="__main__")
        # No specific outputs to assert; success means no exceptions.
        assert result is not None
