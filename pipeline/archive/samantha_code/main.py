'''This is where we store global variables, such as
the name of participants, directory information, and
other important parameters of analysis'''

import mne
##### CHECK THESE EVERY NEW ANALYSIS #####

# General parameters

# What's the directory? (This will vary as a function of which computer/user is running the code!)
# Dustin's ROOT:
# ROOT = '/Users/meglab/Desktop/South Slavic/'
# Desktop Analysis Mac ROOT:
# Dave's TAG analysis ROOT for Common dropbox
# He in an arse!
#ROOT = '/Volumes/Transcend/Dropbox/SAVANT-MEG-FILES/TAG/'



# Who are your subjects, and what's your N?
#subjects = ['P049', 'P050', 'P054', 'P056', 'P057', 'P058', 'P059', 'P060', 'P061', 'P062', 'P063', 'P064', 'P065', 'P066', 'P068', 'P069', 'P070', 'P071']
#subjects = ['P049', 'P050', 'P054', 'P056', 'P057', 'P058', 'P059', 'P060', 'P061', 'P062', 'P063', 'P064', 'P065', 'P066', 'P068', 'P069', 'P070', 'P071']

#sampleSize = len(subjects)

# What's today's date?
date = '2023_Sept8_pmin05'
# Any notes you want to keep in the filename?
# (I sometimes include p-values for cluster-based permutation tests or other parameters here if I'm running
# more than one plot or analysis in the same day and want to keep track)
notes = ''

##### CHANGE THESE ONCE #####
sampleSize = 1

# General parameters

# What's your experiment's name? (this will need to be included in the .fif files)
expName = 'BiDipilot'
#expName = 'SAVANTTAG'
# What are your trigger-condition correpsondences?
# -*- coding: utf-8 -*-
event_ids = dict(MSA_MSA=20,MSA_EGY=25,MSA_ENG=30,EGY_EGY=35,EGY_MSA=40,EGY_ENG=45)
subjects_dir = ('mri')


# How many trials are in your experiment total? (comment when analysing lex dec task?)
# expected_nb_events = 220
# Tark events (uncomment when using Tark analysis)
#expected_nb_events = 300

# Epoching parameters
epoch_tmin = -0.1
epoch_tmax = 0.6
epoch_baseline = (-0.1,0.0)

# Are we decimating the epochs?
decim = 1 # No
# decim = 10 # Yes

# Are we equalizing the number of epochs across conditions? (Important for ANOVAs)
equalize_epochs = False

# Plotting parameters

# Grouping parameters for plotting:

mappings = dict(
#MSA_MSA=['MSA_MSA'],
#        MSA_EGY=['MSA_EGY'],
#        MSA_ENG=['MSA_ENG'],
            #EGY_EGY=['EGY_EGY'],
                #EGY_MSA=['EGY_MSA'],
                #EGY_ENG=['EGY_ENG'],
                switch=['MSA_EGY','MSA_ENG','EGY_MSA','EGY_ENG'],
                noswitch=['MSA_MSA','EGY_EGY']
                )

conditions = event_ids.keys()
newConds = mappings.keys()



# Visual parameters for your plots

colors = dict(#MSA_MSA="#ffb201",
	#MSA_EGY="#2eb135",
	#MSA_ENG="#0000FF",
    #EGY_EGY="#ea7125",
    #EGY_MSA="#01a0e9",
    #EGY_ENG="#005195",
    switch="#b70a53",
    noswitch="#15c8b1"
#	)
    #(MSA_MSA=['MSA_MSA'],
    )
'''
linetype = dict(MSA_MSA="#ffb201",
	MSA_EGY="#2eb135",
	MSA_ENG="#0000FF",
    EGY_EGY="#ea7125",
    EGY_MSA="#01a0e9",
    EGY_ENG="#005195",
    switch="#b70a53",
    noswitch="#15c8b1")
linetype = dict(CatViol="solid",
	SemViol="solid",
	Gramm="dashed",
	)
'''

condNames = dict(#MSA_MSA="MSA_MSA",
            #MSA_EGY='MSA_EGY',
            #MSA_ENG='MSA_ENG',
                    #EGY_EGY='EGY_EGY',
                    #EGY_MSA='EGY_MSA',EGY_ENG='EGY_ENG',
                    switch="Switch",noswitch="No Switch"
                    )
#)

# In case you want to reorder the conditions

newPoss = {
    0:0,
    1:1,
    2:2,
    3:3,
    4:4,
}

#newPoss_tark = {
#    0:0,ِ
#    1:1,
#    2:2,
#    3:3,
#    4:4,
#    5:5
#}

# Regression parameters

# n-tuples:
# ('title', (start.time, end.time), [rois], 'parc', formula, only correct trials?, include grammatical items?, include ung. items?)

parc = mne.read_labels_from_annot('fsaverage',parc='aparc',subjects_dir=subjects_dir,hemi='lh')
#occipTemp_cumm_lh_regions = ['lateraloccipital-lh', 'cuneus-lh', 'lingual-lh','pericalcarine-lh', 'fusiform-lh', 'middletemporal-lh', 'inferiortemporal-lh']
#occipTemp_cumm_lh = [i for i in parc if (i.name in occipTemp_cumm_lh_regions)]
#print(len(occipTemp_cumm_lh))
#occipTemp_cumm = [occipTemp_cumm_lh[0] + occipTemp_cumm_lh[1] + occipTemp_cumm_lh[2] + occipTemp_cumm_lh[3] + occipTemp_cumm_lh[4] + occipTemp_cumm_lh[5] + occipTemp_cumm_lh[6]]
#occipTemp_cumm[0].name = 'occipTemp_cumm'
#mne.write_labels_to_annot(occipTemp_cumm, subject='fsaverage',parc='occipTemp_cumm_lh',subjects_dir=subjects_dir,overwrite=True)
###parc = mne.read_labels_from_annot('fsaveevoked_plot.savefig('Plots/Individuals/%s/%s_evoked.png'%(subj,subj))rage',parc='occipTemp_cumm_lh',subjects_dir=subjects_dir,hemi='lh')
###print(parc)

'''
analyses = [

  # title          times             ROIs            name   parcelation               formula           only corrects? gramms? viols?
#('M170 Analysis_fROI_1', (0.09999999999999998,0.16499999999999998), ['Tark_FROI_left-lh'],'Tark_FROI_left','Tark_FROI_left_1', 'left', 'TP', False, True, False),
#('M170 Analysis_fROI_2', (0.12999999999999998,0.176), ['Tark_FROI_left-lh'],'Tark_FROI_left','Tark_FROI_left_2', 'left', 'TP', False, True, False),
###('M170 Analysis', (0.12, 0.22), ['fusiform-lh'], 'fusiform gyri', 'aparc', 'both', 'TP', False, True, False),
###('M350 Analysis', (0.3, 0.4), ['LOBE.TEMPORAL-lh'], 'temporal lobe', 'PALS_B12_Lobes', 'both', 'stemFreq + wholeWordFreq', False, True, False),
#('PTL Analysis',  (0.2, 0.3), ['LOBE.TEMPORAL-lh'], 'left temporal lobe', 'PALS_B12_Lobes', 'left', 'condition', False, False, True),
###('PTL Analysis',  (0.2, 0.3), ['LOBE.TEMPORAL-lh'], 'temporal lobe', 'PALS_B12_Lobes', 'both', 'condition', False, False, True),
('OF Analysis',   (0.3, 0.5), ['Brodmann.11-lh', 'Brodmann.11-rh', 'Brodmann.10-lh', 'Brodmann.10-rh'], 'orbitofrontal cortex', 'PALS_B12_Brodmann', 'both', 'condition', True, False, True)
#ds['stc'].mean('source')
]

occipTemp = ['lateraloccipital-lh', 'lateraloccipital-rh', 'cuneus-lh', 'cuneus-rh', 'lingual-lh', 'lingual-rh', 'pericalcarine-lh', 'pericalcarine-rh', 'fusiform-lh', 'fusiform-rh', 'middletemporal-lh', 'middletemporal-rh', 'inferiortemporal-lh', 'inferiortemporal-rh']
occipTempLeft = ['lateraloccipital-lh', 'cuneus-lh', 'lingual-lh','pericalcarine-lh', 'fusiform-lh', 'middletemporal-lh', 'inferiortemporal-lh']
occipTempRight = ['lateraloccipital-rh', 'cuneus-rh', 'lingual-rh','pericalcarine-rh', 'fusiform-rh', 'middletemporal-rh', 'inferiortemporal-rh']

#



tark_analyses = [

  # title                               times       ROIs              name                               parc      hemi      formula     include noise? include symb? include words?
('Type Two - Noise',                  (0.1, 0.2), occipTempLeft, 'left occipital and temporal regions', 'aparc', 'left', 'noise', True,            False,        False),
('Type Two - Letter vs. Symbol',      (0.1, 0.2), occipTempLeft, 'left occipital and temporal regions', 'aparc', 'left', 'letter', False,          True,         False),
('Type Two - Letter&Word vs. Symbol', (0.1, 0.2), occipTempLeft, 'left occipital and temporal regions', 'aparc', 'left', 'letterWord', False,      True,         True),
('Type Two - Word vs. Symbol', (0.1, 0.2), occipTempLeft, 'left occipital and temporal regions', 'aparc', 'left', 'word', False,      True,         True),
('Type Two - Noise',                  (0.1, 0.2), occipTempRight, 'right occipital and temporal regions', 'aparc', 'right', 'noise', True,            False,        False),
('Type Two - Letter vs. Symbol',      (0.1, 0.2), occipTempRight, 'right occipital and temporal regions', 'aparc', 'right', 'letter', False,          True,         False),
('Type Two - Letter&Word vs. Symbol', (0.1, 0.2), occipTempRight, 'right occipital and temporal regions', 'aparc', 'right', 'letterWord', False,      True,         True),
('Type Two - Word vs. Symbol', (0.1, 0.2), occipTempRight, 'right occipital and temporal regions', 'aparc', 'right', 'word', False,      True,         True),
#('Type Two - Noise',                  (0.1, 0.2), ['occipTemp_cumm-lh'], 'left occipital and temporal regions - cummulative', 'occipTemp_cumm_lh', 'left', 'noise', True,            False,        False),
#('Type Two - Letter vs. Symbol',      (0.1, 0.2), ['occipTemp_cumm-lh'], 'left occipital and temporal regions - cummulative', 'occipTemp_cumm_lh', 'left', 'letter', False,          True,         False),
#('Type Two - Letter&Word vs. Symbol', (0.1, 0.2), ['occipTemp_cumm-lh'], 'left occipital and temporal regions - cummulative', 'occipTemp_cumm_lh', 'left', 'letterWord', False,      True,         True),
#'Type Two - Word vs. Symbol', (0.1, 0.2), ['occipTemp_cumm-lh'], 'left occipital and temporal regions - cummulative', 'occipTemp_cumm_lh', 'left', 'word', False,      True,         True),
]

tark_analyses = [

  # title                               times       ROIs              name                               parc      hemi      formula     include noise? include symb? include words?
('Type Two - Noise',                  (0.12, 0.20), occipTemp, 'bilateral occipital and temporal regions', 'aparc', 'both', 'noise + pos', True,            False,        False),
('Type Two - Letter vs. Symbol',      (0.12, 0.20), occipTemp, 'bilateral occipital and temporal regions', 'aparc', 'both', 'letter + pos', False,          True,         False),
('Type Two - Letter&Word vs. Symbol', (0.12, 0.2), occipTemp, 'bilateral occipital and temporal regions', 'aparc', 'both', 'letterWord + pos', False,      True,         True),

]

samples = 10000
pmin = 0.05
mintime = 0.010
minsource = 10

regressorFile = 'savantara_tp_13feb2023.csv'

analyses_fROI = [
('M170 Analysis_fROI_1', (0.09999999999999998,0.16499999999999998), ['Tark_FROI_left-lh'],'Tark_FROI_left','Tark_FROI_left_1', 'left', 'TP', False, True, False),
('M170 Analysis_fROI_2', (0.12999999999999998,0.176), ['Tark_FROI_left-lh'],'Tark_FROI_left','Tark_FROI_left_2', 'left', 'TP', False, True, False),

]
'''
