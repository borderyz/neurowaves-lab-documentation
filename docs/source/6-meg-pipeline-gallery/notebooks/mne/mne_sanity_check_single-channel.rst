--------------------------------------------
Sanity check for single-channel trigger mode
--------------------------------------------


Author: Hadi Zaatiti <hadi.zaatiti@nyu.ed>


What & why
^^^^^^^^^^

The **single-channel trigger sanity check** verifies that your NYUAD-KIT MEG dataset’s **trigger pulses** recorded on the analog MISC lines match the **event annotations** in your BIDS `*_events.tsv/.csv`.
It ensures that your dataset’s event timing and channel counts are valid and that no pulses were lost, duplicated, or misaligned.

This step is **mandatory** for datasets acquired in **single-channel trigger mode**, where all trigger lines are encoded sequentially on a single analog channel.
Running this check prevents analysis errors due to incorrect event ordering or timing drift.

What you need to provide
^^^^^^^^^^^^^^^^^^^^^^^^

Your dataset must include:

- **MEG recording files**

  .. code-block:: text

     sub-<id>/meg/sub-<id>_task-<task>_meg.con

- **Events file**

  .. code-block:: text

     sub-<id>/meg/sub-<id>_task-<task>_events.tsv
     # or .csv

- **Mandatory JSON sidecar**
  The JSON file defines the trigger mode and **must** specify `"TriggerMode": "single-channel"`.
  Without this, the run will be **skipped** automatically (the check applies only to single-channel mode).

  .. code-block:: text

     sub-<id>/meg/sub-<id>_task-<task>_events.json

  Example content:

  .. code-block:: json

     {
       "TriggerMode": "single-channel"
     }

Configuration file
^^^^^^^^^^^^^^^^^^

The script reads its configuration from a YAML file, typically located at:

.. code-block:: text

   pipeline/mne_pipelines/kit_general_pipelines/pipeline_config_files/config_template.yml

This file defines the dataset, subjects, and optional filtering settings.

Example configuration
"""""""""""""""""""""

.. code-block:: yaml

   project:
     name: script-testing-dataset
     root_env: MEG_DATA        # You must have an environment variable that points to the directory where your dataset root folder is

   subjects:
     include: []               # empty → all subjects auto-discovered
     exclude: []

   bids_selection:
     sessions: []
     tasks: []
     runs: []

If using ``root_env``, define the environment variable before running:

.. code-block:: bash

   export MEG_DATA=/path/to/bids_root_parent

The BIDS root will be resolved as:

.. code-block:: text

   $MEG_DATA/<project.name>

How to run
^^^^^^^^^^

Basic command
"""""""""""""

.. code-block:: bash

   python pipeline/mne_pipelines/kit_general_pipelines/sanity_single_channel_check.py \
       --config pipeline/mne_pipelines/kit_general_pipelines/pipeline_config_files/config_template.yml

This will automatically:

1. Load your configuration.
2. Find all subjects and runs.
3. Skip any run whose `*_events.json` is missing or not `"TriggerMode": "single-channel"`.
4. Detect pulses, compare with the events table, and compute statistics.


What the script does
^^^^^^^^^^^^^^^^^^^^

1. **Discovers** all subjects/runs matching your config.
2. **Validates trigger mode** using the events JSON (only “single-channel” runs are processed).
3. **Detects trigger pulses** in MISC channels using adaptive thresholds:
   - Median + MAD computed on the *lower amplitude tail* of the baseline (robust to pulse contamination).
   - Includes hysteresis, width, and debounce filtering.
4. **Compares** detected pulses with the events file:
   - Count differences per KIT trigger channel.
   - Sequence order (chronological pulses vs. event table order).
5. **Computes pulse statistics**:
   - Amplitude (mean, variance, max)
   - Width (mean, variance, min, max)
   - Stability across channels
6. **Summarizes results** into log files and one summary CSV.


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

- Paths to raw and events files
- Trigger mode confirmation
- Thresholds per MNE channel
- Counts comparison table
- Sequence check results (and sequences if mismatched)
- Pulse amplitude and width statistics (per channel and overall)
- Final PASS/FAIL summary

Example snippet from a log file:

.. code-block:: text

   [Thresholds per channel]
   channel_mne   thr_hi   thr_lo   n
   MISC001        0.45     0.36   400

   [Counts per KIT channel]
           csv_count  detected_count  diff
   224            80              80     0
   225            80              80     0
   ...

   [Pulse amplitude & width stats per KIT channel]
            n_pulses  amp_max_mean  amp_max_var  width_ms_mean  width_ms_var
   224           80          0.49        0.001          4.01        0.002
   ...

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
- ``log_file`` (path to corresponding log)

Pass/Fail criteria
^^^^^^^^^^^^^^^^^^

A run **passes** only if:

1. All per-channel event counts match exactly.
2. The detected chronological order matches the CSV row order.

Tuning & interpretation
^^^^^^^^^^^^^^^^^^^^^^^

You do not need to change any of the default values in the script unless you think there is a good reason for it.
The following is provided only for information.

Threshold parameters (in-script)
""""""""""""""""""""""""""""""""

- ``absolute_floor`` (default: 0.3) → minimum threshold floor
- ``mad_mult`` (default: 12.0) → multiplier for MAD noise estimate
- ``hysteresis_frac`` (default: 0.8) → fraction for low threshold
- ``baseline_s`` (optional) → baseline window (e.g., (0.0, 10.0))
- ``baseline_q`` (default: 0.7) → quantile limit for baseline pool
- ``min_width_ms`` (default: 3.0) → reject spikes
- ``min_distance_ms`` (default: 6.0) → debounce spacing

Interpreting pulse stats
""""""""""""""""""""""""

- **amp_max_mean / amp_mean_mean**: measure signal strength; high variance suggests unstable amplifier scaling.
- **width_ms_mean / width_ms_var**: uniform width = consistent trigger pulses.
  Wide variation = possible timing drift or clipping.

Troubleshooting
^^^^^^^^^^^^^^^

Skipped run (not single-channel)
""""""""""""""""""""""""""""""""

- Ensure your `*_events.json` includes `"TriggerMode": "single-channel"`.
  Runs missing this key will be **skipped** automatically.

No MEG files found
""""""""""""""""""

- Check your ``project.name`` and ``root_env`` or ``root_override`` in the config.
- Ensure `.con` files exist under `sub-*/meg/`.

Count mismatch or sequence mismatch
"""""""""""""""""""""""""""""""""""

- Inspect the per-run log for details.
  - Channels with mismatched counts are listed.
  - Sequence mismatches include both the CSV and detected sequences.

Too few or too many pulses
""""""""""""""""""""""""""

- Adjust detection parameters (`mad_mult`, `absolute_floor`, `min_width_ms`).
- Provide a cleaner baseline window (`baseline_s`) if the early segment is noisy.

Windows console output
""""""""""""""""""""""

- The script automatically switches to ASCII (“OK” / “FAIL”) if the console doesn’t support Unicode checkmarks.


Summary
^^^^^^^

This sanity check provides a **quantitative validation** that your MEG triggers and events tables are synchronized, consistent, and reliable.
Always run it after dataset conversion to BIDS before proceeding to downstream MNE or FieldTrip analyses.
