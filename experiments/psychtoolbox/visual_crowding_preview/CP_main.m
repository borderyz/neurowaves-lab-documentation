clearvars
%Screen('Preference', 'SkipSyncTests', 1);
%AssertOpenGL;


% Modes
use_vpixx = 1;
use_eyetracker = 1;
trigger_test = 1;
use_response_box = 1;
use_keyboard  = 0;

% Open vpix

if use_vpixx==1

    Datapixx('Open');

    Datapixx('DisablePixelMode');
    Datapixx('RegWr');

    Datapixx('SetPropixxDlpSequenceProgram', 0);
    Datapixx('RegWr');

end





% PARTICIPANT DATA
name1='Participant Data';
prompt1={'Subject Number', ...
    'Subject ID', ...
    'Sex (f/m)', ...
    'Age', ...
    'Task order'};
numlines1=1;
defaultanswer1={ '000', 'p', 'M', '0', '1'};
answer1=inputdlg(prompt1,name1,numlines1,defaultanswer1);
DEMO.num = str2double(answer1{1});
DEMO.ID  = answer1{2};
DEMO.sex = answer1{3};
DEMO.age = str2double(answer1{4});
DEMO.order = str2double(answer1{5});
DEMO.date = datetime;

% Edited by Tarek: timestamped log filename to avoid overwriting
% original:
%logFilename = sprintf('trigger_log_subject_%03d.txt', DEMO.num);
ts = datestr(now,'yyyymmdd_HHMMSS');
logFilename = sprintf('trigger_log_s%03d_%s.txt', DEMO.num, ts);


logFile = fopen(logFilename, 'w');
fprintf(logFile, 'Trial\tChannel\tCondition\tTime\tImageName\tConditionLabel\tMessage\n');

fixColor = [0 0 0]; % Fixation color (black)
fixColorCue = [0 128 0];
fixBadColor = [255 0 0]; % Fixation bad color (red)
fixRadius = 10;
black = [0 0 0];
fixTolerance = 100; % 75 pixels -> 2 dva
targetTolerance = 100;
%saccadeOffset = 305; % pixel -> 8 dva
saccadeOffset = 600; % pixel -> 10 dva
targetDuration = .5; % seconds



% Edited by Tarek: lower saccade threshold for sensitivity
% original:
%saccThreshold = 125; % pixel -> 2.5 dva (25% of 500) saccThreshold = round(0.25 * saccadeOffset);
% edited by Tarek:
saccThreshold = 10; % Michele usually uses 10


try

    PsychDebugWindowConfiguration(0, 1); % 1 for running exp; 0.5 for debugging
    PsychDefaultSetup(2);
    InitializePsychSound;
    % Screen setup
    s = max(Screen('Screens'));
    
    % Set the background color to white during window initialization
    [w, rect] = Screen('OpenWindow', s, [255 255 255]); %,[200 200 1000 1000]);
    Priority(MaxPriority(w));
    Screen('BlendFunction', w, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    pixelSizes = Screen('PixelSizes', s);
    fps = Screen('FrameRate', w);
    ifi = Screen('GetFlipInterval', w);
    [wx, wy] = RectCenter(rect);

    fixRect = CenterRectOnPoint([0, 0, fixRadius*2, fixRadius*2], wx, wy);


    if length([answer1{1} answer1{2}]) > 4
        error('EYELINK FILENAMES NEED TO BE LESS THAN 4 CHARACTERS LONG (2 subjectID, 2 subject number)')
    end

    % TRIGGERS SETUP
    trig.SYNCTIME = 0;
    trig.START = 1;
    trig.PREVIEW = 2;
    trig.SACCADE = 3;
    trig.TARGET = 4;
    trig.RESPONSE = 5;
    disp('setup trigger done');

    %added by tarek
    % ------ codes to send to EyeLink (must be scalars) ------
    etCode.SYNC     = 100;  % any numbers you like, just keep them unique
    etCode.START    = 101;
    etCode.PREVIEW  = 102;
    etCode.SACCADE  = 103;
    etCode.TARGET   = 104;
    etCode.RESPONSE = 105;
    
    etCode.CH225    = 225;  % match the MEG channel number if you want
    etCode.CH226    = 226;
    etCode.CH227    = 227;
    etCode.CH228    = 228;
    etCode.CH229    = 229;
    etCode.CH230    = 230;
    etCode.CH231    = 231;


    if use_eyetracker==1

        % EYE-TRACKING SETUP
        el = EyelinkInitDefaults(w);
        
        el.backgroundcolour = 255;
        el.foregroundcolour = 0;
        el.calibrationtargetcolour = [0 0 0];
        el.msgfontcolour = 0;
        EyelinkUpdateDefaults(el);
        disp('eyelink test 1');
        if ~EyelinkInit() % 1 means enable dummy mode
            fprintf('Eyelink Init aborted.\n');
            Eyelink('Shutdown');
            Screen('CloseAll');
        end
        disp('Eyelink calibration starting');
        xOffset = 0;
        Eyelink('command', 'screen_pixel_coords = %ld %ld %ld %ld', xOffset, 0, (rect(3)-1)-xOffset, rect(4)-1); %comment out to last working version
%         disp(rect(3),rect(4));
        % Link to edf data
        Eyelink('command', 'file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'); WaitSecs(0.05);
        Eyelink('command', 'file_sample_data  = LEFT,RIGHT,GAZE,HREF,AREA,GAZERES,STATUS,INPUT,HTARGET'); WaitSecs(0.05);

        % Link data to Matlab
        Eyelink('command', 'link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,FIXUPDATE,INPUT'); WaitSecs(0.05);
        Eyelink('command', 'link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT,HTARGET'); WaitSecs(0.05);
        Eyelink('command', 'link_event_data = GAZE,GAZERES,HREF,AREA,VELOCITY'); WaitSecs(0.05);

        edfFile = ['Subj' answer1{1} '.edf'];
        Eyelink('Openfile', edfFile);
        

        %% added automatic calibration
        
        Eyelink('Command', 'calibration_type = HV6');
        Eyelink('Command', 'enable_automatic_calibration = YES');



%         Eyelink('Command', 'enable_automatic_calibration = NO');
%         calX = [420, 640, 860];
%         calY = [540 540 540]; %[0, 0, 0];  % all at center height
%         
%         Eyelink('command', sprintf('calibration_targets = %.2f,%.2f %.2f,%.2f %.2f,%.2f', ...
%             calX(1), calY(1), ...
%             calX(2), calY(2), ...
%             calX(3), calY(3)));
%         
%         Eyelink('command', sprintf('validation_targets = %.2f,%.2f %.2f,%.2f %.2f,%.2f', ...
%             calX(1), calY(1), ...
%             calX(2), calY(2), ...
%             calX(3), calY(3)));
%         
        WaitSecs(0.05);


        % Before recording, we place reference graphics on the host display
        % Must be offline to draw to EyeLink screen
       
        Eyelink('Command', 'set_idle_mode'); WaitSecs(0.05);

        EyelinkDoTrackerSetup(el); WaitSecs(0.05);

    end



    % Top left pixel that controls triggers in PixelMode
    if trigger_test == 1
        trigRect = [0 0 1 1];
        %centeredRect_trigger = CenterRectOnPointd(trigRect, 0.5, 0.5);
    elseif trigger_test == 0
        trigRect = [0 0 100 100]; % To debug
        %centeredRect_trigger = CenterRectOnPointd(trigRect, 25, 25);
    end


    Screen('FillRect', w, black, trigRect);
    Screen('Flip', w);

    if use_vpixx==1
        Datapixx('EnablePixelMode');  % to use topleft pixel to code trigger information, see https://vpixx.com/vocal/pixelmode/
        Datapixx('RegWr');
    end

    % KEYBOARD SETUP
    responseKeys = {'c', 'v', 'a', 'y', 'n', 'return'}; % eyelink commands
    KbName('UnifyKeyNames');
    KbCheckList = [KbName('space'), KbName('ESCAPE'), KbName('leftarrow'), KbName('rightarrow')];
    for i = 1:length(responseKeys)
        KbCheckList = [KbName(responseKeys{i}), KbCheckList];
    end
    RestrictKeysForKbCheck(KbCheckList);
    ListenChar(-1)

    % Define trigger pixels for all usable MEG channels
    trig.ch224 = [4  0  0]; %224 meg channel
    trig.ch225 = [16  0  0];  %225 meg channel
    trig.ch226 = [64 0 0]; % 226 meg channel
    trig.ch227 = [0  1 0]; % 227 meg channel
    trig.ch228 = [0  4 0]; % 228 meg channel
    trig.ch229 = [0 16 0]; % 229 meg channel
    trig.ch230 = [0 64 0]; % 230 meg channel
    trig.ch231 = [0 0  1]; % 231 meg channel


    counts.ch224 = 0;
    counts.ch225 = 0;
    counts.ch226 = 0;
    counts.ch227 = 0;
    counts.ch228 = 0;
    counts.ch229 = 0;
    counts.ch230 = 0;
    counts.ch231 = 0;


    % Clear the screen with the background color (white)
    Screen('FillRect', w, [255 255 255]);
    Screen('FillRect', w, black, trigRect);
    Screen('Flip', w);


stim_set = 'stimuli_images';

    stim_dir = dir(fullfile(stim_set, '*.jpg'));
    stim_fn = {stim_dir.name};

    quest_dir_fn = 'Probe_images';
    quest_dir = dir(fullfile(quest_dir_fn, '*.jpg'));
    quest_fn = {quest_dir.name};
    quest_fn = quest_fn(randperm(length(quest_fn)));

    CP_table;

    fprintf(logFile, 'N/A\t224\tStart Experiment\t%f\tN/A\tN/A\tTriggering start of experiment\n', GetSecs());

    % START EXPERIMENT
    text = {
        'You will see a fixation point in the middle of the screen. Please keep your eyes fixated on it.'
        'Keep your eyes fixated on the point until it turns green.'
        'When the point turns green, look at the word either to the left or right of the fixation point.'
        'You will be prompted to answer the question "Is this the same word you last saw?"'
        'You can answer with the yellow button for "YES" or the red button for "NO".'
        'NOTE: The word will appear before the fixation point turns green. Please do not look at the word before the point turns to green.'
        ''
        'PRESS SPACE TO START'
        };

    yPos = wy - 200;

    for i = 1:length(text)
        Screen('DrawText', w, text{i},  wx - 600, yPos, [0 0 0]);
        yPos = yPos + 50;
    end
    Screen('FillRect', w, black, trigRect);
    Screen('Flip', w);
    KbWait([], 2)

    % Trigger 1
    counts.ch224 = counts.ch224+1;
    Screen('FillRect', w, trig.ch224, trigRect);
    Screen('Flip', w);
    Screen('FillRect', w, black, trigRect);
    Screen('Flip', w);

    if use_eyetracker==1
        Eyelink('Command', 'SetOfflineMode');
        Eyelink('StartRecording');
        expStartSecs = GetSecs(); %put by tarek
        Screen('FillOval', w, fixColor, fixRect);
        Screen('FillRect', w, black, trigRect);
        Screen('Flip', w);
        WaitSecs(2);
        trig.SYNCTIMEsecs = GetSecs();
%         changed by tarek
%         Eyelink('Message', 'TRIGGER %d', trig.SYNCTIMEsecs);
%         eyeUsed = Eyelink('EyeAvailable');
%         eyeUsed = eyeUsed + 1;
        timestamp_ms = round( (trig.SYNCTIMEsecs - expStartSecs) * 1000 );
        Eyelink('Message', 'TRIGGER %d', timestamp_ms);
    
        eyeUsed = Eyelink('EyeAvailable') + 1;

    end

    goodTrial = 1;
    nBadTrials = 0;
    i_trial = 1;
    numTrials = size(expTable, 1);
    questIdx = 1;

    %Question: What is this validTrialsIndex?
    validTrialsIndex = true(size(expTable,1), 1);


    while i_trial <= size(expTable, 1)
        disp(['Starting trial ', num2str(i_trial), ' of ', num2str(size(expTable, 1))]);
        fprintf(logFile, '%d\tN/A\tN/A\t%f\tN/A\tN/A\tStarting trial\n', i_trial, GetSecs());

        % PAUSE
        if mod(i_trial, round(size(expTable, 1)/3+1)) == 0
            Screen('DrawText', w, 'WELL DONE, TAKE A BREAK !',  wx-400, wy, [0 0 0]);
            %Screen('FillRect', w, black, trigRect);
            % Correction
            Screen('FillRect', w, black, trigRect);
            Screen('Flip', w);
            KbWait([], 2)

        end

        conn = expTable.connection(i_trial);
        cwdg = expTable.crowding(i_trial);
        imgIdx = expTable.imageIndex(i_trial);

        % preview_fn = sprintf('SET1_conn_%d_cwdg_%d_%d.jpg', conn, cwdg, imgIdx);

        preview_fn = sprintf('Img_%03d_con%d_crwd%d.jpg', imgIdx, conn, cwdg);


        imageFilePath = fullfile(stim_set, preview_fn);

        if ~isfile(imageFilePath)
            % Question: the following line doesn't do anything
            validTrialsIndex(i_trial) = false;
            i_trial = i_trial + 1;
            continue;
        end

        previewMatrix = imread(fullfile(stim_set, preview_fn));
        previewTexture = Screen('MakeTexture', w, previewMatrix);


        % === TARGET IMAGE: Clean version from corresponding folder ===
        target_fn = sprintf('Img_%03d_con%d_crwd0.jpg', imgIdx, conn);
        clean_folder = fullfile('stimuli_images', ['clean_crwd' num2str(cwdg)]);
        target_path = fullfile(clean_folder, target_fn);

        if ~isfile(target_path)
            warning('Clean target image not found: %s', target_path);
            validTrialsIndex(i_trial) = false; % Optional: mark trial invalid
            i_trial = i_trial + 1;
            continue;
        end
        disp(['Preview: ' fullfile('stimuli_imageJPG', preview_fn)]);
        disp(['Target:  ' target_path]);


        targetMatrix = imread(target_path);
        targetTexture = Screen('MakeTexture', w, targetMatrix);

        if isempty(previewMatrix)
            warning('Preview image loaded as empty.');
        end
        if isempty(targetMatrix)
            warning('Target image loaded as empty.');
        end


        % Trial settings for question/response
        question_fn = ['img_' num2str(i_trial) '.jpg'];
        % questRect = CenterRectOnPoint([0 0 size(previewMatrix, 1)*2 size(previewMatrix, 2)], wx , wy);

%         if expTable.preview(i_trial) == 0
%             previewTexture = Screen('MakeTexture', w, fliplr(previewMatrix));
%         end
        expTable.imageFn{i_trial} = preview_fn;

        if expTable.questionType(i_trial) == 0
            questionTexture = targetTexture;

        else
            if questIdx <= length(quest_fn)
                selectedTexture = quest_fn{questIdx};
                selectedTextureMatrix = imread(fullfile(quest_dir_fn, selectedTexture));
                questionTexture = Screen('MakeTexture', w, selectedTextureMatrix);
                questIdx = questIdx + 1;
            end
        end

        % OFFSCREEN

        wFixation = Screen('OpenOffscreenWindow', w, 255);
        % fixRect = CenterRectOnPoint([0, 0, fixRadius*2, fixRadius*2], wx, wy);
        Screen('FillOval', wFixation, black, fixRect);

        wPreview = Screen('OpenOffscreenWindow', w, 255);
        previewRect = CenterRectOnPoint([0 0 size(previewMatrix, 2) size(previewMatrix, 1)], wx+ saccadeOffset*expTable.side(i_trial), wy);
        Screen('FillOval', wPreview, black, fixRect);
        Screen('DrawTexture', wPreview, previewTexture, [], previewRect);

        wCue = Screen('OpenOffscreenWindow', w, 255);
        cueRect = CenterRectOnPoint([0 0 size(previewMatrix, 2) size(previewMatrix, 1)], wx+ saccadeOffset*expTable.side(i_trial), wy);
        Screen('FillOval', wCue, fixColorCue, fixRect);
        Screen('DrawTexture', wCue, previewTexture, [], cueRect);

        wTarget = Screen('OpenOffscreenWindow', w, 255);
        Screen('FillOval', wTarget, fixColorCue, fixRect);
        Screen('DrawTexture', wTarget, targetTexture, [], previewRect);

        wQuestion = Screen('OpenOffscreenWindow', w, 255);
        questRect = CenterRectOnPoint([0 0 size(previewMatrix, 2) size(previewMatrix, 1)], wx, wy);
        Screen('DrawTexture', wQuestion, questionTexture, [], questRect);
        Screen('DrawText', wQuestion, 'no', wx - 305, wy + 150, black);
        Screen('DrawText', wQuestion, 'yes', wx + 305, wy + 150, black);


        if i_trial <= size(expTable, 1)
            imageName = expTable.imageFn{i_trial};  % Get the image name for this trial

            % Extract the condition label from the image name
            conditionPattern = 'crwd(\d+)';  % Regex pattern to match 'cwdg_X'
            conditionMatch = regexp(imageName, conditionPattern, 'tokens');
            if ~isempty(conditionMatch)
                conditionLabel = conditionMatch{1}{1};  % Extract the condition number (e.g., '3')
            else
                conditionLabel = 'Unknown';  % In case the condition can't be determined
            end

        else
            imageName = 'N/A';  % No image available (indicating an extra trigger)
            conditionLabel = 'N/A';  % No condition for extra triggers
        end

        % FIXATION
        goodTrial = 1;
        errorMsg = 'BAD TRIAL';

        % counts.ch225 = counts.ch225+1;
        % Screen('DrawTexture', w, wFixation);
        % Screen('FillRect', w, trig.ch225, trigRect);
        % Screen('Flip', w);
        Screen('DrawTexture', w, wFixation);
        Screen('FillRect', w, black, trigRect);
        Screen('Flip', w);

        fixOnsetTime = GetSecs();
        expTable.fixStartTime(i_trial) = GetSecs();
        if use_eyetracker==1
            Eyelink('Message', 'TRIGGER %d', etCode.START)
        end

        expTable.fixDuration(i_trial) = (1000+randperm(500,1))/1000; % random fixation duration
        eyeX = nan; eyeY = nan;
        disp('DEBUG 3')
        while goodTrial
            [~,~, keyCode] = KbCheck();
            if keyCode(KbName('escape'))
                endExperiment(logFile, DEMO, expTable, trig, stim_fn, answer1, true)
                ShowCursor()
                RestrictKeysForKbCheck([]);
                Screen(w,'Close');
                sca;
                ListenChar(0)
                return;
            end


            if use_eyetracker==1

                if Eyelink('NewFloatSampleAvailable')
                    eyeSample = Eyelink('NewestFloatSample');
                    eyeX = eyeSample.gx(eyeUsed);
                    eyeY = eyeSample.gy(eyeUsed);

                    if eyeX~=el.MISSING_DATA && eyeY~=el.MISSING_DATA % no blinks
                        dist_center = sqrt( (eyeX-wx)^2 + (eyeY-wy)^2 );
                        if dist_center < fixTolerance % fixation is good
                            if GetSecs() - expTable.fixStartTime(i_trial) > expTable.fixDuration(i_trial) % fixation is long enough


                                % TRIGGER ONLY HERE, ON GOOD FIXATION
                                counts.ch225 = counts.ch225 + 1;
                                Screen('FillRect', w, trig.ch225, trigRect);
                                Screen('Flip', w);
                                WaitSecs(0.01);
                                Screen('FillRect', w, black, trigRect);
                                Screen('Flip', w);

                                expTable.realFixConfirmTime(i_trial) = GetSecs();

                                if use_eyetracker == 1
                                    Eyelink('Message', 'TRIGGER %d', etCode.CH225);
                                end

                                break;
                            end
                        else
                            for i=1:3
                                Screen('FillRect', w, fixBadColor, fixRect);
                                Screen('FillRect', w, black, trigRect);

                                Screen('Flip', w);
                                WaitSecs(.1);
                                Screen('FillRect', w, black, trigRect);

                                Screen('Flip', w);
                                WaitSecs(.1);
                            end

                            Screen('DrawTexture', w, wFixation);
                            Screen('FillRect', w, black, trigRect);
                            Screen('Flip', w);

                            expTable.fixStartTime(i_trial) = GetSecs();

                            if use_eyetracker == 1
                                Eyelink('Message', 'TRIGGER %d', etCode.START)

                            end

                        end
                    else % blink
                        expTable.fixStartTime(i_trial) = GetSecs();
                        % Question: Does this line display something on
                        % the screen?
                        Eyelink('Message', 'TRIGGER %d', etCode.START)

                    end
                end
            else

                % If no eyetracker, wait for the fixation duration and proceed
                if GetSecs() - fixOnsetTime > expTable.fixDuration(i_trial)
                    break; % Exit fixation loop automatically
                end
            end
        end


        % PREVIEW AND CUE

        % Determine the condition-based MEG trigger channel
        if strcmp(conditionLabel, '1')
            currentTriggerChannel = trig.ch226;  % Condition 1 -> Channel 226
        elseif strcmp(conditionLabel, '2')
            currentTriggerChannel = trig.ch227;  % Condition 2 -> Channel 227
        elseif strcmp(conditionLabel, '3')
            currentTriggerChannel = trig.ch228;  % Condition 3 -> Channel 228
        elseif strcmp(conditionLabel, '4')
            currentTriggerChannel = trig.ch229;  % Condition 4 (flipped) -> Channel 229
        end


        % Trigger for preview image
        Screen('DrawTexture', w, wPreview);
        if strcmp(imageName, 'N/A')
            fprintf(logFile, '%d\t%d\tPreview Image\t%f\t%s\t%s\tExtra trigger - no image\n', i_trial, currentTriggerChannel, GetSecs(), imageName, conditionLabel);
        else
            fprintf(logFile, '%d\t%d\tPreview Image\t%f\t%s\t%s\tTriggering preview image\n', i_trial, currentTriggerChannel, GetSecs(), imageName, conditionLabel);
        end
        Screen('FillRect', w, currentTriggerChannel, trigRect);
        Screen('Flip', w);

        if isequal(currentTriggerChannel, trig.ch226)
            counts.ch226 = counts.ch226 + 1;
        elseif isequal(currentTriggerChannel, trig.ch227)
            counts.ch227 = counts.ch227 + 1;
        elseif isequal(currentTriggerChannel, trig.ch228)
            counts.ch228 = counts.ch228 + 1;
        elseif isequal(currentTriggerChannel, trig.ch229)
            counts.ch229 = counts.ch229 + 1;
        end

        if use_eyetracker
            switch conditionLabel
                case '1', chCode = etCode.CH226;   % map crowding-1 to code 226
                case '2', chCode = etCode.CH227;   % crowding-2  -> 227
                case '3', chCode = etCode.CH228;   % crowding-3  -> 228
                case '4', chCode = etCode.CH229;   % flipped-4   -> 229
                otherwise, chCode = etCode.PREVIEW;
            end
            Eyelink('Message', 'TRIGGER %d', chCode);
        end
        Screen('DrawTexture', w, wPreview);
        Screen('FillRect', w, black, trigRect);
        Screen('Flip', w);

        expTable.previewOnsetTime(i_trial) = GetSecs();

        if use_eyetracker==1
            Eyelink('Message', 'TRIGGER %d', etCode.PREVIEW);
        end

        saccTrigger = 0;

        while goodTrial % Cue
            [~,~, keyCode] = KbCheck();
            if keyCode(KbName('escape'))
                endExperiment(logFile, DEMO, expTable, trig, stim_fn, answer1, true)
                ShowCursor()
                RestrictKeysForKbCheck([]);
                Screen(w,'Close');
                sca;
                ListenChar(0)
                return;
            end

            if use_eyetracker==1
                if Eyelink('NewFloatSampleAvailable')
                    eyeSample = Eyelink('NewestFloatSample');
                    eyeX = eyeSample.gx(eyeUsed);
                    eyeY = eyeSample.gy(eyeUsed);
                    disp(['EyeX: ', num2str(eyeX)]);

                    if eyeX~=el.MISSING_DATA && eyeY~=el.MISSING_DATA % no blinks
                        dist_center = sqrt( (eyeX-wx)^2 + (eyeY-wy)^2 );
                        if dist_center < fixTolerance % fixation is good
                            if GetSecs() - expTable.fixStartTime(i_trial) > expTable.fixDuration(i_trial)+.5 % fixation is long enough
                                if strcmp(imageName, 'N/A')
                                    fprintf(logFile, '%d\tN/A\tCue\t%f\t%s\t%s\tExtra trigger - no image\n', i_trial, GetSecs(), imageName, conditionLabel);
                                else
                                    fprintf(logFile, '%d\tN/A\tCue\t%f\t%s\t%s\tTriggering preview image\n', i_trial, GetSecs(), imageName, conditionLabel);
                                end

                                % counts.ch229 = counts.ch229+1;
                                % Screen('DrawTexture', w, wCue);
                                % Screen('FillRect', w, trig.ch230, trigRect);
                                % Screen('Flip', w);
                                Screen('DrawTexture', w, wCue);
                                Screen('FillRect', w, black, trigRect);
                                Screen('Flip', w);
                                break;
                            end
                            %                     else
                            %                         goodTrial = 0;
                        end
                        %                 else % blink
                        %                     goodTrial = 0;
                    end
                end

            else
                if GetSecs() - expTable.fixStartTime(i_trial) > expTable.fixDuration(i_trial) + 0.5 % simulate fixation time
                    if strcmp(imageName, 'N/A')
                        fprintf(logFile, '%d\tN/A\tCue\t%f\t%s\t%s\tExtra trigger - no image\n', i_trial, GetSecs(), imageName, conditionLabel);
                    else
                        fprintf(logFile, '%d\tN/A\tCue\t%f\t%s\t%s\tTriggering preview image\n', i_trial, GetSecs(), imageName, conditionLabel);
                    end

                    % % counts.ch229 = counts.ch229 + 1;
                    % Screen('DrawTexture', w, wCue);
                    % Screen('FillRect', w, trig.ch230, trigRect);
                    % Screen('Flip', w);
                    Screen('DrawTexture', w, wCue);
                    Screen('FillRect', w, black, trigRect);
                    Screen('Flip', w);
                    WaitSecs(0.3)
                    break;
                end
            end
        end


        disp('DEBUG 4')

        if use_eyetracker==1 % Saccade 
            while goodTrial
                % detect saccadeOnset with threshold
                if Eyelink('NewFloatSampleAvailable')
                    eyeSample = Eyelink('NewestFloatSample');
                    newEyeX = eyeSample.gx(eyeUsed);
                    disp(['newEyeX: ', num2str(newEyeX)]); % Debugging output


                    % Edited by Tarek: added a condition to check if the side is on the right side
                    if abs(newEyeX - eyeX) > saccThreshold && sign(newEyeX - eyeX) == expTable.side(i_trial) % if neeyeX > over the imaginary boundary
                        saccTrigger = saccTrigger + 1;
                        if saccTrigger > 1
                            expTable.saccadeOnsetTime(i_trial) = GetSecs();
                            disp('Saccade detected'); % Debugging output

                            Eyelink('Message', 'TRIGGER %d', etCode.SACCADE);

                            if strcmp(imageName, 'N/A')
                                fprintf(logFile, '%d\tN/A\tSaccade\t%f\t%s\t%s\tExtra trigger - no image\n', i_trial, GetSecs(), imageName, conditionLabel);
                            else
                                fprintf(logFile, '%d\tN/A\tSaccade\t%f\t%s\t%s\tTriggering preview image\n', i_trial, GetSecs(), imageName, conditionLabel);
                            end
                            Screen('FillRect', w, black, trigRect);
                            Screen('Flip', w);
                            Screen('FillRect', w, black, trigRect);
                            Screen('Flip', w);
                            break;
                        end
                    else
                        disp('Saccade not detected');
                        saccTrigger=0;
                    end
                    eyeX = newEyeX;
                end
            end
        else
            % Simulate saccade detection and proceed
            disp('Simulating saccade detection (no eyetracker).');

            % Instead of break, use a flag or condition to exit goodTrial loop
            goodTrial = 0; % Exit the goodTrial loop

        end

        % TARGET
        disp('DEBUG 5')
        Screen('DrawTexture', w, wTarget);
        if strcmp(imageName, 'N/A')
            fprintf(logFile, '%d\t230\tTarget Image\t%f\t%s\t%s\tExtra trigger - no image\n', i_trial, GetSecs(), imageName, conditionLabel);
        else
            fprintf(logFile, '%d\t230\tTarget Image\t%f\t%s\t%s\tTriggering preview image\n', i_trial, GetSecs(), imageName, conditionLabel);
        end
        Screen('FillRect', w, trig.ch230, trigRect);
        Screen('Flip', w);
        Screen('DrawTexture', w, wTarget);
        Screen('FillRect', w, black, trigRect);
        Screen('Flip', w);

        if use_keyboard == 1
        WaitSecs(.1)
        end

        % Set trigger back to black

        expTable.targetOnsetTime(i_trial) = GetSecs();
        if use_eyetracker==1
            Eyelink('Message', 'TRIGGER %d', etCode.TARGET);
        end

        while GetSecs() - expTable.targetOnsetTime(i_trial) < targetDuration
            [~, ~, keyCode] = KbCheck();
            if keyCode(KbName('escape'))
                endExperiment(logFile, DEMO, expTable, trig, stim_fn, answer1, true)
                ShowCursor()
                RestrictKeysForKbCheck([]);
                Screen(w,'Close');
                sca;
                ListenChar(0)
                return; 
            elseif use_eyetracker==1
                if Eyelink('NewFloatSampleAvailable')
                    eyeSample = Eyelink('NewestFloatSample');
                    eyeX = eyeSample.gx(eyeUsed);
                    eyeY = eyeSample.gy(eyeUsed);

                    if eyeX~=el.MISSING_DATA && eyeY~=el.MISSING_DATA % if there are no blinks
                        % dist_target = sqrt( (eyeX- (wx+saccadeOffset*expTable.side(i_trial)) )^2 + (eyeY-wy)^2 );
                        dist_target = eyeX - (wx+saccadeOffset*expTable.side(i_trial));
                        %                     disp(['dist_target: ', num2str(dist_target)]);
                        if dist_target < fixTolerance % and the saccade landed inside the word
                            if GetSecs() - expTable.targetOnsetTime(i_trial) > targetDuration % and they fixated the word long enough
                                break;
                            end
                            %                     else
                            %                         errorMsg = 'BAD SACCADE';
                            %                         goodTrial = 0;
                        end
                        %                 else % blink
                        %                     errorMsg = 'BAD BLINK';
                        %                     goodTrial = 0;
                    end
                end
            end
        end

        Screen('FillRect', w, [255 255 255]);
        Screen('FillRect', w, black, trigRect);
        Screen('Flip', w);
        WaitSecs(1);   %wait time between response and target


        % RESPONSE
        disp('DEBUG 6')
        Screen('DrawTexture', w, wQuestion);
        if strcmp(imageName, 'N/A')
            fprintf(logFile, '%d\t231\tQuestion Onset\t%f\t%s\t%s\tExtra trigger - no image\n', i_trial, GetSecs(), imageName, conditionLabel);
        else
            fprintf(logFile, '%d\t231\tQuestion Onset\t%f\t%s\t%s\tTriggering preview image\n', i_trial, GetSecs(), imageName, conditionLabel);
        end
        Screen('FillRect', w, trig.ch231, trigRect);
        Screen('Flip', w);
        Screen('DrawTexture', w, wQuestion);
        Screen('FillRect', w, black, trigRect);
        Screen('Flip', w);



        expTable.questionOnsetTime(i_trial) = GetSecs();
        % expTable.responseOnsetTime(i_trial) = GetSecs();

        while true  % Keep looping until a valid response is detected

            % Handle escape key to exit experiment
            [~, secs, keyCode] = KbCheck();
            if keyCode(KbName('escape'))
                endExperiment(logFile, DEMO, expTable, trig, stim_fn, answer1, true)
                
                ShowCursor();
                RestrictKeysForKbCheck([]);
                Screen('CloseAll');
                sca;
                ListenChar(0);
                return;  % Exit the script
            end

            if use_response_box == 1
                % Actual experiment: wait for participant's response via the response box
                [response, ResponseTime] = getButton();  % Function to capture MEG button press
                if response == 8 || response == 9  % Valid responses (8 = yes, 9 = no)
                    % Log the response
                    expTable.response(i_trial) = response;
                    expTable.responseOnsetTime(i_trial) = ResponseTime;

                    % Check correctness
                    if (targetTexture == questionTexture && response == 8) || ...
                            (targetTexture ~= questionTexture && response == 9)
                        expTable.correctness(i_trial) = 1;  % Correct response
                    else
                        expTable.correctness(i_trial) = 0;  % Incorrect response
                    end

                    % Log the response in the log file edited by tarek
                    fprintf(logFile, '%d\tEndTrial\tN/A\t%f\t%s\t%s\tEnding trial\n', ...
                        i_trial, GetSecs(), imageName, conditionLabel);

                    break;  % Exit the loop after logging the response
                end

            elseif use_keyboard == 1
                % Wait for keyboard response if not using the response box and not simulating
                [keyIsDown, secs, keyCode] = KbCheck();
                if keyIsDown
                    % Check for valid key presses ('y' for yes and 'n' for no)
                    if keyCode(KbName('y'))
                        responseKey = 'y';
                    elseif keyCode(KbName('n'))
                        responseKey = 'n';
                    else
                        responseKey = [];  % Invalid key pressed, do nothing
                    end

                    % Only log if a valid response was detected
                    if ~isempty(responseKey) % && (responseKey == 1 || responseKey == 0)
                        ResponseTime = secs - expTable.questionOnsetTime(i_trial);

                        % Log the response
                        expTable.response(i_trial) = responseKey;
                        expTable.responseOnsetTime(i_trial) = ResponseTime;

                        % Check correctness
                        if (targetTexture == questionTexture && responseKey == 'y') || ...
                                (targetTexture ~= questionTexture && responseKey == 'n')
                            expTable.correctness(i_trial) = 1;
                        else
                            expTable.correctness(i_trial) = 0;
                        end

                        % Log the response in the log file
                        fprintf(logFile, '%d\tEndTrial\tN/A\t%f\t%s\t%s\tEnding trial\n', ...
                            i_trial, GetSecs(), 'imageName', 'conditionLabel');

                        break;  % Exit the loop after logging the response
                    end
                end

            else
                % Debug phase: automatically simulate a response
                response = 8;  % Simulate "yes" response (you can alternate if needed)
                ResponseTime = GetSecs() - expTable.questionOnsetTime(i_trial);

                % Log the simulated response
                expTable.response(i_trial) = response;
                expTable.responseOnsetTime(i_trial) = ResponseTime;

                % Simulate correctness (you can randomize this if needed)
                expTable.correctness(i_trial) = randi([0, 1]);  % Randomly assign correct/incorrect

                % Log the simulated response in the log file
                fprintf(logFile, '%d\tSimulatedEndTrial\tN/A\t%f\t%s\t%s\tSimulated trial\n', ...
                    i_trial, GetSecs(), 'imageName', 'conditionLabel');

                break;  % Exit the loop after simulating the response
            end

            % Optionally, add a short delay to avoid hogging the CPU
            WaitSecs(0.001);
        end


        % Display a white screen for 1 second as a pause
        Screen('FillRect', w, [255 255 255]); % White screen
        Screen('FillRect', w, black, trigRect); % Trigger rectangle
        Screen('Flip', w);
        WaitSecs(1);

        % Edited By tarek to stop overwhelming the VRam
        Screen('Close', wFixation);
        Screen('Close', wPreview);
        Screen('Close', wCue);
        Screen('Close', wTarget);
        Screen('Close', wQuestion);
        Screen('Close', previewTexture);
%         Screen('Close', targetTexture);
%         Screen('Close', questionTexture);

        % Move to the next trial after the response loop
        i_trial = i_trial + 1;
        disp(['Moving to trial ', num2str(i_trial)]);

    end


    Screen('DrawText', w, 'Congrats! You are done.',  wx-400, wy, [0 0 0]);
    Screen('FillRect', w, black, trigRect);
    Screen('Flip', w);
    WaitSecs(5);

    expTable = expTable(validTrialsIndex, :);

    disp('--- Trigger Count Summary ---');
    disp(counts);

    endExperiment(logFile, DEMO, expTable, trig, stim_fn, answer1, false)


    % if use_vpixx==1
    %     Datapixx('DisablePixelMode');
    %     Datapixx('RegWr');
    %     Datapixx('Close');
    % end

    if use_eyetracker==1
        % SAVE EYE DATA
        Eyelink('StopRecording');
        Eyelink('CloseFile');
        Eyelink('ReceiveFile');
        Eyelink('ShutDown');
    end

    if use_vpixx==1
        Datapixx('DisablePixelMode');
        Datapixx('RegWr');
        Datapixx('Close');
    end


    % Commented out by tarek to remove the replication
    % if use_vpixx==1

    %     Datapixx('DisablePixelMode');
    %     Datapixx('RegWr');
    %     Datapixx('Close');

    % end

    % FINISH EXPERIMENT
    ShowCursor();
    RestrictKeysForKbCheck([]);
    Screen('CloseAll');
    sca;
    ListenChar(0);


catch
    % FINISH EXPERIMENT
endExperiment(logFile, DEMO, expTable, trig, stim_fn, answer1, true)
ShowCursor();
    RestrictKeysForKbCheck([]);
    Screen('CloseAll');
    sca;
    ListenChar(0);
    rethrow(lasterror);
end

fclose(logFile);