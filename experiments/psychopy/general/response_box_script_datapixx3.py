from pypixxlib import DATAPixx3
from psychopy import core

#connect to VPixx device
device = DATAPixx3()

#First, let's make a dictionary of codes that correspond to our buttons. This is in decimal.
#Note 1: these codes ARE NOT UNIVERSAL. You can check what your own button codes are using the PyPixx Digital I/O demo
#Note 2: these codes are for single button presses only. If two buttons are pressed at the same time this will generate a unique code, which we will ignore
buttonCodes = {65527:'blue', 65533:'yellow', 65534:'red', 65531:'green', 65519:'white', 65535:'button release'}
exitButton = 'white'

myLog = device.din.setDinLog(12e6, 1000)
device.din.startDinLog()
device.updateRegisterCache()
startTime = device.getTime()
finished = False


#let's create a loop which checks the schedule at 0.25 s intervals for button presses.
#Any time a button press is found, we print the timestamp and button pressed.
#If a designated exit button is pressed, we disconnect.
while finished == False:
    #read device status
    device.updateRegisterCache()
    device.din.getDinLogStatus(myLog)
    newEvents = myLog["newLogFrames"]

    if newEvents > 0:
        eventList = device.din.readDinLog(myLog, newEvents)

        for x in eventList:
           if x[1] in buttonCodes:
                #look up the name of the button
                buttonID = buttonCodes[x[1]]

                #get the time of the press, since we started logging
                time = round(x[0] - startTime, 2)
                printStr = 'Button pressed! Button code: ' + str(x[1]) + ', Button ID: ' + buttonID + ', Time:' + str(time)
                print(printStr)
                if buttonID == exitButton:
                    finished = True
    core.wait(0.25)

#Stop logging
device.din.stopDinLog()
device.updateRegisterCache()