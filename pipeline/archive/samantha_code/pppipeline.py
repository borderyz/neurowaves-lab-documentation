# Suhail Matar, March 2022
# MNE Preprocessing Pipeline code, for SAVANT
# Using MNE 0.23.4
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

exppath = '/home/scw9/wray_workspace/Savant_Arabic/doubletime/savant_main' # ENTER PATH TO EXPERIMENT FODLER HERE (folder containing meg and mri folders)
megpath = exppath + '/meg'
exppath = '/home/scw9/wray_workspace/Savant_Arabic/doubletime/savant_main/mri'
#mripath = exppath + '/mri'
#os.chdir(exppath)
expname = 'SavantAra' # ENTER EXPERIMENT CODENAME HERE (e.g., SAVANTARA or whatever convention we follow)
# pphelpers has all the functions that I use for preprocessing
from pphelpers import *

# Get a list of all the subjects
#subjlist = ['Y0398b','Y0399b']
#'Y0400'
subjlist = ['Y0400']
#'Y0369','Y0395','Y0396'
#'Y0371','Y0373','Y0374','Y0378','Y0379','Y0381','Y0382','Y0387','Y0393'-needs stcs?,'Y0395','Y0396','Y0400']

#subjlist = ['Y0208','Y0312','Y0321','Y0367','Y0371','Y0373','Y0374','Y0378','Y0379','Y0381','Y0382','Y0387','Y0393']
#,'Y0208','Y0312','Y0321','Y0367','Y0368','Y0369','Y0371','Y0373','Y0374','Y0378','Y0379','Y0381','Y0382','Y0387','Y0393','Y0395','Y0396']
#subj = 'R0006' ##IN CASE YOU'RE RUNNING MORE SUBJECTS AT ONCE, DON'T RUN THIS

####################################################
### PART 1: Load, filter, bad channels, epoching ###
####################################################


# Go through all the subjects, load raw file, filter it, make epochs, and save
tmin = -0.1  # INSERT TIME TO INCLUDE BEFORE TRIGGER (baseline) in SECONDS
tmax = 0.6  # INSERT EXTENT OF EPOCH, in SECONDS


for subj in subjlist: ###AVOID THIS LINE IF YOU'RE RUNNING ONLY ONE SUBJECT
    print('\n\nFiltering and epoching data from subject %s' % subj)
    #####
    # If subject has already been processed, raise warning (you can delete this part if it annoys you)
    if os.path.isfile('%s/%s/%s_%s_1-40-ica-rej-epo.fif' % (megpath, subj, subj, expname)):
        print("Subject %s's data appears to have already been preprocessed." % subj)
        overwrite = input("\nWould you like to abort? Y/y = yes, N/n = no: ")
        if overwrite.lower() == 'y':
            raise ValueError("Aborted -- check files of %s and re-run if you would like to redo preprocessing." % subj)
    #####
    # Load raw data
    raw = rawload(megpath, subj, expname)

    ## max balls ## #use a maxwell filter to align head positions
    #raw = rawfilt(raw, l_freq = 0.1, h_freq = 40.) # REPLACE None with filtering values wanted. Can be None
    #raw = badsel(raw, redo = False)
    #original_head_dev_t = raw.info["dev_head_t"]
    #raw_sss = mne.preprocessing.maxwell_filter(raw, coord_frame='head', destination=original_head_dev_t,ignore_ref=True)
    #raw = raw_sss
    #epochs, events = raw2epo(raw, tmin = tmin, tmax = tmax, baseline = None)

    # Filter data. This will plot an example of what the data before and after looks like from one channel
    raw = rawfilt(raw, l_freq = 0.1, h_freq = 40.) # REPLACE None with filtering values wanted. Can be None #max#
    # Select bad channels. If there is a file called SUBJID_expname-bad_channels.txt , it will load those channels
    raw = badsel(raw, redo = False) #max#
    # Make epochs between tmin and tmax, but without applying baseline

    epochs, events = raw2epo(raw, tmin = tmin, tmax = tmax, baseline = None) #max#
    del(raw)
    del(epochs)
    del(events)


####################################################
################## PART 2: ICA #####################
####################################################

# For every subject

for subj in subjlist: #DON'T RUN THIS LINE IF YOU ARE RUNNING ONLY ONE SUBJECT
    print('\n\nNow working on ICA solution for subject %s...' % subj)
    # Read epochs file and add the relevant info
    epochs = mne.read_epochs('%s/%s/%s_%s_1-40-epo.fif' % (megpath, subj, subj, expname))
    #tarkepochs = mne.read_epochs('/home/scw9/wray_workspace/Savant_Arabic/new_ica/savant_tark/meg/%s/%s_TarkAra_1-40-epo.fif' % (subj, subj)) #for calculating co
    epochs.info['subj'] = subj
    epochs.info['megpath'] = megpath
    epochs.info['expname'] = expname
    print('These are the bad channels saved:')
    print(epochs.info['bads'])
    # Make a copy of the epochs object, just for the sake of ICA
    epochs4ica = epochs.copy()
    num_epochs = len(epochs4ica) # How many epochs do we have?
    old_badchans = [] # Leave this blank

    # Initialize some parameters for the loop
    done = False
    curr_ica = []
    noisy_inds = []
    # Calculate and re-calculate ICA solution until there are no weird components

    while done == False:

        # Calculate ICA solution, taking into account any new "dropped" epochs and channels
        done, curr_ica = make_ica(epochs4ica, curr_ica = curr_ica, n_components = 0.95)
        # If you're done, then save the ICA solutiona and apply it
        if done == True:
            print('Applying ICA and saving files...')
            epochs.info['bads'] = epochs4ica.info.copy()['bads']
            epochs = curr_ica.apply(epochs, exclude = curr_ica.exclude)
            curr_ica.save('%s/%s/%s_%s_sol-ica.fif' % (megpath, subj, subj, expname)) # max #
            # max # curr_ica.save('%s/%s/%s_%s_sol-ica.fif' % (megpath, subj, subj, expname), overwrite = True)
            curr_ica.get_sources(inst = epochs4ica).save('%s/%s/%s_%s_1-40-ica-sources-epo.fif' % (megpath, subj, subj, expname), overwrite = True)
            epochs.save('%s/%s/%s_%s_1-40-ica-epo.fif' % (megpath, subj, subj, expname), overwrite = True)
            del(epochs4ica)
        # If you're not done (you want to exclude bad channels or epochs)
        else:
            # Get which components had noisy epochs
            noisy_comps = curr_ica.exclude
            sources = curr_ica.get_sources(inst = epochs4ica)

            # For each noisy component, find the noisiest epochs
            # This is based on those epochs whose variance is an outlier compared to the rest of the epochs
            # The indices of offensive epochs are stored in a list called noisy_inds
            noisy_inds = []
            for ind in noisy_comps:
                data_max = np.max(np.abs(sources.get_data()[:, ind, :]), axis = 1)
                #data_max = stats.zscore(data_max)
                quants = np.quantile(data_max, q = [0.25, 0.75])
                upper_end = quants[1] + 3.0 * (quants[1] - quants[0])
                noisy_inds_quants = list(np.where(data_max > upper_end)[0])
                epoch_var = np.var(sources.get_data()[:, ind, :], axis = 1)
                noisy_inds_var = list((-epoch_var).argsort()[:int(0.05 * len(epochs4ica))])

                noisy_inds_add = (noisy_inds_quants if len(noisy_inds_quants) < len(noisy_inds_var) else noisy_inds_var)
                noisy_inds = noisy_inds + noisy_inds_add

            # This is the final set of noisy indices
            noisy_inds = np.unique(np.asarray(noisy_inds))
            print("There are %i epochs with outlier ICA source values:" % len(noisy_inds))
            print(noisy_inds)

            # If you want to select more bad channels, the ICA solution is re-computed afterwards
            redobads = input("\nDo you need to select more bad channels? Y/y = Yes, N/n = No: ")
            if redobads.lower() == 'y':
                old_badchans = epochs4ica.info.copy()['bads']
                epochs4ica = badsel(epochs4ica, redo = True)
                new_badchans = epochs4ica.info.copy()['bads']
                print(epochs4ica.info['bads'])
                new_ica# If bad channels have changed (you selected new ones, say)
                if set(old_badchans) != set(epochs4ica.info['bads']):
                    # Reset ICA solution
                    curr_ica = []
                    # Reset the epochs copy (restoring any dropped epochs)
                    epochs4ica = epochs.copy()
                    epochs4ica.info['bads'] = new_badchans
                    num_epochs = len(epochs4ica)
                    print('Resetting ICA')
                continue
                #old_badchans1 = copy.deepcopy(raw1.info['bads'])[:]

            # If you want to drop epochs, it is bes%st to do it automatically (based on the variance calculation above)
            # But, if there are elusive epochs that can't be removed, you can do it manually
            epochdrop = input("\nWould you like to Automatically (A/a) or Maunally (M/m) or Not (N/n) drop any epochs before ICA? ")
            if epochdrop.lower() == 'm':
                # If manually, just click on offensive epochs and close plot when you're done
                epochs4ica.plot(block = True, n_epochs = 40, n_channels = 40)
            if epochdrop.lower() == 'a':
                epochs4ica.drop(indices = noisy_inds)
            if epochdrop.lower() == 'n':
                noisy_inds = []
            # If the number of epochs has changed, calculate how many epochs you've dropped so far
            # Reset ICA solution
            if len(epochs4ica) != num_epochs:
                num_epochs = len(epochs4ica)
                print('**** So far dropped %i epochs for ICA. ****' % len([ind for ind in range(0, len(epochs)) if epochs4ica.drop_log[ind] == ('USER',)]))
                print('Number of epochs changed; resetting ICA solution...')
                curr_ica = []


###############################################################
### PART 3: Interpolate bads, Apply baseline, reject epochs ###
###############################################################

# Once you're past this stage, you should have a clean ICA solution saved and a clean epochs file

for subj in subjlist: ##DON'T RUN THIS LINE IF YOU ARE RUNNING ONLY ONE SUBJECT
    epochs = mne.read_epochs('%s/%s/%s_%s_1-40-ica-epo.fif' % (megpath, subj, subj, expname))
    epochs = epochs.crop(tmin=tmin,tmax=tmax)
    #tarkepochs = mne.read_epochs('/home/scw9/wray_workspace/Savant_Arabic/new_ica/savant_tark/meg/%s/%s_TarkAra_1-40-epo.fif' % (subj, subj)) #for calculating co
    #tarkepochs = tarkepochs.crop(tmin=tmin, tmax=tmax)
    ##combining the epochs
    #tarkepochs.info['dev_head_t'] = epochs.info['dev_head_t']
    '''
    epochs.info['dev_head_t'] = tarkepochs.info['dev_head_t']
    if epochs.info['bads'] == tarkepochs.info['bads']:
        print("Channel match between tark and main")
    else:
        if len(epochs.info['bads']) > len(tarkepochs.info['bads']):
            tarkepochs.info['bads'] = epochs.info['bads']
        else:
            epochs.info['bads'] = tarkepochs.info['bads']
    #epochs.info['bads'] = tarkepochs.info['bads']
    allepochs = mne.concatenate_epochs([epochs,tarkepochs])
    '''



    epochs.info['subj'] = subj
    epochs.info['megpath'] = megpath
    epochs.info['expname'] = expname


    # Interpolate bads and manually reset bads -- we're done with them
    print('\nInterpolating bad channels...')
    epochs.interpolate_bads(reset_bads = True, mode = 'accurate')
    epochs.info['bads'] = []
    '''
    allepochs.interpolate_bads(reset_bads = True, mode = 'accurate')
    allepochs.info['bads'] = []

    tarkepochs.interpolate_bads(reset_bads = True, mode = 'accurate')
    tarkepochs.info['bads'] = []
    '''

    # APPLY BASELINE
    baseline = (tmin, 0)# SET BASELINE NEEDED. Usually it's (tmin, 0)
    epochs = epochs.apply_baseline(baseline = baseline)
    #allepochs = allepochs.apply_baseline(baseline =baseline)
    #tarkepochs = tarkepochs.apply_baseline(baseline =baseline)

    # Reject epochs exceeding absolute threshold.
    num_epochs = len(epochs)
    epochs = make_rej(epochs, show = False, save = True)
    print('Total number of epochs: %i. Number of epochs removed: %i' % (len(epochs), num_epochs - len(epochs)))


    # Calculate and plot evoked, save to file
    note = '_sanity'
    evoked = epochs.average()
    fig_evo = evoked.plot_joint()
    fname = '%s/%s/%s_%s_butterfly%s.svg' % (megpath, subj, subj, expname, note)
    fig_evo.savefig(fname)
    fname = '%s/%s/%s_%s_butterfly%s.png' % (megpath, subj, subj, expname, note)
    fig_evo.savefig(fname, dpi = 200)

    # Compute noise covariance matrix based on baseline
    noise_cov = mne.compute_covariance(epochs, tmax = 0.0, method = ['shrunk', 'diagonal_fixed', 'empirical'])#method = ['shrunk', 'diagonal_fixed', 'empirical'] 'auto') #replace method with auto to have additional option
    #noise_cov = mne.compute_covariance(tarkepochs, tmax = 0.0, method = ['shrunk', 'diagonal_fixed', 'empirical'])#method = 'auto')
    mne.write_cov('%s/%s/%s_%s-cov%s.fif' % (megpath, subj, subj, expname, note), noise_cov)

    # Finally, plot some quality assurance plots relating to the covariance matrix
    #remove "from_tark" in filenames here when not calculating covariance from tark exp
    fig_covmat, fig_covnoise = noise_cov.plot(epochs.info, proj = True)
    fname = '%s/%s/%s_%s_covmat%s.svg' % (megpath, subj, subj, expname, note)
    fig_covmat.savefig(fname)
    fname = '%s/%s/%s_%s_covmat%s.png' % (megpath, subj, subj, expname, note)
    fig_covmat.savefig(fname, dpi = 200)
    fname = '%s/%s/%s_%s_covnoise%s.svg' % (megpath, subj, subj, expname, note)
    fig_covnoise.savefig(fname)
    fname = '%s/%s/%s_%s_covnoise%s.png' % (megpath, subj, subj, expname, note)
    fig_covnoise.savefig(fname, dpi = 200)

    fig_white = evoked.plot_white(noise_cov, time_unit = 's')
    fname = '%s/%s/%s_%s_whitened%s.svg' % (megpath, subj, subj, expname, note)
    fig_white.savefig(fname)
    fname = '%s/%s/%s_%s_whitened%s.png' % (megpath, subj, subj, expname, note)
    fig_white.savefig(fname, dpi = 200)


################################################################################
# By the time you get here, you should have an epochs object with bad epochs   #
# dropped. You should also have all the necessary files saved, including the   #
# one that ends with -ica-rej-epo.fif                                          #
################################################################################
