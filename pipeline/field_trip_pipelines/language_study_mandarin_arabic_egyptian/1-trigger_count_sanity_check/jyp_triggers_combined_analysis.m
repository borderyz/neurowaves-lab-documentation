% Authors: Hadi Zaatiti

% Trigger count for combined binary use with stability check
% To use the script do the following:
% - run word_counting_script.py on the csv first
% - set confile path, set csv path generated from the python script
% - ensure that everything is ok in the output

% Checklist if something is wrong:
% - check that the threshold of 0.5 is good enough
% - test with csv that has break on row

clear

%% Define paths for data
BOX_DIR = getenv('MEG_DATA');

% For egyptian study

%confile = fullfile([BOX_DIR,'egyptian-language-study\sub-trigger\meg-kit\egyptian_list1.con']); 
%csv_file_experiment = fullfile(['egyptian_list1.csv']);

confile = fullfile(['emirati_sub004.con'])
csv_file_experiment = fullfile(['word_count_emirati_list4.csv']);

% For mandarin study

%confile = fullfile(['mandarin_list3.con'])
%csv_file_experiment = fullfile(['word_count_mandarin_list3.csv']);

%% Load data from files
cfg              = [];
cfg.dataset      = confile;
cfg.coilaccuracy = 0;

% Only plotting the trigger channels for now

% On KIT, channel "224" in the hardware often becomes "225" in MATLAB, etc.

cfg.channel         = {'225','226','227','228','229','230','231','232'};
dataTrigger         = ft_preprocessing(cfg);

%% Plot data (optional)
cfg = [];
cfg.viewmode  = 'vertical';
cfg.blocksize = 300; % seconds
ft_databrowser(cfg, dataTrigger);  % <-- 'data_all' must exist; adjust as needed

% dataTrigger.trial{1} is 8 x N (8 channels, N samples)
% dataTrigger.fsample  is the sampling frequency

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
clear event
for i = 1:length(onsetCodes)
    event(i).type      = 'trigger';
    event(i).value     = onsetCodes(i);
    event(i).sample    = changeIdx(i);
    event(i).timestamp = changeIdx(i);
    event(i).offset    = 0;
    event(i).duration  = 1;  
    event(i).time      = onsetTimes(i);
end


%% STEP 5: Compare observed trigger counts to an expected matrix (from CSV)

% Suppose you have a matrix describing [code, expectedCount]
expectedMatrix = jyp_compute_matrix_words(csv_file_experiment);

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