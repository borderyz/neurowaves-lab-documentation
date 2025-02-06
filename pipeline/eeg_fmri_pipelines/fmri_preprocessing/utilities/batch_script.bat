@echo off
dcm2bids ^
    -c C:\Users\hz3752\PycharmProjects\meg-pipeline\pipeline\eeg_fmri_pipelines\fmri_preprocessing\utilities\config1.json ^
    -o C:\Users\hz3752\Desktop\EEG-FMRI\data_finger_tapping\ ^
    -d C:\Users\hz3752\Desktop\EEG-FMRI\data_finger_tapping\Subject_0665_ses_01\Subject_0665_ses_01\scans ^
    -p 0665 ^
    --force_dcm2bids
pause