Finger-tapping experiment
=========================


In this experiment, the participant will tap each finger in a random order for 12 seconds continuously.
This is repeated 5 times. The block duration is 12 seconds.


.. dropdown:: Finger Tapping task code

    .. literalinclude:: ../../../../experiments/EEG-FMRI/finger-tapping/main.m
      :language: matlab



Variant version that needs to be designed
-----------------------------------------

The above version does not have single same finger type trials, but rather one type of trial for all fingers.
To benefit from EEG's temporal resolution, the experiment can be redesigned as the following:

- each block involves a first trigger indicating the start of the block and then the participant is asked to tap a finger and then wait for a moment (so that the Hemodynamic response has enough time to show)
- the randomness of the finger can be kept as it is, but we must ensure that the participant is tapping a single finger per trigger signal

