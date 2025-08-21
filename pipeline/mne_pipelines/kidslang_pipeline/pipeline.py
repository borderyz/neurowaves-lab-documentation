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


SUBJ_ID = ['Y0312', 'Y0366', 'Y0367', 'Y0371', 'Y0372', 'Y0373', 'Y0374', 'Y0375', 'Y0376', 'Y0377', 'Y0378', 'Y0380', 'Y0381', 'Y0382', 'Y0383', 'Y0384', 'Y0387', 'Y0388', 'Y0390', 'Y0392', 'Y0393']


import pandas as pd


# Set path to the CSV
status_csv_path = os.path.join(DATASETS_PATH, PROJ_NAME, 'processing_status.csv')

# Read or create the DataFrame if file doesn't exist
if os.path.exists(status_csv_path):
    df = pd.read_csv(status_csv_path)
else:
    df = pd.DataFrame(columns=['Subject_ID', 'Processing status', 'ICA', 'Filter 50 Hz', 'Coregistration'])

# Function to update/add status for a subject
def update_status(subject_id, status, ica=None, filter50=None, coreg=None):
    global df
    if subject_id in df['Subject_ID'].values:
        idx = df[df['Subject_ID'] == subject_id].index[0]
        df.at[idx, 'Processing status'] = status
        if ica is not None:
            df.at[idx, 'ICA'] = ica
        if filter50 is not None:
            df.at[idx, 'Filter 50 Hz'] = filter50
        if coreg is not None:
            df.at[idx, 'Coregistration'] = coreg
    else:
        df = pd.concat([
            df,
            pd.DataFrame([{
                'Subject_ID': subject_id,
                'Processing status': status,
                'ICA': ica,
                'Filter 50 Hz': filter50,
                'Coregistration': coreg
            }])
        ], ignore_index=True)





for subj_id in SUBJ_ID:

    # Coregistration
    # Import MEG and MRI data for the subject

    # Convert files to .fif format
    subj_meg_path = os.path.join(ROOT_DIR_MEG, subj_id)
    subj_mri_path = os.path.join(ROOT_DIR_MRI, subj_id)

    con_files = sorted(glob.glob(os.path.join(subj_meg_path, '*.con')))
    mrk_files = sorted(glob.glob(os.path.join(subj_meg_path, '*.mrk')))
    head_shape_point_file = glob.glob(os.path.join(subj_meg_path, '*_points.txt'))
    head_shape_surface_file = glob.glob(os.path.join(subj_meg_path, '*_basic.txt'))


    print(con_files)
    for con_file in con_files:
        # Run kit2fiff
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
        mrk=mrk_fname[0],
        elp=elp_fname,
        hsp=hsp_fname,
        stim=stim,
        slope=slope,
        stimthresh=stimthresh,
    )

    raw.save(out_fname)
    raw.close()

    # Example update
    update_status(subj_id, 'Incomplete', ica=False, filter50=False, coreg=False)



    # Save the DataFrame back to CSV
    df.to_csv(status_csv_path, index=False)