.. _attention_exp:

Experiment example (Psychtoolbox): Attention Task
-------------------------------------------------

Authors: Karima Raafat <karima.raafat@nyu.edu>, Hadi Zaatiti <hadi.zaatiti@nyu.edu>

Description
^^^^^^^^^^^

In this experiment, the participant is asked to pay attention (attend) to the left side of the screen, then
targets will appear randomly either on the right or the left side for 10 minutes.
The participant is then asked again to attend to the right side of the screen and the targets will appear aswell randomly
either left or right side.


    .. figure:: figures-attention/fixation.png
        :alt: Visual Stimulus
        :width: 80%

        Fixation cross maintained throughout the experiment.


    .. figure:: figures-attention/target_right.png
        :alt: Visual Stimulus
        :width: 80%

        Target shown on the right side.

The target is almost isoluminant with the background in order to minimise the effect of the visual sensory confounds, ensuring that the measurements reflect the attentional preparation mechanism of the brain rather than obvious visual differences.
The target appears randomly either to the right or left regardless of the cued spatial location, since the goal is not to study motor reflexes or anticipatory behavior.

[Worden2000]_ investigates the brain oscillations, specifically the :math:`\alpha`-band (8-14 Hz) when attention is directed to a spatial location (right or left side).
The paper shows that :math:`\alpha`-band power increases ipsilateral to the attended side and contralateral to the ignored side, prior to the appearence of a visual target.


.. [Worden2000] Worden MS, Foxe JJ, Wang N, Simpson GV. Anticipatory biasing of visuospatial attention indexed by
    retinotopically specific alpha-band electroencephalography increases over occipital cortex.
    J Neurosci. 2000 Mar 15;20(6):RC63. doi: 10.1523/JNEUROSCI.20-06-j0002.2000. PMID: 10704517; PMCID: PMC6772495.


Code Access
^^^^^^^^^^^

:github-file:`Attention task launch experiment <experiments/psychtoolbox/attention/meg_attention_task.m>`

:github-file:`Attention task project directory <experiments/psychtoolbox/attention/>`


