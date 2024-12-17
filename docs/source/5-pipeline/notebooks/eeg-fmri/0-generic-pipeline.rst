Generic pipeline
================

Different modalities for processing EEG-fMRI data exists in the literature:

- assymetrical approach where one modality (EEG or fMRI) constrains the other modality
    - mainly the EEG data constrains temporally the fMRI data
    - or the fMRI data constrains spatially the EEG data
- symetrical approach where both modalities constrain each other

The assymetrical approach is more popular in the literature.



Required Data
-------------

- fMRI data consists of
    - times series of Bold signals mapped to a geometric space (either to each voxel, or to vertices of a surface)
- EEG data consists of
    - A .eeg file: raw data from the electrodes (time series)
    - A .vhdr or .xhdr file: a header containing metadata on parameters and sensors, layout of coordinates of sensors
    - A .xmrk file: contains markers with their time (can be opened in a text file)
- for source reconstruction
    - EEG/FMRI requires a T1 image (the subject should not have the EEG cap while getting the T1)


Example of such datasets are present on NYU-BOX.
Demo dataset has been provided by BP and are available on the recording computer:

The generic pipeline for EEG-fMRI data processing involves the following steps, detailed below

.. contents:: Table of Contents
   :local:
   :depth: 2

.. admonition:: References

    1. Cilia Jaeger (2024). *BP Academy Webinar Recording: Combined EEG and fMRI data analysis*.
        - Youtube webinar available at `https://www.youtube.com/watch?v=vGQVeCn53ys <https://www.youtube.com/watch?v=vGQVeCn53ys>`_



Preprocessing of the EEG data
-----------------------------

Preprocessing of the EEG data involves multiple step. We will be using BrainVision Analyzer.


ECG Removal
~~~~~~~~~~~

- The subtraction method can work better than ICA, use the substraction method to remove ECG signals

Steps for noise removal and pre-processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Gradient artifact correction:
  - Always remove the gradient artifacts first.
  - ECG with gradient artifacts can be saturated sometimes, which means that the ECG sensor should be moved around.
  - MRI artifact correction: then pick use markers, then R128, making sure the correction is only during these triggers and not for the rest.
  - Then Next.
  - Artifact Type is always **Continuous** (interleaved was an old thing when MRI was collected for a period of time and then EEG for another period of time).
  - Enable **Baseline correction for average** (compute baseline over the whole artifact).
  - Use **sliding average calculation** to account for changes in gradient artifacts over time.
  - Do not select **Common use of all channels** for bad intervals and correlation.
  - Then next: select all EEG channels (only time we don’t use all channels is if we are measuring a specific thing).
  - Then next: deselect downsampling (we can do this later).
  - How to store data Select **store corrected data** in a cached file.

- ECG signals correction after gradient artifact cleaning:
  - Also use a **sliding average subtraction** approach (Not ICA), use ICA if there is a residual.
  - We do not have markers on the peaks (this is needed for the subtraction method).
  - We need to add **R peaks** (peaks on the ECG signals).
  - After the gradient artifact correction, some high-frequency noise stays in the ECG channel during MRI acquisition.
  - Apply **High Cutoff Frequency**: go to **Transformations**, then **IIR filter**, disable the Low cutoff and High cutoff of all channels, then select only the ECG channel and apply a high cutoff (15 Hz), then apply filter.
  - Then **Transformations**, **Special Signal Processing**, then **CB correction**.
  - Choose the **ECG channel** (if it's a clear heartbeat, if not use another EEG channel that shows a clearer one than ECG).
  - Go through the manual check if the automatic analyzer skipped some R peaks.
  - After selecting all the R peaks (which should be marked in Green), click **Finish**.
  - Then the R peaks should appear on the peaks as R.
  - Go to **Special Signal Processing**, select **CB**, then select **Use Markers**, then select **R markers**.
  - Then next, and use the whole data to compute the time delay. The total number of pulses is the sliding signal window. Empirically, we use 21 as the parameters.
  - Select all EEG channels except for CWL and the ECG channel.

- Carbon Wired Loops (CWL), accounts for movement correction:
  - Change sampling rate: we need to downsample and then apply the **CWL regression**.

We can automate the process by saving all the analysis steps.


Helium Pump Noise:
~~~~~~~~~~~~~~~~~~
- Components around the 50Hz frequency should appear in all channels.
- The helium pumps cannot be turned off during an experiment.

Pre-processing steps should involve:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Inspecting the static field data.
2. Gradient-artifact correction.
3. ECG correction or CWL regression (Cardioballistic artifacts).
4. Classic EEG analysis.




Pre-processing of the fMRI data
-------------------------------

Author: Putti Wen


.. literalinclude:: ../../../../pipeline/eeg-fmri-pipelines/generic-pipeline_fmri_preprocessing/main.m
   :language: matlab
   :caption: Preprocessing Script for EEG-fMRI Data
   :linenos:




Other possible processing steps

- draining vein effect correction (linear offset or CBV scaling or spatial deconvolution)
- Vascular Space Occupancy combined with EEG
- Nordic denoising, with time there is more heating that causes higher amplitudes so this requires denoising



Preparation of the forward/head model
-------------------------------------




Perform fMRI-informed EEG source reconstruction
-----------------------------------------------

- Coregistration requires computing the transformation, use the “layout” file that should help you match the electrodes with the headface
- Some technique uses the ultrasound protocol to locate the electrode and get a geometrical representation of the electrodes




Other methods
-------------

- Typical fMRI uses the GLM fitting, with EEG data it is possible to add regressors
    - Proposed method is to take the variability of the EEG data and inject that as regressor into the GLM (variability can be each trial variability or spectral feature such as correlation with a band, or temporal feature ERP peak … this will depend on your paradigm)
    - The non-stimulus activity can be used to correlate baselines (from eeg and fmri) together