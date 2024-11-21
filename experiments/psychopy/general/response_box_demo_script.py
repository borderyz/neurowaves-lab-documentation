
# Response button test script to be used with PsychoPy
# Author: Hadi Zaatiti, Jayeon Park

from pypixxlib._libdpx import DPxOpen, DPxClose, DPxWriteRegCache, DPxUpdateRegCache, DPxGetTime, DPxStopDinLog, DPxGetDinValue
from utilities import *


#Connect to VPixx device
DPxOpen()

# Updated table 21-11-2024 tested
# RIGHT BOX
# 9  RED
# 7  GREEN
# 6 BLUE
# 8 Yellow

# Left Box
# 4 RED
# 2 Green
# 1 Blue
# 3 Yellow

response = getbutton()


while True:
    response = getbutton()
    print(' Button press', response)

DPxClose()
