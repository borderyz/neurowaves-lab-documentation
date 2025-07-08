
# In OPM sensor space coordinates, the (0, 0, 0) correspond to the center of the helmet
# (x, y, z)

# The x-axis is right to left
# The y-axis is anterior to posterior
# the z-axis is superior to inferior
# the x-axis increases from left to right
# the y-axis increases from posterior to anterior
# the z-axis increases from inferior to superior
# therefore it is a RAS coordinate system



import numpy as np
import mne
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Option to add sensor names as labels
add_labels = False  # Set to True to display labels

# Define the file path
PATH_FILE = r"emptyroom_11-raw.fif"

# Load the raw data
raw = mne.io.read_raw_fif(PATH_FILE, preload=False)

# Plot the sensors and retrieve the Matplotlib figure
# Set show_names=False to prevent default labeling
fig = mne.viz.plot_sensors(raw.info, kind='3d', show_names=False, show=False)

# Get the current 3D Axes from the figure
ax = fig.gca()

# Extract sensor positions, orientation vectors, and names
chs = raw.info['chs']
positions = []
nax_vectors = []
nbx_vectors = []
ncx_vectors = []
sensor_names = []

for ch in chs:
    loc = ch['loc']
    if len(loc) >= 12:  # Ensure loc has enough elements
        positions.append(loc[:3])        # [px, py, pz]
        nax_vectors.append(loc[3:6])     # [nax, nay, naz]
        nbx_vectors.append(loc[6:9])     # [nbx, nby, nbz]
        ncx_vectors.append(loc[9:12])    # [ncx, ncy, ncz]
        sensor_names.append(ch['ch_name'])  # Add sensor name

positions = np.array(positions)
nax_vectors = np.array(nax_vectors)
nbx_vectors = np.array(nbx_vectors)
ncx_vectors = np.array(ncx_vectors)

# Reorder vectors and labels to ensure Radial vector is first
vectors = [ncx_vectors, nax_vectors, nbx_vectors]
colors = ['b', 'r', 'g']
vector_labels = ['Radial vector', 'Tangential Vector 1', 'Tangential Vector 2']

# Add vectors to the 3D plot with distinct colors
for vector, color, label in zip(vectors, colors, vector_labels):
    ax.quiver(
        positions[:, 0], positions[:, 1], positions[:, 2],  # Start positions
        vector[:, 0], vector[:, 1], vector[:, 2],           # Vector directions
        color=color, label=label, length=0.02, normalize=True
    )


if add_labels:
    for pos, name in zip(positions, sensor_names):
        ax.text(
            pos[0], pos[1], pos[2], name,
            size=8, color='black', zorder=10
        )

# Add legend
ax.legend()

# Show the updated plot
plt.show()