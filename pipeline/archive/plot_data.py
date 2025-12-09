import mne
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')  # or can use 'TkAgg', whatever you have/prefer


# Replace 'your_data-raw.fif' with the path to your FIFF file
#raw = mne.io.read_raw_fif(r'../data/sub_0_task_empty-room-26-06-2024-raw.fif')

#raw = mne.io.read_raw_fif(r'C:\Users\hz3752\Box\MEG\Data\empty-room\sub-emptyroom\meg-kit\sub-0_task-empty-room2-2013-12-11-raw.fif')

#raw = mne.io.read_raw_fif(r'C:\Users\hz3752\Box\MEG\Data\empty-room\sub-emptyroom\meg-kit\sub-0_task-empty-room-2024-02-21-raw.fif')



#raw = mne.io.read_raw_fif(r'../data/test_04-raw.fif')
#raw = mne.io.read_raw_fif(r'C:\Users\hz3752\PycharmProjects\meg-pipeline\data\no_OPM\emptyroom_7-1-2024-raw.fif')

raw = mne.io.read_raw_fif(r'C:\Users\hz3752\PycharmProjects\meg-pipeline\data\fwnm_hannah\Hannah_Test_01-raw.fif')

#raw = mne.io.read_raw_fif(r'C:\Users\hz3752\Box\MEG\Data\ToBeSorted\AS_Arabic_01-raw.fif')


#raw = mne.io.read_raw_fif(r'C:\Users\hz3752\Box\MEG\Data\empty-room\sub-emptyroom\meg-kit\sub_0_task_empty-room-26-06-2024-1h15minPM-raw.fif')

#raw = mne.io.read_raw_fif(r'C:\Users\hz3752\Box\MEG\Data\empty-room\sub-emptyroom\meg-kit\sub-0_task-empty-room-26-06-2024-1h36minPM-raw.fif')

# # Specify the channel name you want to plot
# channel_name = 'MISC 001'
# raw.pick_channels([channel_name])
# scalings = {'misc':0.1}
raw.plot(start=0, duration=5)

#raw.plot(scalings = scalings, duration=320, start=0, n_channels=1)

plt.show(block=True)
#raw.plot(scalings = scalings, duration=320, start=0, n_channels=1)

a = 1


