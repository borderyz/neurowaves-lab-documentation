import os

import json
from pathlib import Path

from boxsdk import Client
from boxsdk.auth.jwt_auth import JWTAuth


def _has_local_dataset(p: Path) -> bool:
    return p.exists() and any(p.iterdir())

def _box_client():

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

def _box_mirror_folder(client, folder_id: str, out_dir: Path, exclude_folders: list = None) -> None:
    """Mirror a Box folder to local directory, optionally excluding specified folders.
    
    Args:
        client: Box client instance
        folder_id: Box folder ID to mirror
        out_dir: Local output directory
        exclude_folders: List of folder names to skip (e.g., ["derivatives"])
    """
    if exclude_folders is None:
        exclude_folders = []
    
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
                    # Skip excluded folders
                    if item.name not in exclude_folders:
                        _walk(item.id, local / item.name)
            if count < limit:
                break
            offset += limit
    _walk(folder_id, out_dir)


def ensure_dataset_present(project_name: str, meg_data_root: Path) -> Path:
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

    # Exclude derivatives folder to ensure tests generate fresh outputs
    _box_mirror_folder(client, dataset_folder_id, bids_root, exclude_folders=["derivatives"])
    if not _has_local_dataset(bids_root):
        raise AssertionError(f"Downloaded dataset appears empty at {bids_root}")
    return bids_root