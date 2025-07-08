--------------------
Operational Protocol
--------------------

The Operational Protocol of OPM will be fully ready during 2025.

There are three ways to coregister with OPM:

- First method:
    - laser scan the participants head and stylus points, before placing the participant in the OPM helmet
    - place participant in helmet, then laser scan the fiducials on the face again
    - laser scan the 8 points on the OPM helmet
    - we now can compute the rigid-body transformation of the head laser scan with restpect to the 8 points of the OPM helmet based on the fiducials laser points
    - computing this matrix, allows us to coregister the laser headscan with the OPM helmet
    - this method assumes that the participant is not moving their head within the OPM helmet
    - advantages: HPI coils are not needed

- Second method:
    - laser scan the participant head and stylus points
    - then place the participant in the OPM-helmet
    - then place HPI coils on known stylus points (must standardize those locations)
    - In this case, a script must be ran at beginning and end of the experiment to energize the coils with sinusoidal waves of known frequencies (follow up with fieldtrip tutorial section 2)

- Third method:
    - laser scan the participant, laser scan the fiducials
    - place participant in helmet, laser scan everything (i.e. face and helmet together)
    - mark fiducials
    - Coregister both set of fiducial