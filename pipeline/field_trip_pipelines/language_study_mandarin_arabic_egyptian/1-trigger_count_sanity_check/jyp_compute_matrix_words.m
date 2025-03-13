function expectedMatrix = compute_matrix_words(csvFilename)
% COMPUTEEXPECTEDMATRIXFROMCSV loads a CSV file which:
%  - Has columns trigger224..trigger231 (the first-word triggers),
%    columns trigger224w..trigger231w (subsequent-word triggers),
%    and a 'wordcount' column telling how many words in this row.
%  - Returns expectedMatrix = [uniqueTriggerCode, expectedCount].
%
% For each row, we add 1 occurrence of the first-word code
% and (wordcount - 1) occurrences of the subsequent-word code (if wordcount > 1).

    % 1) Read the CSV into a table
    T = readtable(csvFilename);

    % Check for required trigger columns
    firstWordCols = ["trigger224","trigger225","trigger226","trigger227", ...
                     "trigger228","trigger229","trigger230","trigger231"];
    wordCols      = ["trigger224w","trigger225w","trigger226w","trigger227w", ...
                     "trigger228w","trigger229w","trigger230w","trigger231w"];

    if ~all(ismember(firstWordCols, T.Properties.VariableNames))
        error('CSV must contain columns: %s', strjoin(firstWordCols, ', '));
    end
    if ~all(ismember(wordCols, T.Properties.VariableNames))
        error('CSV must contain columns: %s', strjoin(wordCols, ', '));
    end

    % Make sure the CSV has a "wordcount" column
    if ~ismember("wordcount", T.Properties.VariableNames)
        error('CSV must contain a "wordcount" column (integer number of words).');
    end

    % 2) Ensure the 'wordcount' column is numeric
    if iscell(T.wordcount) || isstring(T.wordcount)
        T.wordcount = str2double(T.wordcount);  % Convert text to numbers
    end

    % Check for any invalid entries in the 'wordcount' column
    if any(isnan(T.wordcount))
        error('The "wordcount" column contains invalid or non-numeric entries.');
    end

    % 3) Extract the bit columns into matrices
    bitDataFirst = [T.trigger224,  T.trigger225,  T.trigger226,  T.trigger227, ...
                    T.trigger228,  T.trigger229,  T.trigger230,  T.trigger231];

    bitDataOther = [T.trigger224w, T.trigger225w, T.trigger226w, T.trigger227w, ...
                    T.trigger228w, T.trigger229w, T.trigger230w, T.trigger231w];

    % 4) Decode these bits into integer trigger codes
    %bitWeights = 2.^(0:7).';  % column vector [1;2;4;8;16;32;64;128]
    bitWeights = flip(2.^(0:7).');
    codeFirst  = bitDataFirst * bitWeights;  % Nx1
    codeOther  = bitDataOther * bitWeights;  % Nx1

    % 5) Accumulate counts in a Map (code -> occurrences)
    codeCounts = containers.Map('KeyType','double','ValueType','double');

    for i = 1:height(T)
        nWords = T.wordcount(i);  % the number of words from the CSV

        % If at least 1 word, add first-word trigger
        if nWords >= 1
            c = codeFirst(i);
            if ~isKey(codeCounts, c), codeCounts(c) = 0; end
            codeCounts(c) = codeCounts(c) + 1;
        end
        
        % If more than 1 word, add subsequent-word triggers
        if nWords > 1
            c = codeOther(i);
            if ~isKey(codeCounts, c), codeCounts(c) = 0; end
            codeCounts(c) = codeCounts(c) + (nWords - 1);
        end
    end

    % 6) Convert the Map to a matrix [triggerCode, expectedCount]
    allCodes  = cell2mat(codeCounts.keys);
    allCounts = cell2mat(codeCounts.values);

    % Sort by code, just for neatness
    [uniqueCodes, idx] = sort(allCodes);
    expectedCount       = allCounts(idx);

    expectedMatrix = [uniqueCodes(:), expectedCount(:)];

    % Display results
    disp(' ');
    disp('--- Computed expectedMatrix from CSV (TriggerCode, Count) ---');
    disp(array2table(expectedMatrix, ...
        'VariableNames', {'TriggerCode','ExpectedCount'}));
end
