Process for new MEG user
========================

.. mermaid::

    graph TD;
        A[User arrives at MEG lab] --> B[Design Experiment];
        B --> C[Present Research];
        C --> D[Submit Draft Code via Pull Request on GitHub];
        D --> E[Code Reviewed];
        E --> F{Does Code Work?};
        F -- No --> G[Iterate & Revise Code];
        G --> D;
        F -- Yes --> H[Keep Testing Code];
        H --> I[Experiment Finalized];

