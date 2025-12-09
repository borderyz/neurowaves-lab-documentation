import matplotlib
matplotlib.use('TkAgg')

import mne

# Replace 'your_data-raw.fif' with the path to your FIFF file
raw = mne.io.read_raw_fif(r'C:\Users\hz3752\Box\MEG\Data\resting-state\sub-01\meg-kit\sub-01_01-eyes-closed-raw.fif')


# For a 2D topographic plot of the sensor locations
raw.plot_sensors(kind='topomap', show_names=True)


a =1




# # For a 3D plot of the sensor locations
# raw.plot_sensors(kind='3d')
#
#
# # Interactive 3D plot in a separate window
# raw.plot_sensors(kind='3d', show_names=True, ch_type='mag')
