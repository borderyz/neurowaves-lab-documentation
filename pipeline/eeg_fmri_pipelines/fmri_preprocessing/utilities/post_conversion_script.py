#!/usr/bin/env python3

import os
import re
import glob
import shutil

def replicate_sbref(directory):
    """
    For each BOLD run in 'directory', replicate the existing AP and PA SBRef files
    (both .nii.gz and .json) and rename them to match the run identifier.
    """

    # Look for the AP and PA sbref files (assumes exactly one set of each in the folder)
    ap_nii_list = glob.glob(os.path.join(directory, "*_dir-AP_sbref.nii.gz"))
    ap_json_list = glob.glob(os.path.join(directory, "*_dir-AP_sbref.json"))
    pa_nii_list = glob.glob(os.path.join(directory, "*_dir-PA_sbref.nii.gz"))
    pa_json_list = glob.glob(os.path.join(directory, "*_dir-PA_sbref.json"))

    # Basic checks
    if not (ap_nii_list and ap_json_list and pa_nii_list and pa_json_list):
        print("Error: Could not find a matching set of AP/PA sbref files.")
        return

    # For simplicity, take the first match in each list
    ap_nii = ap_nii_list[0]
    ap_json = ap_json_list[0]
    pa_nii = pa_nii_list[0]
    pa_json = pa_json_list[0]

    # Regex to identify BOLD run files
    # Example filename: sub-0065_task-fingertapping_run-01_bold.nii.gz
    bold_pattern = re.compile(r"^(sub-\d+)_task-([a-zA-Z0-9]+)_run-(\d+)_bold\.nii\.gz$")

    # Loop through files in the directory and look for BOLD runs
    for fname in os.listdir(directory):
        match = bold_pattern.match(fname)
        if match:
            sub_id = match.group(1)   # e.g., sub-0065
            task = match.group(2)    # e.g., fingertapping or restingstate
            run = match.group(3)     # e.g., 01, 02, 03

            # Construct the new SBRef filenames for AP and PA
            new_ap_nii = f"{sub_id}_task-{task}_dir-AP_run-{run}_sbref.nii.gz"
            new_ap_json = f"{sub_id}_task-{task}_dir-AP_run-{run}_sbref.json"
            new_pa_nii = f"{sub_id}_task-{task}_dir-PA_run-{run}_sbref.nii.gz"
            new_pa_json = f"{sub_id}_task-{task}_dir-PA_run-{run}_sbref.json"

            # Copy/replicate the original AP sbref files
            shutil.copyfile(os.path.join(directory, ap_nii),
                            os.path.join(directory, new_ap_nii))
            shutil.copyfile(os.path.join(directory, ap_json),
                            os.path.join(directory, new_ap_json))

            # Copy/replicate the original PA sbref files
            shutil.copyfile(os.path.join(directory, pa_nii),
                            os.path.join(directory, new_pa_nii))
            shutil.copyfile(os.path.join(directory, pa_json),
                            os.path.join(directory, new_pa_json))

            print(f"Created SBRef for: {sub_id}, task={task}, run={run}")

if __name__ == "__main__":
    # Example usage: python replicate_sbref.py /path/to/data
    import sys
    if len(sys.argv) < 2:
        print("Usage: python replicate_sbref.py <directory>")
        sys.exit(1)

    data_dir = sys.argv[1]
    replicate_sbref(data_dir)
