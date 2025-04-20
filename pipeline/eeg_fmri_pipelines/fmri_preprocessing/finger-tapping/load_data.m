clear all; close all; clc;

subject = 'sub-0665';
nRuns = 3;

task = 'fingertapping';
space = 'fsnative';
fileType = '.mgh';

hemi = {'L';'R'};
bidsDir = '/Volumes/MS_osama/hadiBIDS/fmriprep_output_from_HPC';
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

        % check to see if data exists in the desired fileType, if not,
        % mir_convert file from gii
        if ~exist(output)
            disp(['File does not exist in ' fileType ' format, converting from .gii ...'])
            system(['mri_convert ' input ' ' output]);
        end

        disp(['Loading: ' output])

        tmp = MRIread(output);
        func{iH} = squeeze(tmp.vol);
    end
    datafiles{iRun} = cat(1,func{:});

end


%%

data = datafiles{1}(100,:);