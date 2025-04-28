%%



% load data into 1 by nRun cell array

% create design matrix  n by m 

datapath = 'C:\Users\hz3752\Box\EEG-FMRI\Data\finger-tapping\sub-0665\matlab';

number_conditions = 5;  % Five fingers
number_regressors_motion = 6;  % translation x,y,z and rotation x,y,z 
number_regressors_extra = 2;   % constant regressor and drift
n_cols_total = number_conditions+number_regressors_motion+number_regressors_extra
run_length = 300; %In seconds (the TR was 1 seconds)
nRuns = 3;
block_size = 20;

designMatrix = zeros(run_length, n_cols_total,  nRuns);

const_regress_vector = repelem(1, run_length)';

drift_regress_vector = 1:300;
drift_regress_vector = drift_regress_vector';

hrf = gampdf(run_length,2,3);

%filename = 'fingertap_01.csv';
for iRun=1:nRuns
    %iRun = 1
    file_array_name = ['fingertap_0', num2str(iRun), '.csv'];
    fullpath = fullfile(datapath, file_array_name);
    data_output = readtable(fullpath);
    

    % the designmatrix is filled from data_output
    % the first column is for finger number 1 and so on, the last columns are
    % for the noise regressors
    % in data_output we look at the blocktype column, each block is 20 seconds,
    % so we need to create a repetition of 20 times the values

    condition_vector = repelem(data_output.blocktype, 20);
    
    % Determine the number of rows (same as number of elements in vector)
    num_rows = length(condition_vector);
    
    % Determine the number of columns (max value in vector)
    num_cols = max(condition_vector);
    
    % Preallocate binary matrix
    binary_matrix = zeros(num_rows, num_cols);
    
    % Fill matrix using subscript indexing
    row_indices = (1:num_rows)';
    col_indices = condition_vector(:);  % Ensure it's a column vector
    
    % Linear indexing to set the appropriate entries to 1
    binary_matrix(sub2ind(size(binary_matrix), row_indices, col_indices)) = 1;

    designMatrix(:,1:number_conditions,iRun) = binary_matrix;
    
    % The noise regressors have already been loaded in load_data.m
    designMatrix(:,number_conditions+1:number_regressors_motion+number_conditions,iRun ) = table2array(noise_regressors_data{iRun});
    
    designMatrix(:, number_conditions+number_regressors_motion+1:n_cols_total, iRun) = [const_regress_vector, drift_regress_vector] ;
      
    % PUTI - add constant 1s as a regressor, add linear drift 1:300 as
    % another regressor
    
    % PUTI - - remember to chop the left overs
    % HADI TODO continue here
    conv(designMatrix(1:5,hrf) 

    % get hrf from gamma 
    % hrf = gammapdf(timeRange,2,3);


end

%% run glm

% Y = X.B + Epsilon, with Epsilon = 0
% B = pinv(X) * Y

betas = cell(1, nRuns);


% Three approaches are possible to handle the different runs

% Either concatenate the designmatrix and data for all the runs
% OR you can average the data per run and then estimate beta (this can help
% reduce the noise)
% Or estimate betas per run and then average the betas

% WE wil try all three ways and see which one produces ebtter results



%% Method 1, concatenation of design matrices across runs


% Concatenate the designMatrix of shape (runtime,  features, nRuns)
% New shape (runtime x nRuns, features)
designMatrix_concatenated = reshape( permute(designMatrix, [1 3 2]), [], size(designMatrix,2) );

% Concatenate the datafiles (bold signal array) of shape (runtime, nVoxels,
% nRuns


for iRun = 1:nRuns
    % Need 
    designMatrix_full = co
    betas = pinv(designMatrix) * datafiles; % done per run separatelyf
end

% save result in surface space 
%