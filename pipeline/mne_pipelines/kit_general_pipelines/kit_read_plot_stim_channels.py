import mne

import matplotlib

from pipeline.mne_pipelines.kit_general_pipelines.utilities import *

matplotlib.use('TkAgg')

meg_data_dir = '../egyptian_language_study/egyptian_sub009.con'
csv_file_experiment = '../egyptian_language_study/word_count_egyptian_list9.csv'


RAW_DATA = mne.io.read_raw_kit(meg_data_dir, preload=False, verbose=False)

RAW_DATA.plot(picks=trigger_channels,
         block=True,
         scalings={"misc": DEFAULT_MISC_CHANNELS_AMPLITUDE_SCALE},
         duration=DEFAULT_TIME_SCALE)



