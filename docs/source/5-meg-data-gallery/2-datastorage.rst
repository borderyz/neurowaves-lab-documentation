-----------------------
Data Naming and Storing
-----------------------

.. contents::
   :local:
   :depth: 4


Data Naming and Storing: MEG
^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Data host
"""""""""

The MEG data is securely stored on NYU BOX, access is given through invitations.
The *Data* folder is structured in the **BIDS** standardized format.
Please raise an issue on *github* repository if you think the structure does not conform to **BIDS**.

Sign in on NYU Box in the below link

.. admonition:: Link to MEG data (Box Invitation Only)

    `https://nyu.box.com/v/meg-datafiles <https://nyu.box.com/v/meg-datafiles>`_


Or directly from the below widget

.. raw:: html

    <iframe src="https://nyu.app.box.com/embed/s/wefkhu5yn7tzzhw2gcr45zvnsqqnbyuf?sortColumn=name&expandSidebars=true" width="650" height="550" frameborder="0" allowfullscreen webkitallowfullscreen msallowfullscreen></iframe>

If you are unable to access the datasets it means you do not have the permission to. Kindly send an email to `nyuad.meg@nyu.edu`



Data naming BIDS protocol
"""""""""""""""""""""""""

A typical MEG dataset from NYUAD contains the following files and folders in BIDS-specification `https://bids-specification.readthedocs.io/ <https://bids-specification.readthedocs.io/>`_ :

Your data should be stored in the BIDS format.
Find a template to be used under `bids-template`, the template contains all the information that you should have in each file.

In the following, [SUB_ID] should be replaced with the ID of the subject for naming purposes.
The different data files generated from a MEG experiment are the following.

.. note::
    If you have found a bug in the BIDS naming format please raise an issue on github
    or create a pull request with your proposed modifications.


Directory structuring
~~~~~~~~~~~~~~~~~~~~~

Your file structure should look like this:

- **root** level directory named after your project 'PROJECT_NAME'
- within the **root** directory, you should have:
    - `README.md`: general information on your project
    - `dataset_description.json`: a `JSON` object detailing authors, project name, grants and so on
    - `sub-[SUB_ID]`: a folder for each subject, within which there should be:
        - Optionally a `ses-[SES_ID]` where SES_ID is a numeric session ID, inside which you will find:
            - `meg` (must have one): will contain your MEG data and other meta-data
            - `sourcedata` (not necessary)
        - If the `ses-[SES_ID]` folder is not there, it means you do not have multiple sessions for the subject, in that case you will directly find `meg` and `sourcedata` within the `sub-[SUB_ID]` folder

Additionally, it can have:
    - `events.json` should have meta-data about the device used for presenting Stimulus
    - `events.tsv` should have information about the types of trials, onset and duration
    - `task-[PROJECT_NAME]_meg.json` should have information about the MEG system used, sampling frequency and so on

If the three above files are not found at the root of your dataset, it means that each subject or session might have a specific configuration, in that case make sure to have these files within the subject or session, while adding the sub/ses ID's to the name of the file.
The three above files can be found at the root of your dataset, while having the same files within each session/subject under the following condition:
- when some parameters are specified at the level of the dataset, while other are specific for the session/subject

.. note::
    General BIDS notes:
    - If a particular file applies to all runs, then it should not have the `run` descriptor in its name
    - If a particular file applies to all sessions, then it should not have the `ses` descriptor in its name

MEG-Laserscan files
~~~~~~~~~~~~~~~~~~~

#. A `.fsn` filename that should be named ``sub-\[SUB_ID\]_acq-laserproject_headshape.fsn`` : This file is obtained by saving the whole fastscan laser project (File Save)
    * The `.fsn` file is stored under `sourcedata`

#. Two .txt files holding the head surface scan and stylus points should be named:
    * ``sub-001_ses-01_acq-head_headshape.txt``  is the head scan of the participant
    * ``sub-001_ses-01_acq-points_headshape.txt`` is the stylus points location file of the participant
        - all should be stored under `meg`


MEG-KIT files
~~~~~~~~~~~~~

Depending on the experiment, many .con files can be produced by the KIT machine.

#. .con files are named:
    * ``sub-[SUB_ID]_ses-[SES_ID]_task-[TASK_NAME]_run-[RUN_ID]_meg.con``
    * example: `sub-001_ses-01_task-audiovisualmotor_run-03_meg.con`
    * if you applied the `CALM` filtering or other kind of pre-processing to your con file then:
        * sub-[SUB_ID]_task-[TASK_NAME]_proc-CALMnoisereduction_meg.con or replace the `proc` value with the name of your filter
        * Example: ``sub-001_task-attention_proc-CALMnoisereduction_meg.con``
    * all `.con` files should be stored under `meg`

#. .mrk files are named:
    * ``sub-[SUB_ID]_ses-[SES_ID]_task-rest_acq-[MARKER_ORDER_NUMBER]_space-ALS_markers.mrk`` where:
        * [MARKER_ORDER_NUMBER] is the chronological order in which the marker has been acquired at in that session
        * The `task` should be set to `rest` because there is no stimuli events involved (if not we get warning from the BIDS-Validator)
        * The `space` refers to the coordinate system type, for Yokogawa/KIT it is Anterior on X-axis, Left on Y-axis, Superior on Z-axis, therfore it is ALS
    * all `.con` files should be stored under `meg`

.. note::
        - The `ses` is optional, but must be present if the same subject had multiple sessions
        - The `run` is optional, but must be present if in the same session, a subject had multiple MEG acquisitions leading to multiple `.con` files




MEG-OPM files
~~~~~~~~~~~~~

The OPM system generates a BIDS directory with the .fif files

#. The generated .fif files are named:
   * ``sub-[SUB_ID]_ses-[SES_ID]_meg_raw.fif``


Data uploading
""""""""""""""

Data will be uploaded to NYU BOX, to the following link

.. admonition:: Link to MEG data (Box Invitation Only)

    `https://nyu.box.com/v/meg-datafiles <https://nyu.box.com/v/meg-datafiles>`_

Steps

#. Access the folder of NYU Box
#. Identify the project that the data belongs to, or request for a new project folder
#. Access the folder for that project or create a new folder if non-existent
#. Follow the BIDS structure format described above, within each project file,
#. Make sure that all files have been uploaded to the folder


Data Naming and Storing: MRI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MRI data is hosted on XNAT

.. admonition:: Link to MRI data (Access given after requesting and upon eligibility)

    `https://xnat.abudhabi.nyu.edu/#/login <https://xnat.abudhabi.nyu.edu/#/login>`_
    Contact the xnat administrator `admin.nyuad.xnat@nyu.edu`


