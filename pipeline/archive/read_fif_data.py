import mne
import matplotlib.pyplot as plt

raw = mne.io.read_raw_fif('../input_data/meg/sub-00/sub-00_01_analysis_01-raw.fif')


raw.plot(duration = 15)
print(raw.info.get_channel_types())

plt.show()

b=1