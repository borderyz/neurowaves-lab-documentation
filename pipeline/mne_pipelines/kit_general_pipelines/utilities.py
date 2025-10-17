from dataclasses import dataclass, field, asdict
from typing import List, Dict

@dataclass(frozen=True)
class _NYUADKitConstants:

    # Trigger channels
    trigger_channels_MNE: List[str] = field(default_factory=lambda: [
        'MISC 001', 'MISC 002', 'MISC 003', 'MISC 004',
        'MISC 005', 'MISC 006', 'MISC 007', 'MISC 008'
    ])
    trigger_channels_KIT: List[int] = field(default_factory=lambda: [224, 225, 226, 227, 228, 229, 230, 231])

    # Plotting defaults
    DEFAULT_MISC_CHANNELS_AMPLITUDE_SCALE: float = 1.5
    DEFAULT_TIME_SCALE: float = 100.0

    # BIDS / file-naming constants (static for your setup)
    DATATYPE: str = "meg"
    MEG_EXTENSIONS: List[str] = field(default_factory=lambda: [".con"])
    HEAD_POSITION_INDICATOR_EXTENSIONS: List[str] = field(default_factory=lambda: [".mrk"])
    NOISE_PROCESSING_LABEL: str = "CALMnoisereduction"
    IGNORE_PROCESSING_LABEL: str = "CALMnoisereduction"
    HEADSHAPE_EXTENSIONS: List[str] = field(default_factory=lambda: [".txt"])
    ACQ_LABEL_DIGITIZER_POINTS: str = "points"
    ACQ_LABEL_DIGITIZER_HEAD: str = "head"
    TRIGGER_MODE: List[str] = field(default_factory=lambda: [
        "Single-channel trigger mode",
        "Binary-coded trigger mode"
    ])
    EVENTS_EXTENSIONS: List[str] = field(default_factory=lambda: [".csv"])
    METADATA_EXTENSIONS: List[str] = field(default_factory=lambda: [".json"])

    # Derived mappings
    KIT_from_MNE: Dict[str, int] = field(init=False)
    MNE_from_KIT: Dict[int, str] = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "KIT_from_MNE",
                           dict(zip(self.trigger_channels_MNE, self.trigger_channels_KIT)))
        object.__setattr__(self, "MNE_from_KIT",
                           dict(zip(self.trigger_channels_KIT, self.trigger_channels_MNE)))

    # Optional: quick dict view
    def asdict(self) -> Dict:
        return asdict(self)

# Single, shared instance to import elsewhere
NYUAD_KIT_CONSTANTS = _NYUADKitConstants()
