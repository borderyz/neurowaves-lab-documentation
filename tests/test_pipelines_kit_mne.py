import subprocess
import pandas as pd
from pathlib import Path
import os
import yaml


def test_sanity_check_pipeline():
    """
    Integration test for kit_count_sanity_check_single_channel.py.
    Runs the script using the dummy dataset defined in config_template.yml
    and checks that the sanity check passes (counts + order correct).
    """

    # --- Paths ---
    repo_root = Path(__file__).resolve().parents[1]
    script_path = (
        repo_root
        / "pipeline"
        / "mne_pipelines"
        / "kit_general_pipelines"
        / "kit_count_sanity_check_single_channel.py"
    )
    config_path = (
        repo_root
        / "pipeline"
        / "mne_pipelines"
        / "kit_general_pipelines"
        / "pipeline_config_files"
        / "config_template.yml"
    )

    # --- Load config to extract project info ---
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
    proj_cfg = cfg.get("project", {})
    project_name = proj_cfg.get("name")
    root_env = proj_cfg.get("root_env", "MEG_DATA")

    # --- Ensure MEG_DATA is set ---
    meg_data_root = os.getenv(root_env)
    assert meg_data_root, f"{root_env} environment variable not set"
    meg_data_root = Path(meg_data_root)

    # --- Compute BIDS root exactly like the script does ---
    bids_root = meg_data_root / project_name

    # --- Run the actual script ---
    result = subprocess.run(
        ["python", str(script_path), "--config", str(config_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    print("\n====== STDOUT ======\n", result.stdout)
    print("\n====== STDERR ======\n", result.stderr)
    assert result.returncode == 0, f"Script failed with exit code {result.returncode}"

    # --- Check for the expected summary CSV ---
    summary_csv = bids_root / "derivatives" / "sanity_check" / "sanity_check_overview.csv"
    assert summary_csv.exists(), f"Summary CSV not found at {summary_csv}"

    # --- Validate its contents ---
    df = pd.read_csv(summary_csv)
    assert not df.empty, "Summary CSV is empty"
    assert df["pass"].all(), "Some sanity checks failed unexpectedly"
    assert df["counts_match"].all(), "Unexpected count mismatch"
    assert df["row_order_match"].all(), "Unexpected order mismatch"

    print("\n✅ Sanity check pipeline test passed successfully!")
