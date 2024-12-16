EEG compatible fMRI System setup
--------------------------------

The MRI lab is equipped with an fMRI compatible EEG system from BrainProducts installed on the 24th of september 2024.

fMRI and EEG data can be collected simultaneously to benefit from the high spatial resolution of fMRI
and the high temporal resolution of EEG.

However, noise is induced from the MRI onto the EEG data due to the gradient artifacts, those must be removed to make the EEG data usable.
Therefore, special analysis pipelines are needed.

- Data storage :ref:`eeg-fmri-data`
- Guideline on designing your EEG-fMRI experiment can be found here :ref:`eeg-fmri-experiment`

Example Experiments EEG-FMRI
============================


.. nbgallery::
    :name: rst-gallery
    :glob:

    ../3-experimentdesign/experiments-eeg-fmri/*

.. toctree::
   :maxdepth: 2
   :glob:

   ../3-experimentdesign/experiments-eeg-fmri/*

Example Processing EEG-FMRI data
================================

.. nbgallery::

   ../3-experimentdesign/experiments-eeg-fmri/1-alpha-blocking
   ../3-experimentdesign/experiments-eeg-fmri/2-finger-tapping


