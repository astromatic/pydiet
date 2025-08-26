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

  \mathrm{SNR} = \frac{F}{\sqrt{\mathrm{Var}(F)}}.

:math:`F=f.t` is readily computed using the expected number of photons per unit of time :math:`f` and the exposure time :math:`t`.
The expected uncertainty :math:`\sqrt(\mathrm{Var}(F)` depends on the quality of the estimator of the source flux.
Assuming that noise over pixel values is majoritarily Gaussian-distributed and independent from pixel to pixel, source model-fitting using inverse-variance-weighted `least-squares <https://en.wikipedia.org/wiki/Least_squares>`_ regression offers a fully efficient unbiased estimation of the flux through Maximum Likelihood.
In practice there are of course other contributors to flux uncertainties, such as background estimation errors or contamination by neighboring objects, but they are not relevant in the context of an exposure time calculator.

From there, using Fisher information we can compute a lower bound to the flux uncertainty (the Cramér-Rao bound), and therefore, a higher limit to the |SNR|.

Under the independent Gaussian noise hypothesis, the log-likelihood of the fit writes

.. math::
  :label:

  \ln{{\cal L}}(F|\vec{I}) = \sum_i \ln{{\cal L}}(F|I_i) = - \frac{1}{2} \sum_i \frac{(I_i - F\phi_i)^2}{\sigma_i^2},

where :math:`\vec{\phi}` is the model, :math:`\vec{I}` the background-subtracted exposure to which the model is fitted, and :math:`\sigma_i^2` the variance of pixel :math:`i`:

.. math::
  :label:

  \sigma_i^2 = \sigma_r^2 + \sigma_b^2.t + F\phi_i,

comprising contributions from the readout noise :math:`\sigma_r^2`, from the background noise (per unit of time) :math:`\sigma_b^2`, and from Poisson noise (in the Gaussian regime) from the source photons themselves, :math:`F`.
Now, the Cramér-Rao bound to flux uncertainty :math:`\mathrm{Var}(F)` is simply the inverse of the Fisher information:

.. math::
  :label:

  \mathrm{Var}(F) \geq \frac{1}{{\cal I}},

with

.. math::
  :label:

   {\cal I}(F) = - \esp{\frac{\partial^2}{\partial F^2}\ln{\cal L}(F|\vec{I})}.
   
Therefore we have

.. math::
  :label:

  \begin{aligned}
  {\cal I}(F) & = \frac{1}{2} \sum_i \esp{\frac{\partial^2}{\partial F^2} \frac{(I_i - F\phi_i)^2}{\sigma_i^2}}\\
              & = \frac{1}{2} \left( \sum_i \esp{\frac{\partial}{\partial F} \frac{- 2 \phi_i (I_i - F\phi_i)}{\sigma_i^2}} - \sum_i \esp{\frac{\partial}{\partial F} \frac{(I_i - F\phi_i)^2\phi_i}{\sigma_i^4}} \right).
  \end{aligned}

The second term is 0 as :math:`\esp{I_i - F\phi_i} = 0\ \  \forall i` hence we obtain

.. math::
  :label:

  \begin{aligned}
  {\cal I}(F) & = \frac{1}{2} \sum_i \esp{\frac{\partial}{\partial F} \frac{\phi_i^2\sigma_i^2 - (I_i - F\phi_i)\phi_i}{\sigma_i^4}}\\
              & = \sum_i \frac{\phi_i^2}{\sigma_i^2}.
  \end{aligned}

and

.. math::
  :label:

  \mathrm{SNR} \leq F \sqrt{\sum_i \frac{\phi_i^2}{\sigma_i^2}} = f.t \sqrt{\sum_i \frac{\phi_i^2}{\sigma_r^2 + (\sigma_b^2 + f\phi_i)t}}.
