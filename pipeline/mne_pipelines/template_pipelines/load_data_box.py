import os
import sys

from mne_bids import (
    BIDSPath,
    find_matching_paths,
    get_entity_vals,
    make_report,
    print_dir_tree,
    read_raw_bids,
)
MEG_DATA_PATH = os.getenv("MEG_DATA") # Define this environment varialbe and point it to the path that holds the NYU-BOX datasets


PROJECT_NAME = "egyptian-language-study"  #The name of your dataset folder on NYU-BOX

DATASET_PATH = os.path.join(MEG_DATA_PATH, PROJECT_NAME)

print(DATASET_PATH)
print_dir_tree(DATASET_PATH)
print(make_report(DATASET_PATH))

sessions = get_entity_vals(DATASET_PATH, "session", ignore_sessions="on")

print(sessions)







