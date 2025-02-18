#!/bin/bash


module load fmriprep/24.0.0

# Load the fMRIPrep module
module load fmriprep

# Define key directories (modify these paths)
BIDS_DIR="/home/hz3752/data_eeg_fmri/bids_output"      # Input BIDS dataset
OUTPUT_DIR="/home/hz3752/data_eeg_fmri/fmriprep_output"     # Output directory for fMRIPrep
WORK_DIR="/home/hz3752/data_eeg_fmri"              # Temporary working directory

# Define the participant label (optional, for processing a specific subject)
PARTICIPANT_LABEL="sub-0665"

# Run fMRIPrep
fmriprep $BIDS_DIR $OUTPUT_DIR participant \
    --participant-label $PARTICIPANT_LABEL \
    --work-dir $WORK_DIR \
    --output-spaces MNI152NLin2009cAsym fsaverage \










