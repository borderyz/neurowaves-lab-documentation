%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MEG GO/NO-GO TASK - Psychtoolbox (MATLAB)- Gianluca Marsicano
%
% Description:
% Visual Go/No-Go Task for Magnetoencephalography (MEG).
% Participants must press the 'M' key as fast as possible when a white 
% CIRCLE appears (Go Trials), and must inhibit response when a 
% white TRIANGLE appears (No-Go Trials).
%
% Incorrect and too slow responses will trigger a brief beep and text (negative feedback).
%
% Stimuli are presented fast (see below for more details about timing),
% Trials are randomized.
% For MEG Triggers Details, see below.
%
% Inquiries:
% For any questions or issues related to this script,
% Gianluca Marsicano, gm3598@nyu.edu
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



%% GO-NOGO TASK

%Setup Psychtoolbox
clear; close all; clc;
PsychDebugWindowConfiguration(0, 1);
PsychDefaultSetup(2);
Screen('Preference', 'SkipSyncTests', 1); 
KbName('UnifyKeyNames');

% Participant Data
name1 = 'Participant Data';
prompt1 = {'Subject Number', 'Subject ID', 'Sex (f/m)', 'Age', 'Nationality'};
numlines1 = 1;
defaultanswer1 = {'0', 'GM', 'm', '28', 'Italy'};
answer1 = inputdlg(prompt1, name1, numlines1, defaultanswer1);
DEMO.num = str2double(answer1{1});
DEMO.ID  = answer1{2};
DEMO.sex = answer1{3};
DEMO.age = str2double(answer1{4});
DEMO.Nationality = answer1{5};

% Setup screen
screenNumber = max(Screen('Screens'));
white = WhiteIndex(screenNumber);
black = BlackIndex(screenNumber);
gray = (black + white) / 2;
[window, rect] = PsychImaging('OpenWindow', screenNumber, black);
Screen('TextSize', window, 32);
Screen('TextFont', window, 'Arial');
ifi = Screen('GetFlipInterval', window);
[xCenter, yCenter] = RectCenter(rect);

%-------------------------------------------
% TRIGGERS SETUP
%-------------------------------------------
% % Define trigger pixels for all usable MEG channels
% trig.ch224 = [4  0  0]; %224 meg channel
% trig.ch225 = [16  0  0];  %225 meg channel
% trig.ch226 = [64 0 0]; % 226 meg channel
% trig.ch227 = [0  1 0]; % 227 meg channel
% trig.ch228 = [0  4 0]; % 228 meg channel
% trig.ch229 = [0 16 0]; % 229 meg channel
% trig.ch230 = [0 64 0]; % 230 meg channel
% trig.ch231 = [0 0  1]; % 231 meg channel

trigRect = [0 0 1 1];
trig.start = [4  0  0];
trig.end   = [16  0  0];
% Go/No-Go Trigger Event Codes
trig.go = [64 0 0];
trig.nogo = [0  1 0];
% Response Trigger Event Codes
trig.go_resp = [0  4 0]; % Go trials with Responses (Correct)
trig.go_noresp = [0 16 0]; % Go trials with NO Responses (Too Slow/Error)
trig.nogo_resp = [0 64 0]; % NoGo trials with Responses (Error)
trig.nogo_noresp = [0 0  1]; % NoGo trials with NO Responses (Correct)

%-------------------------------------------
% VPIXX SETUP
%-------------------------------------------    
Datapixx('Open');
Datapixx('EnablePixelMode'); 
Datapixx('RegWr');

% Audio setup
InitializePsychSound(1);
freq = 48000; % Audio Sample rate
nrchannels = 1; % Single Channel Mono
pahandle = PsychPortAudio('Open', [], [], 1, freq, nrchannels); 
% Negative Feedback Beep 
beepFreq = 80; 
beepDur = 0.15; % 150 ms (Match VIsual negativeFeedback)
beepSamples = beepDur * freq;
t = linspace(0, beepDur, beepSamples);
beep = square(2 * pi * beepFreq * t);   % Buzzing tone
%beep = sawtooth(2 * pi * beepFreq * t); % Siren-like
PsychPortAudio('FillBuffer', pahandle, beep);

% Fixation cross
fixCrossDimPix = 14;
xCoords = [-fixCrossDimPix fixCrossDimPix 0 0];
yCoords = [0 0 -fixCrossDimPix fixCrossDimPix];
allCoords = [xCoords; yCoords];
lineWidthPix = 2;

% Trial setup
nGo = 150;
nNoGo = 150;
nTrials = nGo + nNoGo;
trialTypes = [ones(1, nGo), zeros(1, nNoGo)]; % 1 = Go, 0 = NoGo
trialTypes = trialTypes(randperm(nTrials)); % Randomize Order

% Timing
fixTime = 0.4; % 400 ms
blankTime = 0.1; % 200 ms
stimTime = 0.05; % 50 ms
respTime = 1; % 1 s response window
negativeFeedback = 0.15; % ms negative feedback text
iti = 0.5; % 500 ms inter-trial interval

% Start Task
Screen('FillRect', window, getRGB(trig.start), trigRect); % Trigger Start
Screen('Flip', window);

% Keys
escapeKey = KbName('ESCAPE');

% Instructions
instructions = ['In this task, press the M key on the keyboard as quickly as possible whenever a white CIRCLE appears on the screen.\n\n' ...
                'Conversely, when a TRIANGLE appears, DO NOT press anything. Try to inhibit your response.\n\n' ...
                'Stimuli will be presented very fast, so you need to respond AS FAST AS YOU CAN.\n\n' ...
                'If you make a mistake, by pressing M when a triangle is shown, or by failing to press M when a circle appears, \n\n' ... 
                'you will hear a negative feedback sound along with a red text message indicating the error. \n\n' ... 
                'Press the Spacebar to start the Experiment'];

DrawFormattedText(window, instructions, 'center', 'center', white);
Screen('Flip', window);
listenButton(0); % Red Button

% Store Data and Result Table
results = struct('trialType', [], 'RT', [], 'Correct', []);

HideCursor;

for t = 1:nTrials
    % Fixation
    Screen('DrawLines', window, allCoords, lineWidthPix, white, [xCenter yCenter]);
    fixOnset = Screen('Flip', window);
    WaitSecs(fixTime);

    % Blank Pre-Stimulus
    DrawFormattedText(window, '', 'center', 'center', white);
    Screen('Flip', window);
    WaitSecs(blankTime);
    
    % Stimulus Trigger for Go/NoGo Stimuli Onset
    if trialTypes(t) == 1
        stimTrig = trig.go;
    else
        stimTrig = trig.nogo;
    end
    Screen('FillRect', window, getRGB(stimTrig), trigRect);
    Screen('Flip', window);
    WaitSecs(0.005); % Short pulse for trigger

    % Stimulus
    if trialTypes(t) == 1 % Go - Circle
        baseRect = [0 0 100 100];
        centeredRect = CenterRectOnPointd(baseRect, xCenter, yCenter);
        Screen('FillOval', window, white, centeredRect);
    else % No-Go - Triangle
        triangle = [0 -50; 50 50; -50 50]';
        triangle(1,:) = triangle(1,:) + xCenter;
        triangle(2,:) = triangle(2,:) + yCenter;
        Screen('FillPoly', window, white, triangle', 1);
    end
    stimOnset = Screen('Flip', window);

    % Stimulus Duration (50 ms)
    WaitSecs(stimTime);
    Screen('Flip', window);

% Response 
respMade = false;
rt = NaN;
startTime = GetSecs;
while GetSecs - startTime < respTime
    buttonPressed = listenButton(1); % Yellow button on button box
    % Still listen for ESC key on keyboard for abort
    [~, ~, keyCode] = KbCheck;
    if keyCode(KbName('ESCAPE'))
        ShowCursor;
        sca;
        error('Experiment aborted');
    end
    % Button press = response
    if buttonPressed && ~respMade
        rt = GetSecs - stimOnset;
        respMade = true;
    end
end


    % Determine accuracy
    if trialTypes(t) == 1 % Go
        correct = respMade;
    else % No-Go
        correct = ~respMade;
    end

        % 'Hit', 'miss', 'false alarm', 'correct inhibition'   
    if trialTypes(t) == 1 && respMade
        responseType = 'hit';
    elseif trialTypes(t) == 1 && ~respMade
        responseType = 'miss';
    elseif trialTypes(t) == 0 && respMade
        responseType = 'false alarm';
    else
        responseType = 'correct inhibition';
    end
    
        % Response Trigger
    if trialTypes(t) == 1 && respMade
        respTrig = trig.go_resp;
    elseif trialTypes(t) == 1 && ~respMade
        respTrig = trig.go_noresp;
    elseif trialTypes(t) == 0 && respMade
        respTrig = trig.nogo_resp;
    else
        respTrig = trig.nogo_noresp;
    end

    Screen('FillRect', window, getRGB(respTrig), trigRect);
    Screen('Flip', window);
    WaitSecs(0.005); % Short trigger pulse
    
    
% Play sound and text if incorrect (nogo) or too slow (go)
if ~correct
    Screen('TextSize', window, 80);
    if trialTypes(t) == 1 && ~respMade
        feedbackText = 'TOO SLOW!!';
    else
        feedbackText = 'ERROR!!';
    end
    DrawFormattedText(window, feedbackText, 'center', 'center', [255 0 0]); 
    Screen('Flip', window);
    PsychPortAudio('Start', pahandle, 1, 0, 1);
    WaitSecs(negativeFeedback);
    PsychPortAudio('Stop', pahandle);
    Screen('TextSize', window, 32);
end

    % Save trial results
    results(t).trialType = trialTypes(t);
    results(t).RT = rt;
    results(t).Correct = correct;
    results(t).ResponseType = responseType;
    results(t).TriggerCode = respTrig;

    % ITI
     WaitSecs(iti);
end
    
    % Trigger End Exp
    Screen('Flip', window);
    Screen('FillRect', window, getRGB(trig.end), trigRect);
    WaitSecs(0.005); % Short trigger pulse

ShowCursor;
sca;
PsychPortAudio('Close', pahandle);

% Display summary
nCorrect = sum([results.Correct]);
fprintf('Experiment completed.\n');
fprintf('Accuracy: %.2f%%\n', 100 * nCorrect / nTrials);

% % % SAVE PARTICIPANT INFO AND MATRIX % % %
numStr = num2str(DEMO.num, '%03d');
filename = sprintf('%s_%s_%s.mat', 'MEG_Go_NoGo', numStr, DEMO.ID);
save(filename, 'results'); 
