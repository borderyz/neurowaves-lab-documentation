import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

import mne

data_path = mne.datasets.phantom_kit.data_path()
actual_pos, actual_ori = mne.dipole.get_phantom_dipoles("oyama")
actual_pos, actual_ori = actual_pos[:49], actual_ori[:49]  # only 49 of 50 dipoles

raw = mne.io.read_raw_kit(data_path / "002_phantom_11Hz_100uA.con")
# cut from ~800 to ~300s for speed, and also at convenient dip stim boundaries
# chosen by examining MISC 017 by eye.
raw.crop(11.5, 302.9).load_data()
raw.filter(None, 40)  # 11 Hz stimulation, no need to keep higher freqs
plot_scalings = dict(mag=5e-12)  # large-amplitude sinusoids
raw_plot_kwargs = dict(duration=15, n_channels=50, scalings=plot_scalings)
raw.plot(**raw_plot_kwargs)