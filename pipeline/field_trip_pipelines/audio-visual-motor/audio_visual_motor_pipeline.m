%% FieldTrip pipeline for audio-visual-motor experiment
% Author: Hadi Zaatiti <hadi.zaatiti@nyu.edu>


clear;

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


filePattern_mrk = fullfile(DATA_FOLDER_PATH, '*.mrk');

mrkFiles = dir(filePattern_mrk);

% Construct the directory path
DATA_FOLDER_PATH_LASER = fullfile(MEG_DATA_FOLDER, TASK_NAME, SUB_ID, LASER_DEVICE);

filePattern_laser_surface = fullfile(DATA_FOLDER_PATH_LASER,  [SUB_ID,'*basic-surface.txt']);
filePattern_laser_stylus = fullfile(DATA_FOLDER_PATH_LASER,  [SUB_ID,'*stylus-points.txt']);

laser_points = dir(filePattern_laser_surface);
laser_surf = dir(filePattern_laser_stylus);


%%

% Initialize FieldTrip configuration
cfg = [];
cfg.coilaccuracy = 0;

% Cell array to store preprocessed data
dataList = {};

% Loop through all .con files
for k = 1:length(conFiles)
    % Construct the full path for the current .con file
    conFile = fullfile(DATA_FOLDER_PATH, conFiles(k).name);
    
    % Set the dataset in the configuration
    cfg.dataset = conFile;
    
    % Preprocess the MEG data
    fprintf('Processing file: %s\n', conFiles(k).name);
    dataList{k} = ft_preprocessing(cfg); % Store preprocessed data in the list
end

% Concatenate all preprocessed data
fprintf('Concatenating all preprocessed data...\n');
combinedData = ft_appenddata([], dataList{:});

% Display a message when concatenation is complete
disp('Data concatenation complete.');




%% Filtering data

if APPLY_FILTERS
    % Notch filter the data at 50 Hz
    cfg = [];
    cfg.bsfilter = 'yes';
    cfg.bsfreq = [49 51]; % Notch filter range
    combinedData = ft_preprocessing(cfg, combinedData);

    % Band-pass filter the data
    cfg = [];
    cfg.bpfilter = 'yes';
    cfg.bpfreq = [4 40]; % Band-pass filter range
    cfg.bpfiltord = 4;   % Filter order
    combinedData = ft_preprocessing(cfg, combinedData);
    
    disp('Filtering operations complete on combined data.');
end



