#For defining a fROI based off the results of a previous regression.
#This script is intended to define the fROI from the Tark localizer.
#
#
#This code needs output from "T5_Regresion.py" and also draws from "main.py"
#The output of this code is a file containing a list of statistical tests
#which will then need copy-pasted at the end of "main.py"
#"5b_Regresions_fROI.py" will need run after the copy-pasting into main.py
#
#
#Samantha Wray, 2022, Partially based off of code from Dustin Chacón, Suhail Matar, and Julien Dirani
#
#

import wx
import csv
import itertools
import mne, eelbrain, os, glob, pickle
import numpy as np
import pandas as pd
from os.path import join
import os.path as op
from scipy.stats import zscore
from eelbrain import *
from time import sleep
import matplotlib.pyplot as plt

from main import *

mne.set_log_level(verbose='WARNING')
eelbrain.configure(frame=False)


###define your directory structure here. remember to set the date and sampleSize in "main.py"
output = os.path.join('new_ica/savant_tark', 'Plots/Group/%s_Regressions_n%s/' %(date,str(sampleSize)))
print(output)
subjects_dir = ('new_ica/savant_main/mri')


############################
clustersToPlot = []
toPrint = []

hemisphereAnnotation = {"left":"lh","right":"rh"}


for fileName in os.listdir(op.join(output, 'clusters')):

    if fileName.endswith('pickle'):
        if 'Word' in fileName: #for Savant_Arabic: if 'Word' in fileName
            clusFile = open(op.join(output, 'clusters', fileName), 'rb')
            clus = pickle.load(clusFile)
            clusFile.close()
            clustersToPlot.append(clus)
if len(clustersToPlot) > 1:
    i = 1
    print("Multiple clusters found. Parcellations will be Tark_FROI_hemisphere_N with N = cluster number")
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
        label = eelbrain.labels_from_clusters(cluster)
        label[0].name = "Tark_FROI_" + hemi
        parcName = "Tark_FROI_" + hemi + "_" + str(i)
        mne.write_labels_to_annot(label,subject='fsaverage', parc=parcName ,subjects_dir=subjects_dir, overwrite=True)
        toPrint.append("('M170 Analysis_fROI_" + str(i) + "', (" + str(tstart) + "," + str(tstop) + "), ['Tark_FROI_" + hemi + "-" + hemisphereAnnotation[hemi] + "'],'" + str(label[0].name) + "','" + parcName + "', '" + hemi + "', 'TP', False, True, False),") #this needs fixed, it is not the label name at the moment
        i += 1 #Tark_FROI_left-lh

elif len(clustersToPlot) == 1:
    print("One cluster found")
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
        label = eelbrain.labels_from_clusters(cluster)
        label[0].name = "Tark_FROI_" + hemi
        mne.write_labels_to_annot(label,subject='fsaverage', parc='Tark_FROI',subjects_dir=subjects_dir, overwrite=True)
        toPrint.append("('Tark_Analysis_fROI_" + str(i) + "', (" + str(tstart) + "," + str(tstop) + "), ['Tark_FROI_" + hemisphereAnnotation[hemi] + "'],'" + str(label[0].name) + "','Tark_FROI', '" + hemi + "', 'TP', False, True, False),")
else:
    print("No clusters found. Check that there was a significant cluster from the Tark localizer for Words/Letters")


if toPrint:
    myfile = open('fROI_regressions_for_main.txt','w')
    myfile.write('analyses_fROI = [' + '\n')
    for x in toPrint:
        myfile.write(x + '\n')
    myfile.write('\n'+']')
    myfile.close()
#analyses_fROI = [
  # title          times             ROIs            name   parcelation               formula           only corrects? gramms? viols?
#('M170 Analysis_fROI_1', (0.09999999999999998,0.16499999999999998), ['Tark_FROI_left-lh'],'Tark_FROI_left','Tark_FROI_left_1', 'left', 'TP', False, True, False),
#('M170 Analysis_fROI_2', (0.12999999999999998,0.176), ['Tark_FROI_left-lh'],'Tark_FROI_left','Tark_FROI_left_2', 'left', 'TP', False, True, False),
#]
