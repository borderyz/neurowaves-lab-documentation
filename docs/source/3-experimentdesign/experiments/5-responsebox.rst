Experiments example 5: Response buttons experiment
--------------------------------------------------

The MEG Lab has two response boxes which allow the user to provide their input during an experiment.

The `Left box` is the grey box and the `Right box` is the blue box.

.. warning::

   Both response boxes (left and right) need to be connected in order to have the below functions `getButton` and `listenButton` working.


- To test the response boxes you can run the following script


.. literalinclude:: ../../../../experiments/psychtoolbox/general/button_response.m
  :language: matlab


- To get the response of a user while performing your experiment, you can use the following MATLAB function `getButton.m <https://github.com/hzaatiti-NYU/meg-pipeline/blob/main/experiments/psychtoolbox/general/getButton.m>`_.


.. literalinclude:: ../../../../experiments/psychtoolbox/general/getButton.m
  :language: matlab


The above function will return an integer `resp` which you will have to translate using the following table to identify the color that has been pressed.

+-------------+--------------+---------------------------+-----------------------+---------------+
| Box         | Button Color | Button States             | Response Number (resp)| Offset button |
+=============+==============+===========================+=======================+===============+
| Left Box    | Red          | 111111111111110000000001  |          4            |      5        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Left Box    | Yellow       | 111111111111110000000010  |          3            |      6        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Left Box    | Green        | 111111111111110000000100  |          2            |      7        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Left Box    | Blue         | 111111111111110000001000  |          1            |      8        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Right Box   | Red          | 111111111111110000100000  |          9            |      0        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Right Box   | Yellow       | 111111111111110001000000  |          8            |      1        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Right Box   | Green        | 111111111111110010000000  |          7            |      2        |
+-------------+--------------+---------------------------+-----------------------+---------------+
| Right Box   | Blue         | 111111111111110100000000  |          6            |      3        |
+-------------+--------------+---------------------------+-----------------------+---------------+


.. literalinclude:: ../../../../experiments/psychtoolbox/general/listenButton.m
  :language: matlab


The above function listens to a specific button press depending on the offset variable given as input, if the specific button is not pushed, the function stays in the while loop.





