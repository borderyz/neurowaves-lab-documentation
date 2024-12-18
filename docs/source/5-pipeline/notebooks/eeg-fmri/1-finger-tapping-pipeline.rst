Finger tapping pipeline
=======================

Familiarise yourself with the generic pipeline first.

Preprocess EEG Data
-------------------

Setup your workspace
~~~~~~~~~~~~~~~~~~~~

- Create three folders in a directory, name them as follow
    - export: this will contain exported data from analysis pipeline
    - history: this will contain all processing steps
    - raw: put your raw .eeg, .vhdr, .vmrk here

- Open BrainVision Analyzer
- Press New then set the Raw, History and Export to the created folders above
    - your workspace is saved in a .wksp
- You should now see the datasets as folders in your Primary view



EEG data triggers
~~~~~~~~~~~~~~~~~

The EEG data from an EEG/fMRI experiment should have the following trigger signals

- `Sync On` of marker type `Sync Status` is a marker repeated every period of time ensuring that the MRI clock and EEG system are in sync
- `T 1_off` of marker type `Toggle` is a marker

    .. figure:: 0-generic-pipeline-figures/fig1.png
       :align: center
       :alt: Description of the image
       :width: 50%

       One TR (repetition time) corresponds to T 1_off - T 1_on.

- Paradigm-based triggers scripted from your experiment, for the finger-tapping experiment we programmed the `S1` marker to appear



Preprocess fMRI Data
--------------------


