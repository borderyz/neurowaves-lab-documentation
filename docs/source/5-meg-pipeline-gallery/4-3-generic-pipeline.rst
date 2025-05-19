Installation
------------

To use MEG-Pipeline, first install it using pip:

.. code-block:: console

   (.venv) $ pip install megpipeline

Reading the Raw Data
--------------------

The ``kind`` parameter should be either ``"raw"``, ``"fif"``,
or ``"fll"``.


.. literalinclude:: ../../../pipeline/import_raw_data.py
  :language: python

The above script will later be implemented as part of the following class :py:class:`MEGpipeline` and function :py:func:`megpipeline.get_raw_data`.


.. autoclass::MEGpipeline

The ``kind`` parameter should be either ``"raw"``, ``"fif"``,
or ``"fll"``. Otherwise, :py:func:`megpipeline.get_raw_data`
will raise an exception.



For example:

>>> import megpipeline
>>> megpipeline.get_raw_data()
['a', 'b', 'c']



Manual labelling of "bad" channels
----------------------------------


Denoising
---------

Awareness of the many sources of noise:

- Related to the site in which the MEG system is installed
- Related to conditions that could happen from time to time (parking garage nearby,)

Once the reasons are understood, we can identify the pattern that the noise makes.

With training data of the different possible noises, it is very possible to train a neural classifier
that could identify the noise coming from the different sources and be able to denoise it from the MEG data.


Independent component analysis
------------------------------

Independent component analysis (ICA) is commonly used to generate what is supposed a set of independent
signals from a given set of assumingly correlated signals.

The signals produced by MEG are highly correlated, therefore ICA is suitable to reduce correlation.
Given a set of MEG signal X(t), ICA learns a matrix W and the output signals S(t) such that

add latex here: X(t) = W.S(t)

ICA can perform well to identify the noise signals that has a certain long lasting continuous-time pattern, but less efficient when the noise is a single event, happening at irregular periods of time.

.. code-block:: python
   :caption: Calling ICA withint a Python pipeline

    projs, raw.info['projs'] = raw.info['projs'], []
    ica.fit(raw)
    raw.info['projs'] = projs


Frequency Analysis
------------------
Fast-oscillating signals means high frequencies, while slow oscillations are low frequencies.
In fourier space (signal represented by its Fourier transform) we can see the frequency components constituting
the signal. FFT (Fast Fourier Transform) algorithm is commonly to identify the frequency components.


Research showed that signals at different frequencies have different functions at different locations of the brain.
In other words, given a region of the brain, signals of frequency 8Hz are responsible of an activity that is much different than signals with frequency 20 Hz


Brain Source Estimate
---------------------

When neurons become active, they do so in large groups.




Code Overview
-------------

The code for an example.

.. code-block:: python
    :caption: This installs dependencies

    # Install required Meg-pipeline dependencies
    import matplotlib as plt
    import mne




Fieldtrip specific pipelines
----------------------------

.. toctree::
   :maxdepth: 2
   :caption: Fieldtrip pipelines

   4-3-a-fieldtrip-pipelines




Beamforming, source reconstruction
----------------------------------

- measuring the contribution of a specific sensor in a soruce signal (weighing of the sensor w.r.t a specific source)

S(r,t) = W(r)b(t)

S rouce estimate,
W beamformer weights (3 columns because 3 orientations of each dipole (add location and so on can be extended))
b channel measurement

The question is finding W (the right one among the different possible ones)
adding constriants will reduce the ill-posedness of the problem
- forward model constraints cfrom physiological data
- inverse problem constraints

spatial filtering: assume there is only one source and estimate its activity independetly from the other sources ( the estimation is the multiplication of the weight matrix with the chanenl measurements) repeated over the number of sources

The lead matrix L is the inverse of the weight matrix W (simple assumption)
Additional constraint to take the neighborhood sources into account, the W at a source r should not give high gain for another source q at a certain distance from r ( q should not be the direct neighbor)
so for the direct neighbor, we wana minimise by a bit the gain and not ocmpletely set it to 0
the variance over the position  is therefore minimised (ensuring smoothness, and reduced gain in neighbors)
(beamformer Linearly constrained minimum variance (LCMV))

W and S are unknowns, minimising var(S) requires knowing W, but there is a relationship between W, L and C (the measured data covariance matrix, how dep/independent each measurement is with the others)

(In fieldtrip, the configuration points to LCMV  or DICS(for frequency analysis) algorithm to use this beamformer)

Computing the inverse of C (used for the solution) requires that C is not rank deficient (a measure of the dependency between the rows/columns), small time window, ICA can increase deficiency




Continuous stimulus
-------------------

The use of Dissimilarity matrix (is a comparison measure between two different stimulus), the matrix is low in values when the sitmulus are similar

at the stimulus level but also the brain response, computed at each time point is a way of measuring brain activity in time-continuous stimuli (video, speech,






















