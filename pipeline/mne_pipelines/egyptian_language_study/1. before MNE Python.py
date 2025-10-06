#################
#MEG processing steps that happen before MNE Python steps
#################

#--------------
#Install MNE Python
#--------------
#By far the easiest approach is to use the MNE installer (https://mne.tools/stable/install/index.html). 
#This comes with all of the tools and packages that are likely to be necessary, including autoreject and the mne gui.
#MNE installs a shortcut to the terminal that it calls **Prompt** in the MNE applications folder. 
#This will open a terminal window with MNE active. This is very useful! This is how you open mne kit2fiff to integrate headshape information.


#--------------
#Install Spyder
#--------------
#It is easiest to interact with Python through an IDE. There are several options, including Spyder, Pycharm, and VS Code.
#I prefer Spyder for MEG analysis so far:
#https://www.spyder-ide.org/
#Once Spyder is installed, use the setup instructions on the MNE website to set the preferences for Spyder so that it uses the MNE interpreter: 
#https://mne.tools/stable/install/ides.html#ide-setup (basically, `Tools > Preferences > Python Interpreter > Use the following interpreter`)
#This should make all of the MNE packages available for import in Spyder. (If you use Pycharm, you also need to direct it to the python interpretor in mne... you can find out where that is by opening Prompt and looking at the "Using python..." line that opens in the terminal.)


#--------------
#1. MEG160 
#--------------
#Diogo has a copy shared here: https://drive.google.com/file/d/1rTvjU9tDBc0OaBCOZl5VifNYR5BDkY_A/view?usp=sharing

#It would be great to port the CALM algorithm this to MNE Python one day; Diogo may be working on this.

#1. Denoising: run CALM algorithm, use channels 208, 209, 210
#Edit -> Noise Reduction, save as -CALM.con

#2. Concatenate files for any subject that was multiple sessions
#File -> Offline  Operation -> Edit: File Concatenate

#NOTES on concatenating files:
#It may be possible to do the concatenation in MNE Python *before* adding headshape information.
#But I'd need to test the mne.io.read_raw_kit() function to make sure it doesn't mess anything up.
#I have also explored combining the files in MNE *after* adding the headshape information. It does not work yet. The attempts are in the "combining files.py" script.
#It is safest to do the concatenation in MEG160 for now.


#--------------
#2. Python: Delete dx dy dz columns from stylus points
#--------------
#These extra columns cause an error in kit2fiff if they are not removed

import os
import pandas as pd

#loop through participants

#quickly create a list of names that we will need in the loop
#uses the f-string syntax to pad the integer to 3 places

n=12 #number of participants
names = [ ] #initialize an empty list
for i in range(n):  #loop through and append each name to the list
    folder_name = "egy_sub_"+f'{i+1:03}'#for the path
    file_name = 'egyptian_sub'+f'{i+1:03}'+'_styluspoints' #the stylus file
    names.append((folder_name, file_name))


#Now we can loop through the names tuple, and access each of these names
for i,j in names:
    head_path = "/Users/jrs9906/Documents/MEG data/egyptian/raw_data/"+i+"/anat/digitized-headshape/"
    stylus_file = j+'.txt'
    
    #set working directory
    os.chdir(head_path)

    # make sure it worked
    os.getcwd()

    #read in the txt, make a copy to work on just in case
    fiducials = pd.read_csv(stylus_file, sep='\s+', skiprows=3, header=None) #the delimiter means whitespace

    #remove the last 3 columns
    fiducials_new=fiducials.drop(fiducials.columns[[3,4,5]], axis = 1)

    #write txt
    save_name = j+'_edited.txt'
    fiducials_new.to_csv(save_name, sep=' ', index=False, header=False)


#---------------
#3. Create a CSV file with the word counts for comparison
#---------------
"""
The code in "2. extracting event codes" requires a CSV file with columns 'trigger224'..'trigger231' (the first-word triggers),
columns 'trigger224w'..'trigger231w' (subsequent-word triggers),
and a 'wordcount' column telling how many words in this row. This can be made from the 
expriment script using this loop. All other columns will be kept in the file and ignored.
"""

#loop through participants

#quickly create a list of names that we will need in the loop
#uses the f-string syntax to pad the integer to 3 places
n=12 #number of participants
names = [ ] #initialize an empty list
for i in range(n):  #loop through and append each name to the list
    folder_name = "egy_sub_"+f'{i+1:03}'#for the path
    file_name = 'egyptian_list'+str(i+1) #the list
    names.append((folder_name, file_name))


#Now we can loop through the names tuple, and access each of these names
for i,j in names:
    list_path = "/Users/jrs9906/Documents/MEG data/egyptian/raw_data/"+i+"/derivatives/"
    list_file = j+'.csv'
    
    #set working directory
    os.chdir(list_path)

    # make sure it worked
    os.getcwd()

    #read in the CSV, make a copy to work on just in case
    materials = pd.read_csv(list_file, encoding='utf-8-sig') #need the encoding to preserve the Arabic
    wordcount_df = materials.copy()

    #split each sentence, count words, append to dataset as a new column
    wordcount_df['wordcount'] = materials['sentence'].str.split(" ").str.len()

    #write csv for safekeeping (automatically adds .csv)
    save_name = 'word_count_'+list_file
    wordcount_df.to_csv(
        save_name, 
        encoding='utf-8-sig', 
        index=False, 
        header=True,
    )


#--------------
#4. MNE kit2fiff
#--------------

#Use the GUI to add headshape information
#Use PROMPT from MNE Python installation
#type MNE kit2fiff and hit enter
#Takes 5 files: The data, the 2 marker files, headshape is called basicsurface in our files, and fiducials is called stylus points in our files
#Saves as .fif

#For participants that had 2 separate recording runs, use the 1st marker for the fisrt run and the 2nd marker for the 2nd run. This is a hack.
#Someday this might be done in MNE, and might use all of the markers.