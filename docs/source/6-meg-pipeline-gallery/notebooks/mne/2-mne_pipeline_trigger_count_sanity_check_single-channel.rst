--------------------------------------------
Sanity check for single-channel trigger mode
--------------------------------------------

Author: Hadi Zaatiti <hadi.zaatiti@nyu.edu>

What & why
^^^^^^^^^^

The **single-channel trigger sanity check** validates that your NYUAD-KIT MEG dataset’s **trigger pulses** recorded on the analog MISC lines match the **event annotations** in your BIDS `*_events.tsv/.csv`.
It ensures that event timing and per-channel counts are consistent and that no pulses were lost, duplicated, or misaligned.

This check is **mandatory** for datasets acquired in **single-channel trigger mode**, where all trigger bits are serialized on a single analog channel.
Running it helps detect misconfigured conversions or timing drifts before downstream analysis.

What you need to provide
^^^^^^^^^^^^^^^^^^^^^^^^

Your dataset must include:

- **MEG recording files**

  .. code-block:: text

     sub-<id>/meg/sub-<id>_task-<task>_meg.con

- **Events table and JSON sidecar pair**

  .. code-block:: text

     sub-<id>/meg/sub-<id>_task-<task>_events.csv
     sub-<id>/meg/sub-<id>_task-<task>_events.json

  The JSON sidecar **must exist** and include:

  .. code-block:: json

     {
       "TriggerMode": "single_channel"
     }

  Without this exact `"TriggerMode": "single_channel"` key-value, the run will be **skipped automatically**.

Fallback hierarchy for events files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The script requires a **paired** `events.csv` (or `.tsv`) and `events.json` at the *same scope level*.
Both must exist and share the same entity pattern (subject/session/task/run).

The search hierarchy (most specific → least specific) is:

1. **Exact match:**
   ``sub-<id>[_ses-<id>]_task-<task>_run-<run>_events.*``

2. **Subject + task level:**
   ``sub-<id>[_ses-<id>]_task-<task>_events.*``

3. **Subject-only level:**
   ``sub-<id>[_ses-<id>]_events.*``
   *(applies to all tasks/runs for that subject)*

4. **Dataset root global pair:**
   ``events.csv`` + ``events.json`` at the dataset root
   *(applies to all subjects if nothing more specific exists)*

If any level provides **only one** of the two files (CSV/JSON), that level is ignored.
The first level containing both files is used, ensuring subject and task consistency.

Configuration file
^^^^^^^^^^^^^^^^^^

The script reads its configuration from a YAML file, typically:

.. code-block:: text

   pipeline/mne_pipelines/kit_general_pipelines/pipeline_config_files/config_template.yml

Example configuration
"""""""""""""""""""""

.. code-block:: yaml

   project:
     name: script-testing-dataset
     root_env: MEG_DATA        # environment variable for data location

   subjects:
     include: []               # empty → all subjects auto-discovered
     exclude: []

   bids_selection:
     sessions: []
     tasks: []
     runs: []

Define the environment variable before running:

.. code-block:: bash

   export MEG_DATA=/path/to/bids_root_parent

The dataset root will be resolved as:

.. code-block:: text

   $MEG_DATA/<project.name>

How to run
^^^^^^^^^^

Basic command
"""""""""""""

.. code-block:: bash

   python pipeline/mne_pipelines/kit_general_pipelines/sanity_single_channel_check.py \
       --config pipeline/mne_pipelines/kit_general_pipelines/pipeline_config_files/config_template.yml

This performs:

1. Configuration loading.
2. Subject and run discovery.
3. **Paired events file resolution** (CSV + JSON).
4. Skip if:
   - No valid events pair exists.
   - JSON doesn’t declare `"TriggerMode": "single_channel"`.
5. Pulse detection, event matching, and statistics output.

What the script does
^^^^^^^^^^^^^^^^^^^^

1. **Discovers** subjects and runs from your config.
2. **Resolves paired events files** (CSV+JSON) using the fallback hierarchy.
3. **Validates trigger mode** → skips non-single-channel runs.
4. **Detects trigger pulses** using robust thresholds:
   - Median + MAD on the *lower-tail* baseline distribution.
   - Hysteresis and debounce filtering for clean pulse isolation.
5. **Compares** detected pulses vs. event annotations:
   - Count differences per KIT trigger channel.
   - Sequence order consistency.
6. **Computes pulse statistics**:
   - Amplitude mean/variance.
   - Width mean/variance (temporal duration consistency).
7. **Generates logs and summary CSV** in derivatives.

Outputs
^^^^^^^

Derivative output directory
"""""""""""""""""""""""""""

.. code-block:: text

   <BIDS_ROOT>/derivatives/sanity_check/
     sub-<id>/[ses-<id>]/sub-<id>_..._desc-sanitycheck_log.txt
     sanity_check_overview.csv

Per-run log file contents
"""""""""""""""""""""""""

- Raw and events file paths
- TriggerMode value
- Thresholds per channel
- Count comparison (CSV vs. detected)
- Sequence check and mismatched channel info
- Pulse amplitude & width statistics
- Final PASS/FAIL summary

Example snippet
"""""""""""""""

.. code-block:: text

   [Thresholds per channel]
   channel_mne   thr_hi   thr_lo   n
   MISC001        0.45     0.36   400

   [Counts per KIT channel]
           csv_count  detected_count  diff
   224            80              80     0
   225            80              80     0
   ...

   [Overall pulse stats]
   amp_max_mean: 0.48 | width_ms_mean: 4.02 | width_ms_var: 0.003

Root-level summary table
"""""""""""""""""""""""""

.. code-block:: text

   sanity_check_overview.csv

Columns:

- ``subject``
- ``file``
- ``trigger_mode``
- ``csv_events`` / ``detected_events``
- ``counts_match`` / ``row_order_match`` / ``pass``
- ``log_file`` (points to the run’s text log)

Pass/Fail criteria
^^^^^^^^^^^^^^^^^^

A run **passes** only if:

1. Every KIT channel count matches the CSV exactly.
2. The detected chronological order matches the event file order.

Otherwise, the run is marked as **FAIL**.

Tuning & interpretation
^^^^^^^^^^^^^^^^^^^^^^^

Threshold parameters
""""""""""""""""""""

- ``absolute_floor`` (default: 0.3)
- ``mad_mult`` (default: 12.0)
- ``hysteresis_frac`` (default: 0.8)
- ``min_width_ms`` (default: 3.0)
- ``min_distance_ms`` (default: 6.0)
- ``baseline_q`` (default: 0.7)
- ``baseline_s`` (optional: (0.0, 10.0))

Interpretation
""""""""""""""

- **Stable amplitude & width** → reliable triggering.
- **Large width variance** → possible timing drift or noise.
- **Count mismatch** → event table misalignment.

Troubleshooting
^^^^^^^^^^^^^^^

Missing events pair
"""""""""""""""""""

If either the `.csv` or `.json` is missing, or they belong to different scopes,
the run will be skipped automatically with a warning.

Wrong TriggerMode
""""""""""""""""""

If `"TriggerMode"` is not `"single_channel"`, the run will be reported but not analyzed.

Count or sequence mismatch
""""""""""""""""""""""""""

Inspect the log for per-channel differences and event order mismatches.

Too many or too few pulses
""""""""""""""""""""""""""

Adjust `mad_mult`, `absolute_floor`, or `baseline_s` if necessary.

Console compatibility
"""""""""""""""""""""

On Windows, Unicode glyphs are replaced by ASCII-safe “OK”/“FAIL”.

Summary
^^^^^^^

This enhanced sanity check ensures that both your **event annotations** and **trigger signals** are perfectly synchronized.
It enforces strict validation for **single-channel trigger mode**, ensures correct CSV/JSON pairing, and automatically handles global vs. subject/task-specific event files.
Run it immediately after BIDS conversion to guarantee data integrity for all subsequent analyses.
