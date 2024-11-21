import os, sys
import pandas as pd
from psychopy import core, visual, event, parallel, data, monitors, gui

from pypixxlib import _libdpx as dp
from utilities import *

dp.DPxOpen()
dp.DPxDisableDoutPixelMode()
dp.DPxWriteRegCache()

# KIT MEG Channels triggered via Pixel Model by setting top left pixel to a specific color
trigger = [[4, 0, 0], [16, 0, 0], [64, 0, 0], [0, 1, 0], [0, 4, 0], [0, 16, 0], [0, 64, 0], [0, 0, 1]]
channel_names  = ['224', '225', '226', '227', '228', '229', '230', '231']
black = [0, 0, 0]

def RGB2Trigger(color):
    # helper function determines expected trigger from a given RGB 255 colour value
    return int((color[2] << 16) + (color[1] << 8) + color[0])  # dhk

# Define this dictionary to map channel numbers to RGB codes for triggers
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

for i in range(8):
    dp.DPxSetDoutValue(trigger_channels_dictionary[224+i], 0xFFFFFF)
    dp.DPxUpdateRegCache()
    dp.DPxSetDoutValue(RGB2Trigger(black), 0xFFFFFF)
    dp.DPxUpdateRegCache()
    core.wait(1)  ## Adjusted timing

# Screen and experiment settings
SCREEN_NUMBER = 2
trialList = data.importConditions('egyptian_backward.csv')  # Load trial list (CSV file)
clock = core.Clock()

# Additional settings (colors, sizes, etc.)
backgroundColor = 'black'
stimuliFont = 'Arial'
stimuliColor = 'yellow'
stimuliUnits = 'deg'
stimuliSize = 2
wordOn = 5
wordOff = 5
lastWordOn = 5

# Result storage
subjectColumns = ['name', 'age', 'sex', 'handedness', 'experiment', 'list', 'sentence', 'taskQuestion', 'trigger',
                  'expectedAnswer', 'participantAnswer', 'answer']
results = pd.DataFrame(index=range(len(trialList)), columns=subjectColumns)

# Dialog to gather participant info
myDlg = gui.Dlg(title="RSVP EEG experiment", size=(600, 600))
myDlg.addText('Participant Info', color='Red')
myDlg.addField('Participant Name:', 'First Last')
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

win = visual.Window(screen=1, size=[1910, 1070], fullscr=False, color=backgroundColor, monitor='testMonitor')

# Instructions display
stim = visual.TextStim(win, text='In this experiment, you will read sentences one word at a time.\n\nAfter each sentence is finished, you will be asked a Yes or No question about that sentence.\n\nPress the YES key to see some examples.', font=stimuliFont, units='deg', height=2, color='yellow')
stim.setPos((0, 0))
stim.draw()
win.flip()

pauseResponse = event.waitKeys(keyList=['j', 'escape'])

if pauseResponse[-1] == 'escape':
    filename = f'results.{participantInfo[0].replace(" ", "")}.csv'
    results.to_csv(filename)
    win.close()
    core.quit()

# Start the experiment
for trialIndex in range(len(trialList)):
    trial = trialList[trialIndex]
    sentence = trial['sentence']
    trigger_value = trial['trigger']
    words = sentence.split()
    numWords = len(words)
    triggerList = [trigger_value] * numWords  # Trigger is applied for the whole sentence

    # Create the box for word display
    box = visual.Rect(win, width=11, height=stimuliSize + 1, units='deg')
    box.setPos((0, 0))
    box.setLineColor('red')
    box.setAutoDraw(True)

    # Fixation point before the sentence starts
    for frameN in range(60):  # 1 second fixation
        win.flip()

    for wordIndex in range(numWords):
        if event.getKeys(keyList=['escape']):
            filename = f'results.{participantInfo[0].replace(" ", "")}.csv'
            results.to_csv(filename)
            win.close()
            core.quit()

        stim = visual.TextStim(win, text=words[wordIndex], font=stimuliFont, units='deg', height=stimuliSize, color=stimuliColor)
        stim.setPos((0, 0))

        # Send trigger for each word (only once when the word is shown)
        for frameN in range(wordOn):
            stim.draw()
            win.flip()
            if frameN == 0:
                clock.reset()
                dp.DPxSetDoutValue(trigger_channels_dictionary[224 + i], 0xFFFFFF)  # Use the trigger based on the sentence trigger
                dp.DPxUpdateRegCache()


        win.flip()
        dp.DPxSetDoutValue(RGB2Trigger(black), 0xFFFFFF)  # Clear the trigger after displaying the word
        dp.DPxUpdateRegCache()

        results.loc[trialIndex, 'name'] = participantInfo[0]
        results.loc[trialIndex, 'sentence'] = trial['sentence']
        results.loc[trialIndex, 'trigger'] = trigger_value

        for frameN in range(wordOff - 2):
            win.flip()
        win.flip()

    box.setAutoDraw(False)

    # Task question section (if present)
    if isinstance(trial['taskQuestion'], str) and len(trial['taskQuestion']) >= 4:
        stim = visual.TextStim(win, text=trial['taskQuestion'], font=stimuliFont, units='deg', height=1.5, color='red')
        stim.setPos((0, 0))
        stim.draw()
        win.flip()

        responses = event.waitKeys(keyList=['f', 'j', 'escape'])

        if responses[-1] == 'escape':
            filename = f'results.{participantInfo[0].replace(" ", "")}.csv'
            results.to_csv(filename)
            win.close()
            core.quit()

        if responses[-1] == trial['correctAnswer']:
            recentCorrectResponses += 1
            totalCorrectResponses += 1
            answer = 1
        else:
            answer = 0

        results.loc[trialIndex, 'expectedAnswer'] = trial['correctAnswer']
        results.loc[trialIndex, 'participantAnswer'] = responses[-1]
        results.loc[trialIndex, 'answer'] = answer

        for frameN in range(5):  # Display time for task question
            win.flip()
        win.flip()

# End of experiment
stim = visual.TextStim(win, text='Congratulations, you are finished! Press any key to close this program.')
stim.setPos((0, 0))
stim.draw()
win.flip()
event.waitKeys()

filename = f'results.{participantInfo[0].replace(" ", "")}.csv'
results.to_csv(filename)

win.close()
core.quit()

dp.DPxClose()
