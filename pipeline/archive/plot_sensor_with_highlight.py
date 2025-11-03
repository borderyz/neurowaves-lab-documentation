import matplotlib
matplotlib.use('TkAgg')
import mne

# Replace with the path to your FIFF file
fiff_file_path = r'C:\Users\hz3752\Box\MEG\Data\resting-state\sub-01\meg-kit\sub-01_01-eyes-closed-raw.fif'
raw = mne.io.read_raw_fif(fiff_file_path)

# List of sensor names to highlight in red
list_1 = ['MEG 014', 'MEG 067', 'MEG 094', 'MEG 136', 'MEG 137', 'MEG 147', 'MEG 160', 'MEG 165']  # replace with your sensor names

list_2 = ['MEG 014', 'MEG 046', 'MEG 067', 'MEG 094', 'MEG 136', 'MEG 137', 'MEG 142', 'MEG 160']

# Get sensor locations and names
info = raw.info
fig = mne.viz.plot_sensors(info, kind='topomap', show_names=True)

#fig = mne.viz.plot_sensors(info, kind='3d', show_names=True)

# Customize plot
ax = fig.axes[0]  # Get the axes

for sensor_name in list_2:
    # Find the sensor index
    idx = info['ch_names'].index(sensor_name)
    # Get the text object corresponding to the sensor
    text_obj = ax.texts[idx]
    # Change the color to red
    text_obj.set_color('red')




# Display the plot
fig.show()

a = 1