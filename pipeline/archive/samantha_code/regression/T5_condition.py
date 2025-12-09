import wx
#import os #for doing brain stuff
####os.environ['ETS_TOOLKIT'] = 'wx' #for doing brain plotting stuff

import csv
import itertools
import mne, eelbrain, os, glob, pickle
import numpy as np
import pandas as pd
from os.path import join
import os.path as op
from scipy.stats import zscore
from eelbrain import *
# import statsmodels.formula.api as smf
#from statsmodels.formula.api import ols
#from numpy import npy_float64
from time import sleep
import matplotlib.pyplot as plt


#import mne
#import eelbrain
#from surfer import Brain

mne.set_log_level(verbose='WARNING')
eelbrain.configure(frame=False)

#=========Edit here=========#

SNR = 2 # 3 for ANOVAs, 2 for regressions
fixed = True # False for orientation free (=unsigned), True for fixed orientation (=signed)


from main import *
#del analyses
analyses = tark_analyses
sampleSize = 20

def redirect_stdout():
    # Redirecting stdout
    sys.stdout.flush() # <--- important when redirecting to files
    newstdout = os.dup(1)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 1)
    os.close(devnull)
    sys.stdout = os.fdopen(newstdout, 'w')

subjects = ['Y0387','Y0312']
################################################################################################,'Y0321','Y0366','Y0367','Y0368','Y0369','Y0371','Y0372','Y0373','Y0374','Y0375','Y0377','Y0378','Y0379','Y0381','Y0382','Y0383','Y0388','Y0393']
hemi = 'both'
hemiShort = 'whole'

if True:
    ds = Dataset()
    coefficientDict = dict()

    #print("Computing regressions in %s from %s to %s'" %(regionName, str(time[0]), str(time[1])))

    # Lists containing the subject factor and the beta values
    subjF = []
    betas = []

    all_subjs =[]
    all_stcs = []
    all_noiseF = []
    all_letterF = []
    all_letterWordF = []
    all_wordF = []
    '''
    if 'Noise' in analysis[0]:
        subjects = subjects_noise
    elif 'Word' in analysis[0]:
        subjects = subjects_word
    else:
        subjects = subjects_letter
    '''
    for subj in subjects:
        all_subjs.append(subj)
        if True:
        #regResFileName = op.join('new_ica/savant_tark/','Regressions/',subj,'Tark',hemi,regionName,str(time[0])+'-'+str(time[1]),formula+'.pickle')
        #if os.path.exists(regResFileName):
            #print('Regressions already done! Loading regression dSPM ~ 1 + %s for subject %s in %s from %s to %s' %(formula,subj,regionName,str(time[0]),str(time[1])))
            #regResF = open(regResFileName, 'rb')
            #regRes = pickle.load(regResF)
            #regResF.close()
        #else:
            #print('Computing regression dSPM ~ 1 + %s for subject %s in %s from %s to %s' %(formula,subj,regionName,str(time[0]),str(time[1])))

            ds_subj = Dataset()
            stcs = []

            noiseF = []
            letterF = []
            letterWordF = []
            wordF = []

            pos = []

            if True: # WE DON'T NEED LOGS FOR THIS ANALYSIS!!!!
#            if not os.path.exists(op.join(ROOT,'Logs/%s-Savant_Ara.log' %subj)):
#                print('No log file for %s :(' %subj)
#            else:
#                print('Found log file for %s' %subj)
#
#                logFile = open(op.join('Logs','%s-Savant_Ara.log' %subj))
                for fileName in os.listdir(os.path.join('stc','savant_tark',subj)):
                    #myfile.write(str(fileName)+'\n')
                    includeTrial = True
                    stc_append = True
                    if (hemi == 'whole' or fileName.endswith(hemiShort+'.stc') or hemi == "both") and fileName.endswith('.stc'):
                        splitName = fileName.split('_')
                        stcPosNo = int(splitName[1])
                        '''
                        if includeNoise == False and 'noisy' in fileName:
                            includeTrial = False

                        if includeSymbols == False and 'symbols' in fileName:
                            includeTrial = False

                        if includeWords == False and 'word' in fileName:
                            includeTrial = False
                        '''
                        if includeTrial:

                            pos.append(stcPosNo)

                            if 'noisy' in fileName:
                                #stc_append = False
                                noiseF.append('noise')
                                all_noiseF.append('noise')
                                #print("found noisy")
                            else:
                                #print("found clean")
                                noiseF.append('clean')
                                all_noiseF.append('clean')
                            #'''
                            if 'symbol' in fileName:
                                letterWordF.append('nonLetterWord')
                                all_letterWordF.append('nonLetterWord')
                                if 'letter' in fileName:
                                    letterF.append('nonLetter')
                                    #wordF.append('skip')
                                    all_letterF.append('nonLetter')
                                    #all_wordF.append('skip')
                                elif 'word' in fileName:
                                    #print("found word")
                                    #print(fileName)
                                    #letterF.append('skip')
                                    #all_letterF.append('skip')
                                    wordF.append('nonWord')
                                    all_wordF.append('nonWord')
                            else:
                                letterWordF.append('letterWord')
                                all_letterWordF.append('letterWord')
                                if 'letter' in fileName:
                                    letterF.append('letter')
                                    all_letterF.append('letter')
                                    #wordF.append('skip')
                                    #all_wordF.append('skip')
                                elif 'word' in fileName:
                                    #letterF.append('skip')
                                    #all_letterF.append('skip')
                                    wordF.append('word')
                                    all_wordF.append('word')
                            if stc_append:
                                tmp = mne.read_source_estimate('stc/savant_tark/%s/%s' %(subj,fileName),subject=subj)
                                stcs.append(tmp)
                                all_stcs.append(tmp)
                            #all_subjs.append(subj)

clustersToPlot = []
output = os.path.join('new_ica/savant_tark', 'Plots/Group/%s_Regressions_n%s/' %(date,str(sampleSize)))
exp = "savant_tark/"

subjects_dir = ('new_ica/' + exp + 'mri')
parc = 'aparc'

for fileName in os.listdir(op.join(output, 'clusters')):

    if fileName.endswith('pickle'):
        clusFile = open(op.join(output, 'clusters', fileName), 'rb')
        clus = pickle.load(clusFile)
        clusFile.close()
        clustersToPlot.append(clus)

for clus in clustersToPlot:

    res_fname = clus[0]
    res_table = clus[1]
    cluster = clus[2]
    tstart = clus[3]
    tstop = clus[4]
    coef = clus[5]
    regionName = clus[6]
    timecourse = clus[7]
    hemi = clus[8]
    region = clus[9]
    analysisType = clus[10]
    cluster_nb = clus[11]
    ds = clus[12]
    p_start = clus[13]
    p_stop = clus[14]
    clusP = clus[15]


    eelbrain.load.update_subjects_dir(cluster, subjects_dir=subjects_dir, depth = -1)
    eelbrain.load.update_subjects_dir(ds, subjects_dir=subjects_dir, depth = -1)

    multiClusters = {}

newds = eelbrain.Dataset()
newds['stc'] = load.fiff.stc_ndvar(stcs, subject='fsaverage', src='ico-4', subjects_dir=subjects_dir, parc=parc)
#newds['word_or_symbol'] = Factor(all_wordF)
newds['letter_or_symbol'] = Factor(all_letterF)
#newds['noise_or_clean'] = Factor(all_noiseF)
newds['letterWord_or_symbol'] = Factor(all_letterWordF)
#newds['Subject'] = eelbrain.Factor(all_subjs,random=True)

src_region = newds['stc'].sub(region)
newds['stc']=src_region

if 'letter' in analysisType:
    if 'Word' in analysisType:
        myCondition = 'letterWord_or_symbol'
    else:
        myCondition = 'letter_or_symbol'
elif 'word' in analysisType:
    myCondition = 'word_or_symbol'
else:
    myCondition = 'noise_or_clean'

new_timecourse = newds['stc'].mean('source')

activation = plot.UTSStat(new_timecourse,myCondition,match='Subject',
    ds = newds,
    error='sem',
    error_alpha = 0.10,
    legend = None,
    xlabel = 'Time (ms)',
    ylabel = 'Predicted dSPM',
#    xlim = (epoch_tmin, epoch_tmax),
    show = False,
    title = str('Activity at ' + str(regionName))
            )
activation.add_vspan(xmin=tstart, xmax=tstop, color='lightgrey', zorder=-50, alpha=0.4)
activation._axes[0].set_xticks([0,tstart,tstop])

for j in range(0,len(activation._axes[0].lines)):
    activation._axes[0].lines[j].set_lw(w=0.75)

activation._axes[0].axvline(x=0.0,color="black",linestyle="solid")

activation._axes[0].grid()

interceptYlim = activation.get_ylim()

        #coef = coef.replace('/','')
        #coef = coef.replace(':','')

graphName = op.join(output, 'graphs','%s_%s_cluster%s_%s-%s_%s-%s_%s_%s_p%s_new.png' %(hemi,regionName,cluster_nb,str(tstart),str(tstop),str(p_start),str(p_stop),analysisType,coef,str(clusP)))

activation.save(graphName, dpi=300)
sleep(15)
try:
    activation.close()
except:
    print("Can't close activation plot")
