import mne

mne.sys_info()

mne.gui.coregistration(
    inst='MEG_DATA/Y0409/Y0409_SavantAra-raw_from_script.fif',
    subject='Y0409',
    subjects_dir='MEG_DATA/Y0409',  # contains a sub-folder for subject
    head_high_res=True,
    # trans=None,  # only if you already have one
    interaction='terrain',
)