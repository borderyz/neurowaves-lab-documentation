# Author: Hadi Zaatiti hadi.zaatiti@nyu.edu

from psychopy import visual, core, monitors
from pypixxlib import _libdpx as dp



monitor = monitors.Monitor("testMonitor")
MONITOR_INDEX = 0 # 1 Indicates second screen and 0 indicates the first screen

# To install pypixxlib, download the vpixx software then find it under
# the vpixx software directory, then install it into the python environment using pip . after navigating to the extracted files

# Define trigger pixels for all usable MEG channels
#trig.ch224 = [4  0  0]; %224 meg channel
#trig.ch225 = [16  0  0];  %225 meg channel
#trig.ch226 = [64 0 0]; % 226 meg channel
#trig.ch227 = [0  1 0]; % 227 meg channel
#trig.ch228 = [0  4 0]; % 228 meg channel
#trig.ch229 = [0 16 0]; % 229 meg channel
#trig.ch230 = [0 64 0]; % 230 meg channel
#trig.ch231 = [0 0  1]; % 231 meg channel



def RGB2Trigger(color):
    # helper function determines expected trigger from a given RGB 255 colour value
    # operates by converting individual colours into binary strings and stitching them together
    # and interpreting the result as an integer

    # return triggerVal
    return int((color[2] << 16) + (color[1] << 8) + color[0])  # dhk


def Trigger2RGB(trigger):
    # helper function determines pixel mode RGB 255 colour value based on 24-bit trigger (in decimal, base 10)
    # returns a list with R, G and B elements

    # return [red, green, blue]
    return [trigger % 256, (trigger >> 8) % 256, (trigger >> 16) % 256]  # dhk


##
# START
# Initialize connection and set up some default parameters:
dp.DPxOpen()
dp.DPxDisableDoutPixelMode()
dp.DPxWriteRegCache()


# KIT MEG Channels triggered via Pixel Model by setting top left pixel to a specific color
#trig.ch224 = [4  0  0]; %224 meg channel
#trig.ch225 = [16  0  0];  %225 meg channel
#trig.ch226 = [64 0 0]; % 226 meg channel
#trig.ch227 = [0  1 0]; % 227 meg channel
#trig.ch228 = [0  4 0]; % 228 meg channel
#trig.ch229 = [0 16 0]; % 229 meg channel
#trig.ch230 = [0 64 0]; % 230 meg channel
#trig.ch231 = [0 0  1]; % 231 meg channel

trigger = [[4, 0, 0], [16, 0, 0], [64, 0, 0], [0, 1, 0], [0, 4, 0], [0, 16, 0], [0, 64, 0], [0, 0, 1]]
channel_names  = ['224', '225', '226', '227', '228', '229', '230', '231']
black = [0, 0, 0]



failcount = 0
print('\nStarting Pixel Mode Test\n\nTest#\tRGB225 Color\t    Expected Dout    Returned Dout')

value = RGB2Trigger([256, 256, 256])

for i in range(8):
    # New test with digital out settings
    print('Testing channel', channel_names[i])
    dp.DPxSetDoutValue(RGB2Trigger(trigger[i]), 0xFFFFFF)
    dp.DPxUpdateRegCache()
    core.wait(1)


    dp.DPxSetDoutValue(RGB2Trigger(black), 0xFFFFFF)
    dp.DPxUpdateRegCache()
    core.wait(2)

    print('Iteration ', i)

dp.DPxClose()

