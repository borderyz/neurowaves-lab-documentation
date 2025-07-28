Experiments example 5: Response buttons experiment
--------------------------------------------------

The MEG Lab has two response boxes which allow the user to provide their input during an experiment.

The `Left box` is the grey box and the `Right box` is the blue box.

Scripts can be found under

:github-file:`experiments/psychtoolbox/general`

:github-file:`experiments/psychtoolbox/general/getButton.m`

:github-file:`experiments/psychtoolbox/general/button_response.m`


.. warning::

   Both response boxes (left and right) need to be connected in order to have the below functions `getButton` and `listenButton` working.


- To test the response boxes you can run the following script


.. literalinclude:: ../../../../../experiments/psychtoolbox/general/button_response.m
  :language: matlab


- To get the response of a user while performing your experiment, you can use the following MATLAB function `getButton.m <https://github.com/hzaatiti-NYU/meg-pipeline/blob/main/experiments/psychtoolbox/general/getButton.m>`_.


.. literalinclude:: ../../../../../experiments/psychtoolbox/general/getButton.m
  :language: matlab


The above function will return an integer `resp` which you will have to translate using the following table to identify the color that has been pressed.

+-------------+--------------+---------------------------+-----------------------+---------------+
| Box         | Button Color | Button States             | Response Number (resp)| Offset button |
+=============+==============+===========================+=======================+===============+
| Left Box    | Red          | 0001100000  |          4            |      5        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Left Box    | Yellow       | STUCK  |          3            |      6        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Left Box    | Green        | 0011000000  |          2            |      7        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Left Box    | Blue         | 0101000000  |          1            |      8        |
+
| Left Box     |White        | 1001000000   |                      |  9
+-------------+--------------+---------------------------+-----------------------+---------------+
| Right Box   | Red          | 0001000001  |          9            |      0        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Right Box   | Yellow       | 0001000010  |          8            |      1        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Right Box   | Green        | 0001000100  |          7            |      2        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Right Box   | Blue         | 0001001000  |          6            |      3        |
+-------------+--------------+---------------------------+-----------------------+---------------+
  Right Box   | White        | 0001010000  |                             4

.. literalinclude:: ../../../../../experiments/psychtoolbox/general/listenButton.m
  :language: matlab


The above function listens to a specific button press depending on the offset variable given as input, if the specific button is not pushed, the function stays in the while loop.





