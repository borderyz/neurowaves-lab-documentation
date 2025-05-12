clearvars

vpix_use = 1; % 0 if vpixx is not conected

if vpix_use
    Datapixx('Open')
    Datapixx('DisablePixelMode')
    Datapixx('RegWr')
    Datapixx('SetPropixxDlpSequenceProgram', 0)
    Datapixx('RegWr')
end

PsychDebugWindowConfiguration(0, 1);
PsychDefaultSetup(2);
Screen('Preference', 'SkipSyncTests', 1); 
  

% TRIGGERS CHANNEL 225 during the eyes open period

% Time to rest in seconds
time2rest = 60*5 ;


% KEYBOARD SETUP
responseKeys = {'2', '3', 'y', 'n'};
KbName('UnifyKeyNames');  
KbCheckList = [KbName('space'),KbName('ESCAPE'), KbName('leftarrow'), KbName('rightarrow')];
for i = 1:length(responseKeys)
    KbCheckList = [KbName(responseKeys{i}),KbCheckList];
end

% SCREEN SETUP
screens = Screen('Screens'); 

s = max(screens);

black = [0 0 0];

[w, rect] = Screen('Openwindow',s,black)

Priority(MaxPriority(w));

Screen('BlendFunction', w, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);    
pixelSizes=Screen('PixelSizes', s);
fps=Screen('FrameRate',w);
ifi=Screen('GetFlipInterval', w);

[wx, wy] = RectCenter(rect);
Screen('Flip', w)


% Uncomment if Vpixx is connected, or else experiment will crash

if vpix_use == 1
    %VIEW PIXX SETUP
    Datapixx('EnablePixelMode');  % to use topleft pixel to code trigger information, see https://vpixx.com/vocal/pixelmode/
    Datapixx('RegWr');
end

% TRIGGERS SETUP
trigRect = [0 0 1 1]; % Top left pixel that controls triggers in PixelMode
%centeredRect_trigger = CenterRectOnPointd(baseRect_trigger, 0.5, 0.5);


% RGB color for top left pixel to trigger a channel on MEG

% output of Vpixx will be triggered
% Ref: https://docs.vpixx.com/vocal/defining-triggers-using-pixel-mode

% % triggers as color (RGB) of tope-left pixel in the screen
% Reference of all triggers for KIT MEG in NYUAD:
% trigger_224 = [4  0 0]; % 224 meg channel
% trigger_225 = [16 0 0]; % 225 meg channel
% trigger_226 = [64 0 0]; % 226 meg channel
% trigger_227 = [0  1 0]; % 227 meg channel
% trigger_228 = [0  4 0]; % 228 meg channel
% trigger_229 = [0 16 0]; % 229 meg channel
% trigger_230 = [0 64 0]; % 230 meg channel
% trigger_231 = [0 0  1]; % 231 meg channel
% example: 
%   [16 0 0]  in binary is [10000 0 0] ==> Means pin number 4 on digital
%   [64 0 0] in binary is [1000000 0 0] ==> Means pin number 7 will be triggered 

% Define triggers for closing eyes and opening eyes

trig.open = [16  0  0];  %225 meg channel

%Ensure all vpixx digital output are set to 0 by putting the trigger pixel
%to black [0 0 0]
Screen('FillRect', w, black, trigRect);


% STIMULI SETUP

fixRadius = 30;
fixRect = CenterRectOnPoint([0, 0, fixRadius*2, fixRadius*2], wx, wy);
fixColor = [150 150 150];



% START EXPERIMENT


Screen('DrawText', w, 'PRESS SPACE and keep Eyes open on Fixation Cross',  wx-250, wy, [255,255,255]);
Screen('Flip', w);
KbWait([],2)

Screen('FillRect', w, trig.open, trigRect);
Screen('FillOval', w, fixColor, fixRect);
Screen('Flip', w);
WaitSecs(time2rest)

Screen('FillRect', w, black, trigRect);
Screen('FillOval', w, fixColor, fixRect);
Screen('Flip', w);


Screen('DrawText', w, 'Eyes open is now Finished, press Space to Exit',  wx-250, wy, [255,255,255]);
Screen('Flip', w);
KbWait([],2) 

Screen('CloseAll');

if vpix_use == 1
    %VIEW PIXX SETUP
    Datapixx('Close');
end