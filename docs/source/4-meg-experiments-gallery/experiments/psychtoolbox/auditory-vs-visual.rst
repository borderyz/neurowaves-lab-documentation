.. _auditory-vs-visual-vs-motor:

Experiment example: Auditory vs Visual vs Motor stimulus
--------------------------------------------------------

Author: Hadi Zaatiti <hadi.zaatiti@nyu.edu>

Description
^^^^^^^^^^^

In this experiment implemented using the Psychtoolbox framework, a random sequence of three stimulus is performed:

- an auditory stimulus with a 200 Hz audio of 500 ms duration
- a visual stimulus with a full field white flash appearing on screen

    .. figure:: figures/visual_stimulus.pdf
        :alt: Visual Stimulus
        :width: 80%

        Visual stimulus: full field flash black to white

- a motor stimulus requiring a button press

Every stimulis occurrence  is spaced from the next one by an Inter-Stimulus Interval (ISI) randomly picked from 2 to 2.5 seconds (with 100 ms step size)



Code access
^^^^^^^^^^^

:github-file:`Auditory vs Visual vs Motor Experiment Code <experiments/psychtoolbox/auditory-vs-visual>`

:github-file:`Auditory vs Visual vs Motor Processing Pipeline Code <pipeline/field_trip_pipelines/audio-visual-motor>`

Data access
^^^^^^^^^^^

Acquired datasets are stored safely on NYU Box under `audio-visual-motor`.

`MEG Data Directory <https://nyu.box.com/v/meg-datafiles>`_

Analysis results
^^^^^^^^^^^^^^^^

`Auditory vs Visual vs Motor Pipeline Notebook <../../../6-meg-pipeline-gallery/notebooks/fieldtrip/fieldtrip_kit_audio_visual_motor.ipynb>`_

