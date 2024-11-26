% Read the environment variable to NYU BOX
MEG_DATA_FOLDER = getenv('MEG_DATA');


% Define paths
TASK_NAME = 'audio-visual-motor';
SYSTEM = 'meg-kit';
SUB_ID = 'sub-001';
LASER_DEVICE = 'laser-scan';


% Construct the directory path
DATA_FOLDER_PATH = fullfile(MEG_DATA_FOLDER, TASK_NAME, SUB_ID, SYSTEM);

% List all .con files with the prefix 'sub-001'
filePattern = fullfile(DATA_FOLDER_PATH, [SUB_ID,'*.con']);
conFiles = dir(filePattern);


% Display the file names
disp('Found .con files:');
for k = 1:length(conFiles)
    disp(conFiles(k).name);
end

%%

% Construct the directory path
DATA_FOLDER_PATH_LASER = fullfile(MEG_DATA_FOLDER, TASK_NAME, SUB_ID, LASER_DEVICE);

filePattern_laser_surface = fullfile(DATA_FOLDER_PATH,  [SUB_ID,'*basic-surface.txt']);
filePattern_laser_stylus = fullfile(DATA_FOLDER_PATH,  [SUB_ID,'*stylus-points.txt']);
laser_points = dir(filePattern);


laser_surf = dir()

laser_points    = [MEG_DATA_FOLDER, 'oddball\sub-03\anat\digitized-headshape\sub-03-stylus-cleaned.txt'];
mrkfile1        = [MEG_DATA_FOLDER,'oddball\sub-03\meg-kit\240524-1.mrk'];
mrkfile2        = [MEG_DATA_FOLDER, 'oddball\sub-03\meg-kit\240524-2.mrk'];


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