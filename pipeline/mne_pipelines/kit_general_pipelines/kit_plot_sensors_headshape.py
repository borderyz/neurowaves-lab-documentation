import mne
import matplotlib.pyplot as plt
from qtpy import QtWidgets  # pip install qtpy
mne.viz.set_3d_backend("pyvistaqt")  # needs pyvistaqt + PyQt5/6 installed

# Define the file path
PATH_FILE = r"C:\Users\hz3752\Box\MEG\Data\visual_crowding_preview\sub-001\derivatives\sub-001_task-visualcrowdpreview_proc-CALMnoisereduction_meg-raw.fif"
import pyvista as pv
# Load the raw data
raw = mne.io.read_raw_fif(PATH_FILE, preload=False)

# Plot the sensors and retrieve the Matplotlib figure
# Set show_names=False to prevent default labeling
# fig = mne.viz.plot_sensors(raw.info, kind='3d', show_names=False, show=False)
#
# # Get the current 3D Axes from the figure
# ax = fig.gca()
#
# plt.show()

fig = mne.viz.plot_alignment(raw.info,
                             meg=["helmet", "sensors"],
                             dig=True)


app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
app.exec_()


#fig.plotter.show()
