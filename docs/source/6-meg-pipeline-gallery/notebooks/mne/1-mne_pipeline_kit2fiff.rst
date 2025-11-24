----------------------
KIT to FIFF conversion
----------------------

Author: Hadi Zaatiti <hadi.zaatiti@nyu.edu>

What & why
----------

``kit2fiff_from_config.py`` converts NYUAD-KIT ``.con`` recordings into MNE
``.fif`` files while **preserving all BIDS entities** in the output filenames,
pairing **head-position marker** (``.mrk``) files deterministically, `headshape` head surface laser digitization and `headshape` laser points digitization
and storing results and logs under BIDS **derivatives**.

Use this after BIDS-structuring your KIT dataset to obtain analysis-ready
``.fif`` per run/split/processing, with clear provenance for which
**CON**, **MRK**, **HSP** (headshape) and **ELP** (digitizer points) were used.

Key features
------------

- **Entity preservation:** output names include *all* present entities
  (``sub``, ``ses``, ``task``, ``acq``, ``run``, **``split``**, ``rec``,
  ``space``, **``proc``**) plus ``desc-rawkit``.
- **Deterministic MRK pairing:** MRKs are ordered by ``acq-<n>``; for run-group *i*,
  use MRK[*i*] (before) and, if present, MRK[*i+1*] (after). If only MRK[*i*]
  exists, use it alone. **Never** reuse “way-before” MRKs for later runs.
- **Run/split ordering:** CONs are grouped by **run** and ordered by **split**;
  missing entities default to 0, so split-less data works seamlessly.
- **Session-aware HSP/ELP:** points and headshape are applied **per subject /
  session**; if session-specific files are absent, fallback to subject-level.
  These files **do not** include task/run in names, so they are never filtered by task/run.
- **Edited points once per scope:** creates a ``*_edited.txt`` (drops last 3 cols)
  and reuses it for all CONs in that subject/session.
- **Reproducible logging:** a root summary CSV and per-subject text logs recording,
  for each generated ``.fif``, the exact CON / MRK / HSP / ELP used.

What you need to provide
------------------------

A BIDS-like KIT dataset named following the BIDS standard and the additional NYUAD-naming constraints found at :ref:`data_naming`.



Configuration file
------------------

The script reads by default the template config:

.. code-block:: text

   pipeline/mne_pipelines/kit_general_pipelines/pipeline_config_files/config_template.yml

Provide your own configuration for your own dataset by providing the script with the argument `--config PATH_TO_YOUR_CONFIG`

Example configuration
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   project:
     name: script-testing-dataset
     root_env: MEG_DATA        # or set project.root_override to an absolute path

   subjects:
     include: []               # [] → discover all subjects
     exclude: []

   bids_selection:
     sessions: []              # [] / "" / null => not specified
     tasks: []
     runs: []
     splits: []
     processings: []

Environment
-----------

Set the base directory for your datasets:

.. code-block:: bash

   export MEG_DATA=/path/to/datasets_parent

The BIDS root resolves to:

.. code-block:: text

   $MEG_DATA/<project.name>

How to run
----------

Basic command
^^^^^^^^^^^^^

.. code-block:: bash

   python pipeline/mne_pipelines/kit_general_pipelines/kit_con_to_fif.py \
     --config pipeline/mne_pipelines/kit_general_pipelines/pipeline_config_files/config_template.yml

What the script does
--------------------

1. **Load config & locate BIDS root.**
2. **Discover subjects** (``include`` empty ⇒ all; ``exclude`` removed).
3. **Select runs** using optional ``sessions/tasks/runs/splits/processings``;
   empty arrays are treated as *not specified*.
4. **Order recordings**: group CONs by **run** (missing ⇒ 0), sort within group by **split** (missing ⇒ 0).
5. **Order MRKs**: sort by **``acq``**; pair per run-group:
   - group *i* → [MRK[*i*], MRK[*i+1*]] if both exist,
   - else [MRK[*i*]] if only one exists,
   - else skip group (no MRK for that group).
6. **Resolve HSP/ELP** per subject/session (never by task/run). If session-scoped files
   are absent, fallback to subject-level.
7. **Create edited points** once per (subject, session, source points) at:

   .. code-block:: text

      <BIDS_ROOT>/derivatives/kit2fiff/sub-<id>/[ses-<id>/]/*_edited.txt

8. **Read KIT and save FIFF** using the resolved MRK/HSP/ELP.
9. **Preserve entities in output names** (see below).
10. **Log** each conversion row into a root CSV and append a subject log.

File naming (entity preservation)
---------------------------------

All present entities are serialized in a stable order into the output name,
including **split** and **proc**, followed by ``desc-rawkit``:

.. code-block:: text

   sub-<id>[_ses-<id>][_task-<task>][_acq-<label>][_run-<n>][_split-<n>]
   [_rec-<label>][_space-<label>][_proc-<label>] _desc-rawkit_meg_raw.fif

Examples:

- No processing: ``sub-test1_task-400events_desc-rawkit_meg_raw.fif``
- With CALM: ``sub-test1_task-400events_proc-CALMnoisereduction_desc-rawkit_meg_raw.fif``
- With split: ``sub-01_task-rest_run-02_split-01_desc-rawkit_meg_raw.fif``

This guarantees **no overwrites** between processed/unprocessed or split variants.

Outputs
-------

Derivative directory layout
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   <BIDS_ROOT>/derivatives/kit2fiff/
     kit2fiff_summary.csv
     sub-<id>/
       kit2fiff_log.txt
       [ses-<id>/]
         sub-<id>[_ses-<id>]_..._desc-rawkit_meg_raw.fif
         sub-<id>[_ses-<id>]_acq-points_headshape_edited.txt

Root-level summary CSV
^^^^^^^^^^^^^^^^^^^^^^

``kit2fiff_summary.csv`` columns:

- ``timestamp``
- ``subject`` / ``session`` / ``run`` / ``split``
- ``con_path`` — input KIT file
- ``mrk_paths`` — semicolon-joined MRKs used for the run-group
- ``hsp_path`` — headshape file
- ``elp_points_edited`` — edited points used
- ``fif_out`` — output FIFF path (if success)
- ``status`` — ``success`` | ``error``
- ``error`` — error message if any

Per-subject log file
^^^^^^^^^^^^^^^^^^^^

``sub-<id>/kit2fiff_log.txt`` contains one block per converted run:

.. code-block:: text

   [2025-10-24T10:22:31] subject=test1 session= run=0 split=0
     CON : <...>/sub-test1_task-400events_meg.con
     MRK : <...>/sub-test1_task-rest_acq-1_space-ALS_markers.mrk
     HSP : <...>/sub-test1_acq-head_headshape.txt
     ELP*: <...>/sub-test1_acq-points_headshape_edited.txt  (*edited points)
     OUT : <...>/sub-test1_task-400events_desc-rawkit_meg_raw.fif
     STATUS: success

Edge cases & safeguards
-----------------------

- **Missing MRKs:** a run-group without MRKs is skipped (logged as a warning).
- **Single MRK for a group:** only that MRK is used (no “way-before” reuse).
- **Missing HSP/ELP:** that run is skipped with a warning.
- **Missing run/split:** treated as 0 (ordering still deterministic).
- **Edited points reuse:** cached per (subject, session, source points) to avoid rewriting.

Troubleshooting
---------------

- **No FIFFs created / empty summary:** check that your MEG ``.con`` files
  are discoverable under the selected entities and that MRKs exist.
- **Overwrites observed:** verify the output stems include the expected entities
  (especially ``proc`` and ``split``); the script’s builder preserves all.
- **Wrong HSP/ELP used:** ensure session-specific HSP/ELP exist if you expect per-session files;
  otherwise the subject-level fallback is used.

Testing
-------

A companion pytest can run the script on the **script-testing-dataset** and assert:

- Three FIFFs for ``sub-test1`` (proc and no-proc kept distinct),
- No rows for ``sub-test2`` (no MEG) and ``sub-test3`` (missing MRKs),
- Presence and structure of ``kit2fiff_summary.csv``,
- Presence of per-subject ``kit2fiff_log.txt`` with CON/MRK/HSP/ELP/OUT/STATUS lines.

Summary
-------

``kit2fiff_from_config.py`` produces **entity-faithful FIFFs**, applies
**before/after MRK pairing** by acquisition order, uses **session-aware**
headshape and points, generates minimal **edited points** once per scope,
and writes comprehensive **logs** to make the conversion fully auditable.
Run it early in your pipeline to lock in clean, reproducible inputs for MNE.```
