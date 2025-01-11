Contact for this experiment:

Tasnim Ezzedin te2207@nyu.edu


Description of the experiment:

"This experiment examines the crowding (the spacing between the letters within each word) and preview effects in the Arabic language, utilizing three distinct crowding values: 0, -75, and -125. Within the experiment, these values are represented as follows: 1 for -125, 2 for -75, and 3 for 0. These values are used in the naming of the images as well as in the final output of the .mat file. Within the .mat file, a column appears containing the number corresponding to the level of crowding (1, 2, or 3).
For example, SET1_conn_0_cwdg_1_1.jpg, SET1_conn_0_cwdg_2_1.jpg, etc.
Due to the nature of the arabic language being written in cursive, it has a varity of connections between letters. In the naming of the images, the 'conn' refers to the connectivity of the letters. For example, if a word has only two letters that are connected and a crowding level of 1 (i.e. -125) the name would be SET1_conn_2_cwdg_1_1.jpg.
The stimuli are made of 300 different arabic words. SET1 has a different combination of crowding values assigned to the words than SET2, however, both have the same words.

In this paradigm, participants are instructed to focus on a fixation point on the screen. Words will be presented either to the left or right of the fixation point, and participants will be required to look at the presented word when cued by the fixation point turning green. When a saccade is detected, the target word is displayed. 
The stimuli were presented as either valid or invalid, with the invalid stimulus being a flipped version of the valid one.
After that, the participant has to decide weather or not the word displayed is the same your they saw during the trial by answering the question 'Is this the last word you saw?'.
The study employs magnetoencephalography (MEG) and eye-tracking techniques to record brain activity.


The trigger channels in MEG are as follows: 

trigger channel 224: beginn of the overall experiment.
trigger channel 225: each display of the fixation point.
trigger channel 226: display of the preview image for condition 1.
trigger channel 227: display of the preview image for condition 2.
trigger channel 228: display of the preview image for condition 3.
trigger channel 229: display of the cue (fixation point turns green).
trigger channel 230: display of the target image.

Each trigger appears only once in each trial, except trigger channel 225, which appears each time the fixation point is presented. For example, if a fixation is not detected, channels 225 is triggered again until a fixation is detected. 

The .mat file outputs a table with relevant information about the trials, such as the crowding level of each word that was displayed, weather or not it was valid or invalid, number of connections of the letters, question answers, etc."





## Step-by-Step Experiment Guide

### Requirements

- **MATLAB**: R2024a or higher
- **Psychtoolbox**: Installed in MATLAB
- **Eyelink**: For eye-tracking (optional in debug mode)
- **VPixx/MEG Controller**: For stimulus projection and trigger setup
- **Response Box**: For participant input during the experiment
- **Polhemus FastSCAN II Laser Scanner**: For pre-MEG head geometry scanning



### Files and Folder Structure

- `CP_main.m`: The main MATLAB script to run the experiment.
- `CP_table.m`: Stores all experiment information (Do Not Edit).
- **Stimuli Folders**:
  - `/SET1` and `/SET2`: Contain image stimuli for the experiment.
  - `/QuestImages`: Folder for question-related images.
- `readme.md`: This documentation file.


 
## Device Setup Instructions

### **Connecting Devices**

1. **Eyelink**: Connect for eye-tracking functionality.
2. **MEG Controller**: Ensure the participant's response box is connected and working.
3. **VPixx**: Set up for stimulus projection inside the MEG room.


## Experiment Steps

### **1. Polhemus Laser Scanner (Pre-MEG)**

1. Ensure the participant wears a cap to capture accurate head geometry.
2. Mark five fiducial points in the following order:
   - **Nasion**
   - **Right Preauricular**
   - **Left Preauricular**
   - **Right Front**
   - **Left Front**
3. Remove all metal from the participant before entering the MEG room:
   - Jewelry, shoes, phones, etc.
   - Provide scrubs as an alternative if necessary.

    

### 2. In the MEG Room

1. Place **HPI coils** on the participant's head at the marked fiducial points.
2. Provide the participant with an earpiece for communication.
3. Position the Eyelink camera and adjust focus on the participant’s eyes.
4. Explain the experiment steps to the participant (explained in detail bellow).
5. Close the MEG room door and ensure the environment is ready for data collection.




### 3. Start the Experiment

**Debug or Experiment Mode** 
1. Set the following variables before running the script:
```matlab
use_vpixx = 1;         % 1 for experiment, 0 for debugging
use_eyetracker = 1;    % 1 for experiment, 0 for debugging
trigger_test = 1;      % Set to 0 for trigger debugging
use_response_box = 1;  % 1 for participant input, 0 for auto-response in debug
```

2. Open MATLAB and run CP_main.m.
3. Enter participant information when prompted:

- Subject Number (make sure the number is three digits (e.g. 001, 002, etc.))
- Subject ID (participant initials)
- Age
- Sex (f/m)
- Task Order (leave as is)

4. If use_eyetracker = 1, calibrate and validate the Eyelink system:
Follow instructions to complete calibration and validation (explained in detail bellow).
5. The experiment will beginn after calibration and validation of the eyetracker.

**Eyetracker Calibration and Validation**
1. Calibration:
- Instruct the participant to follow the black circles as they appear on the screen.
- Ensure the participant maintains focus and follows the circles in the displayed order.
2. Validation:
- After calibration, repeat the same process to validate the eyetracker.
- Confirm that the eyetracker accurately tracks the participant’s gaze before proceeding.

**MEG Preparation**
1. Lock Sensors: Ensure the MEG sensors are locked and stable (IMPORTANT).
2. First HPI Coil Measurement:
- Take an initial head position indicator (HPI) coil measurement.
- Verify that all fiducial markers are properly detected.
3. Start MEG Measurement: Begin data recording in the MEG system.
4. Post-Experiment HPI Measurement:
- Once the MATLAB experiment is complete, but **before** stopping the MEG recording, take another HPI coil measurement to account for any head movement.
5. Stop MEG Measurement: End the MEG recording session after the second HPI measurement.

**During the Experiment**

1. Instruction Screen:
- Display the instructions on the screen.
- Allow the participant 1–2 minutes to read and ask any questions before proceeding.
2. Fixation Point:
- A black dot appears in the center of the screen.
- Instruct the participant to fixate on the dot.
3. Preview Word:
- After a random duration, a preview word appears either to the left or right of the fixation point.
- The participant should continue fixating on the black dot and not look at the word yet.
4. Cue (Fixation Point Turns Green):
- The black fixation point changes to green, signaling the participant to shift their gaze to the preview word.
5. Target Word:
- Once the participant’s gaze lands on the preview word, it transforms into the target word.
6. Response Section:
- A question appears, asking whether the target word matches the preview word.
- The participant responds by pressing:
     - Yellow button for "Yes".
     - Red button for "No".
- The system logs the response along with the trial's timing and conditions.



## Important Notes

1. Blinking:
- Instruct the participant to avoid blinking during trials to ensure accurate eyetracking.
- Blinking is allowed during the fixation and response/question phases, but the participant must refrain from blinking momentarily during fixation to proceed to the next trial.
2. Trigger Logging:
- Each trial's triggers are recorded in the log file: trigger_log_subject_<num>.txt.



## Output Files

At the end, you should have the following files:

**from MEG:**
1. sub-<num>-01-vcp.con
2. sub-<num>-vcp-analysis_NR.con
3. Sub_<num>_1_vcp.mrk
4. Sub_<num>_2_vcp.mrk

**from MATLAB:**

1. sub-<num>-vcp.mat
2. Sub-<num>-vcp.edf (for the eyetracking data)
3. trigger_log_subject_<num>.txt (Logs for MEG triggers and trial information).

**from the Polhemus laser scan:**

1. Sub-<num>-scan-stylus-vcp.txt
2. Sub-<num>-scan-vcp.txt



## Debugging

1. To debug without one of the following, set it to 0:

use_vpixx = 0;
use_eyetracker = 0;
trigger_test = 0;
use_response_box = 0;

- Setting 'use_eyetracker = 0;' ensures that the trials are run without eyetracker, i.e. no fixation from a participant is needed.
- Setting 'use_response_box = 0;' ensures that it can continue into the next trial without having to wait for a response from a participant, i.e. responses are automated.
- 'trigger_test = 0;' changes the trigger pixel size for debugging purposes.



## Trigger Info:


The trigger channels in MEG are as follows: 

trigger channel 224: beginn of the overall experiment.
trigger channel 225: each display of the fixation point.
trigger channel 226: display of the preview image for condition 1.
trigger channel 227: display of the preview image for condition 2.
trigger channel 228: display of the preview image for condition 3.
trigger channel 229: display of the cue (fixation point turns green).
trigger channel 230: display of the target image.

Each trigger appears only once in each trial, except trigger channel 225, which appears each time the fixation point is presented. For example, if a fixation is not detected, channels 225 is triggered again until a fixation is detected. 




