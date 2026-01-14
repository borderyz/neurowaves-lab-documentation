------------
Contributing
------------

After building an initial draft of your experiment code and you wish to start testing it, collect all the files relative to your experiment into one directory, name your directory as the name of your experiment.
The contribution will be submitted for review through github. If you already have a github account sign in to it, if not create a github account.

- Fork the current repository to your account
- On the created fork, create a new branch named with the feature you are developping or change you are making
- Add the directory containing the files of your experiment under the `experiments/psychopy` or `experiments/psychtoolbox` according to which framework you are using.
- Create a pull request from your branch to the main branch of the source repository (Not your fork, but the original repo)
- Add any comments you want the reviewer to know of
- A reviewer will review your code and either approve or ask for changes
- If changes are needed, make the changes and push your new code to the same branch, your PR (Pull Request) will then get automatically updated
- Consider adding a page describing your experiment to the `docs\source\3-experimentdesign\experiments`
- Once your branch is merged to the main branch (meaning your experiment is approved), your code will be available in the MEG lab Stimulus computer

Building your processing pipeline
=================================

Do the same steps as before to fork the repository and create a new branch named as `experiment_name-analysis`
Submit an initial notebook under `docs/source/5-pipeline/notebooks` or simply code file for your pipeline under `pipeline\experiment_name`



Contributing to this repository Overview
========================================

Your contribution, mistake correction, code contributions are very welcome.
Contributions are made through pull reqests, please do the following steps:

- Fork the current repository to your account
- Create a new branch named with the feature you are developping or change you are making
- Make the change on that branch
- Create a pull request from this branch  to the main brach
- Ensure that all automated checks have passed
    - Many times the sphinx documentation build fails due to error in the syntax of your .rst files. To access the logfile, on your Pull Request, click the failing `docs/readthedocs.org:neurowaves` check to access the logfile and correct all Warnings/Errors.
- Wait until your pull request is approved, or commented on
- Address all comments until the PR is approved
- Once the PR is merged to the main branch, delete your branch



Contributing to the documentation
=================================

Use the Sphinx-documentation cheat-sheet below to correctly syntax, explore and use capabilities of Sphinx-documentation.

Sphinx header templates
^^^^^^^^^^^^^^^^^^^^^^^


If you'd like to contribute to this documentation, please follow the heading-adornment conventions below:

+---------------------+------------------------+----------------+------------+
| Level               | Overline & Underline   | Underline only | Character  |
+=====================+========================+================+============+
| Document title      | ``=============``      | N/A            | ``=``      |
+---------------------+------------------------+----------------+------------+
| Top-level section   | ``-------------``      | N/A            | ``-``      |
+---------------------+------------------------+----------------+------------+
| Sub-section         | N/A                    | ``^^^^^^^^``   | ``^``      |
+---------------------+------------------------+----------------+------------+
| Sub-sub-section     | N/A                    | ``""""""""``   | ``"``      |
+---------------------+------------------------+----------------+------------+
| Fourth-level        | N/A                    | ``~~~~~~~~``   | ``~``      |
+---------------------+------------------------+----------------+------------+
| Fifth-level         | N/A                    | ``++++++++``   | ``+``      |
+---------------------+------------------------+----------------+------------+



Adding a toctree within a page
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add a toctree with the content of your page, copy the following code at the beginning of your page contents::

   .. contents::
      :local:
      :depth: 2

This will render as:

.. contents::
   :local:
   :depth: 2

Reference links from within the repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Referencing code files and directories on Github repository
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


For a directory:

- Syntax: ``:github-file:`experiments/psychtoolbox/general``
- Rendered: :github-file:`experiments/psychtoolbox/general`

For a file:

- Syntax: ``:github-file:`docs/source/4-meg-experiments-gallery/experiments/psychtoolbox/attention-experiment.rst``
- Rendered: :github-file:`docs/source/4-meg-experiments-gallery/experiments/psychtoolbox/attention-experiment.rst`

Masking link with text, file:

- Syntax: ``:github-file:`Psychtoolbox Scripts <experiments/psychtoolbox/general>``
- Rendered: :github-file:`Psychtoolbox Scripts <experiments/psychtoolbox/general>`

Masking link with text, directory:

- Syntax: ``:github-file:`Psychtoolbox Scripts <experiments/psychtoolbox/general>``
- Rendered: :github-file:`Psychtoolbox Scripts <experiments/psychtoolbox/general>`


Referencing Jupyter notebooks already rendered by sphinx
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

If you want to reference the notebook's code that is the .ipynb file on the repository, use the above syntax
but if you want to reference the published page of the notebook, then use the below:

- Syntax: ``Resting state: Access link to Analysis Notebook <../6-meg-pipeline-gallery/notebooks/fieldtrip/fieldtrip_kit_restingstate.ipynb>`_``
- Rendered: `Resting state: Access link to Analysis Notebook <../6-meg-pipeline-gallery/notebooks/fieldtrip/fieldtrip_kit_restingstate.ipynb>`_



Making a Checklist
^^^^^^^^^^^^^^^^^^


You can add simple task checklists to any page using the ``checklist`` directive.

.. note::
   Checklists are **clickable in HTML builds**. In PDF/LaTeX they render as
   static boxes (``□`` / ``☒``). If your project includes the optional
   ``checklist.js``, checkbox state is remembered per browser.

Prerequisites
"""""""""""""

- The custom extension is enabled in ``conf.py`` (for example)::

    extensions = [
        # ... other extensions ...
        'checklist',   # or '_checklist' if that’s your package name
    ]

Basic usage
"""""""""""

Write one task per line inside the directive. Use ``[ ]`` for unchecked and
``[x]`` for checked.

.. code-block:: rst

   .. checklist::

      - [ ] Write the introduction
      - [x] Add figures
      - [ ] Final proofreading

Result (HTML)
""-------------""

- ☐ Write the introduction
- ☑ Add figures
- ☐ Final proofreading

Tips
----

- Start each task with ``- [ ]`` or ``- [x]`` exactly (lowercase ``x``).
- Each task is **plain text** (no nested markup).
- For sub-tasks, add another checklist block under a bullet or subsection.

Example with sections
---------------------

.. code-block:: rst

   Project TODOs
   --------------

   **Docs**

   .. checklist::

      - [ ] API reference pass
      - [x] Tutorial outline

   **Release**

   .. checklist::

      - [ ] Changelog
      - [ ] Tag and publish


Setting up MATLAB Kernel for Jupyter
====================================

To run MATLAB code within Jupyter Notebooks, you need to set up the MATLAB kernel in your environment.

Prerequisites
^^^^^^^^^^^^^

- Ensure you have **MATLAB R2025b** installed (required for Python 3.12+ compatibility).
- Your conda environment should be using **Python 3.12**.

Installation Steps
^^^^^^^^^^^^^^^^^^

1. **Activate your environment**:
   
   .. code-block:: bash

      conda activate neurowaves-lab-documentation

2. **Install Jupyter and the MATLAB Kernel**:

   .. code-block:: bash

      conda install notebook jupyter_client
      pip install matlab_kernel

3. **Install the MATLAB Engine for Python**:
   Navigate to your MATLAB installation folder (e.g., ``C:\Program Files\MATLAB\R2025b\extern\engines\python``) and install the engine:

   .. code-block:: bash

      cd "C:\Program Files\MATLAB\R2025b\extern\engines\python"
      python -m pip install .

Using the Kernels
^^^^^^^^^^^^^^^^

Two kernels will be available in Jupyter:

- **Matlab**: Starts a new, independent MATLAB session for the notebook.
- **Matlab (Connection)**: Connects to an already running MATLAB instance, allowing you to share the workspace.

To use the **Connection** kernel:

1. In your standalone MATLAB Command Window, run:

   .. code-block:: matlab

      matlab.engine.shareEngine

2. In Jupyter, select the **Matlab (Connection)** kernel. You can now access variables from your standalone MATLAB session using commands like ``who`` or simply typing the variable name.

Thank you for your contribution!
