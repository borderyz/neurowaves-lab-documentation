import os

import pandas as pd

# KIT2FIFF
from mne.commands.mne_kit2fiff import *
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


# Define this environment variable and point it to the path that holds the NYU-BOX datasets
# Or just set the path to the folder parent of your dataset folder

MEG_DATA_PATH = os.getenv("MEG_DATA")

# Set the name of your dataset folder on NYU-BOX
PROJECT_NAME = "egyptian-language-study"

# Define the path to your dataset folder
# Using the `os` library ensure that this script is cross-platform (Linux, MacOS, Windows)
DATASET_PATH = os.path.join(MEG_DATA_PATH, PROJECT_NAME)


# Dataset is BIDS structured so we can use the following functions
print_dir_tree(DATASET_PATH)
print(make_report(DATASET_PATH))

datatypes = get_datatypes(DATASET_PATH)

print("Dataset type", datatypes)

# Define subject ID's that should be ignored from the pipeline
ignore_subjects = ["trigger", "sanity"]

# Get subjects ID's while ignoring unwanted ones
# If your dataset has sessions then do not ignore sessions
# Here we are assuming there is no "sessions" layer between the subject and the scans
subjects = get_entity_vals(DATASET_PATH,
                           entity_key="subject",
                           ignore_sessions="on",
                           ignore_subjects=ignore_subjects)

print("Found", len(subjects), "subjects")

# These are static variables specific to the NYUAD setup and BIDS-naming scheme
# You do not need to change any of those variables

# Type of scan we are interested in for this pipeline
# This assumes we have an `meg` folder within each subject
DATATYPE = "meg"

# MEG scan and marker coils files extension
MEG_EXTENSIONS = [".con"]
HEAD_POSITION_INDICATOR_EXTENSIONS = [".mrk"]

# MEG Noise reduction algorithm label
NOISE_PROCESSING_LABEL = "CALMnoisereduction"
IGNORE_PROCESSING_LABEL = "CALMnoisereduction"

# MEG headshape digitizer file extention
HEADSHAPE_EXTENSIONS = [".txt"]

# ACQ Label used for files containing the stylus points digitization of fiducials
# Your stylus points has "...acq_points..." somewhere in its name

ACQ_LABEL_DIGITIZER_POINTS = "points"

# Same for headshape digitzation
# Your head surface digization file has "...acq_head..." somewhere in its name

ACQ_LABEL_DIGITIZER_HEAD = "head"

sub_id = "001"
for sub_id in subjects:

    print("Start KIT2FIFF Processing for subject ID ", sub_id)

    # Find CALM noise reduced data set:

    if NOISE_PROCESSING_LABEL != None:

        con_bids_path_no_proc = find_matching_paths(DATASET_PATH,
                                                       datatypes=DATATYPE,
                                                       subjects=sub_id,
                                                       extensions=MEG_EXTENSIONS)

        con_bids_path_noise_proc = find_matching_paths(DATASET_PATH,
                                            datatypes=DATATYPE,
                                            subjects=sub_id,
                                            processings=NOISE_PROCESSING_LABEL,
                                            extensions=MEG_EXTENSIONS)







    points_bids_path = find_matching_paths(DATASET_PATH,
                                           datatypes=DATATYPE,
                                           subjects=sub_id,
                                           acquisitions=ACQ_LABEL_DIGITIZER_POINTS,
                                           extensions=HEADSHAPE_EXTENSIONS)


    # read in the txt, make a copy to work on just in case
    points_edited_bids_path = pd.read_csv(points_bids_path[0].fpath, sep=r'\s+', skiprows=3, header=None)  # the delimiter means whitespace

    # remove the last 3 columns
    points_edited_bids_path = points_edited_bids_path.drop(points_edited_bids_path.columns[[3, 4, 5]], axis=1)

    # write txt
    points_edited_file_save_name =  os.path.join(DATASET_PATH, 'sub-' + sub_id, 'derivatives', 'sub-' + sub_id + '_points_edited.txt')

    points_edited_bids_path.to_csv(points_edited_file_save_name, sep=' ', index=False, header=False)


    DERIVATIVES_FOLDER = os.path.join(DATASET_PATH, 'sub-' + sub_id, 'derivatives')



    head_bids_path = find_matching_paths(DATASET_PATH,
                                         datatypes=DATATYPE,
                                         subjects=sub_id,
                                         acquisitions=ACQ_LABEL_DIGITIZER_HEAD,
                                         extensions=HEADSHAPE_EXTENSIONS)




    mrk_bids_path = find_matching_paths(DATASET_PATH,
                                        datatypes=DATATYPE,
                                        subjects=sub_id,
                                        extensions=HEAD_POSITION_INDICATOR_EXTENSIONS)




    # Remind that a .mrk file is the position of the five head coils at a time t
    # If the participant moved at some point and we got an additional .mrk to account for the movement, we should apply this one after movement and not the first .mrk
    # This logic is implemented here:
        # When multiple .mrk are found, the built-in function by default will average all the provided .mrk position of the Head Positioning Indicators
        # if N>1 .con files are found :
        # if there is N+1  .mrk files, then the first two .mrk files are used for the first .con,
        # then the second and third are used for the second .con etc...

    if len(con_bids_path) ==1 and len(head_bids_path) ==1 and len(points_bids_path)==1 and len(mrk_bids_path)>=1:
        raw_sub_test = read_raw_kit(
            input_fname=con_bids_path[0],
            mrk=mrk_bids_path,
            elp=points_edited_file_save_name,
            hsp=head_bids_path[0],
            # stim=stim,
            # slope=slope,
            # stimthresh=stimthresh,
        )
    elif len(mrk_bids_path)>=len(con_bids_path)+1:

        for index, con_file in enumerate(con_bids_path):
            raw_sub_test = read_raw_kit(
                input_fname=con_file,
                mrk=[mrk_bids_path[index], mrk_bids_path[index+1]],
                elp=points_edited_file_save_name,
                hsp=head_bids_path[0],
                # stim=stim,
                # slope=slope,
                # stimthresh=stimthresh,
            )
    else:
        print('Problem for subject ID ', sub_id, 'Found multiple .con files but not enough .mrk files')

    #TODO: Ensure that the multiple MRK's are taken into account in the .fif

    out_fname = 'sub-' + sub_id + '_task-' + PROJECT_NAME + '_meg_raw.fif'
    SAVE_PATH = os.path.join(DERIVATIVES_FOLDER, out_fname)
    raw_sub_test.save(SAVE_PATH)
    raw_sub_test.close()

    print(".fif files for subject ID ", sub_id, " saved in ", SAVE_PATH)















