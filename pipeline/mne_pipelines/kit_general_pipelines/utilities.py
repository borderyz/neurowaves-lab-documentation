# NYUAD KIT-SQUID system MNE-based utilities



# Trigger channels name in MNE standard

trigger_channels = ['MISC 001', 'MISC 002', 'MISC 003', 'MISC 004', 'MISC 005', 'MISC 006', 'MISC 007', 'MISC 008']

# Recommended scales for plotting stimulus channels
DEFAULT_MISC_CHANNELS_AMPLITUDE_SCALE  = 1.5
DEFAULT_TIME_SCALE = 100.0


# These are static variables specific to the NYUAD setup and BIDS-naming scheme
# You do not need to change any of those variables

# Type of scan we are interested in for this pipeline
# This assumes we have an `meg` folder within each subject
DATATYPE = "meg"

# MEG scan and marker coils files extension
MEG_EXTENSIONS = [".con"]
HEAD_POSITION_INDICATOR_EXTENSIONS = [".mrk"]

# MEG Noise reduction algorithm label
NOISE_PROCESSING_LABEL = "CALMnoisereduction"
IGNORE_PROCESSING_LABEL = "CALMnoisereduction"

# MEG headshape digitizer file extention
HEADSHAPE_EXTENSIONS = [".txt"]

# ACQ Label used for files containing the stylus points digitization of fiducials
# Your stylus points has "...acq_points..." somewhere in its name

ACQ_LABEL_DIGITIZER_POINTS = "points"

# Same for headshape digitzation
# Your head surface digization file has "...acq_head..." somewhere in its name

ACQ_LABEL_DIGITIZER_HEAD = "head"

TRIGGER_MODE = ["Single-channel trigger mode",
                "Binary-coded trigger mode"]