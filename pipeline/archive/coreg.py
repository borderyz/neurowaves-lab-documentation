


import mne
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication.instance()  # checks if QApplication already exists
if not app:  # create QApplication if it doesnt exist
    app = QApplication(sys.argv)

mne.gui.coregistration(
    inst=r'C:\Users\hz3752\PycharmProjects\mne_bids_pipeline\data\meg\Sub-0037\sub-01_01-eyes-closed-raw.fif',
    subject='Sub-0037',
    subjects_dir=r'C:\Users\hz3752\PycharmProjects\mne_bids_pipeline\data\anat\outputs\PostFreeSurfer\T1w',  # contains a sub-folder for subject
    head_high_res=True,
)

app.exec_()



