import os
import mne

# GLOBAL VARS
ROOT = r"C:\Users\hz3752\Box\MEG\Data\kidslang_data"
subjects_dir = os.path.join(ROOT, 'mri')

# Left hemisphere
def get_left_hemisphere():
    annot_name = 'PALS_B12_Lobes'
    lobes = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'lh')
    
    label_name = 'LOBE.FRONTAL-lh'
    frontal = [label for label in lobes if label.name==label_name][0]
    
    label_name = 'LOBE.LIMBIC-lh'
    limbic = [label for label in lobes if label.name==label_name][0]
    
    label_name = 'LOBE.OCCIPITAL-lh'
    occipital = [label for label in lobes if label.name==label_name][0]
    
    label_name = 'LOBE.PARIETAL-lh'
    parietal = [label for label in lobes if label.name==label_name][0]
    
    label_name = 'LOBE.TEMPORAL-lh'
    temporal = [label for label in lobes if label.name==label_name][0]
    
    # label_name = 'GYRUS-lh'
    # gyrus = [label for label in lobes if label.name==label_name][0]
    LH = frontal + limbic + occipital + parietal + temporal
    
    return LH

# Right hemisphere
def get_right_hemisphere():
    annot_name = 'PALS_B12_Lobes'
    lobes = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'rh')
    
    label_name = 'LOBE.FRONTAL-rh'
    frontal = [label for label in lobes if label.name==label_name][0]
    
    label_name = 'LOBE.LIMBIC-rh'
    limbic = [label for label in lobes if label.name==label_name][0]
    
    label_name = 'LOBE.OCCIPITAL-rh'
    occipital = [label for label in lobes if label.name==label_name][0]
    
    label_name = 'LOBE.PARIETAL-rh'
    parietal = [label for label in lobes if label.name==label_name][0]
    
    label_name = 'LOBE.TEMPORAL-rh'
    temporal = [label for label in lobes if label.name==label_name][0]
    
    label_name = 'GYRUS-rh'
    gyrus = [label for label in lobes if label.name==label_name][0]
    
    RH = frontal + limbic + occipital + parietal + temporal + gyrus

    return RH


# Left parietal
def get_left_parietal():
    annot_name = 'PALS_B12_Lobes'
    lobes = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'lh')
    
    label_name = 'LOBE.PARIETAL-lh'
    leftpar = [label for label in lobes if label.name==label_name][0]

    return leftpar


# Right parietal
def get_right_parietal():
    annot_name = 'PALS_B12_Lobes'
    lobes = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'rh')
    
    label_name = 'LOBE.PARIETAL-rh'
    rightpar = [label for label in lobes if label.name==label_name][0]
    
    return rightpar


# Left occipital
def get_left_occipital():
    annot_name = 'PALS_B12_Lobes'
    lobes = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'lh')
    
    label_name = 'LOBE.OCCIPITAL-lh'
    leftocc = [label for label in lobes if label.name==label_name][0]

    return leftocc


# Right occipital
def get_right_occipital():
    annot_name = 'PALS_B12_Lobes'
    lobes = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'rh')
    
    label_name = 'LOBE.OCCIPITAL-rh'
    rightocc = [label for label in lobes if label.name==label_name][0]

    return rightocc


# Left Broca's and vmPFC
def get_broca_vmPFC():
    annot_name = 'PALS_B12_Brodmann'
    brodmann = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'lh')
    
    label_name = 'Brodmann.11-lh'
    b11l = [label for label in brodmann if label.name==label_name][0]
    
    label_name = 'Brodmann.10-lh'
    b10l = [label for label in brodmann if label.name==label_name][0]
    
    label_name = 'Brodmann.45-lh'
    b45l = [label for label in brodmann if label.name==label_name][0]
    
    label_name = 'Brodmann.44-lh'
    b44l = [label for label in brodmann if label.name==label_name][0]
    
    label_name = 'Brodmann.47-lh'
    b47l = [label for label in brodmann if label.name==label_name][0]
    
    vmPFC = b11l + b44l + b45l + b47l

    return vmPFC


# Left rest of the frontal lobe
def get_non_language_frontal():
    annot_name = 'PALS_B12_Brodmann'
    brodmann = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'lh')
    
    label_name = 'Brodmann.4-lh'
    b4l = [label for label in brodmann if label.name==label_name][0]
    
    label_name = 'Brodmann.6-lh'
    b6l = [label for label in brodmann if label.name==label_name][0]
    
    label_name = 'Brodmann.8-lh'
    b8l = [label for label in brodmann if label.name==label_name][0]
    
    label_name = 'Brodmann.9-lh'
    b9l = [label for label in brodmann if label.name==label_name][0]
    
    label_name = 'Brodmann.10-lh'
    b10l = [label for label in brodmann if label.name==label_name][0]
    
    label_name = 'Brodmann.46-lh'
    b46l = [label for label in brodmann if label.name==label_name][0]
    
    frontal = b4l + b6l + b8l + b9l + b10l + b46l

    return frontal

# Left PTL
def get_LPTL():
    mne.datasets.fetch_aparc_sub_parcellation(subjects_dir=subjects_dir,verbose=True)
    annot_name = 'aparc_sub'
    lobes = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'lh')

    label_name = "middletemporal_1-lh"
    mtl1 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_2-lh"
    mtl2 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_3-lh"
    mtl3 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_4-lh"
    mtl4 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_1-lh"
    stl1 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_2-lh"
    stl2 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_3-lh"
    stl3 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_4-lh"
    stl4 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_5-lh"
    stl5 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_6-lh"
    stl6 = [label for label in lobes if label.name==label_name][0]
    label_name = "transversetemporal_1-lh"
    ttl1 = [label for label in lobes if label.name==label_name][0]
    label_name = "transversetemporal_2-lh"
    ttl2 = [label for label in lobes if label.name==label_name][0]
    label_name = "bankssts_1-lh"
    bsts1 = [label for label in lobes if label.name==label_name][0]
    label_name = "bankssts_2-lh"
    bsts2 = [label for label in lobes if label.name==label_name][0]
    label_name = "bankssts_3-lh"
    bsts3 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_1-lh"
    fg1 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_2-lh"
    fg2 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_3-lh"
    fg3 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_4-lh"
    fg4 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_5-lh"
    fg5 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_6-lh"
    fg6 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_5-lh"
    itg5 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_6-lh"
    itg6 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_7-lh"
    itg7 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_8-lh"
    itg8 = [label for label in lobes if label.name==label_name][0]
    label_name = "insula_1-lh"
    is1 = [label for label in lobes if label.name==label_name][0]
    label_name = "insula_2-lh"
    is2 = [label for label in lobes if label.name==label_name][0]

    PTL = is1+is2+mtl1+mtl2+mtl3+mtl4+stl1+stl2+stl3+stl4+stl5+stl6+ttl1+ttl2+bsts1+bsts2+bsts3+fg1+fg2+fg3+fg4+fg5+fg6+itg5+itg6+itg7+itg8
    
    return PTL


# Right PTL
def get_RPTL():
    mne.datasets.fetch_aparc_sub_parcellation(subjects_dir=subjects_dir,verbose=True)
    annot_name = 'aparc_sub'
    lobes = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'rh')

    label_name = "middletemporal_1-rh"
    mtl1 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_2-rh"
    mtl2 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_3-rh"
    mtl3 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_4-rh"
    mtl4 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_5-rh"
    mtl5 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_6-rh"
    mtl6 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_1-rh"
    stl1 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_2-rh"
    stl2 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_3-rh"
    stl3 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_4-rh"
    stl4 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_5-rh"
    stl5 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_6-rh"
    stl6 = [label for label in lobes if label.name==label_name][0]
    label_name = "transversetemporal_1-rh"
    ttl1 = [label for label in lobes if label.name==label_name][0]
    label_name = "bankssts_1-rh"
    bsts1 = [label for label in lobes if label.name==label_name][0]
    label_name = "bankssts_2-rh"
    bsts2 = [label for label in lobes if label.name==label_name][0]
    label_name = "bankssts_3-rh"
    bsts3 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_1-rh"
    fg1 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_2-rh"
    fg2 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_3-rh"
    fg3 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_4-rh"
    fg4 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_5-rh"
    fg5 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_6-rh"
    fg6 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_5-rh"
    itg5 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_6-rh"
    itg6 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_7-rh"
    itg7 = [label for label in lobes if label.name==label_name][0]

    PTL = mtl1+mtl2+mtl3+mtl4+mtl5+mtl6+stl1+stl2+stl3+stl4+stl5+stl6+bsts1+bsts2+bsts3+fg1+fg2+fg3+fg4+fg5+fg6+itg5+itg6+itg7+ttl1
    
    return PTL


# Left ALT
def get_LATL():
    annot_name = 'aparc_sub'
    lobes = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'lh')
    label_name = "middletemporal_5-lh"
    mtl5 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_5-lh"
    mtl5 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_6-lh"
    mtl6 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_7-lh"
    mtl7 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_7-lh"
    stl7 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_8-lh"
    stl8= [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_9-lh"
    stl9 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_10-lh"
    stl10 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_11-lh"
    stl11 = [label for label in lobes if label.name==label_name][0]
    label_name = "temporalpole_1-lh"
    tp11 = [label for label in lobes if label.name==label_name][0]
    label_name = "entorhinal_1-lh"
    er = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_7-lh"
    fg7 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_8-lh"
    fg8 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_1-lh"
    itg1 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_2-lh"
    itg2 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_3-lh"
    itg3 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_4-lh"
    itg4 = [label for label in lobes if label.name==label_name][0]
    label_name = "insula_1-lh"
    is1 = [label for label in lobes if label.name==label_name][0]
    label_name = "insula_2-lh"
    is2 = [label for label in lobes if label.name==label_name][0]
    label_name = "insula_3-lh"
    is3 = [label for label in lobes if label.name==label_name][0]
    label_name = "insula_4-lh"
    is4 = [label for label in lobes if label.name==label_name][0]
    label_name = "insula_5-lh"
    is5 = [label for label in lobes if label.name==label_name][0]
    label_name = "insula_6-lh"
    is6 = [label for label in lobes if label.name==label_name][0]
    label_name = "insula_7-lh"
    is7 = [label for label in lobes if label.name==label_name][0]

    ATL = mtl5+mtl6+mtl7+stl7+stl8+stl9+stl10+stl11+tp11+er+fg7+fg8+itg1+itg2+itg3+itg4+is3+is4+is5+is6+is7

    return ATL

# Right ATL
def get_RATL():
    annot_name = 'aparc_sub'
    lobes = mne.read_labels_from_annot('fsaverage', annot_name, subjects_dir = subjects_dir, hemi = 'rh')
    label_name = "middletemporal_9-rh"
    mtl9 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_8-rh"
    mtl8 = [label for label in lobes if label.name==label_name][0]
    label_name = "middletemporal_7-rh"
    mtl7 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_7-rh"
    stl7 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_8-rh"
    stl8= [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_9-rh"
    stl9 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_10-rh"
    stl10 = [label for label in lobes if label.name==label_name][0]
    label_name = "superiortemporal_11-rh"
    stl11 = [label for label in lobes if label.name==label_name][0]
    label_name = "temporalpole_1-rh"
    tp11 = [label for label in lobes if label.name==label_name][0]
    label_name = "entorhinal_1-rh"
    er = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_7-rh"
    fg7 = [label for label in lobes if label.name==label_name][0]
    label_name = "fusiform_8-rh"
    fg8 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_1-rh"
    itg1 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_2-rh"
    itg2 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_3-rh"
    itg3 = [label for label in lobes if label.name==label_name][0]
    label_name = "inferiortemporal_4-rh"
    itg4 = [label for label in lobes if label.name==label_name][0]
    
    ATL = mtl9+mtl8+mtl7+stl7+stl8+stl9+stl10+stl11+tp11+er+fg7+fg8+itg1+itg2+itg3+itg4
    
    return ATL