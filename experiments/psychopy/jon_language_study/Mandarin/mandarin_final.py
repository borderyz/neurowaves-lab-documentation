import os, sys
import pandas as pd
from psychopy import core, visual, event, parallel, data, monitors, gui

from pypixxlib import _libdpx as dp


from utilities import *

# Setup the connection with the Vpixx systems and disable Pixel Mode

TIME_TO_RESET_BUTTON_BOX =1.7
TIME_WAIT_BREAK = 0.5
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


dp.DPxOpen()
dp.DPxDisableDoutPixelMode()
dp.DPxWriteRegCache()
dp.DPxSetDoutValue(RGB2Trigger(black), 0xFFFFFF)
dp.DPxUpdateRegCache()

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

trialList = data.importConditions('mandarin_list12.csv')

#mon = monitors.Monitor('BenQ24', width=53, distance=100)
#port = parallel.ParallelPort(address=0xD010)
clock = core.Clock()

backgroundColor = 'black'
instructionsFont = 'Arial'
stimuliFont = 'SimSun'
stimuliColor = 'gold' #rgb(255, 215, 0)
stimuliUnits = 'deg'
stimuliSize = 2
instructionSize = 1
wordOn = 42 #350ms
wordOff = 24 #200ms
lastWordOn =  132  #1100

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

instructionColor = 'gold'
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

myDlg = gui.Dlg(title="RSVP MEG experiment", size=(600, 600))
myDlg.addText('Participant Info', color='Red')
myDlg.addField('Participant Name:', 'First Last', tip='or subject code')
myDlg.addField('Age:', 21)
myDlg.addField('Biological Sex:', choices=["Female", "Male"])
myDlg.addField('Handedness:', 100)
myDlg.addText('Experiment Info', color='Red')
myDlg.addField('Experiment Name:', 'Mandarin')
myDlg.addField('Experiment List:', 1)
myDlg.show()

if myDlg.OK:
    participantInfo = myDlg.data
else:
    print('user cancelled')

win = visual.Window(screen =1, size=[1919.5, 1079.5], fullscr=False, color=backgroundColor, monitor='testMonitor')  # Set the border color to black)

#win = visual.Window(screen =1, size=[1920, 1080], fullscr=True, color=backgroundColor, monitor='testMonitor')  # Set the border color to black)


stim = visual.TextStim(win, text= '在本次实验中，您将阅读一系列句子，句子将逐词出现在屏幕上。\n\n'
                                  '与此同时，我们将会记录脑磁图收集到的信息。\n\n'
                                  '在一些句子结束后，您将回答一道关于该句子的是非题。\n\n'
                                  '这些问题非常简单。\n\n他们仅仅是用来保证您认真阅读了那些句子。\n\n'
                                  '您只需要正常地阅读屏幕上的句子，然后回答问题。\n\n'
                                  '在您阅读句子的时候，请不要眨眼。\n\n 您可以在句子结束后，或者回答是非题过程中眨眼。\n\n'
                                  '请按下“是”按钮来看几句例子。',
                       font= 'SimSun', units= instructionUnits, color=instructionColor, height= 0.7, alignText= 'center', wrapWidth= 30)
stim.setPos((0, 0))
stim.draw()
win.flip()


listenbutton(9)

#1 we need to write code where at a specific time, we decide to listen to an escape button and if the escape button happens we save the data

#2 add the previous code at multiple occasions so that we are listening to this during the experiment (covering as much as possible of the experiment time)


# if responses[-1] == quitKey:
#     participantName = participantInfo[0].replace(" ", "")
#     filename = 'results.' + participantName + '.csv'
#     results.to_csv(filename)
#     win.close()
#     core.quit()

for frameN in range(instructionOff - 1):
    win.flip()
win.flip()

# Loop for each trial
for trialIndex in range(startItem - 1, totalTrials):

    pauseResponse = []
    responses = []
    event.clearEvents()

    if trialList[trialIndex]['sentence'] == breakKeyword:
        # Handling breaks
        event.clearEvents()
        currentBreakCount += 1
        completedTrials = trialIndex + 1 - practiceCount - currentBreakCount
        remainingTrials = (totalTrials - totalBreakCount - practiceCount) - completedTrials

        if currentBreakCount == 1:
            stim = visual.TextStim(win, text= '恭喜您！您已经正确回答了%i道练习题中的%i道。\n\n'
                                              '您已经准备好开始进行真正的实验了。\n\n'
                                              '现在还有%i句句子要阅读。\n\n '
                                              '请保持不动，不要眨眼。\n\n '
                                              '请在我们通知您可以开始实验后按下“是”按钮开始阅读第一句话。'
                                              % (trialsSinceLastBreak,recentCorrectResponses, remainingTrials),
                                   font= 'SimSun', units=instructionUnits, color=instructionColor, height = 1, alignText = 'center', wrapWidth= 30)


            totalCorrectResponses = 0
            print('congratulations window')
        else:
            stim = visual.TextStim(win, text='自上一次休息后，您已经正确回答了%i个问题中的%i道。\n\n '
                                             '你已经完成了%i句句子，还有%i句句子。\n\n'
                                             '当您准备好阅读下一句话时，\n\n '
                                             '请保持不动，不要眨眼，然后按下“是”按钮。'
                                             % (trialsSinceLastBreak,recentCorrectResponses, completedTrials, remainingTrials),
                                   font= 'SimSun', units=instructionUnits, color=instructionColor, height = 1, alignText = 'center', wrapWidth= 30)
            print('break window')

        stim.setPos((0, 0))
        stim.draw()
        win.flip()
        print('listening to button')
        core.wait(TIME_WAIT_BREAK)
        # Pause until response
        listenbutton(9)
        # response = getbutton()  # listen to a button
        # responses.append(response)

        # if responses[-1] == quitKey:
        #     participantName = participantInfo[0].replace(" ", "")
        #     filename = 'results.' + participantName + '.csv'
        #     results.to_csv(filename)
        #     win.close()
        #     core.quit()

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
    win.flip()

    for frameN in range(fixationOff - 2):
        win.flip()
    win.flip()

    for wordIndex in range(numWords):
        print(repr(words[wordIndex]))
        if event.getKeys(quitKey):
            participantName = participantInfo[0].replace(" ", "")
            filename = 'results.' + participantName + '.csv'
            results.to_csv(filename, encoding='utf-8-sig')
            win.close()
            core.quit()

        stim = visual.TextStim(win, text=words[wordIndex],  font=stimuliFont, units=stimuliUnits, height=stimuliSize, color=stimuliColor, alignText = 'center', anchorHoriz = 'center')
        stim.setPos((0, 0))


        if wordIndex == max(range(numWords)):
            for frameN in range(lastWordOn):
                stim.draw()
                win.flip()
                if frameN == 0:
                    clock.reset()

                if frameN < 10:
                    combined_trigger_value = (
                            trialList[trialIndex]['trigger224w'] * trigger_channels_dictionary[224] +
                            trialList[trialIndex]['trigger225w'] * trigger_channels_dictionary[225] +
                            trialList[trialIndex]['trigger226w'] * trigger_channels_dictionary[226] +
                            trialList[trialIndex]['trigger227w'] * trigger_channels_dictionary[227] +
                            trialList[trialIndex]['trigger228w'] * trigger_channels_dictionary[228] +
                            trialList[trialIndex]['trigger229w'] * trigger_channels_dictionary[229] +
                            trialList[trialIndex]['trigger230w'] * trigger_channels_dictionary[230] +
                            trialList[trialIndex]['trigger231w'] * trigger_channels_dictionary[231]
                    )
                    print(f"Trial {trialIndex}, Trigger: Combined Value = {combined_trigger_value}")

                    dp.DPxSetDoutValue(combined_trigger_value, 0xFFFFFF)
                    dp.DPxUpdateRegCache()
                    print('wordIndex', wordIndex)
                    print('frameN', frameN)

                if frameN == 10:
                    # Debugging log: Print the calculated combined value
                    dp.DPxSetDoutValue(RGB2Trigger(black), 0xFFFFFF)
                    dp.DPxUpdateRegCache()

            win.flip()

            results.loc[trialIndex, wordIndex + len(subjectColumns)] = clock.getTime()
        else:
            for frameN in range(wordOn):
                stim.draw()
                win.flip()


                if wordIndex == 0:
                    if frameN < 10:
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
                        print(f"Trial {trialIndex}, Trigger: Combined Value = {combined_trigger_value}")


                        dp.DPxSetDoutValue(combined_trigger_value, 0xFFFFFF)
                        dp.DPxUpdateRegCache()
                        print('wordIndex', wordIndex)
                        print('frameN', frameN)
                    if frameN == 10:

                        # Debugging log: Print the calculated combined value
                        dp.DPxSetDoutValue(RGB2Trigger(black), 0xFFFFFF)
                        dp.DPxUpdateRegCache()
                else:
                    # Trigger logic for the rest of the words
                    if frameN < 10:
                        combined_trigger_value = (
                            trialList[trialIndex]['trigger224w'] * trigger_channels_dictionary[224] +
                            trialList[trialIndex]['trigger225w'] * trigger_channels_dictionary[225] +
                            trialList[trialIndex]['trigger226w'] * trigger_channels_dictionary[226] +
                            trialList[trialIndex]['trigger227w'] * trigger_channels_dictionary[227] +
                            trialList[trialIndex]['trigger228w'] * trigger_channels_dictionary[228] +
                            trialList[trialIndex]['trigger229w'] * trigger_channels_dictionary[229] +
                            trialList[trialIndex]['trigger230w'] * trigger_channels_dictionary[230] +
                            trialList[trialIndex]['trigger231w'] * trigger_channels_dictionary[231]
                        )
                        print(f"Trial {trialIndex}, Trigger: Combined Value = {combined_trigger_value}")


                        dp.DPxSetDoutValue(combined_trigger_value, 0xFFFFFF)
                        dp.DPxUpdateRegCache()
                        print('wordIndex', wordIndex)
                        print('frameN', frameN)
                    if frameN == 10:

                        # Debugging log: Print the calculated combined value
                        dp.DPxSetDoutValue(RGB2Trigger(black), 0xFFFFFF)
                        dp.DPxUpdateRegCache()




                if frameN == 0:
                    clock.reset()
            win.flip()
            results.loc[trialIndex, wordIndex + len(subjectColumns)] = clock.getTime()

        for frameN in range(wordOff - 2):
            win.flip()
        win.flip()

    box.setAutoDraw(False)

    # Display task question with yellow text
    if isinstance(trialList[trialIndex]['taskQuestion'], str) and len(trialList[trialIndex]['taskQuestion']) >= 4:
        event.clearEvents()

        stim = visual.TextStim(win, text=trialList[trialIndex]['taskQuestion'], font= stimuliFont, units= stimuliUnits, height=1.5, color=taskQuestionColor, alignText = 'center',wrapWidth= 30)
        stim.setPos((0, 0))
        stim.draw()
        win.flip()

        # Wait until button press to proceed to next trial
        response = getbutton()  # listen to a button

        responses.append(response)


        stim = visual.TextStim(win, text='请确保您的手指没有持续按压任何按钮。\n\n',
                               font= stimuliFont, units= stimuliUnits, height=1.5, color=taskQuestionColor, alignText = 'center',wrapWidth= 30)
        stim.setPos((0,-1.5))
        stim.draw()
        win.flip()
        core.wait(TIME_TO_RESET_BUTTON_BOX)

        if responses[-1] == quitKey:
            participantName = participantInfo[0].replace(" ", "")
            filename = 'results.' + participantName + '.csv'
            results.to_csv(filename, encoding='utf-8-sig')
            win.close()
            core.quit()

        if responses[-1] == trialList[trialIndex]['correctAnswer']:
            recentCorrectResponses += 1
            totalCorrectResponses += 1
            answer = 1
        else:
            answer = 0

        # Wait a little longer before moving on
        #core.wait(0.5)  # This ensures that the yellow text stays for an additional moment; here it awaits indefinitely

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

    # TODO: check that this works correctly, this should save one by one
    participantName = participantInfo[0].replace(" ", "")
    filename = 'results.' + participantName + '.csv'
    results.to_csv(filename, encoding='utf-8-sig')

    event.clearEvents()
    #responses = []
    stim = visual.TextStim(win,
                           text='现在您可以眨眼了。\n\n' 
                                '当您准备好阅读下一句话时,\n\n'
                                '请保持不动，不要眨眼，\n\n'
                                '然后按下“是”按钮。\n\n',
                           font= stimuliFont, units= stimuliUnits, height= instructionSize, color=stimuliColor, alignText = 'center')
    stim.setPos((0, -1.5))
    stim.draw()
    win.flip()

    # pauseResponse = event.waitKeys(keyList=[responseYes, quitKey])
    # response = getbutton()  # listen to a button
    # responses.append(response) # everytime we get a response we add it to the table
    listenbutton(9)

    #core.wait(0.5)  # This ensures that the yellow text stays for an additional moment; here it waits for exactly 500 ms



    # if responses[-1] == quitKey:
    #     participantName = participantInfo[0].replace(" ", "")
    #     filename = 'results.' + participantName + '.csv'
    #     results.to_csv(filename)
    #     win.close()
    #     core.quit()

    for frameN in range(taskQuestionOff - 1):
        win.flip()

    win.flip()




event.clearEvents()
stim = visual.TextStim(win,
                       text='您已经完成了所有内容 \n\n' 
                            '请您暂时保持不动，\n\n'
                            '以便我们进行最后的记录。\n\n'
                            '记录过程大约持续30秒钟。 \n\n'
                            '您阅读了%i句句子，\n\n'
                            '并成功答对了其中的%i个问题。（共%i个问题）。\n\n' 
                            '非常感谢您来参与我们的实验。'  % (
                       (totalTrials - totalBreakCount - practiceCount), totalCorrectResponses, totalQuestionCount),
                       font= stimuliFont, units= stimuliUnits, height=instructionSize, color=stimuliColor,  alignText = 'center')

stim.setPos((0, 0))
stim.draw()
win.flip()

#listenbutton(3) we want to add this to let them press at the end?

event.waitKeys()

participantName = participantInfo[0].replace(" ", "")
filename = 'results.' + participantName + '.csv'
results.to_csv(filename, encoding='utf-8-sig')

win.close()
core.quit()

dp.DPxClose()

