clear all
close all
clc
%% This script processed KIT resting state MEG data (Eyes Closed, EC, and Eyes Open EO)
% from the KIT MEG at NYUAD.
% IT's tested on subject GS (assumes folder GS is current working dir), and uses the .con files
% steps are adapted from  here :https://www.fieldtriptoolbox.org/tutorial/networkanalysis/
% and here https://www.fieldtriptoolbox.org/getting_started/yokogawa/

addpath '/Users/osamaabdullah/Dropbox/matlab_codes_osama/fieldtrip-20240110'


%% concat the 2 .con files (containing Eyes Closed EC, and Eyes Open EO)
ft_defaults
hdr = ft_read_header('GS_01_analysis_01.con');% read header from first file
dat1 = ft_read_data('GS_01_analysis_01.con');% ready data
dat2 = ft_read_data('GS_02_analysis_01.con'); % read data
dat = cat(2,dat1,dat2); %concatenate both files

ft_write_data('GS_concat.vhdr', dat, 'header', hdr);
dat_EC = dat(:,find(dat(225,:)>1));% EO: use trigger channel 225 (note Matlab adds 1 to indexes, which means it's 224 in actuality)
dat_EO  = dat(:,find(dat(226,:)>1));% EC: use trigger channel 226 (note Matlab adds 1 to indexes, which means it's 224 in actuality)
ft_write_data('rsMEG_EC.vhdr', dat_EC, 'header', hdr);%write EC data to desk as vhdr file (4.59 minutes recording, use size(dat_EC,2)*1e-3/60 to check)
ft_write_data('rsMEG_EO.vhdr', dat_EO, 'header', hdr);%Write EO data to desk as vhdr file (5 minutes recording)

%% start with reading EC
cfg            = [];
cfg.dataset    = 'rsMEG_EC.vhdr'; % note that you may need to add the full path to the .ds directory
cfg.continuous = 'yes';
data           = ft_preprocessing(cfg); %this function simly reads the dataset

%Then read EO
cfg            = [];
cfg.dataset    = 'rsMEG_EO.vhdr'; % note that you may need to add the full path to the .ds directory
cfg.continuous = 'yes';
data_EO           = ft_preprocessing(cfg);

%% segment into 2 seconds epochs, demean, trim ends of trials (if needed)
%start with EC
cfg         = [];
cfg.length  = 2;
cfg.overlap = 0.5;
data        = ft_redefinetrial(cfg, data);

% this step is needed to 1) remove the DC-component, and to 2) get rid of a few segments of data at
% the end of the recording
cfg        = [];
cfg.demean = 'yes';
cfg.trials = 1:(numel(data.trial)-6);
data       = ft_preprocessing(cfg, data);

% do same for EO
cfg         = [];
cfg.length  = 2;
cfg.overlap = 0.5;
data_EO        = ft_redefinetrial(cfg, data_EO);

cfg        = [];
cfg.demean = 'yes';
cfg.trials = 1:(numel(data.trial)-6);
data_EO       = ft_preprocessing(cfg, data_EO);

%% create KIT Layout as described here: https://www.fieldtriptoolbox.org/getting_started/yokogawa/
% read the position of the sensors from the data

grad                        = ft_read_sens('GS_01_analysis_01.con'); % this can be inspected with ft_plot_sens(grad)

% prepare the custom channel layout
cfg                         = [];
cfg.grad                    = grad;
layout                      = ft_prepare_layout(cfg);
sel                         = 1:(length(layout.label)-2); % the last two are COMNT and SCALE

% scale & stretch the position of the sensors
layout.pos(sel,:)           = layout.pos(sel,:) * 1.05;
layout.pos(sel,2)           = layout.pos(sel,2) * 1.08 + 0.02;

% load the CTF151 helmet and mask
cfg                         = [];
cfg.layout                  = 'CTF151_helmet';
ctf151                      = ft_prepare_layout(cfg);

% use the CTF151 outlint and mask instead of the circle
layout.outline              = ctf151.outline;
layout.mask                 = ctf151.mask;

% plot the custom layout
figure;
ft_plot_layout(layout, 'box', 1);

%% make a visual inspection and reject bad trials/sensors
%This is EC condition (interactive step)
cfg         = [];
cfg.method  = 'summary';
% cfg.channel = 'MEG';
cfg.layout  = layout;
dataclean   = ft_rejectvisual(cfg, data);

trlind = [];
for i=1:length(dataclean.cfg.artfctdef.summary.artifact)
  badtrials(i) = find(data.sampleinfo(:,1)==dataclean.cfg.artfctdef.summary.artifact(i));
end
disp(badtrials);

%% EO: make a visual inspection and reject bad trials/sensors
%This is for EO condition (interactive step)

cfg         = [];
cfg.method  = 'summary';
% cfg.channel = 'MEG';
cfg.layout  = layout;
dataclean_EO   = ft_rejectvisual(cfg, data_EO);

trlind = [];
for i=1:length(dataclean_EO.cfg.artfctdef.summary.artifact)
  badtrials_EO(i) = find(data.sampleinfo(:,1)==dataclean_EO.cfg.artfctdef.summary.artifact(i));
end
disp(badtrials_EO);

% note ICA isn't done yet

%%
%% compute the power spectrum
% EC
cfg              = [];
cfg.output       = 'pow';
cfg.method       = 'mtmfft';
cfg.taper        = 'dpss';
cfg.tapsmofrq    = 1;
cfg.keeptrials   = 'no';
datapow          = ft_freqanalysis(cfg, dataclean);

% EO
cfg              = [];
cfg.output       = 'pow';
cfg.method       = 'mtmfft';
cfg.taper        = 'dpss';
cfg.tapsmofrq    = 1;
cfg.keeptrials   = 'no';
datapow_EO          = ft_freqanalysis(cfg, dataclean_EO);

    
%% plot the topography and the spectrum
close all
cfg        = [];
cfg.xlim   = [9 11]; %frequency range for alpha
cfg.zlim = [0 4e-27]
cfg.layout = layout;
cfg.colorbar = 'east'
cfg.interactive='no'
ft_topoplotER(cfg, datapow); %plot Power for EO
ft_topoplotER(cfg, datapow_EO);%plot Power for EC

% select a few channels, and plot EC versus EO
cfg         = [];
cfg.channel = {'AG194', 'AG207', 'AG064'}; %a few sensors in occipital lobe
cfg.layout = layout;
cfg.interactive='no'
cfg.xlim   = [0 20];
cfg.showlegend ='yes'
ft_singleplotER(cfg, datapow, datapow_EO);

%% Another way to use native matlab plotting to do similar plot
close all
figure
chansel = 64; % Check channels in the back of the head near occipital area

plot(datapow.freq, datapow.powspctrm(chansel,:), 'r', datapow_EO.freq, datapow_EO.powspctrm(chansel,:), 'b')
legend('EyeClosed', 'EyesOpen')
xlim([0,50])
xlabel('Frequency(Hz)')
ylabel('Power')
