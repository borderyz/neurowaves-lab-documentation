import mne

subjects_dir = r'C:\Users\hz3752\PycharmProjects\mne_bids_pipeline\data\meg\Sub-0037\sub-0037-fwd.fif'


fwd = mne.read_forward_solution(subjects_dir, include=(), exclude=(), ordered=True, verbose=None)

a=1
