Experiments example 3 (Psychopy): Triggering all channels on KIT
----------------------------------------------------------------

- Triggering all channels on the KIT machine one by one

The following script triggers each event channel on the KIT from 224 to 231 using PsychoPy script

- `trigger_test_psychopy_digital_out.py <https://github.com/hzaatiti-NYU/meg-pipeline/blob/main/experiments/psychopy/trigger_test_psychopy_digital_out.py>`_.
- `trigger_test_psychopy_pixel_mode.py <https://github.com/hzaatiti-NYU/meg-pipeline/blob/main/experiments/psychopy/trigger_test_psychopy_pixel_mode.py>`_.

For the moment, full screen with PsychoPy does not work on Windows, the second script therefore do not work because it requires the top left pixel to change color.

.. literalinclude:: ../../../../experiments/psychopy/general/trigger_test_psychopy_digital_out.py
  :language: python


.. literalinclude:: ../../../../experiments/psychopy/general/trigger_test_psychopy_pixel_mode.py
  :language: python