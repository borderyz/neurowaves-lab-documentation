Experiment example 10: Go-No/Go experiment
------------------------------------------

Author: Gianluca Marsciano, gm3598@nyu.edu

**Description**


The participant will see a fixation cross for a period of `400ms` followed by a blank time of 100ms then a stimulus either a

- circle, in which case the participant should press the `Yellow` response button
- triangle, in which case the participant should not respond

The reponse window is 1 second
The stimulus is presented for 50 ms

Shall the participant react incorrectly (wrong press, or no press when there should be), a negative feedback is provided visually and auditory (150 ms)


**Used Trigger Channels**

- For resting state experiment, the trigger event stays on during the event period
    - Eyes closed trigger corresponds to channel 224
    - Eyes open trigger corresponds to channel 225
- For Go-No/Go experiment
    - trig.start = [4  0  0]; % ch224
    - trig.end   = [16  0  0]; % ch225
    - trig.go = [64 0 0]; % ch226
    - trig.nogo = [0  1 0]; % ch227
    - trig.go_resp = [0  4 0]; % ch228 % Go trials with Responses (Correct)
    - trig.go_noresp = [0 16 0];  % ch229 % Go trials with NO Responses (Too Slow/Error)
    - trig.nogo_resp = [0 64 0]; % ch230 NoGo trials with Responses (Error)
    - trig.nogo_noresp = [0 0  1]; % ch231 NoGo trials with NO Responses (Correct)


**Protocol for Heal Project usage of Go-No/Go experiment**

- Make resting state eyes closed (5min)
    - Run experiments/restingstate/resting_state_meg_EYES_CLOSED.m
    - Ensure that time2rest = 60*5
- Make resting state eyes open (5min)
    - Run experiments/restingstate/resting_state_meg_EYES_OPEN.m
    - Ensure that time2rest = 60*5
-Make go-no-go experiment (10min)
    - Ensure that
    - Run experiments/psychtoolbox/go-no-go/GO_NOGO_BEHAVIOR_NYUAD_AudioVisual_Negative_Feedback_MEG_GM.m
    - Set all details of participants in the pop-up-window
- Make resting state eyes closed (10min)
    - Run experiments/restingstate/resting_state_meg_EYES_CLOSED.m
    - Set time2rest = 60*10    (If the participant and time allows more, please increase the time2rest)



.. dropdown:: Go-No-Go code available under `experiments\psychtoolbox\go-no-go`

    .. literalinclude:: ../../../../experiments/psychtoolbox/go-no-go/meg_main_go-no_go.m
      :language: matlab