#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2024.2.4),
    on July 30, 2025, at 21:42
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

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
        originPath='D:\\NYUAD\\Visual_Imagery\\Experiment\\Visual_Imagery_WM_MEG\\Visual_Imagery\\visual_imagery_practice_lastrun.py',
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
    if deviceManager.getDevice('P_Key_Resp') is None:
        # initialise P_Key_Resp
        P_Key_Resp = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='P_Key_Resp',
        )
    # create speaker 'P_Sound'
    deviceManager.addDevice(
        deviceName='P_Sound',
        deviceClass='psychopy.hardware.speaker.SpeakerDevice',
        index=-1
    )
    # create speaker 'P_Cue'
    deviceManager.addDevice(
        deviceName='P_Cue',
        deviceClass='psychopy.hardware.speaker.SpeakerDevice',
        index=-1
    )
    if deviceManager.getDevice('P_Key_Resp2') is None:
        # initialise P_Key_Resp2
        P_Key_Resp2 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='P_Key_Resp2',
        )
    if deviceManager.getDevice('P_CQ_Key_Resp') is None:
        # initialise P_CQ_Key_Resp
        P_CQ_Key_Resp = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='P_CQ_Key_Resp',
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
    
    # --- Initialize components for Routine "P_Start" ---
    P_Intro = visual.TextStim(win=win, name='P_Intro',
        text='This is a practice before official experiment. \n\nPlease let the experimenter know when you are ready to begin.',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    P_Key_Resp = keyboard.Keyboard(deviceName='P_Key_Resp')
    
    # --- Initialize components for Routine "P_Interval" ---
    P_Inter = visual.ImageStim(
        win=win,
        name='P_Inter', 
        image=None, mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(0.5, 0.5),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    
    # --- Initialize components for Routine "P_Imagine" ---
    P_BG = visual.ImageStim(
        win=win,
        name='P_BG', 
        image=None, mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(0.5, 0.5),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    P_Sound = sound.Sound(
        'A', 
        secs=1.5, 
        stereo=True, 
        hamming=True, 
        speaker='P_Sound',    name='P_Sound'
    )
    P_Sound.setVolume(1.0)
    P_Cue = sound.Sound(
        'A', 
        secs=1.0, 
        stereo=True, 
        hamming=True, 
        speaker='P_Cue',    name='P_Cue'
    )
    P_Cue.setVolume(1.0)
    
    # --- Initialize components for Routine "P_Rate" ---
    P_RateText = visual.TextStim(win=win, name='P_RateText',
        text='Please rate the clarity of your imagination.',
        font='Arial',
        pos=(0, 0.35), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    P_IMG1 = visual.ImageStim(
        win=win,
        name='P_IMG1', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.72, 0), draggable=False, size=(0.35, 0.35),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    P_IMG2 = visual.ImageStim(
        win=win,
        name='P_IMG2', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(-0.36, 0), draggable=False, size=(0.35, 0.35),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-2.0)
    P_IMG3 = visual.ImageStim(
        win=win,
        name='P_IMG3', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(0.35, 0.35),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-3.0)
    P_IMG4 = visual.ImageStim(
        win=win,
        name='P_IMG4', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0.36, 0), draggable=False, size=(0.35, 0.35),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-4.0)
    P_IMG5 = visual.ImageStim(
        win=win,
        name='P_IMG5', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0.72, 0), draggable=False, size=(0.35, 0.35),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-5.0)
    P_Key_Resp2 = keyboard.Keyboard(deviceName='P_Key_Resp2')
    
    # --- Initialize components for Routine "P_Catch" ---
    P_CQ = visual.TextStim(win=win, name='P_CQ',
        text='',
        font='Arial',
        pos=(0, 0.12), draggable=False, height=0.1, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    P_CQ_Option = visual.TextStim(win=win, name='P_CQ_Option',
        text="YES      NO      DON'T KNOW",
        font='Arial',
        pos=(0, -0.1), draggable=False, height=0.07, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    P_CQ_Key_Resp = keyboard.Keyboard(deviceName='P_CQ_Key_Resp')
    
    # --- Initialize components for Routine "P_End" ---
    VI_P_End = visual.TextStim(win=win, name='VI_P_End',
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
    
    # --- Prepare to start Routine "P_Start" ---
    # create an object to store info about Routine P_Start
    P_Start = data.Routine(
        name='P_Start',
        components=[P_Intro, P_Key_Resp],
    )
    P_Start.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for P_Key_Resp
    P_Key_Resp.keys = []
    P_Key_Resp.rt = []
    _P_Key_Resp_allKeys = []
    # store start times for P_Start
    P_Start.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    P_Start.tStart = globalClock.getTime(format='float')
    P_Start.status = STARTED
    thisExp.addData('P_Start.started', P_Start.tStart)
    P_Start.maxDuration = None
    # keep track of which components have finished
    P_StartComponents = P_Start.components
    for thisComponent in P_Start.components:
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
    
    # --- Run Routine "P_Start" ---
    P_Start.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *P_Intro* updates
        
        # if P_Intro is starting this frame...
        if P_Intro.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            P_Intro.frameNStart = frameN  # exact frame index
            P_Intro.tStart = t  # local t and not account for scr refresh
            P_Intro.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(P_Intro, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'P_Intro.started')
            # update status
            P_Intro.status = STARTED
            P_Intro.setAutoDraw(True)
        
        # if P_Intro is active this frame...
        if P_Intro.status == STARTED:
            # update params
            pass
        
        # *P_Key_Resp* updates
        waitOnFlip = False
        
        # if P_Key_Resp is starting this frame...
        if P_Key_Resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            P_Key_Resp.frameNStart = frameN  # exact frame index
            P_Key_Resp.tStart = t  # local t and not account for scr refresh
            P_Key_Resp.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(P_Key_Resp, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'P_Key_Resp.started')
            # update status
            P_Key_Resp.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(P_Key_Resp.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(P_Key_Resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if P_Key_Resp.status == STARTED and not waitOnFlip:
            theseKeys = P_Key_Resp.getKeys(keyList=['s'], ignoreKeys=["escape"], waitRelease=False)
            _P_Key_Resp_allKeys.extend(theseKeys)
            if len(_P_Key_Resp_allKeys):
                P_Key_Resp.keys = _P_Key_Resp_allKeys[-1].name  # just the last key pressed
                P_Key_Resp.rt = _P_Key_Resp_allKeys[-1].rt
                P_Key_Resp.duration = _P_Key_Resp_allKeys[-1].duration
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
            P_Start.forceEnded = routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in P_Start.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "P_Start" ---
    for thisComponent in P_Start.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for P_Start
    P_Start.tStop = globalClock.getTime(format='float')
    P_Start.tStopRefresh = tThisFlipGlobal
    thisExp.addData('P_Start.stopped', P_Start.tStop)
    # check responses
    if P_Key_Resp.keys in ['', [], None]:  # No response was made
        P_Key_Resp.keys = None
    thisExp.addData('P_Key_Resp.keys',P_Key_Resp.keys)
    if P_Key_Resp.keys != None:  # we had a response
        thisExp.addData('P_Key_Resp.rt', P_Key_Resp.rt)
        thisExp.addData('P_Key_Resp.duration', P_Key_Resp.duration)
    thisExp.nextEntry()
    # the Routine "P_Start" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # set up handler to look after randomisation of conditions etc
    P_Trials = data.TrialHandler2(
        name='P_Trials',
        nReps=1.0, 
        method='random', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=data.importConditions('VI_P_Objects.csv'), 
        seed=None, 
    )
    thisExp.addLoop(P_Trials)  # add the loop to the experiment
    thisP_Trial = P_Trials.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisP_Trial.rgb)
    if thisP_Trial != None:
        for paramName in thisP_Trial:
            globals()[paramName] = thisP_Trial[paramName]
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    for thisP_Trial in P_Trials:
        currentLoop = P_Trials
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # abbreviate parameter names if possible (e.g. rgb = thisP_Trial.rgb)
        if thisP_Trial != None:
            for paramName in thisP_Trial:
                globals()[paramName] = thisP_Trial[paramName]
        
        # --- Prepare to start Routine "P_Interval" ---
        # create an object to store info about Routine P_Interval
        P_Interval = data.Routine(
            name='P_Interval',
            components=[P_Inter],
        )
        P_Interval.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # store start times for P_Interval
        P_Interval.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        P_Interval.tStart = globalClock.getTime(format='float')
        P_Interval.status = STARTED
        thisExp.addData('P_Interval.started', P_Interval.tStart)
        P_Interval.maxDuration = None
        # keep track of which components have finished
        P_IntervalComponents = P_Interval.components
        for thisComponent in P_Interval.components:
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
        
        # --- Run Routine "P_Interval" ---
        # if trial has changed, end Routine now
        if isinstance(P_Trials, data.TrialHandler2) and thisP_Trial.thisN != P_Trials.thisTrial.thisN:
            continueRoutine = False
        P_Interval.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 1.0:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *P_Inter* updates
            
            # if P_Inter is starting this frame...
            if P_Inter.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_Inter.frameNStart = frameN  # exact frame index
                P_Inter.tStart = t  # local t and not account for scr refresh
                P_Inter.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_Inter, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_Inter.started')
                # update status
                P_Inter.status = STARTED
                P_Inter.setAutoDraw(True)
            
            # if P_Inter is active this frame...
            if P_Inter.status == STARTED:
                # update params
                pass
            
            # if P_Inter is stopping this frame...
            if P_Inter.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > P_Inter.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    P_Inter.tStop = t  # not accounting for scr refresh
                    P_Inter.tStopRefresh = tThisFlipGlobal  # on global time
                    P_Inter.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'P_Inter.stopped')
                    # update status
                    P_Inter.status = FINISHED
                    P_Inter.setAutoDraw(False)
            
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
                P_Interval.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in P_Interval.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "P_Interval" ---
        for thisComponent in P_Interval.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for P_Interval
        P_Interval.tStop = globalClock.getTime(format='float')
        P_Interval.tStopRefresh = tThisFlipGlobal
        thisExp.addData('P_Interval.stopped', P_Interval.tStop)
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if P_Interval.maxDurationReached:
            routineTimer.addTime(-P_Interval.maxDuration)
        elif P_Interval.forceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-1.000000)
        
        # --- Prepare to start Routine "P_Imagine" ---
        # create an object to store info about Routine P_Imagine
        P_Imagine = data.Routine(
            name='P_Imagine',
            components=[P_BG, P_Sound, P_Cue],
        )
        P_Imagine.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        P_Sound.setSound('AuditoryPrompt/' + Object + '.mp3', secs=1.5, hamming=True)
        P_Sound.setVolume(1.0, log=False)
        P_Sound.seek(0)
        P_Cue.setSound('AuditoryPrompt/Cue.mp3', secs=1.0, hamming=True)
        P_Cue.setVolume(1.0, log=False)
        P_Cue.seek(0)
        # store start times for P_Imagine
        P_Imagine.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        P_Imagine.tStart = globalClock.getTime(format='float')
        P_Imagine.status = STARTED
        thisExp.addData('P_Imagine.started', P_Imagine.tStart)
        P_Imagine.maxDuration = None
        # keep track of which components have finished
        P_ImagineComponents = P_Imagine.components
        for thisComponent in P_Imagine.components:
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
        
        # --- Run Routine "P_Imagine" ---
        # if trial has changed, end Routine now
        if isinstance(P_Trials, data.TrialHandler2) and thisP_Trial.thisN != P_Trials.thisTrial.thisN:
            continueRoutine = False
        P_Imagine.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 6.5:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *P_BG* updates
            
            # if P_BG is starting this frame...
            if P_BG.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_BG.frameNStart = frameN  # exact frame index
                P_BG.tStart = t  # local t and not account for scr refresh
                P_BG.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_BG, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_BG.started')
                # update status
                P_BG.status = STARTED
                P_BG.setAutoDraw(True)
            
            # if P_BG is active this frame...
            if P_BG.status == STARTED:
                # update params
                pass
            
            # if P_BG is stopping this frame...
            if P_BG.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > P_BG.tStartRefresh + 6.5-frameTolerance:
                    # keep track of stop time/frame for later
                    P_BG.tStop = t  # not accounting for scr refresh
                    P_BG.tStopRefresh = tThisFlipGlobal  # on global time
                    P_BG.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'P_BG.stopped')
                    # update status
                    P_BG.status = FINISHED
                    P_BG.setAutoDraw(False)
            
            # *P_Sound* updates
            
            # if P_Sound is starting this frame...
            if P_Sound.status == NOT_STARTED and t >= 1.0-frameTolerance:
                # keep track of start time/frame for later
                P_Sound.frameNStart = frameN  # exact frame index
                P_Sound.tStart = t  # local t and not account for scr refresh
                P_Sound.tStartRefresh = tThisFlipGlobal  # on global time
                # add timestamp to datafile
                thisExp.addData('P_Sound.started', t)
                # update status
                P_Sound.status = STARTED
                P_Sound.play()  # start the sound (it finishes automatically)
            
            # if P_Sound is stopping this frame...
            if P_Sound.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > P_Sound.tStartRefresh + 1.5-frameTolerance or P_Sound.isFinished:
                    # keep track of stop time/frame for later
                    P_Sound.tStop = t  # not accounting for scr refresh
                    P_Sound.tStopRefresh = tThisFlipGlobal  # on global time
                    P_Sound.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.addData('P_Sound.stopped', t)
                    # update status
                    P_Sound.status = FINISHED
                    P_Sound.stop()
            
            # *P_Cue* updates
            
            # if P_Cue is starting this frame...
            if P_Cue.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_Cue.frameNStart = frameN  # exact frame index
                P_Cue.tStart = t  # local t and not account for scr refresh
                P_Cue.tStartRefresh = tThisFlipGlobal  # on global time
                # add timestamp to datafile
                thisExp.addData('P_Cue.started', tThisFlipGlobal)
                # update status
                P_Cue.status = STARTED
                P_Cue.play(when=win)  # sync with win flip
            
            # if P_Cue is stopping this frame...
            if P_Cue.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > P_Cue.tStartRefresh + 1.0-frameTolerance or P_Cue.isFinished:
                    # keep track of stop time/frame for later
                    P_Cue.tStop = t  # not accounting for scr refresh
                    P_Cue.tStopRefresh = tThisFlipGlobal  # on global time
                    P_Cue.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'P_Cue.stopped')
                    # update status
                    P_Cue.status = FINISHED
                    P_Cue.stop()
            
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
                    playbackComponents=[P_Sound, P_Cue]
                )
                # skip the frame we paused on
                continue
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                P_Imagine.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in P_Imagine.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "P_Imagine" ---
        for thisComponent in P_Imagine.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for P_Imagine
        P_Imagine.tStop = globalClock.getTime(format='float')
        P_Imagine.tStopRefresh = tThisFlipGlobal
        thisExp.addData('P_Imagine.stopped', P_Imagine.tStop)
        P_Sound.pause()  # ensure sound has stopped at end of Routine
        P_Cue.pause()  # ensure sound has stopped at end of Routine
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if P_Imagine.maxDurationReached:
            routineTimer.addTime(-P_Imagine.maxDuration)
        elif P_Imagine.forceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-6.500000)
        
        # --- Prepare to start Routine "P_Rate" ---
        # create an object to store info about Routine P_Rate
        P_Rate = data.Routine(
            name='P_Rate',
            components=[P_RateText, P_IMG1, P_IMG2, P_IMG3, P_IMG4, P_IMG5, P_Key_Resp2],
        )
        P_Rate.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        P_IMG1.setImage('imgs_diffusion/' + Object + '1.jpg')
        P_IMG2.setImage('imgs_diffusion/' + Object + '3.jpg')
        P_IMG3.setImage('imgs_diffusion/' + Object + '5.jpg')
        P_IMG4.setImage('imgs_diffusion/' + Object + '8.jpg')
        P_IMG5.setImage('imgs_diffusion/' + Object + '50.jpg')
        # create starting attributes for P_Key_Resp2
        P_Key_Resp2.keys = []
        P_Key_Resp2.rt = []
        _P_Key_Resp2_allKeys = []
        # store start times for P_Rate
        P_Rate.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        P_Rate.tStart = globalClock.getTime(format='float')
        P_Rate.status = STARTED
        thisExp.addData('P_Rate.started', P_Rate.tStart)
        P_Rate.maxDuration = None
        # keep track of which components have finished
        P_RateComponents = P_Rate.components
        for thisComponent in P_Rate.components:
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
        
        # --- Run Routine "P_Rate" ---
        # if trial has changed, end Routine now
        if isinstance(P_Trials, data.TrialHandler2) and thisP_Trial.thisN != P_Trials.thisTrial.thisN:
            continueRoutine = False
        P_Rate.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *P_RateText* updates
            
            # if P_RateText is starting this frame...
            if P_RateText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_RateText.frameNStart = frameN  # exact frame index
                P_RateText.tStart = t  # local t and not account for scr refresh
                P_RateText.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_RateText, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_RateText.started')
                # update status
                P_RateText.status = STARTED
                P_RateText.setAutoDraw(True)
            
            # if P_RateText is active this frame...
            if P_RateText.status == STARTED:
                # update params
                pass
            
            # *P_IMG1* updates
            
            # if P_IMG1 is starting this frame...
            if P_IMG1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_IMG1.frameNStart = frameN  # exact frame index
                P_IMG1.tStart = t  # local t and not account for scr refresh
                P_IMG1.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_IMG1, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_IMG1.started')
                # update status
                P_IMG1.status = STARTED
                P_IMG1.setAutoDraw(True)
            
            # if P_IMG1 is active this frame...
            if P_IMG1.status == STARTED:
                # update params
                pass
            
            # *P_IMG2* updates
            
            # if P_IMG2 is starting this frame...
            if P_IMG2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_IMG2.frameNStart = frameN  # exact frame index
                P_IMG2.tStart = t  # local t and not account for scr refresh
                P_IMG2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_IMG2, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_IMG2.started')
                # update status
                P_IMG2.status = STARTED
                P_IMG2.setAutoDraw(True)
            
            # if P_IMG2 is active this frame...
            if P_IMG2.status == STARTED:
                # update params
                pass
            
            # *P_IMG3* updates
            
            # if P_IMG3 is starting this frame...
            if P_IMG3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_IMG3.frameNStart = frameN  # exact frame index
                P_IMG3.tStart = t  # local t and not account for scr refresh
                P_IMG3.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_IMG3, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_IMG3.started')
                # update status
                P_IMG3.status = STARTED
                P_IMG3.setAutoDraw(True)
            
            # if P_IMG3 is active this frame...
            if P_IMG3.status == STARTED:
                # update params
                pass
            
            # *P_IMG4* updates
            
            # if P_IMG4 is starting this frame...
            if P_IMG4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_IMG4.frameNStart = frameN  # exact frame index
                P_IMG4.tStart = t  # local t and not account for scr refresh
                P_IMG4.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_IMG4, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_IMG4.started')
                # update status
                P_IMG4.status = STARTED
                P_IMG4.setAutoDraw(True)
            
            # if P_IMG4 is active this frame...
            if P_IMG4.status == STARTED:
                # update params
                pass
            
            # *P_IMG5* updates
            
            # if P_IMG5 is starting this frame...
            if P_IMG5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_IMG5.frameNStart = frameN  # exact frame index
                P_IMG5.tStart = t  # local t and not account for scr refresh
                P_IMG5.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_IMG5, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_IMG5.started')
                # update status
                P_IMG5.status = STARTED
                P_IMG5.setAutoDraw(True)
            
            # if P_IMG5 is active this frame...
            if P_IMG5.status == STARTED:
                # update params
                pass
            
            # *P_Key_Resp2* updates
            waitOnFlip = False
            
            # if P_Key_Resp2 is starting this frame...
            if P_Key_Resp2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_Key_Resp2.frameNStart = frameN  # exact frame index
                P_Key_Resp2.tStart = t  # local t and not account for scr refresh
                P_Key_Resp2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_Key_Resp2, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_Key_Resp2.started')
                # update status
                P_Key_Resp2.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(P_Key_Resp2.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(P_Key_Resp2.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if P_Key_Resp2.status == STARTED and not waitOnFlip:
                theseKeys = P_Key_Resp2.getKeys(keyList=['1','2','3','4','5'], ignoreKeys=["escape"], waitRelease=False)
                _P_Key_Resp2_allKeys.extend(theseKeys)
                if len(_P_Key_Resp2_allKeys):
                    P_Key_Resp2.keys = _P_Key_Resp2_allKeys[-1].name  # just the last key pressed
                    P_Key_Resp2.rt = _P_Key_Resp2_allKeys[-1].rt
                    P_Key_Resp2.duration = _P_Key_Resp2_allKeys[-1].duration
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
                P_Rate.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in P_Rate.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "P_Rate" ---
        for thisComponent in P_Rate.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for P_Rate
        P_Rate.tStop = globalClock.getTime(format='float')
        P_Rate.tStopRefresh = tThisFlipGlobal
        thisExp.addData('P_Rate.stopped', P_Rate.tStop)
        # check responses
        if P_Key_Resp2.keys in ['', [], None]:  # No response was made
            P_Key_Resp2.keys = None
        P_Trials.addData('P_Key_Resp2.keys',P_Key_Resp2.keys)
        if P_Key_Resp2.keys != None:  # we had a response
            P_Trials.addData('P_Key_Resp2.rt', P_Key_Resp2.rt)
            P_Trials.addData('P_Key_Resp2.duration', P_Key_Resp2.duration)
        # the Routine "P_Rate" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
        
        # --- Prepare to start Routine "P_Catch" ---
        # create an object to store info about Routine P_Catch
        P_Catch = data.Routine(
            name='P_Catch',
            components=[P_CQ, P_CQ_Option, P_CQ_Key_Resp],
        )
        P_Catch.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        P_CQ.setText(CatchQuestion)
        # create starting attributes for P_CQ_Key_Resp
        P_CQ_Key_Resp.keys = []
        P_CQ_Key_Resp.rt = []
        _P_CQ_Key_Resp_allKeys = []
        # store start times for P_Catch
        P_Catch.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        P_Catch.tStart = globalClock.getTime(format='float')
        P_Catch.status = STARTED
        thisExp.addData('P_Catch.started', P_Catch.tStart)
        P_Catch.maxDuration = None
        # keep track of which components have finished
        P_CatchComponents = P_Catch.components
        for thisComponent in P_Catch.components:
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
        
        # --- Run Routine "P_Catch" ---
        # if trial has changed, end Routine now
        if isinstance(P_Trials, data.TrialHandler2) and thisP_Trial.thisN != P_Trials.thisTrial.thisN:
            continueRoutine = False
        P_Catch.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *P_CQ* updates
            
            # if P_CQ is starting this frame...
            if P_CQ.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_CQ.frameNStart = frameN  # exact frame index
                P_CQ.tStart = t  # local t and not account for scr refresh
                P_CQ.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_CQ, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_CQ.started')
                # update status
                P_CQ.status = STARTED
                P_CQ.setAutoDraw(True)
            
            # if P_CQ is active this frame...
            if P_CQ.status == STARTED:
                # update params
                pass
            
            # *P_CQ_Option* updates
            
            # if P_CQ_Option is starting this frame...
            if P_CQ_Option.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_CQ_Option.frameNStart = frameN  # exact frame index
                P_CQ_Option.tStart = t  # local t and not account for scr refresh
                P_CQ_Option.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_CQ_Option, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_CQ_Option.started')
                # update status
                P_CQ_Option.status = STARTED
                P_CQ_Option.setAutoDraw(True)
            
            # if P_CQ_Option is active this frame...
            if P_CQ_Option.status == STARTED:
                # update params
                pass
            
            # *P_CQ_Key_Resp* updates
            waitOnFlip = False
            
            # if P_CQ_Key_Resp is starting this frame...
            if P_CQ_Key_Resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                P_CQ_Key_Resp.frameNStart = frameN  # exact frame index
                P_CQ_Key_Resp.tStart = t  # local t and not account for scr refresh
                P_CQ_Key_Resp.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(P_CQ_Key_Resp, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'P_CQ_Key_Resp.started')
                # update status
                P_CQ_Key_Resp.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(P_CQ_Key_Resp.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(P_CQ_Key_Resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if P_CQ_Key_Resp.status == STARTED and not waitOnFlip:
                theseKeys = P_CQ_Key_Resp.getKeys(keyList=['s','d','f'], ignoreKeys=["escape"], waitRelease=False)
                _P_CQ_Key_Resp_allKeys.extend(theseKeys)
                if len(_P_CQ_Key_Resp_allKeys):
                    P_CQ_Key_Resp.keys = _P_CQ_Key_Resp_allKeys[-1].name  # just the last key pressed
                    P_CQ_Key_Resp.rt = _P_CQ_Key_Resp_allKeys[-1].rt
                    P_CQ_Key_Resp.duration = _P_CQ_Key_Resp_allKeys[-1].duration
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
                P_Catch.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in P_Catch.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "P_Catch" ---
        for thisComponent in P_Catch.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for P_Catch
        P_Catch.tStop = globalClock.getTime(format='float')
        P_Catch.tStopRefresh = tThisFlipGlobal
        thisExp.addData('P_Catch.stopped', P_Catch.tStop)
        # check responses
        if P_CQ_Key_Resp.keys in ['', [], None]:  # No response was made
            P_CQ_Key_Resp.keys = None
        P_Trials.addData('P_CQ_Key_Resp.keys',P_CQ_Key_Resp.keys)
        if P_CQ_Key_Resp.keys != None:  # we had a response
            P_Trials.addData('P_CQ_Key_Resp.rt', P_CQ_Key_Resp.rt)
            P_Trials.addData('P_CQ_Key_Resp.duration', P_CQ_Key_Resp.duration)
        # Run 'End Routine' code from code
        # Catch question key response (P_CQ_Key_Resp)
        cq_key_pressed = P_CQ_Key_Resp.keys
        cq_key_rt = P_CQ_Key_Resp.rt
        cq_key_duration = None
        
        thisExp.addData('P_CQ_KeyResp_key', cq_key_pressed)
        thisExp.addData('P_CQ_KeyResp_rt', cq_key_rt)
        thisExp.addData('P_CQ_KeyResp_duration', cq_key_duration)
        
        # the Routine "P_Catch" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
        thisExp.nextEntry()
        
    # completed 1.0 repeats of 'P_Trials'
    
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    # --- Prepare to start Routine "P_End" ---
    # create an object to store info about Routine P_End
    P_End = data.Routine(
        name='P_End',
        components=[VI_P_End],
    )
    P_End.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # store start times for P_End
    P_End.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    P_End.tStart = globalClock.getTime(format='float')
    P_End.status = STARTED
    thisExp.addData('P_End.started', P_End.tStart)
    P_End.maxDuration = None
    # keep track of which components have finished
    P_EndComponents = P_End.components
    for thisComponent in P_End.components:
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
    
    # --- Run Routine "P_End" ---
    P_End.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *VI_P_End* updates
        
        # if VI_P_End is starting this frame...
        if VI_P_End.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            VI_P_End.frameNStart = frameN  # exact frame index
            VI_P_End.tStart = t  # local t and not account for scr refresh
            VI_P_End.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(VI_P_End, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'VI_P_End.started')
            # update status
            VI_P_End.status = STARTED
            VI_P_End.setAutoDraw(True)
        
        # if VI_P_End is active this frame...
        if VI_P_End.status == STARTED:
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
            P_End.forceEnded = routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in P_End.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "P_End" ---
    for thisComponent in P_End.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for P_End
    P_End.tStop = globalClock.getTime(format='float')
    P_End.tStopRefresh = tThisFlipGlobal
    thisExp.addData('P_End.stopped', P_End.tStop)
    thisExp.nextEntry()
    # the Routine "P_End" was not non-slip safe, so reset the non-slip timer
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
