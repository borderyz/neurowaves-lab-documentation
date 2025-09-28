Sanity check script for trigger counting
========================================

MEG data:
- is a .con file (sensor data + trigger data)
- .mrk file (marker coils positions)

- the script takes as input:
  - ".con" file and the CSV that contains type of triggers (i.e., which channel combinations it takes)
  - the number of triggers per type

- the script provide as output:
  - "passed" if trigger count is correct
  - "fail + some information on what is missing" when trigger count is missing


Problems:

- Sound on trigger should go off earlier
- Sound off trigger should go off earlier