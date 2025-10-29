import mne

PATH_FILE = r"sub-Y0312_task-kidlang_meg.fif"

# Load the raw data
raw = mne.io.read_raw_fif(PATH_FILE, preload=False)

# Assuming 'raw' is your already loaded Raw object
raw.filter(l_freq=2, h_freq=40, fir_design='firwin')

raw.notch_filter(freqs=[50, 100, 150])