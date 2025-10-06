import os
import sys

from mne_bids import (
    BIDSPath,
    find_matching_paths,
    get_entity_vals,
    make_report,
    print_dir_tree,
    read_raw_bids,
    get_datatypes
)


# Define this environment variable and point it to the path that holds the NYU-BOX datasets
# Or just set the path to the folder parent of your dataset folder

MEG_DATA_PATH = os.getenv("MEG_DATA")

PROJECT_NAME = "egyptian-language-study"  #The name of your dataset folder on NYU-BOX

DATASET_PATH = os.path.join(MEG_DATA_PATH, PROJECT_NAME)


print(DATASET_PATH)
print_dir_tree(DATASET_PATH)
print(make_report(DATASET_PATH))

datatypes = get_datatypes(DATASET_PATH)

print("Dataset type", datatypes)




# Get subjects ID's while ignoring the trigger test and sanity check subjects
subjects = get_entity_vals(DATASET_PATH,
                           entity_key="subject",
                           ignore_sessions="on",
                           ignore_subjects=["trigger", "sanity"])

print("Found", len(subjects), "subjects")





# Test one subject first


# Find CALM noise reduced data set:
processings = "CALMnoisereduction"
meg_extensions = [".con"]
con_bids_path = find_matching_paths(DATASET_PATH,
                                 datatypes="meg",
                                 subjects="001",
                                 processings=processings,
                                 extensions=meg_extensions)


headshape_extensions = [".txt"]
acq = "points"

sub_id = "001"

points_bids_path = find_matching_paths(DATASET_PATH,
                                 datatypes="meg",
                                 subjects=sub_id,
                                 acquisitions=acq,
                                 extensions=headshape_extensions)

import pandas as pd
# read in the txt, make a copy to work on just in case
points_edited_bids_path = pd.read_csv(points_bids_path[0].fpath, sep=r'\s+', skiprows=3, header=None)  # the delimiter means whitespace

# remove the last 3 columns
points_edited_bids_path = points_edited_bids_path.drop(points_edited_bids_path.columns[[3, 4, 5]], axis=1)

# write txt
points_edited_file_save_name =  os.path.join(DATASET_PATH, 'sub-' + sub_id, 'derivatives', 'sub-' + sub_id + '_points_edited.txt')

points_edited_bids_path.to_csv(points_edited_file_save_name, sep=' ', index=False, header=False)


DERIVATIVES_FOLDER = os.path.join(DATASET_PATH, 'sub-' + sub_id, 'derivatives')

acq = "head"

head_bids_path = find_matching_paths(DATASET_PATH,
                                 datatypes="meg",
                                 subjects=sub_id,
                                 acquisitions=acq,
                                 extensions=headshape_extensions)


mrk_extensions = [".mrk"]

mrk_bids_path = find_matching_paths(DATASET_PATH,
                                 datatypes="meg",
                                 subjects=sub_id,
                                 extensions=mrk_extensions)


# KIT2FIFF
from mne.commands.mne_kit2fiff import *
from mne.io import read_raw_kit



if len(con_bids_path) ==1 and len(head_bids_path) ==1 and len(points_bids_path)==1:
    raw_sub_test = read_raw_kit(
        input_fname=con_bids_path[0],
        mrk=mrk_bids_path,
        elp=points_edited_file_save_name,
        hsp=head_bids_path[0],
        # stim=stim,
        # slope=slope,
        # stimthresh=stimthresh,
    )

    out_fname = 'sub-' + sub_id + '_task-' + PROJECT_NAME + '_meg_raw.fif'
    SAVE_PATH = os.path.join(DERIVATIVES_FOLDER, out_fname)
    raw_sub_test.save(SAVE_PATH)
    raw_sub_test.close()















