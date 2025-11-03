import matplotlib.pyplot as plt
import mne
from mne.time_frequency import stft
import numpy as np

# Load your FIFF file
raw = mne.io.read_raw_fif(r"C:\Users\hz3752\Box\MEG\Data\resting-state\sub-01\meg-kit\sub-01_01-eyes-closed-raw.fif", verbose=False)



# Plot the first 5 seconds of the data
#raw.plot(start=0, duration=5)



channel_name = 'MISC 001'
raw_picked = raw.copy().pick_channels([channel_name])
scalings = {'misc':0.1}

#raw_picked.plot(scalings = scalings, duration=315, start=0, n_channels=1)


croped_data = raw.copy()

croped_data.crop(100, 250)



# Extract the data for all channels
data = croped_data.get_data()

# Define the parameters for STFT
n_fft = 256  # Number of FFT points
step = n_fft // 2  # Overlap between windows

# Perform STFT on the data
stft_data = stft(data, wsize=n_fft, tstep=step, verbose=True)

# The shape of stft_data will be (n_channels, n_freqs, n_times)
print("STFT data shape:", stft_data.shape)

# Example: Access the STFT result for the first channel
first_channel_stft = stft_data[0]
print("First channel STFT shape:", first_channel_stft.shape)


# The shape of stft_data will be (1, n_freqs, n_times)
stft_data = stft_data[0]  # Remove the first dimension as it's only one channel

# Get the time and frequency vectors for plotting
times = np.arange(stft_data.shape[1]) * step / raw.info['sfreq']
freqs = np.fft.rfftfreq(n_fft, d=1. / raw.info['sfreq'])


# Filter the frequencies to be within the range of 0 to 50 Hz
freq_mask = freqs <= 50
filtered_stft_data = stft_data[freq_mask, :]
filtered_freqs = freqs[freq_mask]

# Get the time vector for plotting
times = np.arange(filtered_stft_data.shape[1]) * step / raw.info['sfreq']

# Plot the filtered STFT data for the specific channel
plt.figure(figsize=(10, 6))
plt.imshow(np.abs(filtered_stft_data), aspect='auto', origin='lower',
           extent=[times.min(), times.max(), filtered_freqs.min(), filtered_freqs.max()])
plt.colorbar(label='Magnitude')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title(f'STFT of {channel_name} (0-50 Hz)')
plt.show()





# #croped_data.plot(start=0, duration =5)
#
#
# data, times = raw[:]
# wsize=256
# fourier_transform_data = mne.time_frequency.stft(data, wsize=wsize)
#
#
# # Select the channel index you're interested in
# channel_index = 1
# import numpy as np
# # Compute magnitude of STFT results
# magnitude = np.abs(fourier_transform_data[channel_index])
#
# # Prepare frequencies and time vectors for plotting
# sfreq = raw.info['sfreq']
# print('Sampling frequency', sfreq)
# frequencies = np.linspace(0, sfreq / 2, magnitude.shape[0], endpoint=True)
# t_secs = np.arange(magnitude.shape[1]) * (wsize / sfreq)
#
# # Plotting
# plt.figure()
# plt.pcolormesh(t_secs, frequencies, magnitude, shading='auto')
# plt.title(f'STFT Magnitude - Channel {raw.info["ch_names"][channel_index]}')
# plt.ylabel('Frequency (Hz)')
# plt.ylim(0, 20)
# plt.xlabel('Time (sec)')
# plt.colorbar(label='Magnitude')
# plt.show()
#
