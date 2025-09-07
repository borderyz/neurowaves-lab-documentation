import os
import subprocess
import glob

import mne
from mne.io import kit
from mne.commands.mne_kit2fiff import *

DATASETS_PATH = os.getenv('MEG_DATA')
PROJ_NAME = 'kidlang'

ROOT_DIR_MEG = os.path.join(DATASETS_PATH, PROJ_NAME, 'meg')
ROOT_DIR_MRI = os.path.join(DATASETS_PATH, PROJ_NAME, 'mri')



SUBJ_ID = ['Y0312',
           'Y0366',
           'Y0367',
           'Y0371',
           'Y0372',
           'Y0373',
           'Y0374',
           'Y0375',
           'Y0376',
           'Y0377',
           'Y0378',
           'Y0380',
           'Y0381',
           'Y0382',
           'Y0383',
           'Y0384',
           'Y0387',
           'Y0388',
           'Y0390',
           'Y0392',
           'Y0393']


import pandas as pd


# Set path to the CSV
status_csv_path = os.path.join(DATASETS_PATH, PROJ_NAME, 'processing_status.csv')

# Read or create the DataFrame if file doesn't exist
if os.path.exists(status_csv_path):
    LOG_DATA_FRAME = pd.read_csv(status_csv_path)
else:
    LOG_DATA_FRAME = pd.DataFrame(columns=['Subject_ID', 'KIT2FIFF', 'Processing status', 'ICA', 'Filter 50 Hz', 'Coregistration'])

# Function to update/add status for a subject
def update_status(subject_id, status, kit2fiff=None, ica=None, filter50=None, coreg=None):
    global LOG_DATA_FRAME
    if subject_id in LOG_DATA_FRAME['Subject_ID'].values:
        idx = LOG_DATA_FRAME[LOG_DATA_FRAME['Subject_ID'] == subject_id].index[0]
        LOG_DATA_FRAME.at[idx, 'Processing status'] = status
        if ica is not None:
            LOG_DATA_FRAME.at[idx, 'ICA'] = ica
        if filter50 is not None:
            LOG_DATA_FRAME.at[idx, 'Filter 50 Hz'] = filter50
        if coreg is not None:
            LOG_DATA_FRAME.at[idx, 'Coregistration'] = coreg
        if kit2fiff is not None:
            LOG_DATA_FRAME.at[idx, 'KIT2FIFF'] = kit2fiff
    else:
        LOG_DATA_FRAME = pd.concat([
            LOG_DATA_FRAME,
            pd.DataFrame([{
                'Subject_ID': subject_id,
                'Processing status': status,
                'KIT2FIFF': kit2fiff,
                'ICA': ica,
                'Filter 50 Hz': filter50,
                'Coregistration': coreg
            }])
        ], ignore_index=True)

    # Save the DataFrame back to CSV
    LOG_DATA_FRAME.to_csv(status_csv_path, index=False)

def reset_status_csv():
    """Reset the processing status CSV as if no processing was done."""
    global LOG_DATA_FRAME
    # Create a fresh DataFrame with only Subject IDs
    LOG_DATA_FRAME = pd.DataFrame([{
        'Subject_ID': subj,
        'Processing status': 'Not started',
        'ICA': None,
        'Filter 50 Hz': None,
        'Coregistration': None
    } for subj in SUBJ_ID])

    # Save to CSV
    LOG_DATA_FRAME.to_csv(status_csv_path, index=False)
    print(f"CSV reset: all subjects marked as 'Not started'.")


if __name__ == "__main__":

    for subj_id in SUBJ_ID:


        # Change directory to subject directory

        work_dir = os.path.join(ROOT_DIR_MEG, subj_id)
        os.chdir(work_dir)

        print('Processing subject', subj_id)
        # Coregistration
        # Import MEG and MRI data for the subject

        # Convert files to .fif format
        subj_meg_path = os.path.join(ROOT_DIR_MEG, subj_id)
        subj_mri_path = os.path.join(ROOT_DIR_MRI, subj_id)


        # Each subject can have multiple marker files and multiple con files
        # We are assuming that the first marker files are associated with the first con files as per their name, this is why we are sorting them

        con_files = sorted(glob.glob(os.path.join(subj_meg_path, '*.con')))
        mrk_files = sorted(glob.glob(os.path.join(subj_meg_path, '*.mrk')))
        head_shape_point_file = glob.glob(os.path.join(subj_meg_path, '*_points.txt'))
        head_shape_surface_file = glob.glob(os.path.join(subj_meg_path, '*_basic.txt'))


        print('\tFound', len(con_files), '.con files')
        print('\tFound', len(mrk_files), '.mrk files')

        for con_file in con_files:
            # Run kit2fiff

            subprocess.run(['mne',
                            'kit2fiff',
                            ], shell=True)  # Use 'ls' instead of 'dir' on Unix


            subprocess.run(['mne',
                            'kit2fiff',
                            '--input',
                            con_file,
                            '--mrk',
                            mrk_files[0],
                            '--elp'
                            ], shell=True)  # Use 'ls' instead of 'dir' on Unix



        raw = read_raw_kit(
            input_fname=con_files[0],
            mrk=mrk_files[0],
            elp=head_shape_surface_file,
            hsp=head_shape_surface_file,
            #stim=stim,
            #slope=slope,
            #stimthresh=stimthresh,
        )

        raw.save(OUT_FNAME,
                 overwrite=True)
        raw.close()



        # Example update
        update_status(subj_id, 'Incomplete',kit2fiff=True, ica=False, filter50=False, coreg=False)


    # Save the DataFrame back to CSV
    LOG_DATA_FRAME.to_csv(status_csv_path, index=False)

