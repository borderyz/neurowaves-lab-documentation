%% ------------------ Code section: Build expectedMatrix from CSV ------------------ %%
% Specify the .csv filename or path
csvFilename = 'my_events.csv';

% Read the CSV into a table
T = readtable(csvFilename);

% Suppose your CSV has columns named exactly:
%  - 'trigger' (integer code of the event)
%  - 'trigger225', 'trigger226', ..., 'trigger232' (bits 0/1)

% 1) Extract the bit columns [trigger225..trigger232] into a matrix
bitData = [T.trigger225, T.trigger226, T.trigger227, T.trigger228, ...
           T.trigger229, T.trigger230, T.trigger231, T.trigger232];

% 2) Decode these bits into a single integer per event
%    If 'trigger225' is your least significant bit, use:
bitWeights = 2.^(0:7);  % [1, 2, 4, 8, 16, 32, 64, 128]
decodedFromBits = bitData * bitWeights(:);  % Column vector of decoded trigger codes

% 3) (Optional) Compare decodedFromBits with T.trigger to make sure they match
mismatchIdx = find(decodedFromBits ~= T.trigger);
if ~isempty(mismatchIdx)
    fprintf('WARNING: The following row(s) have mismatch between decoded bits and trigger column:\n');
    disp(mismatchIdx');
    % You could decide to proceed or handle mismatches differently
else
    fprintf('All decoded bit patterns match the trigger column.\n');
end

% 4) Build the expectedMatrix = [ uniqueTriggerCode, countOfThatCode ]
%    We'll count how many times each trigger type appears in T.trigger.
uniqueCodes     = unique(T.trigger);              % All unique trigger codes
numUniqueCodes  = numel(uniqueCodes);
expectedCount   = zeros(numUniqueCodes,1);

for i = 1:numUniqueCodes
    expectedCount(i) = sum(T.trigger == uniqueCodes(i));
end

% The final matrix: first column = code, second column = how many times
expectedMatrix = [uniqueCodes, expectedCount];

% Display or return
disp('Computed expectedMatrix from CSV:');
disp(array2table(expectedMatrix, ...
    'VariableNames', {'TriggerCode','ExpectedCount'}));
