import mne
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from pipeline.mne_pipelines.kit_general_pipelines.utilities import *
# Use your preferred matplotlib backend
matplotlib.use('TkAgg')


# Sanity Check for combined_binary_mode and trigger count and preparation for MNE epoching

def compute_matrix_words(csv_filename):
    """
    Loads a CSV file which:
      - Has columns 'trigger224'..'trigger231' (the first-word triggers),
        columns 'trigger224w'..'trigger231w' (subsequent-word triggers),
        and a 'wordcount' column telling how many words in this row.
      - Returns expectedMatrix = [uniqueTriggerCode, expectedCount].

    For each row, we add 1 occurrence of the first-word code and
    (wordcount - 1) occurrences of the subsequent-word code (if wordcount > 1).
    """
    # 1) Read the CSV into a DataFrame
    df = pd.read_csv(csv_filename)

    # Define required columns
    first_word_cols = ["trigger224", "trigger225", "trigger226", "trigger227",
                       "trigger228", "trigger229", "trigger230", "trigger231"]
    word_cols = ["trigger224w", "trigger225w", "trigger226w", "trigger227w",
                 "trigger228w", "trigger229w", "trigger230w", "trigger231w"]

    # Check for required columns
    missing_first = [col for col in first_word_cols if col not in df.columns]
    missing_word = [col for col in word_cols if col not in df.columns]
    if missing_first:
        raise ValueError("CSV must contain columns: " + ", ".join(first_word_cols))
    if missing_word:
        raise ValueError("CSV must contain columns: " + ", ".join(word_cols))

    # Ensure the CSV has a 'wordcount' column
    if "wordcount" not in df.columns:
        raise ValueError('CSV must contain a "wordcount" column (integer number of words).')

    # 2) Ensure the 'wordcount' column is numeric
    df["wordcount"] = pd.to_numeric(df["wordcount"], errors="coerce")
    if df["wordcount"].isnull().any():
        raise ValueError('The "wordcount" column contains invalid or non-numeric entries.')

    # 3) Extract the bit columns into matrices (as NumPy arrays)
    bitDataFirst = df[first_word_cols].values  # shape (N, 8)
    bitDataOther = df[word_cols].values  # shape (N, 8)

    # 4) Decode these bits into integer trigger codes
    # Bit weights: flip(2.^(0:7))' gives [128, 64, 32, 16, 8, 4, 2, 1]
    bit_weights = np.array([128, 64, 32, 16, 8, 4, 2, 1]).reshape(8, 1)
    codeFirst = (bitDataFirst.dot(bit_weights)).flatten()  # shape (N,)
    codeOther = (bitDataOther.dot(bit_weights)).flatten()  # shape (N,)

    # 5) Accumulate counts in a dictionary (map: code -> occurrences)
    codeCounts = {}
    for idx in range(len(df)):
        nWords = df.iloc[idx]["wordcount"]
        # If at least 1 word, add first-word trigger
        if nWords >= 1:
            c = codeFirst[idx]
            codeCounts[c] = codeCounts.get(c, 0) + 1
        # If more than 1 word, add subsequent-word triggers
        if nWords > 1:
            c = codeOther[idx]
            codeCounts[c] = codeCounts.get(c, 0) + (nWords - 1)

    # 6) Convert the dictionary to a matrix [triggerCode, expectedCount]
    uniqueCodes = np.array(sorted(codeCounts.keys()))
    expectedCounts = np.array([codeCounts[code] for code in uniqueCodes])
    expectedMatrix = np.column_stack((uniqueCodes, expectedCounts))

    # Display results
    print("\n--- Computed expectedMatrix from CSV (TriggerCode, Count) ---")
    print(pd.DataFrame(expectedMatrix, columns=["TriggerCode", "ExpectedCount"]))

    return expectedMatrix


# -----------------------------
# Parameters and File Paths
# -----------------------------
meg_data_dir = 'egyptian_sub009.con'
csv_file_experiment = 'word_count_egyptian_list9.csv'
threshold_value = 0.5    # Voltage threshold for binarizing analog trigger channels
min_stable_win = 20       # Minimum consecutive samples to accept a change

# -----------------------------
# 1. Read Raw Data and Select Trigger Channels
# -----------------------------
# Read KIT data file (ensure preload=True so data is in memory)
raw = mne.io.read_raw_kit(input_fname=meg_data_dir, preload=True, verbose=False)

# Define trigger channels (order should match the bit weight assumption)


# Extract data from the specified channels (shape: n_channels x n_samples)
raw_triggers = raw.copy().pick_channels(trigger_channels)
data = raw_triggers.get_data()  # analog data for the 8 channels

# -----------------------------
# 2. Binarize the Analog Data
# -----------------------------
binary_data = data > threshold_value  # shape: (8, n_samples)

# -----------------------------
# 3. Combine Binary Channels into a Single Trigger Code
# -----------------------------
bit_weights = np.array([128, 64, 32, 16, 8, 4, 2, 1]).reshape(-1, 1)  # shape (8, 1)
trigger_code_raw = np.dot(bit_weights.T, binary_data).flatten()  # shape: (n_samples,)

# -----------------------------
# 4. Debounce the Trigger Signal (Stability Check)
# -----------------------------
N = trigger_code_raw.shape[0]
stable_codes = np.zeros(N, dtype=int)
stable_codes[0] = trigger_code_raw[0]
current_code = trigger_code_raw[0]
count_stable = 1

for i in range(1, N):
    if trigger_code_raw[i] == current_code:
        count_stable += 1
    else:
        # If the new code did not last for the minimum stable window, revert the previous samples to 0
        if count_stable < min_stable_win:
            stable_codes[i - count_stable:i] = 0
        # Update current code and reset the count
        current_code = trigger_code_raw[i]
        count_stable = 1
    stable_codes[i] = current_code

# -----------------------------
# 5. Detect Trigger Onsets
# -----------------------------
diff_code = np.diff(stable_codes, prepend=stable_codes[0])
change_idx = np.where(diff_code != 0)[0]

onset_codes = stable_codes[change_idx]
nonzero_mask = onset_codes != 0
onset_codes = onset_codes[nonzero_mask]
change_idx = change_idx[nonzero_mask]
onset_times = change_idx / raw.info['sfreq']  # Convert sample indices to seconds

events = []
for sample, code, time in zip(change_idx, onset_codes, onset_times):
    event_dict = {
        'type': 'trigger',
        'value': int(code),
        'sample': int(sample),
        'timestamp': int(sample),
        'offset': 0,
        'duration': 1,
        'time': time
    }
    events.append(event_dict)

print(f"Number of events detected: {len(events)}")

# -----------------------------
# 6. Load Expected Trigger Counts from CSV
# -----------------------------
expected_matrix = compute_matrix_words(csv_file_experiment)
# Convert expected_matrix to a dictionary for easier comparison:
expected_dict = {int(code): int(count) for code, count in expected_matrix}

# -----------------------------
# 7. Tally Observed Trigger Counts and Compare to Expected
# -----------------------------
observed_counts = {}
for ev in events:
    code = ev['value']
    observed_counts[code] = observed_counts.get(code, 0) + 1

print('----------------------------------')
print('Observed counts of each trigger code (after stabilization):')
print(observed_counts)
print('----------------------------------')

for code, expected_count in expected_dict.items():
    observed_count = observed_counts.get(code, 0)
    if observed_count == expected_count:
        print(f"Code {code}: OK (observed {observed_count}, expected {expected_count})")
    else:
        print(f"Code {code}: MISMATCH (observed {observed_count}, expected {expected_count})")




mne_events = np.zeros((len(events), 3), dtype=int)
for idx, ev in enumerate(events):
    mne_events[idx, 0] = ev['sample']  # sample index
    mne_events[idx, 1] = 0             # typically 0 (no previous trigger info)
    mne_events[idx, 2] = ev['value']     # trigger code (event id)

print("MNE events array shape:", mne_events.shape)






