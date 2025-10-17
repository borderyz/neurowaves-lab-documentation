# plot_triggers.py
import os
from pathlib import Path

import mne
from mne_bids import (
    BIDSPath,
    find_matching_paths,
    get_entity_vals,
    make_report,
    print_dir_tree,
    read_raw_bids,
    get_datatypes,
)

import matplotlib
matplotlib.use('TkAgg')

# Use the constants instance
from pipeline.mne_pipelines.kit_general_pipelines.utilities import NYUAD_KIT_CONSTANTS as C

# Resolve dataset root from env
MEG_DATA_PATH = os.getenv("MEG_DATA")
if not MEG_DATA_PATH:
    raise EnvironmentError("MEG_DATA is not set.")

data_path = Path(MEG_DATA_PATH)
print(f"Resolved path: {data_path.resolve()}")

# Project folder (adjust or move into your YAML config if you prefer)
PROJECT_NAME = "script-testing-dataset"
DATASET_PATH = str(data_path / PROJECT_NAME)

# Show the BIDS tree
print_dir_tree(DATASET_PATH)

# Subject to plot
sub_id = "test1"

# Find the KIT raw file(s) for this subject using constants
meg_matches = find_matching_paths(
    DATASET_PATH,
    datatypes=C.DATATYPE,
    subjects=sub_id,
    extensions=tuple(C.MEG_EXTENSIONS),
)
if not meg_matches:
    raise FileNotFoundError(f"No MEG files found for sub-{sub_id} in {DATASET_PATH}")

meg_path = meg_matches[0].fpath
print(f"Plotting from: {meg_path}")

# Load raw
RAW_DATA = mne.io.read_raw_kit(meg_path, preload=False, verbose=False)

# Ensure the requested trigger channels exist; warn if any are missing
missing = [ch for ch in C.trigger_channels_MNE if ch not in RAW_DATA.ch_names]
if missing:
    print(f"Warning: the following trigger channels are not present in raw: {missing}")

# Plot MISC trigger channels
RAW_DATA.plot(
    picks=[ch for ch in C.trigger_channels_MNE if ch in RAW_DATA.ch_names],
    block=True,
    scalings={"misc": C.DEFAULT_MISC_CHANNELS_AMPLITUDE_SCALE},
    duration=C.DEFAULT_TIME_SCALE,
)
