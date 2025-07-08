clear;
clc;

%% Define paths for MEG .con files
filename1 = 'egyptian_sub004_session1.con';  % Update with actual filenames
filename2 = 'egyptian_sub004_session2.con';  

% Read headers, data, and events
hdr1 = ft_read_header(filename1);
dat1 = ft_read_data(filename1);
evt1 = ft_read_event(filename1);

hdr2 = ft_read_header(filename2);
dat2 = ft_read_data(filename2);
evt2 = ft_read_event(filename2);

% Ensure consistency in sampling rate and channels
if hdr1.Fs ~= hdr2.Fs
    error('Mismatch in sampling frequency between the two .con files!');
end
if size(dat1,1) ~= size(dat2,1)
    error('Mismatch in number of channels between the two .con files!');
end

% Get number of samples in the first dataset
nsamples1 = size(dat1, 2);

% Concatenate the data (time dimension)
dat = cat(2, dat1, dat2);

% Adjust event sample indices for the second file
for i = 1:length(evt2)
    evt2(i).sample = evt2(i).sample + nsamples1;
end

% Merge events
evt = cat(1, evt1, evt2);

% Use the first header as the reference
hdr = hdr1;
hdr.nSamples = hdr1.nSamples + hdr2.nSamples;

% Save the merged dataset
merged_filename = 'merged_egyptian_sub004.vhdr';
ft_write_data(merged_filename, dat, 'header', hdr, 'event', evt);

disp(['Merged file saved as: ', merged_filename]);

%% Define paths for trigger analysis
BOX_DIR = getenv('MEG_DATA');
confile = merged_filename;
csv_file_experiment = fullfile(['word_count_egyptian_list4_sub004.csv']);

%% Load data from the merged .con file
cfg              = [];
cfg.dataset      = confile;
cfg.coilaccuracy = 0;
cfg.channel      = {'225','226','227','228','229','230','231','232'};  % Trigger channels
dataTrigger      = ft_preprocessing(cfg);

%% Plot data (optional)
cfg = [];
cfg.viewmode  = 'vertical';
cfg.blocksize = 300;  % seconds
ft_databrowser(cfg, dataTrigger);

%% STEP 1: Convert the 8 binary channels into a single code per sample
% Threshold at 0.5 (adjust if your signals differ)
binary_data = dataTrigger.trial{1} > 0.5;   % 8 x N logical matrix

% Assign bit weights. If channel "225" is the least significant bit:
%bitWeights = 2.^(0:7)';  % [1; 2; 4; 8; 16; 32; 64; 128]
bitWeights = flip(2.^(0:7))';
% Multiply each row (bit) by its bit weight and sum across rows
triggerCodePerSample_raw = bitWeights' * binary_data;  % 1 x N row vector

% (If wiring is reversed, flip bitWeights or reorder bits accordingly.)
% bitWeights = 2.^(7:-1:0)';

%% STEP 2: Strategy 1 - Debounce via "Stability Count"
% We will create a "stableCodes" array by requiring a code to remain
% unchanged for minStableWin consecutive samples before we accept it.

minStableWin = 5;  % number of consecutive samples to confirm stability
N = length(triggerCodePerSample_raw);

stableCodes = zeros(1, N);          % holds the "debounced" code
currentCode = triggerCodePerSample_raw(1);
stableCodes(1) = currentCode;
countStable = 1;

for i = 2:N
    if triggerCodePerSample_raw(i) == currentCode
        % same code → increase stability count
        countStable = countStable + 1;
    else
        % code changed
        if countStable < minStableWin
            % Not stable long enough → revert the last 'countStable' samples to 0
            % (You could also revert to the "old" code or do another approach.)
            for backIdx = (i - countStable):(i - 1)
                stableCodes(backIdx) = 0;
            end
        end
        
        % Update to the new code
        currentCode = triggerCodePerSample_raw(i);
        countStable = 1;
    end
    
    stableCodes(i) = currentCode;
end



%% Count number of transitions

% Example array

% Find transitions (where the number changes)
transitions = diff(stableCodes) ~= 0;

% Identify the unique sequences
sequenceValues = stableCodes([true, transitions]);

% Exclude zero sequences
sequenceValues = sequenceValues(sequenceValues ~= 0);

% Count the non-zero sequences
numSequences = numel(sequenceValues);

% Display the result
disp(['Number of non-zero sequences: ', num2str(numSequences)]);


%% STEP 3: Detect trigger onsets by looking at code changes (using stableCodes)
diffCode  = [0, diff(stableCodes)];
changeIdx = find(diffCode ~= 0);

% Trigger codes at those change points
onsetCodes = stableCodes(changeIdx);

% Times (seconds) for each trigger onset
onsetTimes = changeIdx / dataTrigger.fsample;

sequence_codes = onsetCodes(onsetCodes ~= 0); % Remove zeros

%% STEP 4: (Optional) Build a FieldTrip-like event structure
clear event;
event_idx = 1;  % Initialize an index for valid events
for i = 1:length(onsetCodes)
    if onsetCodes(i) ~= 0
        event(event_idx).type      = 'trigger';
        event(event_idx).value     = onsetCodes(i);
        event(event_idx).sample    = changeIdx(i);
        event(event_idx).timestamp = changeIdx(i);
        event(event_idx).offset    = 0;
        event(event_idx).duration  = 1;  
        event(event_idx).time      = onsetTimes(i);
        
        event_idx = event_idx + 1;  % Increment the index for the next valid event
    else
        disp('The value is zero');
    end
end


%% STEP 5: Compare observed trigger counts to an expected matrix (from CSV)

% Suppose you have a matrix describing [code, expectedCount]
expectedMatrix = compute_matrix_words(csv_file_experiment);

% Tally occurrences for each trigger code
triggerCodes = onsetCodes(:);
uniqueCodes  = unique(triggerCodes);
counts       = arrayfun(@(c) sum(triggerCodes == c), uniqueCodes);

% Display observed counts in a table
observedTable = table(uniqueCodes, counts, ...
                      'VariableNames', {'TriggerCode','ObservedCount'});
disp('----------------------------------');
disp('Observed counts of each trigger code (after stabilization):');
disp(observedTable);
disp('----------------------------------');

% Check each expected code
for i = 1:size(expectedMatrix,1)
    thisCode   = expectedMatrix(i,1);
    thisExpect = expectedMatrix(i,2);
    
    idxObserved = find(uniqueCodes == thisCode);
    if isempty(idxObserved)
        actualCount = 0;  % code never observed
    else
        actualCount = counts(idxObserved);
    end    
    if actualCount == thisExpect
        fprintf('Code %d: OK (observed %d, expected %d)\n',...
            thisCode, actualCount, thisExpect);
    else
        fprintf('Code %d: MISMATCH (observed %d, expected %d)\n',...
            thisCode, actualCount, thisExpect);
    end
end

%% Defining trials based on a given type of triggers (in event.value)


% First we need to code a function that can take the type of trigger and
% the event type = 'trigger


% The function language_study_trial_func needs to have in the provided cfg,
% the event structure.

cfg = [];
cfg.dataset              = 'merged_egyptian_sub004.vhdr';
cfg.trialfun             = 'language_study_trial_func';     % it will call your function and pass the cfg
cfg.trialdef.eventtype  = 'trigger';
cfg.trialdef.eventvalue = [22 129];           % read all conditions at once
cfg.trialdef.prestim    = 1; % in seconds
cfg.trialdef.poststim   = 2; % in seconds

cfg = ft_definetrial(cfg);

cfg.channel = {'AG*'}; % Make sure this is correct by looking at the notebooks
dataMytrialfun = ft_preprocessing(cfg);
% The function language_study_trial_func needs to have in the provided cfg,
% the event structure.

cfg = [];
cfg.dataset              = 'merged_egyptian_sub004.vhdr';
cfg.trialfun             = 'language_study_trial_func';     % it will call your function and pass the cfg
cfg.trialdef.eventtype  = 'trigger';
cfg.trialdef.eventvalue = [22 129];           % read all conditions at once
cfg.trialdef.prestim    = 1; % in seconds
cfg.trialdef.poststim   = 2; % in seconds

cfg = ft_definetrial(cfg);

cfg.channel = {'AG*'}; % Make sure this is correct by looking at the notebooks
dataMytrialfun = ft_preprocessing(cfg);