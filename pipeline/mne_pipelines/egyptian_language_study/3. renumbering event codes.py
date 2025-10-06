##############################
#Edit the events file: Convert 1s (non-initial words) to sequential codes
##############################
"""
This assumes that you have an event codes file that was created in the previous step
This also requires knowing how many words are in each condition/event-code.
Finally, this can only deal with errors of +/-1 word from the expected length.
If the errors are more than that, the behavior will be odd.
(I will try to make this more robust in the future, but this is good enough for now.)
"""

#---------------
#Imports
#---------------
import os
import mne
import numpy as np
import copy

#---------------
#Define functions for replacing the 1s
#---------------

#Function 1: to rewrite the 1s for critical conditions (marks errors as 999+code)
#(had to add a check in the elif clause so that it doesn't run for the last sentence of the structure... not sure if this is the best way or not.)
def rewriteOnesCritical(n, eventCode): #n is the number of words for that condition, eventCode is the code we'd like to use
    penultWordIndex = i + n - 2  # critical words for finding errors
    lastWordIndex = i + n - 1
    nextTrialIndex = i + n
    if events[lastWordIndex, 2] > 1:  # Check if the sentence is 1 word too SHORT, given it an error number
        events[i:penultWordIndex + 1, 2] = int(str(999) + str(eventCode))
    elif (nextTrialIndex < len(events)) and (events[nextTrialIndex, 2] == 1):  # Check if the sentence is 1 word too LONG, give it an error numbers
        events[i:nextTrialIndex + 1, 2] = int(str(999) + str(eventCode))  # replace them all with 999+code
    else:  # the sentence is the correct length (or more than 1 word off?), so give sequential numbers
        for j in range(n):
            events[i + j, 2] = int(str(eventCode) + str(j + 1))

#Function 2: to rewrite 1s for the N400 conditions (these aren't marked as errors, they are corrected!)
#(had to add a check in the elif clause so that it doesn't run for the last sentence of the structure... not sure if this is the best way or not.)
def rewriteOnesN400(n, eventCode): #n is the number of words, #eventCode is the code we'd like to give the condition
    lastWordIndex = i + n - 1
    nextTrialIndex = i + n
    if events[lastWordIndex, 2] > 1:  # Check if the sentence is 1 word too SHORT
        for j in range(n - 1):
            events[i + j, 2] = int(str(eventCode-1000) + str(j + 1))
    elif (nextTrialIndex < len(events)) and (events[nextTrialIndex, 2] == 1):  # Check if the sentence is 1 word too LONG
        for j in range(n + 1):
            events[i + j, 2] = int(str(eventCode+1000) + str(j + 1))
    else:  # the sentence is the correct length (or more than 1 word off?)
        for j in range(n):
            events[i + j, 2] = int(str(eventCode) + str(j + 1))


#---------------
#Loop through all of the participants
#---------------

#create a list of folder and file names
n=12 #number of participants
names = [ ] #initialize an empty list
for i in range(n):  #loop through and append each name to the list
    folder_name = "egy_sub_"+f'{i+1:03}'#for the path
    file_name = 'egyptian_sub'+f'{i+1:03}' #the data file
    names.append((folder_name, file_name))


#Now we can loop through the names tuple, and access each of these names
for folder_name,file_name in names:

    #----------------
    #1. Set working directory, read in the file
    #----------------
    data_path = '/Users/jrs9906/Documents/MEG data/egyptian/raw_data/'+folder_name+'/meg-kit/'
    
    #set working directory
    os.chdir(data_path)
    
    # make sure it worked
    os.getcwd()
    
    #read in the file
    mne_events = mne.read_events(
        filename=file_name+'_events.eve', 
    )

    #make a copy of the events structure in case we need to go back to the original
    events = copy.deepcopy(mne_events)


    #----------------
    #2. Loop through the events and apply the functions
    #----------------
    """
    Thes require us to know the number of words for each condition
    """
    for i in range(0, len(events)):
        match events[i,2]:  #this goes through each possible event code
            case 136:  #cleft #9 words
                n = 9  # expected number of words
                eventCode = events[i, 2]
                rewriteOnesCritical(n, eventCode)
            case 132: #in-situ #9 words
                n = 9  # expected number of words
                eventCode = events[i, 2]
                rewriteOnesCritical(n, eventCode)
            case 129: #yn #9 words
                n = 9  # expected number of words
                eventCode = events[i, 2]
                rewriteOnesCritical(n, eventCode)
            case 34: #BA #8 words
                n = 8  # expected number of words
                eventCode = events[i, 2]
                rewriteOnesCritical(n, eventCode)
            case 33: #BA control #8 words
                n = 8  # expected number of words
                eventCode = events[i, 2]
                rewriteOnesCritical(n, eventCode)
            case 68: #BVA #7 words
                n = 7 #expected number of words
                eventCode = events[i, 2]
                rewriteOnesCritical(n, eventCode)
            case 66: #RA #6 words
                n = 6  # expected number of words
                eventCode = events[i, 2]
                rewriteOnesCritical(n, eventCode)
            case 65: #NP #7 words
                n = 7  # expected number of words
                eventCode = events[i, 2]
                rewriteOnesCritical(n, eventCode)
            case 4:  # NP #4 words
                n = 4  # expected number of words
                eventCode = 400  # event code that we are working on
                rewriteOnesN400(n, eventCode)
            case 5:  # NP #5 words
                n = 5  # expected number of words
                eventCode = 500  # event code that we are working on
                rewriteOnesN400(n, eventCode)
            case 6:  # NP #6 words
                n = 6  # expected number of words
                eventCode = 600  # event code that we are working on
                rewriteOnesN400(n, eventCode)
            case 7:  # NP #7 words
                n = 7  # expected number of words
                eventCode = 700  # event code that we are working on
                rewriteOnesN400(n, eventCode)
            case 20:  # NP #4 words
                n = 4  # expected number of words
                eventCode = 410  # event code that we are working on
                rewriteOnesN400(n, eventCode)
            case 21:  # NP #5 words
                n = 5  # expected number of words
                eventCode = 510  # event code that we are working on
                rewriteOnesN400(n, eventCode)
            case 22:  # NP #6 words
                n = 6  # expected number of words
                eventCode = 610  # event code that we are working on
                rewriteOnesN400(n, eventCode)
            case 23:  # NP #7 words
                n = 7  # expected number of words
                eventCode = 710  # event code that we are working on
                rewriteOnesN400(n, eventCode)

    #----------------
    #3. Some data checks
    #----------------

    #check to see if there are any 1s left, should be empty
    index1 = np.where(events[:,2] == 1)
    
    #check to see if the sentences that should be marked with an error code are there
    indexErrors = np.where(events[:,2] >99900)

    #----------------
    #4. Save the events file
    #----------------

    mne.write_events(
        filename=file_name+'_events_edited.eve', 
        events=events, 
        overwrite=True, 
        verbose=None,
    )
