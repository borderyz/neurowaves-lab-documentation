Experiment example 6: The oddball paradigm
------------------------------------------

The oddball paradigm is an experimental design used within psychology research.
The oddball paradigm relies on the brain's sensitivity to rare deviant stimuli presented
pseudo-randomly in a series of repeated standard stimuli. The oddball paradigm has a wide
selection of stimulus types, including stimuli such as sound duration, frequency, intensity,
phonetic features, complex music, or speech sequences.
The reaction of the participant to this "oddball" stimulus is recorded.

In the classic Oddball paradigm, two types of stimuli affecting the same sensory
channel are presented randomly within an experiment, with a significant difference
in the probability of occurrence. The more frequently occurring stimulus is called
the standard stimulus, which serves as the background of the entire experiment;
the less frequent and sporadic stimulus is known as the deviant stimulus.
Since the physical properties of the two stimuli are very similar, the deviant
stimulus appears as a deviation from the frequently occurring standard stimulus,
hence the names "standard stimulus" and "deviant stimulus." In the classic Oddball
paradigm, the deviant stimulus typically has an occurrence probability of about 20%,
while the standard stimulus has a probability of about 80%.

The experiment is adapted from `sijiazhao` code, the original one is `found here. <https://github.com/sijiazhao/oddball_eyetracking>`_


The code below is the main script, to make it work you will need to download the full directory containing the sound files as well from
`Download oddball full directory <https://github.com/hzaatiti-NYU/meg-pipeline/tree/main/experiments/psychtoolbox/sound/oddball>`_

.. literalinclude:: ../../../../experiments/psychtoolbox/sound/oddball/run_oddball_KIT.m
  :language: matlab

