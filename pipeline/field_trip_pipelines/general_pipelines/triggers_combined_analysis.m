% Written: Adapted from Gayathri Satheesh, 24 October 2024, gayathri.s.satheesh@gmail.com

% Description:
% Extract time of stimulus presentation and noise patches in the face and scene working memory
% task in FWMM project at NYUAD (Face Working Memory MEG).

% The WM Task experiment was coded with the 8 trigger channels (224 -231)
% in 35 unique combination of three channels each
%
% Trigger information: KIT channel indexing starts with 0 while MATLAB indexing starts with 1, so ch224 on KIT is ch225 in MATLAB

% import trigger channels (225-232 in [1-256])
%% extract timing and event information from meg triggers

% Match stimulus identity between MEG trigger channels and phychtoolbox
% outputs

% % pending to make a function
% % ---- Stimulus onset triggers ----
% start of run = trigger_229 + trigger_230;

% % ---- Stimulus onset triggers ----
% trigger_stimulus_WM_face   = trigger_224 + trigger_225 + trigger_226; % WM Face stimulus onset
% trigger_stimulus_WM_scene  = trigger_224 + trigger_225 + trigger_227; % WM Scene stimulus onset
% trigger_stimulus_ANT_face  = trigger_224 + trigger_225 + trigger_228; % ANT Face stimulus onset
% trigger_stimulus_ANT_scene = trigger_224 + trigger_225 + trigger_229; % ANT Scene stimulus onset
% trigger_stimulus_ANT_none  = trigger_224 + trigger_225 + trigger_230; % ANT None stimulus onset
%
% % ---- Delay onset triggers ----
% trigger_delay_WM_face   = trigger_224 + trigger_226 + trigger_227; % WM Face delay onset
% trigger_delay_WM_scene  = trigger_224 + trigger_226 + trigger_228; % WM Scene delay onset
% trigger_delay_ANT_face  = trigger_224 + trigger_226 + trigger_229; % ANT Face delay onset
% trigger_delay_ANT_scene = trigger_224 + trigger_226 + trigger_230; % ANT Scene delay onset
% trigger_delay_ANT_none  = trigger_224 + trigger_226 + trigger_231; % ANT None delay onset
%
% % ---- Probe 1 triggers ----
% trigger_probe1_WM_face   = trigger_224 + trigger_227 + trigger_228; % WM Face probe 1
% trigger_probe1_WM_scene  = trigger_224 + trigger_227 + trigger_229; % WM Scene probe 1
% trigger_probe1_ANT_face  = trigger_224 + trigger_227 + trigger_230; % ANT Face probe 1
% trigger_probe1_ANT_scene = trigger_224 + trigger_227 + trigger_231; % ANT Scene probe 1
% trigger_probe1_ANT_none  = trigger_224 + trigger_228 + trigger_229; % ANT None probe 1
%
% % ---- Probe 2 triggers ----
% trigger_probe2_WM_face   = trigger_224 + trigger_228 + trigger_230; % WM Face probe 2
% trigger_probe2_WM_scene  = trigger_224 + trigger_228 + trigger_231; % WM Scene probe 2
% trigger_probe2_ANT_face  = trigger_224 + trigger_229 + trigger_230; % ANT Face probe 2
% trigger_probe2_ANT_scene = trigger_224 + trigger_229 + trigger_231; % ANT Scene probe 2
% trigger_probe2_ANT_none  = trigger_224 + trigger_230 + trigger_231; % ANT None probe 2
%
% % ---- Probe 3 triggers ----
% trigger_probe3_WM_face   = trigger_225 + trigger_226 + trigger_227; % WM Face probe 3
% trigger_probe3_WM_scene  = trigger_225 + trigger_226 + trigger_228; % WM Scene probe 3
% trigger_probe3_ANT_face  = trigger_225 + trigger_226 + trigger_229; % ANT Face probe 3
% trigger_probe3_ANT_scene = trigger_225 + trigger_226 + trigger_230; % ANT Scene probe 3
% trigger_probe3_ANT_none  = trigger_225 + trigger_226 + trigger_231; % ANT None probe 3
%
% % ---- Report onset triggers ----
% trigger_report_WM_face   = trigger_225 + trigger_227 + trigger_228; % WM Face report onset
% trigger_report_WM_scene  = trigger_225 + trigger_227 + trigger_229; % WM Scene report onset
% trigger_report_ANT_face  = trigger_225 + trigger_227 + trigger_230; % ANT Face report onset
% trigger_report_ANT_scene = trigger_225 + trigger_227 + trigger_231; % ANT Scene report onset
% trigger_report_ANT_none  = trigger_225 + trigger_228 + trigger_229; % ANT None report onset
%
% % ---- Report made triggers ----
% trigger_reportmade_WM_face   = trigger_225 + trigger_228 + trigger_230; % WM Face report made
% trigger_reportmade_WM_scene  = trigger_225 + trigger_228 + trigger_231; % WM Scene report made
% trigger_reportmade_ANT_face  = trigger_225 + trigger_229 + trigger_230; % ANT Face report made
% trigger_reportmade_ANT_scene = trigger_225 + trigger_229 + trigger_231; % ANT Scene report made
% trigger_reportmade_ANT_none  = trigger_225 + trigger_230 + trigger_231; % ANT None report made


%% Visualise data



BOX_DIR = getenv('MEG_DATA');

confile = fullfile([BOX_DIR,'mandarin-language-study\sub-test\meg-kit\sub-test_mandarin-language-study_trigger-test-20250115.con']); 

%confile = fullfile([BOX_DIR,'empty-room\sub-emptyroom\meg-kit\emptyroom_11.con']); 


% load in the data
cfg              = [];
cfg.dataset      = confile;
cfg.coilaccuracy = 0;
data_all         = ft_preprocessing(cfg);


% 
cfg = [];
cfg.viewmode = 'vertical';
cfg.blocksize = 300; % seconds
ft_databrowser(cfg, data_all);





%% settings



%----------------------- Setup FieldTrip Defaults --------------------------
%restore default MATLAB path
% restoredefaultpath

%Add path to FieldTrip directory
%fieldTrip_path='/Users/gs2750/fieldtrip-20240110';
%addpath('/Users/GayathriSatheesh/softwares/fieldtrip-20211208')
%addpath (fieldTrip_path);

%setup the minimal required path settings
ft_defaults

%---------------------------------------------------------------------------


% Set path to KIT .con file
dataset = 'C:\Users\hz3752\Box\MEG\Data\mandarin-language-study\sub-test\meg-kit';


% path
% path = '/Volumes/Pegasus32R8/studies/GERE/preprocessing_tutorial/data/MEG';
path = '/Volumes/Pegasus32R8/data/FWMM';
path_preprocessing = [path '/results/preprocessing/triggers'];
path_behavior = [path '/data/behavior'];


% MEG channels [0-255]
% 0-207: Axial gradiometers (MEG helmet sensors)
% 208-223: Magnetometers (reference sensors used for noise reduction)
% 224-231: Triggers
% 232: Audio
% 233: Photodiode
% 234-238: Marker coils
% 239-255: Not used

blocks = 1; % for trigger test its only 1

for block_i = 1%:blocks % will not be differentiaed by runs but rate=her two blocks each of 10 runs

    %%

    disp(['Triggers: WM task - block ' num2str(block_i)]);

    % data
    [~,meg_con] = system(['ls ' dataset]); %it has both WM and JDG block

    %[~,meg_con] = system(['ls ' path '/' subject_ID '/sess_0' num2str(session) '/GERE_' subjectID '_sess' num2str(session) '*2023_0' num2str(block_i+1) '.con']);
    meg_con = meg_con(1:(end-1));

    % if MEG input file does exist
    if ~strcmp(meg_con(1:2), 'ls')
        trim_from=[];

            % import trigger channels (225-232 in [1-256])
            triggers_data = ft_read_data(meg_con, 'chanindx', 225:232);

            % custom time point for trigger extraction - incase the
            % data started post some time
            if ~isempty(trim_from)
                triggers_data = triggers_data(:, trim_from:end);
            end

            %% unique triggers

            %trigger activation threshold
            threshold_triggers = 2;

            number_triggers = 8;

            trigger_224 = []; % Total events with trigger_224=96(WM)+88(JDG)=184events
            trigger_225 = [];
            trigger_226 = [];
            trigger_227 = [];
            trigger_228 = [];
            trigger_229 = [];
            trigger_230 = [];
            trigger_231 = [];

            % Gaya notes: for each trigger channel find the times when the
            % trigger activation is larger than the threshold
            for trig_i = 1:number_triggers

                tmp = find(triggers_data(trig_i,:) > threshold_triggers);
                tmp_unique = [];

                %Sicen the triggers are activated as a block - find
                %the unqiue times
                for time_i = 1:length(tmp)

                    if time_i == 1 % if its the first instance of impulse count that as unique trigger time

                        tmp_unique = tmp(time_i);

                    else

                        if tmp(time_i) ~= tmp(time_i-1)+1 % if there is no activation in the millisecond before current instance that means its a unique event - so count the trigger

                            tmp_unique = [tmp_unique tmp(time_i)];

                        end

                    end

                end

                if trig_i == 1
                    trigger_224 = tmp_unique;
                elseif trig_i == 2
                    trigger_225 = tmp_unique;
                elseif trig_i == 3
                    trigger_226 = tmp_unique;
                elseif trig_i == 4
                    trigger_227 = tmp_unique;
                elseif trig_i == 5
                    trigger_228 = tmp_unique;
                elseif trig_i == 6
                    trigger_229 = tmp_unique;
                elseif trig_i == 7
                    trigger_230 = tmp_unique;
                elseif trig_i == 8
                    trigger_231 = tmp_unique;
                end
            end



            %% exceptions

            % TO DO: modeling trials with no response hence no
            % respone made

            %% extract time of trial events

            % TO DO : Have a check to make sure no of triggers match what you expect disp('WARNING: number of triggers do not match!');

            %                     % structure to store times
            %                     triggers_trial_events = [];
            %                     triggers_trial_events.info = {'data field = Colums: onsets of stimulus (1), delay (2), noise probe 1 (3), noise probe 2 (4), noise porbe 3 (5), report oset (6), report made (7); Rows: trials';...
            %                                                   'stimuli field = Columns: sequence location; Rows: trials'};
            %                     triggers_trial_events.data = nan(size(trigger_229, 2), 5);
            %                     triggers_trial_events.stimuli = zeros(size(trigger_229, 2), 4);
            %
            %                     triggers_trial_events.data(:, 1) = trigger_229;
            %                     triggers_trial_events.data(:, 3) = trigger_230;
            %                     triggers_trial_events.data(:, 4) = trigger_231(1:2:size(trigger_231, 2));
            %                     triggers_trial_events.data(:, 5) = trigger_231(2:2:size(trigger_231, 2));
            %
            %% unique stimulus trigger for start of experiment
            % experiment start (229 + 230, not 224, not 225)
            id = ismember(trigger_229, trigger_230);
            tmp = trigger_229(id);
            id = ismember(tmp, trigger_224);
            experimentStart = tmp(~id);
            id = ismember(experimentStart, trigger_225);
            triggers_trial_events.expStart = experimentStart(~id);


            %% unique stimulus triggers after onset of first trial

            % merge several triggers apart less than 'threshold_timepoits' (ms), since they are
            % triggering the same event

            threshold_timepoints = 50; % ms of difference between two triggers (assumed to be the same)

            %look at triggers only after the start of the
            %experiment - TO DO: How to incorporate multiple trials
            %into this
            trigger_224 = trigger_224(trigger_224 > triggers_trial_events.expStart(1));
            trigger_225 = trigger_225(trigger_225 > triggers_trial_events.expStart(1));
            trigger_226 = trigger_226(trigger_226 > triggers_trial_events.expStart(1));
            trigger_227 = trigger_227(trigger_227 > triggers_trial_events.expStart(1));
            trigger_228 = trigger_228(trigger_228 > triggers_trial_events.expStart(1));
            trigger_229 = trigger_229(trigger_229 > triggers_trial_events.expStart(1));
            trigger_230 = trigger_230(trigger_230 > triggers_trial_events.expStart(1));
            trigger_231 = trigger_231(trigger_231 > triggers_trial_events.expStart(1));

            % merge all triggers
            triggers_all = sort(unique([...
                trigger_224 trigger_225...
                trigger_226 trigger_227...
                trigger_228 trigger_229...
                trigger_230 trigger_231]));


            % matrix with trigger timepoints to correct: time
            % points at which mutliple triggers are acrivted within
            % 50ms window indicating the triggering of same event
            % and account for slight delays in trigger activation
            contiguous_triggers = [];

            for trig_i = 2:length(triggers_all)

                if abs(triggers_all(trig_i) - triggers_all(trig_i-1)) < threshold_timepoints% if the difference between any two triggers is less than 50 ms

                    if isempty(contiguous_triggers)
                        contiguous_triggers(1, 1) = triggers_all(trig_i-1);
                        contiguous_triggers(1, 2) = triggers_all(trig_i);
                    else
                        contiguous_triggers(end+1, 1) = triggers_all(trig_i-1);
                        contiguous_triggers(end, 2) = triggers_all(trig_i);
                    end

                end

            end

            if ~isempty(contiguous_triggers)

                for trig_i = 1:8

                    if trig_i == 1
                        trigger = trigger_224;
                    elseif trig_i == 2
                        trigger = trigger_225;
                    elseif trig_i == 3
                        trigger = trigger_226;
                    elseif trig_i == 4
                        trigger = trigger_227;
                    elseif trig_i == 5
                        trigger = trigger_228;
                    elseif trig_i == 6
                        trigger = trigger_229;
                    elseif trig_i == 7
                        trigger = trigger_230;
                    elseif trig_i == 8
                        trigger = trigger_231;
                    end

                    for trig_ii = 1:length(trigger)

                        for trig_iii = flip(1:size(contiguous_triggers, 1))

                            %if any of the triggers are activated
                            %within 50ms of another one - replace
                            %the time stamp with the earliest one

                            if trigger(trig_ii) == contiguous_triggers(trig_iii, 2)

                                trigger(trig_ii) = contiguous_triggers(trig_iii, 1);

                            end

                        end

                    end

                    if trig_i == 1
                        trigger_224 = trigger;
                    elseif trig_i == 2
                        trigger_225 = trigger;
                    elseif trig_i == 3
                        trigger_226 = trigger;
                    elseif trig_i == 4
                        trigger_227 = trigger;
                    elseif trig_i == 5
                        trigger_228 = trigger;
                    elseif trig_i == 6
                        trigger_229 = trigger;
                    elseif trig_i == 7
                        trigger_230 = trigger;
                    elseif trig_i == 8
                        trigger_231 = trigger;
                    end

                end

            end

            %% stimulus triggers

            %% ---- Stimulus onset triggers ----

            %All combinations start with trigger_224 and trigger_225
            id = ismember(trigger_224, trigger_225);
            tmp = trigger_224(id);

            % WM Face stimulus onset (trigger_224 + trigger_225 + trigger_226)
            id2 = ismember(tmp, trigger_226);
            trigger_stimulus_WM_face = tmp(id2);

            % WM Scene stimulus onset (trigger_224 + trigger_225 + trigger_227)
            id2 = ismember(tmp, trigger_227);
            trigger_stimulus_WM_scene = tmp(id2);

            % ANT Face stimulus onset (trigger_224 + trigger_225 + trigger_228)
            id2 = ismember(tmp, trigger_228);
            trigger_stimulus_ANT_face = tmp(id2);

            % ANT Scene stimulus onset (trigger_224 + trigger_225 + trigger_229)
            id2 = ismember(tmp, trigger_229);
            trigger_stimulus_ANT_scene = tmp(id2);

            % ANT None stimulus onset (trigger_224 + trigger_225 + trigger_230)
            id2 = ismember(tmp, trigger_230);
            trigger_stimulus_ANT_none = tmp(id2);


            %% ---- Delay onset triggers ----

            % WM Face delay onset (trigger_224 + trigger_226 + trigger_227)
            id = ismember(trigger_224, trigger_226);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_227);
            trigger_delay_WM_face = tmp(id);

            % WM Scene delay onset (trigger_224 + trigger_226 + trigger_228)
            id = ismember(trigger_224, trigger_226);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_228);
            trigger_delay_WM_scene = tmp(id);

            % ANT Face delay onset (trigger_224 + trigger_226 + trigger_229)
            id = ismember(trigger_224, trigger_226);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_229);
            trigger_delay_ANT_face = tmp(id);

            % ANT Scene delay onset (trigger_224 + trigger_226 + trigger_230)
            id = ismember(trigger_224, trigger_226);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_230);
            trigger_delay_ANT_scene = tmp(id);

            % ANT None delay onset (trigger_224 + trigger_226 + trigger_231)
            id = ismember(trigger_224, trigger_226);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_231);
            trigger_delay_ANT_none = tmp(id);


            %% ---- Probe 1 triggers ----

            % WM Face probe 1 (trigger_224 + trigger_227 + trigger_228)
            id = ismember(trigger_224, trigger_227);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_228);
            trigger_probe1_WM_face = tmp(id);

            % WM Scene probe 1 (trigger_224 + trigger_227 + trigger_229)
            id = ismember(trigger_224, trigger_227);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_229);
            trigger_probe1_WM_scene = tmp(id);

            % ANT Face probe 1 (trigger_224 + trigger_227 + trigger_230)
            id = ismember(trigger_224, trigger_227);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_230);
            trigger_probe1_ANT_face = tmp(id);

            % ANT Scene probe 1 (trigger_224 + trigger_227 + trigger_231)
            id = ismember(trigger_224, trigger_227);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_231);
            trigger_probe1_ANT_scene = tmp(id);

            % ANT None probe 1 (trigger_224 + trigger_228 + trigger_229)
            id = ismember(trigger_224, trigger_228);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_229);
            trigger_probe1_ANT_none = tmp(id);


            %% ---- Probe 2 triggers ----

            % WM Face probe 2 (trigger_224 + trigger_228 + trigger_230)
            id = ismember(trigger_224, trigger_228);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_230);
            trigger_probe2_WM_face = tmp(id);

            % WM Scene probe 2 (trigger_224 + trigger_228 + trigger_231)
            id = ismember(trigger_224, trigger_228);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_231);
            trigger_probe2_WM_scene = tmp(id);

            % ANT Face probe 2 (trigger_224 + trigger_229 + trigger_230)
            id = ismember(trigger_224, trigger_229);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_230);
            trigger_probe2_ANT_face = tmp(id);

            % ANT Scene probe 2 (trigger_224 + trigger_229 + trigger_231)
            id = ismember(trigger_224, trigger_229);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_231);
            trigger_probe2_ANT_scene = tmp(id);

            % ANT None probe 2 (trigger_224 + trigger_230 + trigger_231)
            id = ismember(trigger_224, trigger_230);
            tmp = trigger_224(id);
            id = ismember(tmp, trigger_231);
            trigger_probe2_ANT_none = tmp(id);


            %% ---- Probe 3 triggers ----

            % WM Face probe 3 (trigger_225 + trigger_226 + trigger_227)
            id = ismember(trigger_225, trigger_226);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_227);
            trigger_probe3_WM_face = tmp(id);

            % WM Scene probe 3 (trigger_225 + trigger_226 + trigger_228)
            id = ismember(trigger_225, trigger_226);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_228);
            trigger_probe3_WM_scene = tmp(id);

            % ANT Face probe 3 (trigger_225 + trigger_226 + trigger_229)
            id = ismember(trigger_225, trigger_226);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_229);
            trigger_probe3_ANT_face = tmp(id);

            % ANT Scene probe 3 (trigger_225 + trigger_226 + trigger_230)
            id = ismember(trigger_225, trigger_226);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_230);
            trigger_probe3_ANT_scene = tmp(id);

            % ANT None probe 3 (trigger_225 + trigger_226 + trigger_231)
            id = ismember(trigger_225, trigger_226);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_231);
            trigger_probe3_ANT_none = tmp(id);


            %% ---- Report onset triggers ----

            % WM Face report onset (trigger_225 + trigger_227 + trigger_228)
            id = ismember(trigger_225, trigger_227);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_228);
            trigger_report_WM_face = tmp(id);

            % WM Scene report onset (trigger_225 + trigger_227 + trigger_229)
            id = ismember(trigger_225, trigger_227);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_229);
            trigger_report_WM_scene = tmp(id);

            % ANT Face report onset (trigger_225 + trigger_227 + trigger_230)
            id = ismember(trigger_225, trigger_227);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_230);
            trigger_report_ANT_face = tmp(id);

            % ANT Scene report onset (trigger_225 + trigger_227 + trigger_231)
            id = ismember(trigger_225, trigger_227);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_231);
            trigger_report_ANT_scene = tmp(id);

            % ANT None report onset (trigger_225 + trigger_228 + trigger_229)
            id = ismember(trigger_225, trigger_228);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_229);
            trigger_report_ANT_none = tmp(id);


            %% ---- Report made triggers ----

            % WM Face report made (trigger_225 + trigger_228 + trigger_230)
            id = ismember(trigger_225, trigger_228);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_230);
            trigger_reportmade_WM_face = tmp(id);

            % WM Scene report made (trigger_225 + trigger_228 + trigger_231)
            id = ismember(trigger_225, trigger_228);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_231);
            trigger_reportmade_WM_scene = tmp(id);

            % ANT Face report made (trigger_225 + trigger_229 + trigger_230)
            id = ismember(trigger_225, trigger_229);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_230);
            trigger_reportmade_ANT_face = tmp(id);

            % ANT Face report made (trigger_225 + trigger_229 + trigger_231)
            id = ismember(trigger_225, trigger_229);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_231);
            trigger_reportmade_ANT_scene = tmp(id);

            % ANT None report made (trigger_225 + trigger_230 + trigger_231)
            id = ismember(trigger_225, trigger_230);
            tmp = trigger_225(id);
            id = ismember(tmp, trigger_231);
            trigger_reportmade_ANT_none = tmp(id);

            %%

            alltrig = [trigger_location_1 trigger_location_2...
                trigger_location_3 trigger_location_4...
                trigger_location_5 trigger_location_6...
                trigger_location_7 trigger_location_8];

            loc_1 = ones(1, length(trigger_location_1));
            loc_2 = ones(1, length(trigger_location_2)) * 2;
            loc_3 = ones(1, length(trigger_location_3)) * 3;
            loc_4 = ones(1, length(trigger_location_4)) * 4;
            loc_5 = ones(1, length(trigger_location_5)) * 5;
            loc_6 = ones(1, length(trigger_location_6)) * 6;
            loc_7 = ones(1, length(trigger_location_7)) * 7;
            loc_8 = ones(1, length(trigger_location_8)) * 8;
            loc_all = [loc_1 loc_2 loc_3 loc_4 loc_5 loc_6 loc_7 loc_8];

            alltrig_locations = [alltrig; loc_all];

            [temp, order] = sort(alltrig_locations(1,:));
            alltrig_locations = alltrig_locations(:,order);

            % stimulus onset and stimulus identity
            for trial_i = 1:size(triggers_trial_events.data, 1)

                % onset
                trig_stim = alltrig(alltrig > triggers_trial_events.data(trial_i, 1));
                trig_stim = trig_stim(trig_stim < triggers_trial_events.data(trial_i, 3));
                trig_stim = sort(trig_stim);

                % stimulus identity
                id = find(alltrig_locations(1,:) > triggers_trial_events.data(trial_i, 1));
                trial_locations = alltrig_locations(:,id);

                id = find(trial_locations(1,:) < triggers_trial_events.data(trial_i, 3));
                trial_locations = trial_locations(:,id);

                if length(trial_locations(2,:)) == 3
                    trial_locations = [trial_locations(2,:) 0];
                else
                    trial_locations = trial_locations(2,:);
                end

                %% exception - introduce by hand triggers not recorded
                if subject == 6
                    if session == 1
                        if block_i == 2
                            if trial_i == 16
                                trial_locations = [4 1 2 0];
                                trig_stim = [trig_stim(1)-400 trig_stim];
                            end
                        end
                    end
                end

                %% end of exceptions

                triggers_trial_events.data(trial_i, 2) = trig_stim(1);
                triggers_trial_events.stimuli(trial_i, :) = trial_locations;

            end

            % exception (no meg data for the last trial)
            if subject == 25
                if session == 2
                    if block_i == 2
                        triggers_trial_events.data = triggers_trial_events.data(1:69,:);
                        triggers_trial_events.stimuli = triggers_trial_events.stimuli(1:69,:);
                    end
                end
            end

            % save timings
            save([path_preprocessing '/' subject_ID '/sess_0' num2str(session)...
                '/triggers_task_block' num2str(block_i) '.mat'], 'triggers_trial_events');



        %% match stimulus identity between ptb outputs and meg trigger channels

        % load
        load([path_behavior '/' subject_ID '/sess_0' num2str(session) '/block_0' num2str(block_i) '/task_trial_presentation.mat']); % sequences

        %% exceptions

        % block finishes beforehand because Vpixx response button
        % not working
        if subject == 15
            if session == 1
                if block_i == 3
                    sequences = sequences(1:68,:);

                end
            end
        end

        % triggers of last trial not registered
        if subject == 20
            if session == 2
                if block_i == 1
                    sequences = sequences(1:69,:);

                end
            end
        end

        % meg data of last trial not registered
        if subject == 25
            if session == 2
                if block_i == 2
                    sequences = sequences(1:69,:);
                end
            end
        end

        % match
        if sum(sequences - triggers_trial_events.stimuli) == 0
            disp('Match between meg triggers and ptb outputs'); disp(' ');

        else

            disp(['WARNING: Missmatch between meg triggers and ptb outputs in '...
                num2str(sum(sum(sequences - triggers_trial_events.stimuli)))]);
            disp(' ');

        end

    else

        disp('No MEG data');

    end

end


% function timingDifference=triggerTimingDifference(trialTypes,windowTypes)
% end