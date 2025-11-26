Kidslang project
----------------

Investigating Arabic language comprehension in an interactive context setting and a non-interactive (no context) setting.

Two tasks:
- 'interactive context', referred to as the 'dialogue text'
- 'non interactive' referrred to as the 'listening task'

Each task has two conditions an object condition and a phrase condition
So cond_list = ['dialogue_phrase', 'dialogue'object', 'listening_phrase', 'listening_object']

Questions to Sherine:
- is the A_subjects, are english? so these I should not take a look at?
- Was the GUI you were talking about, the mne kitfiff GUI? or something else?

Subjects list
Y_ subjects are the Arabic project

['Y0312', 'Y0366', 'Y0367', 'Y0371', 'Y0372', 'Y0373', 'Y0374', 'Y0375', 'Y0376', 'Y0377', 'Y0378', 'Y0380', 'Y0381', 'Y0382', 'Y0383', 'Y0384', 'Y0387', 'Y0388', 'Y0390', 'Y0392', 'Y0393']
Count: 21




Available data from 21 participants:
- MEG data (.con and .mrk)
- MRI data (fsaverage)
- Digitized headshape

Preprocessing is already done:
- ICA for eyeblinks
- Rejection of bad epochs
- STC computed for all 21 participants (we only care about word 2, which defines the epoch)
What is required:
Time-lock analysis (not frequency)
Statistical analysis:
- Spatiotemporal clustering: finding regions of high activity across the entire brain over the duration of the epoch
- ROI clustering:

Location for STC for word 2/Server/NEUROLING/PersonalFiles/SherineBouDargham/KidLang/Adults/stc/ara_stc_w2