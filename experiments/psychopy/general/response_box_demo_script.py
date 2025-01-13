
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



TIMES_TEST_getbutton_NONE = 10

for i in range(TIMES_TEST_getbutton_NONE):
    print('Testing getbutton None')
    response = getbutton()
    print('Button press', response)

buttons = [1, 3, 6, 8]  # this is the red and green button for both boxes right and left
# test multiple buttons, this function should only listen to the buttons in buttons only

TIMES_TEST_getbutton_array = 10

for i in range(TIMES_TEST_getbutton_array):
    print('Testing getbutton Array')
    response = getbutton(buttons)
    print('Button press array for array', buttons, 'is', response)

DPxClose()





