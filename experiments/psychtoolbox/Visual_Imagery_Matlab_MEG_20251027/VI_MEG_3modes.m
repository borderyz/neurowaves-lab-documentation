%% Visual Imagery Official
clear all; clc; close all;

% ===== Run mode (edit this only) =====
RUN_MODE = 'MEG';  
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
filename = fullfile(beh_datafolder, sprintf('sub-%s_task-VI_split-2_trials.csv', subNumStr));
TrigCheck_filename = fullfile(beh_datafolder, sprintf('sub-%s_task-VI_split-2_events.csv', subNumStr));

%% MATLAB console output data saving
taskName = 'visualimagery';

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
Screen('Preference', 'SkipSyncTests', 1);  % only for debugging
white = [255 255 255];
black = [0 0 0];
KbName('UnifyKeyNames');
black_rgb = [0 0 0];
% Keys
escapeKey = KbName('ESCAPE');
% Open window (use 'win' consistently)
[win, rect] = PsychImaging('OpenWindow', max(Screen('Screens')), white);
[screenX, screenY] = RectSize(rect);
Screen('TextSize', win, 40);

%% Triggers setup

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
trig.PromptStart = [4  0  0]; % ch224
trig.PromptEnd   = [16  0  0]; % ch225
trig.ImagineEnd = [64 0 0]; % ch226
trig.RateResp = [0  1 0]; % ch227
trig.QuestionResp = [0  4 0]; % ch228

PromptStartTrig = trig.PromptStart;
PromptEndTrig = trig.PromptEnd;
ImagineEndTrig = trig.ImagineEnd;
RateRespTrig = trig.RateResp;
QuestionRespTrig = trig.QuestionResp;

% VPIXX SETUP
if USE_VPIXX
    Datapixx('Open');
    Datapixx('EnablePixelMode');
    Datapixx('RegWr');
end

%% set up buttons for MEG controller
% set button for rate
% Map from button ('box|color') to resp we will record
buttonMap = containers.Map;
buttonMap('left box|blue')   = 1; % value 1
buttonMap('left box|green')  = 2; % ...
buttonMap('left box|yellow') = 3;
buttonMap('left box|red')    = 4;
buttonMap('left box|white')  = 5; % value 5

% Define which buttons to listen to (example: right box colors)
selection_rate = struct('left_box', {{'red', 'green', 'blue', 'yellow', 'white'}});

% set button for CatchQuestion
buttonMap('right box|white') = 'StartImagine';
buttonMap('right box|red')   = 'YES'; % YES
buttonMap('right box|yellow')  = 'NO'; % NO
buttonMap('right box|green') = 'DONT KNOWN'; % DONT KNOWN

% Define which buttons to listen to (example: right box colors)
selection_CatchQuestion = struct('right_box', {{'red', 'yellow', 'green'}});
selection_CloseEyes = struct('right_box', {{'white'}});

% Audio setup
InitializePsychSound(1);
pahandle = PsychPortAudio('Open', [], 1, 1, 48000, 2); % playback device, freq 48000, 2 channels

%% Experiment constants (tweak if needed)
blankTime = 0.5; % inter-trial blank interval (seconds)
cuePlaySecs = 1.0; % seconds to play cue
audioTrimSecs = 1.5; % how long to trim object audio for playback
imgNums = [1, 3, 5, 7, 10];  % as in your code
imgWidth = 500; imgHeight = 500;
imagine_time = 4; 
textYPos = round(screenY*0.8);    % rating text lower

%%  Instruction 
Instruction = ['The official experiment is as similar as the practice you just had. ' newline newline ...
    'Only difference is no reference image is presented, ' ...
    'please use the stardard you learned in practice to rate for your imagination each trial. ' newline newline ...
    'MEG Recording is being setup please be patient, press space to continue'];
DrawFormattedText(win, Instruction, 'center', 'center', black, 80);  % 70 = wrap at 70 chars per line
Screen('FillRect', win, black_rgb, trigRect);
Screen('Flip', win);
KbStrokeWait;  % wait for any key

%% Persistent blank screen
Screen('FillRect', win, white);
Screen('FillRect', win, black_rgb, trigRect);
Screen('Flip', win);

if USE_DEBUG_TRIALS
    % Load block file
    blockFiles = {
        'VI_B1_trials_DEBUG.csv'
        'VI_B2_trials_DEBUG.csv'
    };
else
    % Load block file
    blockFiles = {
        'VI_B1_trials.csv'
        'VI_B2_trials.csv'
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
results = repmat(struct('Block',NaN, 'BlockImagineTime', '', 'Prompt','','Object','','Rate',NaN,'Rate_RT',NaN,...
    'Question_Resp','','Question_CorAnswer','','Question_RT',NaN), nTrialsTotal, 1);

TrigCheck_results = repmat(struct('Block',NaN, 'TargetPrompt','','TargetObject','', ...
    'Onset', '', 'Duration','','Channel','','Trial_Type', ''), nTrialsTotal, 1);

HideCursor;
% set counter for trial and trigger check
trialCounter = 1;
TrigCounter = 1;

%% PRELOAD AUDIO FILES BEFORE TRIAL LOOP
disp('Preloading audio files...');

audioCache = containers.Map();   % key = filename, value = struct(wave, Fs)

% Preload cue audio
cueFile = fullfile('AuditoryPrompt', 'Cue.mp3');
[cueWave, cueFs] = audioread(cueFile);
audioCache('Cue') = struct('wave', cueWave', 'Fs', cueFs);

% Preload all object audio used in all blocks
for b = 1:nBlocks
    T = T_blocks{b};
    for i = 1:height(T)

        objName = string(T.Object{i});
        audioFile = fullfile('AuditoryPrompt', objName + ".mp3");

        if ~isKey(audioCache, objName)
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
    end
end



disp('Audio preloading complete.');

%%  Block loop 
for b = 1:nBlocks
    T = T_blocks{b};

    % Optional block start screen
    DrawFormattedText(win, sprintf(['Starting Block %d of %d\n\n' ...
    'Press space to continue.'], ...
    b, nBlocks), 'center', 'center', black);
    
    Screen('FillRect', win, black_rgb, trigRect);
    Screen('Flip', win); 
    KbStrokeWait;

    trialOrder = randperm(height(T));

    %%  Trial Loop 
    for idx = 1:height(T)
        tr = trialOrder(idx);

        % Extract trial info here (MUST be before using objPrompt)
        objPrompt   = string(T.ObjectPrompt{tr});
        objName     = string(T.Object{tr});
        ObjCategory = string(T.Category{tr});
        question    = T.CatchQuestion{tr};

        % Check ESC
        [~, ~, keyCode] = KbCheck;
        if  keyCode(escapeKey)
            Screen('CloseAll'); 
            PsychPortAudio('Close', pahandle); 
            error('Experiment terminated by user.');
        end

        % Stage 1: Prepare to close eyes and start imagine
        Screen('TextSize', win, 40);
        DrawFormattedText(win, sprintf(['Please first close eyes, then press button under right thumb to start this trial.' newline newline ...
            'Keep eyes closed when imagining until hearing "Ding" again after the description.'], ...
            b, nBlocks), 'center', 'center', black);
        
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);

        if USE_SIM
            WaitSecs(0.2); % fake reaction time
            pair_CloseEyes = {'right box','white'};
        else
            pair_CloseEyes = getButtonColor(selection_CloseEyes,true);
        end


        %  Stage 2: Cue Audio
        cueData = audioCache('Cue');
        PsychPortAudio('FillBuffer', pahandle, cueData.wave);
        PsychPortAudio('Start', pahandle, 1, 0, 1);
        WaitSecs(cuePlaySecs);
        PsychPortAudio('Stop', pahandle);
    
        % Stage 3: Random Object Audio
        objName = string(T.Object{tr});
        audioData = audioCache(objName);

        PsychPortAudio('FillBuffer', pahandle, audioData.wave);

        Screen('FillRect', win, PromptStartTrig, trigRect);
%         Screen('Flip', win);
        ts = Screen('Flip', win);



        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);
        
                % immediately record trigger for ending audio
        TrigCheck_results = logTrig(TrigCheck_results, TrigCounter, b, objPrompt, objName, 224, ts, ObjCategory);
        TrigCounter = TrigCounter + 1;

        PsychPortAudio('Start', pahandle, 1, 0, 1);   % start audio
        
        PsychPortAudio('Stop', pahandle, 1);    % stop audio
        Screen('FillRect', win, PromptEndTrig, trigRect);
%         Screen('Flip', win);
        ts = Screen('Flip', win);



        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);

                % immediately record trigger for ending audio
        TrigCheck_results = logTrig(TrigCheck_results, TrigCounter, b, objPrompt, objName, 225, ts, ObjCategory);
        TrigCounter = TrigCounter + 1;

        %% Stage 4: Imagination period
        Screen('FillRect', win, white); 
        %When changing the background color to anything, make sure the trigRect is staying black, so just before the flip add it to black again
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win); 
        WaitSecs(imagine_time);
        Screen('FillRect', win, ImagineEndTrig, trigRect); %% set trigger for prompt end
%         Screen('Flip', win);

        ts = Screen('Flip', win);


        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win); 
        

        % record trigger for catch question response
        TrigCheck_results = logTrig(TrigCheck_results, TrigCounter, b, objPrompt, objName, 228, ts, ObjCategory);
        TrigCounter = TrigCounter + 1;

        % play cue again to let participants open eyes
        cueData = audioCache('Cue');
        PsychPortAudio('FillBuffer', pahandle, cueData.wave);
        PsychPortAudio('Start', pahandle, 1, 0, 1);
        WaitSecs(cuePlaySecs);
        PsychPortAudio('Stop', pahandle);

        %% Stage 5: Imagination Vividness Rating

        % set rate text
        Screen('TextSize', win, 80);
        DrawFormattedText(win, 'Please rate your imagination vividness', 'center', screenY*0.25, black);
        % Flip once to show images and record onset
        Screen('FillRect', win, black_rgb, trigRect);
        Rate_Onset = Screen('Flip', win);
    
        rating = NaN;
        
        if USE_SIM
            WaitSecs(0.2);
            pair_rate = {'left box', 'green'};
            key = sprintf('%s|%s', pair_rate{1}, pair_rate{2});
            rating = buttonMap(key);
        else
            while true
                pair_rate = getButtonColor(selection_rate,true);
                key = sprintf('%s|%s', pair_rate{1}, pair_rate{2});
                if isKey(buttonMap, key)
                    rating = buttonMap(key);
                    break;
                end
            end
        end

        Rate_Resptime = GetSecs();  % get resp time for rating

        Screen('FillRect', win, RateRespTrig, trigRect); %% trigger for rate response
%         Screen('Flip', win);

        ts = Screen('Flip', win);



        %WaitSecs(0.005); % Short trigger pulse
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);
        
        % record trigger for rate
        TrigCheck_results = logTrig(TrigCheck_results, TrigCounter, b, objPrompt, objName, 227, ts, ObjCategory);
        TrigCounter = TrigCounter + 1;

        %% Stage 6: Catch Question
        question = T.CatchQuestion{tr};
        Screen('TextSize', win, 80); % set font size
        DrawFormattedText(win, question, 'center', screenY*0.25, black);
        optionText = 'YES        NO        DONT KNOW';
        DrawFormattedText(win, optionText, 'center', round(screenY*0.5), black);
        Screen('FillRect', win, black_rgb, trigRect);
        CatchQuestion_Onset = Screen('Flip', win);
    
        catchAnswer = '';
        
        if USE_SIM
            WaitSecs(0.2);
            pair_CatchQuestion = {'right box', 'green'};
            key = sprintf('%s|%s', pair_CatchQuestion{1}, pair_CatchQuestion{2});
            catchAnswer = buttonMap(key);
        else
            while true
                pair_CatchQuestion = getButtonColor(selection_CatchQuestion,true);
                key = sprintf('%s|%s', pair_CatchQuestion{1}, pair_CatchQuestion{2});
                if isKey(buttonMap, key)
                    catchAnswer = buttonMap(key);
                    break;
                end
            end
        end

        CatchQuestion_Resptime = GetSecs(); % get resp time for CatchQuestion

        Screen('FillRect', win, QuestionRespTrig, trigRect); %% trigger for question resp
%         Screen('Flip', win);

        ts = Screen('Flip', win);


        %WaitSecs(0.005); % Short trigger pulse
        Screen('FillRect', win, black_rgb, trigRect); %% trigger for question resp
        Screen('Flip', win);
        
        % record trigger for catch question response
        TrigCheck_results = logTrig(TrigCheck_results, TrigCounter, b, objPrompt, objName, 228, ts, ObjCategory);
        TrigCounter = TrigCounter + 1;


        % Save trial results into the preallocated struct array
        results(trialCounter).Block = b;
        results(trialCounter).BlockImagineTime = imagine_time;
        results(trialCounter).Prompt = objPrompt;
        results(trialCounter).Object = objName;
        results(trialCounter).Rate = rating;
        results(trialCounter).Rate_RT = Rate_Resptime - Rate_Onset;
        results(trialCounter).Question_Resp = catchAnswer;
        results(trialCounter).Question_CorAnswer = string(T.CorrectAnswer{tr});
        results(trialCounter).Question_RT = CatchQuestion_Resptime - CatchQuestion_Onset;

        %% save results
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
        breakMsg = sprintf('End of Block of %d\n\nYou can take a short break. \n\n When you are ready, start next block by pressing space.', b);
        DrawFormattedText(win, breakMsg, 'center', 'center', black);
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);
        KbStrokeWait;
    end
end

%%  Stage 7: End Page 
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

%% Cleanup 
PsychPortAudio('Close', pahandle);
Screen('CloseAll');

%% Stop MATLAB console output recording

% Turn off diary to stop recording and close the file
diary off;

fprintf('Console output saved to: %s\n', logFilePath);


% function to log trigger history
function TrigCheck_results = logTrig(TrigCheck_results, counter, block, objPrompt, objName, channel, onset_time, trial_type)

    TrigCheck_results(counter).Block        = block;
    TrigCheck_results(counter).TargetPrompt = objPrompt;
    TrigCheck_results(counter).TargetObject = objName;
    TrigCheck_results(counter).Channel      = channel;
    TrigCheck_results(counter).Onset        = onset_time;
    TrigCheck_results(counter).Trial_Type   = trial_type;
end