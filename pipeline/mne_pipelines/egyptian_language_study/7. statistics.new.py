####################
#mass univariate cluster-based permutation test on difference waves
####################

#adapted from an online tutorial: 
#https://neuraldatascience.io/7-eeg/erp_group_stats.html

#%% 
#####################
#Import libraries
#####################
import mne
import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt

#%% 
#####################################
#Preliminary step: Create an adjacency matrix
#####################################

#we need to load one participant to extract the channel information
data_path = "/Users/jrs9906/Documents/MEG data/egyptian/N400/subject_ERFs_clean/"
file_name = "egyptian_sub001_ERFs-ave.fif"

p1 = mne.read_evokeds(
    fname = data_path+file_name,
    condition=0, 
    baseline=None, 
)

#------------------
#Create an adjacency matrix. 
#This is a matrix that specifies which channels are adjacent to each other on the scalp. 
#------------------

#we can use one participant for all tests as long as they use the same channel arrangment (same MEG system)
adjacency, ch_names = mne.channels.find_ch_adjacency(info = p1.info, ch_type = None)

#--------------
#we have to remove channel 92 because it is broken in the KIT MEG
#--------------
#remove it from ch_names
ch_names.remove('MEG 092')  
#remove it from adjacency, which is in a special scipy format, so it is complicated; first the row, then the column
adjacency = scipy.sparse.csr_array(np.delete(adjacency.toarray(),91, axis=0))
adjacency = scipy.sparse.csr_array(np.delete(adjacency.toarray(),91, axis=1))

#-------------
#We can visualize these in a plot with lines connecting adjacent channels:
#-------------
mne.viz.plot_ch_adjacency(p1.info, adjacency, ch_names=ch_names);

#%% 
#####################################
#Preliminary step: Create a dictionary of channels and hemispheres to arrange the raster plot
#####################################

#use the example subject from above; this is fine as long as all subjects use the same channel numbers and locations

#loop through and extract coordinates
index = []
channel = []
x = []
y =[]
z =[]
for i in range(207):  #loop through and append each name to the list
    temp_index = i
    temp_channel = p1.info["chs"][i]["ch_name"]
    temp_x = p1.info["chs"][i]['loc'][:3][0]
    temp_y = p1.info["chs"][i]['loc'][:3][1]
    temp_z = p1.info["chs"][i]['loc'][:3][2]
    index.append(temp_index)
    channel.append(temp_channel)
    x.append(temp_x)
    y.append(temp_y)
    z.append(temp_z)

#create data frame
df = pd.DataFrame({'index':index, 'channel':channel, 'x':x, 'y':y, 'z':z})

#this function splits into hemispheres
def label_hemisphere(row):
    if row['x'] < 0:
        return 'left'
    elif row['x'] > 0:
        return 'right'
    else:
        return 'error'
    
#It usually doesn't make sense to have a midline in MEG, but if we want one, we have to choose a range for it
#find midline, this line allows us to guess and test until we find values that yield the set of channels we like
#df.loc[df['x'].between(-.0175,.0175)]

#function with a midline
# def label_hemisphere(row):
#     if row['x'] > -.0175 and row['x'] < .0175:
#         return 'midline'
#     elif row['x'] < 0:
#         return 'left'
#     elif row['x'] > 0:
#         return 'right'
#     else:
#         return 'error'


#apply the function
df.apply(label_hemisphere, axis=1)

#save it as a new column
df['hemisphere'] = df.apply(label_hemisphere, axis=1)

#sort by y axis position (anterior to posterior)
#these are sorted backward because the plot function flips it, I think?
dict_sorted=df.sort_values(by='y', ascending = True).groupby('hemisphere')['index'].apply(list).to_dict()

#%%
#########################
#N400
#########################

#------------------
#load subject ERFs in a loop
#if it needs re-baselining or cropping, do it in this loop
#------------------
#rebaseline to -100
data_path = "/Users/jrs9906/Documents/MEG data/egyptian/N400/subject_ERFs_clean/"
save_path = "/Users/jrs9906/Documents/MEG data/egyptian/plots/"
n=12 #number of participants
N400_diff_waves = [ ] #initialize an empty list

for i in range(n):

    file_name = "egyptian_sub"+f'{i+1:03}'+"_ERFs-ave.fif"
    
    congruent = mne.read_evokeds(
        fname = data_path+file_name,
        condition=0, 
        baseline=[-.1,0], 
    )
    
    congruent.crop(0, 1.2) #crop out the baseline
    congruent.comment = 'congruent'
    
    incongruent = mne.read_evokeds(
        fname = data_path+file_name,
        condition=1, 
        baseline=[-.1,0], 
    )
    
    incongruent.crop(0, 1.2) #crop out the baseline
    incongruent.comment = 'incongruent'


    #----------------
    #calculate difference waves
    #----------------
    N400_diff = mne.combine_evoked([incongruent, congruent], weights=[1, -1])

    #----------------
    #append
    #----------------
    N400_diff_waves.append(N400_diff)


#--------------------
#plot to check that the data loaded correctly? This will look like a grand average
#--------------------
# mne.viz.plot_evoked_topomap(mne.grand_average(N400_diff_waves), 
#                             times=.500, average=0.200, 
#                             show_names=True, sensors=False,
#                             contours=False,
#                             size=4
#                            );

#------------------
#Reshape: The spatio_temporal_cluster_1samp_test() function requires the data to be shaped as 
#participants x time x channels, but our data are participants x channels x time
#so we will use np.swapaxes() to swap the time [1] and channel [2] axes:
#------------------
N400_data = np.swapaxes(np.array([e.get_data() for e in N400_diff_waves]),1, 2)

# check shape of result to see that it is participants x time x channels
N400_data.shape

#%%
#----------------
#Run the mass univariate cluster-based permutation test
#----------------

#select the number of permutations
n_perm = 1000

#run the function: ths calls the adjacency matrix from above, the reshaped data, and number of permutations
N400_t_obs, N400_clusters, N400_cluster_pv, N400_H0 = mne.stats.spatio_temporal_cluster_1samp_test( 
    N400_data, 
    adjacency=adjacency,
    n_permutations=n_perm, 
    out_type='mask',
    n_jobs=-1, 
    verbose='Info'
    )

#------------
#find the significant clusters to use in plots
#------------

#if mask_idx is empty, there are no significant clusters
N400_mask_idx = np.where(N400_cluster_pv < 0.05)[0]
N400_mask = [N400_clusters[idx] for idx in N400_mask_idx]

# stats output is time X chan, but MEG data is chan X time, so transpose so it matches the data for plotting
N400_mask = N400_mask[0].T

#with 7 there are no significant results.

#%%
#----------------
#plot a basic raster plot of the cluster results (channels arranged by number)
#----------------

time_unit = dict(time_unit="s")
mne.grand_average(N400_diff_waves).plot_image(
    colorbar=False,
    show=False,
    mask=N400_mask,
    **time_unit,
    )

#%%
##########################
#Plots: raster, topoplot
#This is based on matplotlib
##########################

#--------------------------
#Raster: requires the dictionary that we created above
#--------------------------
selections = dict_sorted

fig, axes = plt.subplots(nrows=2, figsize=(10, 10))
axes = {sel: ax for sel, ax in zip(selections, axes.ravel())}
N400_raster = mne.grand_average(N400_diff_waves).plot_image(axes=axes,
                            group_by=selections,
                            colorbar=False,
                            show=False,
                            mask=N400_mask,
                            show_names=False,
                            titles=None,
                            **time_unit,
                            #clim = dict(eeg=[-2, 2])
                            )
plt.colorbar(axes["left"].images[-1], ax=list(axes.values()), shrink=0.3, label="fT")

plt.show()

#change titles
N400_raster.axes[0].set_title("N400: Left Hemisphere")
N400_raster.axes[1].set_title("N400: Right Hemisphere")

#save
N400_raster.savefig(save_path+'N400_raster.png', dpi=300)

#---------------
#Topoplot that shows the significant channels
#---------------

#grand average for plotting
N400_diff_GA = mne.grand_average(N400_diff_waves)

#plot parameters
times = [.4]
averaging_durations = [0.2]

N400_sig_topo=N400_diff_GA.plot_topomap(times=times,
                                             average=averaging_durations,
                                             mask=N400_mask,
                                             contours=False,
                                             sensors=True,
                                             size=4
                                            );

#change title?
N400_sig_topo.axes[0].set_title("300-500ms")
N400_sig_topo.suptitle("N400 significant channels") 

#set size and save
N400_sig_topo.set_size_inches(4, 4)
N400_sig_topo.savefig(save_path+'N400_sig_topo.png', dpi=300)



#%%
#########################
#WH
#########################
#------------------
#load subject ERFs in a loop
#if it needs re-baselining or cropping, do it in this loop
#------------------
#rebaseline to -100
data_path = "/Users/jrs9906/Documents/MEG data/egyptian/wh/subject_ERFs_clean/"
save_path = "/Users/jrs9906/Documents/MEG data/egyptian/plots/"
n=12 #number of participants
cleft_diff_waves = [ ] #initialize an empty list for cleft
in_situ_diff_waves = [ ] #initialize an empty list for fronting

for i in range(n):

    file_name = "egyptian_sub"+f'{i+1:03}'+"_ERFs-ave.fif"
    
    cleft = mne.read_evokeds(
        fname = data_path+file_name,
        condition=0, 
        baseline=[.5, .6], 
    )

    cleft_control = mne.read_evokeds(
        fname = data_path+file_name,
        condition=2, 
        baseline=[.5, .6], 
    )

    in_situ = mne.read_evokeds(
        fname = data_path+file_name,
        condition=1, 
        baseline=[.5, .6], 
    )

    in_situ_control = mne.read_evokeds(
        fname = data_path+file_name,
        condition=3, 
        baseline=[.5, .6], 
    )
    
    
    #crop out the baseline for stats purposes, also label appropriately
    cleft.crop(.6, 3) #crop out the baseline
    cleft.comment = 'cleft'
    cleft_control.crop(.6, 3) #crop out the baseline
    cleft_control.comment = 'yes_no'
    in_situ.crop(.6, 3) #crop out the baseline
    in_situ.comment = 'in_situ'
    in_situ_control.crop(.6, 3) #crop out the baseline
    in_situ_control.comment = 'yes_no'
    
    

    #----------------
    #calculate difference waves
    #----------------
    cleft_diff = mne.combine_evoked([cleft, cleft_control], weights=[1, -1])
    in_situ_diff = mne.combine_evoked([in_situ, in_situ_control], weights=[1, -1])

    #----------------
    #append
    #----------------
    cleft_diff_waves.append(cleft_diff)
    in_situ_diff_waves.append(in_situ_diff)


#--------------------
#plot to check that the data loaded correctly? This will look like a grand average
#--------------------
# mne.viz.plot_evoked_topomap(mne.grand_average(fronting_diff_waves), 
#                             times=1.600, average=0.200, 
#                             show_names=True, sensors=False,
#                             contours=False,
#                             size=4
#                            );

#------------------
#Reshape: The spatio_temporal_cluster_1samp_test() function requires the data to be shaped as 
#participants x time x channels, but our data are participants x channels x time
#so we will use np.swapaxes() to swap the time [1] and channel [2] axes:
#------------------
cleft_data = np.swapaxes(np.array([e.get_data() for e in cleft_diff_waves]),1, 2)
in_situ_data = np.swapaxes(np.array([e.get_data() for e in in_situ_diff_waves]),1, 2)

# check shape of result to see that it is participants x time x channels
cleft_data.shape
in_situ_data.shape

#%%
#----------------
#Run the mass univariate cluster-based permutation test
#----------------

#select the number of permutations
n_perm = 1000

#run the function: ths calls the adjacency matrix from above, the reshaped data, and number of permutations
cleft_t_obs, cleft_clusters, cleft_cluster_pv, cleft_H0 = mne.stats.spatio_temporal_cluster_1samp_test( 
    cleft_data, 
    adjacency=adjacency,
    n_permutations=n_perm, 
    out_type='mask',
    n_jobs=-1, 
    verbose='Info'
    )

in_situ_t_obs, in_situ_clusters, in_situ_cluster_pv, in_situ_H0 = mne.stats.spatio_temporal_cluster_1samp_test( 
    in_situ_data, 
    adjacency=adjacency,
    n_permutations=n_perm, 
    out_type='mask',
    n_jobs=-1, 
    verbose='Info'
    )

#------------
#find the significant clusters to use in plots
#------------

#if mask_idx is empty, there are no significant clusters
cleft_mask_idx = np.where(cleft_cluster_pv < 0.05)[0]
cleft_mask = [cleft_clusters[idx] for idx in cleft_mask_idx]

# stats output is time X chan, but MEG data is chan X time, so transpose so it matches the data for plotting
cleft_mask = cleft_mask[0].T
#Nothing significant at 12.

#if mask_idx is empty, there are no significant clusters
in_situ_mask_idx = np.where(in_situ_cluster_pv < 0.05)[0]
in_situ_mask = [in_situ_clusters[idx] for idx in in_situ_mask_idx]

# stats output is time X chan, but MEG data is chan X time, so transpose so it matches the data for plotting
in_situ_mask = in_situ_mask[0].T

#Nothing significant at 12.

#%%
#----------------
#plot a basic raster plot of the cluster results (channels arranged by number)
#----------------

time_unit = dict(time_unit="s")
mne.grand_average(cleft_diff_waves).plot_image(
    colorbar=False,
    show=False,
    mask=cleft_mask,
    **time_unit,
    )

#%%
##########################
#Plots: raster, topoplot
#This is based on matplotlib
##########################

#--------------------------
#Raster: requires the dictionary that we created above
#--------------------------
selections = dict_sorted

fig, axes = plt.subplots(nrows=2, figsize=(10, 10))
axes = {sel: ax for sel, ax in zip(selections, axes.ravel())}
cleft_raster = mne.grand_average(cleft_diff_waves).plot_image(axes=axes,
                            group_by=selections,
                            colorbar=False,
                            show=False,
                            mask=cleft_mask,
                            show_names=False,
                            titles=None,
                            **time_unit,
                            #clim = dict(eeg=[-2, 2])
                            )
plt.colorbar(axes["left"].images[-1], ax=list(axes.values()), shrink=0.3, label="fT")

plt.show()

#change titles
cleft_raster.axes[0].set_title("Cleft: Left Hemisphere")
cleft_raster.axes[1].set_title("Cleft: Right Hemisphere")

#save
cleft_raster.savefig(save_path+'cleft_raster.png', dpi=300)

#---------------
#Topoplot that shows the significant channels
#---------------

#grand average for plotting
cleft_diff_GA = mne.grand_average(cleft_diff_waves)

#plot parameters
times = [1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2]
#averaging_durations = [0.1, 0.3, 0.3]

cleft_sig_topo=cleft_diff_GA.plot_topomap(times=times,
                                             #average=averaging_durations,
                                             mask=cleft_mask,
                                             contours=False,
                                             sensors=True,
                                             size=2,
                                             ncols="auto", 
                                             nrows=2,
                                            );

#change title?
#cleft_sig_topo.axes[0].set_title("cleft significant channels\n300-500ms")
cleft_sig_topo.suptitle("wh-cleft significant channels") 

#set size and save
cleft_sig_topo.set_size_inches(8, 4)
cleft_sig_topo.savefig(save_path+'cleft_sig_topo.png', dpi=300)

#%%
#################
#BA
#################
#------------------
#load subject ERFs in a loop
#if it needs re-baselining or cropping, do it in this loop
#------------------
#rebaseline to 1.1 to 1.2

data_path = "/Users/jrs9906/Documents/MEG data/egyptian/ba/subject_ERFs_clean/"
save_path = "/Users/jrs9906/Documents/MEG data/egyptian/plots/"
n=12 #number of participants
ba_diff_waves = [ ] #initialize an empty list for ba

for i in range(n):

    file_name = "egyptian_sub"+f'{i+1:03}'+"_ERFs-ave.fif"
    
    ba_target = mne.read_evokeds(
        fname = data_path+file_name,
        condition=0, 
        baseline=[1.1, 1.2], 
    )

    ba_control = mne.read_evokeds(
        fname = data_path+file_name,
        condition=1, 
        baseline=[1.1, 1.2], 
    )

    
    
    #crop out the baseline for stats purposes, also label appropriately
    ba_target.crop(1.1, 4.8) #crop out the baseline
    ba_target.comment = 'self'
    ba_control.crop(1.1, 4.8) #crop out the baseline
    ba_control.comment = 'I'
    
    
    

    #----------------
    #calculate difference waves
    #----------------
    ba_diff = mne.combine_evoked([ba_target, ba_control], weights=[1, -1])

    #----------------
    #append
    #----------------
    ba_diff_waves.append(ba_diff)


#--------------------
#plot to check that the data loaded correctly? This will look like a grand average
#--------------------
# mne.viz.plot_evoked_topomap(mne.grand_average(ba_diff_waves), 
#                             times=1.600, average=0.200, 
#                             show_names=True, sensors=False,
#                             contours=False,
#                             size=4
#                            );

#------------------
#Reshape: The spatio_temporal_cluster_1samp_test() function requires the data to be shaped as 
#participants x time x channels, but our data are participants x channels x time
#so we will use np.swapaxes() to swap the time [1] and channel [2] axes:
#------------------
ba_data = np.swapaxes(np.array([e.get_data() for e in ba_diff_waves]),1, 2)

# check shape of result to see that it is participants x time x channels
ba_data.shape

#%%
#----------------
#Run the mass univariate cluster-based permutation test
#----------------

#select the number of permutations
n_perm = 1000

#run the function: ths calls the adjacency matrix from above, the reshaped data, and number of permutations
ba_t_obs, ba_clusters, ba_cluster_pv, ba_H0 = mne.stats.spatio_temporal_cluster_1samp_test( 
    ba_data, 
    adjacency=adjacency,
    n_permutations=n_perm, 
    out_type='mask',
    n_jobs=-1, 
    verbose='Info'
    )


#------------
#find the significant clusters to use in plots
#------------

#if mask_idx is empty, there are no significant clusters
ba_mask_idx = np.where(ba_cluster_pv < 0.05)[0]
ba_mask = [ba_clusters[idx] for idx in ba_mask_idx]

# stats output is time X chan, but MEG data is chan X time, so transpose so it matches the data for plotting
ba_mask = ba_mask[0].T

#nothing significant at 7


#%%
#----------------
#plot a basic raster plot of the cluster results (channels arranged by number)
#----------------

time_unit = dict(time_unit="s")
mne.grand_average(ba_diff_waves).plot_image(
    colorbar=False,
    show=False,
    mask=cleft_mask,
    **time_unit,
    )

#%%
##########################
#Plots: raster, topoplot
#This is based on matplotlib
##########################

#--------------------------
#Raster: requires the dictionary that we created above
#--------------------------
selections = dict_sorted

fig, axes = plt.subplots(nrows=2, figsize=(10, 10))
axes = {sel: ax for sel, ax in zip(selections, axes.ravel())}
ba_raster = mne.grand_average(ba_diff_waves).plot_image(axes=axes,
                            group_by=selections,
                            colorbar=False,
                            show=False,
                            mask=ba_mask,
                            show_names=False,
                            titles=None,
                            **time_unit,
                            #clim = dict(eeg=[-2, 2])
                            )
plt.colorbar(axes["left"].images[-1], ax=list(axes.values()), shrink=0.3, label="fT")

plt.show()

#change titles
ba_raster.axes[0].set_title("Backward Anaphora: Left Hemisphere")
ba_raster.axes[1].set_title("Backward Anaphora: Right Hemisphere")

#save
ba_raster.savefig(save_path+'ba_raster.png', dpi=300)

#---------------
#Topoplot that shows the significant channels
#---------------

#grand average for plotting
ba_diff_GA = mne.grand_average(ba_diff_waves)

#plot parameters
times = [1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2]
#averaging_durations = [0.1, 0.3, 0.3]

ba_sig_topo=cleft_diff_GA.plot_topomap(times=times,
                                             #average=averaging_durations,
                                             mask=ba_mask,
                                             contours=False,
                                             sensors=True,
                                             size=2,
                                             ncols="auto", 
                                             nrows=2,
                                            );

#change title?
#cleft_sig_topo.axes[0].set_title("cleft significant channels\n300-500ms")
ba_sig_topo.suptitle("Backward Anaphora significant channels") 

#set size and save
ba_sig_topo.set_size_inches(8, 4)
ba_sig_topo.savefig(save_path+'ba_sig_topo.png', dpi=300)

#%%
#########################
#BVA
#########################
#------------------
#load subject ERFs in a loop
#if it needs re-baselining or cropping, do it in this loop
#------------------
#rebaseline to -100
data_path = "/Users/jrs9906/Documents/MEG data/egyptian/bva/subject_ERFs_clean/"
save_path = "/Users/jrs9906/Documents/MEG data/egyptian/plots/"
n=12 #number of participants
bva_diff_waves = [ ] #initialize an empty list for cleft
ra_diff_waves = [ ] #initialize an empty list for fronting

for i in range(n):

    file_name = "egyptian_sub"+f'{i+1:03}'+"_ERFs-ave.fif"
    
    bva = mne.read_evokeds(
        fname = data_path+file_name,
        condition=0, 
        baseline=[.5, .6], 
    )

    bva_control = mne.read_evokeds(
        fname = data_path+file_name,
        condition=2, 
        baseline=[.5, .6], 
    )

    ra = mne.read_evokeds(
        fname = data_path+file_name,
        condition=1, 
        baseline=[.5, .6], 
    )

    ra_control = mne.read_evokeds(
        fname = data_path+file_name,
        condition=2, 
        baseline=[.5, .6], 
    )
    
    
    #crop out the baseline for stats purposes, also label appropriately
    bva.crop(.6, 2.4) #crop out the baseline
    bva.comment = 'self'
    bva_control.crop(.6, 2.4) #crop out the baseline
    bva_control.comment = 'noun'
    ra.crop(.6, 2.4) #crop out the baseline
    ra.comment = 'self'
    ra_control.crop(.6, 2.4) #crop out the baseline
    ra_control.comment = 'noun'
    
    

    #----------------
    #calculate difference waves
    #----------------
    bva_diff = mne.combine_evoked([bva, bva_control], weights=[1, -1])
    ra_diff = mne.combine_evoked([ra, ra_control], weights=[1, -1])

    #----------------
    #append
    #----------------
    bva_diff_waves.append(bva_diff)
    ra_diff_waves.append(ra_diff)


#--------------------
#plot to check that the data loaded correctly? This will look like a grand average
#--------------------
# mne.viz.plot_evoked_topomap(mne.grand_average(bva_diff_waves), 
#                             times=1.600, average=0.200, 
#                             show_names=True, sensors=False,
#                             contours=False,
#                             size=4
#                            );

#------------------
#Reshape: The spatio_temporal_cluster_1samp_test() function requires the data to be shaped as 
#participants x time x channels, but our data are participants x channels x time
#so we will use np.swapaxes() to swap the time [1] and channel [2] axes:
#------------------
bva_data = np.swapaxes(np.array([e.get_data() for e in bva_diff_waves]),1, 2)
ra_data = np.swapaxes(np.array([e.get_data() for e in ra_diff_waves]),1, 2)

# check shape of result to see that it is participants x time x channels
bva_data.shape
ra_data.shape

#%%
#----------------
#Run the mass univariate cluster-based permutation test
#----------------

#select the number of permutations
n_perm = 1000

#run the function: ths calls the adjacency matrix from above, the reshaped data, and number of permutations
bva_t_obs, bva_clusters, bva_cluster_pv, bva_H0 = mne.stats.spatio_temporal_cluster_1samp_test( 
    bva_data, 
    adjacency=adjacency,
    n_permutations=n_perm, 
    out_type='mask',
    n_jobs=-1, 
    verbose='Info'
    )

ra_t_obs, ra_clusters, ra_cluster_pv, ra_H0 = mne.stats.spatio_temporal_cluster_1samp_test( 
    ra_data, 
    adjacency=adjacency,
    n_permutations=n_perm, 
    out_type='mask',
    n_jobs=-1, 
    verbose='Info'
    )

#------------
#find the significant clusters to use in plots
#------------

#if mask_idx is empty, there are no significant clusters
bva_mask_idx = np.where(bva_cluster_pv < 0.05)[0]
bva_mask = [bva_clusters[idx] for idx in bva_mask_idx]

# stats output is time X chan, but MEG data is chan X time, so transpose so it matches the data for plotting
bva_mask = bva_mask[0].T
#nothing significant at 7!

#if mask_idx is empty, there are no significant clusters
ra_mask_idx = np.where(ra_cluster_pv < 0.05)[0]
ra_mask = [ra_clusters[idx] for idx in ra_mask_idx]

# stats output is time X chan, but MEG data is chan X time, so transpose so it matches the data for plotting
ra_mask = ra_mask[0].T

#Nothing significant at 7.

#%%
#----------------
#plot a basic raster plot of the cluster results (channels arranged by number)
#----------------

time_unit = dict(time_unit="s")
mne.grand_average(bva_diff_waves).plot_image(
    colorbar=False,
    show=False,
    mask=bva_mask,
    **time_unit,
    )

#%%
##########################
#Plots: raster, topoplot
#This is based on matplotlib
##########################

#--------------------------
#Raster: requires the dictionary that we created above
#--------------------------
selections = dict_sorted

fig, axes = plt.subplots(nrows=2, figsize=(10, 10))
axes = {sel: ax for sel, ax in zip(selections, axes.ravel())}
bva_raster = mne.grand_average(bva_diff_waves).plot_image(axes=axes,
                            group_by=selections,
                            colorbar=False,
                            show=False,
                            mask=bva_mask,
                            show_names=False,
                            titles=None,
                            **time_unit,
                            #clim = dict(eeg=[-2, 2])
                            )
plt.colorbar(axes["left"].images[-1], ax=list(axes.values()), shrink=0.3, label="fT")

plt.show()

#change titles
bva_raster.axes[0].set_title("bva: Left Hemisphere")
bva_raster.axes[1].set_title("bva: Right Hemisphere")

#save
bva_raster.savefig(save_path+'bva_raster.png', dpi=300)

#---------------
#Topoplot that shows the significant channels
#---------------

#grand average for plotting
bva_diff_GA = mne.grand_average(bva_diff_waves)

#plot parameters
times = [1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2]
#averaging_durations = [0.1, 0.3, 0.3]

bva_sig_topo=bva_diff_GA.plot_topomap(times=times,
                                             #average=averaging_durations,
                                             mask=bva_mask,
                                             contours=False,
                                             sensors=True,
                                             size=2,
                                             ncols="auto", 
                                             nrows=2,
                                            );

#change title?
#cleft_sig_topo.axes[0].set_title("cleft significant channels\n300-500ms")
bva_sig_topo.suptitle("wh-bva significant channels") 

#set size and save
bva_sig_topo.set_size_inches(8, 4)
bva_sig_topo.savefig(save_path+'bva_sig_topo.png', dpi=300)
