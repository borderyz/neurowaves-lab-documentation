import mne
import matplotlib.pyplot as plt

# Path to your empty-room .fif file
empty_room_fif = '20240415_113034_sub-NA_file-emptyRoom-raw.fif'

# Load empty room data
raw_empty = mne.io.read_raw_fif(empty_room_fif, preload=True)

picks = mne.pick_channels_regexp(raw_empty.ch_names, regexp='^(L|R)*')

raw_picked = raw_empty.copy().pick(picks)


# Set a band-pass filter (optional, useful for removing low-frequency drift and high-frequency noise)
raw_picked.filter(l_freq=0, h_freq=500.0)


# Plot Power Spectral Density (PSD)
# raw_picked.plot_psd(fmax=1000)
#
# plt.show()
#
#
# print(raw_picked.ch_names)


import numpy as np

fig = raw_picked.compute_psd(fmax=500).plot()
ax = fig.axes[0]
lines = ax.get_lines()

for line, ch_name in zip(lines, raw_picked.ch_names):
    x_data = line.get_xdata()
    y_data = line.get_ydata()
    idx = np.argmax(y_data)  # choose the index where the curve is highest
    ax.text(x_data[idx], y_data[idx], ch_name, fontsize=8, rotation=45)

plt.show()