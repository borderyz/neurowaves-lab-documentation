%% Defining trials based on a given type of triggers (in event.value)


% First we need to code a function that can take the type of trigger and
% the event type = 'trigger


% The function language_study_trial_func needs to have in the provided cfg,
% the event structure.

cfg = [];
cfg.dataset              = 'merged_egyptian_sub004.vhdr';
cfg.trialfun             = 'language_study_trial_func';     % it will call your function and pass the cfg
cfg.trialdef.eventtype  = 'trigger';
cfg.trialdef.eventvalue = [22 129];           % read all conditions at once
cfg.trialdef.prestim    = 1; % in seconds
cfg.trialdef.poststim   = 2; % in seconds

cfg = ft_definetrial(cfg);

cfg.channel = {'AG*'}; % Make sure this is correct by looking at the notebooks
dataMytrialfun = ft_preprocessing(cfg);
% The function language_study_trial_func needs to have in the provided cfg,
% the event structure.

cfg = [];
cfg.dataset              = 'merged_egyptian_sub004.vhdr';
cfg.trialfun             = 'language_study_trial_func';     % it will call your function and pass the cfg
cfg.trialdef.eventtype  = 'trigger';
cfg.trialdef.eventvalue = [22 129];           % read all conditions at once
cfg.trialdef.prestim    = 1; % in seconds
cfg.trialdef.poststim   = 2; % in seconds

cfg = ft_definetrial(cfg);

cfg.channel = {'AG*'}; % Make sure this is correct by looking at the notebooks
dataMytrialfun = ft_preprocessing(cfg);