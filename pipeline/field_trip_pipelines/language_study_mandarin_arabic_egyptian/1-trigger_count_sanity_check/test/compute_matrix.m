function expectedMatrix = computeExpectedMatrixFromCSV(csvFilename)
% COMPUTEEXPECTEDMATRIXFROMCSV loads a CSV file, decodes triggers, checks 
% consistency, and returns an expectedMatrix = [uniqueTriggerCode, expectedCount].
%
% The CSV must contain:
%   - a 'trigger' column (the official code),
%   - columns 'trigger224' .. 'trigger231' (the bits).
    
  

    %% 1) Read the CSV into a table
    T = readtable(csvFilename);

    requiredCols = ["trigger","trigger224","trigger225","trigger226","trigger227", ...
                    "trigger228","trigger229","trigger230","trigger231"];
    if ~all(ismember(requiredCols, T.Properties.VariableNames))
        error('CSV must contain columns: %s', strjoin(requiredCols, ', '));
    end
    
    %% 2) Extract the bit columns [trigger224..trigger231] into a matrix
    %    (Check the bit order is correct for your setup!)
    bitData = [T.trigger224, T.trigger225, T.trigger226, T.trigger227, ...
               T.trigger228, T.trigger229, T.trigger230, T.trigger231];
    
    %% 3) Decode these bits into a single integer per event
    % If 'trigger224' is the least significant bit, do:
    bitWeights = 2.^(0:7);  % [1, 2, 4, 8, 16, 32, 64, 128]
    decodedFromBits = bitData * bitWeights(:);  % column vector of code
    
    %% 4) Compare decoded bits with T.trigger
    mismatchIdx = find(decodedFromBits ~= T.trigger);
    if ~isempty(mismatchIdx)
        fprintf('\nWARNING: The following row(s) mismatch "trigger" vs. bit-derived code:\n');
        disp(mismatchIdx');
    else
        fprintf('\nAll decoded bit patterns match the "trigger" column.\n');
    end
    
    %% 5) Append the bit-derived code to the table for clarity
    T.BitDerivedBase10 = decodedFromBits;  %#ok<AGROW> 
    disp('--- CSV rows with bit-derived code ---');
    disp(T);

    %% 6) Build the expectedMatrix = [uniqueTriggerCode, count]
    uniqueCodes   = unique(T.trigger);
    expectedCount = zeros(size(uniqueCodes));
    for i = 1:numel(uniqueCodes)
        expectedCount(i) = sum(T.trigger == uniqueCodes(i));
    end
    
    % The final matrix: first column = code, second = occurrence count
    expectedMatrix = [uniqueCodes, expectedCount];

    disp(' ');
    disp('--- Computed expectedMatrix from CSV (TriggerCode, Count) ---');
    disp(array2table(expectedMatrix, ...
        'VariableNames', {'TriggerCodeBase10','ExpectedCount'}));
end
