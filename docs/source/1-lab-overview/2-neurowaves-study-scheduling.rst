NW Study Scheduling
===================

Identifying your usage
----------------------

(Add usage form)


Booking system and scheduling
-----------------------------


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



Provide your `netID` to the MEG scientists for you to have access to the lab booking calendar.


.. warning::

   While scheduling your experiment, avoid rush hours 8:30am and 5:30pm, and friday prayer time, as more noise can be introduced into the data due to outside movement.
   All bookings should not happen on a monday morning, as Helium refill is scheduled for monday mornings (9:00 am till 10:30 am)
   and it is not possible to acquire data during this period.

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



