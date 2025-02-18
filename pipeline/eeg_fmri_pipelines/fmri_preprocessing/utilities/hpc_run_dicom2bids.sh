#!/bin/bash

# Set paths (Modify these to match your Linux/HPC environment)
CONFIG_FILE="/home/your_user/fmri_preprocessing/utilities/config.json"
BIDS_DIR="/home/your_user/data_finger_tapping/bids_output"
DICOM_DIR="/home/your_user/data_finger_tapping/Subject_0665_ses_01/scans"
SUBJECT_ID="0665"  # Participant ID

## Ensure Singularity module is loaded (only needed on HPC)
#module load singularity 2>/dev/null

# Run dcm2bids inside the Singularity container
singularity run --cleanenv \
    -B "$CONFIG_FILE:/config.json" \
    -B "$BIDS_DIR:/bids" \
    -B "$DICOM_DIR:/dicom" \
    dcm2bids.sif \
    -c /config.json \
    -o /bids \
    -d /dicom \
    -p "$SUBJECT_ID" \
    --force_dcm2bids
