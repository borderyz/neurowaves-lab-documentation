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
        designMatrix_conv(:,col,iRun) = convolved_signal;
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
designMatrix_concatenated = reshape( permute(designMatrix_conv, [1 3 2]), [], size(designMatrix_conv,2) );

% Concatenate the datafiles (bold signal array) of shape (runtime, nVoxels,
% nRuns


percent_change_signals_concatenated = vertcat(percent_change_signals{:}); 


betas = pinv(designMatrix_concatenated) * percent_change_signals_concatenated; % done per run separatelyf


% Save results in surface space

save betas betas


%% Classification and plots


% Which voxels are the ones classifying the conditions well?
%% Visualise data

percent_change_signals_array = cat(3, percent_change_signals{:});

% we need to sort the data according to the conditions in the designMatrix

% Build a condition_matrix such that it has a shape of (n_run, n_conditions,  

% We want to plot each condition alone (5 plots), for 50 voxels (on the y
% axis) and then across runs (3 runs), the heat map will be the activity of
% that voxel averaged over time for this run

% Let us average over time for one condition

% Let us consider condition = 1

percent_change_signals_array_cat = cat(2, percent_change_signals_array, designMatrix(:, 1:5,:));

% For condition 1, for voxedl 50, for run 1 lets get the condition vector
% in each run, the condition appears for 3 blocks each 20 seconds = 60 seconds, 

start_nvox = 150000; 
end_nvox = 150050;  % How many Voxels we want to show in the plot? We would take from start_nvox to end_nvox
n_vox = end_nvox-start_nvox;

TR_per_run = sum( designMatrix(:,1) == 1 );

TR_per_condition = TR_per_run*nRuns;

conditions_total = zeros(TR_per_condition, number_conditions, n_vox);
for iCon = 1:number_conditions
    for voxel = 1:n_vox
        pc = squeeze(percent_change_signals_array_cat(:, voxel, :)); 
        dm = squeeze(designMatrix(:, iCon, :));    
        %condition_1 = percent_change_signals_array_cat(:,voxel, :) .*designMatrix(:,iCon,:);
        condition = pc .* dm;
        
        non_zero_cols = arrayfun(@(c) nonzeros(condition(:,c)), 1:size(condition,2), 'UniformOutput',false);
        v = vertcat(non_zero_cols{:});
        conditions_total(:, iCon, voxel) = v;
   end
end


% Plot per TR

figure(1);

tiledlayout(1,5);

conditions_total_r = reshape(conditions_total,TR_per_condition, n_vox, []);

for condIdx = 1:number_conditions
    nexttile,
    imagesc(conditions_total_r(:, :,condIdx),[min(conditions_total_r(:)) max(conditions_total_r(:))]);  % Show the activity pattern
    xlabel('Voxel');  % Label the x-axis
    ylabel('TR');    % Label the y-axis
    title(sprintf('Condition %d', condIdx));  % Title for this subplot
    colormap(gray);   % Use grayscale colors
    colorbar;         % Show the color scale
end



%% Plot per run
% Let us average the TR's over the runs for each condition and for each
% voxel

% Each run had 60 TR per condition, they are placed in order from 1 to 180

tmp = reshape(conditions_total_r, TR_per_run, nRuns, n_vox, number_conditions);

% Mean over first dimension

conditions_total_r_avg_runs = squeeze( mean(tmp, 1) );   % → size: [nRuns × nVoxels × nConds]


figure(1);

tiledlayout(1,5);

for condIdx = 1:number_conditions
    nexttile,
    imagesc(conditions_total_r_avg_runs(:, :,condIdx),[min(conditions_total_r_avg_runs(:)) max(conditions_total_r_avg_runs(:))]);  % Show the activity pattern
    xlabel('Voxel');  % Label the x-axis
    ylabel('Run');    % Label the y-axis
    title(sprintf('Condition %d', condIdx));  % Title for this subplot
    colormap(gray);   % Use grayscale colors
    colorbar;         % Show the color scale
end



%% Average activity across condition and runs


conditions_total_r = reshape(conditions_total,TR_per_condition, n_vox, []);

conditions_total_r_avg_time = mean(conditions_total_r)
