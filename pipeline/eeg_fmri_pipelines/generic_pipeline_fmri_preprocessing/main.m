%%

% load data into 1 by nRun cell array

% create design matrix  n by m 


EEG_FMRI_DATA_PATH = getenv('EEG_FMRI_DATA');

datapath = sprintf('%s\\%s\\%s\\matlab', EEG_FMRI_DATA_PATH, task, subject);
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

gam_x_values = linspace(1,block_size, block_size);
hrf = gampdf(gam_x_values,2,3);

% Plot hrf

plot(gam_x_values,hrf);

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

    % PUTI - add constant 1s as a regressor, add linear drift 1:300 as
    % another regressor DONE D

    designMatrix(:,number_conditions+1:number_regressors_motion+number_conditions,iRun ) = table2array(noise_regressors_data{iRun});
    
    designMatrix(:, number_conditions+number_regressors_motion+1:n_cols_total, iRun) = [const_regress_vector, drift_regress_vector] ;
     
    
    % PUTI - - remember to chop the left overs

    for col = 1:number_conditions
        convolved_signal = conv(designMatrix(:,col,iRun),hrf);
        convolved_signal = convolved_signal(1:run_length);  % Chop the leftovers
        designMatrix(:,col,iRun) = convolved_signal;
            % Chop off the left overs
        %plot(1:run_length, convolved_signal);
    end
    
    

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


percent_change_signals_concatenated = vertcat(percent_change_signals{:}); 


betas = pinv(designMatrix_concatenated) * percent_change_signals_concatenated; % done per run separatelyf


% Save results in surface space

save betas betas

% save as mgz

% largest betas for index finger +40seconds after the index is pressed

% Make a matrix where the finger is pressed on the rows, and the 40 seconds
% next (random fingers) on the column

%% Find the voxels where there is a peak for the betas of the index finger

% the average on the 40 seconds should eliminate the activity going on
% during fingertap at other fingers

% betas 
% largest


%% Generate ROI labels from the Glasser Atlas in subject native space (fsnative)

% the script createAtlasLabels.sh will load different Atlases for which it
% knows the location of each ROI on the atlas space and will convert them
% into the individual space of each subject


atlas_file_path = 'label/Glasser2016';




for ROI = 1:number_ROIs

% load ROI using GUI select
% Open a file selection dialog for the relevant file type (e.g., .txt or .mat)
[filename, pathname] = uigetfile({'*.*', 'All Files (*.*)'}, 'Select ROI Label File');


% Check if a file was selected
if isequal(filename, 0)
    disp('No file selected.');
else
    fullpath = fullfile(pathname, filename);
    % Pass the selected file to your function
    ROI_voxels_mask = read_ROIlabel(fullpath);
end



%% Use the ROI as filter for betas

% The ROI_voxels_mask is a list of the voxels number that belongs to the ROI
% W're assurming that nothing in the code had changed the order of the
% voxel dimensions in the betas variable


filtered_betas = betas(:, ROI_voxels_mask);






%%


%

% Path to the folder with ROI label files
atlas_file_path = 'label/Glasser2016';

% Get list of all label files (assuming .label or .txt, adjust as needed)
roi_files = dir(fullfile(atlas_file_path, '*.label'));

% Preallocate
nROIs = numel(roi_files);
mean_betas_per_roi = zeros(nROIs, 1);
roi_names = cell(nROIs, 1);

for i = 1:nROIs
    % Full path to ROI label file
    roi_path = fullfile(roi_files(i).folder, roi_files(i).name);
    
    % Read voxel indices for this ROI
    ROI_voxels_mask = read_ROIlabel(roi_path);   % indices into betas

    % Select beta values for this ROI
    betas_roi = betas(:, ROI_voxels_mask);       % [nRegressors × ROI voxels]
    
    % Average across voxels, then across regressors (or just one regressor if needed)
    mean_betas_per_roi(i) = mean(betas_roi(:));  % scalar mean

    % Store the ROI name
    roi_names{i} = roi_files(i).name;
end

% Find the ROI with the maximum average beta
[~, max_idx] = max(mean_betas_per_roi);
max_roi_name = roi_names{max_idx};
max_roi_value = mean_betas_per_roi(max_idx);

fprintf('ROI with max beta = %s (avg beta = %.4f)\n', max_roi_name, max_roi_value);


%% 

% ----- Load voxel indices for the winning ROI -------------------------
chosen_roi_file = fullfile(roi_files(max_idx).folder, roi_files(max_idx).name);
ROI_voxels_mask = read_ROIlabel(chosen_roi_file);

% ----- Initialize for time series collection --------------------------
nRuns = numel(datafiles);
avg_ts_all_runs = [];

for r = 1:nRuns
    X = datafiles{r};   % assumed [time × voxels]
    
    % Extract ROI voxels
    roi_ts = X(:, ROI_voxels_mask);  % [time × ROI_voxels]
    
    % Average across voxels
    avg_ts = mean(roi_ts, 2);        % [time × 1]
    
    % Optionally concatenate across runs (if aligned), or store separately
    avg_ts_all_runs = [avg_ts_all_runs; avg_ts];  % vertical concat
end

% ----- Plot -----------------------------------------------------------
TR = 1.0;  % <- Set your TR
t = (0:numel(avg_ts_all_runs)-1) * TR;

figure('Color','w');
plot(t, avg_ts_all_runs, 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('BOLD Intensity (a.u.)');
title(sprintf('Average Time Series – ROI: %s', roi_files(max_idx).name), 'Interpreter','none');
grid on;









