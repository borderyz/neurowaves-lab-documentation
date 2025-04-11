Go-No-Go experiment project for HEAL project
============================================


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