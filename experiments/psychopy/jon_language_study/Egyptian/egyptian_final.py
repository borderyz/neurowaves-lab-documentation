import os, sys
import pandas as pd
from psychopy import core, visual, event, parallel, data, monitors, gui

from pypixxlib import _libdpx as dp


from utilities import *

# Setup the connection with the Vpixx systems and disable Pixel Mode

TIME_TO_RESET_BUTTON_BOX = 1.7
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

trialList = data.importConditions('egyptian_list9.csv')

#mon = monitors.Monitor('BenQ24', width=53, distance=100)
#port = parallel.ParallelPort(address=0xD010)
clock = core.Clock()

backgroundColor = 'black'
instructionsFont = 'Noto Naskh Arabic' #'Arial'
stimuliFont = 'Noto Naskh Arabic' #'Times New Roman'
stimuliColor = 'gold' #rgb(255, 215, 0)
stimuliUnits = 'deg'
stimuliSize = 2
wordOn = 54  #54 # 450ms #48 #400ms
wordOff = 18 #18 #150ms #24 #200ms
lastWordOn = 144 #144 #1200ms

boxHeight = stimuliSize + 2
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
taskQuestionSize = 1
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
myDlg.addField('Experiment Name:', 'Egyptian')
myDlg.addField('Experiment List:', 1)
myDlg.show()

if myDlg.OK:
    participantInfo = myDlg.data
else:
    print('user cancelled')

win = visual.Window(screen =1, size=[1919.5, 1079.5], fullscr=False, color=backgroundColor, monitor='testMonitor')  # Set the border color to black)

#win = visual.Window(screen =1, size=[1920, 1080], fullscr=True, color=backgroundColor, monitor='testMonitor')  # Set the border color to black)

instructions_text = (
    "في التجربة ده، حتقرا جمل كلمة بكلمة و احنا حنسجل ال MEG.\n\n"  # "MEG" is now part of the first sentence
    "بعد بعض الجمل، حيطلب منك الإجابة بنعم أو لا بخصوص محتوى الجملة.\n\n"  # Second sentence
    "الأسئلة ده بسيطة آوي وهي للتأكيد من أنك بتقرا الجمل.\n\n"  # Third sentence
    "كل ما عليك تعمله هو قراءة الجمل بشكل طبيعي، و بعدين الإجابة على السؤال\n\n"  # Fourth sentence
    "يرجى تحاول مترمش لما تشوف الجمل، يمكنك الرمش بعد الجملة و وقت أسئلة الفهم.\n\n"  # Fifth sentence
    "اضغط على مفتاح نعم عشان تشوف الأمثلة."  # Sixth sentence
)

stim = visual.TextStim(win,
                       text= instructions_text,
                       font= instructionsFont, languageStyle='Arabic', units=breakUnits, color=instructionColor, height= 0.8, alignText= 'center',  wrapWidth= 30)
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
            stim = visual.TextStim(win,
                                   text='مبروك! أنت جوبت على %i من %i من أسئلة التدريب بشكل صحيح.\n\n أنتهت فترة التدريب. \n\n  من فضلك استنة التعلمات و متدسش على أي زرار . \n\n  أنت دلوقتي جاهز تعمل التجربة الحقيقية.\n\n في %i جملة للقراية.\n\n من فضلك اتجنب الحركة والتوقف عن الرمش واضغط علي زرار "نعم" لما نديك التعلمات. ' %
                                        (recentCorrectResponses, trialsSinceLastBreak, remainingTrials),
                                        font=instructionsFont, languageStyle='Arabic', units=breakUnits, color=breakColor, height=0.8, alignText= 'center', wrapWidth= 30)
            totalCorrectResponses = 0
            print('congratulations window')
        else:
            stim = visual.TextStim(win, text = 'انت جوبت على %i من %i سؤال صح من الاستراحة الأخيرة.\n\nانت كملت %i جملة، وباقي %i جملة كمان.\n\nلما تكون جاهز للجملة اللي جية اتجنب الحركة، وقف ترمش ، واضغط على مفتاح "نعم".' %
                                        (recentCorrectResponses, trialsSinceLastBreak, completedTrials, remainingTrials),
                                        font=instructionsFont, languageStyle='Arabic', units=breakUnits, color=breakColor, height=0.8, alignText= 'center', wrapWidth= 30)
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

        stim = visual.TextStim(win, text=words[wordIndex], languageStyle='Arabic', font=stimuliFont, units=stimuliUnits, height=stimuliSize, color=stimuliColor)
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


        stim = visual.TextStim(win, text=trialList[trialIndex]['taskQuestion'],
                               font=instructionsFont, languageStyle='Arabic', units=taskQuestionUnits, height=1.2, color=taskQuestionColor,alignText= 'center', wrapWidth= 30)
        stim.setPos((0, 0))
        stim.draw()
        win.flip()

        # Wait until button press to proceed to next trial
        response = getbutton()  # listen to a button

        responses.append(response)


        stim = visual.TextStim(win, text='اتأكد ان صباعك مش دايس على أي زرار.',
                               font=instructionsFont, languageStyle='Arabic', units=taskQuestionUnits, height=1.2, color=taskQuestionColor,alignText= 'center', wrapWidth= 30)
        stim.setPos((0, 0))
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
    blink_text = (
        "يمكنك ترمش دلوقتي.\n\n"  # First sentence with a newline
        "لما تكون جاهز للجملة اللي جية اتجنب الحركة، وقف ترمش ،\n"  # Second sentence with a newline
        "اضغط على مفتاح \"نعم\"."  # Third sentence
    )

    stim = visual.TextStim(win,
                           text= blink_text,
                           font=instructionsFont, languageStyle='Arabic', units=breakUnits, height=breakSize, color=stimuliColor, wrapWidth= 30 )
    stim.setPos((0, 0))
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
                       text=' مبروك ، انت خلصت! بس من فضلك متتحركش لحد منؤلك.\n\n محتجين 30 ثانية بس عشان نخلص التسجيلات.\n\n انت قريت %i جملة، وجوبت على %i من %i سؤال صح!\n\n شكرا اوي على مشاركتك.\n\n اضغط على أي مفتاح عشان تقفل البرنامج.'% (
                       (totalTrials - totalBreakCount - practiceCount), totalCorrectResponses, totalQuestionCount),
                       font=instructionsFont, languageStyle='Arabic', units=instructionUnits, height=0.8, color=instructionColor, wrapWidth=30, alignText='center')
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

