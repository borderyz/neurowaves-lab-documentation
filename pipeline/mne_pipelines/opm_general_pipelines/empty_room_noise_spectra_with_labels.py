import numpy as np
import matplotlib.pyplot as plt
import mne

# Path to your empty-room .fif file
empty_room_fif = '20240415_113034_sub-NA_file-emptyRoom-raw.fif'

# Load empty room data
raw_empty = mne.io.read_raw_fif(empty_room_fif, preload=True)

# Pick channels based on the regex (adjust as needed)
picks = mne.pick_channels_regexp(raw_empty.ch_names, regexp='^(L|R)*')
raw_picked = raw_empty.copy().pick(picks)

# Exclude the bad channel(s)
bad_channels = ['L115_bz-s51']
raw_picked.drop_channels(bad_channels)

# Apply a band-pass filter (optional)
raw_picked.filter(l_freq=0, h_freq=500.0)

# Extract the data and sampling frequency
data = raw_picked.get_data()
sfreq = raw_picked.info['sfreq']

# Compute the PSD using Welch's method.
# psds shape: (n_channels, n_freqs), units T²/Hz for MEG data.
psds, freqs = mne.time_frequency.psd_array_welch(data, sfreq=sfreq, fmax=1000, n_fft=2048)

# Average the PSDs across channels
psd_avg = np.mean(psds, axis=0)

# Convert the average PSD to amplitude spectral density (ASD):
# Take the square root to convert from T²/Hz to T/√Hz.
asd_avg = np.sqrt(psd_avg)
# Convert from Tesla to femto Tesla (fT)
asd_ft_avg = asd_avg * 1e15

# Plot the averaged noise spectrum
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(freqs, asd_ft_avg, label='Average ASD', color='blue')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Noise Spectrum (fT/√Hz)')
ax.set_title('Average Noise Spectrum Across Channels')

# Set x-axis and y-axis to logarithmic scale with specified limits
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(0.1, 500)
ax.set_ylim(1, 10000)

ax.legend()
plt.show()
