Fieldtrip pipeline
------------------




Visual rejection

using ft_rejectvisual(cfg, data);











Fieldtrip coregistration with OPM data
--------------------------------------

You will need the headshape.pos matrix containing the head shape grid and 3 fiducials: the nasion, the lpa and the RPA
(those three fiducials are at the end of the .pos file)


Remind that:
Using the LaserScanner generates a basic_surface.txt file (which contains the head points)
and a stylus.txt file containing 8 reference points: we will need the first three points
`Laser Scanner protocol reminder <https://meg-pipeline.readthedocs.io/en/latest/2-operationprotocol/operationprotocol.html>`_

Use the ft_read_head_shape to read the .pos matrix and fiducials



Information on head coordinate systems https://www.fieldtriptoolbox.org/faq/coordsys/