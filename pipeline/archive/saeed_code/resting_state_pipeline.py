import numpy as np
import mne
from mne.preprocessing import maxwell_filter

# Load the two raw data files
raw1 = mne.io.read_raw_fif(r'C:\Users\hz3752\PycharmProjects\mne_bids_pipeline\data\meg\Sub-0037\sub-01_02-eyes-open-raw.fif', preload=True)
raw2 = mne.io.read_raw_fif(r'C:\Users\hz3752\PycharmProjects\mne_bids_pipeline\data\meg\Sub-0037\sub-01_01-eyes-closed-raw.fif', preload=True)

# Attempt to apply Maxwell filtering with the assumption that HPI information is automatically utilized if available
try:
    raw1_aligned = maxwell_filter(raw1)
    raw2_aligned = maxwell_filter(raw2)
except Exception as e:
    print(f"Failed to apply Maxwell filtering: {e}")
    raw1_aligned, raw2_aligned = raw1, raw2  # Fallback to using unaligned data

# Concatenate the raw data
try:
    raw_concatenated = mne.io.concatenate_raws([raw1_aligned, raw2_aligned])
except ValueError as e:
    print(f"Error during concatenation: {e}")




# Plotting 2D sensor locations
fig = raw_concatenated.plot_sensors(show_names=True)
plt.show()

# Finding the events, ploting them, and mark them in the raw plot
events = mne.find_events(raw_concatenated, stim_channel="STI 014")

event_dict = {
    "eyes closed": 1,
    "eyes open": 2,
}

fig = mne.viz.plot_events(
    events, sfreq=raw_concatenated.info["sfreq"], first_samp=raw_concatenated.first_samp, event_id=event_dict
)

raw_concatenated.plot(
    events=events,
    color="gray",
    event_color={1: "r", 2: "g"},
)
plt.show()


# Identify channels with zero or infinite values in the PSD
channels_with_issues = ['MEG 053', 'MEG 067', 'MEG 102', 'MEG 137', 'MEG 154', 'MEG 181', 'MEG 182', 'MEG 183']

# Mark bad channels
raw_concatenated.info['bads'] = channels_with_issues

# Remove bad channels
raw_concatenated_cleaned = raw_concatenated.copy().drop_channels(raw_concatenated.info['bads'])

# Define the duration of each epoch (in seconds)
epoch_duration = 2  # 2 sec

# Create fixed-length epochs for the entire concatenated raw data
epochs_all = mne.make_fixed_length_epochs(raw_concatenated_cleaned, duration=epoch_duration, preload=True)

# Plot PSD for cleaned data with labels
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

# Plot PSD for the first 1 minute (eyes closed)
epochs_closed = epochs_all[:len(epochs_all) // 2]  # First half is eyes closed
epochs_closed.plot_psd(fmin=1, fmax=40, ax=ax1, color='blue', show=False, average=True, spatial_colors=False, line_alpha=0.5, dB=True, xscale='log')

# Plot PSD for the last 1 minute (eyes open)
epochs_open = epochs_all[len(epochs_all) // 2:]  # Second half is eyes open
epochs_open.plot_psd(fmin=1, fmax=40, ax=ax2, color='red', show=False, average=True, spatial_colors=False, line_alpha=0.5, dB=True, xscale='log')

# Add labels
ax1.set(title='Power Spectral Density (First 1 Minute - Eyes Closed)', xlabel='Frequency (Hz)', ylabel='Power Spectral Density (dB)')
ax2.set(title='Power Spectral Density (Last 1 Minute - Eyes Open)', xlabel='Frequency (Hz)', ylabel='Power Spectral Density (dB)')

# Show the plot
plt.tight_layout()
plt.show()

# # Apply baseline correction
# epochs.apply_baseline((0, 0))
#
# # Select occipital channels
# occipital_channels = ['MEG 199', 'MEG 198']
# epochs.pick_channels(occipital_channels)
#
# # Compute the power spectral density (PSD) using Morlet wavelets
# freqs = np.logspace(*np.log10([1, 40]), num=50)  # Define frequency range
# power = tfr_morlet(epochs, freqs=freqs, n_cycles=2, return_itc=False, average=True)
#
# # Plot the PSD
# fig, ax = plt.subplots(figsize=(10, 6))
# power.plot([0], baseline=None, mode='logratio', title='Average power', axes=ax, show=False)
# plt.show()
#
# #Epochs objects have a built-in plotting method a plot_image, which shows each epoch as one row of an image map,
# #with color representing signal magnitude; the average evoked response and the sensor location are shown below the image:
# epochs.plot_image(picks=["MEG 199", "MEG 198"])
#
#
# # Extract epochs for "eyes closed" and "eyes open" events using event IDs
# epochs_closed = epochs[event_dict["eyes closed"]]
# epochs_open = epochs[event_dict["eyes open"]]
#
# # Compute PSD for "eyes closed" epochs
# power_closed = tfr_morlet(epochs_closed, freqs=freqs, n_cycles=2, return_itc=False, average=True)
#
# # Compute PSD for "eyes open" epochs
# power_open = tfr_morlet(epochs_open, freqs=freqs, n_cycles=2, return_itc=False, average=True)
#
# # Plot the PSD for "eyes closed" epochs
# fig, ax = plt.subplots(1, 2, figsize=(14, 6))
# power_closed.plot([0], baseline=None, mode='logratio', title='Average power (Eyes Closed)', axes=ax[0], show=False)
#
# # Plot the PSD for "eyes open" epochs
# power_open.plot([0], baseline=None, mode='logratio', title='Average power (Eyes Open)', axes=ax[1], show=False)
#
# # Remove the common title above the subplots
# fig.suptitle('')
#
# # Set titles for each subplot
# ax[0].set_title('Average power (Eyes Closed)')
# ax[1].set_title('Average power (Eyes Open)')
#
# plt.show()
# epochs_closed.compute_psd(fmin=2.0, fmax=40.0).plot(
#     average=True, amplitude=False, picks=None, exclude="bads"
# )
#
# plt.show()
#
# epochs_open.compute_psd(fmin=2.0, fmax=40.0).plot(
#     average=True, amplitude=False, picks="data", exclude="bads"
# )
#
# plt.show()
