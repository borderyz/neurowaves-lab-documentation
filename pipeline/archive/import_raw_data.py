
#Import raw MEG files from the KIT machine
#Saves as .fif
#Lead author: Hadi Zaatiti


import mne

SUBJECTS_ID = ['Y0409', 'Y0440']

experiments = ['01','02']

for experiment in experiments:
    for subject in SUBJECTS_ID:

        DIR = '../MEG_DATA/' + subject + '/'
        MEG_DATA_DIR = DIR + subject + '_'+experiment+'.con'
        HSP_DIR = DIR + subject + '_basic.txt' #Head Shape DIR
        STYLUS_DIR = DIR + subject + '_points_no_grad.txt'
        MARKERS = [subject + '-1.mrk', subject + '-2.mrk', subject + '-3.mrk']

        MARKERS_DIRS = [DIR + marker_path for marker_path in MARKERS]


        RAW_DATA = mne.io.read_raw_kit(input_fname=MEG_DATA_DIR,
                            mrk= MARKERS_DIRS,
                            elp = STYLUS_DIR,
                            hsp = HSP_DIR)


        RAW_DATA.save('../output/' + subject + '/' + subject +'_'+experiment+'_meg.fif')
