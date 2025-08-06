#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2024.2.4),
    on July 30, 2025, at 21:48
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

#



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
        originPath='D:\\NYUAD\\Visual_Imagery\\Experiment\\Visual_Imagery_WM_MEG\\Visual_Imagery\\visual_imagery_lastrun.py',
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
    if deviceManager.getDevice('VI_Key_Resp1') is None:
        # initialise VI_Key_Resp1
        VI_Key_Resp1 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='VI_Key_Resp1',
        )
    # create speaker 'VI_Sound'
    deviceManager.addDevice(
        deviceName='VI_Sound',
        deviceClass='psychopy.hardware.speaker.SpeakerDevice',
        index=-1
    )
    # create speaker 'VI_Cue'
    deviceManager.addDevice(
        deviceName='VI_Cue',
        deviceClass='psychopy.hardware.speaker.SpeakerDevice',
        index=-1
    )
    if deviceManager.getDevice('VI_Key_Resp2') is None:
        # initialise VI_Key_Resp2
        VI_Key_Resp2 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='VI_Key_Resp2',
        )
    if deviceManager.getDevice('VI_CQ_Key_Resp') is None:
        # initialise VI_CQ_Key_Resp
        VI_CQ_Key_Resp = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='VI_CQ_Key_Resp',
        )
    if deviceManager.getDevice('B_Break_Resp') is None:
        # initialise B_Break_Resp
        B_Break_Resp = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='B_Break_Resp',
        )
    if deviceManager.getDevice('End_Key_Resp') is None:
        # initialise End_Key_Resp
        End_Key_Resp = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='End_Key_Resp',
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
    
    # --- Initialize components for Routine "B1_Start" ---
    VI_Intro = visual.TextStim(win=win, name='VI_Intro',
        text='Now the Official Experiment Will Begin.\n\nThe procedure is the same as in the practice round, but no reference images will be shown during the vividness rating stage.\n\nPlease let the experimenter know when you are ready to begin.',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    VI_Key_Resp1 = keyboard.Keyboard(deviceName='VI_Key_Resp1')
    
    # --- Initialize components for Routine "VI_Interval" ---
    VI_Inter = visual.ImageStim(
        win=win,
        name='VI_Inter', 
        image=None, mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(0.5, 0.5),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    
    # --- Initialize components for Routine "VI_Imagine" ---
    VI_BG = visual.ImageStim(
        win=win,
        name='VI_BG', 
        image=None, mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(0.5, 0.5),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    VI_Sound = sound.Sound(
        'A', 
        secs=1.5, 
        stereo=True, 
        hamming=True, 
        speaker='VI_Sound',    name='VI_Sound'
    )
    VI_Sound.setVolume(1.0)
    VI_Cue = sound.Sound(
        'A', 
        secs=1.0, 
        stereo=True, 
        hamming=True, 
        speaker='VI_Cue',    name='VI_Cue'
    )
    VI_Cue.setVolume(1.0)
    
    # --- Initialize components for Routine "VI_Rate" ---
    VI_RateText = visual.TextStim(win=win, name='VI_RateText',
        text='Please rate the clarity of your imagination.',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=10.0, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    VI_Key_Resp2 = keyboard.Keyboard(deviceName='VI_Key_Resp2')
    
    # --- Initialize components for Routine "VI_Catch" ---
    VI_CQ = visual.TextStim(win=win, name='VI_CQ',
        text='',
        font='Arial',
        pos=(0, 0.12), draggable=False, height=0.1, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    VI_CQ_Option = visual.TextStim(win=win, name='VI_CQ_Option',
        text="YES      NO      DON'T KNOW",
        font='Arial',
        pos=(0, -0.1), draggable=False, height=0.07, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    VI_CQ_Key_Resp = keyboard.Keyboard(deviceName='VI_CQ_Key_Resp')
    
    # --- Initialize components for Routine "B_Inter" ---
    B_Break = visual.TextStim(win=win, name='B_Break',
        text='You just completed a block. Now you can have a rest.\n\nPlease let the experimenter know when you are ready to continue.',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    B_Break_Resp = keyboard.Keyboard(deviceName='B_Break_Resp')
    
    # --- Initialize components for Routine "End" ---
    End_Text = visual.TextStim(win=win, name='End_Text',
        text='End of visual imagery.',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    End_Key_Resp = keyboard.Keyboard(deviceName='End_Key_Resp')
    
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
    
    # --- Prepare to start Routine "B1_Start" ---
    # create an object to store info about Routine B1_Start
    B1_Start = data.Routine(
        name='B1_Start',
        components=[VI_Intro, VI_Key_Resp1],
    )
    B1_Start.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for VI_Key_Resp1
    VI_Key_Resp1.keys = []
    VI_Key_Resp1.rt = []
    _VI_Key_Resp1_allKeys = []
    # store start times for B1_Start
    B1_Start.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    B1_Start.tStart = globalClock.getTime(format='float')
    B1_Start.status = STARTED
    thisExp.addData('B1_Start.started', B1_Start.tStart)
    B1_Start.maxDuration = None
    # keep track of which components have finished
    B1_StartComponents = B1_Start.components
    for thisComponent in B1_Start.components:
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
    
    # --- Run Routine "B1_Start" ---
    B1_Start.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *VI_Intro* updates
        
        # if VI_Intro is starting this frame...
        if VI_Intro.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            VI_Intro.frameNStart = frameN  # exact frame index
            VI_Intro.tStart = t  # local t and not account for scr refresh
            VI_Intro.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(VI_Intro, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'VI_Intro.started')
            # update status
            VI_Intro.status = STARTED
            VI_Intro.setAutoDraw(True)
        
        # if VI_Intro is active this frame...
        if VI_Intro.status == STARTED:
            # update params
            pass
        
        # *VI_Key_Resp1* updates
        waitOnFlip = False
        
        # if VI_Key_Resp1 is starting this frame...
        if VI_Key_Resp1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            VI_Key_Resp1.frameNStart = frameN  # exact frame index
            VI_Key_Resp1.tStart = t  # local t and not account for scr refresh
            VI_Key_Resp1.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(VI_Key_Resp1, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'VI_Key_Resp1.started')
            # update status
            VI_Key_Resp1.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(VI_Key_Resp1.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(VI_Key_Resp1.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if VI_Key_Resp1.status == STARTED and not waitOnFlip:
            theseKeys = VI_Key_Resp1.getKeys(keyList=['s'], ignoreKeys=["escape"], waitRelease=False)
            _VI_Key_Resp1_allKeys.extend(theseKeys)
            if len(_VI_Key_Resp1_allKeys):
                VI_Key_Resp1.keys = _VI_Key_Resp1_allKeys[-1].name  # just the last key pressed
                VI_Key_Resp1.rt = _VI_Key_Resp1_allKeys[-1].rt
                VI_Key_Resp1.duration = _VI_Key_Resp1_allKeys[-1].duration
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
            B1_Start.forceEnded = routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in B1_Start.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # --- Ending Routine "B1_Start" ---
    for thisComponent in B1_Start.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for B1_Start
    B1_Start.tStop = globalClock.getTime(format='float')
    B1_Start.tStopRefresh = tThisFlipGlobal
    thisExp.addData('B1_Start.stopped', B1_Start.tStop)
    # check responses
    if VI_Key_Resp1.keys in ['', [], None]:  # No response was made
        VI_Key_Resp1.keys = None
    thisExp.addData('VI_Key_Resp1.keys',VI_Key_Resp1.keys)
    if VI_Key_Resp1.keys != None:  # we had a response
        thisExp.addData('VI_Key_Resp1.rt', VI_Key_Resp1.rt)
        thisExp.addData('VI_Key_Resp1.duration', VI_Key_Resp1.duration)
    thisExp.nextEntry()
    # the Routine "B1_Start" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # set up handler to look after randomisation of conditions etc
    Blocks = data.TrialHandler2(
        name='Blocks',
        nReps=1.0, 
        method='random', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=data.importConditions('VI_Blocks.csv'), 
        seed=None, 
    )
    thisExp.addLoop(Blocks)  # add the loop to the experiment
    thisBlock = Blocks.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisBlock.rgb)
    if thisBlock != None:
        for paramName in thisBlock:
            globals()[paramName] = thisBlock[paramName]
    
    for thisBlock in Blocks:
        currentLoop = Blocks
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        # abbreviate parameter names if possible (e.g. rgb = thisBlock.rgb)
        if thisBlock != None:
            for paramName in thisBlock:
                globals()[paramName] = thisBlock[paramName]
        
        # set up handler to look after randomisation of conditions etc
        Trials = data.TrialHandler2(
            name='Trials',
            nReps=1.0, 
            method='random', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=data.importConditions(Trial_File), 
            seed=None, 
        )
        thisExp.addLoop(Trials)  # add the loop to the experiment
        thisTrial = Trials.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
        if thisTrial != None:
            for paramName in thisTrial:
                globals()[paramName] = thisTrial[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisTrial in Trials:
            currentLoop = Trials
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
            if thisTrial != None:
                for paramName in thisTrial:
                    globals()[paramName] = thisTrial[paramName]
            
            # --- Prepare to start Routine "VI_Interval" ---
            # create an object to store info about Routine VI_Interval
            VI_Interval = data.Routine(
                name='VI_Interval',
                components=[VI_Inter],
            )
            VI_Interval.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # store start times for VI_Interval
            VI_Interval.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            VI_Interval.tStart = globalClock.getTime(format='float')
            VI_Interval.status = STARTED
            thisExp.addData('VI_Interval.started', VI_Interval.tStart)
            VI_Interval.maxDuration = None
            # keep track of which components have finished
            VI_IntervalComponents = VI_Interval.components
            for thisComponent in VI_Interval.components:
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
            
            # --- Run Routine "VI_Interval" ---
            # if trial has changed, end Routine now
            if isinstance(Trials, data.TrialHandler2) and thisTrial.thisN != Trials.thisTrial.thisN:
                continueRoutine = False
            VI_Interval.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine and routineTimer.getTime() < 1.0:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *VI_Inter* updates
                
                # if VI_Inter is starting this frame...
                if VI_Inter.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    VI_Inter.frameNStart = frameN  # exact frame index
                    VI_Inter.tStart = t  # local t and not account for scr refresh
                    VI_Inter.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(VI_Inter, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'VI_Inter.started')
                    # update status
                    VI_Inter.status = STARTED
                    VI_Inter.setAutoDraw(True)
                
                # if VI_Inter is active this frame...
                if VI_Inter.status == STARTED:
                    # update params
                    pass
                
                # if VI_Inter is stopping this frame...
                if VI_Inter.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > VI_Inter.tStartRefresh + 1-frameTolerance:
                        # keep track of stop time/frame for later
                        VI_Inter.tStop = t  # not accounting for scr refresh
                        VI_Inter.tStopRefresh = tThisFlipGlobal  # on global time
                        VI_Inter.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'VI_Inter.stopped')
                        # update status
                        VI_Inter.status = FINISHED
                        VI_Inter.setAutoDraw(False)
                
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
                    VI_Interval.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in VI_Interval.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "VI_Interval" ---
            for thisComponent in VI_Interval.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for VI_Interval
            VI_Interval.tStop = globalClock.getTime(format='float')
            VI_Interval.tStopRefresh = tThisFlipGlobal
            thisExp.addData('VI_Interval.stopped', VI_Interval.tStop)
            # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
            if VI_Interval.maxDurationReached:
                routineTimer.addTime(-VI_Interval.maxDuration)
            elif VI_Interval.forceEnded:
                routineTimer.reset()
            else:
                routineTimer.addTime(-1.000000)
            
            # --- Prepare to start Routine "VI_Imagine" ---
            # create an object to store info about Routine VI_Imagine
            VI_Imagine = data.Routine(
                name='VI_Imagine',
                components=[VI_BG, VI_Sound, VI_Cue],
            )
            VI_Imagine.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            VI_Sound.setSound('AuditoryPrompt/' + Object + '.mp3', secs=1.5, hamming=True)
            VI_Sound.setVolume(1.0, log=False)
            VI_Sound.seek(0)
            VI_Cue.setSound('AuditoryPrompt/Cue.mp3', secs=1.0, hamming=True)
            VI_Cue.setVolume(1.0, log=False)
            VI_Cue.seek(0)
            # store start times for VI_Imagine
            VI_Imagine.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            VI_Imagine.tStart = globalClock.getTime(format='float')
            VI_Imagine.status = STARTED
            thisExp.addData('VI_Imagine.started', VI_Imagine.tStart)
            VI_Imagine.maxDuration = None
            # keep track of which components have finished
            VI_ImagineComponents = VI_Imagine.components
            for thisComponent in VI_Imagine.components:
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
            
            # --- Run Routine "VI_Imagine" ---
            # if trial has changed, end Routine now
            if isinstance(Trials, data.TrialHandler2) and thisTrial.thisN != Trials.thisTrial.thisN:
                continueRoutine = False
            VI_Imagine.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine and routineTimer.getTime() < 6.5:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *VI_BG* updates
                
                # if VI_BG is starting this frame...
                if VI_BG.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    VI_BG.frameNStart = frameN  # exact frame index
                    VI_BG.tStart = t  # local t and not account for scr refresh
                    VI_BG.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(VI_BG, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'VI_BG.started')
                    # update status
                    VI_BG.status = STARTED
                    VI_BG.setAutoDraw(True)
                
                # if VI_BG is active this frame...
                if VI_BG.status == STARTED:
                    # update params
                    pass
                
                # if VI_BG is stopping this frame...
                if VI_BG.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > VI_BG.tStartRefresh + 6.5-frameTolerance:
                        # keep track of stop time/frame for later
                        VI_BG.tStop = t  # not accounting for scr refresh
                        VI_BG.tStopRefresh = tThisFlipGlobal  # on global time
                        VI_BG.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'VI_BG.stopped')
                        # update status
                        VI_BG.status = FINISHED
                        VI_BG.setAutoDraw(False)
                
                # *VI_Sound* updates
                
                # if VI_Sound is starting this frame...
                if VI_Sound.status == NOT_STARTED and t >= 1.0-frameTolerance:
                    # keep track of start time/frame for later
                    VI_Sound.frameNStart = frameN  # exact frame index
                    VI_Sound.tStart = t  # local t and not account for scr refresh
                    VI_Sound.tStartRefresh = tThisFlipGlobal  # on global time
                    # add timestamp to datafile
                    thisExp.addData('VI_Sound.started', t)
                    # update status
                    VI_Sound.status = STARTED
                    # TODO: Add trigger for sound play
                    VI_Sound.play()  # start the sound (it finishes automatically)


                # if VI_Sound is stopping this frame...
                if VI_Sound.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > VI_Sound.tStartRefresh + 1.5-frameTolerance or VI_Sound.isFinished:
                        # keep track of stop time/frame for later
                        VI_Sound.tStop = t  # not accounting for scr refresh
                        VI_Sound.tStopRefresh = tThisFlipGlobal  # on global time
                        VI_Sound.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.addData('VI_Sound.stopped', t)
                        # update status
                        VI_Sound.status = FINISHED
                        VI_Sound.stop()
                
                # *VI_Cue* updates
                
                # if VI_Cue is starting this frame...
                if VI_Cue.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    VI_Cue.frameNStart = frameN  # exact frame index
                    VI_Cue.tStart = t  # local t and not account for scr refresh
                    VI_Cue.tStartRefresh = tThisFlipGlobal  # on global time
                    # add timestamp to datafile
                    thisExp.addData('VI_Cue.started', tThisFlipGlobal)
                    # update status
                    VI_Cue.status = STARTED
                    VI_Cue.play(when=win)  # sync with win flip
                
                # if VI_Cue is stopping this frame...
                if VI_Cue.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > VI_Cue.tStartRefresh + 1.0-frameTolerance or VI_Cue.isFinished:
                        # keep track of stop time/frame for later
                        VI_Cue.tStop = t  # not accounting for scr refresh
                        VI_Cue.tStopRefresh = tThisFlipGlobal  # on global time
                        VI_Cue.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'VI_Cue.stopped')
                        # update status
                        VI_Cue.status = FINISHED
                        VI_Cue.stop()
                
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
                        playbackComponents=[VI_Sound, VI_Cue]
                    )
                    # skip the frame we paused on
                    continue
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    VI_Imagine.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in VI_Imagine.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "VI_Imagine" ---
            for thisComponent in VI_Imagine.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for VI_Imagine
            VI_Imagine.tStop = globalClock.getTime(format='float')
            VI_Imagine.tStopRefresh = tThisFlipGlobal
            thisExp.addData('VI_Imagine.stopped', VI_Imagine.tStop)
            VI_Sound.pause()  # ensure sound has stopped at end of Routine
            VI_Cue.pause()  # ensure sound has stopped at end of Routine
            # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
            if VI_Imagine.maxDurationReached:
                routineTimer.addTime(-VI_Imagine.maxDuration)
            elif VI_Imagine.forceEnded:
                routineTimer.reset()
            else:
                routineTimer.addTime(-6.500000)
            
            # --- Prepare to start Routine "VI_Rate" ---
            # create an object to store info about Routine VI_Rate
            VI_Rate = data.Routine(
                name='VI_Rate',
                components=[VI_RateText, VI_Key_Resp2],
            )
            VI_Rate.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # create starting attributes for VI_Key_Resp2
            VI_Key_Resp2.keys = []
            VI_Key_Resp2.rt = []
            _VI_Key_Resp2_allKeys = []
            # store start times for VI_Rate
            VI_Rate.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            VI_Rate.tStart = globalClock.getTime(format='float')
            VI_Rate.status = STARTED
            thisExp.addData('VI_Rate.started', VI_Rate.tStart)
            VI_Rate.maxDuration = None
            # keep track of which components have finished
            VI_RateComponents = VI_Rate.components
            for thisComponent in VI_Rate.components:
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
            
            # --- Run Routine "VI_Rate" ---
            # if trial has changed, end Routine now
            if isinstance(Trials, data.TrialHandler2) and thisTrial.thisN != Trials.thisTrial.thisN:
                continueRoutine = False
            VI_Rate.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *VI_RateText* updates
                
                # if VI_RateText is starting this frame...
                if VI_RateText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    VI_RateText.frameNStart = frameN  # exact frame index
                    VI_RateText.tStart = t  # local t and not account for scr refresh
                    VI_RateText.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(VI_RateText, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'VI_RateText.started')
                    # update status
                    VI_RateText.status = STARTED
                    VI_RateText.setAutoDraw(True)
                
                # if VI_RateText is active this frame...
                if VI_RateText.status == STARTED:
                    # update params
                    pass
                
                # *VI_Key_Resp2* updates
                waitOnFlip = False
                
                # if VI_Key_Resp2 is starting this frame...
                if VI_Key_Resp2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    VI_Key_Resp2.frameNStart = frameN  # exact frame index
                    VI_Key_Resp2.tStart = t  # local t and not account for scr refresh
                    VI_Key_Resp2.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(VI_Key_Resp2, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'VI_Key_Resp2.started')
                    # update status
                    VI_Key_Resp2.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(VI_Key_Resp2.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(VI_Key_Resp2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if VI_Key_Resp2.status == STARTED and not waitOnFlip:
                    theseKeys = VI_Key_Resp2.getKeys(keyList=['1','2','3','4','5'], ignoreKeys=["escape"], waitRelease=False)
                    _VI_Key_Resp2_allKeys.extend(theseKeys)
                    if len(_VI_Key_Resp2_allKeys):
                        VI_Key_Resp2.keys = _VI_Key_Resp2_allKeys[-1].name  # just the last key pressed
                        VI_Key_Resp2.rt = _VI_Key_Resp2_allKeys[-1].rt
                        VI_Key_Resp2.duration = _VI_Key_Resp2_allKeys[-1].duration
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
                    VI_Rate.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in VI_Rate.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "VI_Rate" ---
            for thisComponent in VI_Rate.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for VI_Rate
            VI_Rate.tStop = globalClock.getTime(format='float')
            VI_Rate.tStopRefresh = tThisFlipGlobal
            thisExp.addData('VI_Rate.stopped', VI_Rate.tStop)
            # check responses
            if VI_Key_Resp2.keys in ['', [], None]:  # No response was made
                VI_Key_Resp2.keys = None
            Trials.addData('VI_Key_Resp2.keys',VI_Key_Resp2.keys)
            if VI_Key_Resp2.keys != None:  # we had a response
                Trials.addData('VI_Key_Resp2.rt', VI_Key_Resp2.rt)
                Trials.addData('VI_Key_Resp2.duration', VI_Key_Resp2.duration)
            # the Routine "VI_Rate" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # --- Prepare to start Routine "VI_Catch" ---
            # create an object to store info about Routine VI_Catch
            VI_Catch = data.Routine(
                name='VI_Catch',
                components=[VI_CQ, VI_CQ_Option, VI_CQ_Key_Resp],
            )
            VI_Catch.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            VI_CQ.setText(CatchQuestion)
            # create starting attributes for VI_CQ_Key_Resp
            VI_CQ_Key_Resp.keys = []
            VI_CQ_Key_Resp.rt = []
            _VI_CQ_Key_Resp_allKeys = []
            # store start times for VI_Catch
            VI_Catch.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            VI_Catch.tStart = globalClock.getTime(format='float')
            VI_Catch.status = STARTED
            thisExp.addData('VI_Catch.started', VI_Catch.tStart)
            VI_Catch.maxDuration = None
            # keep track of which components have finished
            VI_CatchComponents = VI_Catch.components
            for thisComponent in VI_Catch.components:
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
            
            # --- Run Routine "VI_Catch" ---
            # if trial has changed, end Routine now
            if isinstance(Trials, data.TrialHandler2) and thisTrial.thisN != Trials.thisTrial.thisN:
                continueRoutine = False
            VI_Catch.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *VI_CQ* updates
                
                # if VI_CQ is starting this frame...
                if VI_CQ.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    VI_CQ.frameNStart = frameN  # exact frame index
                    VI_CQ.tStart = t  # local t and not account for scr refresh
                    VI_CQ.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(VI_CQ, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'VI_CQ.started')
                    # update status
                    VI_CQ.status = STARTED
                    VI_CQ.setAutoDraw(True)
                
                # if VI_CQ is active this frame...
                if VI_CQ.status == STARTED:
                    # update params
                    pass
                
                # *VI_CQ_Option* updates
                
                # if VI_CQ_Option is starting this frame...
                if VI_CQ_Option.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    VI_CQ_Option.frameNStart = frameN  # exact frame index
                    VI_CQ_Option.tStart = t  # local t and not account for scr refresh
                    VI_CQ_Option.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(VI_CQ_Option, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'VI_CQ_Option.started')
                    # update status
                    VI_CQ_Option.status = STARTED
                    VI_CQ_Option.setAutoDraw(True)
                
                # if VI_CQ_Option is active this frame...
                if VI_CQ_Option.status == STARTED:
                    # update params
                    pass
                
                # *VI_CQ_Key_Resp* updates
                waitOnFlip = False
                
                # if VI_CQ_Key_Resp is starting this frame...
                if VI_CQ_Key_Resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    VI_CQ_Key_Resp.frameNStart = frameN  # exact frame index
                    VI_CQ_Key_Resp.tStart = t  # local t and not account for scr refresh
                    VI_CQ_Key_Resp.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(VI_CQ_Key_Resp, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'VI_CQ_Key_Resp.started')
                    # update status
                    VI_CQ_Key_Resp.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(VI_CQ_Key_Resp.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(VI_CQ_Key_Resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if VI_CQ_Key_Resp.status == STARTED and not waitOnFlip:
                    theseKeys = VI_CQ_Key_Resp.getKeys(keyList=['s','d','f'], ignoreKeys=["escape"], waitRelease=False)
                    _VI_CQ_Key_Resp_allKeys.extend(theseKeys)
                    if len(_VI_CQ_Key_Resp_allKeys):
                        VI_CQ_Key_Resp.keys = _VI_CQ_Key_Resp_allKeys[-1].name  # just the last key pressed
                        VI_CQ_Key_Resp.rt = _VI_CQ_Key_Resp_allKeys[-1].rt
                        VI_CQ_Key_Resp.duration = _VI_CQ_Key_Resp_allKeys[-1].duration
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
                    VI_Catch.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in VI_Catch.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "VI_Catch" ---
            for thisComponent in VI_Catch.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for VI_Catch
            VI_Catch.tStop = globalClock.getTime(format='float')
            VI_Catch.tStopRefresh = tThisFlipGlobal
            thisExp.addData('VI_Catch.stopped', VI_Catch.tStop)
            # check responses
            if VI_CQ_Key_Resp.keys in ['', [], None]:  # No response was made
                VI_CQ_Key_Resp.keys = None
            Trials.addData('VI_CQ_Key_Resp.keys',VI_CQ_Key_Resp.keys)
            if VI_CQ_Key_Resp.keys != None:  # we had a response
                Trials.addData('VI_CQ_Key_Resp.rt', VI_CQ_Key_Resp.rt)
                Trials.addData('VI_CQ_Key_Resp.duration', VI_CQ_Key_Resp.duration)
            # the Routine "VI_Catch" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            thisExp.nextEntry()
            
        # completed 1.0 repeats of 'Trials'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        # --- Prepare to start Routine "B_Inter" ---
        # create an object to store info about Routine B_Inter
        B_Inter = data.Routine(
            name='B_Inter',
            components=[B_Break, B_Break_Resp],
        )
        B_Inter.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # create starting attributes for B_Break_Resp
        B_Break_Resp.keys = []
        B_Break_Resp.rt = []
        _B_Break_Resp_allKeys = []
        # store start times for B_Inter
        B_Inter.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        B_Inter.tStart = globalClock.getTime(format='float')
        B_Inter.status = STARTED
        thisExp.addData('B_Inter.started', B_Inter.tStart)
        B_Inter.maxDuration = None
        # keep track of which components have finished
        B_InterComponents = B_Inter.components
        for thisComponent in B_Inter.components:
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
        
        # --- Run Routine "B_Inter" ---
        # if trial has changed, end Routine now
        if isinstance(Blocks, data.TrialHandler2) and thisBlock.thisN != Blocks.thisTrial.thisN:
            continueRoutine = False
        B_Inter.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *B_Break* updates
            
            # if B_Break is starting this frame...
            if B_Break.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                B_Break.frameNStart = frameN  # exact frame index
                B_Break.tStart = t  # local t and not account for scr refresh
                B_Break.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(B_Break, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'B_Break.started')
                # update status
                B_Break.status = STARTED
                B_Break.setAutoDraw(True)
            
            # if B_Break is active this frame...
            if B_Break.status == STARTED:
                # update params
                pass
            
            # *B_Break_Resp* updates
            waitOnFlip = False
            
            # if B_Break_Resp is starting this frame...
            if B_Break_Resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                B_Break_Resp.frameNStart = frameN  # exact frame index
                B_Break_Resp.tStart = t  # local t and not account for scr refresh
                B_Break_Resp.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(B_Break_Resp, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'B_Break_Resp.started')
                # update status
                B_Break_Resp.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(B_Break_Resp.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(B_Break_Resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if B_Break_Resp.status == STARTED and not waitOnFlip:
                theseKeys = B_Break_Resp.getKeys(keyList=['s'], ignoreKeys=["escape"], waitRelease=False)
                _B_Break_Resp_allKeys.extend(theseKeys)
                if len(_B_Break_Resp_allKeys):
                    B_Break_Resp.keys = _B_Break_Resp_allKeys[-1].name  # just the last key pressed
                    B_Break_Resp.rt = _B_Break_Resp_allKeys[-1].rt
                    B_Break_Resp.duration = _B_Break_Resp_allKeys[-1].duration
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
                B_Inter.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in B_Inter.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "B_Inter" ---
        for thisComponent in B_Inter.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for B_Inter
        B_Inter.tStop = globalClock.getTime(format='float')
        B_Inter.tStopRefresh = tThisFlipGlobal
        thisExp.addData('B_Inter.stopped', B_Inter.tStop)
        # check responses
        if B_Break_Resp.keys in ['', [], None]:  # No response was made
            B_Break_Resp.keys = None
        Blocks.addData('B_Break_Resp.keys',B_Break_Resp.keys)
        if B_Break_Resp.keys != None:  # we had a response
            Blocks.addData('B_Break_Resp.rt', B_Break_Resp.rt)
            Blocks.addData('B_Break_Resp.duration', B_Break_Resp.duration)
        # the Routine "B_Inter" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
    # completed 1.0 repeats of 'Blocks'
    
    
    # --- Prepare to start Routine "End" ---
    # create an object to store info about Routine End
    End = data.Routine(
        name='End',
        components=[End_Text, End_Key_Resp],
    )
    End.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for End_Key_Resp
    End_Key_Resp.keys = []
    End_Key_Resp.rt = []
    _End_Key_Resp_allKeys = []
    # store start times for End
    End.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    End.tStart = globalClock.getTime(format='float')
    End.status = STARTED
    thisExp.addData('End.started', End.tStart)
    End.maxDuration = None
    # keep track of which components have finished
    EndComponents = End.components
    for thisComponent in End.components:
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
    
    # --- Run Routine "End" ---
    End.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *End_Text* updates
        
        # if End_Text is starting this frame...
        if End_Text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            End_Text.frameNStart = frameN  # exact frame index
            End_Text.tStart = t  # local t and not account for scr refresh
            End_Text.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(End_Text, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'End_Text.started')
            # update status
            End_Text.status = STARTED
            End_Text.setAutoDraw(True)
        
        # if End_Text is active this frame...
        if End_Text.status == STARTED:
            # update params
            pass
        
        # *End_Key_Resp* updates
        waitOnFlip = False
        
        # if End_Key_Resp is starting this frame...
        if End_Key_Resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            End_Key_Resp.frameNStart = frameN  # exact frame index
            End_Key_Resp.tStart = t  # local t and not account for scr refresh
            End_Key_Resp.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(End_Key_Resp, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'End_Key_Resp.started')
            # update status
            End_Key_Resp.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(End_Key_Resp.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(End_Key_Resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if End_Key_Resp.status == STARTED and not waitOnFlip:
            theseKeys = End_Key_Resp.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _End_Key_Resp_allKeys.extend(theseKeys)
            if len(_End_Key_Resp_allKeys):
                End_Key_Resp.keys = _End_Key_Resp_allKeys[-1].name  # just the last key pressed
                End_Key_Resp.rt = _End_Key_Resp_allKeys[-1].rt
                End_Key_Resp.duration = _End_Key_Resp_allKeys[-1].duration
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
            End.forceEnded = routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in End.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "End" ---
    for thisComponent in End.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for End
    End.tStop = globalClock.getTime(format='float')
    End.tStopRefresh = tThisFlipGlobal
    thisExp.addData('End.stopped', End.tStop)
    # check responses
    if End_Key_Resp.keys in ['', [], None]:  # No response was made
        End_Key_Resp.keys = None
    thisExp.addData('End_Key_Resp.keys',End_Key_Resp.keys)
    if End_Key_Resp.keys != None:  # we had a response
        thisExp.addData('End_Key_Resp.rt', End_Key_Resp.rt)
        thisExp.addData('End_Key_Resp.duration', End_Key_Resp.duration)
    thisExp.nextEntry()
    # the Routine "End" was not non-slip safe, so reset the non-slip timer
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
