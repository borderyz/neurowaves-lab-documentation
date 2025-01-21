% Pipeline processing finger-tapping experiment data from fmriprep output
% TR = 1 second
% Blockduration = 20 second


SUB_ID = 'sub-0665'
TASK_NAME = 'finger-tapping'
SYSTEM = 'matlab'
FILENAME = 'fingertap_01.csv'

%Temporary one is used now
FMRI_DATA_PATH = 'C:\Users\hz3752\Box\EEG-FMRI\Data\archive\finger-tapping\sub-0665\fmri\derivatives\fmriprep\sub-0665\ses-01\func'
FMRI_DATA_FILE_NAME = 'sub-0665_ses-01_task-fingertapping_dir-AP_run-01_hemi-L_space-fsaverage6_bold.func.gii'

% Fmri processing need two files:
% 4D BOLD timeseries (3D for voxel location and 1 D is time)
%    another possibility is 2D for voxel location on grey matter surface
%    and 1D is time
%Confound timeseries (motion, nuisance regressors)

% Different types of files can be found in output of fmriprep
% .func.gii = 3D (2D surface coordinates and 1D is time)
% .confounds_timeseries.tsv = motion and nuisance
% 



FMRI_DATA_FILE = fullfile(FMRI_DATA_PATH, FMRI_DATA_FILE_NAME);

% Load BOX variable
EEG_FMRI_DATA = getenv('EEG_FMRI_DATA');

DATA_FOLDER_PATH = fullfile(EEG_FMRI_DATA, TASK_NAME, SUB_ID, SYSTEM, FILENAME);

data = readtable(DATA_FOLDER_PATH); 

data.blocktype

%% Prepare your design matrix

% Suppose you already loaded a variable blocktype from a CSV or MAT file.
% blocktype is something like: [1; 2; 3; 4; 5; 1; ... ] for each block.

% 1) Define parameters
blockDuration = 20;    % seconds per block (also # of TRs if TR=1s)
nBlocks       = length(data.blocktype);
nConditions   = 5;     % fingers 1 through 5

% 2) Compute total number of TRs
nTR = nBlocks * blockDuration;

% 3) Initialize the design matrix with zeros
designMatrix = zeros(nTR, nConditions);

% 4) Fill in the design matrix
for iBlock = 1:nBlocks
    cond = data.blocktype(iBlock);   % which finger was tapped?
    
    % Compute the time (TR) indices for this block
    startIdx = (iBlock - 1)*blockDuration + 1;   % inclusive
    endIdx   = iBlock*blockDuration;             % inclusive
    
    % Fill the design matrix with ones in the appropriate column
    designMatrix(startIdx:endIdx, cond) = 1;
end

% designMatrix has dimensions [nTR x 5]. 
% Columns correspond to conditions (fingers) 1 through 5.

%%




% Load fmri prep output from NYU BOX

mri_convert (from freesurfer)

% 	Default surface fmri data post fmriprep is in .gii and is too slow so we want data in .mgh, loads much faster


% Install https://github.com/vistalab/vistasoft read readme for
% Use the MRIread command to read a free-surfer like structure of an MRI.h
% (voxel (i,j,k) and time
% Check --> Surface voxel (2D) or 3D voxels?
MRIread

% installation instructions

% 	Load .mgh 
% Install the package (https://github.com/cvnlab/GLMsingle)
stimulus_duration = 2; % in seconds
tr = 1; % in seconds
getcanonicalhrf(stimulus_duration, tr)
% 	Need the hrf during beta fitting (we haven’t talked about this, basically, we needs to convolve the design matrix with HRF to account for the delay)
% 
% Actual beta fitting — beta = pinv(designMatrix) * data;

beta = pinv(designMatrix) * data;

% 

