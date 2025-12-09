## RUN THIS *eelbrain* IN THE EELBRAIN ENVIRONMENT
# D. A. Chacón (2022)

# Based off of code from Julien Dirani
# ---File structure----
# ROOT>
#     MRI>
#         subjs
#     MEG>
#         subjs
#     STC>

##############################
# Importing relevant packages
##############################

import mne, eelbrain, os, glob, pickle
import numpy as np
import pandas as pd
from os.path import join

from main import *

# This is for trickier graphing

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import (make_axes_locatable, ImageGrid,
                                     inset_locator)

#%gui qt

expName += "Tark"

del event_id
event_id = event_id_tark

del mappings
mappings = mappings_tark

del conditions
conditions = conditions_tark

del newConds
newConds = newConds_tark

del colors, linetype, condNames, newPoss
colors = colors_tark
linetype = linetype_tark
condNames = condNames_tark
newPoss = newPoss_tark

mne.set_log_level(verbose='WARNING')

os.chdir(ROOT) #setting current dir
subjects_dir = os.path.join(ROOT, 'MRI')


# These are the NYUAD KIT sensors split into left/right halves and
# frontal/posterior halves
regions = dict(LeftFrontal =['MEG 009', 'MEG 013', 'MEG 017', 'MEG 020', 'MEG 022', 'MEG 025', 'MEG 026', 'MEG 031', 'MEG 035', 'MEG 036', 'MEG 037', 'MEG 038', 'MEG 039', 'MEG 040', 'MEG 041', 'MEG 043', 'MEG 045', 'MEG 047', 'MEG 048', 'MEG 049', 'MEG 051', 'MEG 052', 'MEG 054', 'MEG 055', 'MEG 056', 'MEG 067', 'MEG 070', 'MEG 072', 'MEG 082', 'MEG 083', 'MEG 084', 'MEG 085', 'MEG 086', 'MEG 087', 'MEG 088', 'MEG 093', 'MEG 095', 'MEG 097', 'MEG 099', 'MEG 101', 'MEG 102', 'MEG 103', 'MEG 104', 'MEG 107', 'MEG 109', 'MEG 110', 'MEG 111', 'MEG 112', 'MEG 120', 'MEG 134', 'MEG 135', 'MEG 146', 'MEG 168'],
LeftPosterior = ['MEG 003', 'MEG 005', 'MEG 006', 'MEG 012', 'MEG 015', 'MEG 016', 'MEG 019', 'MEG 033', 'MEG 034', 'MEG 050', 'MEG 053', 'MEG 064', 'MEG 065', 'MEG 066', 'MEG 068', 'MEG 069', 'MEG 071', 'MEG 098', 'MEG 100', 'MEG 113', 'MEG 115', 'MEG 116', 'MEG 117', 'MEG 118', 'MEG 119', 'MEG 136', 'MEG 145', 'MEG 148', 'MEG 149', 'MEG 150', 'MEG 151', 'MEG 152', 'MEG 161', 'MEG 162', 'MEG 163', 'MEG 164', 'MEG 165', 'MEG 166', 'MEG 167', 'MEG 177', 'MEG 178', 'MEG 179', 'MEG 180', 'MEG 181', 'MEG 182', 'MEG 183', 'MEG 184', 'MEG 187', 'MEG 197', 'MEG 198', 'MEG 199', 'MEG 200', 'MEG 204'],
RightFrontal = ['MEG 001', 'MEG 007', 'MEG 008', 'MEG 018', 'MEG 021', 'MEG 024', 'MEG 028', 'MEG 029', 'MEG 030', 'MEG 032', 'MEG 042', 'MEG 044', 'MEG 046', 'MEG 057', 'MEG 059', 'MEG 060', 'MEG 061', 'MEG 062', 'MEG 063', 'MEG 073', 'MEG 074', 'MEG 075', 'MEG 076', 'MEG 077', 'MEG 078', 'MEG 081', 'MEG 089', 'MEG 090', 'MEG 091', 'MEG 092', 'MEG 094', 'MEG 096', 'MEG 105', 'MEG 106', 'MEG 114', 'MEG 121', 'MEG 122', 'MEG 123', 'MEG 124', 'MEG 125', 'MEG 127', 'MEG 128', 'MEG 130', 'MEG 133', 'MEG 144', 'MEG 158', 'MEG 191'],
RightPosterior = ['MEG 002', 'MEG 004', 'MEG 010', 'MEG 011', 'MEG 014', 'MEG 023', 'MEG 058', 'MEG 079', 'MEG 080', 'MEG 126', 'MEG 129', 'MEG 131', 'MEG 132', 'MEG 137', 'MEG 138', 'MEG 139', 'MEG 140', 'MEG 141', 'MEG 142', 'MEG 143', 'MEG 147', 'MEG 153', 'MEG 154', 'MEG 155', 'MEG 156', 'MEG 157', 'MEG 159', 'MEG 160', 'MEG 169', 'MEG 170', 'MEG 172', 'MEG 173', 'MEG 174', 'MEG 175', 'MEG 176', 'MEG 185', 'MEG 186', 'MEG 188', 'MEG 189', 'MEG 190', 'MEG 192', 'MEG 193', 'MEG 194', 'MEG 195', 'MEG 196', 'MEG 201', 'MEG 202', 'MEG 203', 'MEG 206', 'MEG 208'])

# Do you want to plot individual's butterfly plots (e.g., all of the sensors from an individual)?
indButterfly = True
# Do you want to plot the average sensors over particular regions by condition?
indRegionPlots = True

# Do you want to plot average butterfly plots?
avgButterfly = True
# Do you want to plot the average sensors over particular regions?
avgRegionPlots = True
# Do you want to plot the topographic maps?
avgTopoMaps = True


# This will hold ALL the epochs (across all subjects and conditions) for the grand butterfly plot
allEpos = [] 

# This will hold each participant's average by each condition, which will then be grand averaged. It's held as a dictionary,
# because MNE likes to average over lists of Evoked objects
allConds = dict() 

for mapping in mappings:
    allConds[mapping] = []

# Loop over the subjects...
for subj in subjects:
        print('>>  Getting epochs: subj=%s'%subj)
        epochs = mne.read_epochs('MEG/%s/Tark/%s_%s_ICA-epo.fif' %(subj,subj, expName))

# Collect all their evoked waveforms
        evoked = [] #  This subject's evoked objects

# Figure out the conditions
        conditions = event_id.keys()
        for mapping in mappings:
            evoked.append(epochs[mappings[mapping]].average())
            allEpos.append(epochs[mappings[mapping]].average())
            allConds[mapping].append(epochs[mappings[mapping]].average()) # Getting this subject's averages by condition which we'll then grand average over
        print('Done.')

# Plot average evoked by participant
        if indButterfly:
            if not os.path.isdir('Plots/Individuals/%s' %subj):
                os.makedirs('Plots/Individuals/%s' %subj)
            all_evokeds = mne.combine_evoked(evoked, weights='equal')
            evoked_plot = all_evokeds.plot_joint(show=False,title = subj)

            evoked_plot.savefig('Plots/Individuals/%s/%s_evoked_Tark.png'%(subj,subj))

        if indRegionPlots:

            evkdConds = dict(zip(mappings.keys(),evoked))

            for region in regions:
                sensorPlot = mne.viz.plot_compare_evokeds(evkdConds,
                    picks = regions[region],
                    colors = list(colors.values()),
                    linestyles = list(linetype.values()),
                    title = 'Region %s for subject %s' %(region,subj),
                    show = False)
                sensorPlot[0].set_figwidth(25)
                sensorPlot[0].savefig('Plots/Individuals/%s/%s_%s_avgSensorPlot_Tark.png' %(subj,subj,region))

if avgButterfly:
    all_evokeds = mne.combine_evoked(allEpos, weights='equal')
    evoked_plot = all_evokeds.plot_joint(show=False, title = 'Average')
    evoked_plot.savefig('Plots/Group/%s_avg_evoked_n%s_Tark.png' %(date,str(sampleSize)))
    all_evokeds.crop(tmin=0.0,tmax=1.2)
#    evoked_plot = all_evokeds.plot_joint(show=False, title = 'Average')
#    evoked_plot.savefig('Plots/Group/%s_avg_evoked_n%s_justVerb.png' %(date,str(sampleSize)))

if avgRegionPlots or avgTopoMaps:

    grandAvgs = [] # We'll collect all the grand-averaged conditions, because some plotting functions prefer lists and others prefer dictionaries

    for key in allConds:
        print("Grand averaging condition " + key + "...")
        grandAvg = mne.grand_average(allConds[key])
        grandAvg.comment = key # Grand-averaging loses the condition label, so we're resupplying it
        grandAvgs.append(grandAvg)
        del grandAvg

if avgRegionPlots:

    grandAvgsDict = dict(zip(mappings.keys(),grandAvgs)) # Some functions prefer having a dictionary where the key is the condition name

    for region in regions:
        sensorPlot = mne.viz.plot_compare_evokeds(grandAvgsDict,
            picks = regions[region],
            colors = list(colors.values()),
            linestyles = list(linetype.values()),
            title = 'Average, ' + region,
            show = False)
        sensorPlot[0].set_figwidth(25)
        sensorPlot[0].savefig('Plots/Group/%s_avg_%s_evoked_n%s_Tark.png' %(date, region, str(sampleSize)))

# ######################################################
# # Okay, this part needs some explanation
# # This will generate a scalp distribution map for each word in each condition
# ######################################################

if avgTopoMaps:

    # Next, we'll do the same thing, but zooming in more on the critical analysis window,
    # which is the verb and the subsequent adverb. We won't do the fancy naming scheme this time

    times = [0.050, 0.070, 0.090, 0.110, 0.130, 0.150, 0.170, 0.190, 0.210, 0.230, 0.250, 0.59] # New time slices here
    times100 = ['50ms', '70ms', '90ms', '110ms', '130ms', '150ms', '170ms', '190ms', '210ms', '230ms', '250', 'end']

    fig, axes = plt.subplots(len(grandAvgs),len(times),sharex=True,sharey=True)

    for i in range(0,len(grandAvgs)): # 4 = number of conditions
        evoked = grandAvgs[i]
        cond = evoked.comment
        condName = condNames[cond]

        evoked.plot_topomap(times = times, 
            average = 0.020,   # Average 10ms either direction
            vmin = -50,         # We put a minimum and maximum on the voltage maps, so to equalize the graphs
            vmax = 50,
            show = False,  
            axes = axes[newPoss[i]] # We put it in the row (axes[i]), but I call on newPoss here because I wanted to reorder
            )
        for j in range(0,len(times)-1): # Now, we cycle over the epochs/words
            title = times100[j] # We want the label to just give the time
            axes[newPoss[i]][j].annotate(title,xy=(0.60,-0.05)) # And then, we want to add a label slightly off to the right of the head
            axes[newPoss[i]][j].set_title('') # We don't want a "title" above each head (e.g., 0.3s in large bold font over the 0th epoch)
        axes[newPoss[i]][0].set_title(condName) # ... but we DO want a condition label, which I've chose to put over the 1st word in the row
        #axes[i].plot(subplot)

    fig.suptitle = "Topographic maps at critical time window"
    fig.set_size_inches(20.5,10.5)

    fig.savefig('Plots/Group/%s_avg_topo_n%s_Tark.png' %(date, str(sampleSize)),dpi=400)


#####################
#####################

    grandAvgDiffs = []

    # grandAvgs[0] = FourChars
    # grandAvgs[1] = OneChar
    # grandAvgs[2] = Letters
    # grandAvgs[3] = Noise
    # grandAvgs[4] = Symbols

    LengthEffect = mne.combine_evoked([grandAvgs[0],grandAvgs[1]], weights=[1,-1])
    LengthEffect.comment = 'LengthEffect'

    LetterVsNoiseEffect = mne.combine_evoked([grandAvgs[2],grandAvgs[3]], weights=[1,-1])
    LetterVsNoiseEffect.comment = 'LettersVsNoiseEffect'    

    LetterVsSymbolsEffect = mne.combine_evoked([grandAvgs[2],grandAvgs[4]], weights=[1,-1])
    LetterVsSymbolsEffect.comment = 'LettersVsSymbolsEffect'        

    bigCondNames = {'LengthEffect': 'Four Symbols -\n One Symbol',
    'LettersVsNoiseEffect': 'Letter/Words -\n Noise',
    'LettersVsSymbolsEffect':  'Letter/Words -\n Symbol/Symbols'}

#     bigCondNames = {'CatViolEffect': "Category Viol. -\nGrammatical",
#     'SemViolEffect': 'Semantic Viol. -\nGrammatical',
#     'CatSemDiff': 'Cat Viol. - Sem Viol.'}

    grandAvgDiffs = [LengthEffect, LetterVsNoiseEffect, LetterVsSymbolsEffect]
    fig, axes = plt.subplots(len(grandAvgDiffs),len(times),sharex=True,sharey=True)

    for i in range(0,len(grandAvgDiffs)):
        ev = grandAvgDiffs[i]
        cond = ev.comment
        condName = bigCondNames[cond]

    # Then, we built the topomap....

        ev.plot_topomap(times = times, # The time silces we want
            average = 0.020,   # We average 300ms, i.e., we stretch 150ms on either side; so the first epoch reaches from 150ms-450ms
#            vmin = -50,         # We put a minimum and maximum on the voltage maps, so to equalize the graphs
#            vmax = 50,
            show = False,  
            axes = axes[i]
            #newPoss[i]] # We put it in the row (axes[i]), but I call on newPoss here because I wanted to reorder
            )

        for j in range(0,len(times)-1): # Now, we cycle over the epochs/words
            title = times100[j] # We want a label that says "Word 1/2/3..." and then put the word underneath it
            axes[newPoss[i]][j].annotate(title,xy=(0.60,-0.05)) # And then, we want to add a label slightly off to the right of the head
            axes[i][j].set_title('') # We don't want a "title" above each head (e.g., 0.3s in large bold font over the 0th epoch)

        axes[i][0].set_title(condName) # ... but we DO want a condition label, which I've chose to put over the 1st word in the row
        #axes[i].plot(subplot)        

    fig.suptitle = "Effect of critical conditions"
    fig.set_size_inches(20.5,6.5)

    fig.savefig('Plots/Group/%s_diff_topo_n%s_Tark.png' %(date, str(sampleSize)),dpi=400)




