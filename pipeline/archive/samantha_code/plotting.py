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

from time import sleep
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import (make_axes_locatable, ImageGrid,
                                     inset_locator)
import os #for doing brain stuff
os.environ['ETS_TOOLKIT'] = 'wx' #for doing brain plotting stuff
import mne
import eelbrain
from surfer import Brain

mne.set_log_level(verbose='WARNING')

from main import *

subjects = ['Y0119','Y0208','Y0312','Y0321','Y0368','Y0371','Y0367','Y0369','Y0373','Y0374','Y0378','Y0379','Y0381','Y0382','Y0387','Y0393','Y0395','Y0396']

exp = 'savant_main/'
subjects_dir = ('new_baseline/' + exp + 'mri')

my_stc_names = newConds

stcs,subject,cond = [],[],[]
for sbj in subjects:
	stc_path = 'stc_average/' + exp + '%s/%s' %(sbj,sbj)
	for x in my_stc_names:
		stc = mne.read_source_estimate(stc_path + '_' + x + '_dSPM-rh.stc')
		stcs.append(stc)
        #stc = mne.read_source_estimate(stc_path + '_' + i + '_dSPM-rh.stc')
        #stcs.append(stc)
		cond.append(str.split(x,'%s' %sbj)[0])
        #cond.append(str.split(i,'%s' %sbj)[0])
		#print(cond)
		subject.append(sbj)
        #subject.append(sbj)
		del stc
		print ("done!")


##########plotting clusters####


'''
ds = eelbrain.Dataset()
ds['stc'] = eelbrain.load.fiff.stc_ndvar(stcs_rh,subject='fsaverage',src='ico-4',subjects_dir=subjects_dir,method='dSPM',fixed=True,parc='condition:CatViolCluster2023_May18_pmin05')
ds['Condition'] = eelbrain.Factor(cond)
ds['Subject'] = eelbrain.Factor(subject,random=True)
ds_backup = ds
'''






clustersToPlot = []
output = os.path.join('new_baseline/savant_main/Plots/Group/', '2023_Sept13_pmin05_Regressions_n18/')


for fileName in os.listdir(op.join(output, 'clusters')):

    if fileName.endswith('pickle') and "OF" in fileName:
        clusFile = open(op.join(output, 'clusters', fileName), 'rb')
        clus = pickle.load(clusFile)
        clusFile.close()
        clustersToPlot.append(clus)
print(len(clustersToPlot))
i = 1
for clus in clustersToPlot:



    res_fname = clus[0]
    res_table = clus[1]
    cluster = clus[2]
    tstart = clus[3]
    tstop = clus[4]
    coef = clus[5]
    regionName = clus[6]
    print(regionName)
    #timecourse = clus[7]
    hemi = clus[8]
    region = clus[9]
    analysisType = clus[10]
    cluster_nb = clus[11]
    #ds = clus[12]
    p_start = clus[13]
    p_stop = clus[14]
    clusP = clus[15]

    ds = eelbrain.Dataset()
    ds['stc'] = eelbrain.load.fiff.stc_ndvar(stcs,subject='fsaverage',src='ico-4',subjects_dir=subjects_dir,method='dSPM',fixed=True,parc=coef + 'Cluster' + date + '_' + str(i))
    ds['Condition'] = eelbrain.Factor(cond)
    ds['Subject'] = eelbrain.Factor(subject,random=True)
    ds_average = ds
    '''

    labels = eelbrain.labels_from_clusters(cluster)

    mne.write_labels_to_annot(labels,subject = 'fsaverage',subjects_dir=subjects_dir,
                        overwrite=True,
                        parc = coef + 'Cluster' + date + '_' + str(i)
                        )
    i = i +1
    '''
    labels = mne.read_labels_from_annot(subject='fsaverage', subjects_dir=subjects_dir,
                        parc = coef + 'Cluster' + date + '_' + str(i)
                        )
    print(labels)
    #print(labels[0])
    src = ds_average['stc']
    src_region = src.sub(source=labels[0])
    #print(src_region)
    ds_average['stc']=src_region

    timecourse = ds_average['stc'].mean('source')
    #if i == 0:
    activation = eelbrain.plot.UTSStat(timecourse,'Condition',match='Subject',sub=(ds_average['Condition']!='Gramm'),ds=ds_average,xlim=(0.0,.6),legend='upper right', title='Condition OF Sept 23 %s' %i, colors=colors)
    activation.add_vspan(xmin=tstart, xmax=tstop, color='lightgrey',alpha=.7)
    #print(src_region)
    #activation.savefig('may18%s.png' %str(i))
    i = i +1
    del labels
    #del ds_average
    #del ds
    #del src
    #del src_region
    #del timecourse
    #sleep(10)

'''
#plt.plot(timecourse.time,timecourse[0],color='red')
plt.ylabel('Activation (dSPM)')
plt.xlabel('Time (s)')
plt.title('test')
tstart = 0
plt.axvline(tstart,color='lightgrey',alpha=2)
#plt.xlim = tstart
plt.savefig('test-cooooooooooond.png')
plt.clf()
'''
#parc = mne.read_labels_from_annot('fsaverage','condition:CatViolCluster2023_May18_pmin05',subjects_dir=subjects_dir,hemi='rh') #read in the parcellation here. Typical options are aparc or Brodmann
