import numpy as np
import pandas as pd
import itertools
from scipy import signal, fftpack
import matplotlib as mpl
import matplotlib.pyplot as plt

from mne.viz import plot_filter, plot_ideal_filter
from mne.preprocessing import ICA

import mne
import copy, os, sys
import os.path as op

def rawload(megpath, subj, expname, tag = '_NR', preload = True):
    '''
    Load fif file. Preload is True as default
    Input
    -----
    megpath: path to meg folder
    subj: subject number, string
    expname: string. Experiment identifier (name)

    Output
    ------
    raw: raw object
    '''
    print('Loading raw fif file for subject %s...' % subj)
    raw = mne.io.read_raw_fif('%s/%s/%s_%s%s-raw.fif' % (megpath, subj, subj, expname, tag), preload = preload)

    # Insert subj and megpath into info dictionary for easy retrieval!
    raw.info['subj'] = subj
    raw.info['megpath'] = megpath
    raw.info['expname'] = expname

    return raw

# FILTERING
def rawfilt(raw, h_freq = 40., l_freq = 0.1, plot_diff = True):
    '''
    Filter data in raw object from l_freq to h_freq. iir method is used by default.
    Input
    -----
    raw: raw object
    h_freq: LPF frequency cutoff
    l_freq: HPF frequency cutoff
    plot_diff: Plot a comparison between the two channels

    Output
    ------
    raw: filtered raw object
    '''
    print('\nFILTERING')
    subj = raw.info['subj']
    megpath = raw.info['megpath']
    expname = raw.info['expname']

    # Filtering and visual comparison for a single MEG channel
    #print('\nFiltering between %d and %d Hz... ' % (l_freq, h_freq))
    x0 = raw.copy().pick_channels(['MEG 001']).crop(tmin = 60., tmax = 120.) # saving a copy of original channel, only one minute
    #### TODO TODO: DOUBLE CHECK: FIR MIGHT BE BETTER?
    raw.filter(l_freq = l_freq, h_freq = h_freq, method = 'iir', verbose = True) # Band-pass filter between l_freq & h_freq.
    #raw.filter(l_freq = l_freq, h_freq = h_freq, method = 'fir', phase = 'zero-double', verbose = True) # Band-pass filter between l_freq & h_freq.
    x1 = raw.copy().pick_channels(['MEG 001']).crop(tmin = 60., tmax = 120.) # Choose the same time window of filtered signal

    if plot_diff:
        print('Plotting comparison between filtered and unfiltered data')
        x0, times = x0[:,:]
        x0 = x0[0]
        x1, times = x1[:,:]
        x1 = x1[0]

        figfilt, axes = plt.subplots(3,1, figsize = (6,12))
        axes[0].plot(times, x1)
        axes[0].plot(times, x0)# - 1e-12)
        axes[0].set(xlabel = 'Time (sec)', xlim = [times[0], times[1000]])
        X0 = fftpack.fft(x0)
        X1 = fftpack.fft(x1)
        freqs = fftpack.fftfreq(len(x0), 1./raw.info['sfreq'])
        mask = freqs >= 0
        X0 = X0[mask]
        X1 = X1[mask]
        freqs = freqs[mask]
        axes[1].plot(freqs, 20 * np.log10(np.maximum(np.abs(X1), 1e-16)))
        axes[1].plot(freqs, 20 * np.log10(np.maximum(np.abs(X0), 1e-16)))
        axes[1].set(xlim = [0, 60], xlabel = 'Frequency (Hz)', ylabel = 'Magnitude (dB)')
        angles = np.absolute((np.angle(X1) - np.angle(X0))) / (2 * np.pi)
        angles[np.absolute(angles) > 0.5] = angles[np.absolute(angles) > 0.5] - 1.
        delays = np.abs(angles[1:] / freqs[1:])
        #axes[2].plot(freqs, angles)
        axes[2].plot(freqs[1:], delays)
        axes[2].set_yscale('log')
        #axes[2].plot(freqs[1:], np.abs(np.remainder(np.angle(X1[1:]), 2. * np.pi) - np.remainder(np.angle(X0[1:]), 2 * np.pi)) / (2 * np.pi * freqs[1:]))
        #axes[2].plot(freqs, np.angle(X0))
        axes[2].set(xlim = [0, 60], xlabel = 'Frequency (Hz)', ylabel = 'Phase delay [sec]')
        mne.viz.tight_layout()
        #print('Writing filtered fif to disk.')
        overwrite = 'y'
        if os.path.isfile('%s/%s/%s_%s_1-40-raw.fif' % (megpath, subj, subj, expname)): #'%s/%s/%s_%s%s-raw.fif' % (megpath, subj, subj, expname, tag)
            overwrite = input('Filtered file already exists. Overwrite?\nY/y = yes, N/n = no: ')
        if overwrite.lower() == 'y':
            raw.save('%s/%s/%s_%s_1-40-raw.fif' % (megpath, subj, subj, expname), overwrite = True)

    return raw

def badsel(inst, redo = False):
    '''
    Select bad channels and bad time periods and save them to file
    Input
    -----
    inst: raw/epochs recording object (preferably filtered using rawfilt)
    redo: If True, then redo the bad channel selection. If False, ask before redoing

    Output
    ------
    raw: object file
    '''
    # Bad channel selection
    # Write bad channels to file (for easier access and just in case you want to use eelbrain)
    # Does the file already exist?
    subj = inst.info['subj']
    megpath = inst.info['megpath']
    expname = inst.info['expname']

    if type(inst) == mne.epochs.EpochsFIF:
        isepo = True
    else:
        isepo = False

    print('\nBAD CHANNELS')
    if (os.path.isfile('%s/%s/%s_%s-bad_channels.txt' % (megpath, subj, subj, expname)) or os.path.isfile('%s/%s/%s_%s-annot.fif' % (megpath, subj, subj, expname))) and redo == False:
        # Do you want to redo bad channels?
        with open('%s/%s/%s_%s-bad_channels.txt' % (megpath, subj, subj, expname)) as f:
            badchans = f.readlines()
        inst.info['bads'] = [x.strip() for x in badchans]
        # if not isepo:
        #     if os.path.isfile('%s/%s/%s_%s-annot.fif' % (megpath, subj, subj, expname)):
        #         inst.set_annotations(mne.read_annotations('%s/%s/%s_%s-annot.fif' % (megpath, subj, subj, expname)))
        overwrite = input('Bad channels file already exists. Look anyway? \n(changes will overwrite current badchan/annot files.)\nY/y = yes, N/n = no: ')
        # If so, redo and save file
        if overwrite.lower() == 'y':
            # Select bad channels, script waits for you to choose channels and close window
            if not isepo:
                fig = mne.viz.plot_raw(inst, block = True, duration = 100.0, n_channels = 32)
            else:
                inst.plot(block = True, n_epochs = 40, n_channels = 40)
            print('Overwriting bad channels file.')
            with open('%s/%s/%s_%s-bad_channels.txt' % (megpath, subj, subj, expname), 'w') as f:
                for item in inst.info['bads']:
                    f.write("%s\n" % item)
            # if not isepo:
            #     inst.annotations.save('%s/%s/SAVANT/%s_%s-annot.fif' % (megpath, subj, subj, expname), overwrite = True)

    else:
        # If file does not exist, select bad channels, script waits for you to choose channels and close window
        if not isepo:
            fig = mne.viz.plot_raw(inst, block = True, duration = 100.0, n_channels = 32)
        else:
            inst.plot(block = True, n_epochs = 40, n_channels = 40)
        print('Saving bad channels to file.')
        with open('%s/%s/%s_%s-bad_channels.txt' % (megpath, subj, subj, expname), 'w') as f:
            for item in inst.info['bads']:
                f.write("%s\n" % item)
        # if not isepo:
        #     inst.annotations.save('%s/%s/SAVANT/%s_%s-annot.fif' % (megpath, subj, subj, expname), overwrite = True)

    print('There are **%i** bad channels:' % len(inst.info['bads']))
    print('\n'.join(inst.info['bads']))
    # if not isepo:
    #     if inst.annotations.description.size == 0:
    #         annot_label = 'None'
    #     else:
    #         annot_label = inst.annotations.description[0]
    #     print('There are also %i annotations of %s segments' % (inst.annotations.onset.shape[0], annot_label))
    return inst

# ICA
# setting parameters
def make_ica(epochs, ica_method = 'fastica', n_components = 0.95, random_state = 42, curr_ica = []):
    '''
    Compute ICA solution, wait for user to reject ICA components in GUI, then asks if
    user wants to apply ICA solution. Returns ICA-cleaned data. If user does not want to,
    returns original data. Saves ICA solution + rejected components to file.

    Input
    -----
    epochs: epochs object, preferably filtered + bad chans selected
    ica_method: 'fastica' by default
    n_components: How much of the variance to explain in ICA, 95% by default
    random_state: for replication purposes. default is 42
    curr_ica: to avoid recalculation if nothing has changed, curr_ica is the previous ica solution

    Output
    ------
    done: True if user detected no issues (and does not want to redo bad channel selection + ICA)
    ica: ICA solution
    '''
    print('\nICA')
    subj = epochs.info['subj']
    megpath = epochs.info['megpath']
    expname = epochs.info['expname']

    picks = mne.pick_types(epochs.info, meg = True, stim = False, exclude = 'bads', ref_meg = False)
    # If bad channels have changed, fit new ICA, if nothing has changed, return same ICA solution
    if curr_ica == []:
        # Create ica with parameters
        ica = ICA(n_components = n_components, method = ica_method, random_state = random_state, max_iter = 300)
        print(ica)

        # Run ICA on filtered epochs data
        print('Fitting ICA...')
        thresh = 2e-12 #dict(meg = 3e-12) # Else, use this threshold
        # Note: Annotated segments are rejected by default and are not used to fit ICA on epochs
        ica.fit(inst = epochs, picks = picks, decim = None, reject={'mag': thresh})

    else: # If bad channels are the same, use previous solution
        print('Attention: Bad channels have not changed. Re-using previous ICA solution.')
        ica = curr_ica

    # Plot components
    print("INSTRUCTIONS\n============\nIf you notice any weird components, right click them to inspect them.\n")
    print("If you decide there are noisy channels that you wish to remove, close the window and type Y on the next two promopts.")
    print("If you decide there are noisy epochs that you wish to remove for ICA, choose the components with the noisy epochs, then type Y on the next prompt, and N on the following.")
    print("If you decide there are only identifiable noise sources (e.g. heartbeats), choose the noisy components and type N on the next prompt.\n")
    print("If you notice any really noisy epochs, click the components you'd like to target, then choose YES for the next question")
    ica.plot_components(inst = epochs) #, topomap_args = dict(names = ch_names))
    ica.plot_sources(inst = epochs, block = True, stop = 40)

    done = input('Did you detect any extra bad channels/epochs that you want to get rid of? Y/y = yes, N/n = no: ')
    done = False if done.lower() == 'y' else True

    print("Returning ICA object, please apply it separately")
    return done, ica


def raw2epo(raw, tmin = -0.1, tmax = 0.6, baseline = (-0.1, 0.0)):
    '''
    Convert raw object to epochs object. Also calculates trigger shifts if relevant.
    Saves events and epochs to file
    Input
    -----
    raw: raw object, preferably filtered, bad channel selected + interpolated + ICA-ed
    tmin: relative to trigger, what sample in time to take (secs)
    tmax: relative to trigger, what's the last sample to take (secs)
    baseline: tuple. baseline period to baseline correct and/or do covariance

    Output
    ------
    epochs: epochs object
    events: events object
    '''
    subj = raw.info['subj']
    megpath = raw.info['megpath']
    expname = raw.info['expname']
    print('\nEVENT DETECTION')

    # Trigger shifts per subject.
    # Here, for each subject, insert how much the triggers should be shifted in time
    # relative to the photodiode, in millesconds
    trigger_shift = {'Y0400':8,'Y0374b':8,'Y0398b':8,'Y0399b':8,'Y0119':60,'Y0208':60,'Y0366':60,'Y0371':60,'Y0372':60,'Y0395':60,'Y0396':60,'Y0387':60,'Y0312':60,'Y0321':60,'Y0366':60,'Y0367':60,'Y0368':60,'Y0369': 60,'Y0371':60,'Y0372':60,'Y0373':60,'Y0374':60,'Y0375':60,'Y0376':60,'Y0377':60,'Y0378':60,'Y0379':60,'Y0381':60,'Y0382':60,'Y0383':60,'Y0388':60,'Y0393':60,'Y0394':60}
    #subj_trigshift = trigger_shift[subj]
    subj_trigshift = 8

    # Find trigger events.
    events = mne.find_events(raw, consecutive=True, min_duration = 0.002) #stim_channel = ['STIM 014','MISC 001','MISC 002','MISC 003','MISC 004','MISC 005','MISC 006','MISC 007','MISC 008']
    #events = events[:121]
    print('Found %s events.' % events.shape[0])

    # Shift triggers forward in time
    print('Shifting event times forward in time by %d ms' % subj_trigshift)
    events[:,0] += subj_trigshift

    mne.write_events('%s/%s/%s_%s_1-40-ica-eve.fif' % (megpath, subj, subj, expname), events)

    # Define the trigger number appropriate for each event.
    # Include only those triggers that you want to keep (the epochs you want to analyze)
    #event_id = dict(CatViolRAZ=10,CatViolOD=20,CatViolUZ=30,SemViolRAZ=40,SemViolOD=50,SemViolUZ=60,GrammRAZ=70,GrammOD=80,GrammUZ=90,Filler=99)
    if expname == "SavantAra":
        event_id = dict(CatViol=20,Gramm=10,SemViol=15,Filler=99)
    else:
        event_id = dict (word_clean=1, word_noisy= 2, word_symbols= 4,letter_clean= 8,letter_noisy= 16,letter_symbol= 32)


    # Define epochs
    print('\nEPOCH CREATION')
    print('Creating epochs around selected events: (%s, %s).' % (str(tmin), str(tmax)))
    # Pick only the MEG channels
    picks = mne.pick_types(raw.info, meg = True, stim = False, exclude = [])
    epochs = mne.Epochs(raw, events, event_id, tmin, tmax, proj = True, picks = picks, baseline = baseline, preload = True, verbose = True, reject_by_annotation = False)
    epochs.save('%s/%s/%s_%s_1-40-epo.fif' % (megpath, subj, subj, expname), overwrite = True)

    return epochs, events

# EPOCH REJECTION
def make_rej(epochs, show = True, save = False):
    '''
    Reject epochs that are too noisy. Threshold is set to 3e-12 in NY, 2e-12 in AD.
    Also logs which epochs were dropped.
    Input
    -----
    epochs: epochs object
    tot_trials: total number of epochs expected

    Output
    ------
    epochs: epochs object with the offensive epochs dropped
    '''
    # Rejecting epochs
    subj = epochs.info['subj']
    megpath = epochs.info['megpath']
    expname = epochs.info['expname']
    tot_trials = len(epochs)

    print('\nEPOCH REJECTION:')
    thresh = {'meg': 2e-12} # Else, use this threshold

    if show == False:
        save = True

    epochs_ind = np.linspace(0, len(epochs.drop_log)-1, len(epochs.drop_log), dtype = int)
    dropped_ind = np.where(np.asarray([0 if ep == () else 1 for ep in epochs.drop_log]))[0]
    corrected_ind = np.setdiff1d(epochs_ind, dropped_ind)
    #print('If numbers appear below, they would correspond to epochs in which data exceed the threshold of %.0E -- you should select those in the GUI for dropping:' % (thresh['meg']))
    rejind = [ind for ind, epo in enumerate(epochs) if np.absolute(epo).max() > thresh['meg']]
    #rejind = [ind for ind, epo in enumerate(epochs) if np.absolute(epo[:, tstart_ind: tend_ind]).max() > thresh['meg'] or np.absolute(epo[:, 0:200]).max() > thresh['meg']]
    if rejind == []:
        print('No epochs exceed threshold of %.0E' % thresh['meg'])
    else:
        print('Some absolute values in these %d epochs exceeded the threshold of %.0E -- select them in the GUI to drop them:' % (len(rejind), thresh['meg']))
        #print([ind+1 for ind in rejind]) # +1 so the indices start from 1 and match the indices shown in the plot
        print([ind for ind in rejind]) # +1 so the indices start from 1 and match the indices shown in the plot
        notrejind = [ind for ind in range(0,tot_trials) if ind not in rejind]
        epochs_rej = epochs.copy().drop(indices = notrejind)
        epochs_rej.save('%s/%s/%s_%s_1-40-ica-drop-epo.fif' % (megpath, subj, subj, expname), overwrite = True)

    if epochs.info['kit_system_id'] == 35: # If NYU MEG
        chan_num = 157
    else:
        chan_num = 208
    potential_bads = np.zeros(chan_num)
    for ind in rejind:
        epo = epochs[ind].get_data()
        above_thresh = np.unique(np.where(epo > thresh['meg'])[1])
        np.add.at(potential_bads, above_thresh, np.ones(above_thresh.shape))

    print('Here are some potentially bad channels, and in how many epochs they show up:')
    print('Channel\t# epochs')
    top_potential_bads = potential_bads.argsort()[-10:][::-1]
    for bad in top_potential_bads:
        print('MEG %i\t%d' % (bad+1, potential_bads[bad]))

    if show == True:
        print('Click on epoch data to reject epochs')
        epochs.plot(block = True, n_epochs = 40, n_channels = 40)
    else:
        epochs = epochs.drop(indices = rejind)
    if save == True:
        # Save file with only the non-rejected epochs
        print('Writing epochs to file')
        epochs.save('%s/%s/%s_%s_1-40-ica-rej-epo.fif' % (megpath, subj, subj, expname), overwrite = True)
        with open("%s/%s/%s_%s-rejected_epochs.txt" % (megpath, subj, subj, expname), "w") as text_file:
            text_file.write("%s: %i" % (subj, len(rejind)))
            text_file.write("\nEpochs removed (first epoch = 0): %s" % (str([ind for ind in rejind])))
            #text_file.write("\nEpochs removed (first epoch = 1): %s" % (str([ind+1 for ind in rejind])))

    return epochs
