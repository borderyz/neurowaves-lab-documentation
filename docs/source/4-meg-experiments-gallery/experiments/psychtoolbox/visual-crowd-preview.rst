.. _visual-crowd-preview:

Experiment example: Visual Crowd Preview
----------------------------------------

Author: Maitha AlShaali <ma6895@nyu.edu>, Tasnim Ezzedin <te2207@nyu.edu>


Description
^^^^^^^^^^^



"This experiment examines the crowding (the spacing between the letters within each word) and preview effects in the Arabic language,
utilizing three distinct crowding values: 0, -75, and -125.
Within the experiment, these values are represented as follows: 1 for -125, 2 for -75, and 3 for 0.
These values are used in the naming of the images as well as in the final output of the .mat file.
Within the .mat file, a column appears containing the number corresponding to the level of crowding (1, 2, or 3).
For example, SET1_conn_0_cwdg_1_1.jpg, SET1_conn_0_cwdg_2_1.jpg, etc.
Due to the nature of the arabic language being written in cursive, it has a varity of connections between letters.
In the naming of the images, the 'conn' refers to the connectivity of the letters. For example, if a word has only two letters that
are connected and a crowding level of 1 (i.e. -125) the name would be SET1_conn_2_cwdg_1_1.jpg.
The stimuli are made of 300 different arabic words. SET1 has a different combination of crowding values assigned to the words than SET2,
however, both have the same words.

In this paradigm, participants are instructed to focus on a fixation point on the screen. Words will be presented either to the left or right of the fixation point, and participants will be required to look at the presented word when cued by the fixation point turning green. When a saccade is detected, the target word is displayed.
The stimuli were presented as either valid or invalid, with the invalid stimulus being a flipped version of the valid one.
After that, the participant has to decide weather or not the word displayed is the same your they saw during the trial by answering the question 'Is this the last word you saw?'.
The study employs magnetoencephalography (MEG) and eye-tracking techniques to record brain activity.


Total number of trials = 320, same for every participant.


Stimulus Data
^^^^^^^^^^^^^



Trigger design
^^^^^^^^^^^^^^

This experiment uses the single-channel trigger mode design.

The trigger channels in MEG are as follows:

trigger channel 224: beginning of the overall experiment.
trigger channel 225: the pulse on this channel occurs at the moment when a good fixation point happens, signalling the start of the trial (the number of pulses here should be equal to the total number of trials).
trigger channel 226: display of the preview image for condition: Crowding level 1 (Normal)
trigger channel 227: display of the preview image for condition: Crowding level 2 (Narrow)
trigger channel 228: display of the preview image for condition:  Crowding level 3 (Extra Narrow)
trigger channel 229: display of the preview image for condition: Crowding level 4 (Flipped)
trigger channel 230: display of the target image for condition:  Crowding level 0 (Clean images)
trigger channel 231: display of the "Question Image", the pulse happens exactly when the question showed up on the screen, before the participant responded

Each trigger appears only once in each trial, except trigger channel 225, which appears each time the fixation point is presented. For example, if a fixation is not detected, channels 225 is triggered again until a fixation is detected.

The .mat file outputs a table with relevant information about the trials, such as the crowding level of each word that was displayed, weather or not it was valid or invalid, number of connections of the letters, question answers, etc."





Code access
^^^^^^^^^^^

:github-file:`Visual Crowd Preview <experiments/psychtoolbox/visual_crowding_preview>`


Data access
^^^^^^^^^^^

Acquired datasets are stored safely on NYU Box under `visual_crowding_preview`.

`MEG Data Directory <https://nyu.box.com/v/meg-datafiles>`_



