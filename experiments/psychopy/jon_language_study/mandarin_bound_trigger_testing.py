import os, sys
import pandas as pd
from psychopy import core, visual, event, parallel, data, monitors, gui

from pypixxlib import _libdpx as dp
from utilities_original import *

from experiments.psychopy.general.trigger_test_psychopy_digital_out_combination import trigger_channels_dictionary
# Setup the connection with the Vpixx systems and disable Pixel Mode

dp.DPxOpen()
dp.DPxDisableDoutPixelMode()
dp.DPxWriteRegCache()

# Define the RGB code for each channel on the KIT machine and their name
trigger = [[4, 0, 0], [16, 0, 0], [64, 0, 0], [0, 1, 0], [0, 4, 0], [0, 16, 0], [0, 64, 0], [0, 0, 1]]
channel_names  = ['224', '225', '226', '227', '228', '229', '230', '231']
black = [0, 0, 0]

def RGB2Trigger(color):
    # helper function determines expected trigger from a given RGB 255 colour value
    # operates by converting individual colours into binary strings and stitching them together
    # and interpreting the result as an integer

    # return triggerVal
    return int((color[2] << 16) + (color[1] << 8) + color[0])  # dhk

# If you would like to combine the use of multiple channels at once for a trigger
# Define this dictionary
trigger_channels_dictionary = {
    224: 4,
    225: 16,
    226: 64,
    227: 256,
    228: 1024,
    229: 4096,
    230: 16384,
    231: 65536
}

# Responsebox

# When you need to use it add thisline
responses = [] # Add this at the beginning of your script
#Copy/Paste these two lines everytime the participant should input a button
#response = getbutton() #listen to a button
#responses.append(response) #everytime we get a response we add it to the table

# Save the responses in a variable responses = [] then responses.append(response) then save it to your .csv

SCREEN_NUMBER = 2
#Try 1 or 2 as screen_number
#SCREEN_NUMBER = 1

#os.chdir('/Users/jsprouse/Desktop')
trialList = data.importConditions('mandarin_bound.csv')
#trialList = data.importConditions('egyptian_backward_debugging.csv')

#mon = monitors.Monitor('BenQ24', width=53, distance=100)
#port = parallel.ParallelPort(address=0xD010)
clock = core.Clock()

backgroundColor = 'black'
instructionsFont = 'Arial'
#stimuliFont = 'Microsoft Sans Serif Regular' ######## change 1 (was Calibri)
stimuliFont = 'Microsoft YaHei'
stimuliColor = 'yellow'
stimuliUnits = 'deg'
stimuliSize = 2
wordOn = 12 ##### change 2 (was 18)
wordOff = 12
lastWordOn = 60

boxHeight = stimuliSize + 1.5
boxWidth = 11

longestWordCount = 0
longestWord = 'none'

totalTrials = len(trialList)
for trialIndex in range(totalTrials):
    words = trialList[trialIndex]['sentence'].split()
    for word in words:
        if len(word) > longestWordCount:
            longestWordCount = len(word)
            longestWord = word

print(longestWord)
print(longestWordCount)

fixationPoint = '****'
fixationOn = 60
fixationOff = wordOff
fixationColor = 'red'
fixationSize = stimuliSize
fixationUnits = stimuliUnits
fixationTrigger = 255

taskQuestionColor = 'red'
taskQuestionSize = 1.5
taskQuestionUnits = stimuliUnits
taskQuestionOff = wordOff

instructionColor = 'yellow'
instructionSize = 1
instructionUnits = stimuliUnits
instructionOff = wordOff

practiceCount = 10
breakKeyword = 'break'
breakColor = instructionColor
breakSize = instructionSize
breakUnits = instructionUnits
breakOff = wordOff

quitKey = 'escape'
#responseYes = 'j'
#responseNo = 'f'
#correctTrigger = 251
#incorrectTrigger = 250
startItem = 1

totalTrials = len(trialList)
totalQuestionCount = 0
totalBreakCount = 0

for trialIndex in range(totalTrials):
    if isinstance(trialList[trialIndex]['taskQuestion'], str) and len(trialList[trialIndex]['taskQuestion']) >= 4:
        totalQuestionCount += 1
    if trialList[trialIndex]['sentence'] == breakKeyword:
        totalBreakCount += 1

currentBreakCount = 0
totalCorrectResponses = 0
recentCorrectResponses = 0
trialsSinceLastBreak = 0

longestSentence = 0
for trialIndex in range(totalTrials):
    numWords = len(trialList[trialIndex]['sentence'].split())
    if numWords > longestSentence:
        longestSentence = numWords

subjectColumns = ['name', 'age', 'sex', 'handedness', 'experiment', 'list', 'sentence', 'taskQuestion', 'trigger', 'expectedAnswer', 'participantAnswer', 'answer']
wordColumns = ["word" + str(i) for i in range(1, longestSentence + 1)]
myColumns = subjectColumns + wordColumns
results = pd.DataFrame(index=range(totalTrials), columns=myColumns)

myDlg = gui.Dlg(title="RSVP EEG experiment", size=(600, 600))
myDlg.addText('Participant Info', color='Red')
myDlg.addField('Participant Name:', 'First Last', tip='or subject code')
myDlg.addField('Age:', 21)
myDlg.addField('Biological Sex:', choices=["Female", "Male"])
myDlg.addField('Handedness:', 100)
myDlg.addText('Experiment Info', color='Red')
myDlg.addField('Experiment Name:', 'Unacc.Passive')
myDlg.addField('Experiment List:', 1)
myDlg.show()

if myDlg.OK:
    participantInfo = myDlg.data
else:
    print('user cancelled')

win = visual.Window(screen =1, size=[1919, 1079], fullscr=False, color=backgroundColor, monitor='testMonitor')  # Set the border color to black)

stim = visual.TextStim(win, text='In this experiment, you will read sentences one word at a time.\n\nAfter each sentence is finished, you will be asked a Yes or No question about that sentence.\n\nAll you have to do is read the sentences normally, and then answer the question\n\nPress the YES key to see some examples.', font=instructionsFont, units=breakUnits, height=breakSize, color=instructionColor)
stim.setPos((0, 0))
stim.draw()
win.flip()

response = getbutton()  # listen to a button
responses.append(response)  # everytime we get a response we add it to the table

if responses[-1] == quitKey:
    participantName = participantInfo[0].replace(" ", "")
    filename = 'results.' + participantName + '.csv'
    results.to_csv(filename)
    win.close()
    core.quit()

for frameN in range(instructionOff - 1):
    win.flip()
win.flip()


# this is a loop on each trial
for trialIndex in range(startItem - 1, totalTrials):
    pauseResponse = []
    responses = []
    event.clearEvents()
    if trialList[trialIndex]['sentence'] == breakKeyword:
        event.clearEvents()
        currentBreakCount += 1
        completedTrials = trialIndex + 1 - practiceCount - currentBreakCount
        remainingTrials = (totalTrials - totalBreakCount - practiceCount) - completedTrials

        if currentBreakCount == 1:
            stim = visual.TextStim(win, text='Congratulations! You answered %i of the %i practice questions correctly.\n\nYou are now ready to do the actual experiment.\n\nThere are %i sentences to read.\n\nPlease sit still, stop blinking and press the YES key when you are ready for the first sentence.' % (recentCorrectResponses, trialsSinceLastBreak, remainingTrials), font=instructionsFont, units=breakUnits, height=breakSize, color=breakColor)
            totalCorrectResponses = 0
        else:
            stim = visual.TextStim(win, text='Please feel free to take a short break now if you would like.\n\nYou answered %i out of %i questions correctly since the last break.\n\nYou have completed %i sentences, and have %i to go.\n\nWhen you are ready for the next sentence, please sit still, stop blinking, and press the YES key.' % (recentCorrectResponses, trialsSinceLastBreak, completedTrials, remainingTrials), font=instructionsFont, units=breakUnits, height=breakSize, color=breakColor)
        stim.setPos((0, 0))
        stim.draw()
        win.flip()

        #pauseResponse = event.waitKeys(keyList=[responseYes, quitKey])
        response = getbutton()  # listen to a button
        responses.append(response)  # everytime we get a response we add it to the table

        if responses[-1] == quitKey:
            participantName = participantInfo[0].replace(" ", "")
            filename = 'results.' + participantName + '.csv'
            results.to_csv(filename)
            win.close()
            core.quit()

        trialsSinceLastBreak = 0
        recentCorrectResponses = 0

        results.loc[trialIndex, 'name'] = participantInfo[0]
        results.loc[trialIndex, 'age'] = participantInfo[1]
        results.loc[trialIndex, 'sex'] = participantInfo[2]
        results.loc[trialIndex, 'handedness'] = participantInfo[3]
        results.loc[trialIndex, 'experiment'] = participantInfo[4]
        results.loc[trialIndex, 'list'] = participantInfo[5]
        results.loc[trialIndex, 'sentence'] = 'break'

        for frameN in range(breakOff - 1):
            win.flip()
        win.flip()

        continue

    print(trialList[trialIndex]['sentence'])

    words = trialList[trialIndex]['sentence'].split()
    numWords = len(words)
    triggerList = range(int(trialList[trialIndex]['trigger']), int(trialList[trialIndex]['trigger']) + numWords)

    box = visual.Rect(win, width=boxWidth, height=boxHeight, units=fixationUnits)
    box.setPos((0, 0))
    box.setLineColor(fixationColor)
    box.setAutoDraw(True)

    for frameN in range(fixationOn):
        win.flip()
        if frameN == 0:
            clock.reset()
            #port.setData(fixationTrigger)
    win.flip()
    #port.setData(0)

    for frameN in range(fixationOff - 2):
        win.flip()
    win.flip()

    for wordIndex in range(numWords):
        print(repr(words[wordIndex]))
        if event.getKeys(quitKey):
            participantName = participantInfo[0].replace(" ", "")
            filename = 'results.' + participantName + '.csv'
            results.to_csv(filename)
            win.close()
            core.quit()

        stim = visual.TextStim(win, text=words[wordIndex], languageStyle='Arabic', ### change 3 (was not specified)
                               font=stimuliFont, units=stimuliUnits, height=stimuliSize, color=stimuliColor)
        stim.setPos((0, 0))

        if wordIndex == max(range(numWords)):
            for frameN in range(lastWordOn):
                stim.draw()
                win.flip()
                if frameN == 0:
                    clock.reset()
                    #port.setData(triggerList[wordIndex])
            win.flip()
            #port.setData(0)
            results.loc[trialIndex, wordIndex + len(subjectColumns)] = clock.getTime()
        else:
            for frameN in range(wordOn):
                stim.draw()
                win.flip() # First word appeared after this flip, this flip will occur wordOn number of times, so you only want to trigger at the first win.flip of this loop
                            # add code for trigger under condition (wordIndex==0 and frameN==0)
                if wordIndex == 0 and frameN == 0:
                    # Calculate the combined trigger value using the original method
                    combined_trigger_value = (
                            trialList[trialIndex]['trigger224'] * trigger_channels_dictionary[224] +
                            trialList[trialIndex]['trigger225'] * trigger_channels_dictionary[225] +
                            trialList[trialIndex]['trigger226'] * trigger_channels_dictionary[226] +
                            trialList[trialIndex]['trigger227'] * trigger_channels_dictionary[227] +
                            trialList[trialIndex]['trigger228'] * trigger_channels_dictionary[228] +
                            trialList[trialIndex]['trigger229'] * trigger_channels_dictionary[229] +
                            trialList[trialIndex]['trigger230'] * trigger_channels_dictionary[230] +
                            trialList[trialIndex]['trigger231'] * trigger_channels_dictionary[231]
                    )

                    # Debugging log: Print the calculated combined value
                    print(f"Trial {trialIndex}, Trigger: Combined Value = {combined_trigger_value}")

                    # Send the combined trigger to the hardware
                    dp.DPxSetDoutValue(combined_trigger_value, 0xFFFFFF)
                    dp.DPxUpdateRegCache()

                    # Briefly wait to register the trigger
                    core.wait(0.1)

                    # Reset the trigger to avoid lingering activation
                    dp.DPxSetDoutValue(RGB2Trigger(black), 0xFFFFFF)
                    dp.DPxUpdateRegCache()

                    # Log the trigger to the results for later validation
                    results.loc[trialIndex, 'trigger_value'] = combined_trigger_value

                    # Debugging log to confirm reset
                    print(f"Trigger for Trial {trialIndex} reset to black")

                if frameN == 0:
                    clock.reset()
                    #port.setData(triggerList[wordIndex])
            win.flip()
            #port.setData(0)
            results.loc[trialIndex, wordIndex + len(subjectColumns)] = clock.getTime()

        for frameN in range(wordOff - 2):
            win.flip()
        win.flip()

    box.setAutoDraw(False)


    if isinstance(trialList[trialIndex]['taskQuestion'], str) and len(trialList[trialIndex]['taskQuestion']) >= 4:
        event.clearEvents()
        stim = visual.TextStim(win, text=trialList[trialIndex]['taskQuestion'], font=instructionsFont, units=taskQuestionUnits, height=taskQuestionSize, color=taskQuestionColor)
        stim.setPos((0, 0))
        stim.draw()
        win.flip()

        #responses = event.waitKeys(keyList=[responseNo, responseYes, quitKey])
        response = getbutton()  # listen to a button
        responses.append(response)  # everytime we get a response we add it to the table

        if responses[-1] == quitKey:
            participantName = participantInfo[0].replace(" ", "")
            filename = 'results.' + participantName + '.csv'
            results.to_csv(filename)
            win.close()
            core.quit()

        if responses[-1] == trialList[trialIndex]['correctAnswer']:
            #port.setData(correctTrigger)
            recentCorrectResponses += 1
            totalCorrectResponses += 1
            answer = 1
        else:
            #port.setData(incorrectTrigger)
            answer = 0

        for frameN in range(taskQuestionOff - 1):
            win.flip()
        win.flip()

        trialsSinceLastBreak += 1

    results.loc[trialIndex, 'name'] = participantInfo[0]
    results.loc[trialIndex, 'age'] = participantInfo[1]
    results.loc[trialIndex, 'sex'] = participantInfo[2]
    results.loc[trialIndex, 'handedness'] = participantInfo[3]
    results.loc[trialIndex, 'experiment'] = participantInfo[4]
    results.loc[trialIndex, 'list'] = participantInfo[5]
    results.loc[trialIndex, 'sentence'] = trialList[trialIndex]['sentence']
    results.loc[trialIndex, 'taskQuestion'] = trialList[trialIndex]['taskQuestion']
    results.loc[trialIndex, 'trigger'] = trialList[trialIndex]['trigger']
    if isinstance(trialList[trialIndex]['taskQuestion'], str) and len(trialList[trialIndex]['taskQuestion']) >= 4:
        results.loc[trialIndex, 'expectedAnswer'] = trialList[trialIndex]['correctAnswer']
        results.loc[trialIndex, 'participantAnswer'] = responses[-1]
        results.loc[trialIndex, 'answer'] = answer
    else:
        results.loc[trialIndex, 'expectedAnswer'] = ''
        results.loc[trialIndex, 'participantAnswer'] = ''
        results.loc[trialIndex, 'answer'] = ''

    event.clearEvents()
    responses = []
    stim = visual.TextStim(win, text='You can blink now.\n\nWhen you are ready for the next sentence, sit still, stop blinking, and press the YES key.', font=instructionsFont, units=breakUnits, height=breakSize, color=stimuliColor)
    stim.setPos((0, 0))
    stim.draw()
    win.flip()

    #pauseResponse = event.waitKeys(keyList=[responseYes, quitKey])
    response = getbutton()  # listen to a button
    responses.append(response)  # everytime we get a response we add it to the table

    if responses[-1] == quitKey:
        participantName = participantInfo[0].replace(" ", "")
        filename = 'results.' + participantName + '.csv'
        results.to_csv(filename)
        win.close()
        core.quit()

    for frameN in range(taskQuestionOff - 1):
        win.flip()
    win.flip()

event.clearEvents()
stim = visual.TextStim(win, text='Congratulations, you are finished!\n\nYou read %i sentences, and answered %i out of %i questions correctly!\n\nThank you very much for your participation.\n\nPress any key to close this program.' % ((totalTrials - totalBreakCount - practiceCount), totalCorrectResponses, totalQuestionCount), font=instructionsFont, units=instructionUnits, height=instructionSize, color=instructionColor)
stim.setPos((0, 0))
stim.draw()
win.flip()

event.waitKeys()

participantName = participantInfo[0].replace(" ", "")
filename = 'results.' + participantName + '.csv'
results.to_csv(filename)

win.close()
core.quit()

dp.DPxClose()