import time
from pypixxlib._libdpx import DPxOpen, DPxClose, DPxWriteRegCache, DPxUpdateRegCache, DPxGetTime, DPxStopDinLog, DPxGetDinValue
from experiments.psychopy.general.utilities import *

selection1 = {
    "right box": ["green", "blue", "yellow"],
    "left box": ["white", "blue", "red"]
}


selection2 = {
"left box": ["green", "blue", "yellow", "red", "white"]
}

while True:




    DPxOpen()

    candidates = getbuttonColor(selection2)


    time.sleep(0.5)  # 500 milliseconds

    DPxClose()
    print("candidates", candidates)

