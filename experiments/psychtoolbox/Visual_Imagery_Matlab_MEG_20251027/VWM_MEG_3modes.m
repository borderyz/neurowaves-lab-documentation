%% Visual Working Memory Official
clear all; clc; close all;

% ===== Run mode (edit this only) =====
RUN_MODE = 'SIMULATE_VPIXX';  
% 'MEG' | 'SIMULATE_VPIXX' | 'SIMULATE_LAPTOP'

USE_VPIXX = any(strcmp(RUN_MODE, {'MEG','SIMULATE_VPIXX'}));
USE_SIM   = any(strcmp(RUN_MODE, {'SIMULATE_VPIXX','SIMULATE_LAPTOP'}));

USE_DEBUG_TRIALS = USE_SIM;

% set VPIXX
if USE_VPIXX
    Datapixx('Open');
    Datapixx('EnablePixelMode');
    Datapixx('RegWr');
end

%% Setup 
Screen('Preference', 'SkipSyncTests', 1);  % only for debugging
white = [255 255 255];
black = [0 0 0];
KbName('UnifyKeyNames');
black_rgb = [0 0 0];  % set black rgb for turn off trigger

% Keys
escapeKey = KbName('ESCAPE');

%% Participant Data
name1 = 'Participant Data';
prompt1 = {'Subject Number', 'Subject ID', 'Sex (f/m)', 'Age', 'Nationality'};
numlines1 = 1;
defaultanswer1 = {'0', '', '', '', ''};
answer1 = inputdlg(prompt1, name1, numlines1, defaultanswer1);
DEMO.num = str2double(answer1{1});
DEMO.ID  = answer1{2};
DEMO.sex = answer1{3};
DEMO.age = str2double(answer1{4});
DEMO.Nationality = answer1{5};

% set path and filename for saving beh results
subNumStr = answer1{1};  % e.g., '07'

% Create folder path
beh_datafolder = fullfile(pwd, 'Beh_Data')

% Build filename
filename = fullfile(beh_datafolder, sprintf('sub-%s_task-VWM_split-4_trials.csv', subNumStr));
TrigCheck_filename = fullfile(beh_datafolder, sprintf('sub-%s_task-VWM_split-4_events.csv', subNumStr));

%% MATLAB console output data saving
taskName = 'visualworkingmemory';

% Construct filename
logFileName = sprintf('sub-%s_task-%s_desc-matlabconsole_log.txt', subNumStr, taskName);

% Define full path - creating a 'logs' directory if it doesn't exist
logDir = fullfile(pwd, 'logs');
if ~exist(logDir, 'dir')
    mkdir(logDir);
end
logFilePath = fullfile(logDir, logFileName);

% Turn on diary to start recording command window output
diary(logFilePath);

%% Setup
% Open window (use 'win' consistently)
[win, rect] = PsychImaging('OpenWindow', max(Screen('Screens')), white);
[screenX, screenY] = RectSize(rect);
Screen('TextSize', win, 40);

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
trigImg1Start = [4  0  0]; % ch224
trigImg1End   = [16  0  0]; % ch225
trigImg2Start = [64 0 0]; % ch226
trigImg2End = [0  1 0]; % ch227
trigPromptStart = [0  4 0]; % ch228
trigPromptEnd = [0 16 0];  % ch229 
trigRecallEnd = [0 64 0]; % ch230 
trigQuestionResp = [0 0  1]; % ch231 

% VPIXX SETUP
% set VPIXX
if USE_VPIXX
    Datapixx('Open');
    Datapixx('EnablePixelMode');
    Datapixx('RegWr');
end

%% set up buttons for MEG controller
% set button for CatchQuestion
buttonMap = containers.Map;
buttonMap('right box|white') = 'StartImagine';
buttonMap('right box|red')   = 'YES'; % YES
buttonMap('right box|yellow')  = 'NO'; % NO

% Define which buttons to listen to (example: right box colors)
selection_CatchQuestion = struct('right_box', {{'red', 'yellow'}});
selection_CloseEyes = struct('right_box', {{'white'}});

% Audio setup
InitializePsychSound(1);
pahandle = PsychPortAudio('Open', [], 1, 1, 48000, 2); % playback device, freq 48000, 2 channels

%% Experiment constants (tweak if needed)
blankTime = 0.5; % inter-trial blank interval (seconds)
imageDur = 2.0;   % seconds to show each image
cuePlaySecs = 1.0; % seconds to play cue
audioTrimSecs = 1.5; % how long to trim object audio for playback
imgNums = [1, 3, 5, 7, 10];  % as in your code
imgWidth = 380; imgHeight = 380;
recall_time = 4.0; 
textYPos = round(screenY*0.8);    % rating text lower

%% ------------------- Stage 1: Instruction -------------------
Instruction = 'MEG Recording is being setup please be patient, press any key to continue';
DrawFormattedText(win, Instruction, 'center', 'center', black);
Screen('FillRect', win, black_rgb, trigRect);  % need black_rgb for left top corner pixel before each Screen('Flip', win)
Screen('Flip', win);
KbStrokeWait;  % wait for any key

%% Persistent blank screen
Screen('FillRect', win, white);
Screen('FillRect', win, black_rgb, trigRect);
Screen('Flip', win);

% Load block file
if USE_DEBUG_TRIALS
    % Load block file
    blockFiles = {
        'VWM_B1_trials_DEBUG.csv'
        'VWM_B2_trials_DEBUG.csv'
    };
else
    % Load block file
    blockFiles = {
        'VWM_B1_trials.csv'
        'VWM_B2_trials.csv'
    };
end

%% Assign one random imagine_time per block
nBlocks = numel(blockFiles);  

T_blocks = cell(size(blockFiles));
nTrialsTotal = 0;
for b = 1:nBlocks
    T_blocks{b} = readtable(blockFiles{b}, 'Delimiter', ',', 'ReadVariableNames', true);
    nTrialsTotal = nTrialsTotal + height(T_blocks{b});
end

%% Preallocate results
results = repmat(struct('Block',NaN, 'BlockRecallTime', '', 'TargetPrompt','','TargetObject','', 'TargetOrder', '', 'DistractObject', '', ...
    'Question_CorIMG', '', 'Question_Resp','','Question_RT',NaN), nTrialsTotal, 1);

TrigCheck_results = repmat(struct('Block',NaN, 'TargetPrompt','','TargetObject','', 'TargetOrder', '', 'DistractObject', '', ...
    'Onset', '', 'Duration','','Channel','','Trial_Type', ''), nTrialsTotal, 1);

HideCursor;
trialCounter = 1;
TrigCounter = 1;

%% Preload all stimuli
disp('Preloading all images and audio ...');

% Containers
imageCache = containers.Map;   % key: 'object_imgnum'
audioCache = containers.Map;   % key: object name

% Preload cue audio
cueFile = fullfile('AuditoryPrompt', 'Cue.mp3');
[cueWave, cueFs] = audioread(cueFile);
audioCache('Cue') = struct('wave', cueWave', 'Fs', cueFs);

% Collect all objects used across blocks
allObjects = {};
for b = 1:nBlocks
    T = T_blocks{b};
    objs = T.Object;
    allObjects = [allObjects; objs];
end
allObjects = unique(string(allObjects));

% Preload all object audio
for i = 1:numel(allObjects)
    objName = strtrim(allObjects{i});
    audioFile = fullfile('AuditoryPrompt', objName + ".mp3");

    try
        [y, Fs] = audioread(audioFile);

        % Trim and convert to 2-channel (stereo)
        numSamples = min(round(1.5*Fs), size(y,1));
        y_trim = y(1:numSamples, :);

        if size(y_trim,2) == 1
            y_trim = repmat(y_trim, 1, 2);
        end

        % Transpose to channels × samples for PsychPortAudio
        y_trim = y_trim';

        % Normalize
        if max(abs(y_trim(:))) > 1
            y_trim = y_trim / max(abs(y_trim(:)));
        end

        audioCache(objName) = struct('wave', y_trim, 'Fs', Fs);

    catch ME
        warning('Could not load %s: %s', audioFile, ME.message);
    end
end

% Preload all images
imgNumsToLoad = [6 8 10];   % used for memory test
imgNumsPercept = [10];      % fixed in your code

allImgNums = unique([imgNumsToLoad imgNumsPercept]);

for i = 1:numel(allObjects)
    objName = char(strtrim(allObjects{i}));

    for n = allImgNums
        key = sprintf('%s_%d', objName, n);
        imgPath = fullfile('imgs_diffusion', [objName num2str(n) '.jpg']);

        try
            imageCache(key) = imread(imgPath);
        catch
            warning('Missing image: %s', imgPath);
        end
    end
end

disp('Preloading complete.');

%%  Block loop 
for b = 1:nBlocks
    T = T_blocks{b};

    % Optional block start screen
    DrawFormattedText(win, sprintf(['Starting Block %d of %d\n\n' ...
    'Press any key to continue.'], ...
    b, nBlocks), 'center', 'center', black);

    Screen('FillRect', win, black_rgb, trigRect);
    Screen('Flip', win); 
    KbStrokeWait;

    trialOrder = randperm(height(T));

    %%  Trial Loop
    for idx = 1:height(T)
        tr = trialOrder(idx);

        % Define prompt here
        TargetObjPrompt = string(T.ObjectPrompt{tr});  % The spoken cue (object name)
        TargetObjName   = string(T.Object{tr});  % The actual target object

        
        % check esc
        [~, ~, keyCode] = KbCheck;
        if  keyCode(escapeKey)
            Screen('CloseAll'); 
            PsychPortAudio('Close', pahandle); 
            error('Experiment terminated by user.');
        end

        % Stage 1: Blank screen
        Screen('FillRect', win, white); 
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win); 
        WaitSecs(blankTime);

        %% Stage 2: Image perception
        % Choose target object and distractor object

        targetObj = strtrim(T.Object{tr});  % Target object name
        targetImgNum = 10;  % always imgNums(10)
        targetColor = strtrim(T.Color{tr});
        non_targetObjs = T(strcmp(T.Color, targetColor), :);
        non_targetObjs(strcmp(non_targetObjs.Object, targetObj), :) = [];
        distractIdx = randi(height(non_targetObjs));
        distractObj = strtrim(non_targetObjs.Object(distractIdx));
        distractImgNum = 10;
        ObjCategory = strtrim(T.Category{tr});

        % Randomize order of presentation (target first or distractor first)
        if rand < 0.5
            order = {'target','distract'};
        else
            order = {'distract','target'};
        end

        target_order = find(strcmp(order, 'target'));

        if strcmp(order{1}, 'target')
            Obj1 = targetObj;
            Obj2 = distractObj;
        else
            Obj1 = distractObj;
            Obj2 = targetObj;
        end
        
        Obj1 = char(Obj1);
        Obj2 = char(Obj2);

        % Load and show the image
        key1 = sprintf('%s_%d', Obj1, 10);
        key2 = sprintf('%s_%d', Obj2, 10);

        img1 = imageCache(key1);
        img2 = imageCache(key2);

        % present img1
        tex = Screen('MakeTexture', win, img1);
        Screen('DrawTexture', win, tex, [], ...
            CenterRectOnPoint([0 0 imgWidth imgHeight], screenX/2, screenY*0.5));
        
        % Flip and show
        % the next 4 lines is a whole process of turn on and turn off a trigger
        Screen('FillRect', win, trigImg1Start, trigRect); %% set trigger for img1 start
        ts = Screen('Flip', win);

        TrigCheck_results = logTrig( ...
            TrigCheck_results, TrigCounter, b, ...
            TargetObjPrompt, TargetObjName, target_order, distractObj, ...
            224, ts, ObjCategory);

        TrigCounter = TrigCounter + 1;
        
        % present img1 again after flip, we want it to stay, or the image just flash
        tex = Screen('MakeTexture', win, img1);
        Screen('DrawTexture', win, tex, [], ...
            CenterRectOnPoint([0 0 imgWidth imgHeight], screenX/2, screenY*0.5));
        
        Screen('FillRect', win, black_rgb, trigRect); % turn off trigger for img1 start
        Screen('Flip', win);

        WaitSecs(imageDur); % present img1

        Screen('FillRect', win, trigImg1End, trigRect); %% set trigger for img1 end
        ts = Screen('Flip', win);

        TrigCheck_results = logTrig( ...
            TrigCheck_results, TrigCounter, b, ...
            TargetObjPrompt, TargetObjName, target_order, distractObj, ...
            225, ts, ObjCategory);

        TrigCounter = TrigCounter + 1;
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);

        % Clear texture
        if exist('tex','var')
            Screen('Close', tex);
        end
        
        % Show blank between the two
        Screen('FillRect', win, white);
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win);
        WaitSecs(blankTime);
        
        % present img2
        tex = Screen('MakeTexture', win, img2);
        Screen('DrawTexture', win, tex, [], ...
            CenterRectOnPoint([0 0 imgWidth imgHeight], screenX/2, screenY*0.5));
        
        % Flip and show
        Screen('FillRect', win, trigImg2Start, trigRect); %% set trigger for Img2 start
        ts = Screen('Flip', win);

        TrigCheck_results = logTrig( ...
            TrigCheck_results, TrigCounter, b, ...
            TargetObjPrompt, TargetObjName, target_order, distractObj, ...
            226, ts, ObjCategory);

        TrigCounter = TrigCounter + 1;

        % present img2 again after flip
        tex = Screen('MakeTexture', win, img2);
        Screen('DrawTexture', win, tex, [], ...
            CenterRectOnPoint([0 0 imgWidth imgHeight], screenX/2, screenY*0.5));

        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);

        WaitSecs(imageDur);

        Screen('FillRect', win, trigImg2End, trigRect); %% set trigger for Img2 end
        ts = Screen('Flip', win);

        TrigCheck_results = logTrig( ...
            TrigCheck_results, TrigCounter, b, ...
            TargetObjPrompt, TargetObjName, target_order, distractObj, ...
            227, ts, ObjCategory);

        TrigCounter = TrigCounter + 1;
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);
        
        % Clear texture
        if exist('tex','var')
            Screen('Close', tex);
        end
        
        % blank after both images, but before cue audio
        Screen('FillRect', win, white);
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win);
        WaitSecs(blankTime);

        % close eyes to prepare for recall
        Screen('TextSize', win, 40);
        DrawFormattedText(win, sprintf(['Please first close eyes, then press button under right thumb to wait for description.' newline newline ...
            'Keep eyes closed when recalling until hearing "Ding" again after the description.'], ...
            b, nBlocks), 'center', 'center', black);

        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);

        if USE_SIM
            WaitSecs(0.2); % fake reaction time
            pair_CloseEyes = {'right box','white'};
        else
            pair_CloseEyes = getButtonColor(selection_CloseEyes,true);
        end

        %  Stage 3: Cue Audio         
        cueData = audioCache('Cue');
        PsychPortAudio('FillBuffer', pahandle, cueData.wave);
        PsychPortAudio('Start', pahandle, 1, 0, 1);
        WaitSecs(cuePlaySecs);
        PsychPortAudio('Stop', pahandle);

        % Stage 4: Target Object Audio
        TargetObjName = string(T.Object{tr});  
        audioData = audioCache(TargetObjName);
        PsychPortAudio('FillBuffer', pahandle, audioData.wave);

        Screen('FillRect', win, trigPromptStart, trigRect); %% set trigger for prompt start
        ts = Screen('Flip', win);

        TrigCheck_results = logTrig( ...
            TrigCheck_results, TrigCounter, b, ...
            TargetObjPrompt, TargetObjName, target_order, distractObj, ...
            228, ts, ObjCategory);

        TrigCounter = TrigCounter + 1;
        
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);
        PsychPortAudio('Start', pahandle, 1, 0, 1);   % start playback

        PsychPortAudio('Stop', pahandle, 1);          % wait until done
        Screen('FillRect', win, trigPromptEnd, trigRect); %% set trigger for prompt end
        ts = Screen('Flip', win);

        TrigCheck_results = logTrig( ...
            TrigCheck_results, TrigCounter, b, ...
            TargetObjPrompt, TargetObjName, target_order, distractObj, ...
            229, ts, ObjCategory);

        TrigCounter = TrigCounter + 1;        
        
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);

        %% Stage 5: Memory period
        Screen('FillRect', win, white); 
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win); 
        
        WaitSecs(recall_time);
        
        Screen('FillRect', win, trigRecallEnd, trigRect); %% set trigger for recall end
        ts = Screen('Flip', win);

        TrigCheck_results = logTrig( ...
            TrigCheck_results, TrigCounter, b, ...
            TargetObjPrompt, TargetObjName, target_order, distractObj, ...
            230, ts, ObjCategory);

        TrigCounter = TrigCounter + 1;        
        
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win); 

        % play cue again to let participants open eyes
        PsychPortAudio('FillBuffer', pahandle, cueData.wave);
        PsychPortAudio('Start', pahandle, 1, 0, 1);
        WaitSecs(cuePlaySecs);
        PsychPortAudio('Stop', pahandle);

        %% Stage 6: Memory Test
        % present target object
        testImgNum = randsample([6 8 10], 1);

        keyTest = sprintf('%s_%d', targetObj, testImgNum);
        img = imageCache(keyTest);

        tex = Screen('MakeTexture', win, img);
        % Draw target image centered at top half of the screen
        Screen('DrawTexture', win, tex, [], ...
            CenterRectOnPoint([0 0 imgWidth imgHeight], screenX*0.5, screenY*0.5));

        question = 'Is this the image you just saw?';
        Screen('TextSize', win, 80); % set font size

        DrawFormattedText(win, question, 'center', screenY*0.2, black);
        optionText = 'YES                NO';
        DrawFormattedText(win, optionText, 'center', round(screenY*0.8), black);
        Screen('FillRect', win, black_rgb, trigRect); 
        CatchQuestion_Onset = Screen('Flip', win);

        catchAnswer = '';

        % set button for MEG controller (catch question)

        % Simulate response for catch question
        if USE_SIM
            % Simulate button press
            catchAnswer = randsample({'YES'},1);
            % Simulate reaction time
            CatchQuestion_Resptime = 0.2 ;
            % Simulate onset time (for logging)
            CatchQuestion_Onset = GetSecs();
        else

            while true

                % Blocking call: waits until a valid button press is detected
                pair_CatchQuestion = getButtonColor(selection_CatchQuestion,true);  % blocking = true

                % Build key string
                key = sprintf('%s|%s', pair_CatchQuestion{1}, pair_CatchQuestion{2});

                % Map to resp to CatchQuestion
                if isKey(buttonMap, key)
                    catchAnswer = buttonMap(key);
                    break;
                else
                    % continue looping until a mapped button is pressed
                end
            end
        end

        Screen('FillRect', win, trigQuestionResp, trigRect); %% trigger for question resp
        ts = Screen('Flip', win);

        Screen('FillRect', win, black_rgb, trigRect); %% trigger for question resp
        Screen('Flip', win);
        

        TrigCheck_results = logTrig( ...
            TrigCheck_results, TrigCounter, b, ...
            TargetObjPrompt, TargetObjName, target_order, distractObj, ...
            231, ts, ObjCategory);

        TrigCounter = TrigCounter + 1;

        CatchQuestion_Resptime = GetSecs();
    
        % Save trial results into the preallocated struct array
        results(trialCounter).Block = b;
        results(trialCounter).BlockRecallTime = recall_time;
        results(trialCounter).TargetPrompt = TargetObjPrompt;
        results(trialCounter).TargetObject = TargetObjName;
        results(trialCounter).TargetOrder = target_order;
        results(trialCounter).DistractObject = distractObj;
        results(trialCounter).Question_Resp = catchAnswer;
        results(trialCounter).Question_CorIMG = testImgNum;
        results(trialCounter).Question_RT = CatchQuestion_Resptime - CatchQuestion_Onset;

%         for TrigIdx = 0:7
%             TrigCheck_results((trialCounter - 1) * 8 + TrigIdx + 1).Channel = 224 + TrigIdx;
%             TrigCheck_results((trialCounter - 1) * 8 + TrigIdx + 1).Block = b;
%             TrigCheck_results((trialCounter - 1) * 8 + TrigIdx + 1).TargetPrompt = TargetObjPrompt;
%             TrigCheck_results((trialCounter - 1) * 8 + TrigIdx + 1).TargetObject = TargetObjName;
%             TrigCheck_results((trialCounter - 1) * 8 + TrigIdx + 1).TargetOrder = target_order;
%             TrigCheck_results((trialCounter - 1) * 8 + TrigIdx + 1).DistractObject = distractObj;
%             TrigCheck_results((trialCounter - 1) * 8 + TrigIdx + 1).Onset = (trialCounter - 1) * 8 + TrigIdx + 1;
%             TrigCheck_results((trialCounter - 1) * 8 + TrigIdx + 1).Trial_Type = ObjCategory;
%         end

        % Convert results struct to table
        resultsTable = struct2table(results);
        TrigCheck_resultsTable = struct2table(TrigCheck_results);

        % Save as CSV
        writetable(resultsTable, filename);
        writetable(TrigCheck_resultsTable, TrigCheck_filename);

        trialCounter = trialCounter + 1;
    end

        % Optional: block break before next block
    if b < numel(T_blocks)
        breakMsg = sprintf(['End of Block %d\n\n' ... 
            'You can take a short break. ' newline ...
            'Please tell experimenter when ready for next block.'], b);
        DrawFormattedText(win, breakMsg, 'center', 'center', black);
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win);
        KbStrokeWait;
    end
end

%% ------------------- Stage 7: End Page -------------------
DrawFormattedText(win, 'End. Please wait for experimenter for further action.', 'center', 'center', black);
Screen('FillRect', win, black_rgb, trigRect); 
Screen('Flip', win);
KbWait([], 2);

% switch off trigger
if USE_VPIXX
    Datapixx('DisablePixelMode');
    Datapixx('RegWr');
    Datapixx('Close');
end

%% ------------------- Cleanup -------------------
PsychPortAudio('Close', pahandle);
Screen('CloseAll');

%% Stop MATLAB console output recording

% Turn off diary to stop recording and close the file
diary off;

fprintf('Console output saved to: %s\n', logFilePath);

function TrigCheck_results = logTrig(TrigCheck_results, index, block, ...
    objPrompt, objName, targetOrder, distractObj, channelNum, onset_time, trialType)

    TrigCheck_results(index).Block         = block;
    TrigCheck_results(index).TargetPrompt  = objPrompt;
    TrigCheck_results(index).TargetObject  = objName;
    TrigCheck_results(index).TargetOrder   = targetOrder;
    TrigCheck_results(index).DistractObject = distractObj;

    % Channel number (224–231)
    TrigCheck_results(index).Channel       = channelNum;

    % Time of the trigger flip
    TrigCheck_results(index).Onset         = onset_time;

    TrigCheck_results(index).Trial_Type    = trialType;
end
