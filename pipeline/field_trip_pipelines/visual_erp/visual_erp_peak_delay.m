%% FieldTrip pipeline for studying VEFs from audio-visual-motor experiment
% Author: Hadi Zaatiti <hadi.zaatiti@nyu.edu>


clear;

% Reminder of stimulus types:

% 1 is visual stimulus = ch224
% 2 is auditory stimulus = ch225
% 3 is motor button = ch226

% Read the environment variable to NYU BOX
MEG_DATA_FOLDER = getenv('MEG_DATA');


% Define paths
TASK_NAME = 'audio-visual-motor';
SYSTEM = 'meg';
SUB_ID = 'sub-001';
SESSION_ID = 'ses-01';

% Construct the directory path
DATA_FOLDER_PATH = fullfile(MEG_DATA_FOLDER, TASK_NAME, SUB_ID, SESSION_ID, SYSTEM);

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

% Display the file names
disp('Found .mrk files:');
for k = 1:length(mrkFiles)
    disp(mrkFiles(k).name);
end

% Construct the directory path
DATA_FOLDER_PATH_LASER = fullfile(MEG_DATA_FOLDER, TASK_NAME, SUB_ID, SESSION_ID, SYSTEM);

filePattern_laser_surface = fullfile(DATA_FOLDER_PATH_LASER,  [SUB_ID,'*', SESSION_ID, '*acq-head_headshape.pos']);
filePattern_laser_stylus = fullfile(DATA_FOLDER_PATH_LASER,  [SUB_ID, '*', SESSION_ID, '*acq-points_headshape.pos']);

laser_points = dir(filePattern_laser_surface);
laser_surf = dir(filePattern_laser_stylus);

disp('Found headshape points files:');
for k = 1:length(laser_points)
    disp(laser_points(k).name);
end

disp('Found headshape surface files:');
for k = 1:length(laser_surf)
    disp(laser_surf(k).name);
end


APPLY_FILTERS = false;

%% Loading data and concatenating from the different .con files

% Initialize FieldTrip configuration for loading data
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
    cfg.readbids = 'no';
    % Preprocess the MEG data
    fprintf('Processing file: %s\n', conFiles(k).name);
    dataList{k} = ft_preprocessing(cfg); % Store preprocessed data in the list
end

% Concatenate all preprocessed data
fprintf('Concatenating all preprocessed data...\n');
combinedData = ft_appenddata([], dataList{:});

% Display a message when concatenation is complete
disp('Data concatenation complete.');


%% Filtering data (not used for this pipeline)

if APPLY_FILTERS
    % Notch filter the data at 50 Hz
    cfg = [];
    cfg.bsfilter = 'yes';
    cfg.bsfreq = [49 51]; % Notch filter range
    combinedData = ft_preprocessing(cfg, combinedData);

    % Band-pass filter the data
    cfg = [];
    cfg.bpfilter = 'yes';
    cfg.bpfreq = [4 20]; % Band-pass filter range
    cfg.bpfiltord = 4;   % Filter order
    combinedData = ft_preprocessing(cfg, combinedData);
    
    disp('Filtering operations complete on combined data.');
end


%% Define trials and segmentation of the data


previewTrigger = combinedData.trial{1}(225, :);

threshold = (max(previewTrigger) + min(previewTrigger)) / 2;
    
trigger_channels = [225, 226, 227];

TRIALS_DEF = cell(length(conFiles), length(trigger_channels));
TRIALS = cell(length(conFiles), length(trigger_channels));

for fileIdx = 1:length(conFiles)

    chIdx = 1
    cfg = [];
    conFile = fullfile(DATA_FOLDER_PATH, conFiles(fileIdx).name);
    cfg.dataset  = conFile;
    cfg.trialdef.eventvalue = 1; % placeholder for the conditions
    cfg.trialdef.prestim    = 0.5; % 1s before stimulus onset
    cfg.trialdef.poststim   = 1.2; % 1s after stimulus onset
    cfg.trialfun = 'ft_trialfun_general';
    cfg.trialdef.chanindx = trigger_channels(chIdx);
    cfg.trialdef.threshold = threshold;
    cfg.trialdef.eventtype = 'combined_binary_trigger'; % this will be the type of the event if combinebinary = true
    cfg.trialdef.combinebinary = 1;
    cfg.preproc.baselinewindow = [-0.2 0];
    cfg.preproc.demean     = 'yes';
    cfg.readbids = 'no';
    % Define trials for the current channel and dataset
    TRIALS_DEF{fileIdx, chIdx} = ft_definetrial(cfg);

    % Preprocess trials for the current channel and dataset
    TRIALS{fileIdx, chIdx} = ft_preprocessing(TRIALS_DEF{fileIdx, chIdx});
    
end

%% Trials Concantenation

TRIALS_STIM = cell( length(trigger_channels),1);

chIdx = 1
cfg = [];
cfg.readbids = 'no';
TRIALS_STIM{chIdx} = ft_appenddata(cfg, TRIALS{1,chIdx}, TRIALS{2,chIdx}, TRIALS{3, chIdx});

VISUAL_TRIALS = TRIALS_STIM{1}


%% Inspection of trials and rejection of bad trials 


cfg = [];
cfg.method='summary';
cfg.channel = {'AG*'};
cfg.readbids = 'no';
VISUAL_TRIALS_REJ = ft_rejectvisual(cfg, VISUAL_TRIALS);


save VISUAL_TRIALS_REJ VISUAL_TRIALS_REJ


%% Averaging

cfg = [];
cfg.readbids = 'no';
AVG_TRIALS_VISUAL= ft_timelockanalysis(cfg, VISUAL_TRIALS_REJ);



%% Get KIT Sensor layout

kit_layout = create_kit_layout(conFile);

figure('Position', [100, 100, 1000, 800]); % Adjust the width and height (1000 and 800) as needed
ft_plot_layout(kit_layout, 'box', 1);


%% Plotting in space

% for a single trial type, for each channel, average over time the trial
% and plot the average value on the helmet
% You can still see the time behavior when clicking on one sensor or even
% select a bunch of sensors to see the average over those selected sensors

% What should be done in this plot, is select a bunch of occipital lobe
% sensors, click on them to see the averaged ERP, then select the p100 peak
% from the averaged erp then click on it to see the topology at the peak
% time (you should see a strong dipole in the Occipital lobe)

cfg = [];
cfg.xlim = [0.05 1.2];
cfg.colorbar = 'yes';
cfg.layout = kit_layout;
cfg.readbids = 'no';
ft_topoplotER(cfg, AVG_TRIALS_VISUAL);




%% Plot of the averaged VEF

% List of occipital sensors of interest
occipital_sensors = { ...
    'AG162','AG164','AG165','AG184','AG185','AG186','AG187', ...
    'AG195','AG196','AG197','AG199','AG201','AG202'};

% Select those channels from your averaged VEF
cfg = [];
cfg.channel = occipital_sensors;
VISUAL_OCC = ft_selectdata(cfg, AVG_TRIALS_VISUAL);

% Compute the average across those channels
occipital_avg = mean(VISUAL_OCC.avg, 1);

% Plot VEF (amplitude vs time)
figure;
plot(VISUAL_OCC.time, occipital_avg, 'b','LineWidth',1.5);
xlabel('Time (s)');
ylabel('Amplitude (a.u.)');
title('Occipital ERP (averaged over selected sensors)');
grid on;





%% PDF Plot generation

% Find P100 (positive peak) in 80–130 ms
p100_win = [0.080 0.130];             
winMask  = VISUAL_OCC.time >= p100_win(1) & VISUAL_OCC.time <= p100_win(2);

seg = occipital_avg(winMask);
if mean(seg) < 0, seg = -seg; end
[~, idxRel] = max(seg);
idxAll      = find(winMask);
idxPeak     = idxAll(idxRel);

tP100 = VISUAL_OCC.time(idxPeak);     % latency relative to trigger
yP100 = occipital_avg(idxPeak);       % amplitude at peak


% Plot
figure('Color','w','Units','inches','Position',[1 1 9 4]); % wider figure
plot(VISUAL_OCC.time, occipital_avg, 'b','LineWidth',2); hold on;
xline(tP100,'--','LineWidth',1.5);
plot(tP100, yP100, 'ro','MarkerFaceColor','r');

xlabel('Time (s)','FontSize',12,'FontWeight','bold');
ylabel('Occipital lobe gradiometers average amplitude (fT/cm)','FontSize',12,'FontWeight','bold');
title('Visual Evoked Field','FontSize',14,'FontWeight','bold');
grid on; box on; set(gca,'FontSize',12,'LineWidth',1);

% Stretch/zoom the x-axis
xlim([-0.1 0.6]);  % adjust as needed for your epoch

% Label on the x-axis 
yl = ylim;   
text(tP100, yl(1) - 0.05*range(yl), ...   
     sprintf('P100: %.1f ms', tP100*1000), ...
     'FontSize',12,'FontWeight','bold', ...
     'HorizontalAlignment','center','VerticalAlignment','top');

legend({'Occipital mean','P100 time','P100 peak'},'Location','best');

% --- Save PDF ---
print(gcf,'Occipital_ERP_P100_triggerLocked.pdf','-dpdf','-bestfit');



%% Plot heatmap of the p100 latency across a selection of occipital sensors

% Occipital sensors of interest
occipital_sensors = { ...
    'AG162','AG164','AG165','AG184','AG185','AG186','AG187', ...
    'AG195','AG196','AG197','AG199','AG201','AG202'};

occipital_sensors_2 = { ...
    'AG064','AG149','AG154','AG157','AG161','AG170','AG171', ...
    'AG172','AG177','AG178','AG180','AG182','AG193','AG194', ...
    'AG205','AG206','AG207','AG208'};


occipital_sensors= [occipital_sensors, occipital_sensors_2];

% P100 search window (in seconds)
p100_win = [0.080 0.130];   

% Select Occipital lobe sensors
cfg = [];
cfg.channel = occipital_sensors;
VIS_OCC = ft_selectdata(cfg, AVG_TRIALS_VISUAL);   % keeps dimord 'chan_time'

% Find p100 latency

tmask = VIS_OCC.time >= p100_win(1) & VIS_OCC.time <= p100_win(2);
lat_sec = nan(numel(VIS_OCC.label),1);

for ch = 1:numel(VIS_OCC.label)
    [~, idx] = max(VIS_OCC.avg(ch, tmask));   % max in window
    if ~isempty(idx)
        t_idx = find(tmask);
        lat_sec(ch) = VIS_OCC.time(t_idx(idx));  % latency in seconds
    end
end

%Build a “latency map” timelock for topoplot
% Put latencies at a single time point for topographic plotting.
LATMAP = AVG_TRIALS_VISUAL;              % copy structure to keep meta/layout info
LATMAP.time   = 0;                       % single time sample
LATMAP.avg    = nan(size(LATMAP.avg,1), 1);     % chan x time
LATMAP.dimord = 'chan_time';             % ensure correct dim order

% Fill only your occipital channels; leave others NaN so they don’t render
[~, idx_all] = ismember(VIS_OCC.label, LATMAP.label);
LATMAP.avg(idx_all,1) = lat_sec;         % seconds


% Reduced layout with only occipital sensors
cfg_lay = [];
cfg_lay.layout  = kit_layout;
cfg_lay.channel = occipital_sensors;
lay_occ = ft_prepare_layout(cfg_lay, AVG_TRIALS_VISUAL);

cfg = [];
cfg.parameter   = 'avg';
cfg.xlim        = [0 0];
cfg.layout      = lay_occ;            % <-- reduced layout
cfg.comment     = 'no';
cfg.zlim        = p100_win;
cfg.colorbar    = 'yes';
cfg.marker      = 'on';
cfg.channel     = occipital_sensors;  % ensure only these drive the map
cfg.interplimits= 'electrodes';
cfg.interpmethod= 'natural';
cfg.gridscale   = 150;

figure;
ft_topoplotER(cfg, LATMAP);
title(sprintf('Spatial view of P100 latency, a focused view on the Occipital lobe', ...
      p100_win(1)*1e3, p100_win(2)*1e3));

exportgraphics(gca, 'topoplot_latency100.pdf', 'ContentType', 'vector', ...
               'BackgroundColor', 'white');







%% Histogram

T = table(VIS_OCC.label, round(lat_sec*1000,1), 'VariableNames', {'Channel','Latency_ms'});
disp(T);

T_sorted = sortrows(T, 'Latency_ms', 'descend');

figure('Color','w');
barh(T_sorted.Latency_ms, 'FaceColor',[0.2 0.6 0.8]);
set(gca,'YTick',1:height(T_sorted),'YTickLabel',T_sorted.Channel, ...
    'YDir','reverse','FontSize',10);
xlabel('Latency (ms)','FontSize',12,'FontWeight','bold');
ylabel('Channel','FontSize',12,'FontWeight','bold');
title('P100 latency by occipital channel (sorted high→low)','FontSize',14,'FontWeight','bold');
grid on; box on;

% Export to PDF
exportgraphics(gca, 'histogram.pdf', 'ContentType', 'vector', ...
               'BackgroundColor', 'white');


%% Spatial distribution (not so good plot for a report, but good interactively)

cfg = [];
cfg.parameter = 'avg';
cfg.xlim      = [0 0]; 
cfg.layout    = kit_layout;
cfg.comment   = 'no';
cfg.zlim      = [min(lat_sec) max(lat_sec)]; % colorbar across full latency range
cfg.colorbar  = 'yes';
cfg.marker    = 'labels';  % label channels
cfg.highlight = 'on';
cfg.highlightsymbol = '.';
cfg.highlightsize   = 20;
cfg.highlightchannel = occipital_sensors;
figure;
ft_topoplotER(cfg, LATMAP);
title('Spatial distribution of P100 latencies (s)');


%% Plot spatially while labelling the p100 latency

% Get XY positions from layout
lay = ft_prepare_layout([], AVG_TRIALS_VISUAL);
[~, idx_occ] = ismember(VIS_OCC.label, lay.label);

% Scatter with latency as color
figure;
scatter(lay.pos(idx_occ,1), lay.pos(idx_occ,2), 100, lat_sec*1000, 'filled');
colormap(jet); colorbar;
xlabel('X (m)'); ylabel('Y (m)');
title('P100 latency (ms) by occipital sensor position');

% Add vertical padding so lowest points are not on axis
yl = ylim;
ylim([yl(1)-0.1*range(yl), yl(2)+0.05*range(yl)]);

% Export to PDF
exportgraphics(gca, 'latency_vs_spatial.pdf', 'ContentType', 'vector', ...
               'BackgroundColor', 'white');



%% 










