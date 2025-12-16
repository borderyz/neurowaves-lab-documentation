% save_matlab_output.m
% This script demonstrates how to save MATLAB console output to a log file
% automatically stamped with date, subject ID, and other relevant info.
% It uses the 'diary' function to capture everything printed to the Command Window.

%% 1. Clean Workspace
clear; clc; 

%% 2. Participant Data Collection
% (Code adapted from VI_MEG_20251027.m)
name1 = 'Participant Data';
prompt1 = {'Subject Number', 'Subject ID', 'Sex (f/m)', 'Age', 'Nationality'};
numlines1 = 1;
defaultanswer1 = {'0', '', '', '', ''};
answer1 = inputdlg(prompt1, name1, numlines1, defaultanswer1);

if isempty(answer1)
    disp('Experiment cancelled by user.');
    return;
end

% Parse input
subNumStr = answer1{1};
subIDStr  = answer1{2};
sex       = answer1{3};
age       = str2double(answer1{4});
nat       = answer1{5};

%% 3. Setup Logging
% Create a unique filename based on Subject Number, ID, and current timestamp
% Create a BIDS-compliant filename
% Format: sub-[SubjectID]_task-[TaskName]_beh.log
% Example: sub-01_task-visualimagery_beh.log

% You can define the task name here
taskName = 'visualimagery'; 

% Ensure Subject ID is formatted correctly (remove spaces, etc.)
subIDClean = regexprep(subNumStr, '\s', ''); 

% Construct filename
logFileName = sprintf('sub-%s_task-%s_desc-matlabconsole_log.txt', subIDClean, taskName);

% Define full path - creating a 'logs' directory if it doesn't exist
logDir = fullfile(pwd, 'logs');
if ~exist(logDir, 'dir')
    mkdir(logDir);
end
logFilePath = fullfile(logDir, logFileName);

% Turn on diary to start recording command window output
diary(logFilePath);

%% 4. Start of Experiment Simulation
fprintf('================================================\n');
fprintf('     PSYCHTOOLBOX EXPERIMENT LOG\n');
fprintf('================================================\n');
fprintf('Log file: %s\n', logFilePath);
fprintf('Date/Time: %s\n', datestr(now));
fprintf('\n--- Participant Info ---\n');
fprintf('Subject Number: %s\n', subNumStr);
fprintf('Subject ID:     %s\n', subIDStr);
fprintf('Sex:            %s\n', sex);
fprintf('Age:            %d\n', age);
fprintf('Nationality:    %s\n', nat);
fprintf('================================================\n\n');

fprintf('Initializing Experiment...\n');
WaitSecs(0.5); % Simulate setup time
fprintf('Setup Complete.\n\n');

%% 5. Simulated Trial Loop
nTrials = 5;

for i = 1:nTrials
    fprintf('--- Starting Trial %d of %d ---\n', i, nTrials);
    
    % Simulate Stimulus Onset
    onset = GetSecs();
    fprintf('Trial %d: Stimulus presented at %.4f\n', i, onset);
    
    % Simulate variable wait time (e.g., waiting for response)
    waitTime = 0.5 + rand() * 1.0; % Random between 0.5s and 1.5s
    WaitSecs(waitTime);
    
    % Simulate Response
    rt = GetSecs() - onset;
    fprintf('Trial %d: Response received.\n', i);
    fprintf('Trial %d: Reaction Time = %.4f seconds\n', i, rt);
    
    fprintf('--- Trial %d Complete ---\n\n', i);
end

%% 6. End of Experiment
fprintf('================================================\n');
fprintf('Experiment Finished at %s\n', datestr(now));
fprintf('================================================\n');

% Turn off diary to stop recording and close the file
diary off;

fprintf('Console output saved to: %s\n', logFilePath);
