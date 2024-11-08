##############################################################################################################
#A script for RAPID SERIAL VISUAL PRESENTATION in EEG using PsychoPy
#Jon Sprouse, jon.sprouse@uconn.edu
#Version 1 - 10/14
##############################################################################################################

###############################################################################
#Requirements:
#PsychoPy, of course
#A parallel port (otherwise the trigger calls will fail). If you don't have a parallel port on your debugging computer, comment out the trigger lines.
#A CSV file for the materials.
#The materials.csv file should have four columns with following labels: sentence, trigger, taskQuestion, correctAnswer.
#Each row in the materials.csv file is a trial (a sentence + task Question)
#The sentence column should contain the sentences for the experiment.
#The sentences should appear in the order that you want them presentend (going down the column) (there is no randomization in this code, yet)
#The sentences should be typed normally in the cell. The code will break them into separate words (based on the spaces).
#The sentence column should also contain the word "break" (no quotes) wherever you want to offer the participant a break.
#There must be a "break" between the last practice item and the first target item.
#The trigger column should contain the trigger number for the first word of each sentence. The code will automatically generate sequential trigger numbers for each successive word.
#The taskQuestion column should contain the question/task that will be presented after each sentence.
#The correctAnswer column should contain the keyboard key stroke that is the correct answer for each taskQuestion
#The code sends a trigger 
#An example file should be available with this script
#The script will save a results file to the working directory on quit/escape/exit
###############################################################################

###############################################################################
#Features to implement
    #Use trialhandler? Right now, I am storing everything using python
    #Make things more pythonic? Right now, I am not really using any dictionaries, and very little list comprehension stuff
    #Figure out how to make an escape code snippet that doesn't need to be placed in every loop --- one per experiment would be cleaner (and easier to update)
    #Figure out how to deal with the mismatches in python counting (0) versus human counting (1).... everything works, but it feels inelegant



#################################################
#####Import some information#####################
#################################################

#import modules
import os, sys, pandas, csv
from psychopy import core, visual, event, parallel, data, monitors, gui

#change the working directory to the path with the materials.csv file
os.chdir('/Users/jsprouse/Desktop')


#read in the data
trialList=data.importConditions('test.materials.csv')

###################################################
#####Set some hardware properties##################
###################################################

#Have you saved the settings of your monitor in psychopy's monitor center? If so, give its name here. This allows you to use visual degrees for the font size.
mon=monitors.Monitor('BenQ24', width=53, distance=100)  

#If you haven't, you should do it. Monitor Center is under tools in the menu. Or you could use the psychopy.monitors class to define it in the script. Like this:
#mon=monitors.Monitor('test monitor', width=59.6, distance=62)  #Jon's office
#mon=monitors.Monitor('test monitor', width=52, distance=80)    #EEG lab
#mon=monitors.Monitor('test monitor', width=52, distance=66)    #laptop
#mon.setSizePix([2560,1440])
#mon.setSizePix([1920,1200])
#mon.setSizePix([1440,900])

#Set the parallel port address (comment it out if you are debugging on a computer without a parallel port)
port = parallel.ParallelPort(address=0xD010)
clock = core.Clock()        #this can be useful if you want to time things; the current script does not.

        
#############################################################################   
###Set all of the user-definable properties of the experiment ###############
#############################################################################

###PROPERTIES OF THE WINDOW#################

#size of window (don't use full screen while debugging the script; but you probably want to use it for the experiment itself)
#You may even want to replace this in the script below with fullscr=True
#windowSize=[1920,1080]

#background color
backgroundColor='black'

###PROPERTIES OF THE RSVP WORD STIMULI################# 

#font of the stimuli
stimuliFont='Calibri'

#font color of stimuli
stimuliColor='yellow'

#units for stimulus font (recommend visual degree or cm so that it is constant, but this requires you to save information about your monitor in monitor center or a .monitor object)
stimuliUnits='deg'

#size of font for stimulus (this is actually height, width is determined by the font) ##change to height? ##add a font choice to the list?
stimuliSize=2

#RSVP word presentation time in frames (16.67ms per frame)
wordOn=18

#RSVP word off time (ISI) in frames
wordOff=12

#RSVP time for the last word in a sentence
lastWordOn=60

###PROPERTIES OF THE FIXATION BOX AND FIXATION POINT#################   

#height of the fixation box
boxHeight=stimuliSize+.5

#width of the fixation box
#This will depend on the longest word in your experiment, the height of your font, and your font choice
boxWidth=11      

#Here is a code snippet that will find the longest word in the experiment
longestWordCount=0
longestWord='none'

totalTrials=len(trialList)

for trialIndex in range(totalTrials):
    #split the sentence into words
    words = trialList[trialIndex]['sentence'].split()
    
    for wordIndex in range(len(words)):
        wordLength=len(words[wordIndex])    
        if wordLength > longestWordCount:
            longestWordCount = wordLength
            longestWord = words[wordIndex]

print longestWord
print longestWordCount

#From this, it may be possible to automatically choose the correct boxwidth??? (but it will be complicated)


#fixation point (this should be a string, such as '*' or '****', but isn't strictly necessary with the box outline)
fixationPoint='****'

#fixation presentaiton time in frames (default is identical to the RSVP word)
fixationOn=60

#fixation off time in frames (default is identical to the RSVP word)
fixationOff=wordOff

#fixation font color (default is identical to the RSVP word)
fixationColor='red'

#Size of the fixation point (default is the same as RSVP word stimuli)
fixationSize=stimuliSize

#Units of the fixation point (default is the same as RSVP word stimuli)
fixationUnits=stimuliUnits

#fixation trigger code (for segmenting the data later)
fixationTrigger=255

###PROPERTIES OF THE TASK QUESTION################# 

#set color for the taskQuestion
taskQuestionColor='red'

#Size of the taskQuestion (probably needs to be smaller than the stimuli size, but perhaps the same?)
taskQuestionSize=1.5

#Units of the taskQuestion (recommend same as the stimuliSize)
taskQuestionUnits=stimuliUnits

#in this version, the taskQuestion remains on until there is a button press

#set the number of frames between the offset of the task question and the onset of the next fixation (recommend it is identical to wordOff:
taskQuestionOff=wordOff

###PROPERTIES OF THE INSTRUCTIONS AND THANK YOU MESSAGE#################    

#set the font color for the instructions
instructionColor='yellow'

#Size of the instructions (probably needs to be smaller than the stimuliSize, but perhaps the same?)
instructionSize=1

#Units of the taskQuestion (recommend same as the stimuliSize)
instructionUnits=stimuliUnits

#set the number of frames between the offset of the instructions and the onset of the first fixation (recommend it is identical to wordOff):
instructionOff=wordOff

#in this version, the instructions stay on until there is a button press

###PROPERTIES OF THE PRACTICE ITEMS#################    
#Place your practice items in the materials.csv file as the first items
#Place a break after the practice items. The script will recognize the first break as the end of the practice, and post the end-of-practice message
#For every other break, it will show the typical break text

#How many practice items are there?
practiceCount=10            #This is just so we can get an accurate count of items, and tell the participants how many items are remaining

###PROPERTIES OF THE BREAK TEXT#################    

#What word are you using in the material.csv to indicate a break?
breakKeyword='break'

#set the font color for the breaks (recommend same as instructions)
breakColor=instructionColor

#Size of the break font (recommend the same as the instructions)
breakSize=instructionSize

#Units of the break font (recommend same as the instructions)
breakUnits=instructionUnits

#set the number of frames between the offset of the break and the onset of the next fixation (recommend it is identical to wordOff):
breakOff=wordOff

#in this version, the breaks stay on until the user presses a button

###PROPERTIES OF RESPONSES###############

#Which key should quit the program?
quitKey='escape'

#Which keys should be the yes and no response keys
responseYes='j'
responseNo='f'

#Which trigger codes should the script send to the amp for each response type?
correctTrigger=251
incorrectTrigger=250

###WHICH ITEM DO YOU WANT TO START WITH?###
startItem=1     #This is human counting. Python actually starts with 0. This is difference is accounted for in the loops below by subtracting one. 

####################################################################
###SOME MINOR HOUSE-KEEPING - nothing for you to do here############
####################################################################

#count the number of trials (this is critical to the script)
totalTrials=len(trialList)

#count the number of comprehension questions in the experiment (this isn't critical; it just allows us to report progress to the participants
totalQuestionCount=0
for trialIndex in range(totalTrials):
    if (isinstance(trialList[trialIndex]['taskQuestion'],basestring) and len(trialList[trialIndex]['taskQuestion'])>=4):    #this checks to see if there is a task question or not
        totalQuestionCount=totalQuestionCount+1
    #when this loop ends, totalQuestionCount should be correct

#count the number of breaks in the experiment (this isn't critical; it just allows us to report progress to the participants
totalBreakCount=0
for trialIndex in range(totalTrials):
    if trialList[trialIndex]['sentence']=='break':
        totalBreakCount=totalBreakCount+1
    #when this loop ends, totalBreakCount should be correct

#create a counter for the pauses as they are encountered (again, just to allow us to report progress to the participants)
currentBreakCount=0

#create counters for correct responses so you can tell participants how they are doing
totalCorrectResponses=0         #Just in case you want to tell them the total at the end of the experiment
recentCorrectResponses=0        #So you can tell them the total for the current segment of the experiment
trialsSinceLastBreak=0

#create a dataframe to store results from the experiment
#Step 1: figure out how long the longest sentence is
longestSentence=0
for trialIndex in range(totalTrials):
    #split the sentence into words
    words = trialList[trialIndex]['sentence'].split()

    #count the number of words in the list
    #use the len() function
    numWords = len(words)
    
    #compare to current longestSentence
    if numWords > longestSentence:
        longestSentence=numWords

#Step 2: create column names for each of the words in the sentences
subjectColumns=['name','age','sex','handedness','experiment','list','sentence','taskQuestion','trigger','expectedAnswer','participantAnswer','answer']
wordColumns=["word"+str(i) for i in range(1,longestSentence+1)]
myColumns=[subjectColumns,wordColumns]
myColumns=[item for sublist in myColumns for item in sublist]


#Step 3: create the dataframe with 11 columns for partcipant/experiment info, followed by one column for each word presentation time:     
results=pandas.DataFrame(index=range(totalTrials),columns=myColumns)


###############################################
#####START THE EXPERIMENT######################
###############################################

###OPEN A DIALOG BOX TO COLLECT SUBJECT INFO###
#Cannot currently change the size of the text boxes. There are modifications to psychopy out there to do it, but I am sticking with core functionality for this script.
myDlg = gui.Dlg(title="RSVP EEG experiment", size=(600,600))
myDlg.addText('Participant Info', color='Red')
myDlg.addField('Participant Name:', 'First Last', tip='or subject code')
myDlg.addField('Age:', 21)
myDlg.addField('Biological Sex:', choices=["Female","Male"])
myDlg.addField('Handedness:', 100)
myDlg.addText('Experiment Info', color='Red')
myDlg.addField('Experiment Name:', 'Unacc.Passive')
myDlg.addField('Experiment List:', 1)


myDlg.show()#you have to call show() for a Dlg (it gets done implicitly by a DlgFromDict)
if myDlg.OK:
    participantInfo = myDlg.data1 #this will be a list of data returned from each field added in order; it used later
else: print 'user cancelled'

###INTIALIZE THE DISPLAY###
#win = visual.Window(size=windowSize, color=backgroundColor, monitor=mon)
win = visual.Window(size=[1920,1080], fullscr=True, color=backgroundColor, monitor=mon)

###PRESENT INSTRUCTIONS###
stim = visual.TextStim(win, text='In this experiment you will read sentences one word at a time. \n \nAfter each sentence is finished, you will be asked a Yes or No question about that sentence. \n \nAll you have to do is read the sentences normally, and then answer the question \n \nPress the YES key to see some examples.', font=stimuliFont, units=breakUnits, height=breakSize, color=instructionColor)
stim.setPos((0,0))
stim.draw()                 #draw stim to buffer
win.flip()                  #draw to monitor
    
#wait for response before continuing
pauseResponse=event.waitKeys(keyList=[responseYes,quitKey])
        
if pauseResponse[-1]==quitKey:
    #write the results to a csv file
    participantName=participantInfo[0].replace(" ","")     #Take the space out of the participant's name, for file nameing below

    filename='results.'+participantName+'.csv'      #make a filename that is results.FirstLast.csv
    results.to_csv(filename)                        #write to csv

    win.close()
    core.quit()

#draw blank for the number of frames specified in instructionsOff minus 1. We subtract 1 because there is one win.flip below
for frameN in range(instructionOff-1):
    win.flip()                  #draw to monitor
win.flip()                      # Show blank screen        
        
###LOOP THROUGH THE PRACTICE ITEMS AND THE EXPERIMENTAL TRIALS###
for trialIndex in range(startItem-1, totalTrials):
    pauseResponse=[];
    responses=[];
    event.clearEvents();
    ###check to see if there is a break scheduled here###
    if trialList[trialIndex]['sentence'] == breakKeyword:
        event.clearEvents();
        #increment pauseCount and calculate how many items have been completed, and how many are left to go
        currentBreakCount=currentBreakCount+1
        completedTrials=trialIndex+1-practiceCount-currentBreakCount
        remainingTrials=(totalTrials-totalBreakCount-practiceCount)-completedTrials
        
        if currentBreakCount==1:
            stim = visual.TextStim(win, text='Congratulations! You answered %i of the %i practice questions correctly. \n \nYou are now ready to do the actual experiment. \n \nThere are %i sentences to read. \n \nPlease sit still, stop blinking and press the YES key when you are ready for the first sentence.' %(recentCorrectResponses, trialsSinceLastBreak, remainingTrials), font=stimuliFont, units=breakUnits, height=breakSize, color=breakColor)
            totalCorrectResponses=0         #this resets the counter so that practice items don't count as correct responses
        else:
            stim = visual.TextStim(win, text='Please feel free to take a short break now if you would like. \n \nYou answered %i out of %i questions correctly since the last break. \n \nYou have completed %i sentences, and have %i to go. \n \nWhen you are ready for the next sentence, please sit still, stop blinking, and press the YES key.' %(recentCorrectResponses, trialsSinceLastBreak, completedTrials, remainingTrials), font=stimuliFont, units=breakUnits, height=breakSize, color=breakColor)
        stim.setPos((0,0))
        stim.draw()                 #draw stim to buffer
        win.flip()                  #draw to monitor
    
        #wait for response before continuing
        pauseResponse=event.waitKeys(keyList=[responseYes,quitKey])
        
        if pauseResponse[-1]==quitKey:
            #write the results to a csv file
            participantName=participantInfo[0].replace(" ","")     #Take the space out of the participant's name, for file nameing below

            filename='results.'+participantName+'.csv'      #make a filename that is results.FirstLast.csv
            results.to_csv(filename)                        #write to csv
            
            win.close()
            core.quit()
        
        trialsSinceLastBreak=0
        recentCorrectResponses=0
        
        results.ix[trialIndex,'name']=participantInfo[0]
        results.ix[trialIndex,'age']=participantInfo[1]
        results.ix[trialIndex,'sex']=participantInfo[2]
        results.ix[trialIndex,'handedness']=participantInfo[3]
        results.ix[trialIndex,'experiment']=participantInfo[4]
        results.ix[trialIndex,'list']=participantInfo[5]
        results.ix[trialIndex,'sentence']='break'
        
        #draw blank for the number of frames specified in breakOff minus 1. We subtract 1 because there is one win.flip below
        for frameN in range(breakOff-1):
            win.flip()                  #draw to monitor
        win.flip()                      # Show blank screen
        
        continue    #this should end this loop iteration early, and move on...
  
    ###print the entire sentence to the shell, just so you have a log somewhere of what has been presented###  
    print trialList[trialIndex]['sentence']     
    
    #split the sentence into words
    words = trialList[trialIndex]['sentence'].split()

    #count the number of words in the list
    #use the len() function
    numWords = int(len(words))
    
    #create a sequence of trigger numbers starting with the trigger given in the row, and ending with the number of words
    triggerList=range(int(trialList[trialIndex]['trigger']), int(trialList[trialIndex]['trigger'])+numWords)
    
    #dispaly a fixation box (the commented out lines add a text fixation inside the box; not necessary)
    #stim = visual.TextStim(win, text=fixationPoint, font=stimuliFont, units=fixationUnits, height=fixationSize, color=fixationColor)
    #stim.setPos((0,0)) 
    box=visual.Rect(win, width=boxWidth, height=boxHeight, units=fixationUnits) 
    box.setPos((0,0))
    box.setLineColor(fixationColor)
    box.setAutoDraw(True)    #make the box draw in every win.flip from here until this is turned off
    
    ###draw the fixation point###
    for frameN in range(fixationOn):
        #stim.draw()                 #draw stim to buffer - only necessary if you have a text stimulus you want to use in addition to the box
        win.flip()                  #draw to monitor
        if frameN == 0:             # For first frame, just after stimulus appears on monitor
            clock.reset()           # Set clock time to zero
            port.setData(fixationTrigger)   # Start trigger
    win.flip()                      # Show blank screen
    port.setData(0)                 # Stop trigger  

    #draw blank for the number of frames specified in fixationOff minus 2. We subtract 2 because there is one win.flip above and one win.flip below
    for frameN in range(fixationOff-2):
        win.flip()                  #draw to monitor
        #if frameN == 0:             # For first frame, just after stimulus appears on monitor
            #clock.reset()           # Set clock time to zero
    win.flip()                      # Show blank screen
    
    ###Present each word using RSVP###
    for wordIndex in range(numWords):
        
        
        #press ESC to quit
        if event.getKeys(quitKey):
            #write the results to a csv file
            participantName=participantInfo[0].replace(" ","")     #Take the space out of the participant's name, for file nameing below

            filename='results.'+participantName+'.csv'      #make a filename that is results.FirstLast.csv
            results.to_csv(filename)                        #write to csv
            
            win.close()
            core.quit()
            
        #present the word in the words that corresponds to wordIndex
        #initialize the stimulus before presentation
        stim = visual.TextStim(win, text=words[wordIndex], font=stimuliFont, units=stimuliUnits, height=stimuliSize, color=stimuliColor)
        stim.setPos((0,0))
    
    #draw text stim for the number of frames specified by wordOn
        
        if wordIndex == max(range(numWords)):
            for frameN in range(lastWordOn):
                stim.draw()                 #draw stim to buffer
                win.flip()                  #draw to monitor
                if frameN == 0:             # For first frame, just after stimulus appears on monitor
                    clock.reset()           # Set clock time to zero
                    port.setData(triggerList[wordIndex])   # Start trigger, send the trigger for the word we are on
            win.flip()                      # Show blank screen
            port.setData(0)                 # Stop trigger  
            results.ix[trialIndex, (wordIndex+(len(subjectColumns)))]=clock.getTime()    #the complicated column index automatically calculates the first word-time column index
        
        else:
            for frameN in range(wordOn):
                stim.draw()                 #draw stim to buffer
                win.flip()                  #draw to monitor
                if frameN == 0:             # For first frame, just after stimulus appears on monitor
                    clock.reset()           # Set clock time to zero
                    port.setData(triggerList[wordIndex])   # Start trigger, send the trigger for the word we are on
            win.flip()                      # Show blank screen
            port.setData(0)                 # Stop trigger  
            results.ix[trialIndex, (wordIndex+(len(subjectColumns)))]=clock.getTime()    #the complicated column index automatically calculates the first word-time column index
        
        #draw blank for the number of frames specified in wordOff minus 2. We subtract 2 because there is one win.flip above and one win.flip below
        for frameN in range(wordOff-2):
            win.flip()                  #draw to monitor
        win.flip()                      # Show blank screen

    box.setAutoDraw(False)        #turn off the autoDraw of the box
    
    ###Present the taskQuestion###  
    
    if (isinstance(trialList[trialIndex]['taskQuestion'],basestring) and len(trialList[trialIndex]['taskQuestion'])>=4):    #this checks to see if there is a task question or not
        event.clearEvents();
        stim = visual.TextStim(win, text=trialList[trialIndex]['taskQuestion'], font=stimuliFont, units=taskQuestionUnits, height=taskQuestionSize, color=taskQuestionColor)
        stim.setPos((0,0))
        stim.draw()                 #draw stim to buffer
        win.flip()                  #draw to monitor

        #wait for response
        responses=event.waitKeys(keyList=[responseNo,responseYes,quitKey])
    
        #quit if ESC is pressed
        if responses[-1]==quitKey:
            #write the results to a csv file
            participantName=participantInfo[0].replace(" ","")     #Take the space out of the participant's name, for file nameing below

            filename='results.'+participantName+'.csv'      #make a filename that is results.FirstLast.csv
            results.to_csv(filename)                        #write to csv

            win.close()
            core.quit()
        
        #send a trigger 
        if responses[-1]==trialList[trialIndex]['correctAnswer']:       #answer is correct
            port.setData(correctTrigger)
            recentCorrectResponses=recentCorrectResponses+1
            totalCorrectResponses=totalCorrectResponses+1
            answer=1
    
        else: 
            port.setData(incorrectTrigger)          #answer is incorrect
            answer=0
    
        #draw blank for the number of frames specified in taskOff minus 1. We subtract 1 because there is one win.flip below
        for frameN in range(taskQuestionOff-1):
            win.flip()                  #draw to monitor
        win.flip()                      # Show blank screen
        
        trialsSinceLastBreak=trialsSinceLastBreak+1     #This only increments if there was a question
    
    #enter the information into the data structure
    results.ix[trialIndex,'name']=participantInfo[0]
    results.ix[trialIndex,'age']=participantInfo[1]
    results.ix[trialIndex,'sex']=participantInfo[2]
    results.ix[trialIndex,'handedness']=participantInfo[3]
    results.ix[trialIndex,'experiment']=participantInfo[4]
    results.ix[trialIndex,'list']=participantInfo[5]
    results.ix[trialIndex,'sentence']=trialList[trialIndex]['sentence']
    results.ix[trialIndex,'taskQuestion']=trialList[trialIndex]['taskQuestion']
    results.ix[trialIndex,'trigger']=trialList[trialIndex]['trigger']
    if (isinstance(trialList[trialIndex]['taskQuestion'],basestring) and len(trialList[trialIndex]['taskQuestion'])>=4):
        results.ix[trialIndex,'expectedAnswer']=trialList[trialIndex]['correctAnswer']
        results.ix[trialIndex,'participantAnswer']=responses[-1]
        results.ix[trialIndex,'answer']=answer #this is set in the response if/else above
    else: 
        results.ix[trialIndex,'expectedAnswer']=''
        results.ix[trialIndex,'participantAnswer']=''
        results.ix[trialIndex,'answer']=''
    
    #Print the you can blink message and wait for them to press a key - this happens on every trial
    event.clearEvents();
    stim = visual.TextStim(win, text='You can blink now. \n \nWhen you are ready for the next sentence, sit still, stop blinking, and press the YES key.', font=stimuliFont, units=breakUnits, height=breakSize, color=stimuliColor)
    stim.setPos((0,0))
    stim.draw()                 #draw stim to buffer
    win.flip()                  #draw to monitor
    
    #wait for response before continuing
    pauseResponse=event.waitKeys(keyList=[responseYes,quitKey])
    
    if pauseResponse[-1]==quitKey:
        #write the results to a csv file
        participantName=participantInfo[0].replace(" ","")     #Take the space out of the participant's name, for file nameing below

        filename='results.'+participantName+'.csv'      #make a filename that is results.FirstLast.csv
        results.to_csv(filename)                        #write to csv
            
        win.close()
        core.quit()
    
     
    #draw blank for the number of frames specified in taskOff minus 1. We subtract 1 because there is one win.flip below
    for frameN in range(taskQuestionOff-1):
        win.flip()                  #draw to monitor
    win.flip()                      # Show blank screen                           
                                                                                        
#End the SENTENCE LOOP
    

###THANK THE PARTICIPANT AND CLOSE THE PROGRAM###
event.clearEvents();
stim = visual.TextStim(win, text='Congratulations, you are finished! \n \nYou read %i sentences, and answered %i out of %i questions correctly! \n \nThank you very much for your participation. \n \nPress any key to close this program.'%((totalTrials-totalBreakCount-practiceCount), totalCorrectResponses, totalQuestionCount), font=stimuliFont, units=instructionUnits, height=instructionSize, color=instructionColor)
stim.setPos((0,0))  
stim.draw()                 #draw stim to buffer
win.flip()                  #draw to monitor

        
#wait for response before continuing
event.waitKeys()

#write the results to a csv file
participantName=participantInfo[0].replace(" ","")     #Take the space out of the participant's name, for file nameing below

filename='results.'+participantName+'.csv'      #make a filename that is results.FirstLast.csv
results.to_csv(filename)                        #write to csv

win.close()
core.quit()




