EEG compatible fMRI System setup
--------------------------------

The MRI lab is equipped with an fMRI compatible EEG system from BrainProducts installed on the 24th of september 2024.

fMRI and EEG data can be collected simultaneously to benefit from the high spatial resolution of fMRI
and the high temporal resolution of EEG.

However, noise is induced from the MRI onto the EEG data due to the gradient artifacts, those must be removed to make the EEG data usable.
Therefore, special analysis pipelines are needed.

- Operational Protocol :ref:`brainamp_mr_plus_sop`
- Data storage :ref:`eeg-fmri-data`
- Guideline on designing your EEG-fMRI experiment can be found here :ref:`eeg-fmri-experiment`

Example Experiments EEG-FMRI
============================


.. nbgallery::
    :name: rst-gallery
    :glob:

    ../3-experimentdesign/experiments-eeg-fmri/*


Pipelines Processing EEG-FMRI data
==================================

.. nbgallery::
    :glob:

    ../5-pipeline/notebooks/eeg-fmri/*


