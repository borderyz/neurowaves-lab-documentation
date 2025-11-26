## ADAPTED FROM JULIEN'S SCRIPT BY MIRIAM ##

import mne, eelbrain, os, glob, pickle
import numpy as np
import pandas as pd
from os.path import join
import matplotlib.pyplot as plt
mne.set_log_level(verbose=False)

# set defaults: change subjects as necessary
ROOT = '/Volumes/MEG/NYUAD-Lab-Server/Personal Files/Sherine/2Tones_Preproc/' #twotones
#ROOT = '/Volumes/server/NEUROLING/PersonalFiles/SherineBouDargham/KidLang/' #kidlang
os.chdir(ROOT)
subjects_dir='/Volumes/MEG/NYUAD-Lab-Server/Personal Files/Sherine/mri/'
#subjects_dir=ROOT+'/mri/' #kidlang
task = 'TwoTones'
typ = 'forAv'

subjects = [
'Y0312', 'Y0366', 'Y0367', 'Y0371', 'Y0372', 'Y0373', 'Y0374', 'Y0375', 'Y0376', 'Y0377',
'Y0378', 'Y0380', 'Y0381', 'Y0382', 'Y0383', 'Y0384', 'Y0387', 'Y0388', 'Y0390', 'Y0392', 'Y0393'
]

#all english subjects
#subjects = [
#'A0446', 'A0448', 'A0449', 'A0451', 'A0452', 'A0456', 'A0457', 'A0458', 'A0459', 'A0460',
#'A0462', 'A0464', 'A0465', 'A0466', 'A0468', 'A0469', 'A0470', 'A0471', 'A0473', 'P062', 'R0001'
#]

#all arabic subjects
#subjects = [
#'Y0312', 'Y0366', 'Y0367', 'Y0371', 'Y0372', 'Y0373', 'Y0374', 'Y0375', 'Y0376', 'Y0377',
#'Y0378', 'Y0380', 'Y0381', 'Y0382', 'Y0383', 'Y0384', 'Y0387', 'Y0388', 'Y0390', 'Y0392', 'Y0393'
#]

##timing parameters
#English
#dialogue/listening
epoch_tmin = -0.7 #fixation
epoch_tmax = 2.35 #after ptcp response
epoch_baseline = (-0.7,-0.6) #baseline during fixation

#Arabic
#dialogue/listening
epoch_tmin = -0.7 #fixation
epoch_tmax = 1.95 #after ptcp response
epoch_baseline = (-0.7,-0.6) #baseline during fixation

#English & Arabic
#production
epoch_tmin = -0.1 #picture onset
epoch_tmax = 0.6 #after ptcp response
epoch_baseline = (-0.1,0) #baseline before picture onset
#two tones
epoch_tmin = -0.1
epoch_tmax = 0.5
epoch_baseline = (-0.1,0)

#EVENT IDS
#dialogue
event_id_all = dict(dialogue_object = 34, dialogue_phrase = 18)
#listening
event_id_all = dict(listening_object = 36, listening_phrase = 20)
#production
event_id_all = dict(production_object = 33, production_phrase = 17)
#two tones
event_id_all = dict(low = 1, high = 2)

'''==========================================================================='''
'''                             Filter, bads, ICA                             '''
'''==========================================================================='''
# THIS SECTION IS COMPLETED ONE PARTICIPANT AT A TIME
subj='Y0393'
cache_dir = join(ROOT, '%s/cache/' %(subj)) #twotones
#cache_dir = join(ROOT, 'Adults/meg/%s/cache/' %(subj)) #kidlang
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

print('Loading raw.')
raw = mne.io.read_raw_fif('%s/%s_TwoTones-raw.fif' %(subj,subj), preload=True) #twotones
#raw = mne.io.read_raw_fif('Adults/meg/%s/%s_KidLang-raw.fif' %(subj,subj), preload=True) #kidlang
print('Raw loaded.')

# filter, then identify bad channels. use raw.plot() to visualize channels
print('Filtering...')
raw.filter(1,40, method='iir')
print('Done filtering.')
print('Plotting channel power/amplitudes spectrum...')
#raw.plot_psd(fmax =50)
print('Plotting raw...')
#raw.plot()
print('Plotted raw.')

#exporting trigger times to csv file
#rawfile = mne.find_events(raw, shortest_event=1)
#pd.DataFrame(rawfile).to_csv("/Users/Sherine/Desktop/rawfile.csv")

#only if you exclude
#input('Press enter when done selecting bads on the plot.')
#pickle.dump(raw.info['bads'], open(cache_dir + 'bad_channels.p', 'wb'))
#print('Interpolating bads.')
#raw.interpolate_bads()

#run ICA. visualize components. select components to remove.
print('Fitting ICA...')
#ica = mne.preprocessing.ICA(n_components=0.95, method='fastica')
ica = mne.preprocessing.ICA(n_components=0.8, method='fastica', random_state=733)
ica.fit(raw, reject_by_annotation=True)
print('Plotting ICA.')
ica.plot_sources(raw)
ica.plot_components()

#apply ICA
print('Excluding bad components and saving.')
#twotones
raw = ica.apply(raw, exclude=ica.exclude)
pickle.dump(ica.exclude, open(cache_dir + '%s_ica_exclude.p' %(subj), 'wb'))
raw.save('%s/%s_ICA-raw.fif' %(subj,subj),overwrite=True)
#kidlang
#pickle.dump(ica.exclude, open(cache_dir + 'Adults/meg/%s/ica_exclude.p' %(subj), 'wb'))
#raw.save('Adults/meg/%s/%s_ICA-raw.fif' %(subj,subj),overwrite=True)
print('Done!')
del raw

'''==========================================================================='''
'''                               Prepare epochs                              '''
'''==========================================================================='''
# THIS SECTION IS COMPLETED IN BATCHES
# epochs will be created for all subjects listed in 'subjects'
# kidlang
for subj in subjects:
    print('Starting epoch assembly: Participant = %s' %subj)
    print('%s: Importing filtered+ICA data' %subj)

    raw = mne.io.read_raw_fif('Adults/meg/%s/%s_ICA-raw.fif' %(subj, subj), preload=True)
    print("%s: Finding events..." %subj)
    events = mne.find_events(raw,min_duration=0.002)

    # audio delay correction for dialogue & listening ONLY - not production
    # this section aligns trigger onset with stimulus onset
#    print('Correcting audio delay...')
#    delay_fname = os.path.join(ROOT,'Adults/aud_delay/%s_aud_delay.txt') % (subj)
#    delay = np.loadtxt(delay_fname)
#    cond_idx = np.squeeze(np.where((events[:,2]==20)|(events[:,2]==36)|(events[:,2]==18)|(events[:,2]==34)))
#    events[cond_idx,0] = events[cond_idx,0]+delay[:,1] # make trigger onset align to stimulus onset
#    print('Audio delay corrected!')

    # specify MEG, pickle raw info
    info = raw.info
    picks_meg = mne.pick_types(info, meg=True, eeg=False, eog=False, stim=False)
    if os.path.exists('Adults/meg/%s/%s/' %(subj,task)) == False:
        os.makedirs('Adults/meg/%s/%s/' %(subj,task))
    pickle.dump(info, open('Adults/meg/%s/%s/%s_info.pickled' %(subj,task,subj), 'wb'))

    # FORWARDS AVERAGING
    print('Forwards averaging! Epochs will print once loaded.')
    if os.path.exists('Adults/meg/%s/%s/epochs_forAv_23' %(subj,task)) == False:
        os.makedirs('Adults/meg/%s/%s/epochs_forAv_23' %(subj,task))
    epochs=mne.Epochs(raw, events=events, event_id=event_id_all, tmin=epoch_tmin, tmax=epoch_tmax, baseline=epoch_baseline, picks=picks_meg, decim=1, preload=True, reject_by_annotation=False)
    print(epochs)

    # load log file that was created in R (see individual_task_logs_2022.r)
    # keep only the good trials (== 1 under column 'keep')
    # order of epochs and log file must be chronological
    print('Importing log file.')
    logfile='logs/logs2023/%s_%s_forwards_2023.csv' %(subj,task)
    log=pd.read_csv(logfile)
    log['keepers']=np.where(log['keep'] == 1,True,False)
    print('Rejecting trials...')
    epochs=epochs[log.keepers]
    log_keepers=log[log.keepers]
    log_keepers.index=np.arange(0,len(epochs))
    print(epochs)
    epochs.save('Adults/meg/%s/%s/epochs_forAv_23/%s_epochs-epo.fif'%(subj,task,subj),overwrite=True)

    # baseline stuff!!!
    # ENGLISH dialogue & listening epochs are 3050 ms in length, production is -700 ms
    # ARABIC dialogue & listening epochs are 2650 ms in length, production is -700 ms
    # save baselines seperately.
    # for dialogue & listening: baseline is before picture onset (i.e., -700 to -600 ms)
    # for production: baseline is -100 ms before trigger until trigger (i.e., -100 to 0 ms)
    # no baseline correction for two tones!

#    # A R A B I C: dialogue & listening baseline stuff!
#    print('Grabbing good epochs.')
#    epochs_out = []
#    baselines = []
#    for epoch in range(len(epochs)):
#        epoch_copy = epochs[epoch].copy()
#        epoch_copy.crop(-0.7, 1.95) #this is the epoch length
#        epoch_copy = epoch_copy.apply_baseline((-0.7,-0.6)) #the actual baseline
#        baseline = epoch_copy.copy().crop(-0.7,-0.6) #the actual baseline again
#        epoch_copy._set_times(np.arange(-0.7,1.955,0.005)) #this is the full epoch length (depends on tmin and tmax)
#        epochs_out.append(epoch_copy)
#        baselines.append(baseline)
#    print('Concatenating and saving.')
#    epochs = mne.concatenate_epochs(epochs_out)
#    baselines = mne.concatenate_epochs(baselines)
#    del epochs_out

    # E N G L I S H: dialogue & listening baseline stuff!
#    print('Grabbing good epochs.')
#    epochs_out = []
#    baselines = []
#    for epoch in range(len(epochs)):
#        epoch_copy = epochs[epoch].copy()
#        epoch_copy.crop(-0.7, 2.35) #this is the epoch length
#        epoch_copy = epoch_copy.apply_baseline((-0.7,-0.6)) #the actual baseline
#        baseline = epoch_copy.copy().crop(-0.7,-0.6) #the actual baseline again
#        epoch_copy._set_times(np.arange(-0.7,2.355,0.005)) #this is the full epoch length (depends on tmin and tmax)
#        epochs_out.append(epoch_copy)
#        baselines.append(baseline)
#    print('Concatenating and saving.')
#    epochs = mne.concatenate_epochs(epochs_out)
#    baselines = mne.concatenate_epochs(baselines)
#    del epochs_out

    # # production baseline stuff! SAME FOR BOTH LANGUAGES
    print('Grabbing good epochs.')
    epochs_out = []
    baselines = []
    for epoch in range(len(epochs)):
        epoch_copy = epochs[epoch].copy()
        epoch_copy.crop(-0.1, 0.6)
        epoch_copy = epoch_copy.apply_baseline((-0.1,0))
        baseline = epoch_copy.copy().crop(-0.1,0)
        epoch_copy._set_times(np.arange(-0.1,0.605,0.005))
        epochs_out.append(epoch_copy)
        baselines.append(baseline)
    print('Concatenating and saving.')
    epochs = mne.concatenate_epochs(epochs_out)
    baselines = mne.concatenate_epochs(baselines)
    del epochs_out

    # Save them!
    epochs.save('Adults/meg/%s/%s/epochs_forAv_23/%s_epochs-epo.fif'%(subj,task,subj),overwrite=True)
    baselines.save('Adults/meg/%s/%s/epochs_forAv_23/%s_baselines-epo.fif'%(subj,task,subj),overwrite=True)
    print('Saved epochs and baselines.')

# two twotones
for subj in subjects:
    print('Generating epochs: Participant = %s' %subj)
    if not os.path.exists('%s/epochs_forAv' %subj):
        os.makedirs('%s/epochs_forAv' %subj)
    # Open text file to save rejection info
    f = open(cache_dir + 'rej_info.txt', 'w')
    # Load data
    print('%s: Importing filtered+ICA data' %subj)
    raw = mne.io.read_raw_fif('%s/%s_ICA-raw.fif' %(subj, subj), preload=True)
    events = mne.find_events(raw,min_duration=0.002)
    # create epochs
    picks_meg = mne.pick_types(raw.info, meg=True, eeg=False, eog=False, stim=False)
    epochs = mne.Epochs(raw, events, event_id=event_id_all,
                        tmin=epoch_tmin, tmax=epoch_tmax, baseline=epoch_baseline, decim=1,
                        picks=picks_meg, preload=True)
    epochs.save('%s/epochs_forAv/%s_epochs-epo.fif'%(subj,subj),overwrite=True)
    print('Saved epochs.')

'''==========================================================================='''
'''                           Epoch rejection                                 '''
'''==========================================================================='''
# THIS SECTION IS COMPLETED ONE PARTICIPANT AT A TIME
# specify the participant below.
# specify event ids if this is a new session!
subj = 'R0001'
print('Reading epochs...')
epochs = mne.read_epochs('Adults/meg/%s/%s/epochs_forAv_23/%s_epochs-epo.fif' %(subj,task,subj))
epochs = epochs['%s_phrase'%(task),'%s_object'%(task)]
print (epochs)

# epoch rejection gui
# note: if the epoch rejection gui isn't showing up, rerun terminal WITHOUT importing matplotlib
print ('Pulling up epoch rejection GUI...')
eelbrain.gui.select_epochs(epochs, vlim=2e-12, mark=['MEG 087','MEG 130'])

# apply epoch rejection.
# take note of epochs_rej: here you will learn the final count of epochs per condition
print('Applying epoch rejection...')
rejfile = eelbrain.load.unpickle('Adults/meg/%s/%s/%s_%s_rejfile.pickled' %(subj,task,subj,task))
rejs = rejfile['accept'].x
epochs_rej = epochs[rejs]
print('Equalizing epochs...')
epochs_rej.equalize_event_counts(event_id_all)
info = epochs_rej.info
baselines = mne.read_epochs('Adults/meg/%s/%s/epochs_forAv_23/%s_baselines-epo.fif'%(subj,task,subj))
baselines = baselines[rejs]
print(epochs_rej)
print ('Saving epochs to file...')
epochs_rej.save('Adults/meg/%s/%s/%s_%s_rej_epochs-epo.fif' %(subj,task,subj,task),overwrite=True)
baselines.save('Adults/meg/%s/%s/%s_%s_rej_baselines-epo.fif' %(subj,task,subj,task),overwrite=True)
print ('Done.')

#two TwoTones
subj = 'Y0393'
epochs = mne.read_epochs('%s/epochs_forAv/%s_epochs-epo.fif' %(subj,subj))
eelbrain.gui.select_epochs(epochs, vlim=2e-12, mark=['MEG 087','MEG 130'])
# apply epoch rejection.
print('Applying epoch rejection...')
rejfile = eelbrain.load.unpickle('%s/%s_rejfile.pickled' %(subj,subj))
rejs = rejfile['accept'].x
epochs_rejfile = epochs[rejs]
print('Equalizing epochs...')
epochs_rejfile.equalize_event_counts(event_id_all)
raw = mne.io.read_raw_fif('%s/%s_ICA-raw.fif' %(subj, subj), preload=True)
print(epochs_rejfile)
print ('Saving epochs to file...')
epochs_rejfile.save('%s/epochs_forAv/%s_epochs_rej-epo.fif' %(subj,subj),overwrite=True)
pickle.dump(raw.info, open('%s/%s_info.pickled' %(subj,subj), 'wb'))
print ('Done.')

'''==========================================================================='''
'''                               Create STCs                                 '''
'''==========================================================================='''
## THIS SECTION IS FOR THE MAINDATASET + PRODUCTION
for subj in subjects:
    print ("STCs for subj = %s:"%subj)
    print('Epochs are %s'%(typ))
    print ('Importing data...')

    epochs_rej = mne.read_epochs('Adults/meg/%s/%s/%s_%s_rej_epochs-epo.fif' %(subj,task,subj,task))
    info = epochs_rej.info
    trans = mne.read_trans('Adults/meg/%s/%s-trans.fif' %(subj,subj))
    bem_fname = os.path.join(subjects_dir, '%s/bem/%s-inner_skull-bem-sol.fif'%(subj,subj))
    src_fname = os.path.join(subjects_dir, '%s/bem/%s-ico-4-src.fif' %(subj,subj))
    fwd_fname = os.path.join(ROOT,'Adults/meg/%s/%s/%s-fwd.fif' %(subj,task,subj))
    cov_fname = os.path.join(ROOT,'Adults/meg/%s/%s/%s-cov.fif' %(subj,task,subj))

    #------------------------get evoked-----------------------------#

    print ('%s: Creating evoked responses' %subj)
    evoked = []
    conditions = event_id_all.keys()
    for cond in conditions:
        evoked.append(epochs_rej[cond].average())
    print ('Done.')

    # sanity check: plot evoked
    if not os.path.isdir('Adults/meg/%s/%s/evoked/'%(subj,task)):
        os.makedirs('Adults/meg/%s/%s/evoked/'%(subj,task))
    all_evokeds = mne.combine_evoked(evoked, weights='equal')
    evoked_plot = all_evokeds.plot_joint(show=False)
    evoked_plot.savefig('Adults/meg/%s/%s/evoked/%s_forwards.png'%(subj,task,subj))
    print('Plot saved.')

    # marco's: compute evoked responses
    print('MARCO: computing evoked responses...')
    evk = []
    conditions = event_id_all.keys()
    for cond in conditions:
        evk.append(epochs_rej[cond].average())
    # plot evoked
    print('plotting...')
    evk_dir = os.path.join('/Users/Sherine/Desktop/figs/stc_april2023')
    if not os.path.exists(evk_dir):
        os.makedirs(evk_dir)
    evk_all = mne.combine_evoked(evk, weights='equal')
    evk_fname = os.path.join(evk_dir, '%s_%s_avg_allcond.png') %(subj,task)
    evk_plot = evk_all.plot_joint(show = False,
                                  ts_args = dict(gfp=True, ylim=dict(mag=[-300, 300]),
                                                 time_unit='ms'),
                                  topomap_args = dict(vmin=-100, vmax=100,
                                                      time_unit='ms'))
    evk_plot.savefig(evk_fname)
    plt.close(evk_plot)

    #----------------------source space---------------------------#
    print ('Generating source space...')
    src = mne.read_source_spaces(src_fname)
    print ('Done.')

    #-------------------------- BEM ------------------------------#
    print('Reading bem solution...')
    bem = mne.read_bem_solution(bem_fname)
    print ('Done.')

    #--------------------forward solution-------------------------#
    print('Getting forward solution')
    fwd = mne.make_forward_solution(info=info, trans=trans, src=src, bem=bem_fname, ignore_ref=True)
    mne.write_forward_solution(fwd_fname, fwd, overwrite=True)
    fwd = mne.read_forward_solution(fwd_fname)
    print ('Done.')

    #----------------------covariance------------------------------#
    print ('Getting covariance')
    cov = mne.compute_covariance(epochs_rej,tmin=epoch_baseline[0],tmax=epoch_baseline[1], method=['shrunk', 'diagonal_fixed', 'empirical'])
    cov.save(cov_fname) #overwrite=True
    print ('Done. File saved.')

    #---------------------Inverse operator-------------------------#
    print ('Getting inverse operator')
    fixed = False
    SNR = 3 # 3 for ANOVAs, 2 for regressions
    if fixed == True:
        fwd = mne.convert_forward_solution(fwd, surf_ori=True)
    inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, depth=0.8, loose=0.2, fixed=fixed) #fixed=False: Ignoring dipole direction.
    lambda2 = 1.0 / SNR ** 2.0
    print('Done.')

    #--------------------------STCs--------------------------------#
    #change stc directory based on whether created stcs are production, two tones or part of the maindataset
    print ('%s: Creating STCs...'%subj)
    for ev in evoked:
        stc = mne.minimum_norm.apply_inverse(ev, inv, lambda2=lambda2, method='dSPM')
        morph = mne.compute_source_morph(stc, subject_from=subj, subject_to='fsaverage', subjects_dir=subjects_dir, spacing=4)
        stc_fsaverage = morph.apply(stc)
        stc_fsaverage.save('Adults/stc/eng_stc_2x2/production/%s/%s_%s_dSPM' %(ev.comment,subj,ev.comment)) #overwrite=True
        del stc, stc_fsaverage
    print ('DONE CREATING STCS FOR SUBJ = %s'%subj)

    #--------------------------STCs 2.0------------------------------#
    #to split your task_cond.stc files into task_cond_word1.stc and task_cond_word2.stc
    #not needed for production, just for dialogue & listening
    group = 'adults'
    main_dir = '/Volumes/server/NEUROLING/PersonalFiles/SherineBouDargham/KidLang/'
    os.chdir(main_dir) # change directory
    mri_dir = os.path.join(main_dir, 'mri')         # mri directory
    meg_dir = os.path.join(main_dir, group, 'meg')  # meg directory
    stc_dir = os.path.join(main_dir, group, 'stc/ara_stc_2x2/maindataset')         # stc directory
    new_stc_dir = os.path.join(main_dir, group, 'stc/ara_stc_3x2/maindataset')

    times = np.arange(-0.1,0.6+0.001,0.001)
    cond_list = ['listening_phrase',
                 'listening_object',
                 'dialogue_phrase',
                 'dialogue_object']

    for c, cond in enumerate(cond_list):
        print(cond)

        if cond[-6:] == 'phrase':
            w2_onset = 0.875
        elif cond[-6:] == 'object':
            w2_onset = 0.65

        for s, subj in enumerate(subjects):
            print(subj)

            stc_fname = os.path.join(stc_dir, '%s', '%s_%s_dSPM') % (cond, subj, cond)
            stc = mne.read_source_estimate(stc_fname)
            stc_w1 = stc.copy()
            stc_w2 = stc.copy()

            # crop
            stc_w1.crop(-0.1, 0.6)
            stc_w1._times = times
            stc_w1._tmin = times[0]
            stc_w2.crop(w2_onset-0.1, w2_onset+0.6)
            stc_w2._times = times
            stc_w2._tmin = times[0]

            # save stc
            stc_w1_fname = os.path.join(new_stc_dir, '%s_w1', '%s_%s_w1_dSPM') %(cond, subj, cond)
            stc_w1.save(stc_w1_fname)
            print(stc_w1)
            stc_w2_fname = os.path.join(new_stc_dir, '%s_w2', '%s_%s_w2_dSPM') %(cond, subj, cond)
            stc_w2.save(stc_w2_fname)
            print(stc_w2)

## THIS SECTION IS FOR TWO TONES
for subj in subjects:
    cache_dir = join(ROOT,'meg/%s/cache/'%subj)
    print ("STCs for subj = %s:"%subj)
    print('Epochs are %s'%(typ))
    print ('Importing data...')
    info = pickle.load(open('meg/%s/%s_info.pickled' %(subj,subj), 'rb'))
    epochs_rej = mne.read_epochs('meg/%s/epochs_%s/%s_epochs_rej-epo.fif' %(subj,typ,subj))
    trans = mne.read_trans('meg/%s/%s-trans.fif' %(subj,subj))
    bem_fname = os.path.join(subjects_dir, '%s/bem/%s-inner_skull-bem-sol.fif'%(subj,subj))
    src_fname = os.path.join(subjects_dir, '%s/bem/%s-ico-4-src.fif' %(subj,subj))
    fwd_fname = 'meg/%s/epochs_%s/%s-fwd.fif' %(subj,typ,subj)
    cov_fname = 'meg/%s/epochs_%s/%s-cov.fif' %(subj,typ,subj)

    #------------------------get evoked-----------------------------#
    print ('%s: Creating evoked responses' %subj)
    if not os.path.isdir('meg/%s/evoked/'%subj):
        os.makedirs('meg/%s/evoked/'%subj)
    evokeds = []
    for cond in event_id_all.keys():
        ev = epochs[cond].average()
        ev_plot = ev.plot_joint(show=False)
        ev_plot.savefig(cache_dir + '%s_evoked.jpg' %cond)
        evokeds.append(ev)
    print ('Done.')

    # sanity check: plot evoked
    all_evokeds = mne.combine_evoked(evokeds, weights='equal')
    evoked_plot = all_evokeds.plot_joint(show=False)
    evoked_plot.savefig('meg/%s/evoked/%s_forwards.png'%(subj,subj))

    # marco's: compute evoked responses
    print('MARCO: computing evoked responses...')
    evk = []
    conditions = event_id_all.keys()
    for cond in conditions:
        evk.append(epochs_rej[cond].average())
    # plot evoked
    print('plotting...')
    evk_dir = os.path.join('/Users/Sherine/Desktop/figs/2tones')
    if not os.path.exists(evk_dir):
        os.makedirs(evk_dir)
    evk_all = mne.combine_evoked(evk, weights='equal')
    evk_fname = os.path.join(evk_dir, '%s_%s_avg_allcond.png') %(subj,task)
    evk_plot = evk_all.plot_joint(show = False,
                                  ts_args = dict(gfp=True, ylim=dict(mag=[-300, 300]),
                                                 time_unit='ms'),
                                  topomap_args = dict(vmin=-100, vmax=100,
                                                      time_unit='ms'))
    evk_plot.savefig(evk_fname)
    plt.close(evk_plot)

    #----------------------source space---------------------------#
    print ('Generating source space...')
    src = mne.read_source_spaces(src_fname)
    print ('Done.')

    #-------------------------- BEM ------------------------------#
    print('Reading bem solution...')
    bem = mne.read_bem_solution(bem_fname)
    print ('Done.')

    #--------------------forward solution-------------------------#
    print('Getting forward solution')
    fwd = mne.make_forward_solution(info=info, trans=trans, src=src, bem=bem_fname, ignore_ref=True)
    mne.write_forward_solution(fwd_fname, fwd, overwrite=True)
    fwd = mne.read_forward_solution(fwd_fname)
    print ('Done.')

    #----------------------covariance------------------------------#
    print ('Getting covariance')
    cov = mne.compute_covariance(epochs_rej,tmin=epoch_baseline[0],tmax=epoch_baseline[1], method=['shrunk', 'diagonal_fixed', 'empirical'])
    cov.save(cov_fname) #overwrite=True
    print ('Done. File saved.')

    #---------------------Inverse operator-------------------------#
    print ('Getting inverse operator')
    fixed = False
    SNR = 3 # 3 for evoked, 2 for single-trial/epochs
    lambda2 = 1.0 / SNR ** 2.0

    if fixed:
        fwd = mne.convert_forward_solution(fwd, surf_ori=True)
    inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, depth=0.8, loose=0.2, fixed=fixed) #fixed=False: Ignoring dipole direction.

    #--------------------------STCs--------------------------------#
    print ('%s: Creating STCs...'%subj)
    for ev in evokeds:
        stc = mne.minimum_norm.apply_inverse(ev, inv, lambda2=lambda2, method='dSPM')
        morph = mne.compute_source_morph(stc, subject_from=subj, subject_to='fsaverage', subjects_dir=subjects_dir, spacing=4)
        stc_fsaverage = morph.apply(stc)
        stc_fsaverage.save('stc/twotones/%s/%s_%s_dSPM' %(ev.comment,subj,ev.comment))
        del stc, stc_fsaverage
    print ('DONE CREATING STCS FOR SUBJ = %s'%subj)

    # delete variables
    del epochs_rej, info, trans, src, fwd, cov, inv, evoked
