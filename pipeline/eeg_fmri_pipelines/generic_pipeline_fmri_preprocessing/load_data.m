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


%% simple preprocessing of data

% converting to % signal change


% fft get rid of  high-pass filter  1/40 
