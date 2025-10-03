%% Visual Working Memory Official
clear; clc; close all;

% set VPIXX to DisablePixelMode
Datapixx('Open');
Datapixx('DisablePixelMode');  % disable pixelmodel at the beginning
Datapixx('RegWr');

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
trigImg1Start = [4  0  0]; % ch224
trigImg1End   = [16  0  0]; % ch225
trigImg2Start = [64 0 0]; % ch226
trigImg2End = [0  1 0]; % ch227
trigPromptStart = [0  4 0]; % ch228
trigPromptEnd = [0 16 0];  % ch229 
trigRecallEnd = [0 64 0]; % ch230 
trigQuestionResp = [0 0  1]; % ch231 

%-------------------------------------------
% VPIXX SETUP
%-------------------------------------------    
Datapixx('Open');
Datapixx('EnablePixelMode');   % open pixel model
Datapixx('RegWr');



%% set up buttons for MEG controller
% set button for CatchQuestion
buttonMap = containers.Map;
buttonMap('right box|white')   = 'YES'; % YES
buttonMap('right box|red')  = 'NO'; % NO

% Define which buttons to listen to (example: right box colors)
selection_CatchQuestion = struct('right_box', {{'red', 'white'}});

% Audio setup
InitializePsychSound(1);
pahandle = PsychPortAudio('Open', [], 1, 1, 48000, 2); % playback device, freq 48000, 2 channels

%% Experiment constants (tweak if needed)
blankTime = 0.5; % inter-trial blank interval (seconds)
imageDur = 2.0;   % seconds to show each image
cuePlaySecs = 1.0; % seconds to play cue
audioTrimSecs = 1.5; % how long to trim object audio for playback
imgNums = [1, 3, 5, 7, 10];  % as in your code
imgWidth = 600; imgHeight = 600;
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
blockFiles = {
    'C:\Users\vpixx\PycharmProjects\neurowaves-lab-documentation\experiments\psychopy\Visual_Imagery_DM_YZ\Visual_Imagery_Matlab_MEG\VWM_B1_trials.csv'
    'C:\Users\vpixx\PycharmProjects\neurowaves-lab-documentation\experiments\psychopy\Visual_Imagery_DM_YZ\Visual_Imagery_Matlab_MEG\VWM_B2_trials.csv'
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
results = repmat(struct('Block',NaN, 'BlockRecallTime', '', 'TargetPrompt','','TargetObject','', 'TargetOrder', '', 'DistractObject', '', ...
    'Question_CorIMG', '', 'Question_Resp','','Question_RT',NaN), nTrialsTotal, 1);

HideCursor;
trialCounter = 1;

%% ------------------- Block loop -------------------
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

        %% Stage 2: Image perception
        % --- Choose target object and distractor object ---
        targetObj = strtrim(T.Object{tr});  % Target object name
        targetImgNum = 10;  % always imgNums(10)

        % Randomly pick distractor object offset (+/-10, 20, 30)
        offsetOptions = [10, 20, 30];

        valid = false;
        while ~valid
            offset = offsetOptions(randi(numel(offsetOptions)));

            % Randomly decide whether to add or subtract
            if rand < 0.5
                distractIdx = tr + offset;
            else
                distractIdx = tr - offset;
            end

            % Check validity
            if distractIdx >= 1 && distractIdx <= height(T)
                valid = true;
            end
        end

        distractObj = strtrim(T.Object{distractIdx});
        distractImgNum = 10;

        % --- Randomize order of presentation (target first or distractor first) ---
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
        
        % Load and show the image
        imgPath = fullfile('C:\Users\vpixx\PycharmProjects\neurowaves-lab-documentation\experiments\psychopy\Visual_Imagery_DM_YZ\imgs_diffusion\', ...
            [Obj1, num2str(10), '.jpg']);
        
        img1 = imread(imgPath);

        imgPath = fullfile('C:\Users\vpixx\PycharmProjects\neurowaves-lab-documentation\experiments\psychopy\Visual_Imagery_DM_YZ\imgs_diffusion\', ...
            [Obj2, num2str(10), '.jpg']);
        
        img2 = imread(imgPath);

        % present img1
        tex = Screen('MakeTexture', win, img1);
        Screen('DrawTexture', win, tex, [], ...
            CenterRectOnPoint([0 0 imgWidth imgHeight], screenX/2, screenY/2));
        
        % Flip and show
        % the next 4 lines is a whole process of turn on and turn off a trigger
        Screen('FillRect', win, trigImg1Start, trigRect); %% set trigger for img1 start
        Screen('Flip', win);
        
        % present img1 again after flip, we want it to stay, or the image just flash
        tex = Screen('MakeTexture', win, img1);
        Screen('DrawTexture', win, tex, [], ...
        CenterRectOnPoint([0 0 imgWidth imgHeight], screenX/2, screenY/2));
        
        Screen('FillRect', win, black_rgb, trigRect); % turn off trigger for img1 start
        Screen('Flip', win);

        WaitSecs(imageDur); % present img1

        Screen('FillRect', win, trigImg1End, trigRect); %% set trigger for img1 end
        Screen('Flip', win);
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
            CenterRectOnPoint([0 0 imgWidth imgHeight], screenX/2, screenY/2));
        
        % Flip and show
        Screen('FillRect', win, trigImg2Start, trigRect); %% set trigger for Img2 start
        Screen('Flip', win);

        % present img2 again after flip
        tex = Screen('MakeTexture', win, img2);
        Screen('DrawTexture', win, tex, [], ...
            CenterRectOnPoint([0 0 imgWidth imgHeight], screenX/2, screenY/2));

        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);

        WaitSecs(imageDur);

        Screen('FillRect', win, trigImg2End, trigRect); %% set trigger for Img2 end
        Screen('Flip', win);
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

        %  Stage 3: Cue Audio 
        % (If you have a special Cue file)
        try
            [cueWave, cueFs] = audioread(fullfile('C:\Users\vpixx\PycharmProjects\neurowaves-lab-documentation\experiments\psychopy\Visual_Imagery_DM_YZ\AuditoryPrompt\', 'Cue.mp3'));
            % Ensure cueWave is channels x samples for PsychPortAudio:
            PsychPortAudio('FillBuffer', pahandle, cueWave'); % audioread gives samples x ch
            PsychPortAudio('Start', pahandle, 1, 0, 1);
            WaitSecs(cuePlaySecs);
            PsychPortAudio('Stop', pahandle);
        catch ME
            % If cue file missing, continue but warn
            warning('Cue audio not played: %s', ME.message);
        end
    
        % Stage 4: Target Object Audio
        TargetObjPrompt = string(T.ObjectPrompt{tr}); 
        TargetObjName = string(T.Object{tr}); % ensure we use table row 'tr' 

        audioFile = fullfile('C:\Users\vpixx\PycharmProjects\neurowaves-lab-documentation\experiments\psychopy\Visual_Imagery_DM_YZ\AuditoryPrompt\', TargetObjName + ".mp3"); 
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

        Screen('FillRect', win, trigPromptStart, trigRect); %% set trigger for prompt start
        Screen('Flip', win);
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);
        PsychPortAudio('Start', pahandle, 1, 0, 1);   % start playback

        PsychPortAudio('Stop', pahandle, 1);          % wait until done
        Screen('FillRect', win, trigPromptEnd, trigRect); %% set trigger for prompt end
        Screen('Flip', win);
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);

        %% Stage 5: Memory period
        Screen('FillRect', win, white); 
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win); 
        
        WaitSecs(recall_time);
        
        Screen('FillRect', win, trigRecallEnd, trigRect); %% set trigger for recall end
        Screen('Flip', win);
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win); 

        %% Stage 6: Catch Question
        % present target object
        testImgNum = randsample([6 8 10], 1);

        targetImgPath = fullfile('C:\Users\vpixx\PycharmProjects\neurowaves-lab-documentation\experiments\psychopy\Visual_Imagery_DM_YZ\imgs_diffusion\', ...
            [targetObj, num2str(testImgNum), '.jpg']);

        tex = [];
        img = imread(targetImgPath);
        tex = Screen('MakeTexture', win, img);
        % Draw target image centered at top half of the screen
        Screen('DrawTexture', win, tex, [], ...
            CenterRectOnPoint([0 0 imgWidth imgHeight], screenX*0.5, screenY*0.5));

        question = 'Is this the image you just saw?';
        Screen('TextSize', win, 80); % set font size

        DrawFormattedText(win, question, 'center', screenY*0.2, black);
        optionText = 'YES                NO';
        DrawFormattedText(win, optionText, 'center', round(screenY*0.9), black);
        Screen('FillRect', win, black_rgb, trigRect); 
        CatchQuestion_Onset = Screen('Flip', win);

        catchAnswer = '';

        % set button for MEG controller (catch question)
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

%         %% set for keyboard resp of CatchQuestion
%         % Wait for key s/d/f
%         key_s = KbName('s');
%         key_d = KbName('d');
%         keyPressed = false;
%         while ~keyPressed
%             [~, ~, keyCode] = KbCheck;
%             if keyCode(escapeKey)
%                 Screen('CloseAll'); PsychPortAudio('Close', pahandle); error('Experiment terminated by user (ESC pressed).');
%             end
%             if keyCode(key_s)
%                 catchAnswer = 'YES';
%                 keyPressed = true;
%             elseif keyCode(key_d)
%                 catchAnswer = 'NO';
%                 keyPressed = true;
%             end
%             WaitSecs(0.001);
%         end

        Screen('FillRect', win, trigQuestionResp, trigRect); %% trigger for question resp
        Screen('Flip', win);
        %WaitSecs(0.005); % Short trigger pulse
        Screen('FillRect', win, black_rgb, trigRect); %% trigger for question resp
        Screen('Flip', win);

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

        trialCounter = trialCounter + 1;
    end

        % Optional: block break before next block
    if b < numel(T_blocks)
        breakMsg = sprintf('End of Block of %d\n\nYou can take a short break. When you are ready, start next block by pressing space.', b);
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

%% ------------------- Cleanup -------------------
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
filename = fullfile(beh_datafolder, sprintf('Visual_WorkingMemory_MEG_Official_Sub%s.csv', subNumStr));

% Save as CSV
writetable(resultsTable, filename);
fprintf('Results saved to %s\n', filename);