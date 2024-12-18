Alpha-blocking pipeline
=======================

.. contents:: Table of Contents
   :depth: 3
   :local:


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

    .. figure:: 2-alpha-blocking-pipeline-figures/img_2.png
       :align: center
       :alt: Description of the image
       :width: 50%

       Importing the two alpha-blocking datasets into BrainVision Analyzer

EEG data triggers and sanity check
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The EEG data from an EEG/fMRI experiment should have the following trigger signals

- `Sync On` of marker type `Sync Status` is a marker repeated every period of time ensuring that the MRI clock and EEG system are in sync
- `T 1_off` of marker type `Toggle` is a marker

    .. figure:: 0-generic-pipeline-figures/fig1.png
       :align: center
       :alt: Description of the image
       :width: 50%

       One TR (repetition time) corresponds to T 1_off - T 1_on.

- Paradigm-based triggers scripted from your experiment, for the alpha-blocking experiment we programmed the `S1` marker to appear
- Perform a sanity check on the number of markers (trigger signals)

    .. figure:: 2-alpha-blocking-pipeline-figures/img.png
       :align: center
       :alt: Description of the image
       :width: 50%

       Right click your Raw data in primary view then `Markers` to do a sanity check on the number of markers.

- We had programmed 25 blocks per experiment starting with eyes open as first block
- A .csv produced from the MATLAB script holds the sequence and time of each block for sanity check

    .. figure:: 2-alpha-blocking-pipeline-figures/img_1.png
       :align: center
       :alt: Description of the image
       :width: 50%

       Under EEG-FMRI\Data\resting-state\sub-0665\matlab


- Once we checked that:
    - the number of triggers of each type is correct
    - the sync on is appearing throughout the acquisition
- we can then procceed with the analysis


Renaming the toggle markers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The markers for the TR (Repetition Time) in NYUAD's setting will be called T 1_on and T 1_off, we need to rename them all to T1 in order to check for any missed TR markers.

- Under `Transformations` pick `Edit markers`
- Put the following settings

    .. figure:: 2-alpha-blocking-pipeline-figures/img_3.png
       :align: center
       :alt: Description of the image
       :width: 50%

       Edit markers transformations all toggle marker will be called T1.

- Press `Finish`, check that all toggle markers are now called `T1`


Repetition Time (TR) Sanity Check
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Make sure you have all the BrainProducts Solutions installed (these are separate from the software itself)
- Go to Solutions -> Views -> Marker Timing -> Set parameters as following

    .. figure:: 2-alpha-blocking-pipeline-figures/img_4.png
       :align: center
       :alt: Description of the image
       :width: 50%

       Compute timing between consecutive T1 markers to ensure they correspond to the TR.

    .. figure:: 2-alpha-blocking-pipeline-figures/img_5.png
       :align: center
       :alt: Description of the image
       :width: 50%

       The used TR of 750ms corresponds to the max and min different of successive T1's.

- The result is displayed as an extra step in the processing tree and is correct, the used TR was indeed of 750ms during the whole experiment
    - Sanity check is therefore checked

    .. hint::

        You can reproduce the same analysis steps for another dataset by clicking and dragging the step node in the `history tree` onto the other dataset.
        The history files have an `.ehtp` extension.
        To load the files in click on History Template → Open → select history tree file → drag and drop history tree onto data node of interest.

Gradient artifact correction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Observe that when the gradient coils are activated a noise pattern is induced, it is an artifact that requires removal

    .. figure:: 2-alpha-blocking-pipeline-figures/img_6.png
       :align: center
       :alt: Description of the image
       :width: 50%

       EEG data prior and after gradient coil activation.



