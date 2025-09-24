%% Visual Imagery Official
clear; clc; close all;

Datapixx('Open');
Datapixx('DisablePixelMode'); 
Datapixx('RegWr');

%% Setup 
Screen('Preference', 'SkipSyncTests', 1);  % only for debugging
white = [255 255 255];
black = [0 0 0];
KbName('UnifyKeyNames');
black_rgb = [0 0 0];
% Keys
escapeKey = KbName('ESCAPE');

%% Participant Data
name1 = 'Participant Data';
prompt1 = {'Subject Number', 'Subject ID', 'Sex (f/m)', 'Age', 'Nationality'};
numlines1 = 1;
defaultanswer1 = {'0', 'YZ', 'm', '30', 'CHN'};
answer1 = inputdlg(prompt1, name1, numlines1, defaultanswer1);
DEMO.num = str2double(answer1{1});
DEMO.ID  = answer1{2};
DEMO.sex = answer1{3};
DEMO.age = str2double(answer1{4});
DEMO.Nationality = answer1{5};

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
trig.PromptStart = [4  0  0]; % ch224
trig.PromptEnd   = [16  0  0]; % ch225
trig.ImagineEnd = [64 0 0]; % ch226
trig.RateResp = [0  1 0]; % ch227
trig.QuestionResp = [0  4 0]; % ch228
% trig.go_noresp = [0 16 0];  % ch229 % Go trials with NO Responses (Too Slow/Error)
% trig.nogo_resp = [0 64 0]; % ch230 NoGo trials with Responses (Error)
% trig.nogo_noresp = [0 0  1]; % ch231 NoGo trials with NO Responses (Correct)

PromptStartTrig = trig.PromptStart;
PromptEndTrig = trig.PromptEnd;
ImagineEndTrig = trig.ImagineEnd;
RateRespTrig = trig.RateResp;
QuestionRespTrig = trig.QuestionResp;

%-------------------------------------------
% VPIXX SETUP
%-------------------------------------------    
Datapixx('Open');
Datapixx('EnablePixelMode'); 
Datapixx('RegWr');


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
Instruction = 'MEG Recording is being setup please be patient, press any key to continue';
DrawFormattedText(win, Instruction, 'center', 'center', black);
Screen('FillRect', win, black_rgb, trigRect);
Screen('Flip', win);
KbStrokeWait;  % wait for any key

%% Persistent blank screen
Screen('FillRect', win, white);
Screen('FillRect', win, black_rgb, trigRect);
Screen('Flip', win);

% Load block file
blockFiles = {
    'C:\Users\vpixx\PycharmProjects\meg-pipeline\experiments\psychopy\Visual_Imagery_DM_YZ\Visual_Imagery_Matlab_MEG\VI_B1_trials.csv'
    'C:\Users\vpixx\PycharmProjects\meg-pipeline\experiments\psychopy\Visual_Imagery_DM_YZ\Visual_Imagery_Matlab_MEG\VI_B2_trials.csv'
};

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

HideCursor;
trialCounter = 1;

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

        % Check ESC
        [keyIsDown, ~, keyCode] = KbCheck;
        if keyIsDown && keyCode(escapeKey)
            Screen('CloseAll'); PsychPortAudio('Close', pahandle); error('Experiment terminated by user.');
        end

        % Stage 1: Blank screen
        Screen('FillRect', win, white); 
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win); 
        WaitSecs(blankTime);

        %  Stage 2: Cue Audio
        % (If you have a special Cue file)
        try
            [cueWave, cueFs] = audioread(fullfile('C:\Users\vpixx\PycharmProjects\meg-pipeline\experiments\psychopy\Visual_Imagery_DM_YZ\AuditoryPrompt\', 'Cue.mp3'));
            % Ensure cueWave is channels x samples for PsychPortAudio:
            PsychPortAudio('FillBuffer', pahandle, cueWave'); % audioread gives samples x ch
            PsychPortAudio('Start', pahandle, 1, 0, 1);
            WaitSecs(cuePlaySecs);
            PsychPortAudio('Stop', pahandle);
        catch ME
            % If cue file missing, continue but warn
            warning('Cue audio not played: %s', ME.message);
        end
    
        % Stage 3: Random Object Audio
        objPrompt = string(T.ObjectPrompt{tr}); 
        objName = string(T.Object{tr}); % ensure we use table row 'tr' 

        audioFile = fullfile('C:\Users\vpixx\PycharmProjects\meg-pipeline\experiments\psychopy\Visual_Imagery_DM_YZ\AuditoryPrompt\', objName + ".mp3"); 
        numChannels = 2;   % must match pahandle
        [y, Fs] = audioread(audioFile);
        numSamples = min(round(1.5*Fs), size(y,1));

        y_trim = y(1:numSamples, :);   % samples × channels

        % If mono audio, replicate to stereo
        if size(y_trim,2) == 1 && numChannels == 2
            y_trim = repmat(y_trim, 1, 2);   % now samples × 2
        end

        % Transpose to channels × samples
        y_trim = y_trim';

        % Ensure double and normalize
        y_trim = double(y_trim);
        if max(abs(y_trim(:))) > 1
            y_trim = y_trim / max(abs(y_trim(:)));
        end

        PsychPortAudio('FillBuffer', pahandle, y_trim);


        Screen('FillRect', win, PromptStartTrig, trigRect);
        Screen('Flip', win);
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);
        PsychPortAudio('Start', pahandle, 1, 0, 1);   % start audio


        PsychPortAudio('Stop', pahandle, 1);    % stop audio
        Screen('FillRect', win, PromptEndTrig, trigRect);
        Screen('Flip', win);
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);

        %% Stage 4: Imagination period
        Screen('FillRect', win, white); 
        %When changing the background color to anything, make sure the trigRect is staying black, so just before the flip add it to black again
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win); 
        WaitSecs(imagine_time);
        Screen('FillRect', win, ImagineEndTrig, trigRect); %% set trigger for prompt end
        Screen('Flip', win);
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win); 
        %% Stage 5: Imagination Vividness Rating

        % set rate text
        Screen('TextSize', win, 80);
        DrawFormattedText(win, 'Please rate your imagination vividness', 'center', screenY*0.25, black);
        % Flip once to show images and record onset
        Screen('FillRect', win, black_rgb, trigRect);
        Rate_Onset = Screen('Flip', win);
    
        % Wait for numeric key 1-5
        validKeys = [KbName('1!') KbName('2@') KbName('3#') KbName('4$') KbName('5%')];
        rating = NaN;
        keyPressed = false;
        while ~keyPressed
            [~, ~, keyCode] = KbCheck;
            if keyCode(escapeKey)
                Screen('CloseAll'); PsychPortAudio('Close', pahandle); error('Experiment terminated by user (ESC pressed).');
            end
            for k = 1:length(validKeys)
                if keyCode(validKeys(k))
                    rating = k;
                    keyPressed = true;
                    break;
                end
            end
            WaitSecs(0.001);
        end

        Screen('FillRect', win, RateRespTrig, trigRect); %% trigger for rate response
        Screen('Flip', win);
        WaitSecs(0.005); % Short trigger pulse
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);
        Rate_Resptime = GetSecs();  

        %% Stage 6: Catch Question
        question = T.CatchQuestion{tr};
        Screen('TextSize', win, 80); % set font size
        DrawFormattedText(win, question, 'center', screenY*0.4, black);
        optionText = 'YES        NO        DON''T KNOW';
        DrawFormattedText(win, optionText, 'center', round(screenY*0.6), black);
        Screen('FillRect', win, black_rgb, trigRect);
        CatchQuestion_Onset = Screen('Flip', win);
    
        % Wait for key s/d/f
        key_s = KbName('s');
        key_d = KbName('d');
        key_f = KbName('f');
        keyPressed = false;
        catchAnswer = '';
        while ~keyPressed
            [~, ~, keyCode] = KbCheck;
            if keyCode(escapeKey)
                Screen('CloseAll'); PsychPortAudio('Close', pahandle); error('Experiment terminated by user (ESC pressed).');
            end
            if keyCode(key_s)
                catchAnswer = 'YES';
                keyPressed = true;
            elseif keyCode(key_d)
                catchAnswer = 'NO';
                keyPressed = true;
            elseif keyCode(key_f)
                catchAnswer = 'DON''T KNOW';
                keyPressed = true;
            end
            WaitSecs(0.001);
        end

        Screen('FillRect', win, QuestionRespTrig, trigRect); %% trigger for question resp
        Screen('Flip', win);
        WaitSecs(0.005); % Short trigger pulse
        Screen('FillRect', win, black_rgb, trigRect); %% trigger for question resp
        Screen('Flip', win);

        CatchQuestion_Resptime = GetSecs();
    
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
Datapixx('DisablePixelMode'); 
Datapixx('RegWr');
Datapixx('Close');

%%  Cleanup 
PsychPortAudio('Close', pahandle);
Screen('CloseAll');

%% save results
% Convert results struct to table
resultsTable = struct2table(results);
subNumStr = answer1{1};  % e.g., '07'

% Create folder path
beh_datafolder = fullfile(pwd, 'Beh_Data')

% Build filename
% filename = sprintf('Visual_Imagery_MEG_Practice_Sub%s.csv', subNumStr);
filename = fullfile(beh_datafolder, sprintf('Visual_Imagery_MEG_Practice_Sub%s.csv', subNumStr));

% Save as CSV
writetable(resultsTable, filename);
fprintf('Results saved to %s\n', filename);