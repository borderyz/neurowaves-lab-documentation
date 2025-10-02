Experiments example 5: Response buttons experiment
--------------------------------------------------

The MEG Lab has two response boxes which allow the user to provide their input during an experiment.

For the right box the colors of the buttons from left side to right side are:
- white
- red
- yellow
- green
- blue

For the left box it is the same order above, but from right side to left side.

Scripts can be found under

:github-file:`experiments/psychtoolbox/general`


:github-file:`experiments/psychtoolbox/general/getButtonColor.m`



.. warning::

   Both response boxes (left and right) need to be connected in order to have the function to work correctly.


- To test the response boxes you can run the following script


.. literalinclude:: ../../../../../experiments/psychtoolbox/general/test_getButtonColor.m
  :language: matlab

- The `getButtonColor()` function takes as input:
    - a struct selection of the buttons to listen to
    - provides as output the pressed button box and which button color
    - it can work in blocking (wait until a press is obtained) or non-blocking mode (a one frame pass on listening to the button press)









