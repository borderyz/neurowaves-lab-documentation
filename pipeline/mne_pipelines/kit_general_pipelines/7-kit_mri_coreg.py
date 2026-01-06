import argparse
import os
from pathlib import Path
import yaml
import mne
from mne_bids import get_entity_vals, find_matching_paths

from pipeline.mne_pipelines.kit_general_pipelines.utilities import (
    NYUAD_KIT_CONSTANTS as C
)

def _none_if_empty(x):
    if x in (None, "", [], {}):
        return None
    return x

def main():
    parser = argparse.ArgumentParser(
        description="Launch MNE Coregistration GUI for a BIDS project."
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
    bids_root = root / project_name
    print(f"Resolved BIDS root: {bids_root}")

    # Resolve SUBJECTS_DIR
    # We look for it in the config first, then default to a BIDS-standard derivatives location
    coreg_cfg = CFG.get("coregistration", {}) or {}
    subjects_dir_override = coreg_cfg.get("subjects_dir")
    
    if subjects_dir_override:
        subjects_dir = Path(subjects_dir_override).expanduser()
    else:
        # Default fallback: bids_root/derivatives/freesurfer/subjects
        subjects_dir = bids_root / "derivatives" / "freesurfer" / "subjects"
        
    if not subjects_dir.exists():
        print(f"WARNING: SUBJECTS_DIR does not exist: {subjects_dir}")
        print("MNE Coregistration might fail to find your MRI data.")
    else:
        print(f"Using SUBJECTS_DIR: {subjects_dir}")

    # Set the MNE config permanently for this session (it uses the environment if set_env=True)
    mne.utils.set_config("SUBJECTS_DIR", str(subjects_dir), set_env=True)

    # Subjects: empty include => ALL
    sub_cfg = CFG.get("subjects", {}) or {}
    include = sub_cfg.get("include") or []
    exclude = set(sub_cfg.get("exclude") or [])

    all_subjects = get_entity_vals(str(bids_root), entity_key="subject")
    subjects = sorted(s for s in (include or all_subjects) if s not in exclude)
    print(f"Subjects to process ({len(subjects)}): {subjects}")

    # Optional selections
    sel = CFG.get("bids_selection", {}) or {}
    sessions_sel = _none_if_empty(sel.get("sessions"))

    # Script name for finding derivatives
    # Usually we coregister the 'rawkit' or 'filtered' files
    # Let's search for kit2fiff outputs as a sensible default 'inst'
    previous_step = "2-kit_con_to_fif" # Default to using the raw converted fifs
    
    for sub in subjects:
        print(f"\nProcessing sub-{sub}...")
        
        # Try to find a FIFF file to use as 'inst'
        fif_files = find_matching_paths(
            str(bids_root),
            subjects=sub,
            sessions=sessions_sel,
            extensions=".fif",
            datatypes="meg"
        )
        
        if not fif_files:
            print(f"No .fif files found for sub-{sub} in {bids_root}. Skipping.")
            continue
            
        # Take the first one found
        inst_path = fif_files[0].fpath
        print(f"Using instance file: {inst_path}")

        try:
            # Launch the GUI
            print(f"Launching MNE Coregistration for {sub}...")
            # Note: head_high_res=True is often desired if available
            mne.gui.coregistration(
                inst=str(inst_path),
                subject=f"sub-{sub}",
                subjects_dir=str(subjects_dir),
                # If the subject folder in subjects_dir is just "fsaverage" or something else, 
                # you might need to adjust the 'subject' parameter accordingly.
            )
            print("To coregister the next subject, please close the GUI.")
        except Exception as e:
            print(f"Error launching coregistration for sub-{sub}: {e}")

    print("\nAll subjects processed.")

if __name__ == "__main__":
    main()
