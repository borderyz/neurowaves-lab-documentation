# tests/test_sanity_pipeline.py
import os
import sys
import json
from pathlib import Path
import runpy
import subprocess
import pandas as pd
import yaml
from unittest.mock import patch


def _has_local_dataset(p: Path) -> bool:
    return p.exists() and any(p.iterdir())

def _box_client():
    from boxsdk import Client
    from boxsdk.auth.jwt_auth import JWTAuth
    cfg_json = os.environ.get("BOX_CLIENT_SDK_CONFIG")
    if not cfg_json:
        raise RuntimeError("BOX_CLIENT_SDK_CONFIG is not set")
    try:
        settings = json.loads(cfg_json)
    except json.JSONDecodeError as e:
        raise RuntimeError("Invalid JSON in BOX_CLIENT_SDK_CONFIG") from e
    auth = JWTAuth.from_settings_dictionary(settings)
    client = Client(auth)
    _ = client.user(user_id="me").get()  # validate creds
    return client

def _box_find_dataset_folder_id_direct(client, *, parent_folder_id: str, dataset_name: str) -> str:
    """Return the id of the folder named dataset_name directly under parent_folder_id."""
    items = client.folder(parent_folder_id).get_items(limit=1000, fields=["id", "name", "type"])
    for it in items:
        if it.type == "folder" and it.name == dataset_name:
            return it.id
    raise RuntimeError(
        f"Dataset '{dataset_name}' not found directly under Box folder {parent_folder_id}."
    )

def _box_mirror_folder(client, folder_id: str, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    def _walk(fid: str, local: Path):
        local.mkdir(parents=True, exist_ok=True)
        offset, limit = 0, 1000
        while True:
            batch = client.folder(fid).get_items(limit=limit, offset=offset, fields=["id","name","type","size"])
            count = 0
            for item in batch:
                count += 1
                if item.type == "file":
                    tgt = local / item.name
                    tgt.parent.mkdir(parents=True, exist_ok=True)
                    with open(tgt, "wb") as fh:
                        client.file(item.id).download_to(fh)
                elif item.type == "folder":
                    _walk(item.id, local / item.name)
            if count < limit:
                break
            offset += limit
    _walk(folder_id, out_dir)

def _ensure_dataset_present(project_name: str, meg_data_root: Path) -> Path:
    bids_root = meg_data_root / project_name
    if _has_local_dataset(bids_root):
        return bids_root  # local dev: already present

    # CI path: fetch from Box
    dataset_folder_id = os.getenv("BOX_DATASET_FOLDER_ID")  # optional direct dataset folder id
    parent_folder_id = os.getenv("BOX_MEG_DATA_PARENT_FOLDER_ID")    # REQUIRED if dataset id not provided
    if not os.getenv("BOX_CLIENT_SDK_CONFIG"):
        raise AssertionError(
            f"{bids_root} not found and no Box creds; set BOX_CLIENT_SDK_CONFIG "
            f"+ (BOX_DATASET_FOLDER_ID or BOX_MEG_DATA_PARENT_FOLDER_ID)."
        )

    client = _box_client()
    if not dataset_folder_id:
        if not parent_folder_id:
            raise AssertionError("BOX_MEG_DATA_PARENT_FOLDER_ID is required when BOX_DATASET_FOLDER_ID is not set.")
        dataset_folder_id = _box_find_dataset_folder_id_direct(
            client, parent_folder_id=parent_folder_id, dataset_name=project_name
        )

    _box_mirror_folder(client, dataset_folder_id, bids_root)
    if not _has_local_dataset(bids_root):
        raise AssertionError(f"Downloaded dataset appears empty at {bids_root}")
    return bids_root

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

    bids_root = _ensure_dataset_present(project_name, meg_data_root)

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
    script_path = repo_root / "pipeline" / "mne_pipelines" / "kit_general_pipelines" / "plot_triggers.py"

    # The script hardcodes:
    project_name = "script-testing-dataset"

    # MEG_DATA root (provided by CI env; local users already have it)
    meg_data_root = os.getenv("MEG_DATA")
    assert meg_data_root, "MEG_DATA environment variable not set"
    meg_data_root = Path(meg_data_root)

    # Ensure dataset exists (local or Box)
    _ensure_dataset_present(project_name, meg_data_root)

    # Headless plotting: force non-GUI backend for matplotlib used inside the script
    monkeypatch.setenv("MPLBACKEND", "Agg")

    # Patch mne Raw.plot to a no-op so the script doesn't block on GUI
    # (The method lives on BaseRaw; accept any args/kwargs)
    def _noop_plot(*args, **kwargs):
        return None

    with patch("mne.io.base.BaseRaw.plot", side_effect=_noop_plot):
        # Run the script as __main__ so its top-level code executes
        result = runpy.run_path(str(script_path), run_name="__main__")
        # No specific outputs to assert; success means no exceptions.
        assert result is not None
