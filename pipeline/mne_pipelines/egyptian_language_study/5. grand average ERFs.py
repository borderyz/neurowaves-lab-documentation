##########################
#Calculating Grand Average ERFs
##########################

import os
import mne

#%%Clean loop

#-----------------
#1. Create file names to loop through
#-----------------

#create a list of filenames to load for each condition
n=12 #number of participants
file_names = [ ] #initialize an empty list
for i in range(n):  #loop through and append each name to the list
    participant = 'egyptian_sub'+f'{i+1:03}'+'_ERFs-ave.fif' #the stylus file
    file_names.append(participant)

#set the working directory to read
read_path = "/Users/jrs9906/Documents/MEG data/egyptian/"
os.chdir(read_path)

#-----------------
#2. Read in the evokeds in a loop, store in a list
#-----------------

#If you use the condition argument, then it will be an evoked object (the numbers are the order in which they were written in the write function)
#If you don't use the condition argument, it will be a list of evokeds, so it will need an index

#initialize a list
# N400_congruent=[]
# N400_incongruent=[]

cleft=[]
cleft_control=[]
in_situ=[]
in_situ_control=[]

# ba_target = []
# ba_control = []

bva = []
ra = []
np = []

#loop through
for entry in file_names:    
    # N400_congruent_temp = mne.read_evokeds(
    #     fname = read_path+"N400/subject_ERFs_clean/"+entry,
    #     condition=0, 
    #     baseline=None, 
    # )
    # N400_congruent.append(N400_congruent_temp)

    # N400_incongruent_temp = mne.read_evokeds(
    #     fname = read_path+"N400/subject_ERFs_clean/"+entry,
    #     condition=1, 
    #     baseline=None, 
    # )
    # N400_incongruent.append(N400_incongruent_temp)
    
    cleft_temp = mne.read_evokeds(
        fname = read_path+"wh/subject_ERFs_clean/"+entry,
        condition=0, 
        baseline=None, 
    )
    cleft.append(cleft_temp)
    
    in_situ_temp = mne.read_evokeds(
        fname = read_path+"wh/subject_ERFs_clean/"+entry,
        condition=1, 
        baseline=None, 
    )
    in_situ.append(in_situ_temp)
    
    cleft_control_temp = mne.read_evokeds(
        fname = read_path+"wh/subject_ERFs_clean/"+entry,
        condition=2, 
        baseline=None, 
    )
    cleft_control.append(cleft_control_temp)
    
    in_situ_control_temp = mne.read_evokeds(
        fname = read_path+"wh/subject_ERFs_clean/"+entry,
        condition=3, 
        baseline=None, 
    )
    in_situ_control.append(in_situ_control_temp)
    
    # ba_target_temp = mne.read_evokeds(
    #     fname = read_path+"ba/subject_ERFs_clean/"+entry,
    #     condition=0, 
    #     baseline=None, 
    # )
    # ba_target.append(ba_target_temp)
    
    # ba_control_temp = mne.read_evokeds(
    #     fname = read_path+"ba/subject_ERFs_clean/"+entry,
    #     condition=1, 
    #     baseline=None, 
    # )
    # ba_control.append(ba_control_temp)
    
    bva_temp = mne.read_evokeds(
        fname = read_path+"bva/subject_ERFs_clean/"+entry,
        condition=0, 
        baseline=None, 
    )
    bva.append(bva_temp)
    
    ra_temp = mne.read_evokeds(
        fname = read_path+"bva/subject_ERFs_clean/"+entry,
        condition=1, 
        baseline=None, 
    )
    ra.append(ra_temp)
    
    np_temp = mne.read_evokeds(
        fname = read_path+"bva/subject_ERFs_clean/"+entry,
        condition=2, 
        baseline=None, 
    )
    np.append(np_temp)
    


#-----------------
#3. Create the Grand Average
#-----------------

# N400_congruent_GA = mne.grand_average(
#     N400_congruent,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# N400_incongruent_GA = mne.grand_average(
#     N400_incongruent,
#     interpolate_bads=True,
#     drop_bads=True,
# )

cleft_GA = mne.grand_average(
    cleft,
    interpolate_bads=True,
    drop_bads=True,
)

in_situ_GA = mne.grand_average(
    in_situ,
    interpolate_bads=True,
    drop_bads=True,
)

cleft_control_GA = mne.grand_average(
    cleft_control,
    interpolate_bads=True,
    drop_bads=True,
)

in_situ_control_GA = mne.grand_average(
    in_situ_control,
    interpolate_bads=True,
    drop_bads=True,
)

# ba_target_GA = mne.grand_average(
#     ba_target,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# ba_control_GA = mne.grand_average(
#     ba_control,
#     interpolate_bads=True,
#     drop_bads=True,
# )

bva_GA = mne.grand_average(
    bva,
    interpolate_bads=True,
    drop_bads=True,
)

ra_GA = mne.grand_average(
    ra,
    interpolate_bads=True,
    drop_bads=True,
)

np_GA = mne.grand_average(
    np,
    interpolate_bads=True,
    drop_bads=True,
)

#-----------------
#4. Save the Grand Average
#-----------------

save_path = "/Users/jrs9906/Documents/MEG data/egyptian/GAs/"

# N400_congruent_GA.save(
#     fname = save_path+"N400_congruent_clean_GA-ave.fif",
#     overwrite = True,
# )

# N400_incongruent_GA.save(
#     fname = save_path+"N400_incongruent_clean_GA-ave.fif",
#     overwrite = True,
# )

cleft_GA.save(
    fname = save_path+"cleft_clean_GA-ave.fif",
    overwrite = True,
)

in_situ_GA.save(
    fname = save_path+"in_situ_clean_GA-ave.fif",
    overwrite = True,
)

cleft_control_GA.save(
    fname = save_path+"cleft_control_clean_GA-ave.fif",
    overwrite = True,
)

in_situ_control_GA.save(
    fname = save_path+"in_situ_control_clean_GA-ave.fif",
    overwrite = True,
)

# ba_target_GA.save(
#     fname = save_path+"ba_target_clean_GA-ave.fif",
#     overwrite = True,
# )

# ba_control_GA.save(
#     fname = save_path+"ba_control_clean_GA-ave.fif",
#     overwrite = True,
# )

bva_GA.save(
    fname = save_path+"bva_clean_GA-ave.fif",
    overwrite = True,
)

ra_GA.save(
    fname = save_path+"ra_clean_GA-ave.fif",
    overwrite = True,
)

np_GA.save(
    fname = save_path+"np_clean_GA-ave.fif",
    overwrite = True,
)


# #%%Dirty loop
#Needs updating - does not match above in terms of variable names

# #-----------------
# #1. Create file names to loop through
# #-----------------

# #create a list of filenames to load for each condition
# n=12 #number of participants
# file_names = [ ] #initialize an empty list
# for i in range(n):  #loop through and append each name to the list
#     participant = 'egyptian_sub'+f'{i+1:03}'+'_ERFs-ave.fif' #the stylus file
#     file_names.append(participant)

# #set the working directory to read
# read_path = "/Users/jrs9906/Documents/MEG data/egyptian/"
# os.chdir(read_path)

# #-----------------
# #2. Read in the evokeds in a loop, store in a list
# #-----------------

# #If you use the condition argument, then it will be an evoked object (the numbers are the order in which they were written in the write function)
# #If you don't use the condition argument, it will be a list of evokeds, so it will need an index

# #initialize a list
# N400_congruent=[]
# N400_incongruent=[]

# wh_cleft=[]
# wh_in_situ=[]
# yn=[]

# ba_target = []
# ba_control = []

# bva = []
# ra = []
# np = []

# #loop through
# for entry in file_names:    
#     N400_congruent_temp = mne.read_evokeds(
#         fname = read_path+"N400/subject_ERFs_dirty/"+entry,
#         condition=0, 
#         baseline=None, 
#     )
#     N400_congruent.append(N400_congruent_temp)

#     N400_incongruent_temp = mne.read_evokeds(
#         fname = read_path+"N400/subject_ERFs_dirty/"+entry,
#         condition=1, 
#         baseline=None, 
#     )
#     N400_incongruent.append(N400_incongruent_temp)
    
#     wh_cleft_temp = mne.read_evokeds(
#         fname = read_path+"wh/subject_ERFs_dirty/"+entry,
#         condition=0, 
#         baseline=None, 
#     )
#     wh_cleft.append(wh_cleft_temp)
    
#     wh_in_situ_temp = mne.read_evokeds(
#         fname = read_path+"wh/subject_ERFs_dirty/"+entry,
#         condition=1, 
#         baseline=None, 
#     )
#     wh_in_situ.append(wh_in_situ_temp)
    
#     yn_temp = mne.read_evokeds(
#         fname = read_path+"wh/subject_ERFs_dirty/"+entry,
#         condition=2, 
#         baseline=None, 
#     )
#     yn.append(yn_temp)
    
#     ba_target_temp = mne.read_evokeds(
#         fname = read_path+"ba/subject_ERFs_dirty/"+entry,
#         condition=0, 
#         baseline=None, 
#     )
#     ba_target.append(ba_target_temp)
    
#     ba_control_temp = mne.read_evokeds(
#         fname = read_path+"ba/subject_ERFs_dirty/"+entry,
#         condition=1, 
#         baseline=None, 
#     )
#     ba_control.append(ba_control_temp)
    
#     bva_temp = mne.read_evokeds(
#         fname = read_path+"bva/subject_ERFs_dirty/"+entry,
#         condition=0, 
#         baseline=None, 
#     )
#     bva.append(bva_temp)
    
#     ra_temp = mne.read_evokeds(
#         fname = read_path+"bva/subject_ERFs_dirty/"+entry,
#         condition=1, 
#         baseline=None, 
#     )
#     ra.append(ra_temp)
    
#     np_temp = mne.read_evokeds(
#         fname = read_path+"bva/subject_ERFs_dirty/"+entry,
#         condition=2, 
#         baseline=None, 
#     )
#     np.append(np_temp)
    


# #-----------------
# #3. Create the Grand Average
# #-----------------

# N400_congruent_GA = mne.grand_average(
#     N400_congruent,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# N400_incongruent_GA = mne.grand_average(
#     N400_incongruent,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# wh_cleft_GA = mne.grand_average(
#     wh_cleft,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# wh_in_situ_GA = mne.grand_average(
#     wh_in_situ,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# yn_GA = mne.grand_average(
#     yn,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# ba_target_GA = mne.grand_average(
#     ba_target,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# ba_control_GA = mne.grand_average(
#     ba_control,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# bva_GA = mne.grand_average(
#     bva,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# ra_GA = mne.grand_average(
#     ra,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# np_GA = mne.grand_average(
#     np,
#     interpolate_bads=True,
#     drop_bads=True,
# )

# #-----------------
# #4. Save the Grand Average
# #-----------------

# save_path = "/Users/jrs9906/Documents/MEG data/egyptian/GAs/"

# N400_congruent_GA.save(
#     fname = save_path+"N400_congruent_dirty_GA-ave.fif",
#     overwrite = True,
# )

# N400_incongruent_GA.save(
#     fname = save_path+"N400_incongruent_dirty_GA-ave.fif",
#     overwrite = True,
# )

# wh_cleft_GA.save(
#     fname = save_path+"wh_cleft_dirty_GA-ave.fif",
#     overwrite = True,
# )

# wh_in_situ_GA.save(
#     fname = save_path+"wh_in_situ_dirty_GA-ave.fif",
#     overwrite = True,
# )

# yn_GA.save(
#     fname = save_path+"yn_dirty_GA-ave.fif",
#     overwrite = True,
# )

# ba_target_GA.save(
#     fname = save_path+"ba_target_dirty_GA-ave.fif",
#     overwrite = True,
# )

# ba_control_GA.save(
#     fname = save_path+"ba_control_dirty_GA-ave.fif",
#     overwrite = True,
# )

# bva_GA.save(
#     fname = save_path+"bva_dirty_GA-ave.fif",
#     overwrite = True,
# )

# ra_GA.save(
#     fname = save_path+"ra_dirty_GA-ave.fif",
#     overwrite = True,
# )

# np_GA.save(
#     fname = save_path+"np_dirty_GA-ave.fif",
#     overwrite = True,
# )





