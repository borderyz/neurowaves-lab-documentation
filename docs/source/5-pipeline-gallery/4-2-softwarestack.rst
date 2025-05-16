Software stack and installation
===============================

The folowing software/library are available MEG/EEG data analysis:

* BESA
* MNE Python library
* FieldTrip

Sample pipelines are provided for each one of them


BESA installation
=================

Download BESA from `https://www.besa.de/ <https://www.besa.de/>`_

The BESA license available at NYUAD-MEG lab will be soon hosted on a server, and instructions to use it will be made shortly available on this page.


MNE Python library installation
===============================

Follow instructions here `MNE Install <https://mne.tools/stable/install/index.html>`_
Ideally, choose the standalone installer it usually has the complete suite.

We recommend to install MNE as a standalone installer.

The data of the MNE environment will be under ``C:\ProgramData\mne-python\1.x.y_z``

You can setup Pycharm to use this environment as a Python environment for your pipeline project.

The configuration file for setting ``SUBJECTS_DIR``, the directory to the data of your subject, can be set in:
``C:\Users\user_name\.mne\mne-python.json``



Network setting up
==================
To connect to the internet via ethernet on network, make sure the MAC address of your ethernet interface is registered:
Got to `computer-registration.abudhabi.nyu.edu <https://computer-registration.abudhabi.nyu.edu>`_ and register the MAC address found in network settings, properties of the interface, replace the dash - with a column :


Installing freesurfer on windows (For source localization with MNE)
===================================================================
If you want to do source localization in MNE, you will need to install freesurfer.

If you are under windows, configure WSL2 on windows. You can then access the files of the ubuntu distribution by typing ``\\wsl$\Ubuntu`` in the file explorer in windows.

Install freesurfer following their documentation page. https://surfer.nmr.mgh.harvard.edu/fswiki/FS7_wsl_ubuntu


FieldTrip
=========

First download fieldtrip from here `https://www.fieldtriptoolbox.org/download/ <https://www.fieldtriptoolbox.org/download/>`_
Then, install fieldtrip folowing `https://www.fieldtriptoolbox.org/download/ <https://www.fieldtriptoolbox.org/download/>`_


BESA Software
=============

The following steps are primary to process MEG data using the BESA MRI and BESA Research suite

You have MRI data of your participant
-------------------------------------

Open BESA MRI, start a new segmentation project, check all the segmentation options (especially BEM and FEM), pick the landmarks for segmentation
and start the process. Once done, BESA will save the segmentation, BEM, FEM model outputs.

In BESA MRI, start a new coregistration project.

Open BESA Research, load your MEG data from a .fif format.


AC choosing: start with sagittal, pick the last end of the white matter fibers
then go to coronal and pick the point where the white matter fibers are linked from left to right hemisphere(above the black point)


Set the nasion on the surface of the skin, because the digitization is performed on the top of the ksin


Connectivity analysis:
SOme regions can be activated at the same time
However, in other situations, one region fires and then triggers other regions.

It is an unsolved question to identify which begins the activity

Source montage (add to glossary): is definition of the sources

Epilepsy:can be one region activated or many other regions activating at the same time
another kind of epilepsy where all the brain gets activated
another kind, right hemisphere then left hemisphere




MNe kit2fiff to get a fif from .con and .mrk
then open the .fif in BESA

To quickly inspect the data, and have a view of the field at a specific time, on a template head, within the sensor layout loaded from the .fif
you can enable in Options -> Mapping -> Enable direct mapping by double clicking
Then double click at a specific time and see the field on the template head

Radial activity within the brain cannot be picked up except for partially by the SQUIDS
There is examples folder in BESA, with different datasets

Algorithms for source localization
sLoreta, Loreta (named Clara in BESA, which is recursively applied), dspm
Equal end current dipole (good when the phenomona is triggered by one area of the brain and not multiple areas at once)
EQUILAVENT Current Dipole
Beamformer (

Issues to resolve:
- number of digitized head points, and alignment during coregistration
- triggers in oddball experiment how to pick them up by Besa software

Open file and clear DB(to erase previous settings)

- Identify the metrics used in computing the artifact rejection heatmap (see if we can have different metrics of these)

In artifact rejection:
Low signal is to cut flat signals (that are saturated with noise)



Question about PCA components time axis

Question: Save solution works for dipoles only but not for CLARA
Question: Saving activity coregistered with MRI-T1


If source analysis crashes using CLARA, reduce the voxel size


Source localization steps:

after coregistration, make sure in BESA Research, File, Coregistration, the coreg file is checked
define your trials and average them, then pick a window, right click -> source analysis
Pick BEM or FEM as conducting model. (the spherical model is only a template and is not used for source localization)
choose a window on the left top window then pick Clara or another algorithm


Check how the USB license can be hosted on a server


Agenda:
- global presentation on besa
- beamformer
- OPM trigger processing and coregistration

We can find the coregistration files in C:\Users\Public\Documents\BESA MRI\Projects\AS-oddball-task_19010101\

After source localization, you can use up and down arrows to change the sensitivity of the heatmap



SESAME uses bayesian statistics to estimate the number of sources, cortical loreta

Cortical Loreta = Loreta not on MRI but the reconstructed brain model (inflated or not inflated)

Batch-processing is the automation workflow in BESA to run similar steps multiple times

DONETODO:MATLAB import from BESA
DONETODO: seeding dipole


Clara operation: goes through each time point and does the inverse (for each time point) then show the average of the time region of activation

When to use Clara or Beamformer or SESAME?
Clinically: Clara (distributed model, each voxel have an activity) and Dipole fitting are approved clinically
For MEG: beamformer (coz MEG has better spatial separation than EEG)
SESAME (uses a dipole model, and does not assume that each voxel has an activity):
DONETODO: Clara followed by SESAME, CLARA can show you regions of activity, and then SESAME can use dipoles on these regions as a prior to its operation
a CLARA followed by SESAME should give a more accurate pointy result, you need to click Weight By Image (to use output of clara as input to sesame [prior])


PCA: The PCA can indicate how many sources you need, if you have 3 high activity components then you need 3 dipoles

right click a PCA component, and add to solution, this will show you where the dipole is located for that component


In Source Analysis: Residual to see what data is not covered, you can uncheck the data and keep the residual and then fit again just for the residual part

There is something called confidence level to see how the dipole explains the data (but this is nnot a validation)

In source analysis, never forget to set the baseline properly on areas where there is not much activity, prior to the stimulus




TODO: Frequency analysis difference eyes close and open, in sensor space and in source space


TODO: OPM Coregistration, how are the pink points and the sensors connected

Export NII with acivity source localized
solution 1: with MIND it is a solution
solution 2: .vmr file, BrainVoyager, neuroelf (in matlab)
in Neuro ELFis free to import VMR, import the MRI from a .VMR file, then import analys to VMR

solution3: export after source analysis choose ACPC.nii (this setting only appears when the coregistration is set)

Solution4: longer term solution, find the transformation parameters in the project file and use them to get to ACPC coordinates, apply it on the dicom. then the exported.nii (In ACPC) activity image should match wh


OPM trigger solution:

Show code amplitude value

TODO: Send FIeldline a question about the fiducials in the .fif that has been automatically added without digitized head


Beamformer not working in oddball task because the noise level is high, (the artifacts is ok)
The result can be better choosing a baseline with lower noise (-300 -200)

REgularization parameter for all methods is very important, the higher the regulalirzation parameter
In beamerformer oddball, set regul parameter to 0.01 (best value), parameter accessed from Image Settings

Frequency-time analysis is not possible today with sloreta, clara,
a workaround is to apply HPF and LPF filters o the region of interest then apply time-lock analysis with clara/loreta

Agenda for today:

- finish resting state
- do frequency analysis on time series of oddball after CLARA

==> This is not directly possible, because the orientations of the sources can be very different, in this case, the oscillation effect can double the frequency power


A directory of BESA:

- .pdg = paradigm file (triggers, conditions, groups)
- .fsg = averaged trials (trials and averages)


TODO(Problem): Send to BESA trigger on MISC_002 one is up and one is down, both should be up


IN resting state:
- after doing an FFT, you can define your own band that your looking for in Options Band Name and Width, (you must be in SRC first)
- we did beamformer in the time domain, then defined a source on the maxima obtained. then we saw the estimated time series on the maxima



BATCH creation to automate a pipeline:
Shift+R or process --> Batch Processing
Pause: it stops after a step in oredr for tghe user to check for things or take a screenshot, then it continues