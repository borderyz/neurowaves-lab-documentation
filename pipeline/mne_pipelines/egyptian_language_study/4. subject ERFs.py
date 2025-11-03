#######################
#Creating subject ERFs
#######################
#this runs in two chunks because you have to manually inspect the ICA and manually set the components to exclude
#the first chunk is pretty fast - maybe 1 or 2 minutes
#the second chunk takes 20 minutes or so.

import mne
import autoreject

#%% Up through ICA

#----------------
# 1. Read in the fif file
#----------------

# set path for my computer. Needs to change to fit other's computers.

subject = '012'

data_path = "/Users/jrs9906/Documents/MEG data/egyptian/raw_data/egy_sub_"+subject+"/meg-kit/"
save_path = "/Users/jrs9906/Documents/MEG data/egyptian/"
subject = "egyptian_sub"+subject

#read in the raw data
raw = mne.io.read_raw_fif(
    fname=data_path+subject+'_CALM-raw.fif',
    preload=True,
    verbose=False,
    )

#read in the events file

events = mne.read_events(filename=data_path+subject+'_events_edited.eve')

#----------------
# 2. Highpass filter
#----------------
raw.filter(l_freq=.1, h_freq=None)


#-----------------
#annotate breaks?
#-----------------
#I am going to make this very close to the edges of sentences, so it might need some tweaking
break_annots=mne.preprocessing.annotate_break(
    raw, 
    events=events, 
    min_break_duration=4.0, 
    t_start_after_previous=2.0, 
    t_stop_before_next=1.0, 
    ignore=('bad', 'edge'), 
    verbose=None
)

raw.set_annotations(break_annots)

#Look at the annotations?
raw.plot(events=events)

#----------------
#3. Find and interpolate bad channels?
#----------------
#So, reject_by_annotation=True does not work for finding bad channels. I don't think this is the end of the world, but it would be nice to ignore the breaks..

#the tutorial says we need to find bad channels first?
raw.info["bads"] = [] #this should already be empty

auto_noisy_chs = mne.preprocessing.find_bad_channels_lof(
    raw,
    return_scores=False,
    verbose=True,
    picks='meg',
    )
print(auto_noisy_chs)  #print them out

#update the bads list in the dataset
bads = raw.info["bads"] + auto_noisy_chs
raw.info["bads"] = bads

#interpolate?
raw.interpolate_bads()

#----------------
# 4. ICA: to remove ECG only (blinks might remove SAN)
#----------------
#ICA automatically ignores the annotated bad segments, so you can't use reject_by_annotation=True explicitly.

#run the ICA on a copy of the data with a higher high-pass filter (works better)
filt_raw = raw.copy().filter(l_freq=1.0, h_freq=None)

#fit the ICA
ica = mne.preprocessing.ICA(
    n_components=15, 
    max_iter="auto", 
    random_state=17,
)

ica.fit(filt_raw)
ica

#evaluate BY HAND
#get explained variance
# explained_var_ratio = ica.get_explained_variance_ratio(filt_raw)
# for channel_type, ratio in explained_var_ratio.items():
#     print(f"Fraction of {channel_type} variance explained by all components: {ratio}")

#plot the timecourse
ica.plot_sources(filt_raw)

#%% Manually input the exclusion and run the rest of the steps

#plot topoplot
ica.plot_components()

#plot overlay of data with and without the component
ica.plot_overlay(filt_raw, exclude=[0], picks="mag")

#properties of the component
ica.plot_properties(filt_raw, picks=[5])

#choose the channel(s) to exclude
ica.exclude = [0]

#apply to a copy of the data (safe) or the original data (if you are sure)
#reconst_raw = raw.copy()
#ica.apply(reconst_raw)
ica.apply(raw)

#remove the filt_raw
del filt_raw

#This tutorial suggests that you can find the ECG component automatically:
    #https://mne.tools/stable/auto_tutorials/preprocessing/40_artifact_correction_ica.html
    #but it is not returning anything for me
# ica.exclude = []
# # find which ICs match the ECG pattern
# ecg_indices, ecg_scores = ica.find_bads_ecg(raw, method="correlation", threshold="auto")
# ica.exclude = ecg_indices

#----------------
# 5. Create epochs
#----------------

#This requires logical details of the experimental conditions

#WH
#cleft 136, from 2 to 6 (after that it mismatches)
#cleft_control is yn 129, 1-5 (after that mismatches)
 #insitu 132, 6 (wh) to 9 (end), but will add 5(verb)-9 for extra
#insitu_control, yn 129, 6 (N) to 9, but will add 5(verb)-9 for extra

#exploration (creates mismatch at item 7 in cleft and 6 in insitu/yn)
#cleft 3-9
#insitu and yn: 2-8

#BA
#For search, we want to see 2 to 6
#For discourse update, we want to see 6 to 8
#We can do this with the full sentence and re-baselining because they are perfectly matched
#BA 34 - lexical matching is perfect
#Control 33 - lexical matching is perfect

#BVA
#BVA 68 - 4-7: 5 (self) to 7 (end), add 4 (V) for extra
#RA 66 - 3-6: 4 (self) to 6 (end), add 3 (V) for extra
#NP 65 - 4-7: 5 (noun) to 7 (end), add 4 (V) for extra

#BVA-Exploration
#BVA: 1-7
#NP: 1-7
#RA: 1-6 DONE
#NP: 2-7 DONE


#N400 paradigm - analyze final word
#congruent 4, 5, 6, 7 -> 4004, 5005, 6006, 7007
#incongruent 20, 21, 22, 23? -> 4104, 5105, 6106, 7107


#define a dictionary for events; I will separate by sub-design
wh_event_dict = {
    "cleft": 1362,
    "cleft_control": 1291,
    "in_situ": 1325,
    "in_situ_control": 1295,
}

ba_event_dict = {
    "ba_target": 341,
    "ba_control": 331,
}

bva_event_dict = {
    "bva": 684,
    "ra": 663,
    "np": 654,
}

N400_event_dict = {
    "congruent/4": 4004,
    "congruent/5": 5005,
    "congruent/6": 6006,
    "congruent/7": 7007,
    "incongruent/4": 4104,
    "incongruent/5": 5105,
    "incongruent/6": 6106,
    "incongruent/7": 7107,
}


#define time windows for each
wh_tmin, wh_tmax = (-0.2, 3.0) #5 words total
ba_tmin, ba_tmax = (-0.2, 4.8) #8 words
bva_tmin, bva_tmax = (-0.2, 2.4) #4 words
N400_tmin, N400_tmax = (-0.2, 1.2)

wh_epochs = mne.Epochs(
    raw=raw,
    events=events,
    event_id=wh_event_dict,
    tmin=wh_tmin,
    tmax=wh_tmax,
    proj=True,
    baseline=None,
    #reject_by_annotation=True,
    #reject=reject_criteria,
    preload=True,
    picks=mne.pick_types(raw.info, meg=True, exclude=[]), #for some reason, this is necessary to not get an error in the ar.fit() command later.
)

ba_epochs = mne.Epochs(
    raw=raw,
    events=events,
    event_id=ba_event_dict,
    tmin=ba_tmin,
    tmax=ba_tmax,
    proj=True,
    baseline=None,
    #reject_by_annotation=True,
    #reject=reject_criteria,
    preload=True,
    picks=mne.pick_types(raw.info, meg=True, exclude=[]), #for some reason, this is necessary to not get an error in the ar.fit() command later.
)

bva_epochs = mne.Epochs(
    raw=raw,
    events=events,
    event_id=bva_event_dict,
    tmin=bva_tmin,
    tmax=bva_tmax,
    proj=True,
    baseline=None,
    #reject_by_annotation=True,
    #reject=reject_criteria,
    preload=True,
    picks=mne.pick_types(raw.info, meg=True, exclude=[]), #for some reason, this is necessary to not get an error in the ar.fit() command later.
)

N400_epochs = mne.Epochs(
    raw=raw,
    events=events,
    event_id=N400_event_dict,
    tmin=N400_tmin,
    tmax=N400_tmax,
    proj=True,
    baseline=None,
    #reject_by_annotation=True,
    #reject=reject_criteria,
    preload=True,
    on_missing='ignore',
    picks=mne.pick_types(raw.info, meg=True, exclude=[]), #for some reason, this is necessary to not get an error in the ar.fit() command later.
)


#plot epochs
N400_epochs.plot(events=True)

#an image map of the epochs
N400_epochs["incongruent"].plot_image(combine="mean")



#save epochs
N400_epochs.save(
    fname=save_path+"N400/epochs_dirty/"+subject+"_epochs-epo.fif",
    overwrite=True,
)
wh_epochs.save(
    fname=save_path+"wh/epochs_dirty/"+subject+"_epochs-epo.fif",
    overwrite=True,
)
bva_epochs.save(
    fname=save_path+"bva/epochs_dirty/"+subject+"_epochs-epo.fif",
    overwrite=True,
)
ba_epochs.save(
    fname=save_path+"ba/epochs_dirty/"+subject+"_epochs-epo.fif",
    overwrite=True,
)

#----------------
#reject artifacts visually?
#----------------
#https://github.com/mne-tools/mne-python/issues/6361
#This page suggests that epochs.plot() will allow you to click on trials to mark them as bad
#When the plot is closed, it will remove those trials
#To see which ones were removed, you can use some cobinaton of epochs.drop_log and epochs.selection 

#----------------
# 6. Use autoreject to repair bad channels and remove bad trials?
#----------------
#Is there a way to only use this for trials, not channel interpolation?

#short name of the function
ar = autoreject.AutoReject()

#using fit_transform to do both steps at once

N400_epochs_clean = ar.fit_transform(N400_epochs)
wh_epochs_clean = ar.fit_transform(wh_epochs)
bva_epochs_clean = ar.fit_transform(bva_epochs)
ba_epochs_clean = ar.fit_transform(ba_epochs)

#save cleaned epochs
N400_epochs_clean.save(
    fname=save_path+"N400/epochs_clean/"+subject+"_epochs-epo.fif",
    overwrite=True,
)

wh_epochs_clean.save(
    fname=save_path+"wh/epochs_clean/"+subject+"_epochs-epo.fif",
    overwrite=True,
)

bva_epochs_clean.save(
    fname=save_path+"bva/epochs_clean/"+subject+"_epochs-epo.fif",
    overwrite=True,
)

ba_epochs_clean.save(
    fname=save_path+"ba/epochs_clean/"+subject+"_epochs-epo.fif",
    overwrite=True,
)

#plots of rejections, requires return_log to be TRUE above
#Requires modifying the arfit command above like this: N400_epochs_clean, N400_reject_log = ar.fit_transform(N400_epochs, return_log=True)
#N400_epochs_clean[N400_reject_log.bad_epochs].plot()
#N400_reject_log.plot('horizontal')


#----------------
# 7. Create ERFs: baseline and average
#----------------

#low pass filter?

#cleaned
N400_epochs_clean.filter(l_freq=None, h_freq=30)
wh_epochs_clean.filter(l_freq=None, h_freq=30)
bva_epochs_clean.filter(l_freq=None, h_freq=30)
ba_epochs_clean.filter(l_freq=None, h_freq=30)

#define some baselines
baseline_pre = (None, 0) #typical for word 1
baseline_400 = (.400, .600) #basically, typical for word 2
baseline_50 = (0, .050) #post-stimulus for word 1
baseline_650 = (.600, .650) #post-stimelus for word 2

cleft_choice = baseline_400
in_situ_choice = baseline_400
ba_choice = baseline_50
bva_choice = baseline_400

#MNE can only create one condition at a time

#dirty epochs; with baselining happening during averaging:
# N400_congruent_ERF = N400_epochs["congruent"].average().apply_baseline(baseline_pre)
# N400_incongruent_ERF = N400_epochs["incongruent"].average().apply_baseline(baseline_pre)

# wh_cleft_ERF = wh_epochs["wh_cleft"].average().apply_baseline(wh_choice)
# wh_in_situ_ERF = wh_epochs["wh_in_situ"].average().apply_baseline(wh_choice)
# yn_ERF = wh_epochs["yn"].average().apply_baseline(wh_choice)

# ba_target_ERF = ba_epochs["ba_target"].average().apply_baseline(ba_choice)
# ba_control_ERF = ba_epochs["ba_control"].average().apply_baseline(ba_choice)

# bva_ERF = bva_epochs["bva"].average().apply_baseline(bva_choice)
# ra_ERF = bva_epochs["ra"].average().apply_baseline(bva_choice)
# np_ERF = bva_epochs["np"].average().apply_baseline(bva_choice)

#clean epochs; with baselining 
N400_congruent_clean_ERF = N400_epochs_clean["congruent"].average().apply_baseline(baseline_pre)
N400_incongruent_clean_ERF = N400_epochs_clean["incongruent"].average().apply_baseline(baseline_pre)

cleft_clean_ERF = wh_epochs_clean["cleft"].average().apply_baseline(cleft_choice)
cleft_control_clean_ERF = wh_epochs_clean["cleft_control"].average().apply_baseline(cleft_choice)
in_situ_clean_ERF = wh_epochs_clean["in_situ"].average().apply_baseline(in_situ_choice)
in_situ_control_clean_ERF = wh_epochs_clean["in_situ_control"].average().apply_baseline(in_situ_choice)

ba_target_clean_ERF = ba_epochs_clean["ba_target"].average().apply_baseline(ba_choice)
ba_control_clean_ERF = ba_epochs_clean["ba_control"].average().apply_baseline(ba_choice)

bva_clean_ERF = bva_epochs_clean["bva"].average().apply_baseline(bva_choice)
ra_clean_ERF = bva_epochs_clean["ra"].average().apply_baseline(bva_choice)
np_clean_ERF = bva_epochs_clean["np"].average().apply_baseline(bva_choice)



#----------------
# 8. Saving ERFs
#----------------

#evoked.save() #saves one ERF at a time
#to save multiple evoked fields into a single file, use this function:
# mne.write_evokeds(
#     fname=save_path+"wh/subject_ERFs_dirty/"+subject+"_ERFs-ave.fif",
#     evoked=[wh_cleft_ERF, wh_in_situ_ERF, yn_ERF],
#     overwrite=True,
# )

# mne.write_evokeds(
#     fname=save_path+"ba/subject_ERFs_dirty/"+subject+"_ERFs-ave.fif",
#     evoked=[ba_target_ERF, ba_control_ERF],
#     overwrite=True,
# )

# mne.write_evokeds(
#     fname=save_path+"bva/subject_ERFs_dirty/"+subject+"_ERFs-ave.fif",
#     evoked=[bva_ERF, ra_ERF, np_ERF],
#     overwrite=True,
# )

# mne.write_evokeds(
#     fname=save_path+"N400/subject_ERFs_dirty/"+subject+"_ERFs-ave.fif",
#     evoked=[N400_congruent_ERF, N400_incongruent_ERF],
#     overwrite=True,
# )

#cleaned
mne.write_evokeds(
    fname=save_path+"wh/subject_ERFs_clean/"+subject+"_ERFs-ave.fif",
    evoked=[cleft_clean_ERF, in_situ_clean_ERF, cleft_control_clean_ERF, in_situ_control_clean_ERF],
    overwrite=True,
)

mne.write_evokeds(
    fname=save_path+"ba/subject_ERFs_clean/"+subject+"_ERFs-ave.fif",
    evoked=[ba_target_clean_ERF, ba_control_clean_ERF],
    overwrite=True,
)

mne.write_evokeds(
    fname=save_path+"bva/subject_ERFs_clean/"+subject+"_ERFs-ave.fif",
    evoked=[bva_clean_ERF, ra_clean_ERF, np_clean_ERF],
    overwrite=True,
)

mne.write_evokeds(
    fname=save_path+"N400/subject_ERFs_clean/"+subject+"_ERFs-ave.fif",
    evoked=[N400_congruent_clean_ERF, N400_incongruent_clean_ERF],
    overwrite=True,
)

