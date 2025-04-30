%% Goal

% Step 1 - simulate neural activity
% Step 2 - simulate fMRI data - convolve with hrf
% Step 3 - add noise
% Step 4 - visualize active vs non-active voxels
% Step 5 - build a model and solve for beta

%% useful functions to try 

% pwd - get current working directory
% clear all - clear all variables in the workspace
% clc - clear command window
% close all - close all open figures
% others:
    %help/doc - type doc doc in command window to learn more
    %repmat
    %repelem
    %mod
    %conv
    %squeeze
    %flip
    %pinv
    %'
    %imagesc/imshow/plot/scatter/hist
    %randn
      
% given any variable 'val'
    % it is always good to check the following things:
        % size and dimension - size(vals)
            % size of the kth dimension - size(vals,k)
        % basic stats - min(vals), max(vals), mean(vals)
            % use vals(:) instead of vals to get the result across all the values in this variable regardless of dimensions
        % distribution - hist(vals)
    % always keep in mind:
        %  what each dimension of my variable means
        %  what does large and small number mean in my variable, what's the range

%% Clear workspace and close figures
clear all
close all
clc

%% Part 1: Simulating Neural Activity
% Let's start by understanding the basic components of fMRI data

% First, let's set up some basic parameters
expDuration = 300; % experiments lasts 5 minutes - 300 seconds
blockDuration = 15; % each block lasts 15 seconds 
myTime = 1:expDuration; % 1:300, every second of this duration
blockDesign  = repelem([1 0],1,blockDuration); % 15 1s and 15 0s
expDesign  = repmat(blockDesign,1,expDuration/blockDuration/2); % we repeat the blocks many times through out 5 minutes

% for now, this expDesign is as good of a guess to neural activity as we can 
% basically mean neuron spikes at onset of the stimulus
dataNeural = expDesign;

% let's visualize it
figure(1); clf;
plot(dataNeural,'LineWidth',2)
ylim([0,1.1])
ylabel('neural activity (a.u.)')
xlabel('time (secs)');
title('ON and OFF of neural activity')
set(gca,'FontSize',15,'TickDir','out','Linewidth',2,'YTick',[0 0.5 1]);

%% Part 2: Simulating fMRI Data - Convolve with HRF

% real fMRI data are sluggish and not like the sharp on/off shape for the expDesign
% this is because of the HRF (hemodynamic impulse response function)
% we can model it and add it to our neural activity

% there are fancy ways to generate, model, and estimate HRF
% for now,  we will use a budget version -  the gamma function

%% Part 2.1: Generate HRF 

% we have two knobs (parameters) to set:
tau = 2; % decides shape of the peak
delta =  2; % decides delay after stimulus onset

% make our budget HRF
timeHrf = 0:1:30; % we will get the hrf for 30 seconds
hrf = (max(timeHrf-delta,0)/tau).^2 .* exp(-max(timeHrf-delta,0)/tau) / (2*tau);

figure(2); clf;
plot(timeHrf,hrf,'LineWidth',2);
title('HRF')
ylabel('intensities (a.u.)')
xlabel('time (sec)')
set(gca,'FontSize',15,'TickDir','out','Linewidth',2,'YTick',[0 0.5 1]);

%% Part 2.2: Generate fMRI Data 

% now let's transform our on/off neural activity to fmri data with the hrf

datafMRI =  conv(dataNeural,hrf);
datafMRI = datafMRI(1:length(dataNeural)); % chop off extra data generated from the function conv 

figure(3); clf;
plot(datafMRI,'LineWidth',2);
ylim([0,1.1])
title('fMRI signal')
ylabel('intensities (a.u.)')
xlabel('time (sec)')
set(gca,'FontSize',15,'TickDir','out','Linewidth',2,'YTick',[0 0.5 1]);
 
%% Part 2.3: Add Baseline and Convert to Percentage Signal Change

% some extra stuff: add a baseline for the fMRI signal and converting it to %signal change

datafMRI = 100 + conv(dataNeural,hrf); % 100 value added as a baseline
datafMRI = datafMRI(1:length(dataNeural)); % chop off extras
datafMRIpercent = 100 * ((datafMRI/(mean(datafMRI)) - 1)); % percentage signal change

figure(4); clf;
plot(datafMRIpercent,'Linewidth',2);

title('fMRI percentage signal change')
ylabel('signal change (%)')
xlabel('time (sec)')
set(gca,'FontSize',15,'TickDir','out','Linewidth',2);

%% Part 3: Adding Noise
% Real fMRI data has noise - let's add some

% Add Gaussian noise
noiseLevel = 0.5;
noise = noiseLevel * randn(size(datafMRI)); % generate noise using randn
dataNoisy = datafMRI + noise; % add noise
dataNoisy = 100 * ((dataNoisy/(mean(dataNoisy)) - 1)); % convert to %signal change

% Plot it
figure(5); clf;
subplot(3,1,1)
plot(noise,'Linewidth',2)
title('noise')
ylabel('intensities (a.u.)')
xlabel('time (sec)')
set(gca,'FontSize',15,'TickDir','out','Linewidth',2);

subplot(3,1,2)
plot(datafMRIpercent,'Linewidth',2);
ylim([-1 1])
title('fMRI data without noise')
ylabel('signal change (%)')
xlabel('time (sec)')
set(gca,'FontSize',15,'TickDir','out','Linewidth',2);

subplot(3,1,3)
plot(dataNoisy,'Linewidth',2);
ylim([-1 1])
title('fMRI data with noise')
ylabel('signal change (%)')
xlabel('time (sec)')
set(gca,'FontSize',15,'TickDir','out','Linewidth',2);

%% Part 4: Visualizing Active vs Non-Active Voxels
% Let's create and compare active and non-active voxels

% Create a non-active voxel (baseline + noise)
baseline = 100; % same baseline as our active voxel
nonActiveVoxel = baseline + noiseLevel * randn(size(datafMRI));
nonActiveVoxel = 100 * ((nonActiveVoxel/(mean(nonActiveVoxel)) - 1)); % convert to %signal change

% Plot both voxels on the same plot
figure(6); clf;
subplot(2,1,1)
plot(dataNoisy,'Linewidth',2);
title('Active Voxel')
ylabel('signal change (%)')
xlabel('time (sec)')
set(gca,'FontSize',15,'TickDir','out','Linewidth',2);
ylim([-1 1])

subplot(2,1,2)
plot(nonActiveVoxel,'Linewidth',2);
title('Non-Active Voxel')
ylabel('signal change (%)')
xlabel('time (sec)')
set(gca,'FontSize',15,'TickDir','out','Linewidth',2);
ylim([-1 1])

%% Part 5: Building a Model and Solving for Beta
% Now let's build a simple model to analyze our data

% Create the task regressor convolved with HRF
taskRegressor = conv(expDesign, hrf);
taskRegressor = taskRegressor(1:expDuration); % trim to match data length

% Create linear drift term
drift = linspace(0, 1, expDuration)';

% Create design matrix with task regressor, drift, and constant term
model = [taskRegressor' drift ones(expDuration,1)];

% Solve for beta weights using the noisy data
b = pinv(model) * dataNoisy';

% Calculate the model fit
modelFit = model * b;

% Plot the results
figure(7); clf;

plot(dataNoisy,'Linewidth',2);
hold on;
plot(modelFit,'r--','Linewidth',2);
title('Model Fit')
ylabel('signal change (%)')
xlabel('time (sec)')
legend('Data', 'Model Fit')
set(gca,'FontSize',15,'TickDir','out','Linewidth',2);
ylim([-1 1])


disp('Basic fMRI concepts tutorial completed successfully!');
disp('Next steps: Run fMRI_Classification.m to learn about classification analysis.'); 