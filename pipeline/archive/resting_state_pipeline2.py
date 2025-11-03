import mne
from mne.time_frequency import stft
import matplotlib.pyplot as plt
import numpy as np



#Gamma (γ)	&gt;35 Hz	Concentration
#Beta (β)	12–35 Hz	Anxiety dominant, active, external attention, relaxed
#Alpha (α)	8–12 Hz	Very relaxed, passive attention
#Theta (θ)	4–8 Hz	Deeply relaxed, inward focused
#Delta (δ)	0.5–4 Hz	Sleep

# Load your raw data (using an example dataset here)
raw = mne.io.read_raw_fif(r"C:\Users\hz3752\Box\MEG\Data\resting-state\sub-01\meg-kit\sub-01_01-eyes-closed-raw.fif", preload=True)

# Plot the first 5 seconds of the data
raw.plot(start=0, duration=5)

croped_data = raw.copy()

croped_data.crop(100, 250)


# Select a specific channel by name
channel_name = 'MEG 194'  # Change this to the name of the channel you want to plot
channel_index = croped_data.ch_names.index(channel_name)

# Extract the data for the specific channel
data = croped_data.get_data(picks=channel_index)

# Define the parameters for STFT
wsize = 256  # Window size in samples
step = wsize // 2  # Step size in samples

# Perform STFT on the data for the specific channel
stft_data = stft(data, wsize=wsize, tstep=step)
stft_data = stft_data[0]  # Remove the first dimension as it's only one channel

# Get the time and frequency vectors
sfreq = raw.info['sfreq']
freqs = np.fft.rfftfreq(wsize, d=1./sfreq)

# Filter the frequencies to be within the range of 0 to 50 Hz
freq_mask = freqs <= 20
filtered_stft_data = stft_data[freq_mask, :]
filtered_freqs = freqs[freq_mask]

# Get the time vector for plotting
times = np.arange(filtered_stft_data.shape[1]) * step / sfreq

# Plot the filtered STFT data for the specific channel
plt.figure(figsize=(10, 6))
plt.imshow(np.abs(filtered_stft_data), aspect='auto', origin='lower',
           extent=[times.min(), times.max(), filtered_freqs.min(), filtered_freqs.max()])
plt.colorbar(label='Magnitude')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title(f'STFT of {channel_name} (0-50 Hz)')
plt.show()
