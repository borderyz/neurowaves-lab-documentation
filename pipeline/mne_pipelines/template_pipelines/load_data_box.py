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

PROJECT_NAME = "egyptian-language-study"  #The name of your dataset folder on NYU-BOX


DATASET_PATH = os.path.join(MEG_DATA_PATH, PROJECT_NAME)


#Dataset is BIDS so we can use the following functions
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

meg_extensions = [".con"]
headshape_extensions = [".txt"]
processings = "CALMnoisereduction"

ignore_processing = "CALMnoisereduction"

acq_points = "points"
datatype = "meg"
acq_head = "head"
mrk_extensions = [".mrk"]

for sub_id in subjects:

    print("Start KIT2FIFF Processing for subject ID ", sub_id)


    # Find CALM noise reduced data set:

    if processings != None:
        con_bids_path = find_matching_paths(DATASET_PATH,
                                         datatypes=datatype,
                                         subjects=sub_id,
                                         processings=processings,
                                         extensions=meg_extensions)

        get_entity_vals(DATASET_PATH,
                        entity_key=sub_id,
                        ignore_processings=ignore_processing)




    points_bids_path = find_matching_paths(DATASET_PATH,
                                     datatypes=datatype,
                                     subjects=sub_id,
                                     acquisitions=acq_points,
                                     extensions=headshape_extensions)


    # read in the txt, make a copy to work on just in case
    points_edited_bids_path = pd.read_csv(points_bids_path[0].fpath, sep=r'\s+', skiprows=3, header=None)  # the delimiter means whitespace

    # remove the last 3 columns
    points_edited_bids_path = points_edited_bids_path.drop(points_edited_bids_path.columns[[3, 4, 5]], axis=1)

    # write txt
    points_edited_file_save_name =  os.path.join(DATASET_PATH, 'sub-' + sub_id, 'derivatives', 'sub-' + sub_id + '_points_edited.txt')

    points_edited_bids_path.to_csv(points_edited_file_save_name, sep=' ', index=False, header=False)


    DERIVATIVES_FOLDER = os.path.join(DATASET_PATH, 'sub-' + sub_id, 'derivatives')



    head_bids_path = find_matching_paths(DATASET_PATH,
                                     datatypes=datatype,
                                     subjects=sub_id,
                                     acquisitions=acq_head,
                                     extensions=headshape_extensions)




    mrk_bids_path = find_matching_paths(DATASET_PATH,
                                     datatypes=datatype,
                                     subjects=sub_id,
                                     extensions=mrk_extensions)




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















