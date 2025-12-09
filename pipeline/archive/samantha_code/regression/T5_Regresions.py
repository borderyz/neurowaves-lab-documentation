## RUN THIS *ipython* IN THE EELBRAIN ENVIRONMENT


# D. A. Chacón (2020)

# Based off of code from Julien Dirani
# ---File structure----
# ROOT>
#     MRI>
#         subjs
#     MEG>
#         subjs
#     STC>

# epochs rejection based on log files not included


# ----------File structure-----------#
# ROOT>
#     MRI>
#         subjs
#     MEG>
#         subjs
#     STC>
#import wx
#import pyface.qt
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

subjects = ['Y0119','Y0208','Y0321','Y0366','Y0367','Y0368','Y0369','Y0371','Y0372','Y0373','Y0374','Y0378','Y0379','Y0381','Y0382','Y0387','Y0393','Y0395','Y0396']
#subjects = [,'Y0371']

#'Y0368'
#subjects_noise = ['Y0312','Y0321','Y0366','Y0368','Y0373','Y0374','Y0375','Y0377']
#subjects_letter = ['Y0312','Y0321','Y0373','Y0369','Y0377','Y0369']
#subjects_word = ['Y0377','Y0369','Y0371','Y0378']
#,,,
#,
#sampleSize = len(subjects)
#367,369,371 is a noise:noise
#'Y0378'.Y0375,Y0374,Y0368,Y0366 is a letter:letter

output = os.path.join('new_ica/savant_tark', 'Plots/Group/%s_Regressions_n%s/' %(date,str(sampleSize)))

if not os.path.exists(output):
    os.makedirs(output)
    os.makedirs(op.join(output,'clusters'))
    os.makedirs(op.join(output,'graphs'))
    os.makedirs(op.join(output,'csv'))
    os.makedirs(op.join(output,'results'))

#os.chdir(ROOT) #setting current dir
exp = "savant_tark/"

subjects_dir = ('new_ica/' + exp + 'mri')
myfile = open('my_file.txt', 'w')

for analysis in analyses:

#('M350 Analysis', (0.2, 0.5), ['LOBE.TEMPROAL-lh'], 'left temporal lobe', 'PALS_B12_Lobes', 'left', 'stemFrequency + wholeWordFreq', True, True, False),
    analysisType = analysis[0]
    time = analysis[1]
    sources = analysis[2]
    regionName = analysis[3]
    parc = analysis[4]
    hemi = analysis[5]
    formula = analysis[6]
    includeNoise = analysis[7]
    includeSymbols = analysis[8]
    includeWords = analysis[9]

    print('Conducting analysis %s' %analysisType)

    if hemi == "left":
        hemiShort = 'lh'
    elif hemi == "right":
        hemiShort = 'rh'
    elif hemi == "whole" or hemi == "both":
        hemiShort = 'whole'

    if parc == 'aparc_sub':
        mne.datasets.fetch_aparc_sub_parcellation(subjects_dir=subjects_dir,verbose=True)


    # The dataset and the coefficient dictionary
    ds = Dataset()
    coefficientDict = dict()

    print("Computing regressions in %s from %s to %s'" %(regionName, str(time[0]), str(time[1])))

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
        regResFileName = op.join('new_ica/savant_tark/','Regressions/',subj,'Tark',hemi,regionName,str(time[0])+'-'+str(time[1]),formula+'.pickle')
        if os.path.exists(regResFileName):
            print('Regressions already done! Loading regression dSPM ~ 1 + %s for subject %s in %s from %s to %s' %(formula,subj,regionName,str(time[0]),str(time[1])))
            regResF = open(regResFileName, 'rb')
            regRes = pickle.load(regResF)
            regResF.close()
        else:
            print('Computing regression dSPM ~ 1 + %s for subject %s in %s from %s to %s' %(formula,subj,regionName,str(time[0]),str(time[1])))

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
                    if (hemi == 'whole' or fileName.endswith(hemiShort+'.stc') or hemi == "both") and fileName.endswith('.stc'):
                        splitName = fileName.split('_')
                        stcPosNo = int(splitName[1])

                        if includeNoise == False and 'noisy' in fileName:
                            includeTrial = False

                        if includeSymbols == False and 'symbols' in fileName:
                            includeTrial = False

                        if includeWords == False and 'word' in fileName:
                            includeTrial = False

                        if includeTrial:

                            pos.append(stcPosNo)

                            if 'noisy' in fileName:
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
                                    wordF.append('skip')
                                    all_letterF.append('nonLetter')
                                    all_wordF.append('skip')
                                elif 'word' in fileName:
                                    #print("found word")
                                    #print(fileName)
                                    letterF.append('skip')
                                    all_letterF.append('skip')
                                    wordF.append('nonWord')
                                    all_wordF.append('nonWord')
                            else:
                                letterWordF.append('letterWord')
                                all_letterWordF.append('letterWord')
                                if 'letter' in fileName:
                                    letterF.append('letter')
                                    all_letterF.append('letter')
                                    wordF.append('skip')
                                    all_wordF.append('word')
                                elif 'word' in fileName:
                                    letterF.append('skip')
                                    all_letterF.append('skip')
                                    wordF.append('word')
                                    all_wordF.append('word')
                                #else:
                                #    print(fileName)
                                #    letterF.append('nonLetter')
                            '''
                            #From Suhail's original code:

                            if 'symbol' in fileName:
                                letterF.append('nonLetter')
                                letterWordF.append('nonLetterWord')
                            else:
                                letterWordF.append('letterWord')
                                if 'letter' in fileName:
                                    letterF.append('letter')
                                else:
                                    letterF.append('nonLetter')
                            '''

                            tmp = mne.read_source_estimate('stc/savant_tark/%s/%s' %(subj,fileName),subject=subj)
                            stcs.append(tmp)
                            all_stcs.append(tmp)


            #print(wordF)
            #print(letterWordF)
            #print(len(nonLetterWordF))
            '''temp_11thhour

            print('Loading fiff...')
            ds_subj['stcs'] = load.fiff.stc_ndvar(stcs, subject='fsaverage', src='ico-4', subjects_dir=subjects_dir, parc=parc)
            eelbrain.load.update_subjects_dir(ds_subj, subjects_dir=subjects_dir, depth=-1)
            print('Done.')

            print('Subsetting the regions...')
            stc = ds_subj['stcs']
            stc_region = stc.sub(source=sources)
            ds_subj['stcs'] = stc_region
            print('Done.')

            print('Assigning factors to the DS...')


            ds_subj['letter'] = Factor(letterF,labels={'nonLetter':'nonLetter','letter':'letter'})
            ds_subj['letterWord'] = Factor(letterWordF,labels={'nonLetterWord':'nonLetterWord','letterWord':'letterWord'})
            ds_subj['word'] = Factor(wordF,labels={'nonWord':'nonWord','word':'word'})
            ds_subj['noise'] = Factor(noiseF,labels={'clean':'clean','noise':'noise'})
            ds_subj['pos'] = Var(pos)



            nd = ds_subj['stcs'].x
            nd = np.array(ds_subj['stcs'].x, dtype='float64')
            ds_subj['stcs'].x = nd
            #print(ds_subj['noise'])
            #nd = ds_subj['stcs']
            #nd = np.array(ds_subj['stcs'], dtype='float64')
            #ds_subj['stcs'] = nd
            print('Done.')

            print('Beginning regression...')

            #regRes = testnd.LM(ds_subj['stcs'],model=formula,ds=ds_subj)
            regRes = testnd.LM(ds_subj['stcs'],model=formula,ds=ds_subj,sub=None)
            print(regRes.column_names)

            if not os.path.exists(op.join('new_ica/savant_tark/','Regressions',subj,'Tark',hemi,regionName,str(time[0])+'-'+str(time[1]))):
                os.makedirs(op.join('new_ica/savant_tark/','Regressions',subj,'Tark',hemi,regionName,str(time[0])+'-'+str(time[1])))

            pickle.dump(regRes, open(regResFileName, 'wb'),protocol=4)
            #all_stcs.append(stcs)
            del ds_subj, stcs, tmp

        for coef in regRes.column_names:
            #print(regRes.column_names)
            if coef not in coefficientDict:
                coefficientDict[coef] = []
            coefficientDict[coef].append(regRes.coefficient(coef))

        subjF.append(subj)

    for coef in coefficientDict.keys():
        #print(coefficientDict[coef])
        #myfile.write(str(coef) + ' ' + str(subj))

#                    stc_region = stc.sub(source=sources)

        ds = Dataset()
        ds['beta'] = coefficientDict[coef]

#                    for stc in ds['beta']:
#                        stc_region = stc[0].sub(source=sources)
#                        ds['beta'][stc] = stc_region

        ds['subject'] = Factor(subjF, random=True)
        eelbrain.load.update_subjects_dir(ds, subjects_dir=subjects_dir, depth = -1)

        for t in [-1, 1]:

            res_fname = op.join(output, coef, 'results', hemi + '_' + regionName + '_' + str(t) + '_' + str(time[0]) + '-' + str(time[1]) + '_' + analysisType + '_' + coef + '_spatiotemporal.pickle')
            res_table = op.join(output, coef, 'table', hemi + '_' + regionName + '_' + str(t) + '_' + str(time[0]) + '-' + str(time[1]) + '_' + analysisType + '_' + coef + '_spatiotemporal_results_table.txt')

            if os.path.exists(res_fname):
                print('Already exists for ' + coef + ' in ' + regionName)

            elif coef == 'intercept':
                print('Ignoring intercept')
                if not os.path.exists(op.join(output,coef)):
                    os.makedirs(op.join(output,coef,'results'))
                    os.makedirs(op.join(output,coef,'table'))
                pickle.dump(ds, open(res_fname, 'wb'),protocol=4)

            elif 'condition' in coef or 'prefix' in coef or coef == 'condition x prefix':
                if not os.path.exists(op.join(output,coef)):
                    os.makedirs(op.join(output,coef,'results'))
                    os.makedirs(op.join(output,coef,'table'))
                ds_fname = op.join(output, coef, 'results', hemi + '_' + regionName + '_' + str(t) + '_' + str(time[0]) + '-' + str(time[1]) + '_' + analysisType + '_' + coef + '_betas.pickle')
                pickle.dump(ds, open(ds_fname, 'wb'),protocol=4)

            if coef != "intercept" and not os.path.exists(res_fname):
                if not os.path.exists(op.join(output,coef,'results')):
                    os.makedirs(op.join(output,coef,'results'))
                    os.makedirs(op.join(output,coef,'table'))

            # n = coefficient number
            # j = subject number

                res = testnd.ttest_1samp('beta', ds=ds,
                tstart=time[0], tstop=time[1],
                pmin = pmin,
                tail = t,
                force_permutation=True,
                mintime = mintime, minsource = minsource,
                #tfce = True,
                #eelbrain.load.update_subjects_dir(ds_subj, subjects_dir=subjects_dir, depth=-1),
                samples = samples
                #match='subject'
                )

                pickle.dump(res, open(res_fname, 'wb'),protocol=4)

                f = open(res_table, 'w')
                f.write(str(res.clusters))
                f.close()

                # plot clusters that are significant at alpha level 0.10
                plot_pmin = 0.10
                mask_sig_clusters = np.where(res.clusters['p'] <= plot_pmin, True, False)
                sig_clusters = res.clusters[mask_sig_clusters]

                if sig_clusters.n_cases != None:

                    for i in range(sig_clusters.n_cases):

                        cluster_nb = i + 1

                        cluster = sig_clusters[i]['cluster']
                        tstart = sig_clusters[i]['tstart']
                        tstop = sig_clusters[i]['tstop']
                        clusterp = str(sig_clusters[i]['p'])

                        cluster_fname = op.join(output, 'clusters', hemi + '_' + regionName + '_' + str(t) + '_' + str(tstart) + '-' + str(tstop) + '_' + str(cluster_nb) + '_' + analysisType + '_' + coef + '_p' + clusterp + '.pickle')

                        timecourse = combine(ds['beta']).mean('source')
                        #################################################################################################full_timecourse = combine(ds['stc']).mean('source')


                        clusterNTuple = (res_fname,# res_fname
                            res_table, # res_table
                            cluster, # cluster
                            tstart, # tstart
                            tstop, # tstop
                            coef, # coefficient
                            #region, # regionName
                            regionName, # regionName
                            timecourse, # timecourse
                            hemi, # hemi
                            sources, # region
                            analysisType, # analysisType
                            cluster_nb, # cluster number
                            ds, # data
                            time[0], # original start time
                            time[1], # original stop time
                            clusterp # cluster p-value
                        )


                        pickle.dump(clusterNTuple,open(cluster_fname, 'wb'),protocol=4)
                        '''#temp_11thhour


clustersToPlot = []

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
    '''temp_11thhour
    graphName = op.join(output, 'graphs','%s_%s_cluster%s_%s-%s_%s-%s_%s_%s_p%s.png' %(hemi,regionName,cluster_nb,str(tstart),str(tstop),str(p_start),str(p_stop),analysisType,coef,str(clusP)))

    if os.path.exists(graphName):
        print('Cluster already plotted')
    else:

        ########################################################################
        ########################################################################
        # Plotting coefficient time course
        ########################################################################
        ########################################################################

        print('Plotting betas for time series time series for %s at %s %s from %s' %(coef,hemi,regionName,tstart))

        labels = eelbrain.labels_from_clusters(cluster)

        mne.write_labels_to_annot(labels,subject = 'fsaverage',subjects_dir=subjects_dir,
            overwrite=True,
            parc = coef + 'Cluster' + date
            )
        labels = mne.read_labels_from_annot(subject='fsaverage', subjects_dir=subjects_dir,
            parc = coef + 'Cluster' + date
            )

        stc = combine(ds['beta'])
        stc_region = stc.sub(source=labels[0])
        ds['beta'] = stc_region

        timecourse = stc_region.mean('source')

        activation = plot.UTSStat(timecourse, #x='intercept',#xeffect,
            ds = ds,
            error='sem',
            error_alpha = 0.10,
            legend = None,
            xlabel = 'Time (ms)',
            ylabel = 'Beta values',
            xlim = (epoch_tmin, epoch_tmax),
            show = False,
            title = 'Beta values of %s cluster in %s' %(coef, regionName)
            )
        activation.add_vspan(xmin=tstart, xmax=tstop, color='lightgrey', zorder=-50, alpha=0.4)
        #activation._axes[0].set_xticks([0,tstart,tstop])

        #for j in range(0,len(activation._axes[0].lines)):
            #activation._axes[0].lines[j].set_lw(w=0.75)
        #activation._axes[0].axvline(x=0.0,color="black",linestyle=":")
        activation.save(graphName, dpi=300)
        sleep(10)

        try:
            activation.close()
        except:
            print("Can't close activation plot")

        ########################################################################
        ########################################################################
        # Plotting intercept time course
        ########################################################################
        ########################################################################

        print('Plotting time series for %s at %s %s from %s' %(coef,hemi,regionName,tstart))

        intercept_fname = op.join(output, 'intercept', 'results', hemi + '_' + regionName + '_' + '1' + '_' + str(p_start) + '-' + str(p_stop) + '_' + analysisType + '_' + 'intercept' + '_spatiotemporal.pickle')
        intercept_file = open(intercept_fname, 'rb')
        intercept = pickle.load(intercept_file)
        intercept_file.close()
        stc = combine(intercept['beta'])

        stc_region = stc.sub(source=labels[0])
        int_timecourse = stc_region.mean('source')
        intercept['beta'] = stc_region
        '''
        #if 'condition' in coef or 'prefix' in coef:
        #    print(analysis)

        #    cond_fname = op.join(output, 'condition:CatViol', 'results', hemi + '_' + regionName + '_' + '1' + '_' + str(p_start) + '-' + str(p_stop) + '_' + analysisType + '_' + 'condition:CatViol' + '_betas.pickle')
        #    cond_file = open(cond_fname, 'rb')
        #    cond = pickle.load(cond_file)
        #    cond_file.close()
        #    stc = combine(cond['beta'])
        #    stc_region = stc.sub(source=labels[0])
        #    cond_timecourse = stc_region.mean('source')

        #    pref_fname = op.join(output, 'prefix:DU', 'results', hemi + '_' + regionName + '_' + '1' + '_' + str(p_start) + '-' + str(p_stop) + '_' + analysisType + '_' + 'prefix:DU' + '_betas.pickle')
        #    pref_file = open(pref_fname, 'rb')
        #    pref = pickle.load(pref_file)
        #    pref_file.close()
        #    stc = combine(pref['beta'])
        #    stc_region = stc.sub(source=labels[0])
        #    pref_timecourse = stc_region.mean('source')

        #    interact_fname = op.join(output, 'condition x prefix', 'results', hemi + '_' + regionName + '_' + '1' + '_' + str(p_start) + '-' + str(p_stop) + '_' + analysisType + '_' + 'condition x prefix' + '_betas.pickle')
        #    interact_file = open(interact_fname, 'rb')
        #    interact = pickle.load(interact_file)
        #    interact_file.close()
        #    stc = combine(interact['beta'])
        #    stc_region = stc.sub(source=labels[0])
        #    interact_timecourse = stc_region.mean('source')

        #    condEffect_timecourse = int_timecourse + cond_timecourse
        #    prefEffect_timecourse = int_timecourse + pref_timecourse
        #    intEffect_timecourse = int_timecourse + cond_timecourse + pref_timecourse + interact_timecourse

'''
        effect_timecourse = int_timecourse + timecourse

        ds['intercept'] = intercept['beta']

        ########################################################################
        ########################################################################
        # Plotting intercept vs. coefficient time course
        ########################################################################
        ########################################################################

        print("Printing fitted values for coefficient...")

        activation = plot.UTSStat(int_timecourse,
            ds = intercept,
            error='sem',
            error_alpha = 0.10,
            legend = None,
            xlabel = 'Time (ms)',
            ylabel = 'Predicted dSPM',
#            xlim = (epoch_tmin, epoch_tmax),
            show = False,
            title = str('Intercept at ' + regionName)
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

        graphName = op.join(output, 'graphs','%s_%s_cluster%s_%s-%s_%s-%s_%s_%s_p%s_intercept.png' %(hemi,regionName,cluster_nb,str(tstart),str(tstop),str(p_start),str(p_stop),analysisType,coef,str(clusP)))

        activation.save(graphName, dpi=300)
        sleep(15)
        try:
            activation.close()
        except:
            print("Can't close activation plot")

        fig, axes = plt.subplots()

        plt.plot(int_timecourse.mean(dims='case'),'black',label='Intercept',linewidth=0.75,linestyle='dashed')
        plt.plot(effect_timecourse.mean(dims='case'),'blue',label=coef,linewidth=0.75)
        #plt.plot(effect_timecourse.mean(dims='case'),'red',label=coef[1],linewidth=0.75)





        #print(tstart)
        #print(tstop)

        #fixedTStart = int(round(tstart,3) * 100) + 110
        #fixedTStop = int(round(tstop,3) * 100) + 110
        fixedTStart = (tstart*1000)+200
        fixedTStop = (tstop*1000)+200

        tStartName = str(fixedTStart)
        tStopName = str(fixedTStop)

        tStartName = str(int(round(tstart,3)*1000))
        tStopName = str(int(round(tstop,3)*1000))

        #print(fixedTStart)
        #print(fixedTStop)
        #print(coef)
        #print(intercept)

        if ':' in coef:
            fig.suptitle("Intercept vs. Coefficient for %s in %s %s cluster, %s - %s ms" %(str(coef.split(':')[0]),hemi,regionName,tStartName,tStopName))
        else:
            fig.suptitle("Intercept vs. Coefficient for %s in %s %s cluster, %s - %s ms" %(coef,hemi,regionName,tStartName,tStopName))


        axes.set_xticks([0,100,200,300,400,500,600,700,800])
        axes.set_xticklabels(['-200','','0','','200','','400','','600'])

        axes.axvline(x=200,color="black",linestyle="solid")

        axes.axvspan(fixedTStart, fixedTStop, alpha=0.2,color="grey")

        interceptYlim = activation.get_ylim()

        axes.set_ylim(ymin=-1*max(abs(interceptYlim[0]),abs(interceptYlim[1])),
            ymax=max(abs(interceptYlim[0]),abs(interceptYlim[1])))

        axes.set_ylabel("Fitted Activation (dSPM)")
        axes.set_xlabel("Time (ms)")

        axes.legend(loc="lower left")

        axes.spines['top'].set_visible(False)
        axes.spines['left'].set_visible(False)
        axes.spines['right'].set_visible(False)

        fig.set_figwidth(10)
        fig.set_figheight(4)

        #coef = coef.replace('/','')
        #coef = coef.replace(':','')

        graphName = op.join(output, 'graphs','%s_%s_cluster%s_%s-%s_%s-%s_%s_%s_p%s_effVsInt.png' %(hemi,regionName,cluster_nb,str(tstart),str(tstop),str(p_start),str(p_stop),analysisType,coef,str(clusP)))

        fig.savefig(graphName, dpi=300)
'''#temp_11thhour

        ########################################################################
        ########################################################################
        # Plotting levels of condition with shading for significant results
        ########################################################################
        ########################################################################
        #activation = eelbrain.plot.UTSStat(timecourse,'Condition',match='Subject',ds=ds,xlim=(0.0,1),legend='upper right', title='STG-lh, TagSurp, n=all (19)')
if True:
        newds = eelbrain.Dataset()
        newds['stc'] = load.fiff.stc_ndvar(stcs, subject='fsaverage', src='ico-4', subjects_dir=subjects_dir, parc=parc)
        newds['word_or_symbol'] = Factor(all_wordF)
        newds['letter_or_symbol'] = Factor(all_letterF)
        newds['noise_or_clean'] = Factor(all_noiseF)
        newds['letterWord_or_symbol'] = Factor(all_letterWordF)
        newds['Subject'] = eelbrain.Factor(all_subjs,random=True)

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
        '''
        fixedTStart = (tstart*1000)+200
        fixedTStop = (tstop*1000)+200

        tStartName = str(fixedTStart)
        tStopName = str(fixedTStop)

        tStartName = str(int(round(tstart,3)*1000))
        tStopName = str(int(round(tstop,3)*1000))

        timecourse = ds['stc'].mean('source')

        axes.set_xticks([0,100,200,300,400,500,600,700,800])
        axes.set_xticklabels(['-200','','0','','200','','400','','600'])

        axes.axvline(x=200,color="black",linestyle="solid")

        axes.axvspan(fixedTStart, fixedTStop, alpha=0.2,color="grey")

        interceptYlim = activation.get_ylim()

        axes.set_ylim(ymin=-1*max(abs(interceptYlim[0]),abs(interceptYlim[1])),
            ymax=max(abs(interceptYlim[0]),abs(interceptYlim[1])))

        axes.set_ylabel("Fitted Activation (dSPM)")
        axes.set_xlabel("Time (ms)")

        axes.legend(loc="lower left")

        axes.spines['top'].set_visible(False)
        axes.spines['left'].set_visible(False)
        axes.spines['right'].set_visible(False)

        fig.set_figwidth(10)
        fig.set_figheight(4)

        #coef = coef.replace('/','')
        #coef = coef.replace(':','')

        graphName = op.join(output, 'graphs','%s_%s_cluster%s_%s-%s_%s-%s_%s_%s_p%s_effVsInt.png' %(hemi,regionName,cluster_nb,str(tstart),str(tstop),str(p_start),str(p_stop),analysisType,coef,str(clusP)))

        fig.savefig(graphName, dpi=300)

        plt.plot(condEffect_timecourse.mean(dims='case'),'#69AD63',label='Prôti, CatViol',linewidth=0.75)
        plt.plot(prefEffect_timecourse.mean(dims='case'),'#61244A',label='Duḥ, SemViol',linewidth=0.75,linestyle="dashed")
        '''

        '''
        if 'condition' in coef or 'prefix' in coef:

            print("Plotting main effects...")

            fig, axes = plt.subplots()

            plt.plot(int_timecourse.mean(dims='case'),'#32612E',label='Prôti, SemViol',linewidth=0.75,linestyle="dashed")
            plt.plot(condEffect_timecourse.mean(dims='case'),'#69AD63',label='Prôti, CatViol',linewidth=0.75)
            plt.plot(prefEffect_timecourse.mean(dims='case'),'#61244A',label='Duḥ, SemViol',linewidth=0.75,linestyle="dashed")
            plt.plot(intEffect_timecourse.mean(dims='case'),'#AD6391',label='Duḥ, CatViol',linewidth=0.75)

            #print(tstart)
            #print(tstop)

            #print(fixedTStart)
            #print(fixedTStop)

            fig.suptitle("Effect of Condition * Prefix in %s %s cluster, %s - %s ms" %(hemi,regionName,tStartName,tStopName))

            axes.set_xticks([0,100,200,300,400,500,600,700,800])
            axes.set_xticklabels(['-200','','0','','200','','400','','600'])

            axes.axvspan(fixedTStart, fixedTStop, alpha=0.2,color="grey")

            axes.axvline(x=200,color="black",linestyle="solid")

            axes.set_ylim(ymin=-1*max(abs(interceptYlim[0]),abs(interceptYlim[1])),
                ymax=max(abs(interceptYlim[0]),abs(interceptYlim[1])))

            axes.set_ylabel("Fitted Activation (dSPM)")
            axes.set_xlabel("Time (ms)")

            axes.legend(loc="lower left")

            axes.spines['top'].set_visible(False)
            axes.spines['left'].set_visible(False)
            axes.spines['right'].set_visible(False)

            fig.set_figwidth(10)
            fig.set_figheight(4)

            #coef.replace('/','')

            graphName = op.join(output, 'graphs','%s_%s_cluster%s_%s-%s_%s-%s_%s_%s_p%s_conditions.png' %(hemi,regionName,cluster_nb,str(tstart),str(tstop),str(p_start),str(p_stop),analysisType,coef,str(clusP)))

            fig.savefig(graphName, dpi=300)

            # plt.plot(objCeffect_timecourse.mean(dims='case'),'#527A73',label='Bare Subj, Bare Obj',linewidth=0.6)
            # plt.plot(int_timecourse.mean(dims='case'),'#8457AD',label='Bare Subj, Acc Obj',linewidth=0.6)
            # plt.plot(subjCeffect_timecourse.mean(dims='case'),'#C489FA',label='Erg Subj, Acc Obj',linewidth=0.6)
            # plt.plot(intEffect_timecourse.mean(dims='case'),'#4AC7B1',label='Erg Subj, Bare Obj',linewidth=0.6)

            # timecourses = [int_timecourse,                            # Bare Subj, Acc Obj
            #                             objCeffect_timecourse,        # Bare Subj, Bare Obj
            #                             subjCeffect_timecourse,       # Erg Subj, Acc Obj
            #                             intEffect_timecourse,         # Erg Subj, Bare Obj
            # ]

            # condLabels = ['BareAcc','BareBare','ErgAcc','ErgBare']

            # for j in range(0,len(timecourses)):
            #     tc = timecourses[j]
            #     condLabel = condLabels[j]

            #     timecourseFile = open(output+'csv/'+condLabel+'_'+coef+'_'+str(tstart)+'_'+str(tstop)+'_'+str(cluster_nb)+'_'+region+'.csv', 'w')

            #     # get the timestamp
            #     toWrite = ''

            #     for i in range(0,len(tc.time)):
            #         #print(i)

            #     # check that it's within the cluster
            #         if tc.time[i] >= tstart:
            #             if tc.time[i] <= tstop:
            #                 print('hi')
            #                 toWrite += str(tc.time[i]) + ','

            #     # now, we'll iterate over each participant and get their information
            #                 for ptcp in tc.x:
            #                     toWrite += str(ptcp[i]) + ','

            #                 toWrite = toWrite[:-1]
            #                 toWrite += '\n'

            #     timecourseFile.write(toWrite)
            #     timecourseFile.close()
        '''

        ########################################################################
        ########################################################################
        # Plotting brain
        ########################################################################
        ########################################################################
        if hemi == 'left':
            brainside = 'lh'
#            if oppositeHemi:
#                brainside = 'rh'
        elif hemi == "right":
            brainside = 'rh'
#            if oppositeHemi:
#                brainside = 'lh'
        else:
            brainside = 'split'

        brain = plot.brain.cluster(cluster.mean('time'), surf='inflated', hemi=brainside,
        colorbar=True, time_label='ms', #w=600, h=400,
        foreground='black',
        mask = False,
        background='white',
        title = "Cluster for %s in %s %s from %s – %s" %(coef, hemi, regionName, str(tstart), str(tstop)),
#        vmin = -2.0,
        vmax = 2.0,
        smoothing_steps = 15,
        views = ['lateral','medial','rostral',
        'ventral'],
        subjects_dir=subjects_dir)
#        brain.plot_colorbar(label='t',orientation='vertical')


        graphName = op.join(output, 'graphs','%s_%s_cluster%s_%s-%s_%s-%s_%s_%s_p%s_brain.png' %(hemi,regionName,cluster_nb,str(tstart),str(tstop),str(p_start),str(p_stop),analysisType,coef,str(clusP)))

        brain.save_image(graphName)
        sleep(15)
        try:
            brain.close()
        except:
            print("Can't close brain")
