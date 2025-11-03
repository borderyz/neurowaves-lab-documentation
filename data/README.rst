XNAT for MEG documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

This directory will hold all test data and files to migrate data storage from NYU BOX to XNAT

In the future, this directory will hold all scripts for retrieving data from XNAT and proper documentation



New instructions for MEG workstation
------------------------------------

- From the master branch clone and follow instructions https://github.com/NrgXnat/xnat-docker-compose
- The MEG workstation have a static IP address: 10.224.44.161
  - to allow connections from external requests you need to add a firewall rule
    - on windows add an inbound rule that accepts all connections to port 80
    - netsh advfirewall firewall add rule name="XNAT Web Server Port 80" dir=in action=allow protocol=TCP localport=80

 