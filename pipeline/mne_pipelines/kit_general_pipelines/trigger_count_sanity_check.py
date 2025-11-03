from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

import numpy as np
import pandas as pd
import mne

PathLike = str | Path

__all__ = ["run_trigger_count", "read_expected_matrix"]



# Plot parameters: Make the plot viewable in an easier way

DEFAULT_MISC_CHANNELS_AMPLITUDE_SCALE = 1.5 #amplitude per division for the MISC channels
DEFAULT_TIME_SCALE = 100  #100 seconds per window


# ---------- I/O ----------

def _read_kit_con(confile: PathLike) -> mne.io.BaseRaw:
    confile = Path(confile)
    if not confile.exists():
        raise FileNotFoundError(f"CON file not found: {confile}")
    raw = mne.io.read_raw_kit(str(confile), preload=True, verbose="ERROR")
    return raw

def _pick_trigger_data(raw: mne.io.BaseRaw, channels: List[str]) -> Tuple[np.ndarray, float, List[int]]:
    all_names = np.array(raw.ch_names)
    idxs: List[int] = []
    for ch in channels:
        exact = np.where(all_names == ch)[0]
        if exact.size:
            idxs.append(int(exact[0]))
            continue
        cand = [i for i, nm in enumerate(all_names) if nm.endswith(ch)]
        if cand:
            idxs.append(cand[0])
            continue
        raise ValueError(f"Could not find trigger channel '{ch}' in raw.ch_names")
    data, _ = raw[idxs, :]
    return data, float(raw.info["sfreq"]), idxs

# ---------- Signal processing ----------

def _combine_bits(binary_data: np.ndarray, bit_order: str = "lsb_first") -> np.ndarray:
    n_bits, _ = binary_data.shape
    if bit_order == "lsb_first":
        weights = 2 ** np.arange(n_bits)
    elif bit_order == "msb_first":
        weights = 2 ** np.arange(n_bits - 1, -1, -1)
    else:
        raise ValueError("bit_order must be 'lsb_first' or 'msb_first'")
    return (weights[:, None] * binary_data.astype(int)).sum(axis=0)

def _debounce_stability(codes: np.ndarray, min_stable_win: int) -> np.ndarray:
    if min_stable_win < 1:
        raise ValueError("min_stable_win must be >= 1")
    n = codes.size
    if n == 0:
        return codes
    stable = np.zeros(n, dtype=int)
    cur = codes[0]
    count = 1
    stable[0] = cur
    for i in range(1, n):
        if codes[i] == cur:
            count += 1
        else:
            if count < min_stable_win:
                stable[i - count:i] = 0
            cur = codes[i]
            count = 1
        stable[i] = cur
    if count < min_stable_win:
        stable[n - count:n] = 0
    return stable

def _detect_transitions(stable_codes: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    diff_code = np.diff(stable_codes, prepend=stable_codes[0])
    change_idx = np.flatnonzero(diff_code != 0)
    onset_codes = stable_codes[change_idx]
    return change_idx, onset_codes

def _build_event_table(change_idx: np.ndarray, onset_codes: np.ndarray, sfreq: float) -> pd.DataFrame:
    onset_times = change_idx / sfreq
    return pd.DataFrame({
        "type": "trigger",
        "value": onset_codes,
        "sample": change_idx,
        "timestamp": change_idx,
        "offset": 0,
        "duration": 1,
        "time": onset_times,
    })

# ---------- Expected CSV ----------

def read_expected_matrix(csv_path: PathLike) -> np.ndarray:
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    df = pd.read_csv(csv_path)
    cols = [c.lower() for c in df.columns]
    if "code" in cols and ("expected" in cols or "expected_count" in cols):
        c_code = df.columns[cols.index("code")]
        c_exp = df.columns[cols.index("expected")] if "expected" in cols else df.columns[cols.index("expected_count")]
        return df[[c_code, c_exp]].to_numpy(dtype=int)
    if df.shape[1] >= 2:
        return df.iloc[:, :2].to_numpy(dtype=int)
    raise ValueError("CSV must have ['code','expected'|'expected_count'] or at least two columns")

# ---------- Public API ----------



import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

def read_expected_matrix_vi(
    csv_path: Path | str,
    *,
    bit_cols: Tuple[str, ...] = (
        "trigger224","trigger225","trigger226","trigger227",
        "trigger228","trigger229","trigger230","trigger231"
    ),
    count_col: str = "nTriggers",
    lsb_first: bool = True,
) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Parse a 'VI' CSV where each row defines an 8-bit trigger pattern and a count.

    Returns:
      - expected_mat: Nx2 ndarray [[code, expected_count], ...] (aggregated by code)
      - tidy_df:      DataFrame with columns ['code','expected','TrigType',<bit_cols>]
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Basic validation
    missing = [c for c in bit_cols if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing bit columns: {missing}")
    if count_col not in df.columns:
        raise ValueError(f"CSV missing count column: '{count_col}'")

    # Coerce bits to 0/1 (handle strings, floats, NaN)
    bits = df.loc[:, bit_cols].fillna(0).astype(int).clip(lower=0, upper=1).to_numpy()
    # Build weights (trigger224 is LSB by default)
    if lsb_first:
        weights = 2 ** np.arange(len(bit_cols))            # [1,2,4,...,128]
    else:
        weights = 2 ** np.arange(len(bit_cols)-1, -1, -1)  # [128,...,2,1]
    codes = (bits * weights).sum(axis=1)

    counts = df[count_col].fillna(0).astype(int).to_numpy()

    # Optional: keep TrigType if present
    trigtype = df["TrigType"] if "TrigType" in df.columns else pd.Series([None]*len(df))

    tidy = pd.DataFrame({
        "code": codes,
        "expected": counts,
        "TrigType": trigtype,
        **{c: df[c] for c in bit_cols},
    })

    # Aggregate by code (if CSV has multiple rows per code)
    agg = tidy.groupby("code", as_index=False)["expected"].sum()

    expected_mat = agg[["code", "expected"]].to_numpy(dtype=int)
    return expected_mat, tidy


def run_trigger_count(
    confile,
    csv_expected: Optional[str | Path] = None,
    *,
    channels=("MISC 001","MISC 002","MISC 003","MISC 004","MISC 005","MISC 006","MISC 007","MISC 008"),
    threshold=0.5,
    min_stable_win=5,
    bit_order="lsb_first",
    plot=False,
    return_figs=False,
    csv_format: str = "matrix",   # <-- NEW: "matrix" (old) or "vi" (new)
) -> Dict[str, Any]:
    """
    End-to-end trigger processing. Import-friendly.

    Returns dict with keys:
      - sfreq: float
      - num_sequences: int
      - events: pd.DataFrame
      - observed_counts: pd.DataFrame
      - comparison: pd.DataFrame  (if csv_expected provided)
      - stable_codes: np.ndarray
      - figs: dict[str, matplotlib.figure.Figure] (if return_figs=True and plot=True)
    """
    raw = _read_kit_con(confile)
    data, sfreq, idxs = _pick_trigger_data(raw, list(channels))

    # threshold to binary
    binary = (data > threshold).astype(int)

    # combine 8->1 and debounce
    codes_raw = _combine_bits(binary, bit_order=bit_order)
    stable_codes = _debounce_stability(codes_raw, min_stable_win=min_stable_win)

    # transitions
    change_idx, onset_codes = _detect_transitions(stable_codes)
    transitions = np.diff(stable_codes) != 0
    sequence_vals = stable_codes[np.r_[True, transitions]]
    sequence_vals = sequence_vals[sequence_vals != 0]
    num_sequences = int(sequence_vals.size)

    # events + observed counts
    events_df = _build_event_table(change_idx, onset_codes, sfreq)
    sequence_codes = onset_codes[onset_codes != 0]
    unique_codes, counts = np.unique(sequence_codes, return_counts=True)
    observed_df = pd.DataFrame({"TriggerCode": unique_codes, "ObservedCount": counts})

    out: Dict[str, Any] = {
        "sfreq": sfreq,
        "num_sequences": num_sequences,
        "events": events_df,
        "observed_counts": observed_df,
        "stable_codes": stable_codes,
    }

    if csv_expected is not None:
        if csv_format == "vi":
            expected_mat, tidy = read_expected_matrix_vi(csv_expected)
            # keep a copy for debugging / reports
            out["expected_tidy"] = tidy
        else:
            expected_mat = read_expected_matrix(csv_expected)

        obs_map = dict(zip(unique_codes.tolist(), counts.tolist()))
        cmp_rows = []
        for code, expect in expected_mat:
            actual = int(obs_map.get(int(code), 0))
            cmp_rows.append({
                "code": int(code),
                "expected": int(expect),
                "observed": actual,
                "ok": actual == int(expect),
            })
        out["comparison"] = pd.DataFrame(cmp_rows)






    # optional plotting
    if plot:
        import matplotlib
        import matplotlib.pyplot as plt

        #matplotlib.use('TkAgg')

        #meg_data_dir = '../egyptian_language_study/egyptian_sub009.con'
        #csv_file_experiment = '../egyptian_language_study/word_count_egyptian_list9.csv'

        #RAW_DATA = mne.io.read_raw_kit(meg_data_dir, preload=False, verbose=False)

        raw.get_channel_types

        raw.plot(picks=channels,
                 block=True,
                 scalings ={"misc": DEFAULT_MISC_CHANNELS_AMPLITUDE_SCALE},
                 duration = DEFAULT_TIME_SCALE)




        # figs: Dict[str, Any] = {}
        #
        # # MNE browser for the selected channels
        # fig_browser = raw.plot(picks=idxs, duration=30.0, n_channels=len(idxs), title="Trigger channels")
        # figs["browser"] = fig_browser
        #
        # # static overlay of raw trigger channels
        # times = np.arange(data.shape[1]) / sfreq
        # fig_static, ax = plt.subplots(figsize=(12, 4))
        # for i, ch in enumerate(channels):
        #     ax.plot(times, data[i, :], label=f"Ch {ch}")
        # ax.set_xlabel("Time (s)")
        # ax.set_ylabel("Amplitude")
        # ax.legend(loc="upper right")
        # ax.set_title("Trigger channels (raw)")
        # figs["raw_static"] = fig_static
        #
        # # plot combined stable code (scaled for visibility)
        # fig_code, ax2 = plt.subplots(figsize=(12, 3))
        # ax2.plot(times, stable_codes, linewidth=0.8)
        # ax2.set_xlabel("Time (s)")
        # ax2.set_ylabel("Code")
        # ax2.set_title("Combined trigger code (debounced)")
        # figs["stable_code"] = fig_code

        # if return_figs:
        #     out["figs"] = figs
        # else:
        #     # show non-blocking (so caller keeps control)
        #     import matplotlib
        #     # if running in scripts, this will still pop windows; caller can decide
        #     for f in figs.values():
        #         f.show()

    return out
