%% Psychtoolbox Visual Imagery Experiment (Practice)
clear; clc; close all;

% set VPIXX to DisablePixelMode
Datapixx('Open');
Datapixx('DisablePixelMode');
Datapixx('RegWr');
  
%% Setup screen 
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
defaultanswer1 = {'0', '', '', '', ''};
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
Screen('FillRect', win, black_rgb, trigRect);
Screen('Flip', win);
%-------------------------------------------
% VPIXX SETUP
%-------------------------------------------
Datapixx('Open');
Datapixx('EnablePixelMode');
Datapixx('RegWr');

%% set up buttons for MEG controller
% set button for rate
% Map from button ('box|color') to rating number
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
%         buttonMap('right box|green')    = 4;
%         buttonMap('right box|blue')  = 5;

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
imgNums = [1, 3, 5, 8, 50];  % as in your code
imgWidth = 380; 
imgHeight = 380;
imagine_time = 4; 
textYPos = round(screenY*0.8);    % rating text lower

%%  Instruction 
% Instruction = ['Welcome to the experiment! Each trial has 3 parts: imagining, rating and answering a question.' newline newline...
%     'You need to close eyes and press right white button to start a trial.' ...
%     'First, you will hear a "Ding", followed by a brief description of an object (e.g., "A red bus").' newline ...
%     'Your task is to vividly imagine the object in the middle of screen, as clearly and quickly as you can, against the white background. ' newline newline ...
%     'When you hear another "Ding", you need to stop imagination at once and open your eyes. You will see five reference images of the object will appear on the screen.' ...
%     'Then press buttons on left box to choose the image that best matches how clear your mental image felt.' ...
%     'Not the one that looks the most vivid or normal.' newline ...
%     'Left little finger = 1, left ring finger = 2, left middle finger = 3, left index finger = 4, left thumb = 5.' newline ...
%     'Please focus only on clarity. Use your first impression — there are no right or wrong answers, ' ...
%     'and no penalty if your mental image is not very clear.' newline newline ...
%     'Then you need to answer a simple YES/NO/DONT KNOW question about the object (e.g., "Is it food?").' ...
%     'Please respond by pressing right box:' newline ...
%     'Right index finger = YES, right middle finger = NO, Right ring finger = DONT KNOW (if you did not understand the object).' newline ...
%     'Each trial ends with a brief rest period showing only the white background.' newline newline ...
%     'Now you will have a short practice before the main experiment.' ...
%     'Please tell the experimenter if you understand everything.'];
% 
% Screen('TextSize', win, 40);  % Set font size (you can adjust this)
% DrawFormattedText(win, Instruction, 'center', 'center', black, 80);  % 70 = wrap at 70 chars per line
% Screen('FillRect', win, black_rgb, trigRect);
% Screen('Flip', win);
% KbStrokeWait;

% % Define first page of instructions
Instruction1 = ['Welcome to the experiment! Each trial has 3 parts: imagining, rating, and answering a question.' newline newline ...
    'You need to close your eyes and press the right white button to start a trial.' newline ...
    'First, you will hear a "Ding", followed by a brief description of an object (e.g., "A red bus").' newline ...
    'Your task is to close eyes and vividly imagine the object in the following 4 seconds, as clearly as you can.' newline newline ...
    'When you hear "Ding" again, you need to stop imagining at once and open your eyes.' newline newline ...
    'Please tell the experimenter when you understand above instructions.'];

% Define second page of instructions
Instruction2 = ['After imagination, you will then see five reference images of the object appear on the screen.' newline ...
    'Press the buttons on the left box to choose the image that best matches clarity of your mental image.' newline ...
    'Left little finger = 1, left ring finger = 2, left middle finger = 3, left index finger = 4, left thumb = 5.' newline ...
    'Please focus only on clarity. Use your first impression — there are no right or wrong answers.' newline newline...
    'Then you will answer a simple YES/NO/DONT KNOW question about the object (e.g., "Is it food?").' newline ...
    'Respond using the right box:' newline ...
    'Right index finger = YES, right middle finger = NO, right ring finger = DONT KNOW.' newline newline ...
    'Now you will have a short practice before the main experiment.' newline ...
    'Please tell the experimenter if you understand everything.'];

% ---- PAGE 1 ----
Screen('TextSize', win, 40);
DrawFormattedText(win, Instruction1, 'center', 'center', black, 80);
Screen('FillRect', win, black_rgb, trigRect);
Screen('Flip', win);
KbStrokeWait;


% ---- PAGE 2 ----
Screen('TextSize', win, 40);
DrawFormattedText(win, Instruction2, 'center', 'center', black, 80);
Screen('FillRect', win, black_rgb, trigRect);
Screen('Flip', win);
KbStrokeWait;


%% Persistent blank screen
Screen('FillRect', win, white);
Screen('FillRect', win, black_rgb, trigRect);
Screen('Flip', win);

% Load block file
blockFiles = {
    'VI_P_trials.csv'
};

% % Get folder where the current script is located
% scriptDir = fileparts(mfilename('fullpath'));
% 
% % Go one level up (parent folder)
% parentDir = fileparts(scriptDir);
% 
% % Point to AuditoryPrompt folder
% audioDir = fullfile(parentDir, 'AuditoryPrompt');
% imgDir = fullfile(parentDir, 'imgs_diffusion');

% Load Cue.mp3 from that folder


%% Assign one random imagine_time per block
nBlocks = numel(blockFiles);  
% block_imagine_times = imagine_times(randperm(nBlocks));

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

%% Block loop 
for b = 1:nBlocks
    T = T_blocks{b};
%     imagine_time = block_imagine_times(b);

    % Optional block start screen
    DrawFormattedText(win, sprintf(['Starting Practice Block.'...
    'Press any key to continue.'], ...
    b, nBlocks, imagine_time), 'center', 'center', black);

    Screen('FillRect', win, black_rgb, trigRect);
    Screen('Flip', win); 
    KbStrokeWait;

    trialOrder = randperm(height(T));

    %% Trial Loop
    for idx = 1:height(T)
        tr = trialOrder(idx);

        % Check ESC
        [keyIsDown, ~, keyCode] = KbCheck;
        if keyIsDown && keyCode(escapeKey)
            Screen('CloseAll'); PsychPortAudio('Close', pahandle); error('Experiment terminated by user.');
        end

        % Stage 1: Blank screen
        %         Screen('FillRect', win, white);
        %         Screen('FillRect', win, black_rgb, trigRect);
        %         Screen('Flip', win);
        %         WaitSecs(blankTime);

        Screen('TextSize', win, 40);
        DrawFormattedText(win, sprintf(['Please first close eyes, then press button under right thumb to start this trial.' newline newline ...
            'Keep eyes closed when imagining until hearing "Ding" again after the description.'], ...
            b, nBlocks), 'center', 'center', black);

        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);

        while true

            % Blocking call: waits until a valid button press is detected
            pair_CloseEyes = getButtonColor(selection_CloseEyes,true);  % blocking = true

            % Build key string
            key = sprintf('%s|%s', pair_CloseEyes{1}, pair_CloseEyes{2});

            % Map to resp to CatchQuestion
            if isKey(buttonMap, key)
                %                 catchAnswer = buttonMap(key);
                break;
            else
                % continue looping until a mapped button is pressed
            end
        end

        % Stage 2: Cue Audio
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
    
        % Stage 3: Random Object Audio
        objPrompt = string(T.ObjectPrompt{tr}); 
        objName = string(T.Object{tr}); % ensure we use table row 'tr' 

        audioFile = fullfile('C:\Users\vpixx\PycharmProjects\neurowaves-lab-documentation\experiments\psychopy\Visual_Imagery_DM_YZ\AuditoryPrompt', objName + ".mp3"); 
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

        Screen('FillRect', win, PromptStartTrig, trigRect);  %%%% set trigger for audio start
        Screen('Flip', win);
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);
        PsychPortAudio('Start', pahandle, 1, 0, 1);   % start audio


        PsychPortAudio('Stop', pahandle, 1);    % stop audio
        Screen('FillRect', win, PromptEndTrig, trigRect);  %%%% set trigger for audio stop
        Screen('Flip', win);
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);

        %% Stage 4: Imagination period
        Screen('FillRect', win, white); 
        %When changing the background color to anything, make sure the trigRect is staying black, so just before the flip add it to black again
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win); 
        WaitSecs(imagine_time);
        Screen('FillRect', win, ImagineEndTrig, trigRect); %%%% set trigger for prompt end
        Screen('Flip', win);
        Screen('FillRect', win, black_rgb, trigRect); 
        Screen('Flip', win); 

         % play cue again to let participants open eyes
        try
            [cueWave, cueFs] = audioread(fullfile('AuditoryPrompt', 'Cue.mp3'));
            % Ensure cueWave is channels x samples for PsychPortAudio:
            PsychPortAudio('FillBuffer', pahandle, cueWave'); % audioread gives samples x ch
            PsychPortAudio('Start', pahandle, 1, 0, 1);
            WaitSecs(cuePlaySecs);
            PsychPortAudio('Stop', pahandle);
        catch ME
            % If cue file missing, continue but warn
            warning('Cue audio not played: %s', ME.message);
        end

        %% Stage 5: Imagination Vividness Rating
        % Prepare images
        randObj = char(objName); % convert to char for file name concat
        imgTextures = zeros(1, numel(imgNums));
        xPos = linspace(screenX*0.1, screenX*0.9, numel(imgNums)) - imgWidth/2;
%         yPos = screenY*0.2;
        yPos = (screenY*0.5) - (imgHeight*0.5);

        for i = 1:numel(imgNums)
            imgPath = fullfile('C:\Users\vpixx\PycharmProjects\neurowaves-lab-documentation\experiments\psychopy\Visual_Imagery_DM_YZ\imgs_diffusion\', ...
                [randObj, num2str(imgNums(i)), '.jpg']);
            if exist(imgPath, 'file')
                img = imread(imgPath);
                imgTextures(i) = Screen('MakeTexture', win, img);
                Screen('DrawTexture', win, imgTextures(i), [], [xPos(i) yPos xPos(i)+imgWidth yPos+imgHeight]);
            else
                % If missing, draw a placeholder rectangle with the filename
                Screen('FillRect', win, [200 200 200], [xPos(i) yPos xPos(i)+imgWidth yPos+imgHeight]);
                DrawFormattedText(win, sprintf('Missing\n%s', imgPath), xPos(i), yPos, black);
            end
        end

        % set rate text
        Screen('TextSize', win, 80);
        DrawFormattedText(win, 'Please rate your imagination vividness', 'center', screenY*0.25, black);
        % Flip once to show images and record onset
        Screen('FillRect', win, black_rgb, trigRect);
        Rate_Onset = Screen('Flip', win);

        rating = NaN;

        while true
            % Blocking call: waits until a valid button press is detected
            pair_rate = getButtonColor(selection_rate,true);  % blocking = true

            % Build key string
            key = sprintf('%s|%s', pair_rate{1}, pair_rate{2});

            % Map to rating
            if isKey(buttonMap, key)
                rating = buttonMap(key);
                break;
            else
                % continue looping until a mapped button is pressed
            end
        end
        
%         %% set up keyboard for rating 
%         % Wait for numeric key 1-5
%         validKeys = [KbName('1!') KbName('2@') KbName('3#') KbName('4$') KbName('5%')];
%         keyPressed = false;
%         while ~keyPressed
%             [~, ~, keyCode] = KbCheck;
%             if keyCode(escapeKey)
%                 Screen('CloseAll'); PsychPortAudio('Close', pahandle); error('Experiment terminated by user (ESC pressed).');
%             end
%             for k = 1:length(validKeys)
%                 if keyCode(validKeys(k))
%                     rating = k;
%                     keyPressed = true;
%                     break;
%                 end
%             end
%             WaitSecs(0.001);
%         end
        Rate_Resptime = GetSecs();

        Screen('FillRect', win, RateRespTrig, trigRect); %%%% trigger for rate response
        Screen('Flip', win);
        WaitSecs(0.005); % Short trigger pulse
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);
    
        % Close image textures
        for i = 1:numel(imgTextures)
            if imgTextures(i) ~= 0
                Screen('Close', imgTextures(i));
            end
        end

        %% Stage 6: Catch Question
        question = T.CatchQuestion{tr};
        Screen('TextSize', win, 80); % set font size
        DrawFormattedText(win, question, 'center', screenY*0.25, black);
        optionText = 'YES        NO        DONT KNOW';
        DrawFormattedText(win, optionText, 'center', round(screenY*0.5), black);
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

%         %% set for keyboard for CatchQuestion
%         % Wait for key s/d/f
%         key_s = KbName('s');
%         key_d = KbName('d');
%         key_f = KbName('f');
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
%             elseif keyCode(key_f)
%                 catchAnswer = 'DON''T KNOW';
%                 keyPressed = true;
%             end
%             WaitSecs(0.001);
%         end
        CatchQuestion_Resptime = GetSecs();

        Screen('FillRect', win, QuestionRespTrig, trigRect); %% trigger for question resp
        Screen('Flip', win);
        WaitSecs(0.005); % Short trigger pulse
        Screen('FillRect', win, black_rgb, trigRect); %% trigger for question resp
        Screen('Flip', win);
    
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
        breakMsg = sprintf('End of Block of %d\n\nYou can have a short break. Let experimenter know when you are ready for next block.', b);
        DrawFormattedText(win, breakMsg, 'center', 'center', black);
        Screen('FillRect', win, black_rgb, trigRect);
        Screen('Flip', win);
        KbStrokeWait;
    end
end

%% Stage 7: End Page
DrawFormattedText(win, 'End. Please wait for experimenter for further action.', 'center', 'center', black);
Screen('FillRect', win, black_rgb, trigRect);
Screen('Flip', win);
KbWait([], 2);

% switch off trigger
Datapixx('DisablePixelMode'); 
Datapixx('RegWr');
Datapixx('Close');

%% Cleanup
PsychPortAudio('Close', pahandle);
Screen('CloseAll');

%% save results
% Convert results struct to table
resultsTable = struct2table(results);
subNumStr = answer1{1};  % e.g., '07'

% Create folder path
beh_datafolder = fullfile(pwd, 'Beh_Data')

% Build filename
filename = fullfile(beh_datafolder, sprintf('Visual_Imagery_MEG_Practice_Sub%s.csv', subNumStr));

% Save as CSV
writetable(resultsTable, filename);
fprintf('Results saved to %s\n', filename);