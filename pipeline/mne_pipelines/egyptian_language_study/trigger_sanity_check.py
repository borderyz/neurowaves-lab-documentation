import mne

import matplotlib
import matplotlib.pyplot as plt
from pipeline.mne_pipelines.kit_general_pipelines.utilities import *

matplotlib.use('TkAgg')  # or can use 'TkAgg', whatever you have/prefer



#mne.find_events



# Import data

# Sub 009 Egyptian should have 2188 different triggers

MEG_DATA_DIR = 'egyptian_sub009.con'


RAW_DATA = mne.io.read_raw_kit(input_fname=MEG_DATA_DIR, preload=True, verbose=False)







# Specify the channels you want to visualize (by name)


# Plot only those channels
# RAW_DATA.plot(picks=trigger_channels
#               )

#plt.show(block=True)
events = []

for index, channel in enumerate(trigger_channels):
    event_data = mne.find_events(RAW_DATA, stim_channel=channel, min_duration=0.05)
    events.append(event_data)
#event_steps = mne.find_stim_steps(RAW_DATA, stim_channel=trigger_channels)



b = 1