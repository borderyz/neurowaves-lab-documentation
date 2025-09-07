---------
Processes
---------


MEG Project Proposal
^^^^^^^^^^^^^^^^^^^^


All new project proposals must fill the following `form <https://docs.google.com/forms/d/e/1FAIpQLSeZb8tCBbH5FVo9E0uZn7FMjXzXNtYjC6s5Ln1gh_sofFSEBQ/viewform?usp=sharing>`_.
Add as many known details as possible regarding:

- the topic of your project
- the research question you are addressing
- additional systems that you will need to run your experiment successfully

.. mermaid::

    graph TD;
        A[🎓 <b>User arrives<br/>at MEG lab</b>] -->|🚀 Start| B[🧪 <b>Design<br/>Experiment</b>];
        B -->|📢 Present| C[📝 <b>Present<br/>Research</b>];

        %% Contribution Guide
        C --> X[📖 <b><a href='https://neurowaves.readthedocs.io/en/latest/1-lab-overview/6-neurowaves-contribution.html'>
        Contribution Guide</a></b>];

        X -->|📂 Submit| D[💻 <b>Submit Draft Code<br/>via Pull Request</b>];
        D -->|🔍 Review| E[✅ <b>Code<br/>Reviewed</b>];
        E -->|🤔 Decision| F{⚖️ <b>Does Code<br/>Work?</b>};

        F --❌ No --> G[🔄 <b>Iterate & Revise<br/>Code</b>];
        G -->|📂 Resubmit| D;

        F --✅ Yes --> H[🔬 <b>Keep Testing<br/>Code</b>];
        H -->|🏆 Success| I[🎉 <b>Experiment<br/>Finalized</b>];

        %% Clickable Node for GitHub PR
        click D "https://github.com/BioMedicalImaging-Core-NYUAD/neurowaves-lab-documentation/pulls" "Visit GitHub Repository"

        %% Style Definitions
        classDef success fill:#4CAF50,stroke:#2E7D32,color:#fff;
        classDef decision fill:#FFEB3B,stroke:#FBC02D,color:#000;
        classDef process fill:#2196F3,stroke:#1976D2,color:#fff;
        classDef warning fill:#FF5722,stroke:#E64A19,color:#fff;

        class A,B,C,D,E,H,X process;
        class F decision;
        class G warning;
        class I success;





Identifying your usage
^^^^^^^^^^^^^^^^^^^^^^

(Add usage form)




Booking a session for testing/debugging your stimulus code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. mermaid::

    graph TD;
        A["🧑‍💻 <b>Need to Test/Debug<br/>Code</b>"] --> B{👨‍🔬 <b>Need MEG Scientist<br/>Assistance?</b>};

        %% Path: No Scientist Needed
        B -- No --> C["✅ <b>Book Lab Anytime<br/>(24/7)</b>"];
        C --> D["🖥️ <b><a href='https://corelabs.abudhabi.nyu.edu/dashboard.php'>
        MEG Booking Portal</a></b>"];
        D --> E["🧠 <b>Select MEG<br/>System - KIT</b>"];

        %% Path: Scientist Needed
        B -- Yes --> F["🕘 <b>Restricted to<br/>9:00 AM – 5:00 PM</b>"];
        F --> G["📅 <b>Check MEG Scientist’s<br/>Availability</b>"];
        G --> H["📅 <b><a href='https://calendar.google.com/calendar/u/0/r?cid=aHozNzUyQG55dS5lZHU'>
        Book Scientist’s Calendar</a></b>"];
        G --> I["📧 <b><a href='mailto:hadi.zaatiti@nyu.edu'>
        Email MEG Scientist</a></b>"];
        H --> J["🖥️ <b><a href='https://corelabs.abudhabi.nyu.edu/dashboard.php'>
        Book Lab Slot</a></b>"];
        J --> K["🧠 <b>Select MEG<br/>System - KIT</b>"];

        %% Alternative Booking
        C --> O["🖥️ <b><a href='https://corelabs.abudhabi.nyu.edu/'>
        Alternative: Corelabs Reservations</a></b>"];
        K --> O;

        %% Style Definitions
        classDef primary fill:#4CAF50,stroke:#2E7D32,color:#fff,font-weight:bold;
        classDef warning fill:#FF5722,stroke:#D84315,color:#fff,font-weight:bold;
        classDef process fill:#2196F3,stroke:#1976D2,color:#fff,font-weight:bold;
        classDef highlight fill:#FF9800,stroke:#F57C00,color:#fff,font-weight:bold;

        class A,B primary;
        class C,D,E,F,G,H,I,J,K,O process;




Booking an MEG data acquisition session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. warning::

   While scheduling your experiment, avoid rush hours 8:30am and 5:30pm, and friday prayer time, as more noise can be introduced into the data due to outside movement.
   All bookings should not happen on a monday morning, as Helium refill is scheduled for monday mornings (9:00 am till 10:30 am)
   and it is not possible to acquire data during this period.
   Provide your `netID` to the MEG scientists for you to have access to the lab booking calendar.



.. important::

    Scan the QR code below to book your lab for your usage, login with `Gmail` using your `@nyu.edu` account

    .. image:: ../graphic/meg-calendar-qr.png
        :alt: MEG Calendar QR code
        :align: center

    If you do not have access to the booking system, please email `hz3752@nyu.edu` to be added to the system.
    Alternatively, schedule your experiment in the MEG lab using link `https://corelabs.abudhabi.nyu.edu/ <https://corelabs.abudhabi.nyu.edu/>`_
    Under Reservations, Schedule, from the upper drop down menu pick `Brain Imaging` and then book the `MagnetoEncephaloGraphy MEG-KIT`
    If you need the MEG scientist (Hadi Zaatiti) to be present during the booking (in the case of a training for example) please first make sure before booking the MEG lab to do the following:

    - ensure that the slot is available on his gmail calendar `hz3752@nyu.edu` (the calendar is kept up to date)
    - send a meeting on google calendar at the requested slot with subject `MEG Training of [name and netID of trainee]`
    - then book the lab at the same slot using the above QR code/link

.. mermaid::

    graph TD;
        A["🎉 <b>Experiment Finalized</b>"] -->|📩 Submit| B["🆔 <b>Provide NetID to MEG Scientists</b>"];
        B -->|🔑 Get Access| C["🔓 <b>Gain Access to MEG Booking System</b>"];

        %% Booking Process
        C --> D["🖥️ <b>Go to Booking Portal</b>"];
        D -->|🔗 Visit| E["🔗 <b><a href='https://corelabs.abudhabi.nyu.edu/dashboard.php'>MEG Booking Portal</a></b>"];
        E -->|📌 Pick| F["🧠 <b>Select Magnetoencephalography MEG - KIT</b>"];

        %% Restrictions & Warnings
        F --> G{⚠️ <b>Check Scheduling Rules</b>};
        G --❌ Avoid --> G1["⏰ <b>Rush Hours (8:30 AM - 5:30 PM)</b>"];
        G --❌ Avoid --> G2["🛑 <b>Monday Morning (9:00 - 10:30 AM) - Helium Refill</b>"];
        G --❌ Avoid --> G3["🕌 <b>Friday Prayer Time</b>"];

        %% Decision: Does the user need a scientist?
        F --> I{👨‍🔬 <b>Need MEG Scientist Assistance?</b>};
        I -- No --> L["✅ <b>Book Lab at Desired Slot</b>"];
        I -- Yes --> J["📅 <b>Check Availability on Their Calendar</b>"];
        J --> K["📧 <b>Send Google Calendar Invite</b>"];
        K -->|Meeting Subject: MEG Training of Name & NetID| L;

        %% Decide Whether to Book Hadi or Haidee
        I --> M["🔗 <b><a href='https://meg-pipeline.readthedocs.io/en/latest/1-systems/5-team.html'>Who to Book? Responsibilities</a></b>"];
        M -->|📧 Contact| N{📩 <b>Email Hadi or Haidee?</b>};
        N --📩 Hadi Zaatiti --> O["📧 <b><a href='mailto:hadi.zaatiti@nyu.edu'>hadi.zaatiti@nyu.edu</a></b>"];
        N --📩 Haidee Paterson --> P["📧 <b><a href='mailto:haidee.paterson@nyu.edu'>haidee.paterson@nyu.edu</a></b>"];

        %% Alternative Booking Process
        F --> R["🖥️ <b><a href='https://corelabs.abudhabi.nyu.edu/'>Alternative: Corelabs Reservations</a></b>"];

        %% Style Definitions for Enhanced Coloring
        classDef primary fill:#4CAF50,stroke:#2E7D32,color:#fff,font-weight:bold;
        classDef warning fill:#FF5722,stroke:#D84315,color:#fff,font-weight:bold;
        classDef process fill:#2196F3,stroke:#1976D2,color:#fff,font-weight:bold;
        classDef highlight fill:#FF9800,stroke:#F57C00,color:#fff,font-weight:bold;

        class A primary;
        class B,C,D,E,F,H,L,Q,R process;
        class G,G1,G2,G3 warning;
        class I,J,K,M,N,O,P highlight;



