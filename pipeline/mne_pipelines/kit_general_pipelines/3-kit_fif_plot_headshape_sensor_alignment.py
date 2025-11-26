import argparse
import os
import sys
from pathlib import Path
import yaml
import mne
import matplotlib.pyplot as plt

# Ensure we can import from the pipeline package if needed, 
# but we'll try to keep this standalone or use relative imports if the package is installed.
# For now, we'll rely on standard libraries and mne.

def main():
    parser = argparse.ArgumentParser(
        description="Generate sensor alignment plots from FIFF files."
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
        # Try resolving relative to current working directory if default failed
        if not config_path.is_absolute():
             # Assuming script is run from kit_general_pipelines or similar
             # Try looking up one level if we are in report_generation
             pass 
        
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

    # Input: kit2fiff derivatives
    # Look for renamed folders first
    kit2fiff_dir = bids_root / "derivatives" / "2-kit_con_to_fif"
    if not kit2fiff_dir.exists():
        kit2fiff_dir = bids_root / "derivatives" / "kit2fiff"

    if not kit2fiff_dir.exists():
        print(f"No kit2fiff derivatives found at {kit2fiff_dir}")
        return

    # Output: sensor_digitization_coregistration
    # "make sure ur saving in the derivatives that is under the dataset path"
    script_name = Path(__file__).stem
    out_dir = bids_root / "derivatives" / script_name
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {out_dir}")

    # Save a copy of the config file with timestamp
    from datetime import datetime
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    config_save_path = out_dir / f"config_{timestamp_str}.yml"
    with open(config_save_path, 'w') as f:
        yaml.dump(CFG, f, default_flow_style=False)
    print(f"Saved copy of config to: {config_save_path}")

    # Find all .fif files in kit2fiff
    # We look for files ending in .fif
    fif_files = list(kit2fiff_dir.rglob("*.fif"))
    
    if not fif_files:
        print("No .fif files found to plot.")
        return

    print(f"Found {len(fif_files)} .fif files.")

    # Setup 3D backend if possible (pyvista)
    try:
        mne.viz.set_3d_backend("pyvista")
    except Exception:
        print("Could not set pyvista backend, falling back to default.")

    for fif_path in fif_files:
        print(f"Processing {fif_path.name}...")
        
        # Construct output path to mirror structure
        # e.g. derivatives/kit2fiff/sub-01/ses-01/file.fif -> derivatives/sensor_digitization_coregistration/sub-01/ses-01/file.png
        rel_path = fif_path.relative_to(kit2fiff_dir)
        save_path = out_dir / rel_path.with_suffix('.png')
        
        if save_path.exists():
            print(f"  Skipping (already exists): {save_path}")
            continue

        save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            raw = mne.io.read_raw_fif(fif_path, preload=False, verbose=False)
            
            # Generate plot
            # Using the user's requested command
            
            fig = mne.viz.plot_alignment(
                raw.info,
                meg=["helmet", "sensors"],
                dig=True,
                show_axes=True,
                subject=None,
                surfaces=[],
                coord_frame='meg', # usually good for raw info without trans
                interaction='terrain'
            )
            
            # Save plot
            # Check if fig is a PyVistaFigure (it usually is with pyvista backend)
            if hasattr(fig, 'plotter'):
                # Set a nice view if possible? Default is usually top-down or isometric.
                # We can just screenshot.
                fig.plotter.screenshot(str(save_path))
                fig.plotter.close()
            else:
                # Fallback for matplotlib backend (unlikely for plot_alignment but possible)
                try:
                    fig.savefig(str(save_path))
                    if hasattr(fig, 'close'):
                        fig.close()
                except AttributeError:
                    print(f" Could not save figure for {fif_path.name}: Unknown figure type {type(fig)}")

            print(f"  Saved plot: {save_path}")
            
        except Exception as e:
            print(f" Error processing {fif_path.name}: {e}")
            # Continue to next file

    print("Done.")

if __name__ == "__main__":
    main()
