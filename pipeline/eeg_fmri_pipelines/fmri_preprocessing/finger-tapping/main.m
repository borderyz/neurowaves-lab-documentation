% Pipeline processing finger-tapping experiment data from fmriprep output
% TR = 1 second
% Blockduration = 20 second


SUB_ID = 'sub-0665'
TASK_NAME = 'finger-tapping'
SYSTEM = 'matlab'
FILENAME = 'fingertap_01.csv'

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

