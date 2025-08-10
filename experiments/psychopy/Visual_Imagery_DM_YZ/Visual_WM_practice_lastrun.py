#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2024.2.4),
    on July 30, 2025, at 22:04
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""
#Vpixx import

from pypixxlib import _libdpx as dp
from utilities import *

USE_VPIXX = True


if USE_VPIXX:
    dp.DPxOpen()
    dp.DPxDisableDoutPixelMode()
    dp.DPxWriteRegCache()
    dp.DPxSetDoutValue(RGB2Trigger(black), 0xFFFFFF)
    dp.DPxUpdateRegCache()

# --- Import packages ---
from psychopy import locale_setup
from psychopy import prefs
from psychopy import plugins
plugins.activatePlugins()
prefs.hardware['audioLib'] = 'ptb'
prefs.hardware['audioLatencyMode'] = '3'
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware
from psychopy.tools import environmenttools
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER, priority)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

import psychopy.iohub as io
from psychopy.hardware import keyboard

# --- Setup global variables (available in all functions) ---
# create a device manager to handle hardware (keyboards, mice, mirophones, speakers, etc.)
deviceManager = hardware.DeviceManager()
# ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
# store info about the experiment session
psychopyVersion = '2024.2.4'
expName = 'visual_imagery'  # from the Builder filename that created this script
# information about this experiment
expInfo = {
    'participant': f"{randint(0, 999999):06.0f}",
    'session': '001',
    'date|hid': data.getDateStr(),
    'expName|hid': expName,
    'psychopyVersion|hid': psychopyVersion,
}

# --- Define some variables which will change depending on pilot mode ---
'''
To run in pilot mode, either use the run/pilot toggle in Builder, Coder and Runner, 
or run the experiment with `--pilot` as an argument. To change what pilot 
#mode does, check out the 'Pilot mode' tab in preferences.
'''
# work out from system args whether we are running in pilot mode
PILOTING = core.setPilotModeFromArgs()
# start off with values from experiment settings
_fullScr = True
_winSize = [1707, 960]
# if in pilot mode, apply overrides according to preferences
if PILOTING:
    # force windowed mode
    if prefs.piloting['forceWindowed']:
        _fullScr = False
        # set window size
        _winSize = prefs.piloting['forcedWindowSize']

def showExpInfoDlg(expInfo):
    """
    Show participant info dialog.
    Parameters
    ==========
    expInfo : dict
        Information about this experiment.
    
    Returns
    ==========
    dict
        Information about this experiment.
    """
    # show participant info dialog
    dlg = gui.DlgFromDict(
        dictionary=expInfo, sortKeys=False, title=expName, alwaysOnTop=True
    )
    if dlg.OK == False:
        core.quit()  # user pressed cancel
    # return expInfo
    return expInfo


def setupData(expInfo, dataDir=None):
    """
    Make an ExperimentHandler to handle trials and saving.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    dataDir : Path, str or None
        Folder to save the data to, leave as None to create a folder in the current directory.    
    Returns
    ==========
    psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    # remove dialog-specific syntax from expInfo
    for key, val in expInfo.copy().items():
        newKey, _ = data.utils.parsePipeSyntax(key)
        expInfo[newKey] = expInfo.pop(key)
    
    # data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    if dataDir is None:
        dataDir = _thisDir
    filename = u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])
    # make sure filename is relative to dataDir
    if os.path.isabs(filename):
        dataDir = os.path.commonprefix([dataDir, filename])
        filename = os.path.relpath(filename, dataDir)
    
    # an ExperimentHandler isn't essential but helps with data saving
    thisExp = data.ExperimentHandler(
        name=expName, version='',
        extraInfo=expInfo, runtimeInfo=None,
        originPath='D:\\NYUAD\\Visual_Imagery\\Experiment\\Visual_Imagery_WM_MEG\\Visual_Imagery\\Visual_WM_P_lastrun.py',
        savePickle=True, saveWideText=True,
        dataFileName=dataDir + os.sep + filename, sortColumns='time'
    )
    thisExp.setPriority('thisRow.t', priority.CRITICAL)
    thisExp.setPriority('expName', priority.LOW)
    # return experiment handler
    return thisExp


def setupLogging(filename):
    """
    Setup a log file and tell it what level to log at.
    
    Parameters
    ==========
    filename : str or pathlib.Path
        Filename to save log file and data files as, doesn't need an extension.
    
    Returns
    ==========
    psychopy.logging.LogFile
        Text stream to receive inputs from the logging system.
    """
    # set how much information should be printed to the console / app
    if PILOTING:
        logging.console.setLevel(
            prefs.piloting['pilotConsoleLoggingLevel']
        )
    else:
        logging.console.setLevel('warning')
    # save a log file for detail verbose info
    logFile = logging.LogFile(filename+'.log')
    if PILOTING:
        logFile.setLevel(
            prefs.piloting['pilotLoggingLevel']
        )
    else:
        logFile.setLevel(
            logging.getLevel('info')
        )
    
    return logFile


def setupWindow(expInfo=None, win=None):
    """
    Setup the Window
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    win : psychopy.visual.Window
        Window to setup - leave as None to create a new window.
    
    Returns
    ==========
    psychopy.visual.Window
        Window in which to run this experiment.
    """
    if PILOTING:
        logging.debug('Fullscreen settings ignored as running in pilot mode.')
    
    if win is None:
        # if not given a window to setup, make one
        win = visual.Window(
            size=_winSize, fullscr=_fullScr, screen=0,
            winType='pyglet', allowGUI=True, allowStencil=False,
            monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
            backgroundImage='', backgroundFit='none',
            blendMode='avg', useFBO=True,
            units='height',
            checkTiming=False  # we're going to do this ourselves in a moment
        )
    else:
        # if we have a window, just set the attributes which are safe to set
        win.color = [0,0,0]
        win.colorSpace = 'rgb'
        win.backgroundImage = ''
        win.backgroundFit = 'none'
        win.units = 'height'
    if expInfo is not None:
        # get/measure frame rate if not already in expInfo
        if win._monitorFrameRate is None:
            win._monitorFrameRate = win.getActualFrameRate(infoMsg='Attempting to measure frame rate of screen, please wait...')
        expInfo['frameRate'] = win._monitorFrameRate
    win.hideMessage()
    # show a visual indicator if we're in piloting mode
    if PILOTING and prefs.piloting['showPilotingIndicator']:
        win.showPilotingIndicator()
    
    return win


def setupDevices(expInfo, thisExp, win):
    """
    Setup whatever devices are available (mouse, keyboard, speaker, eyetracker, etc.) and add them to 
    the device manager (deviceManager)
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window in which to run this experiment.
    Returns
    ==========
    bool
        True if completed successfully.
    """
    # --- Setup input devices ---
    ioConfig = {}
    
    # Setup iohub keyboard
    ioConfig['Keyboard'] = dict(use_keymap='psychopy')
    
    # Setup iohub experiment
    ioConfig['Experiment'] = dict(filename=thisExp.dataFileName)
    
    # Start ioHub server
    ioServer = io.launchHubServer(window=win, **ioConfig)
    
    # store ioServer object in the device manager
    deviceManager.ioServer = ioServer
    
    # create a default keyboard (e.g. to check for escape)
    if deviceManager.getDevice('defaultKeyboard') is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='iohub'
        )
    if deviceManager.getDevice('WM_P_Key_Resp') is None:
        # initialise WM_P_Key_Resp
        WM_P_Key_Resp = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='WM_P_Key_Resp',
        )
    # create speaker 'WM_P_Cue'
    deviceManager.addDevice(
        deviceName='WM_P_Cue',
        deviceClass='psychopy.hardware.speaker.SpeakerDevice',
        index=-1
    )
    # create speaker 'WM_P_Sound'
    deviceManager.addDevice(
        deviceName='WM_P_Sound',
        deviceClass='psychopy.hardware.speaker.SpeakerDevice',
        index=-1
    )
    if deviceManager.getDevice('WM_P_Test_Resp') is None:
        # initialise WM_P_Test_Resp
        WM_P_Test_Resp = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='WM_P_Test_Resp',
        )
    # return True if completed successfully
    return True

def pauseExperiment(thisExp, win=None, timers=[], playbackComponents=[]):
    """
    Pause this experiment, preventing the flow from advancing to the next routine until resumed.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    timers : list, tuple
        List of timers to reset once pausing is finished.
    playbackComponents : list, tuple
        List of any components with a `pause` method which need to be paused.
    """
    # if we are not paused, do nothing
    if thisExp.status != PAUSED:
        return
    
    # start a timer to figure out how long we're paused for
    pauseTimer = core.Clock()
    # pause any playback components
    for comp in playbackComponents:
        comp.pause()
    # make sure we have a keyboard
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        defaultKeyboard = deviceManager.addKeyboard(
            deviceClass='keyboard',
            deviceName='defaultKeyboard',
            backend='ioHub',
        )
    # run a while loop while we wait to unpause
    while thisExp.status == PAUSED:
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=['escape']):
            endExperiment(thisExp, win=win)
        # sleep 1ms so other threads can execute
        clock.time.sleep(0.001)
    # if stop was requested while paused, quit
    if thisExp.status == FINISHED:
        endExperiment(thisExp, win=win)
    # resume any playback components
    for comp in playbackComponents:
        comp.play()
    # reset any timers
    for timer in timers:
        timer.addTime(-pauseTimer.getTime())


def run(expInfo, thisExp, win, globalClock=None, thisSession=None):
    """
    Run the experiment flow.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    psychopy.visual.Window
        Window in which to run this experiment.
    globalClock : psychopy.core.clock.Clock or None
        Clock to get global time from - supply None to make a new one.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    # mark experiment as started
    thisExp.status = STARTED
    # make sure window is set to foreground to prevent losing focus
    win.winHandle.activate()
    # make sure variables created by exec are available globally
    exec = environmenttools.setExecEnvironment(globals())
    # get device handles from dict of input devices
    ioServer = deviceManager.ioServer
    # get/create a default keyboard (e.g. to check for escape)
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='ioHub'
        )
    eyetracker = deviceManager.getDevice('eyetracker')
    # make sure we're running in the directory for this experiment
    os.chdir(_thisDir)
    # get filename from ExperimentHandler for convenience
    filename = thisExp.dataFileName
    frameTolerance = 0.001  # how close to onset before 'same' frame
    endExpNow = False  # flag for 'escape' or other condition => quit the exp
    # get frame duration from frame rate in expInfo
    if 'frameRate' in expInfo and expInfo['frameRate'] is not None:
        frameDur = 1.0 / round(expInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess
    
    # Start Code - component code to be run after the window creation
    
    # --- Initialize components for Routine "WM_P_Start" ---
    WM_P_Intro = visual.TextStim(win=win, name='WM_P_Intro',
        text='This is a memory test.\n\nFirst, you will see two pictures of different objects one by one. Try to remember them carefully.\n\nThen, you will hear a "Ding", followed by a short description (e.g., “a red bus”). As soon as you hear the description, try to recall the object image you just saw as best as you can, and hold the image until the next stage. \n\nFinally, you will see a new image. Your task is to decide quickly if this image is one of the pictures you saw earlier. \n\nRespond with your right hand, index finger for ‘YES’, middle finger for ‘NO’.\n\nPlease let the experimenter know when you are ready to begin.',
        font='Arial',
        pos=(0, 0.2), draggable=False, height=0.03, wrapWidth=1.2, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    WM_P_Key_Resp = keyboard.Keyboard(deviceName='WM_P_Key_Resp')
    
    # --- Initialize components for Routine "WM_P_Interval" ---
    WM_P_Inter = visual.TextStim(win=win, name='WM_P_Inter',
        text='Please remember next two images.',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # --- Initialize components for Routine "WM_P_Perceive" ---
    WM_P_P_Image1 = visual.ImageStim(
        win=win,
        name='WM_P_P_Image1', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(0.5, 0.5),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    WM_P_P_Image2 = visual.ImageStim(
        win=win,
        name='WM_P_P_Image2', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(0.5, 0.5),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-2.0)
    WM_P_P_BG = visual.ImageStim(
        win=win,
        name='WM_P_P_BG', 
        image=None, mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(0.5, 0.5),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-3.0)
    
    # --- Initialize components for Routine "WM_P_WM" ---
    WM_P_WM_BG = visual.ImageStim(
        win=win,
        name='WM_P_WM_BG', 
        image=None, mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(0.5, 0.5),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    WM_P_Cue = sound.Sound(
        'A', 
        secs=1.0, 
        stereo=True, 
        hamming=True, 
        speaker='WM_P_Cue',    name='WM_P_Cue'
    )
    WM_P_Cue.setVolume(1.0)
    WM_P_Sound = sound.Sound(
        'A', 
        secs=1.5, 
        stereo=True, 
        hamming=True, 
        speaker='WM_P_Sound',    name='WM_P_Sound'
    )
    WM_P_Sound.setVolume(1.0)
    
    # --- Initialize components for Routine "WM_P_Test" ---
    # Run 'Begin Experiment' code from WM_P_Test_Code
    import random
    
    # Create a list of image names with specified counts
    WM_P_T_image_pool = ['8.jpg'] * 2 + ['20.jpg'] * 2 + ['50.jpg'] * 2
    random.shuffle(WM_P_T_image_pool)
    # Initialize a counter
    WM_P_T_image_index = 0
    WM_P_Test_Image = visual.ImageStim(
        win=win,
        name='WM_P_Test_Image', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(0.5, 0.5),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    WM_P_Test_Resp = keyboard.Keyboard(deviceName='WM_P_Test_Resp')
    WM_P_Test_Q = visual.TextStim(win=win, name='WM_P_Test_Q',
        text='Is this the image you saw?',
        font='Arial',
        pos=(0, 0.4), draggable=False, height=0.07, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    WM_P_Test_Option = visual.TextStim(win=win, name='WM_P_Test_Option',
        text='YES          NO',
        font='Arial',
        pos=(0, -0.4), draggable=False, height=0.07, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-4.0);
    
    # --- Initialize components for Routine "WM_P_End" ---
    text_3 = visual.TextStim(win=win, name='text_3',
        text='End of practice',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # create some handy timers
    
    # global clock to track the time since experiment started
    if globalClock is None:
        # create a clock if not given one
        globalClock = core.Clock()
    if isinstance(globalClock, str):
        # if given a string, make a clock accoridng to it
        if globalClock == 'float':
            # get timestamps as a simple value
            globalClock = core.Clock(format='float')
        elif globalClock == 'iso':
            # get timestamps in ISO format
            globalClock = core.Clock(format='%Y-%m-%d_%H:%M:%S.%f%z')
        else:
            # get timestamps in a custom format
            globalClock = core.Clock(format=globalClock)
    if ioServer is not None:
        ioServer.syncClock(globalClock)
    logging.setDefaultClock(globalClock)
    # routine timer to track time remaining of each (possibly non-slip) routine
    routineTimer = core.Clock()
    win.flip()  # flip window to reset last flip timer
    # store the exact time the global clock started
    expInfo['expStart'] = data.getDateStr(
        format='%Y-%m-%d %Hh%M.%S.%f %z', fractionalSecondDigits=6
    )
    
    # --- Prepare to start Routine "WM_P_Start" ---
    # create an object to store info about Routine WM_P_Start
    WM_P_Start = data.Routine(
        name='WM_P_Start',
        components=[WM_P_Intro, WM_P_Key_Resp],
    )
    WM_P_Start.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for WM_P_Key_Resp
    WM_P_Key_Resp.keys = []
    WM_P_Key_Resp.rt = []
    _WM_P_Key_Resp_allKeys = []
    # store start times for WM_P_Start
    WM_P_Start.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    WM_P_Start.tStart = globalClock.getTime(format='float')
    WM_P_Start.status = STARTED
    thisExp.addData('WM_P_Start.started', WM_P_Start.tStart)
    WM_P_Start.maxDuration = None
    # keep track of which components have finished
    WM_P_StartComponents = WM_P_Start.components
    for thisComponent in WM_P_Start.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "WM_P_Start" ---
    WM_P_Start.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *WM_P_Intro* updates
        
        # if WM_P_Intro is starting this frame...
        if WM_P_Intro.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            WM_P_Intro.frameNStart = frameN  # exact frame index
            WM_P_Intro.tStart = t  # local t and not account for scr refresh
            WM_P_Intro.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(WM_P_Intro, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'WM_P_Intro.started')
            # update status
            WM_P_Intro.status = STARTED
            WM_P_Intro.setAutoDraw(True)
        
        # if WM_P_Intro is active this frame...
        if WM_P_Intro.status == STARTED:
            # update params
            pass
        
        # *WM_P_Key_Resp* updates
        waitOnFlip = False
        
        # if WM_P_Key_Resp is starting this frame...
        if WM_P_Key_Resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            WM_P_Key_Resp.frameNStart = frameN  # exact frame index
            WM_P_Key_Resp.tStart = t  # local t and not account for scr refresh
            WM_P_Key_Resp.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(WM_P_Key_Resp, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'WM_P_Key_Resp.started')
            # update status
            WM_P_Key_Resp.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(WM_P_Key_Resp.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(WM_P_Key_Resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if WM_P_Key_Resp.status == STARTED and not waitOnFlip:
            theseKeys = WM_P_Key_Resp.getKeys(keyList=['s'], ignoreKeys=["escape"], waitRelease=False)
            _WM_P_Key_Resp_allKeys.extend(theseKeys)
            if len(_WM_P_Key_Resp_allKeys):
                WM_P_Key_Resp.keys = _WM_P_Key_Resp_allKeys[-1].name  # just the last key pressed
                WM_P_Key_Resp.rt = _WM_P_Key_Resp_allKeys[-1].rt
                WM_P_Key_Resp.duration = _WM_P_Key_Resp_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer], 
                playbackComponents=[]
            )
            # skip the frame we paused on
            continue
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            WM_P_Start.forceEnded = routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in WM_P_Start.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "WM_P_Start" ---
    for thisComponent in WM_P_Start.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for WM_P_Start
    WM_P_Start.tStop = globalClock.getTime(format='float')
    WM_P_Start.tStopRefresh = tThisFlipGlobal
    thisExp.addData('WM_P_Start.stopped', WM_P_Start.tStop)
    # check responses
    if WM_P_Key_Resp.keys in ['', [], None]:  # No response was made
        WM_P_Key_Resp.keys = None
    thisExp.addData('WM_P_Key_Resp.keys',WM_P_Key_Resp.keys)
    if WM_P_Key_Resp.keys != None:  # we had a response
        thisExp.addData('WM_P_Key_Resp.rt', WM_P_Key_Resp.rt)
        thisExp.addData('WM_P_Key_Resp.duration', WM_P_Key_Resp.duration)
    thisExp.nextEntry()
    # the Routine "WM_P_Start" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # set up handler to look after randomisation of conditions etc
    WM_P_Trials = data.TrialHandler2(
        name='WM_P_Trials',
        nReps=1.0, 
        method='random', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=data.importConditions(
        'WM_P_Objects.csv', 
        selection='1:4'
    )
    , 
        seed=None, 
    )
    thisExp.addLoop(WM_P_Trials)  # add the loop to the experiment
    thisWM_P_Trial = WM_P_Trials.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisWM_P_Trial.rgb)
    if thisWM_P_Trial != None:
        for paramName in thisWM_P_Trial:
            globals()[paramName] = thisWM_P_Trial[paramName]
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    for thisWM_P_Trial in WM_P_Trials:
        currentLoop = WM_P_Trials
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # abbreviate parameter names if possible (e.g. rgb = thisWM_P_Trial.rgb)
        if thisWM_P_Trial != None:
            for paramName in thisWM_P_Trial:
                globals()[paramName] = thisWM_P_Trial[paramName]
        
        # --- Prepare to start Routine "WM_P_Interval" ---
        # create an object to store info about Routine WM_P_Interval
        WM_P_Interval = data.Routine(
            name='WM_P_Interval',
            components=[WM_P_Inter],
        )
        WM_P_Interval.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # store start times for WM_P_Interval
        WM_P_Interval.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        WM_P_Interval.tStart = globalClock.getTime(format='float')
        WM_P_Interval.status = STARTED
        thisExp.addData('WM_P_Interval.started', WM_P_Interval.tStart)
        WM_P_Interval.maxDuration = None
        # keep track of which components have finished
        WM_P_IntervalComponents = WM_P_Interval.components
        for thisComponent in WM_P_Interval.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "WM_P_Interval" ---
        # if trial has changed, end Routine now
        if isinstance(WM_P_Trials, data.TrialHandler2) and thisWM_P_Trial.thisN != WM_P_Trials.thisTrial.thisN:
            continueRoutine = False
        WM_P_Interval.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 1.0:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *WM_P_Inter* updates
            
            # if WM_P_Inter is starting this frame...
            if WM_P_Inter.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                WM_P_Inter.frameNStart = frameN  # exact frame index
                WM_P_Inter.tStart = t  # local t and not account for scr refresh
                WM_P_Inter.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(WM_P_Inter, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'WM_P_Inter.started')
                # update status
                WM_P_Inter.status = STARTED
                WM_P_Inter.setAutoDraw(True)
            
            # if WM_P_Inter is active this frame...
            if WM_P_Inter.status == STARTED:
                # update params
                pass
            
            # if WM_P_Inter is stopping this frame...
            if WM_P_Inter.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > WM_P_Inter.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    WM_P_Inter.tStop = t  # not accounting for scr refresh
                    WM_P_Inter.tStopRefresh = tThisFlipGlobal  # on global time
                    WM_P_Inter.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'WM_P_Inter.stopped')
                    # update status
                    WM_P_Inter.status = FINISHED
                    WM_P_Inter.setAutoDraw(False)
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer], 
                    playbackComponents=[]
                )
                # skip the frame we paused on
                continue
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                WM_P_Interval.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in WM_P_Interval.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "WM_P_Interval" ---
        for thisComponent in WM_P_Interval.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for WM_P_Interval
        WM_P_Interval.tStop = globalClock.getTime(format='float')
        WM_P_Interval.tStopRefresh = tThisFlipGlobal
        thisExp.addData('WM_P_Interval.stopped', WM_P_Interval.tStop)
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if WM_P_Interval.maxDurationReached:
            routineTimer.addTime(-WM_P_Interval.maxDuration)
        elif WM_P_Interval.forceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-1.000000)
        
        # --- Prepare to start Routine "WM_P_Perceive" ---
        # create an object to store info about Routine WM_P_Perceive
        WM_P_Perceive = data.Routine(
            name='WM_P_Perceive',
            components=[WM_P_P_Image1, WM_P_P_Image2, WM_P_P_BG],
        )
        WM_P_Perceive.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # Run 'Begin Routine' code from WM_P_P_Code
        ##### make sure allObjs have same order as the loop file WM_Objects.csv!!!!!!
        allObjs = [
        "bus",
        "sunflower",
        "cabbage",
        "strawberry",
        "pineapple",
        "lizard"
        ]
        
        # Get current index
        i = WM_P_Trials.thisIndex  # or your_trial_handler.thisN
        
        # Wrap-around logic for second image index
        if i >= 3:
            j = i - 3  
        else:
            j = i + 3
        
        # Define image filenames
        img1 = 'imgs_diffusion/' + allObjs[i] + '50.jpg'
        img2 = 'imgs_diffusion/' + allObjs[j] + '50.jpg'  # Object_list is the full list of objects
        
        # Randomize order
        import random
        image_pair = [img1, img2]
        random.shuffle(image_pair)
        
        # Assign to variables used by Image components
        imgA = image_pair[0]
        imgB = image_pair[1]
        WM_P_P_Image1.setImage(imgA)
        WM_P_P_Image2.setImage(imgB)
        # store start times for WM_P_Perceive
        WM_P_Perceive.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        WM_P_Perceive.tStart = globalClock.getTime(format='float')
        WM_P_Perceive.status = STARTED
        thisExp.addData('WM_P_Perceive.started', WM_P_Perceive.tStart)
        WM_P_Perceive.maxDuration = None
        # keep track of which components have finished
        WM_P_PerceiveComponents = WM_P_Perceive.components
        for thisComponent in WM_P_Perceive.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "WM_P_Perceive" ---
        # if trial has changed, end Routine now
        if isinstance(WM_P_Trials, data.TrialHandler2) and thisWM_P_Trial.thisN != WM_P_Trials.thisTrial.thisN:
            continueRoutine = False
        WM_P_Perceive.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 5.0:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *WM_P_P_Image1* updates
            
            # if WM_P_P_Image1 is starting this frame...
            if WM_P_P_Image1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                WM_P_P_Image1.frameNStart = frameN  # exact frame index
                WM_P_P_Image1.tStart = t  # local t and not account for scr refresh
                WM_P_P_Image1.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(WM_P_P_Image1, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'WM_P_P_Image1.started')
                # update status
                WM_P_P_Image1.status = STARTED
                # TODO: add trigger for 'WM_P_P_Image1 start'
                WM_P_P_Image1.setAutoDraw(True)
            
            # if WM_P_P_Image1 is active this frame...
            if WM_P_P_Image1.status == STARTED:
                # update params
                pass
            
            # if WM_P_P_Image1 is stopping this frame...
            if WM_P_P_Image1.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > WM_P_P_Image1.tStartRefresh + 2-frameTolerance:
                    # keep track of stop time/frame for later
                    WM_P_P_Image1.tStop = t  # not accounting for scr refresh
                    WM_P_P_Image1.tStopRefresh = tThisFlipGlobal  # on global time
                    WM_P_P_Image1.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'WM_P_P_Image1.stopped')
                    # update status
                    WM_P_P_Image1.status = FINISHED
                    # TODO: add trigger for 'WM_P_P_Image1 end'
                    WM_P_P_Image1.setAutoDraw(False)
            
            # *WM_P_P_Image2* updates
            
            # if WM_P_P_Image2 is starting this frame...
            if WM_P_P_Image2.status == NOT_STARTED and tThisFlip >= 2.5-frameTolerance:
                # keep track of start time/frame for later
                WM_P_P_Image2.frameNStart = frameN  # exact frame index
                WM_P_P_Image2.tStart = t  # local t and not account for scr refresh
                WM_P_P_Image2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(WM_P_P_Image2, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'WM_P_P_Image2.started')
                # update status
                WM_P_P_Image2.status = STARTED
                # TODO: add trigger for 'WM_P_P_Image2 start'
                WM_P_P_Image2.setAutoDraw(True)
            
            # if WM_P_P_Image2 is active this frame...
            if WM_P_P_Image2.status == STARTED:
                # update params
                pass
            
            # if WM_P_P_Image2 is stopping this frame...
            if WM_P_P_Image2.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > WM_P_P_Image2.tStartRefresh + 2-frameTolerance:
                    # keep track of stop time/frame for later
                    WM_P_P_Image2.tStop = t  # not accounting for scr refresh
                    WM_P_P_Image2.tStopRefresh = tThisFlipGlobal  # on global time
                    WM_P_P_Image2.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'WM_P_P_Image2.stopped')
                    # update status
                    WM_P_P_Image2.status = FINISHED
                    # TODO: add trigger for 'WM_P_P_Image2 end'
                    WM_P_P_Image2.setAutoDraw(False)
            
            # *WM_P_P_BG* updates
            
            # if WM_P_P_BG is starting this frame...
            if WM_P_P_BG.status == NOT_STARTED and tThisFlip >= 4.5-frameTolerance:
                # keep track of start time/frame for later
                WM_P_P_BG.frameNStart = frameN  # exact frame index
                WM_P_P_BG.tStart = t  # local t and not account for scr refresh
                WM_P_P_BG.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(WM_P_P_BG, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'WM_P_P_BG.started')
                # update status
                WM_P_P_BG.status = STARTED
                WM_P_P_BG.setAutoDraw(True)
            
            # if WM_P_P_BG is active this frame...
            if WM_P_P_BG.status == STARTED:
                # update params
                pass
            
            # if WM_P_P_BG is stopping this frame...
            if WM_P_P_BG.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > WM_P_P_BG.tStartRefresh + 0.5-frameTolerance:
                    # keep track of stop time/frame for later
                    WM_P_P_BG.tStop = t  # not accounting for scr refresh
                    WM_P_P_BG.tStopRefresh = tThisFlipGlobal  # on global time
                    WM_P_P_BG.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'WM_P_P_BG.stopped')
                    # update status
                    WM_P_P_BG.status = FINISHED
                    WM_P_P_BG.setAutoDraw(False)
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer], 
                    playbackComponents=[]
                )
                # skip the frame we paused on
                continue
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                WM_P_Perceive.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in WM_P_Perceive.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "WM_P_Perceive" ---
        for thisComponent in WM_P_Perceive.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for WM_P_Perceive
        WM_P_Perceive.tStop = globalClock.getTime(format='float')
        WM_P_Perceive.tStopRefresh = tThisFlipGlobal
        thisExp.addData('WM_P_Perceive.stopped', WM_P_Perceive.tStop)
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if WM_P_Perceive.maxDurationReached:
            routineTimer.addTime(-WM_P_Perceive.maxDuration)
        elif WM_P_Perceive.forceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-5.000000)
        
        # --- Prepare to start Routine "WM_P_WM" ---
        # create an object to store info about Routine WM_P_WM
        WM_P_WM = data.Routine(
            name='WM_P_WM',
            components=[WM_P_WM_BG, WM_P_Cue, WM_P_Sound],
        )
        WM_P_WM.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        WM_P_Cue.setSound('AuditoryPrompt/Cue.mp3', secs=1.0, hamming=True)
        WM_P_Cue.setVolume(1.0, log=False)
        WM_P_Cue.seek(0)
        WM_P_Sound.setSound('AuditoryPrompt/' + allObjs[i] + '.mp3', secs=1.5, hamming=True)
        WM_P_Sound.setVolume(1.0, log=False)
        WM_P_Sound.seek(0)
        # store start times for WM_P_WM
        WM_P_WM.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        WM_P_WM.tStart = globalClock.getTime(format='float')
        WM_P_WM.status = STARTED
        thisExp.addData('WM_P_WM.started', WM_P_WM.tStart)
        WM_P_WM.maxDuration = None
        # keep track of which components have finished
        WM_P_WMComponents = WM_P_WM.components
        for thisComponent in WM_P_WM.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "WM_P_WM" ---
        # if trial has changed, end Routine now
        if isinstance(WM_P_Trials, data.TrialHandler2) and thisWM_P_Trial.thisN != WM_P_Trials.thisTrial.thisN:
            continueRoutine = False
        WM_P_WM.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 6.5:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *WM_P_WM_BG* updates
            
            # if WM_P_WM_BG is starting this frame...
            if WM_P_WM_BG.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                # keep track of start time/frame for later
                WM_P_WM_BG.frameNStart = frameN  # exact frame index
                WM_P_WM_BG.tStart = t  # local t and not account for scr refresh
                WM_P_WM_BG.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(WM_P_WM_BG, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'WM_P_WM_BG.started')
                # update status
                WM_P_WM_BG.status = STARTED
                WM_P_WM_BG.setAutoDraw(True)
            
            # if WM_P_WM_BG is active this frame...
            if WM_P_WM_BG.status == STARTED:
                # update params
                pass
            
            # if WM_P_WM_BG is stopping this frame...
            if WM_P_WM_BG.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > WM_P_WM_BG.tStartRefresh + 6.5-frameTolerance:
                    # keep track of stop time/frame for later
                    WM_P_WM_BG.tStop = t  # not accounting for scr refresh
                    WM_P_WM_BG.tStopRefresh = tThisFlipGlobal  # on global time
                    WM_P_WM_BG.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'WM_P_WM_BG.stopped')
                    # update status
                    WM_P_WM_BG.status = FINISHED
                    # TODO: add trigger for 'WM_P_WM_BG end'
                    WM_P_WM_BG.setAutoDraw(False)
            
            # *WM_P_Cue* updates
            
            # if WM_P_Cue is starting this frame...
            if WM_P_Cue.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                WM_P_Cue.frameNStart = frameN  # exact frame index
                WM_P_Cue.tStart = t  # local t and not account for scr refresh
                WM_P_Cue.tStartRefresh = tThisFlipGlobal  # on global time
                # add timestamp to datafile
                thisExp.addData('WM_P_Cue.started', tThisFlipGlobal)
                # update status
                WM_P_Cue.status = STARTED
                WM_P_Cue.play(when=win)  # sync with win flip
            
            # if WM_P_Cue is stopping this frame...
            if WM_P_Cue.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > WM_P_Cue.tStartRefresh + 1.0-frameTolerance or WM_P_Cue.isFinished:
                    # keep track of stop time/frame for later
                    WM_P_Cue.tStop = t  # not accounting for scr refresh
                    WM_P_Cue.tStopRefresh = tThisFlipGlobal  # on global time
                    WM_P_Cue.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'WM_P_Cue.stopped')
                    # update status
                    WM_P_Cue.status = FINISHED
                    WM_P_Cue.stop()
            
            # *WM_P_Sound* updates
            
            # if WM_P_Sound is starting this frame...
            if WM_P_Sound.status == NOT_STARTED and tThisFlip >= 1-frameTolerance:
                # keep track of start time/frame for later
                WM_P_Sound.frameNStart = frameN  # exact frame index
                WM_P_Sound.tStart = t  # local t and not account for scr refresh
                WM_P_Sound.tStartRefresh = tThisFlipGlobal  # on global time
                # add timestamp to datafile
                thisExp.addData('WM_P_Sound.started', tThisFlipGlobal)
                # update status
                WM_P_Sound.status = STARTED
                # TODO: add trigger for 'WM_P_Sound start'
                WM_P_Sound.play(when=win)  # sync with win flip
            
            # if WM_P_Sound is stopping this frame...
            if WM_P_Sound.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > WM_P_Sound.tStartRefresh + 1.5-frameTolerance or WM_P_Sound.isFinished:
                    # keep track of stop time/frame for later
                    WM_P_Sound.tStop = t  # not accounting for scr refresh
                    WM_P_Sound.tStopRefresh = tThisFlipGlobal  # on global time
                    WM_P_Sound.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'WM_P_Sound.stopped')
                    # update status
                    WM_P_Sound.status = FINISHED
                    # TODO: add trigger for 'WM_P_Sound end'
                    WM_P_Sound.stop()
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer], 
                    playbackComponents=[WM_P_Cue, WM_P_Sound]
                )
                # skip the frame we paused on
                continue
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                WM_P_WM.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in WM_P_WM.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "WM_P_WM" ---
        for thisComponent in WM_P_WM.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for WM_P_WM
        WM_P_WM.tStop = globalClock.getTime(format='float')
        WM_P_WM.tStopRefresh = tThisFlipGlobal
        thisExp.addData('WM_P_WM.stopped', WM_P_WM.tStop)
        WM_P_Cue.pause()  # ensure sound has stopped at end of Routine
        WM_P_Sound.pause()  # ensure sound has stopped at end of Routine
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if WM_P_WM.maxDurationReached:
            routineTimer.addTime(-WM_P_WM.maxDuration)
        elif WM_P_WM.forceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-6.500000)
        
        # --- Prepare to start Routine "WM_P_Test" ---
        # create an object to store info about Routine WM_P_Test
        WM_P_Test = data.Routine(
            name='WM_P_Test',
            components=[WM_P_Test_Image, WM_P_Test_Resp, WM_P_Test_Q, WM_P_Test_Option],
        )
        WM_P_Test.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # Run 'Begin Routine' code from WM_P_Test_Code
        # Get the next image
        WM_P_T_chosen_image = WM_P_T_image_pool[WM_P_T_image_index]
        WM_P_T_image_index += 1
        
        # Set the image for this trial
        # WM_P_Test_Image.setImage('imgs_diffusion/' + Object + WM_P_Test_chosen_image)
        thisExp.addData('chosen_image', WM_P_T_chosen_image)
        WM_P_Test_Image.setImage('imgs_diffusion/' + allObjs[i] + WM_P_T_chosen_image)
        # create starting attributes for WM_P_Test_Resp
        WM_P_Test_Resp.keys = []
        WM_P_Test_Resp.rt = []
        _WM_P_Test_Resp_allKeys = []
        # store start times for WM_P_Test
        WM_P_Test.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        WM_P_Test.tStart = globalClock.getTime(format='float')
        WM_P_Test.status = STARTED
        thisExp.addData('WM_P_Test.started', WM_P_Test.tStart)
        WM_P_Test.maxDuration = None
        # keep track of which components have finished
        WM_P_TestComponents = WM_P_Test.components
        for thisComponent in WM_P_Test.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "WM_P_Test" ---
        # if trial has changed, end Routine now
        if isinstance(WM_P_Trials, data.TrialHandler2) and thisWM_P_Trial.thisN != WM_P_Trials.thisTrial.thisN:
            continueRoutine = False
        WM_P_Test.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *WM_P_Test_Image* updates
            
            # if WM_P_Test_Image is starting this frame...
            if WM_P_Test_Image.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                WM_P_Test_Image.frameNStart = frameN  # exact frame index
                WM_P_Test_Image.tStart = t  # local t and not account for scr refresh
                WM_P_Test_Image.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(WM_P_Test_Image, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'WM_P_Test_Image.started')
                # update status
                WM_P_Test_Image.status = STARTED
                WM_P_Test_Image.setAutoDraw(True)
            
            # if WM_P_Test_Image is active this frame...
            if WM_P_Test_Image.status == STARTED:
                # update params
                pass
            
            # *WM_P_Test_Resp* updates
            waitOnFlip = False
            
            # if WM_P_Test_Resp is starting this frame...
            if WM_P_Test_Resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                WM_P_Test_Resp.frameNStart = frameN  # exact frame index
                WM_P_Test_Resp.tStart = t  # local t and not account for scr refresh
                WM_P_Test_Resp.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(WM_P_Test_Resp, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'WM_P_Test_Resp.started')
                # update status
                WM_P_Test_Resp.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(WM_P_Test_Resp.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(WM_P_Test_Resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if WM_P_Test_Resp.status == STARTED and not waitOnFlip:
                # add button press for 'WM_P_Test_Resp respond', right hand controller, index finger for 's', middle for 'd'
                theseKeys = WM_P_Test_Resp.getKeys(keyList=['s','d'], ignoreKeys=["escape"], waitRelease=False)
                _WM_P_Test_Resp_allKeys.extend(theseKeys)
                if len(_WM_P_Test_Resp_allKeys):
                    WM_P_Test_Resp.keys = _WM_P_Test_Resp_allKeys[-1].name  # just the last key pressed
                    WM_P_Test_Resp.rt = _WM_P_Test_Resp_allKeys[-1].rt
                    WM_P_Test_Resp.duration = _WM_P_Test_Resp_allKeys[-1].duration
                    # a response ends the routine
                    continueRoutine = False
            
            # *WM_P_Test_Q* updates
            
            # if WM_P_Test_Q is starting this frame...
            if WM_P_Test_Q.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                WM_P_Test_Q.frameNStart = frameN  # exact frame index
                WM_P_Test_Q.tStart = t  # local t and not account for scr refresh
                WM_P_Test_Q.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(WM_P_Test_Q, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'WM_P_Test_Q.started')
                # update status
                WM_P_Test_Q.status = STARTED
                WM_P_Test_Q.setAutoDraw(True)
            
            # if WM_P_Test_Q is active this frame...
            if WM_P_Test_Q.status == STARTED:
                # update params
                pass
            
            # *WM_P_Test_Option* updates
            
            # if WM_P_Test_Option is starting this frame...
            if WM_P_Test_Option.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                WM_P_Test_Option.frameNStart = frameN  # exact frame index
                WM_P_Test_Option.tStart = t  # local t and not account for scr refresh
                WM_P_Test_Option.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(WM_P_Test_Option, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'WM_P_Test_Option.started')
                # update status
                WM_P_Test_Option.status = STARTED
                WM_P_Test_Option.setAutoDraw(True)
            
            # if WM_P_Test_Option is active this frame...
            if WM_P_Test_Option.status == STARTED:
                # update params
                pass
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer], 
                    playbackComponents=[]
                )
                # skip the frame we paused on
                continue
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                WM_P_Test.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in WM_P_Test.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "WM_P_Test" ---
        for thisComponent in WM_P_Test.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for WM_P_Test
        WM_P_Test.tStop = globalClock.getTime(format='float')
        WM_P_Test.tStopRefresh = tThisFlipGlobal
        thisExp.addData('WM_P_Test.stopped', WM_P_Test.tStop)
        # check responses
        if WM_P_Test_Resp.keys in ['', [], None]:  # No response was made
            WM_P_Test_Resp.keys = None
        WM_P_Trials.addData('WM_P_Test_Resp.keys',WM_P_Test_Resp.keys)
        if WM_P_Test_Resp.keys != None:  # we had a response
            WM_P_Trials.addData('WM_P_Test_Resp.rt', WM_P_Test_Resp.rt)
            WM_P_Trials.addData('WM_P_Test_Resp.duration', WM_P_Test_Resp.duration)
        # the Routine "WM_P_Test" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
        thisExp.nextEntry()
        
    # completed 1.0 repeats of 'WM_P_Trials'
    
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    # --- Prepare to start Routine "WM_P_End" ---
    # create an object to store info about Routine WM_P_End
    WM_P_End = data.Routine(
        name='WM_P_End',
        components=[text_3],
    )
    WM_P_End.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # store start times for WM_P_End
    WM_P_End.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    WM_P_End.tStart = globalClock.getTime(format='float')
    WM_P_End.status = STARTED
    thisExp.addData('WM_P_End.started', WM_P_End.tStart)
    WM_P_End.maxDuration = None
    # keep track of which components have finished
    WM_P_EndComponents = WM_P_End.components
    for thisComponent in WM_P_End.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "WM_P_End" ---
    WM_P_End.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_3* updates
        
        # if text_3 is starting this frame...
        if text_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_3.frameNStart = frameN  # exact frame index
            text_3.tStart = t  # local t and not account for scr refresh
            text_3.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_3, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'text_3.started')
            # update status
            text_3.status = STARTED
            text_3.setAutoDraw(True)
        
        # if text_3 is active this frame...
        if text_3.status == STARTED:
            # update params
            pass
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer], 
                playbackComponents=[]
            )
            # skip the frame we paused on
            continue
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            WM_P_End.forceEnded = routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in WM_P_End.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "WM_P_End" ---
    for thisComponent in WM_P_End.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for WM_P_End
    WM_P_End.tStop = globalClock.getTime(format='float')
    WM_P_End.tStopRefresh = tThisFlipGlobal
    thisExp.addData('WM_P_End.stopped', WM_P_End.tStop)
    thisExp.nextEntry()
    # the Routine "WM_P_End" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # mark experiment as finished
    endExperiment(thisExp, win=win)


def saveData(thisExp):
    """
    Save data from this experiment
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    filename = thisExp.dataFileName
    # these shouldn't be strictly necessary (should auto-save)
    thisExp.saveAsWideText(filename + '.csv', delim='auto')
    thisExp.saveAsPickle(filename)


def endExperiment(thisExp, win=None):
    """
    End this experiment, performing final shut down operations.
    
    This function does NOT close the window or end the Python process - use `quit` for this.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    """
    if win is not None:
        # remove autodraw from all current components
        win.clearAutoDraw()
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed
        win.flip()
    # return console logger level to WARNING
    logging.console.setLevel(logging.WARNING)
    # mark experiment handler as finished
    thisExp.status = FINISHED
    logging.flush()


def quit(thisExp, win=None, thisSession=None):
    """
    Fully quit, closing the window and ending the Python process.
    
    Parameters
    ==========
    win : psychopy.visual.Window
        Window to close.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    thisExp.abort()  # or data files will save again on exit
    # make sure everything is closed down
    if win is not None:
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed before quitting
        win.flip()
        win.close()
    logging.flush()
    if thisSession is not None:
        thisSession.stop()
    # terminate Python process
    core.quit()


# if running this experiment as a script...
if __name__ == '__main__':
    # call all functions in order
    expInfo = showExpInfoDlg(expInfo=expInfo)
    thisExp = setupData(expInfo=expInfo)
    logFile = setupLogging(filename=thisExp.dataFileName)
    win = setupWindow(expInfo=expInfo)
    setupDevices(expInfo=expInfo, thisExp=thisExp, win=win)
    run(
        expInfo=expInfo, 
        thisExp=thisExp, 
        win=win,
        globalClock='float'
    )
    saveData(thisExp=thisExp)
    quit(thisExp=thisExp, win=win)
