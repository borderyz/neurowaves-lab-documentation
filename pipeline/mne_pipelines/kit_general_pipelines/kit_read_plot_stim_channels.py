import os
from pathlib import Path

import mne
from mne.io import read_raw_kit
from mne_bids import (
    BIDSPath,
    find_matching_paths,
    get_entity_vals,
    make_report,
    print_dir_tree,
    read_raw_bids,
    get_datatypes
)

import matplotlib
matplotlib.use('TkAgg')


from pipeline.mne_pipelines.kit_general_pipelines.utilities import *

MEG_DATA_PATH = os.getenv("MEG_DATA")

# Convert to a Path object
if MEG_DATA_PATH:
    data_path = Path(MEG_DATA_PATH)
    print(f"Resolved path: {data_path.resolve()}")
else:
    raise EnvironmentError("MEG_DATA is not set.")


# Set the name of your dataset folder on NYU-BOX
PROJECT_NAME = "script-testing-dataset"

# Define the path to your dataset folder
# Using the `os` library ensure that this script is cross-platform (Linux, MacOS, Windows)
DATASET_PATH = os.path.join(MEG_DATA_PATH, PROJECT_NAME)


# Dataset is BIDS structured so we can use the following functions
print_dir_tree(DATASET_PATH)


sub_id = "test1"

meg_data_file = find_matching_paths(DATASET_PATH,
                    datatypes=DATATYPE,
                    subjects=sub_id,
                    extensions=MEG_EXTENSIONS)


RAW_DATA = mne.io.read_raw_kit(meg_data_file[0], preload=False, verbose=False)

RAW_DATA.plot(picks=trigger_channels,
         block=True,
         scalings={"misc": DEFAULT_MISC_CHANNELS_AMPLITUDE_SCALE},
         duration=DEFAULT_TIME_SCALE)



