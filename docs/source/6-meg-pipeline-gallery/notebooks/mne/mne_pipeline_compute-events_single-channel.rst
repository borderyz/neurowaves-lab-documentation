====================================
Build events from single-channel TTL
====================================

Author: Hadi Zaatiti <hadi.zaatiti@nyu.edu>

What & why
----------

``kit_make_events_from_triggers.py`` detects TTL **trigger pulses** on the KIT
analog trigger lines (single-channel mode) and writes **MNE events** (``N×3``)
plus an **audit TSV**. It’s useful when your dataset’s primary ground-truth is
the **analog pulse stream**, and you want a clean, reproducible ``.eve`` file to
drive epoching downstream in MNE.

Key features
------------

- **Single-channel trigger mode only**: the script requires
  ``"TriggerMode": "single_channel"`` in the paired events JSON sidecar.
- **Robust pulse detection**: per-channel thresholds with an initial baseline
  window and hysteresis (via `detect_pulses_on_channel`).
- **Entity-aware naming**: output basenames include present BIDS entities
  (``sub``, ``ses``, ``task``, ``acq``, ``run``, ``proc``, ``rec``, ``split``)
  plus a configurable ``desc-<tag>`` (default: ``desc-autopulses``).
- **KIT-style event IDs**: the event code is the **KIT channel number**
  (``224..231``), so each pulse knows which physical line fired.
- **Indexing**: writes a root summary CSV listing all created outputs.

What you need to provide
------------------------

- **BIDS-structured KIT recordings**:

  .. code-block:: text

     sub-<id>/meg/sub-<id>[_ses-<id>]_task-<task>[_run-<run>][_split-<n>]_meg.con

- **Paired events table and JSON sidecar** (used to validate mode & scope):

  .. code-block:: text

     sub-<id>/meg/sub-<id>[_ses-<id>]_task-<task>[_run-<run>]__events.csv|.tsv
     sub-<id>/meg/sub-<id>[_ses-<id>]_task-<task>[_run-<run>]__events.json

  The JSON **must** contain:

  .. code-block:: json

     { "TriggerMode": "single_channel" }

The script resolves the **paired** (table + JSON) using the same joint-fallback
policy as the sanity checker (exact scope → subject+task → subject → dataset-root).

Configuration file
------------------

The script reads a YAML config, e.g.:

.. code-block:: text

   pipeline/mne_pipelines/kit_general_pipelines/pipeline_config_files/config_template.yml

Example configuration
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   project:
     name: script-testing-dataset
     root_env: MEG_DATA        # or use project.root_override

   subjects:
     include: []               # [] → discover all subjects
     exclude: []

   bids_selection:
     sessions: []              # [] / "" / null => not specified
     tasks: []
     runs: []

Environment
-----------

Define the base directory (parent of your datasets):

.. code-block:: bash

   export MEG_DATA=/path/to/datasets_parent

The BIDS root will be:

.. code-block:: text

   $MEG_DATA/<project.name>

How to run
----------

Basic command
^^^^^^^^^^^^^

.. code-block:: bash

   python pipeline/mne_pipelines/kit_general_pipelines/kit_make_events_from_triggers.py \
     --config pipeline/mne_pipelines/kit_general_pipelines/pipeline_config_files/config_template.yml

Optional arguments
^^^^^^^^^^^^^^^^^^

- ``--desc <tag>``: set the ``desc`` tag in outputs (default: ``autopulses``).
- ``--overwrite``: allow overwriting existing outputs.

What the script does
--------------------

1. **Load config & discover subjects/runs** with optional filters
   (empty arrays treated as *not specified*).
2. For each candidate run:
   - **Resolve a *paired* events table + JSON** using the joint fallback policy.
   - **Require** ``TriggerMode == "single_channel"``; otherwise **skip** run.
3. **Open KIT raw** with `mne.io.read_raw_kit` (no preload).
4. For each trigger MNE channel in `C.trigger_channels_MNE`:
   - **Detect pulses** with `detect_pulses_on_channel` (per-channel thresholds).
   - Map to **KIT channel number** (``224..231``) → event code.
5. **Assemble MNE events array** (``[sample, 0, event_id]``), sorted by sample.
6. **Build a BIDS-ish basename** from entities
   (``sub/ses/task/acq/run/proc/rec/split``) + ``desc-<tag>``.
7. **Write outputs** into ``derivatives/triggers_to_events``:
   - ``*.eve`` via `mne.write_events`
   - ``*_detail.tsv`` (audit: per-pulse metrics)
8. **Append root index CSV** (``auto_events_index.csv``) with one row per run.

File naming (entity preservation)
---------------------------------

Output basename includes present entities in a stable order, then
``desc-<tag>_events``. Examples:

- ``sub-test1_task-400events_desc-autopulses_events.eve``
- ``sub-01_ses-1_task-rest_run-02_split-01_proc-CALM_desc-autopulses_events.eve``

This avoids collisions between proc/no-proc and split variants.

Outputs
-------

Derivative directory layout
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   <BIDS_ROOT>/derivatives/triggers_to_events/
     auto_events_index.csv
     sub-<id>/
       [ses-<id>/]
         sub-<id>[_ses-<id>]_..._desc-<tag>_events.eve
         sub-<id>[_ses-<id>]_..._desc-<tag>_events_detail.tsv

Root index CSV columns
^^^^^^^^^^^^^^^^^^^^^^

- ``subject``
- ``file`` (input ``.con``)
- ``events_eve`` (output)
- ``detail_tsv`` (audit table)
- ``n_events`` (row count in ``.eve``)

Detection details TSV
^^^^^^^^^^^^^^^^^^^^^

- ``sample`` / ``onset_s``
- ``channel_mne`` / ``channel_kit`` (224..231)
- ``event_id`` (equals ``channel_kit``)
- ``width_ms`` / ``amp_max`` / ``amp_mean``

Edge cases & safeguards
-----------------------

- **Missing paired events files**: run is skipped (can’t confirm trigger mode).
- **TriggerMode ≠ single_channel**: run is skipped.
- **No pulses detected**: nothing is written for that run.
- **Overwrite protection**: existing ``.eve`` is preserved unless ``--overwrite`` is given.
- **Entity normalisation**: the script harvests entities from both
  ``raw_match.entities`` and explicit attributes to avoid missing ``proc``/``split``.

Troubleshooting
---------------

- **No outputs**: verify the paired events files exist at the same scope and
  that ``TriggerMode`` is correctly set to ``single_channel``.
- **Unexpected event counts**: inspect the ``*_detail.tsv`` and tune
  detection parameters in `detect_pulses_on_channel` if needed.
- **Filename collisions**: use a distinct ``--desc`` or confirm entities are
  present on your inputs (proc, split, run).

Summary
-------

This tool turns **analog trigger pulses** into canonical **MNE events**, with
clear, entity-rich filenames and an audit trail. It complements the sanity
checker by producing the actual ``.eve`` files you can feed directly to
epoching and downstream analyses.
