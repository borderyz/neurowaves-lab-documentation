# Visual\_Imagery\_MEG



# Your research question





visual\_imagery\_practice\_lastrun.py and visual\_imagery\_lastrun.py are code file for practice and official experiment of visual imagery. We want to investigate MEG signal when people hearing language description and imagine according to the description.



Visual\_WM\_practice\_lastrun.py and Visual\_WM\_lastrun.py are code file for practice and official experiment of visual working memory. We want to investigate MEG signal when people hearing language description and recall certain image according to the description.





# Your design



visual\_imagery\_practice\_lastrun.py:

P\_Inter(1s, a short break between each trial) -> P\_Cue(1s), P\_Sound(1.5s, language description), P\_BG(6.5s, 1s overlapped with P\_Cue, 1-2.5s overlapped with P\_Sound, 2.5-6.5s shows an empty screen for participant to imagine) -> P\_RateText, P\_IMG1-5, P\_key\_Resp2 (no time limit, giving participants reference images to rate with a value from 1 to 5) -> P\_CQ, P\_CQ\_Option, P\_CQ\_Key\_Resp (no time limit, a question with 3 options 'YES', 'NO', 'DON'T KNOW' for people to choose one as response)





visual\_imagery\_lastrun.py:

VI\_Inter(1s) -> VI\_Cue(1s), VI\_Sound(1.5s), VI\_BG(6.5s, all same as practice) -> VI\_RateText, VI\_KeyResp2 (no reference images, others same as practice) -> VI\_CQ, VI\_CQ\_Option, VI\_CQ\_Key\_Resp (same as practice)





Visual\_WM\_practice\_lastrun.py:

WM\_P\_Inter(1s, a short break between each trial) -> WM\_P\_P\_Image1(2s, present image of an object) -> empty screen(0.5s) -> WM\_P\_P\_Image2(2s, present image of another object) -> WM\_P\_P\_BG(0.5s, just another 0.5s empty screen) -> WM\_P\_Cue(1s), WM\_P\_Sound(1.5s, language description of Image1 or 2), WM\_P\_WM\_BG(6.5s, 1s overlapped with WM\_P\_Cue, 1-2.5s overlapped with WM\_P\_Sound, 2.5-6.5s shows an empty screen for participant to recall) -> WM\_P\_Test\_Image, WM\_P\_Test\_Resp, WM\_P\_Test\_Q, WM\_P\_Test\_Option (no time limit, just present image or a distorted image of the target object and ask people if this is same as what they just saw)





Visual\_WM\_lastrun.py (all stages same as practice):

WM\_Inter(1s) -> WM\_P\_Image1(2s) -> empty screen(0.5s) -> WM\_P\_Image2(2s) -> WM\_P\_BG(0.5s) -> WM\_Cue(1s), WM\_Sound(1.5s), WM\_BG(6.5s) -> WM\_P\_Test\_Image, WM\_P\_Test\_Resp, WM\_P\_Test\_Q, WM\_P\_Test\_Option (no time limit)







# Trigger Dictionary

We use 8 trigger types:

Mapping from binary code to trigger type name (P\_sound start,...)
Channels from 224 to 231
\[00000000]
\[10000000] --> P\_sound start
\[01000000] --> P\_sound end



* Binary Code (8 bits) x Trigger type name









# Button presses

5 buttons on the left hand
and 3 buttons for the right hand

* add more details here: are we listening to any  button press and saving the first pressed button into the logfile

   YES. For both left hand and right hand buttons.





* or are we listening to a specific button(s) and if the user presses something else, nothing happens?

   NO.





* does the button listening is timed? above a certain time we pass the trial or do we keep listening indefinitely to the button press

   NO.









# Operational Protocol



AuditoryPrompt: audio files to play in the experiment

imgs\_diffusion: image stimuli used in the experiment

utilities.py: trigger setting code for MEG experiment

visual\_imagery\_lastrun.py: code for running official visual imagery experiment

visual\_imagery\_practice\_lastrun.py: code for running practice session of visual imagery experiment

Visual\_WM\_lastrun.py: code for running official working memory experiment

Visual\_WM\_practice\_lastrun.py: code for running practice session of working memory experiment

VI\_Blocks.csv: setting blocks for visual\_imagery\_lastrun.py

VI\_trial\_file1.csv: trial file of block1, for visual\_imagery\_lastrun.py

VI\_trial\_file2.csv: trial file of block2, for visual\_imagery\_lastrun.py

VI\_trig.xlsx: trigger info for visual\_imagery\_lastrun.py, including trigger type, binary code and number

VI\_Objects.csv: object info of all trials in visual\_imagery\_lastrun.py

VI\_P\_Objects.csv: trial file for visual\_imagery\_practice\_lastrun.py

VI\_practice\_trig.xlsx: trigger info for visual\_imagery\_practice\_lastrun.py

WM\_blocks.csv: setting blocks for Visual\_WM\_lastrun.py

WM\_trial\_file1.csv: trial file of block1, for Visual\_WM\_lastrun.py

WM\_trial\_file2.csv: trial file of block2, for Visual\_WM\_lastrun.py

WM\_trig.xlsx: trigger info for Visual\_WM\_lastrun.py

WM\_P\_Objects.csv: trial file for Visual\_WM\_practice\_lastrun.py

WM\_practice\_trig.xlsx: trigger info for Visual\_WM\_practice\_lastrun.py



Files need to run:

visual\_imagery\_lastrun.py: official visual imagery experiment

visual\_imagery\_practice\_lastrun.py: practice session of visual imagery experiment

Visual\_WM\_lastrun.py: official working memory experiment

Visual\_WM\_practice\_lastrun.py: practice session of working memory experiment



Input value in running: put subject ID (e.g. '001') into 'participant'

Output file will be 1 csv file, 1 log file, 1 psydat file, named with '001\_ExperimentName\_date\_...'





What each file is, and what we need to run, what are the input values (subject ID, ...)
What is the output of your experiment (files output)



More information on Triggers:

https://docs.vpixx.com/vocal/sending-triggers-with-pixel-mode

