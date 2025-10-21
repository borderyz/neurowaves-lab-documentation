import sys

from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict

import mne
from mne_bids import find_matching_paths
import numpy as np



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



def bids_name_from_entities(entities: dict, suffix: str, ext: str = "") -> str:
    parts = []
    if entities.get("subject"): parts.append(f"sub-{entities['subject']}")
    if entities.get("session"): parts.append(f"ses-{entities['session']}")
    if entities.get("task"): parts.append(f"task-{entities['task']}")
    if entities.get("run"): parts.append(f"run-{entities['run']}")
    if suffix: parts.append(suffix)
    name = "_".join(parts)
    return name + ext

def write_run_log(log_path: Path, text: str):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(text, encoding="utf-8")

def _glyph(ok: bool) -> str:
    """Windows-safe status glyph."""
    enc = (sys.stdout.encoding or "").lower()
    if "utf" in enc:
        return "✅" if ok else "❌"
    return "OK" if ok else "FAIL"

# -------------------------------
# Pairing helpers
# -------------------------------

def _entities_exact_match(candidate, scope):
    """
    Return True iff the candidate's entities match the scope *exactly*:
      - If scope[k] is None -> candidate must NOT have that entity.
      - If scope[k] has a value -> candidate must have the same value.
    """
    ents = (getattr(candidate, "entities", None) or {})
    for k in ("subject", "session", "task", "acquisition", "run"):
        want = scope.get(k)
        have = ents.get(k)
        if want is None:
            if have is not None:
                return False
        else:
            if have != want:
                return False
    return True


def _first_matching_path_exact(
    *, subjects, sessions, tasks, acquisitions, runs, extensions, datatypes
):
    """
    Find the first file whose entities match the query *exactly*.
    If a scope key is None, the candidate must *not* have that entity.
    """
    cands = find_matching_paths(
        bids_root,
        datatypes=datatypes,
        subjects=subjects,
        sessions=sessions,
        tasks=tasks,
        acquisitions=acquisitions,
        runs=runs,
        extensions=extensions,
        suffixes="events",
    )
    if not cands:
        return None

    scope = dict(subject=subjects, session=sessions, task=tasks,
                 acquisition=acquisitions, run=runs)

    for cand in cands:
        if _entities_exact_match(cand, scope):
            return cand.fpath
    return None

def resolve_events_pair_with_joint_fallback(raw_match):
    """
    Return (events_table_path, events_json_path, scope_dict) where table (.tsv/.csv)
    and JSON sidecar exist and share the SAME entity scope.

    Fallback order (most specific → least), always keeping subject/session fixed until dataset root:
      1) exact: subject[/session][task][run][acq]
      2) subject[/session][task]         (drop run,acq)
      3) subject[/session]               (drop task,run,acq)
      4) dataset root                    (no subject/session/task/run/acq)

    Rules:
      - Never borrow files from another subject/session/task/run.
      - Accept a level only if BOTH the table and JSON exist at that same level.
      - Dataset-root files must have NO entities (apply to all data).
    """
    e = raw_match.entities or {}
    subj = e.get("subject")
    sess = e.get("session")
    task = e.get("task")
    run  = e.get("run")
    acq  = e.get("acquisition")

    # Build candidate scopes (most specific → least)
    scopes = [
        dict(subject=subj, session=sess, task=task, run=run, acquisition=acq),
        dict(subject=subj, session=sess, task=task, run=None, acquisition=None),
        dict(subject=subj, session=sess, task=None, run=None, acquisition=None),
        dict(subject=None, session=None, task=None, run=None, acquisition=None),  # dataset root
    ]

    for scope in scopes:
        at_root = all(scope.get(k) is None for k in ("subject","session","task","run","acquisition"))
        dtype = None if at_root else NYUAD_KIT_CONSTANTS.DATATYPE  # search whole dataset at root

        # Table
        tbl = _first_matching_path_exact(
            subjects=scope["subject"],
            sessions=scope["session"],
            tasks=scope["task"],
            acquisitions=scope["acquisition"],
            runs=scope["run"],
            extensions=tuple(NYUAD_KIT_CONSTANTS.EVENTS_EXTENSIONS),
            datatypes=dtype,
        )
        if not tbl and at_root:
            # Explicit root fallback: events.csv/tsv sitting at BIDS root
            for ext in (".csv", ".tsv"):
                cand = Path(bids_root) / f"events{ext}"
                if cand.exists():
                    tbl = str(cand)
                    break
        if not tbl:
            continue  # need a PAIR at this scope

        # JSON
        js = _first_matching_path_exact(
            subjects=scope["subject"],
            sessions=scope["session"],
            tasks=scope["task"],
            acquisitions=scope["acquisition"],
            runs=scope["run"],
            extensions=tuple(NYUAD_KIT_CONSTANTS.METADATA_EXTENSIONS),
            datatypes=dtype,
        )
        if not js and at_root:
            cand = Path(bids_root) / "events.json"
            if cand.exists():
                js = str(cand)
        if not js:
            continue  # require a PAIR at the same scope

        # Pair found at the same scope
        return tbl, js, scope

    # No paired files at any scope
    return None, None, None


# -------------------------------
# Pulse detector (robust thresholds + metrics)
# -------------------------------
def detect_pulses_on_channel(
    raw, ch_name,
    absolute_floor=0.3,
    mad_mult=12.0,
    hysteresis_frac=0.8,
    min_width_ms=3.0,
    min_distance_ms=6.0,
    baseline_s=None,
    baseline_q=0.7,      # use only lower tail (<= quantile) for baseline
    min_baseline_n=256   # minimum samples required in baseline pool
):
    """
    Detect digital-like trigger pulses on a single MNE Raw channel using
    trimmed (lower-tail) robust thresholding, hysteresis, and debouncing.

    Returns:
      pulses_idx (np.ndarray): start sample indices of accepted pulses.
      thr_hi (float): high threshold.
      thr_lo (float): low threshold (hysteresis).
      pulse_metrics (list[dict]): one dict per pulse with:
         - start (int): start sample
         - end (int): end sample (first sample below thr_lo)
         - width_samp (int)
         - width_ms (float)
         - amp_max (float): max |amplitude| within [start:end)
         - amp_mean (float): mean |amplitude| within [start:end)
    """
    sfreq = raw.info['sfreq']
    min_width_samp = max(1, int(round((min_width_ms / 1000.0) * sfreq)))
    min_distance_samp = max(1, int(round((min_distance_ms / 1000.0) * sfreq)))

    pick = mne.pick_channels(raw.ch_names, [ch_name])
    if len(pick) == 0:
        raise ValueError(f"Channel '{ch_name}' not found in raw.")
    x = raw.get_data(picks=pick, reject_by_annotation='omit')[0]

    # Threshold estimation segment
    if baseline_s is not None:
        start_s, stop_s = baseline_s
        start = max(0, int(round(start_s * sfreq)))
        stop  = min(len(x), int(round(stop_s * sfreq)))
        xb = x[start:stop] if stop > start else x
    else:
        xb = x

    # Lower-tail robust baseline
    ax = np.abs(xb)
    if ax.size == 0:
        raise RuntimeError("Empty data segment for threshold estimation.")
    baseline_q = float(baseline_q)
    baseline_q = 0.99 if baseline_q > 0.99 else (0.01 if baseline_q < 0.01 else baseline_q)
    qv = np.quantile(ax, baseline_q)
    pool = ax[ax <= qv]
    if pool.size < min_baseline_n:
        qv2 = np.quantile(ax, 0.9)
        pool = ax[ax <= qv2]
        if pool.size < min_baseline_n:
            pool = ax  # last resort

    med = np.median(pool)
    mad = np.median(np.abs(pool - med)) + 1e-12

    thr_hi = max(absolute_floor, med + mad_mult * mad)
    thr_lo = hysteresis_frac * thr_hi

    # Hysteretic detection + per-pulse metrics
    pulses = []
    metrics = []
    i = 1
    n = x.size
    last_accept = -10**9

    while i < n:
        if x[i - 1] < thr_hi <= x[i]:
            start_i = i
            while i < n and x[i] >= thr_lo:
                i += 1
            end_i = i  # first sample below thr_lo
            width = end_i - start_i
            if width >= min_width_samp and (start_i - last_accept) >= min_distance_samp:
                pulses.append(start_i)
                last_accept = start_i

                seg = np.abs(x[start_i:end_i]) if end_i > start_i else np.empty(0, dtype=float)
                amp_max = float(np.max(seg)) if seg.size else 0.0
                amp_mean = float(np.mean(seg)) if seg.size else 0.0
                width_ms = (width / sfreq) * 1000.0

                metrics.append({
                    "start": int(start_i),
                    "end": int(end_i),
                    "width_samp": int(width),
                    "width_ms": float(width_ms),
                    "amp_max": amp_max,
                    "amp_mean": amp_mean,
                })
        else:
            i += 1

    return np.asarray(pulses, dtype=int), float(thr_hi), float(thr_lo), metrics