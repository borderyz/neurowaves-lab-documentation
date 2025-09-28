.. _checklist:

---------------------
MEG Session Checklist
---------------------

**Step by step MEG Session checklist**

`Author:` Maitha Al Shaali `ma6895@nyu.edu <ma6895@nyu.edu>`_

Scheduling A Session
^^^^^^^^^^^^^^^^^^^^

.. checklist::

    - [ ] Confirm the session date and time with the participant using your preferred method (e.g., Sona, Calendly), and cross-check CTPSS to avoid conflicts with other MEG sessions.
    - [ ] Create and send a Google Calendar invite to the participant.
    - [ ] Book the session on CTPSS, including a ~30-minute buffer before and after. Do not include the participant in this booking.
    - [ ] Email the participant the study requirements, consent form, and any pre-experiment surveys (if applicable).

Before Participant Arrival
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. checklist::

    - [ ] Disinfect surfaces (bed, helmet), HPI-coils (gently), and earphones using disinfectant wipes.
    - [ ] Assemble bedsheet, new earphone covers, and pillow cover.
    - [ ] Cut 15 pieces of tape (~3-inches in length) for attaching HPI coils.
    - [ ] Switch on EyeLink and Eye-tracking computer (if applicable).
    - [ ] Test speakers, microphones, response boxes, and screen inside Magnetically Shielded Room (MSR).
    - [ ] Call security to request switching off all devices until the session is completed.
    - If the participant wears hijab:
        - [ ] Request all male researchers to leave the lab for the session duration.
        - [ ] Put up the “ladies only” sign on the outside of the lab door.
        - [ ] Set up the divider near the door.

Participant Preparation
^^^^^^^^^^^^^^^^^^^^^^^

.. checklist::

    - [ ] Welcome the participant to the lab and confirm their name and/or NetID.
    - [ ] Confirm or remind the participant about the consent form and any pre-experiment surveys (if applicable).
    - [ ] Briefly explain the process and requirements for their participation.
    - [ ] Confirm that the participant does not have any non-removable metal on their body.
    - [ ] If the participant wears glasses, ask for their prescription and provide MEG-compatible glasses.
    - [ ] Ask the participant to change into the scrubs provided and remove all metals (smart watches, jewelry, hair accessories, etc.).
    - [ ] Set all devices to Airplane Mode (phones, smart watches).
    - [ ] Briefly explain the laser scan process.
    - [ ] Equip the participant with a tight-fitting cap to smooth their head shape.
    - [ ] Mark the participant's head with a felt-tip marker.
    - [ ] Ask the participant to close their eyes and remain still during the laser scan.
    - [ ] Conduct the laser scan (sweeps and points).
    - [ ] Guide the participant to the MSR.
    - [ ] Explain the process of attaching HPI coils and the study setup (bed, screen, eye-tracker).
    - [ ] Attach the coils to the participant’s head using the guide on the wall and the cable labels.
    - [ ] Help the participant lie down carefully on the bed, ensuring the coils do not detach or shift.
    - [ ] Equip the participant with one earphone.
    - [ ] Provide the participant with the leg pillow and blanket for comfort.

MSR Preparation
^^^^^^^^^^^^^^^

.. checklist::

    - [ ] Ensure that the Marker Box is switched on.
    - [ ] Switch on the ProPixx screen from the stimulus computer.
    - [ ] Test the speaker and microphone by asking the participant if they are able to hear you.
    - [ ] Test the eye-tracker calibration (if applicable).
    - [ ] Switch off the lights and shut the MSR door.
    - [ ] Switch off the heater.

MEG Recording
^^^^^^^^^^^^^

At the MEG Main Computer:

.. checklist::

    - [ ] Open MEGLaboratory: click Acquire > Autotuning > OK and wait for the autotuning process to complete.
    - [ ] Click Acquire > MEG Measurement > Sensor Check and wait 1–2 minutes until signals stabilise.
    - [ ] While waiting, fill in subject details (e.g., “sub-007”).
    - [ ] Create the subject folder and copy/paste the folder path so that the data is saved correctly.
    - [ ] Once signals are stable, click Lock.
    - [ ] Wait for Lock to complete and for the signals to stabilise again.
    - [ ] Take a marker measurement: click MEG Measurement > Marker Measurement > Start.
    - [ ] After the process is complete, ensure accuracy values are around 99.90% or above.
    - [ ] Ensure the screen is displaying the experiment instructions and that the participant is ready to begin the task.
    - [ ] Start recording: click Continuous Mode > Start > Start Acquisition.
    - [ ] During the session, take note of any signal abnormalities, participant movement, or interruptions with timestamps.

After MEG Session
^^^^^^^^^^^^^^^^^

.. checklist::

    - [ ] Stop recording: click Continuous Mode > Abort.
    - [ ] Save the .con file to the participant folder.
    - [ ] Take a second marker measurement: click Acquire > MEG Measurement > Marker Measurement.
    - [ ] Once the MEG measurement is complete, click Unlock.
    - [ ] Open the MSR door. Assist the participant in sitting up and carefully remove the HPI coils.
    - [ ] Guide the participant back to the laser scan room and instruct them to change back into their clothes and collect all belongings.
    - [ ] Switch the heater back on.
    - [ ] Provide the participant with compensation (if applicable).

After Participant Leaves
^^^^^^^^^^^^^^^^^^^^^^^^

.. checklist::

    - [ ] Switch Marker Box off.
    - [ ] Remove and stow used bedsheets and pillow covers in the laundry basket, and used earphone covers in the bin.
    - [ ] Disinfect MSR surfaces (bed, helmet), HPI coils (gently), and earphones using disinfectant wipes.
    - [ ] Call security to inform them that the session is complete (if finished early).

Saving The Data
^^^^^^^^^^^^^^^

Experiment Data
"""""""""""""""

.. checklist::

    - [ ] At the Stimulus Computer, use the hard drive “EXTREME SSD” to save the data and transfer to the Laser Scan computer.
    - [ ] Open the project folder, select and upload the following files to the hard drive:
        - sub-007.edf
        - trigger_log_s011_YYYYMMDD_000000.txt
        - sub-007-vcp.mat

Laser Scan Data
"""""""""""""""

.. checklist::

    - [ ] At the laser scan computer, create a folder with the participant ID (e.g. “sub-007”).
    - [ ] Save raw laser scan data as “sub-007_laser-scan”.
    - [ ] Apply the smoothing filter: View > Basic Surface > Save as: “sub-007_basic-surface”
    - [ ] Save files to the subject folder: Export > Basic Surface > Export stylus points as well. Save as: “sub-007_stylus-points”
    - [ ] At the Laser Scan Computer, open the project folder, select and upload the following files to the hard drive:
        - sub-007_laser-project
        - sub-007_basic-surface
        - sub-007_stylus-points

MEG Data
""""""""

.. checklist::

    - [ ] Use the hard drive “EXTREME SSD” to save the data and transfer from MEG Main PC to the Laser Scan computer.
    - [ ] At the MEG Main PC, open the “sub-007.con” file and click Edit > Noise Reduction (R) > save as “sub-007_denoised.con”.
    - [ ] At the MEG Main PC, open the project folder, select and upload the following files to the hard drive:
        - YYMMDD-1.mrk
        - YYMMDD-2.mrk
        - sub-007.con
        - sub-007_denoised.con

.. checklist::

    - [ ] Safely eject EXTREME SSD.

Uploading Data to NYU Box:
""""""""""""""""""""""""""

.. checklist::

    - [ ] In the project folder on NYU Box, create 3 sub-folders, name them:
        - "derivatives" for Experiment Data
        - "laserscan" for Laser Scan Data
        - "meg" for Experiment Data

.. checklist::

    - [ ] From the hard drive, select and upload all files to their respective folders.

The “derivatives” folder should contain the following files:

.. checklist::

    - [ ] sub007.edf
    - [ ] trigger_log_s011_YYYYMMDD_000000.txt
    - [ ] sub-007-vcp.mat

The “laserscan” folder should contain the following files:

.. checklist::

    - [ ] sub-007_laser-project
    - [ ] sub-007_basic-surface
    - [ ] sub-007_stylus-points

The "meg" folder should contain the following files:

.. checklist::

    - [ ] YYMMDD-1.mrk
    - [ ] YYMMDD-2.mrk
    - [ ] sub-007.con
    - [ ] sub-007_denoised.con
