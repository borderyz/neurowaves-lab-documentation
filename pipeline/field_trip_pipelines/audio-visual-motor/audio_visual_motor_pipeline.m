% Read the environment variable to NYU BOX
MEG_DATA_FOLDER = getenv('MEG_DATA');

TASK_NAME = 'audio-visual-motor\';


% Set path to KIT .con file of sub-03
DATASET_PATH = [MEG_DATA_FOLDER, TASK_NAME];

% 

SYSTEM  = 'meg-kit2\';
SUB_ID = 'sub-01\';

% Set path to KIT .con file of sub-03
DATASET_PATH = [MEG_DATA_FOLDER,'oddball\sub-03\meg-kit\sub-03-raw-kit.con'];

% Set path to computed .mat variables, these has been obtained by executing this pipeline and
% will allow you to skip steps if you wish to execute a particular cell
LOAD_PATH = [MEG_DATA_FOLDER, 'oddball\derivatives\kit_oddball_pipeline_fieldtrip\sub-03\'];

% Experiment your own test and save your variables in a folder of your choice, choose the folder where to save your variables
% We will also use it to copy variables from LOAD_PATH and use them in the notebook if needed
SAVE_PATH = 'docs\source\5-pipeline\notebooks\fieldtrip\fieldtrip_oddball_kit_data\';

% It is important that you use T1.mgz instead of orig.mgz as T1.mgz is normalized to [255,255,255] dimension
MRI_FILE         = fullfile([MEG_DATA_FOLDER,'oddball\sub-03\anat\sub-003\sub-003\mri\T1.mgz']);

laser_surf      = fullfile([MEG_DATA_FOLDER,'oddball\sub-03\anat\digitized-headshape\sub-03-basic-surface.txt']);
%The cleaned stylus points removes the last three columns (dx, dx, dz) and
%keeps only x,y,z
laser_points    = [MEG_DATA_FOLDER, 'oddball\sub-03\anat\digitized-headshape\sub-03-stylus-cleaned.txt'];
mrkfile1        = [MEG_DATA_FOLDER,'oddball\sub-03\meg-kit\240524-1.mrk'];
mrkfile2        = [MEG_DATA_FOLDER, 'oddball\sub-03\meg-kit\240524-2.mrk'];

try
    cd(SAVE_PATH)
catch
end