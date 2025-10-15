#########################
#Plotting
#########################

import mne

#########################
#N400
#########################

#------------------
#load GAs that we want to plot
#------------------
#rebaseline to -100ms
read_path = "/Users/jrs9906/Documents/MEG data/egyptian/GAs/"
save_path = "/Users/jrs9906/Documents/MEG data/egyptian/plots/"

congruent_clean = mne.read_evokeds(
    fname = read_path+"N400_congruent_clean_GA-ave.fif",
    condition=0, 
    baseline=[-.1,0],     
)

incongruent_clean = mne.read_evokeds(
    fname = read_path+"N400_incongruent_clean_GA-ave.fif",
    condition=0, 
    baseline=[-.1,0], 
)

congruent_clean.crop(-.1,1.2)
incongruent_clean.crop(-.1,1.2)

#--------------
#filter for prettier plotting?
#--------------
congruent_c = congruent_clean.copy().filter(l_freq=None, h_freq=10)
incongruent_c = incongruent_clean.copy().filter(l_freq=None, h_freq=10)

#----------------
#calculate difference waves
#----------------
clean_diff = mne.combine_evoked([incongruent_c, congruent_c], weights=[1, -1])

#------------------
#butterfly plots
#------------------

#butterfly of one condition
N400c_butterfly=congruent_c.plot(spatial_colors=True, gfp=True)
N400i_butterfly=incongruent_c.plot(spatial_colors=True, gfp=True)

#butterfly of difference wave (may or may not be better)
N400_diff_butterfly=clean_diff.plot(spatial_colors=True, gfp=True)

#set titles
N400c_butterfly.axes[0].set_title("N400 Congruent")
N400i_butterfly.axes[0].set_title("N400 Incongruent")
N400_diff_butterfly.axes[0].set_title("N400 difference")

#set size and save
N400c_butterfly.set_size_inches(8, 3)
N400i_butterfly.set_size_inches(8, 3)
N400c_butterfly.savefig(save_path+'N400c_butterfly.png', dpi=300)
N400i_butterfly.savefig(save_path+'N400i_butterfly.png', dpi=300)


#set size and save
N400_diff_butterfly.set_size_inches(8, 3)
N400_diff_butterfly.savefig('N400_diff_butterfly.png', dpi=300)

#---------------
#Topographically arranged waveforms
#---------------

#The legend is created from the comment on the evokeds, so we have to change these first
congruent_c.comment = 'congruent'
incongruent_c.comment = 'incongruent'

N400_topo_wave=mne.viz.plot_evoked_topo(
    evoked=[congruent_c, incongruent_c], 
    color=["blue", "red"], 
    legend = 'lower right',
    title='N400', 
    #background_color="w",
)

#set size and save
N400_topo_wave.set_size_inches(8, 5)
N400_topo_wave.savefig(save_path+'N400_topo_wave.png', dpi=300)

#---------------
#RMS of multiple conditions at once
#---------------

#plotting multiple conditions at the same time
# mne.viz.plot_compare_evokeds(
#     evokeds=dict(congruent=congruent_c, incongruent=incongruent_c, difference = clean_diff),
#     #colors=dict(congruent=0, incongruent=1),
#     #linestyles=dict(left="solid", right="dashed"),
#     time_unit="ms",
#     legend = 'upper right',
# )


#---------------
#Invidual channel, two conditions simultaneously
#---------------

#channel 54 is left anterior, so likely to show an MEG-N400
#channel 97 is even more left anterior

#plotting multiple conditions at the same time
#This returns a list of figures based on the number of picks
N400_wave=mne.viz.plot_compare_evokeds(
    evokeds=dict(congruent=congruent_c, incongruent=incongruent_c),
    picks="MEG 097", #if you don't choose a channel, it calculates the mean of all channels
    colors=['blue','red'],
    #linestyles=dict(left="solid", right="dashed"),
    time_unit="ms",
    legend = 'upper left',
    show_sensors = 'lower right',
    title = 'N400\nLeft Anterior (channel 97)',
)

#extend x-axis to include baseline
N400_wave[0].axes[0].spines['bottom'].set_bounds(-100, 1200)

#set size and save
N400_wave[0].set_size_inches(6, 4)
N400_wave[0].savefig(save_path+'N400_wave.png', dpi=300)



#------------------
#topograthic map/topoplot
#------------------
#import numpy as np

#plot instaneous amplitude at specific times
# times = np.arange(0.05, .8, .05)
# clean_diff.plot_topomap(times, ncols=5, nrows="auto")

#plot average amplitude in a window, centered on specific time points, with a window size given by the average argument
#by saving it as a variable, we can resize and save it to disk
#to see it, just type the name of the variable, or run only the command
N400_topo = clean_diff.plot_topomap(times=.4, average=0.2)

#change title?
N400_topo.axes[0].set_title("300-500ms")
N400_topo.set_suptitle("N400")

#set size and save
N400_topo.set_size_inches(4, 4)
N400_topo.savefig(save_path+'N400_topo.png', dpi=300)


#topoplot over window averages of different lengths
# times = [.100, .225, .400, .650]
# averaging_durations = [0.050, 0.050, 0.200, 0.300]
# clean_diff.plot_topomap(times=times, average=averaging_durations)


#--------------------
#joint plot is both a butterfly plot and a topoplot at peaks
#--------------------
#clean_diff.plot_joint()


#########################
#WH
#########################

#------------------
#load GAs that we want to plot
#------------------
#cleft starts at illi (2nd word)
#cleft_control starts at huwwa (1st word)
#the saved baseline is 400-600, so a pre baseline for the aux (next word)

#Note: These are baselined at the first word at 400-600ms, which is the end of the AUX
#re-baselining to 500-600ms to shorten the baseline period

read_path = "/Users/jrs9906/Documents/MEG data/egyptian/GAs/"
save_path = "/Users/jrs9906/Documents/MEG data/egyptian/plots/"

cleft = mne.read_evokeds(
    fname = read_path+"cleft_clean_GA-ave.fif",
    condition=0, 
    baseline=[.5, .6], 
)

cleft_control = mne.read_evokeds(
    fname = read_path+"cleft_control_clean_GA-ave.fif",
    condition=0, 
    baseline=[.5, .6], 
)

in_situ = mne.read_evokeds(
    fname = read_path+"in_situ_clean_GA-ave.fif",
    condition=0, 
    baseline=[.5, .6], 
)

in_situ_control = mne.read_evokeds(
    fname = read_path+"in_situ_control_clean_GA-ave.fif",
    condition=0, 
    baseline=[.5, .6], 
)

#--------------
#filter for prettier plotting?
#--------------
cleft = cleft.copy().filter(l_freq=None, h_freq=10)
cleft_control = cleft_control.copy().filter(l_freq=None, h_freq=10)
in_situ = in_situ.copy().filter(l_freq=None, h_freq=10)
in_situ_control = in_situ_control.copy().filter(l_freq=None, h_freq=10)

#crop out based on the baseline
cleft.crop(.5, 3)
cleft_control.crop(.5, 3)
in_situ.crop(.5, 3)
in_situ_control.crop(.5, 3)


#----------------
#calculate difference waves
#----------------
cleft_diff = mne.combine_evoked([cleft, cleft_control], weights=[1, -1])
in_situ_diff = mne.combine_evoked([in_situ, in_situ_control], weights=[1, -1])


#------------------
#butterfly plots, one condition at a time
#------------------

#butterfly of one condition
cleft_butterfly=cleft.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))
cleft_control_butterfly=cleft_control.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))

in_situ_butterfly=in_situ.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))
in_situ_control_butterfly=in_situ_control.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))

cleft_diff_butterfly=cleft_diff.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))
in_situ_diff_butterfly=in_situ_diff.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))

#Change the x-axis to be words in the sentence
x=[.6, 1.2, 1.8, 2.4]
labels=['auxiliary','noun','adjective','verb']
cleft_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
cleft_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')
cleft_control_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
cleft_control_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')
in_situ_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
in_situ_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')
in_situ_control_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
in_situ_control_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')
cleft_diff_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
cleft_diff_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')
in_situ_diff_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
in_situ_diff_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')


#set titles
cleft_butterfly.axes[0].set_title("WH-cleft")
cleft_control_butterfly.axes[0].set_title("yes-no")
in_situ_butterfly.axes[0].set_title("WH-in-situ")
in_situ_control_butterfly.axes[0].set_title("yes-no")
cleft_diff_butterfly.axes[0].set_title("WH-cleft difference")
in_situ_diff_butterfly.axes[0].set_title("WH-in-situ difference")

#set size 
cleft_butterfly.set_size_inches(8, 3)
cleft_control_butterfly.set_size_inches(8, 3)
in_situ_butterfly.set_size_inches(8, 3)
in_situ_control_butterfly.set_size_inches(8, 3)
in_situ_diff_butterfly.set_size_inches(8, 3)
in_situ_diff_butterfly.set_size_inches(8, 3)

#save
cleft_butterfly.savefig(save_path+'cleft_butterfly.png', dpi=300)
cleft_control_butterfly.savefig(save_path+'cleft_control_butterfly.png', dpi=300)
in_situ_butterfly.savefig(save_path+'in_situ_butterfly.png', dpi=300)
in_situ_control_butterfly.savefig(save_path+'in_situ_control_butterfly.png', dpi=300)
cleft_diff_butterfly.savefig(save_path+'cleft_diff_butterfly.png', dpi=300)
in_situ_diff_butterfly.savefig(save_path+'in_situ_diff_butterfly.png', dpi=300)

#---------------
#RMS (can do multiple conditions at once)
#---------------

#plotting multiple conditions at the same time
# mne.viz.plot_compare_evokeds(
#     evokeds=dict(cleft=cleft, yes_no=cleft_control, difference = cleft_diff),
#     #colors=dict(congruent=0, incongruent=1),
#     #linestyles=dict(left="solid", right="dashed"),
#     time_unit="ms",
# )


#---------------
#Invidual channel, two conditions simultaneously
#---------------

#channel 54 is left anterior, so likely to show an MEG-N400
#channel 97 is even more left anterior
#106 is right anterior

#CLEFT
#plotting multiple conditions at the same time
cleft_wave_LA=mne.viz.plot_compare_evokeds(
    evokeds=dict(cleft=cleft, yes_no=cleft_control),
    picks="MEG 097", #if you don't choose a channel, it calculates the mean of all channels
    colors=['red','blue'],
    #linestyles=dict(left="solid", right="dashed"),
    time_unit="ms",
    legend = 'lower right',
    show_sensors = 'upper right',
    title = 'WH-cleft\nLeft Anterior (channel 97)',
    vlines = [600],
    ylim=dict(mag=[-100,100]),
)

cleft_wave_RA=mne.viz.plot_compare_evokeds(
    evokeds=dict(cleft=cleft, yes_no=cleft_control),
    picks="MEG 106", #if you don't choose a channel, it calculates the mean of all channels
    colors=['red','blue'],
    #linestyles=dict(left="solid", right="dashed"),
    time_unit="ms",
    legend = 'lower right',
    show_sensors = 'upper right',
    title = 'WH-cleft\nRight Anterior (channel 106)',
    vlines = [600],
    ylim=dict(mag=[-100,100]),
)

#Change the x-axis to be words in the sentence, and make the line extend the entire length
x=[600,1200,1800,2400]
labels=['auxiliary','noun','adjective','verb']
cleft_wave_LA[0].axes[0].spines['bottom'].set_bounds(500, 3000)
cleft_wave_LA[0].axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
cleft_wave_LA[0].axes[0].set_xlabel('Words in the sentences (600ms SOA)')

#Change the x-axis to be words in the sentence
x=[600,1200,1800,2400]
labels=['auxiliary','noun','adjective','verb']
cleft_wave_RA[0].axes[0].spines['bottom'].set_bounds(500, 3000)
cleft_wave_RA[0].axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
cleft_wave_RA[0].axes[0].set_xlabel('Words in the sentences (600ms SOA)')

#set size and save
cleft_wave_LA[0].set_size_inches(6, 4)
cleft_wave_LA[0].savefig(save_path+'cleft_wave_left_anterior.png', dpi=300)
cleft_wave_RA[0].set_size_inches(6, 4)
cleft_wave_RA[0].savefig(save_path+'cleft_wave_right_anterior.png', dpi=300)


#in_situ
#plotting multiple conditions at the same time
in_situ_wave_LA=mne.viz.plot_compare_evokeds(
    evokeds=dict(in_situ=in_situ, yes_no=in_situ_control),
    picks="MEG 097", #if you don't choose a channel, it calculates the mean of all channels
    colors=['red','blue'],
    #linestyles=dict(left="solid", right="dashed"),
    time_unit="ms",
    legend = 'lower right',
    show_sensors = 'upper right',
    title = 'WH-in-situ\nLeft Anterior (channel 97)',
    vlines = [600],
    ylim=dict(mag=[-100,100]),
)

in_situ_wave_RA=mne.viz.plot_compare_evokeds(
    evokeds=dict(in_situ=in_situ, yes_no=in_situ_control),
    picks="MEG 106", #if you don't choose a channel, it calculates the mean of all channels
    colors=['red','blue'],
    #linestyles=dict(left="solid", right="dashed"),
    time_unit="ms",
    legend = 'lower right',
    show_sensors = 'upper right',
    title = 'WH-in-situ\nRight Anterior (channel 106)',
    vlines = [600],
    ylim=dict(mag=[-100,100]),
)

#Change the x-axis to be words in the sentence, and make the line extend the entire length
x=[600,1200,1800,2400]
labels=['wh/noun','preposition','noun','adjective']
in_situ_wave_LA[0].axes[0].spines['bottom'].set_bounds(500, 3000)
in_situ_wave_LA[0].axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
in_situ_wave_LA[0].axes[0].set_xlabel('Words in the sentences (600ms SOA)')

#Change the x-axis to be words in the sentence
x=[600,1200,1800,2400]
labels=['wh/noun','preposition','noun','adjective']
in_situ_wave_RA[0].axes[0].spines['bottom'].set_bounds(500, 3000)
in_situ_wave_RA[0].axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
in_situ_wave_RA[0].axes[0].set_xlabel('Words in the sentences (600ms SOA)')

#set size and save
in_situ_wave_LA[0].set_size_inches(6, 4)
in_situ_wave_LA[0].savefig(save_path+'in_situ_wave_left_anterior.png', dpi=300)
in_situ_wave_RA[0].set_size_inches(6, 4)
in_situ_wave_RA[0].savefig(save_path+'in_situ_wave_right_anterior.png', dpi=300)

#---------------
#Topographically arranged waveforms
#---------------

#cleft

#The legend is created from the comment on the evokeds, so we have to change these first
cleft.comment = 'cleft'
cleft_control.comment = 'yes/no'

cleft_topo_wave=mne.viz.plot_evoked_topo(
    evoked=[cleft, cleft_control], 
    color=["red", "blue"], 
    legend = 'lower right',
    title='WH-cleft', 
    #background_color="w",
)

#set size and save
cleft_topo_wave.set_size_inches(8, 5)
cleft_topo_wave.savefig(save_path+'cleft_topo_wave.png', dpi=300)

#in_situ
in_situ.comment = 'in_situ'
in_situ_control.comment = 'yes/no'

in_situ_topo_wave=mne.viz.plot_evoked_topo(
    evoked=[in_situ, in_situ_control], 
    color=["red", "blue"], 
    legend = 'lower right',
    title='WH-in-situ', 
    #background_color="w",
)

#set size and save
in_situ_topo_wave.set_size_inches(8, 5)
in_situ_topo_wave.savefig(save_path+'in_situ_topo_wave.png', dpi=300)


#------------------
#topograthic map/topoplot
#------------------
#plot average amplitude in a window, centered on specific time points, with a window size given by the average argument
#import numpy as np

#cleft
#topoplot over window averages of potentially different lengths
times = [1.05, 1.605, 2.205, 2.805]
averaging_durations = [0.3, 0.3, 0.3, 0.3]

cleft_topo = cleft_diff.plot_topomap(times=times, average=averaging_durations, vlim=(-45, 45))

#change title?
cleft_topo.axes[0].set_title("auxiliary\n300-600ms")
cleft_topo.axes[1].set_title("noun\n300-600ms")
cleft_topo.axes[2].set_title("adjective\n300-600ms")
cleft_topo.axes[3].set_title("verb\n300-600ms")
cleft_topo.suptitle("WH-cleft (minus yes/no)")

#set size and save
cleft_topo.set_size_inches(8, 4)
cleft_topo.savefig(save_path+'cleft_topo.png', dpi=300)

#in_situ
times = [1.05, 1.605, 2.205, 2.805]
averaging_durations = [0.3, 0.3, 0.3, 0.3]

in_situ_topo=in_situ_diff.plot_topomap(times=times, average=averaging_durations, vlim=(-45, 45))

#change title?
in_situ_topo.axes[0].set_title("wh/noun\n300-600ms")
in_situ_topo.axes[1].set_title("preposotion\n300-600ms")
in_situ_topo.axes[2].set_title("noun\n300-600ms")
in_situ_topo.axes[3].set_title("adjective\n300-600ms")
in_situ_topo.suptitle("WH-in-situ (minus yes/no)")

#set size and save
in_situ_topo.set_size_inches(8, 4)
in_situ_topo.savefig(save_path+'in_situ_topo.png', dpi=300)


#########################
#BA
#########################
#saved baseline is 0-50 on word 1. Might want to re-baseline.
#Word 2 is the pronoun.
#options: 400-600 (so, pre for pronoun), 1000-1200 (so after pronoun)
#can do it during read, or do it with .apply_baseline(.4, .6)

#------------------
#load GAs that we want to plot
#------------------

#Note: These are baselined at the first word at 400-600ms, which is the end of the AUX
#rebaseline to 100ms: 1100 to 1200
read_path = "/Users/jrs9906/Documents/MEG data/egyptian/GAs/"
save_path = "/Users/jrs9906/Documents/MEG data/egyptian/plots/"

ba_target = mne.read_evokeds(
    fname = read_path+"ba_target_clean_GA-ave.fif",
    condition=0, 
    baseline=[1.1, 1.2], 
)

ba_control = mne.read_evokeds(
    fname = read_path+"ba_control_clean_GA-ave.fif",
    condition=0, 
    baseline=[1.1, 1.2], 
)

#crop out the pre-baseline period and the accidental extra word
ba_target.crop(1.1, 4.8)
ba_control.crop(1.1, 4.8)

#--------------
#filter for prettier plotting?
#--------------
ba_target = ba_target.copy().filter(l_freq=None, h_freq=10)
ba_control = ba_control.copy().filter(l_freq=None, h_freq=10)

#----------------
#calculate difference waves
#----------------
ba_diff = mne.combine_evoked([ba_target, ba_control], weights=[1, -1])


#------------------
#butterfly plots, one condition at a time
#------------------

#butterfly of one condition
ba_target_butterfly=ba_target.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))
ba_control_butterfly=ba_control.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))

ba_diff_butterfly=ba_diff.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))

#set x-axis words
x=[1.2, 1.8, 2.4, 3, 3.6, 4.2]
labels=['auxiliary','preposition','noun', 'antecedent', 'verb', 'noun']
ba_target_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
ba_target_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')
ba_control_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
ba_control_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')
ba_diff_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
ba_diff_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')


#set titles
ba_target_butterfly.axes[0].set_title("Backward Anaphora: self")
ba_control_butterfly.axes[0].set_title("Backward Anaphora: I")
ba_diff_butterfly.axes[0].set_title("Backward Anaphora: difference")

#set size 
ba_target_butterfly.set_size_inches(8, 3)
ba_control_butterfly.set_size_inches(8, 3)
ba_diff_butterfly.set_size_inches(8, 3)

#save
ba_target_butterfly.savefig(save_path+'cleft_butterfly.png', dpi=300)
ba_control_butterfly.savefig(save_path+'cleft_control_butterfly.png', dpi=300)
ba_diff_butterfly.savefig(save_path+'cleft_diff_butterfly.png', dpi=300)

#---------------
#RMS (can do multiple conditions at once)
#---------------

#plotting multiple conditions at the same time
# mne.viz.plot_compare_evokeds(
#     evokeds=dict(cleft=cleft, yes_no=cleft_control, difference = cleft_diff),
#     #colors=dict(congruent=0, incongruent=1),
#     #linestyles=dict(left="solid", right="dashed"),
#     time_unit="ms",
# )


#---------------
#Invidual channel, two conditions simultaneously
#---------------

#channel 54 is left anterior, so likely to show an MEG-N400
#channel 97 is even more left anterior
#106 is right anterior

#CLEFT
#plotting multiple conditions at the same time
ba_wave_LA=mne.viz.plot_compare_evokeds(
    evokeds=dict(self=ba_target, I=ba_control),
    picks="MEG 097", #if you don't choose a channel, it calculates the mean of all channels
    colors=['red','blue'],
    #linestyles=dict(left="solid", right="dashed"),
    time_unit="ms",
    legend = 'lower right',
    show_sensors = 'upper right',
    title = 'Backward Anaphor\nLeft Anterior (channel 97)',
    ylim=dict(mag=[-100,100]),
    vlines=[1200],
)

ba_wave_RA=mne.viz.plot_compare_evokeds(
    evokeds=dict(self=ba_target, I=ba_control),
    picks="MEG 106", #if you don't choose a channel, it calculates the mean of all channels
    colors=['red','blue'],
    #linestyles=dict(left="solid", right="dashed"),
    time_unit="ms",
    legend = 'lower right',
    show_sensors = 'upper right',
    title = 'Backward Anaphora\nRight Anterior (channel 106)',
    ylim=dict(mag=[-100,100]),
    vlines=[1200],
)

#Change the x-axis to be words in the sentence, and make the line extend the entire length
x=[1200,1800, 2400, 3000, 3600, 4200]
labels=['auxiliary','prep.', 'noun', 'antecedent', 'verb', 'noun']
ba_wave_LA[0].axes[0].spines['bottom'].set_bounds(1100, 4800)
ba_wave_LA[0].axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
ba_wave_LA[0].axes[0].set_xlabel('Words in the sentences (600ms SOA)')

#Change the x-axis to be words in the sentence
x=[1200,1800, 2400, 3000, 3600, 4200]
labels=['auxiliary','prep.', 'noun', 'antecedent', 'verb', 'noun']
ba_wave_RA[0].axes[0].spines['bottom'].set_bounds(1100, 4800)
ba_wave_RA[0].axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
ba_wave_RA[0].axes[0].set_xlabel('Words in the sentences (600ms SOA)')

#set size and save
ba_wave_LA[0].set_size_inches(6, 4)
ba_wave_LA[0].savefig(save_path+'ba_wave_left_anterior.png', dpi=300)
ba_wave_RA[0].set_size_inches(6, 4)
ba_wave_RA[0].savefig(save_path+'ba_wave_right_anterior.png', dpi=300)


#---------------
#Topographically arranged waveforms
#---------------

#The legend is created from the comment on the evokeds, so we have to change these first
ba_target.comment = 'self'
ba_control.comment = 'I'

ba_topo_wave=mne.viz.plot_evoked_topo(
    evoked=[ba_target, ba_control], 
    color=["red", "blue"], 
    legend = 'lower right',
    title='Backward Anaphora', 
    #background_color="w",
)

#set size and save
ba_topo_wave.set_size_inches(8, 5)
ba_topo_wave.savefig(save_path+'ba_topo_wave.png', dpi=300)


#------------------
#topograthic map/topoplot
#------------------
#plot average amplitude in a window, centered on specific time points, with a window size given by the average argument
#import numpy as np

#cleft
#topoplot over window averages of potentially different lengths
#times = [.45, 1.05, 1.605, 2.205, 2.805, 3.405, 4.05, 4.605]
#averaging_durations = [0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15]
times = [1.605, 2.205, 2.805, 3.405, 4.05, 4.605]
averaging_durations = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3]

ba_topo = ba_diff.plot_topomap(times=times, average=averaging_durations, vlim=(-45, 45))

#change title?
# ba_topo.axes[0].set_title("when\n300-600ms")
# ba_topo.axes[1].set_title("self/I\n300-600ms")
# ba_topo.axes[2].set_title("auxiliary\n300-600ms")
# ba_topo.axes[3].set_title("preposition\n300-600ms")
# ba_topo.axes[4].set_title("noun\n300-600ms")
# ba_topo.axes[5].set_title("antecedent\n300-600ms")
# ba_topo.axes[6].set_title("verb\n300-600ms")
# ba_topo.axes[7].set_title("noun\n300-600ms")

ba_topo.axes[0].set_title("auxiliary\n300-600ms")
ba_topo.axes[1].set_title("prep.\n300-600ms")
ba_topo.axes[2].set_title("noun\n300-600ms")
ba_topo.axes[3].set_title("antecedent\n300-600ms")
ba_topo.axes[4].set_title("verb\n300-600ms")
ba_topo.axes[5].set_title("noun\n300-600ms")

ba_topo.suptitle("Backward Anaphora (self-I)")

#set size and save
ba_topo.set_size_inches(8, 4)
ba_topo.savefig(save_path+'ba_topo.png', dpi=300)




#########################
#BVA
#########################
#saved baseline is 400-600 on word 1 (verb), word 2 is self/noun

#------------------
#load GAs that we want to plot
#------------------

#Note: These are baselined at the first word at 400-600ms, which is the end of the AUX
#re-baseline to .5 to .6 for 100ms

read_path = "/Users/jrs9906/Documents/MEG data/egyptian/GAs/"
save_path = "/Users/jrs9906/Documents/MEG data/egyptian/plots/"

bva = mne.read_evokeds(
    fname = read_path+"bva_clean_GA-ave.fif",
    condition=0, 
    baseline=[.5,.6], 
)

ra = mne.read_evokeds(
    fname = read_path+"ra_clean_GA-ave.fif",
    condition=0, 
    baseline=[.5,.6], 
)

np = mne.read_evokeds(
    fname = read_path+"np_clean_GA-ave.fif",
    condition=0, 
    baseline=[.5,.6], 
)

#crop
bva.crop(.5, 2.4)
ra.crop(.5, 2.4)
np.crop(.5, 2.4)

#--------------
#filter for prettier plotting?
#--------------
bva = bva.copy().filter(l_freq=None, h_freq=10)
ra = ra.copy().filter(l_freq=None, h_freq=10)
np = np.copy().filter(l_freq=None, h_freq=10)

#----------------
#calculate difference waves
#----------------
bva_diff = mne.combine_evoked([bva, np], weights=[1, -1])
ra_diff = mne.combine_evoked([ra, np], weights=[1, -1])


#------------------
#butterfly plots, one condition at a time
#------------------

#butterfly of one condition
bva_butterfly=bva.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))
ra_butterfly=ra.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))
np_butterfly=np.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))


bva_diff_butterfly=bva_diff.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))
ra_diff_butterfly=ra_diff.plot(spatial_colors=True, gfp=True, ylim=dict(mag=[-100,100]))

#add words to x-axis
x=[.6, 1.2, 1.8]
labels=['self/noun','preposition','noun']
bva_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
bva_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')
ra_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
ra_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')
np_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
np_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')
bva_diff_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
bva_diff_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')
ra_diff_butterfly.axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
ra_diff_butterfly.axes[0].set_xlabel('Words in the sentences (600ms SOA)')

#set titles
bva_butterfly.axes[0].set_title("Bound Variable Anaphora: self")
ra_butterfly.axes[0].set_title("Regular Anaphora: self")
np_butterfly.axes[0].set_title("BVA/RA: noun")
bva_diff_butterfly.axes[0].set_title("Bound Variable Anaphora: difference")
ra_diff_butterfly.axes[0].set_title("Regular Anaphora: difference")

#set size 
bva_butterfly.set_size_inches(8, 3)
ra_butterfly.set_size_inches(8, 3)
np_butterfly.set_size_inches(8, 3)

bva_diff_butterfly.set_size_inches(8, 3)
ra_diff_butterfly.set_size_inches(8, 3)

#save
bva_butterfly.savefig(save_path+'bva_butterfly.png', dpi=300)
ra_butterfly.savefig(save_path+'ra_butterfly.png', dpi=300)
np_butterfly.savefig(save_path+'np_butterfly.png', dpi=300)

#---------------
#Invidual channel, two conditions simultaneously
#---------------

#channel 54 is left anterior, so likely to show an MEG-N400
#channel 97 is even more left anterior
#106 is right anterior


#plotting multiple conditions at the same time
bva_wave_LA=mne.viz.plot_compare_evokeds(
    evokeds=dict(bound_variable=bva, regular_anaphora=ra, control=np),
    picks="MEG 097", #if you don't choose a channel, it calculates the mean of all channels
    colors=['red','blue', 'green'],
    #linestyles=dict(left="solid", right="dashed"),
    time_unit="ms",
    legend = 'lower right',
    show_sensors = 'upper right',
    title = 'Bounda Variable Anaphora\nLeft Anterior (channel 97)',
    vlines = [600],
    ylim=dict(mag=[-100,100]),
)

bva_wave_RA=mne.viz.plot_compare_evokeds(
    evokeds=dict(bound_variable=bva, regular_anaphora=ra, control=np),
    picks="MEG 106", #if you don't choose a channel, it calculates the mean of all channels
    colors=['red','blue', 'green'],
    #linestyles=dict(left="solid", right="dashed"),
    time_unit="ms",
    legend = 'lower right',
    show_sensors = 'upper right',
    title = 'Bound Variable Anaphora\nRight Anterior (channel 106)',
    vlines = [600],
    ylim=dict(mag=[-100,100]),
)

#Change the x-axis to be words in the sentence, and make the line extend the entire length
x=[600,1200,1800]
labels=['self/noun','preposition','noun']
bva_wave_LA[0].axes[0].spines['bottom'].set_bounds(500, 2400)
bva_wave_LA[0].axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
bva_wave_LA[0].axes[0].set_xlabel('Words in the sentences (600ms SOA)')

#Change the x-axis to be words in the sentence
x=[600,1200,1800]
labels=['self/noun','preposition','noun']
bva_wave_RA[0].axes[0].spines['bottom'].set_bounds(500, 2400)
bva_wave_RA[0].axes[0].set_xticks(x,  labels, horizontalalignment = 'left')
bva_wave_RA[0].axes[0].set_xlabel('Words in the sentences (600ms SOA)')

#set size and save
bva_wave_LA[0].set_size_inches(6, 4)
bva_wave_LA[0].savefig(save_path+'bva_wave_left_anterior.png', dpi=300)
bva_wave_RA[0].set_size_inches(6, 4)
bva_wave_RA[0].savefig(save_path+'bva_wave_right_anterior.png', dpi=300)


#---------------
#Topographically arranged waveforms
#---------------

#The legend is created from the comment on the evokeds, so we have to change these first
bva.comment = 'bound variable'
ra.comment = 'regular anaphor'
np.comment = 'noun'

bva_topo_wave=mne.viz.plot_evoked_topo(
    evoked=[bva, ra, np], 
    color=["red", "blue", 'green'], 
    legend = 'lower right',
    title='Bound Variable Anaphora', 
    #background_color="w",
)

#set size and save
bva_topo_wave.set_size_inches(8, 5)
bva_topo_wave.savefig(save_path+'bva_topo_wave.png', dpi=300)


#------------------
#topograthic map/topoplot
#------------------
#plot average amplitude in a window, centered on specific time points, with a window size given by the average argument
#import numpy as np

#cleft
#topoplot over window averages of potentially different lengths
#times = [.45, 1.05, 1.605, 2.205, 2.805, 3.405, 4.05, 4.605]
#averaging_durations = [0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15]
times = [1.05, 1.605, 2.205]
averaging_durations = [0.3, 0.3, 0.3]

bva_topo = bva_diff.plot_topomap(times=times, average=averaging_durations, vlim=(-45, 45))
ra_topo = ra_diff.plot_topomap(times=times, average=averaging_durations, vlim=(-45, 45))

bva_topo.axes[0].set_title("self/noun\n300-600ms")
bva_topo.axes[1].set_title("preposition\n300-600ms")
bva_topo.axes[2].set_title("noun\n300-600ms")

ra_topo.axes[0].set_title("self/noun\n300-600ms")
ra_topo.axes[1].set_title("preposition\n300-600ms")
ra_topo.axes[2].set_title("noun\n300-600ms")

bva_topo.suptitle("Bound Variable Anaphora (self-noun)")
ra_topo.suptitle("Regular Anaphora (self-noun)")


#set size and save
bva_topo.set_size_inches(6, 4)
bva_topo.savefig(save_path+'bva_topo.png', dpi=300)
ra_topo.set_size_inches(6, 4)
ra_topo.savefig(save_path+'ra_topo.png', dpi=300)
