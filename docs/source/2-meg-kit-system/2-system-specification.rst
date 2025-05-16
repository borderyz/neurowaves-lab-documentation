


MEG-KIT system description
--------------------------
MEG systems are equipped with highly sensitive sensors called SQUIDs. In order for SQUIDS to operate and become sensitive to changes of very small magnetic fields, they need to be brought to a super-conducting state (which suppresses the resistence of the material of the sensor).
To reach the superconducting state, the sensors need to be cooled down to -277 degres Celsius, to achieve this temperature
liquid Helium is needed.
The MEG-KIT system has:

- 208 axial gradiometers used to measure brain activity
- 8 orthogonally-oriented (reference) magnetometers located in the dewar but away from the brain area, used to measure and reduce external noise offline
- 32 open positions, of which we currently use 8 to record stimulus triggers
- 24 channels to record Eye Tracker data directly, auditory signals from our mixer and vocalization information from our optoacoustic fiber-optic microphone

NYUAD MEG system uses liquid helium to keep our SQUID sensors cold (-269°C, -452°F).
If the helium tank leaks, the liquid helium will immediately boil off.
This can cause rapid suffocation and severe frostbite. Handle with care.
Especially don’t shock the dewar.
If you feel anything strange while doing an experiment (i.e., you suspect a helium leak), open the MSR and release
the subject immediately.  Do not leave the room with a subject in the MSR.


MEG-OPM system description
--------------------------




LAB setup
#########

Computers:

- MEG Control PC: used to acquire the MEG data. Do not use the MEG control computer (MEG CONTROL) except for MEG use.

Most importantly, do not install any software. This may cause the system to not work properly.

- stimulus1 pc: used to run the experiment
- stimulus 2 pc: used to put the experiment


Lab setup: Inside the MSR
-------------------------

The MSR is equipped with dimmable 6 halogen light bulbs. Replacement ones are found in the lab incase of needing to change.
Backup battery is located in one of the office spaces connected via yellow cables

- Lights: switch is located by the door
- Dewar: contains liquid helium that submerges SQUID sensors spread across the helmet
- Foam insert headphones: allows participants to get audio stimulus but also audio indications from the operator
- Marker box: connects the head position indicator coils (marked with 5 colours)
- Heater cable: keeps frost and ice from forming on DEWAR; switch is located at the back of the MSR
- Projector: back-projects stimulus onto a screen; remote control is outside the room.
- Amplitude switches: controls the signal strength of the marker coils

.. image:: ../graphic/light-button-image.png
  :alt: Light button setup


.. image:: ../graphic/meg-kit-helmet.png
  :alt: Eyetracker and MEG Helmet


.. image:: ../graphic/meg-kit-amplitude-switches.png
  :alt: KIT amplitude switches




Legacy system (Older system)
----------------------------
The hardware components constituting the (legacy) MEG system:






Vpixx system (New system)
-------------------------

Screen width 65 cm


Electronic lag times between visual stimulus and KIT trigger box
----------------------------------------------------------------

A trigger signal, representing a visual stimulus sent from the Vpixx system to the KIT DAQ computers arrives slightly prior to the visual stimulus from the Vpixx projector due to the electronic circuits.
This result has been deeply investigated by Gayathri Satheesh after performing a photodiode experiment with 1000 trial.
Gayathri used 1000 trials with a 1000 Hz sampling frequency her findings summarises as:

- the mean lag from the is `-8.27852 ms` (the negative means the trigger signal appears on the data 8.27 ms before the subject has seen the visual stimulus)
- the standard deviation of the lag is `0.534153 ms`
- the maximum value was `11ms`
- the minimum value was `8ms`

Therefore, when processing the MEG data that requires 1 millisecond precision, the user can correct the visual stimulus trigger signals by adding an 8 ms shift in the increasing order of time.


MEG-Channels
############

.. note::
    The numbering of channels on the KIT data acquisition software called `MEG 160` starts with index 0, however in MATLAB processing, channels start with index 1.

Channels 0 to 90 and 92 to 207: Gradiometers SQUIDS
Channel 91: Reference magnetometer
Channels 208-223: Magnetometers for reference magnetic field (these are used to denoising and to understand the ambiant magnetic field the environment)

Old configuration (no longer used)
224: Lightsensor 1

225: Lightsensor 2

228: Microphone

229: Event marker bit 0

230: Event marker bit 1

231: Event marker bit 2

New Vpixx configuration: all these channels are free to be used by the experiment designer, [it can be used as a binary signal of 6 bits

224: Event marker bit 0

225: Event marker bit 1

228: Event marker bit 2

229: Event marker bit 3

230: Event marker bit 4

231: Event marker bit 5



One of the channels (In the 80's ) displays a digital signal, this is because one of the sensors are shut off and not used.
Processing pipeline should include this exclusion and not process data from this channel.
(channel name to be identified).

MEG-Racks
#########

The KIT-MEG system has 7 racks

.. image:: ../graphic/KIT-Racks.png
  :alt: MEG Racks System



MSR: Magnetically Shielded Room
###############################

The KIT-MEG is located in an MSR built by `VacuumShmelze <https://www.vacuumschmelze.com/>`_

.. image:: ../graphic/MagneticShieldedRoom/msr1.png
  :alt: MEG Racks System


.. image:: ../graphic/MagneticShieldedRoom/msr2.png
  :alt: MEG Racks System


.. image:: ../graphic/meg-kit-daq.png
  :alt: Data acquisition interface (DAQ) of KIT MEG

- Consists of four PCs working together, interfacing with MEG160 during data acquisition.
- The DAQ units are located in a cabinet labeled “DAQ”.
    - The units are labelled as ‘DAQ0’, ‘DAQ1’, ‘DAQ2’, and ‘DAQ3’.
    - The last time the system battery for DAQ0 was changed on February 4, 2020.
    - Once changed, the BIOS settings might need to be updated. To enter the setting page, strike F2 while the system is booting.
        - Make sure Power Management is Enabled.
        - Make sure Low Power Mode is Disabled.
    - In case one/some of the DAQs won’t boot, try turning it on by manually pressing the power button on the unit.
    - Inform other lab members if things like that happen. Chances are, they have encountered similar/same problems.


MEG160 Software parameters
##########################

`MEG160` is the main software for data acquisition from the KIT-MEG system.

Auto-tuning should be performed prior to any data acquisition.
From the software --> Acquire Measurement
Sensor check can be performed from this window, this ensures that the sensors circuits are correct when a sinusoidal wave is seen on the channel corresponding to that sensor.

The following table shows the default parameters that should be set in the acquiring window

.. csv-table:: MEG160 parameters
   :header-rows: 1
   :file: meg_160_parameters.csv

If we see a strong noise on a specific frequency (for example 50Hz) and would like to filter that, we use the BEF on 50Hz.


Frequently asked questions (FAQ)
################################

- Does locking the SQUID sensors and opening the MSR door can cause harm to the SQUIDs?

When you open the MSR door with SQUIDs locked, the output of some
sensors may become flat. But they are not dead but just faint away due
to the excessive magnetic field fluctuation by swinging the door. The
function of the sensors come back when they are once unlock and lock
again with the door closed.


- How to test trigger channels while opening the MSR?

Avoid locking the sensors, keep the MSR door open and perform all tests with Vpixx response boxes, microphone and other hardware to test your experiment





Contact
#######

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 1

   * - Name
     - Email
     - Number
     - Role
   * - Hadi Zaatiti
     - hz3752@nyu.edu
     - +971 56 275 4921
     - Research Scientist
   * - Osama Abdullah
     - osama.abdullah@nyu.edu
     - NA
     - Senior Scientist
   * - Yoshiaki Adachi
     - adachi@ael.kanazawa-it.ac.jp
     - NA
     - MEG-KIT machine constructor reference
   * - Jun Kawai
     - j-kawai@neptune.kanazawa-it.ac.jp
     - NA
     - MEG-KIT machine constructor reference






References
##########

The following is a list of references for further understanding on MEG systems

* MNE-Python: Overview and tutorials
    * https://mne.tools/stable/auto_tutorials/intro/10_overview.html#sphx-glr-auto-tutorials-intro-10-overview-py

* Marijn van Vliet's "Introduction to MNE-Python"
    * https://mybinder.org/v2/gh/wmvanvliet/neuroscience_tutorials/master?filepath=mne-intro%2Findex.ipynb

* Processing and analysis scripts from various Nellab members/alumni
    * https://github.com/benebular/mne-python-preproc-templates
    * https://github.com/jdirani/MEGmvpa
    * https://github.com/jdirani/mne-preprocessing-template
    * https://github.com/jdirani/meg-analysis-templates
    * https://github.com/grahamflick/Nellab-MRI-Pipeline
    * https://github.com/grahamflick/Tools-for-Combined-MEG-and-Eye-tracking

* Kit2fiff and ICA examples:
    * https://docs.google.com/document/d/1zoxPCngUmyXuKYTNWM8W-_ncTld9okRuYncGXdVUtV0/edit?usp=sharing
    * https://docs.google.com/document/d/1OrVP9ts1gTGB5fhzx8YcK3JKZQgm0HM4Ic3hKtVzHzA/edit?usp=sharing
    * https://docs.google.com/document/d/1X9Tj28ekJ93TubJ52TnrebDvIh8zeXHLp2aMURNV40Y/edit?usp=sharing

* Books:
    * Hansen, Peter & Kringelbach, Morten & Salmelin, Riitta. (2010). MEG: An introduction to methods. 10.1093/acprof:oso/9780195307238.001.0001.
    * Knösche, Thomas & Haueisen, Jens. (2022). EEG/MEG Source Reconstruction, Textbook for Electro-and Magnetoencephalography. 10.1007/978-3-030-74918-7.
    * Hari, MD, PhD, Riitta, and Aina Puce, PhD, MEG-EEG Primer, 1 (New York, 2017; online edn, Oxford Academic, 1 Mar. 2017), accessed 18 July 2024.
    * Tobimatsu, Shozo, and Ryusuke Kakigi, eds. Clinical applications of magnetoencephalography. No. 8564. Springer Japan, 2016.