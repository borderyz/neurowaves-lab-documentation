import os, sys
import pandas as pd
from psychopy import core, visual, event, parallel, data, monitors, gui

#os.chdir('/Users/jsprouse/Desktop')
trialList = data.importConditions('egyptian_backward.csv')

#mon = monitors.Monitor('BenQ24', width=53, distance=100)
#port = parallel.ParallelPort(address=0xD010)
clock = core.Clock()

backgroundColor = 'black'
stimuliFont = 'Arial'
stimuliColor = 'yellow'
stimuliUnits = 'deg'
stimuliSize = 2
wordOn = 30
wordOff = 12
lastWordOn = 60

boxHeight = stimuliSize + 1
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
responseYes = 'j'
responseNo = 'f'
correctTrigger = 251
incorrectTrigger = 250
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

win = visual.Window(size=[1910, 1070], fullscr=False, color=backgroundColor, monitor='testMonitor')

stim = visual.TextStim(win, text='In this experiment, you will read sentences one word at a time.\n\nAfter each sentence is finished, you will be asked a Yes or No question about that sentence.\n\nAll you have to do is read the sentences normally, and then answer the question\n\nPress the YES key to see some examples.', font=stimuliFont, units=breakUnits, height=breakSize, color=instructionColor)
stim.setPos((0, 0))
stim.draw()
win.flip()

pauseResponse = event.waitKeys(keyList=[responseYes, quitKey])

if pauseResponse[-1] == quitKey:
    participantName = participantInfo[0].replace(" ", "")
    filename = 'results.' + participantName + '.csv'
    results.to_csv(filename)
    win.close()
    core.quit()

for frameN in range(instructionOff - 1):
    win.flip()
win.flip()

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
            stim = visual.TextStim(win, text='Congratulations! You answered %i of the %i practice questions correctly.\n\nYou are now ready to do the actual experiment.\n\nThere are %i sentences to read.\n\nPlease sit still, stop blinking and press the YES key when you are ready for the first sentence.' % (recentCorrectResponses, trialsSinceLastBreak, remainingTrials), font=stimuliFont, units=breakUnits, height=breakSize, color=breakColor)
            totalCorrectResponses = 0
        else:
            stim = visual.TextStim(win, text='Please feel free to take a short break now if you would like.\n\nYou answered %i out of %i questions correctly since the last break.\n\nYou have completed %i sentences, and have %i to go.\n\nWhen you are ready for the next sentence, please sit still, stop blinking, and press the YES key.' % (recentCorrectResponses, trialsSinceLastBreak, completedTrials, remainingTrials), font=stimuliFont, units=breakUnits, height=breakSize, color=breakColor)
        stim.setPos((0, 0))
        stim.draw()
        win.flip()

        pauseResponse = event.waitKeys(keyList=[responseYes, quitKey])

        if pauseResponse[-1] == quitKey:
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
        if event.getKeys(quitKey):
            participantName = participantInfo[0].replace(" ", "")
            filename = 'results.' + participantName + '.csv'
            results.to_csv(filename)
            win.close()
            core.quit()

        stim = visual.TextStim(win, text=words[wordIndex],  languageStyle='Arabic', 
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
                win.flip()
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
        stim = visual.TextStim(win, text=trialList[trialIndex]['taskQuestion'], font=stimuliFont, units=taskQuestionUnits, height=taskQuestionSize, color=taskQuestionColor)
        stim.setPos((0, 0))
        stim.draw()
        win.flip()

        responses = event.waitKeys(keyList=[responseNo, responseYes, quitKey])

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
    stim = visual.TextStim(win, text='You can blink now.\n\nWhen you are ready for the next sentence, sit still, stop blinking, and press the YES key.', font=stimuliFont, units=breakUnits, height=breakSize, color=stimuliColor)
    stim.setPos((0, 0))
    stim.draw()
    win.flip()

    pauseResponse = event.waitKeys(keyList=[responseYes, quitKey])

    if pauseResponse[-1] == quitKey:
        participantName = participantInfo[0].replace(" ", "")
        filename = 'results.' + participantName + '.csv'
        results.to_csv(filename)
        win.close()
        core.quit()

    for frameN in range(taskQuestionOff - 1):
        win.flip()
    win.flip()

event.clearEvents()
stim = visual.TextStim(win, text='Congratulations, you are finished!\n\nYou read %i sentences, and answered %i out of %i questions correctly!\n\nThank you very much for your participation.\n\nPress any key to close this program.' % ((totalTrials - totalBreakCount - practiceCount), totalCorrectResponses, totalQuestionCount), font=stimuliFont, units=instructionUnits, height=instructionSize, color=instructionColor)
stim.setPos((0, 0))
stim.draw()
win.flip()

event.waitKeys()

participantName = participantInfo[0].replace(" ", "")
filename = 'results.' + participantName + '.csv'
results.to_csv(filename)

win.close()
core.quit()
