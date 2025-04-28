clear all; close all; clc;

% Set information for your experiment and fmriprep output

subject = 'sub-0665';
nRuns = 3;

task = 'fingertapping';
space = 'fsnative';
fileType = '.mgh';

hemi = {'L';'R'};
bidsDir = 'Y:/projects/MS_osama/hadiBIDS/fmriprep_output_from_HPC';
setenv('FS_LICENSE', '/Applications/freesurfer/7.4.1/license.txt');


datafiles = cell(1,nRuns); % initialize for all the runs

for iRun = 1:nRuns

    % file path
    subDir = sprintf('%s/derivatives/fmriprep/%s/func',bidsDir,subject);

    func = cell(2,1); % initialize for 2 hemi

    for iH = 1:numel(hemi)

        fileName = sprintf('%s/%s_task-%s_run-%s_hemi-%s_space-%s_bold.func',subDir,subject,task,sprintf('%02d',iRun),hemi{iH},space);

        input = [fileName '.gii'];
        output = [fileName fileType]; % the file type that we want to load
        disp(['Filename ', input])
        % check to see if data exists in the desired fileType, if not,
        % mir_convert file from gii
        if ~exist(output)
            disp(['File does not exist in ' fileType ' format, converting from .gii ...'])
            system(['mri_convert ' input ' ' output]);
        else
            disp(['File exists for Run ', num2str(iRun)])
        
        end
        
        disp(['Loading: ' output])

        tmp = MRIread(output);
        func{iH} = squeeze(tmp.vol);
    end
    datafiles{iRun} = cat(1,func{:});
    datafiles{iRun} = datafiles{iRun}';
end


%%

% datafiles is a structure containing three members (because three
% fingertapping runs)
% each member is a 2D matrix of shape (nvoxels, nTRs)



%% Load noise regressors csv
 
fileName_noise_regressors = sprintf('%s/%s_task-%s_run-%s_desc-confounds_timeseries.tsv', subDir,subject,task,sprintf('%02d',iRun));


noise_regressors_data = cell(1, nRuns);

% We have 381 features in the .tsv, we need to extract the noise regressors

regressors_names = {'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z'};

for iRun = 1:nRuns

    noise_regressors_data{iRun} = readtable(fileName_noise_regressors, 'FileType','text');
    noise_regressors_data{iRun} = noise_regressors_data{iRun}(:, regressors_names);
    %noise_regressors_data{iRun} = table2array(noise_regressors_data{iRun})';
end



%% Visualise the data

% ----- USER CHOICES ---------------------------------------------------
runIdx   = 1;        % which run?  1 … numel(datafiles)
voxelIdx = 1234;     % which voxel/vertex index?
TR       = 1.0;      % repetition time in seconds

% ----- EXTRACT THE TIME-SERIES ---------------------------------------
X = datafiles{runIdx};              % [vox × T] (your current orientation)
if size(X,1) < size(X,2)            % safety: flip if it’s [T × vox]
    X = X';
end

ts = X(voxelIdx, :);                % 1 × T vector
t  = (0:numel(ts)-1) * TR;          % time axis (s)

% ----- PLOT -----------------------------------------------------------
figure('Color','w');
plot(t, ts, 'LineWidth', 1);
xlabel('Time (s)');  ylabel('BOLD signal (a.u.)');
title(sprintf('Run %d   –   Voxel %d', runIdx, voxelIdx));
grid on;

%% Denoising using FFT

% fft get rid of  high-pass filter  1/40

TR   = 1.0;                 % <- set your repetition time in seconds
fs   = 1/TR;                % sampling rate (Hz)
f0   = 1/40;                % target frequency to remove (0.025 Hz)

nRuns = numel(datafiles);
figure('Color','w'); hold on;
cols = lines(nRuns);        % distinct colours for each run

% First visualise the FFT

for iRun = 1:nRuns
    X = datafiles{iRun};
    T      = size(X,1);
    freqs  = (0:floor(T/2))' * fs / T;      % positive frequencies
    Y      = fft(X, [], 1);                 % NO detrending
    
    P      = mean(abs(Y).^2 / T, 2);        % mean power spectrum
    P      = P(1:numel(freqs));             % keep positive half
    
    semilogy(freqs, P, ...
             'LineWidth',1.2, ...
             'Color', cols(iRun,:), ...
             'DisplayName', sprintf('Run %d', iRun));
end


xlim([0 0.25]);                   % zoom to useful band (adjust as needed)
xlabel('Frequency (Hz)');
ylabel('Power (a.u., log scale)');
title('Mean FFT spectrum across all voxels (raw, no detrend)');
legend('show','Location','northoutside','Orientation','horizontal');
grid on; box on;




%% simple preprocessing of data

% converting to % signal change

%Compute the average value


% Assume 'datafiles' is your 1x3 cell array
nCells = numel(datafiles);

% Prepare cell arrays to store outputs
average_signals = cell(1, nCells);
percent_change_signals = cell(1, nCells);

for i = 1:nCells

    % Extract the data matrix
    this_data = datafiles{i};  % Size: 300 x 320721

    % Step 1: Compute average across the 1st dimension (rows)
    % Average the signal for each voxel
    
    avg_signal = mean(this_data, 1);  % Result is 1 x 320721
    

    % Step 2: Compute percent signal change for each point
    % Expand avg_signal to match the size of this_data
    avg_signal_expanded = repmat(avg_signal, size(this_data, 1), 1);  % 300 x 320721
    
    percent_change = ((this_data - avg_signal_expanded) ./ avg_signal_expanded) * 100;

    % Store the results
    average_signals{i} = avg_signal;
    percent_change_signals{i} = percent_change;

end






%% FFT for signal change


%% ============================================================
%  FFT visualisation – percent-signal change (no detrending)
%  Assumes:
%     percent_change_signals  – 1×nRuns cell, each  (T × Nvox)  or  (Nvox × T)
%     TR                      – repetition time (s)
% ==============================================================
TR   = 1.0;                  %  <-- set your real TR here
fs   = 1/TR;                 %  sampling rate (Hz)

nRuns = numel(percent_change_signals);
figure('Color','w'); hold on;
cols = lines(nRuns);         % distinct colours

for r = 1:nRuns
    
    % -------- ensure first dimension is time ---------------------------
    X = percent_change_signals{r};          % raw %ΔBOLD
    if size(X,1) < size(X,2),  X = X.'; end % [T × vox]
    
    % -------- FFT & mean power spectrum --------------------------------
    T       = size(X,1);
    freqs   = (0:floor(T/2))' * fs / T;     % 0 … Nyquist
    Y       = fft(X, [], 1);                % along time
    P       = mean(abs(Y).^2 / T, 2);       % average over voxels
    P       = P(1:numel(freqs));            % keep positive half
    
    semilogy(freqs, P, ...
             'LineWidth', 1.2, ...
             'Color', cols(r,:), ...
             'DisplayName', sprintf('Run %d', r));
end

xlim([0 0.25]);                % zoom to useful band
xlabel('Frequency (Hz)');
ylabel('Power (%ΔBOLD)^2  (log scale)');
title('Mean FFT spectrum – percent-signal change');
legend('show','Location','northoutside','Orientation','horizontal');
grid on; box on;




