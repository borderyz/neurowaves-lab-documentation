.. _resting_state_exp:

Experiments example (Psychtoolbox): Resting state
-------------------------------------------------

Author: Hadi Zaatiti <hadi.zaatiti@nyu.edu>

Description
^^^^^^^^^^^

Resting state experiment implemented using the Psychtoolbox framework.

The participant is asked to either close or open their eyes for a specified duration.
The following triggers (marker events) are sent from the 'Datapixx3' to the KIT-MEG when the eyes closed or open period starts:
- on channel 224 (eyes closed)
- on channel 225 (eyes open)

In MNE reference:
- Channel 224 in KIT indexing corresponds to `MISC 001`
- Channel 225 in KIT indexing corresponds to `MISC 002`


Code access
^^^^^^^^^^^

:github-file:`Resting State Eyes Closed <experiments/psychtoolbox/restingstate/resting_state_meg_EYES_CLOSED.m>`

:github-file:`Resting State Eyes Open <experiments/psychtoolbox/restingstate/resting_state_meg_EYES_OPEN.m>`

Data access
^^^^^^^^^^^

Acquired datasets are stored safely on NYU Box under `resting-state`.

`MEG Data Directory <https://nyu.box.com/v/meg-datafiles>`_


Analysis results
^^^^^^^^^^^^^^^^

The notebook provides analysis results after running the experiment on a participant (Sub-01).

`Resting State Pipeline Notebook <../../../6-meg-pipeline-gallery/notebooks/mne/resting_state_pipeline.ipynb>`_