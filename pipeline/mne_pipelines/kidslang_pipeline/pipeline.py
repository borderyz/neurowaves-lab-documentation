import os
import subprocess
import glob
import warnings

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

DEFAULTS = {
    'Subject_ID'       : None,        # always present; filled per row
    'KIT2FIFF'         : pd.NA,
    'Processing status': 'Not started',
    'ICA'              : pd.NA,
    'Filter 50 Hz'     : pd.NA,
    'Coregistration'   : pd.NA,
}





# Set path to the CSV
status_csv_path = os.path.join(DATASETS_PATH, PROJ_NAME, 'processing_status.csv')

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def _empty_df_from_defaults():
    """Create an empty DataFrame with columns from DEFAULTS (in order)."""
    return pd.DataFrame(columns=list(DEFAULTS.keys()))

def _row_from_defaults(subject_id: str) -> dict:
    """Create a new row dict with DEFAULTS and the given subject id."""
    row = {k: (v if k != 'Subject_ID' else subject_id) for k, v in DEFAULTS.items()}
    row['Subject_ID'] = subject_id
    return row

def _sync_schema(df: pd.DataFrame, strict: bool = False) -> pd.DataFrame:
    """
    Ensure df matches DEFAULTS schema.
    - Adds any missing columns with default values.
    - If strict=True, drops columns not in DEFAULTS and reorders columns.
    - If strict=False (default), keeps extra columns but still adds missing ones.
    """
    # Add missing columns
    for col, default in DEFAULTS.items():
        if col not in df.columns:
            df[col] = default

    if strict:
        # Keep only columns in DEFAULTS and order them
        df = df[list(DEFAULTS.keys())]
    else:
        # Reorder DEFAULT columns to the front, keep extras after
        front = [c for c in DEFAULTS.keys()]
        extras = [c for c in df.columns if c not in DEFAULTS]
        df = df[front + extras]

    return df

def _save(df: pd.DataFrame):
    df.to_csv(status_csv_path, index=False)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def update_status(subject_id: str, column: str, value):
    """
    Update one field for a subject without touching other fields.
    - Only columns defined in DEFAULTS are allowed.
    - Creates a new row initialized from DEFAULTS if subject is new.
    """
    global LOG_DATA_FRAME



    # Ensure schema is still aligned (cheap safety)
    LOG_DATA_FRAME = _sync_schema(LOG_DATA_FRAME, strict=False)

    # Insert row if subject doesn’t exist
    if subject_id not in LOG_DATA_FRAME['Subject_ID'].values:
        new_row = _row_from_defaults(subject_id)
        LOG_DATA_FRAME = pd.concat([LOG_DATA_FRAME, pd.DataFrame([new_row])], ignore_index=True)

    # Update the single field
    idx = LOG_DATA_FRAME.index[LOG_DATA_FRAME['Subject_ID'] == subject_id][0]
    LOG_DATA_FRAME.at[idx, column] = value

    _save(LOG_DATA_FRAME)


def is_status(subject_id: str, column: str, value) -> bool:
    """
    Return True if the subject has the given value in the given column.
    """
    global LOG_DATA_FRAME

    if subject_id not in LOG_DATA_FRAME['Subject_ID'].values:
        return False  # no row yet → treat as not matching

    row = LOG_DATA_FRAME.loc[LOG_DATA_FRAME['Subject_ID'] == subject_id]
    return row[column].iloc[0] == value


def reset_status_csv(subject_ids, strict: bool = True):
    """
    Rebuild the CSV from DEFAULTS for the provided subject_ids.
    - If strict=True, output exactly columns in DEFAULTS (drops any old extras).
    - If strict=False, keeps existing extra columns and fills DEFAULTS.
    """
    global LOG_DATA_FRAME

    if strict:
        rows = [_row_from_defaults(sid) for sid in subject_ids]
        LOG_DATA_FRAME = pd.DataFrame(rows, columns=list(DEFAULTS.keys()))
    else:
        # Keep existing columns but re-init DEFAULT ones
        LOG_DATA_FRAME = _sync_schema(LOG_DATA_FRAME, strict=False)
        # Build blank rows first
        LOG_DATA_FRAME = LOG_DATA_FRAME[0:0]  # clear content keep columns
        for sid in subject_ids:
            row = {c: (DEFAULTS.get(c, pd.NA)) for c in LOG_DATA_FRAME.columns}
            row['Subject_ID'] = sid
            LOG_DATA_FRAME = pd.concat([LOG_DATA_FRAME, pd.DataFrame([row])], ignore_index=True)

    _save(LOG_DATA_FRAME)
    print(f"CSV reset for {len(subject_ids)} subjects.")


# Read or create the DataFrame if file doesn't exist
if os.path.exists(status_csv_path):
    LOG_DATA_FRAME = pd.read_csv(status_csv_path)
    LOG_DATA_FRAME = _sync_schema(LOG_DATA_FRAME, strict=False)  # set strict=True if you want to drop old columns
else:
    LOG_DATA_FRAME = _empty_df_from_defaults()
    _save(LOG_DATA_FRAME)



def kit2fiff(subj_id):
    #TODO: Continue here
    return FAIL


if __name__ == "__main__":

    for subj_id in SUBJ_ID:

        # Change directory to subject directory

        work_dir = os.path.join(ROOT_DIR_MEG, subj_id)
        os.chdir(work_dir)

        # Example: skip ICA if it's already done
        if not is_status(subj_id, "ICA", True):
            print("Converting KIT2FIFF for ", subj_id)
        else:
            print("KIT2FIFF already done for ",subj_id)

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

        # MRK and CON file count sanity check

        if len(mrk_files)!=(len(con_files)+1):
            raise Exception("Warning, subject", subj_id, "has inconsistent number of .mrk/.con files")

        if len(head_shape_point_file)>1:
            raise Exception("Found more than one head-shape point file.")

        if len(head_shape_surface_file)>1:
            raise Exception("Found more than one head-shape surface file.")

        if len(head_shape_point_file) == 0:
            raise Exception("No head-shape point file found.")

        if len(head_shape_surface_file) ==0:
            raise Exception("No head-shape surface file found.")


        print('All file count sanity checks passed for subject', subj_id)

        for index, con_file in enumerate(con_files):


            raw = read_raw_kit(
                input_fname=con_file,
                mrk=[mrk_files[index], mrk_files[index+1]],
                elp=head_shape_point_file[0],
                hsp=head_shape_surface_file[0],
                #stim=stim,
                #slope=slope,
                #stimthresh=stimthresh,
            )

            # What is the unit of measurement of the .mrk? You are given the x,y,z coordinates of five points

            bids_fname = f"sub-{subj_id}_task-{PROJ_NAME}_meg.fif"

            raw.save(bids_fname,
                     overwrite=True)
            raw.close()


        # Example update
        update_status(subj_id, 'KIT2FIFF', 'Complete')
        update_status(subj_id, 'Processing status', 'Started')



