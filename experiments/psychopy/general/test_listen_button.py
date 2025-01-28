# Response button test script to be used with PsychoPy
# Author: Hadi Zaatiti, Jayeon Park

from pypixxlib._libdpx import DPxOpen, DPxClose, DPxWriteRegCache, DPxUpdateRegCache, DPxGetTime, DPxStopDinLog, DPxGetDinValue
from utilities import *


#Connect to VPixx device
DPxOpen()


print('listening')

listenbutton(9)

print('button 9 is pressed')

DPxClose()