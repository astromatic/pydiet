.. File method.rst

.. include:: global.rst

.. _chap_method:

Method
======

Signal-to-Noise ratio
---------------------

The `Signal-to-noise ratio <https://en.wikipedia.org/wiki/Signal-to-noise_ratio>`_, or simply |SNR|_ is defined as the ratio between the source flux :math:`F` and its expected uncertainty :math:`\sqrt{\mathrm{Var}(F)}`:

.. math::
  :label:

  \mathrm{SNR} = \frac{F}{\sqrt{\var{F}}}.

:math:`F=f.t` is readily computed using the expected number of photons per unit of time :math:`f` and the exposure time :math:`t`.
The expected uncertainty :math:`\sqrt{\var{F}}` depends on the quality of the estimator of the source flux.
Assuming that noise over pixel values is majoritarily Gaussian-distributed and independent from pixel to pixel, source model-fitting using inverse-variance-weighted `least-squares <https://en.wikipedia.org/wiki/Least_squares>`_ regression offers a fully efficient unbiased estimation of the flux through `Maximum Likelihood Estimation (MLE) <https://en.wikipedia.org/wiki/Maximum_likelihood_estimation>`_.
In practice there are of course other contributors to flux uncertainties, such as background estimation errors or contamination by neighboring objects, but they are not relevant in the context of an exposure time calculator.

Let's start assuming we know the position of the source; hence the only fitted parameter is the flux.
From there, using `Fisher information <https://en.wikipedia.org/wiki/Fisher_information>`_ we can compute a lower bound to the flux uncertainty (the `Cramér-Rao bound <https://en.wikipedia.org/wiki/Cram%C3%A9r%E2%80%93Rao_bound>`_), and therefore, a higher limit to the |SNR|.

Under the independent Gaussian noise hypothesis, the log-likelihood of the fit writes

.. math::
  :label: likelihood

  \ln{{\cal L}}(F|\vec{I}) = \sum_i \ln{{\cal L}}(F|I_i) = - \frac{1}{2} \sum_i \left( \ln \sigma_i^2 + \frac{(I_i - F\phi_i)^2}{\sigma_i^2} \right),

where :math:`\vec{\phi}` is the source image model normalized such that :math:`\sum_i \phi_i = 1`, :math:`\vec{I}` the background-subtracted exposure to which the model is fitted, and :math:`\sigma_i^2` the variance of pixel :math:`i`:

.. math::
  :label:

  \sigma_i^2 = \sigma_r^2 + \sigma_b^2.t + F\phi_i,

comprising contributions from the readout noise :math:`\sigma_r^2`, from the background noise (per unit of time) :math:`\sigma_b^2`, and from Poisson noise (in the Gaussian regime) from the source photons themselves, :math:`F`.
Now, the Cramér-Rao bound to the variance of the  |MLE|, :math:`\var{\hat{F}}`, is simply the inverse of the Fisher information:

.. math::
  :label:

  \var{\hat{F}} \geq \frac{1}{{\cal I}(\hat{F})},

with

.. math::
  :label: fisher

   {\cal I}(\hat{F}) = \var{\left. \frac{\partial \ln{\cal L}(F|\vec{I})}{\partial F}\right|_{F=\hat{F}}}_\vec{I}\,,

where the expectation is taken over pixel values, at the |MLE| :math:`F=\hat{F}`.
Note that in order to simplify the computations, we expressed the Fisher information as the variance of the `score <https://en.wikipedia.org/wiki/Informant_(statistics)>`_ instead of minus the expectation of the second derivative of the likelihood.

Plugging :eq:`likelihood` in :eq:`fisher` we get

.. math::
  :label:

  \begin{aligned}
  {\cal I}(\hat{F}) = & \var{-\frac{1}{2} \sum_i \Bigg. \frac{\partial}{\partial F} \left\{ \ln \sigma_i^2 + \frac{(I_i - F\phi_i)^2}{\sigma_i^2}\right\}\Bigg|_{F=\hat{F}}}_\vec{I}\\
                    = & \var{\sum_i \left(\frac{-\phi_i}{2\sigma_i^2} + \frac{\phi_i (I_i - \hat{F}\phi_i)}{\sigma_i^2} + \frac{(I_i - \hat{F}\phi_i)^2\phi_i}{2\sigma_i^4}\right)}_\vec{I}\,.
  \end{aligned}

Assuming the covariances between pixels are zero (which is a good approximation on individual exposures), we get
              
              
.. math::
  :label: fisher2

  \begin{aligned}
  {\cal I}(\hat{F}) = & \sum_i \var{\frac{\phi_i (I_i - \hat{F}\phi_i)}{\sigma_i^2} + \frac{\phi_i\left((I_i - \hat{F}\phi_i)^2 - \sigma_i^2\right)}{2\sigma_i^4}}_{I_i}\\
                    = & \sum_i \left(\frac{\phi_i^2}{\sigma_i^4} \var{I_i - \hat{F}\phi_i} + \frac{\phi_i^2}{4\sigma_i^8} \var{(I_i - \hat{F}\phi_i)^2 - \sigma_i^2}\right.\\
                      & \left. + 2\frac{\phi_i^2}{\sigma_i^6} \cov{I_i - \hat{F}\phi_i}{(I_i - \hat{F}\phi_i)^2 - \sigma_i^2}\right).
  \end{aligned}

Remarking that

- :math:`\var{I_i - \hat{F}\phi_i} = \sigma_i^2`,
- :math:`\var{(I_i - \hat{F}\phi_i)^2 - \sigma_i^2} = 2\sigma_i^4` (Gaussian 4th central moment), and
- :math:`\cov{I_i - \hat{F}\phi_i}{(I_i - \hat{F}\phi_i)^2 - \sigma_i^2} = 0`,

:eq:`fisher2` simplifies to

.. math::
  :label:

  {\cal I}(\hat{F}) = \sum_i \frac{\phi_i^2}{\sigma_i^2} + \sum_i \frac{\phi_i^2}{2\sigma_i^4},

and we have

.. math::
  :label:

  \mathrm{SNR} \leq F \sqrt{\sum_i \frac{\phi_i^2}{\sigma_i^2} + \sum_i \frac{\phi_i^2}{2\sigma_i^4}} = f.t \sqrt{\sum_i \frac{\phi_i^2}{\sigma_r^2 + (\sigma_b^2 + f\phi_i)t}}.
