"""
Script to list datasets in a Box folder or get information about a specific dataset.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# --- Box SDK imports ---
try:
    from boxsdk import Client, JWTAuth
except ImportError:
    print("Error: boxsdk not installed. Please run: pip install 'boxsdk[jwt]'")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOG = logging.getLogger("box_info")


def get_box_client(config_json_str: str | None = None) -> Client:
    """Initialize Box Client using JWT config from environment variable."""
    if not config_json_str:
        config_json_str = os.environ.get("BOX_CLIENT_SDK_CONFIG")
    
    if not config_json_str:
        raise RuntimeError("Missing Box config. Set BOX_CLIENT_SDK_CONFIG env var.")

    try:
        settings = json.loads(config_json_str)
    except json.JSONDecodeError as e:
        raise RuntimeError("BOX_CLIENT_SDK_CONFIG is not valid JSON") from e

    auth = JWTAuth.from_settings_dictionary(settings)
    client = Client(auth)
    # Validate token
    client.user(user_id="me").get()
    return client


def list_datasets(client: Client, folder_id: str):
    """List all subfolders (datasets) in the given Box folder."""
    LOG.info(f"Listing datasets in Box folder ID: {folder_id}")
    
    try:
        folder = client.folder(folder_id).get()
        LOG.info(f"Root Folder Name: {folder.name}")
        LOG.info("-" * 40)
        LOG.info(f"{'Name':<40} | {'ID':<15}")
        LOG.info("-" * 40)

        items = folder.get_items(limit=1000, fields=["id", "name", "type"])
        count = 0
        for item in items:
            if item.type == "folder":
                LOG.info(f"{item.name:<40} | {item.id:<15}")
                count += 1
        
        LOG.info("-" * 40)
        LOG.info(f"Total Datasets Found: {count}")

    except Exception as e:
        LOG.error(f"Failed to list datasets: {e}")
        sys.exit(1)


def get_dataset_info(client: Client, parent_folder_id: str, dataset_name: str):
    """Find a specific dataset by name and print its details."""
    LOG.info(f"Searching for dataset '{dataset_name}' in folder {parent_folder_id}...")

    try:
        # Search for the folder by name in the parent folder
        # Note: Box search API is global, but we can iterate or use search with ancestor_folder_ids
        # Iterating is safer for exact name match in a specific parent without search index lag
        
        target_folder = None
        offset = 0
        limit = 1000
        
        while True:
            items = client.folder(parent_folder_id).get_items(
                limit=limit, offset=offset, fields=["id", "name", "type"]
            )
            found_any = False
            for item in items:
                found_any = True
                if item.type == "folder" and item.name == dataset_name:
                    target_folder = item
                    break
            
            if target_folder or not found_any:
                break
            offset += limit

        if not target_folder:
            LOG.error(f"Dataset '{dataset_name}' not found in folder {parent_folder_id}.")
            sys.exit(1)

        # Get detailed info
        folder_details = client.folder(target_folder.id).get(
            fields=["id", "name", "size", "item_collection", "created_at", "modified_at", "description"]
        )

        LOG.info("=" * 40)
        LOG.info(f"DATASET INFO: {folder_details.name}")
        LOG.info("=" * 40)
        LOG.info(f"ID:           {folder_details.id}")
        LOG.info(f"Size:         {folder_details.size} bytes")
        LOG.info(f"Item Count:   {folder_details.item_collection['total_count']}")
        LOG.info(f"Created At:   {folder_details.created_at}")
        LOG.info(f"Modified At:  {folder_details.modified_at}")
        if folder_details.description:
            LOG.info(f"Description:  {folder_details.description}")
        LOG.info("=" * 40)

    except Exception as e:
        LOG.error(f"Failed to get dataset info: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Box Dataset Info Tool")
    parser.add_argument("--box-folder-id", required=True, help="Box Root Folder ID")
    parser.add_argument("--dataset-name", help="Name of the dataset to inspect. If omitted, lists all.")
    
    args = parser.parse_args()

    try:
        client = get_box_client()
    except Exception as e:
        LOG.error(f"Authentication failed: {e}")
        sys.exit(1)

    if args.dataset_name:
        get_dataset_info(client, args.box_folder_id, args.dataset_name)
    else:
        list_datasets(client, args.box_folder_id)


if __name__ == "__main__":
    main()
