.. File method.rst

.. include:: global.rst

.. _chap_method:

Method
======

Signal-to-Noise ratio
---------------------

The Signal-to-noise ratio, or simply |SNR|_, is defined in PyDIET as the ratio between the source "flux" :math:`F` (actually the number of source photons collected in the detector during the observation) and its expected uncertainty :math:`\sqrt{\var{F}}`:

.. math::
  :label: snr

  \mathrm{SNR} = \frac{F}{\sqrt{\var{F}}}.

:math:`F=f.t` is readily computed using the expected number of photons per unit of time :math:`f` and the exposure time :math:`t`.
The expected uncertainty :math:`\sqrt{\var{F}}` depends on the quality of the estimator of the source flux.
Note that the estimator :eq:`snr` is biased, although this can reasonably be ignored in the context of an ETC for usable SNRs :math:`\gtrsim 3`.

Model fitting
"""""""""""""

Assuming that photon noise follows Poisson statistics, that readout noise is Gaussian-distributed, and that noise is independent from pixel to pixel, source model-fitting using inverse-variance-weighted `least-squares <https://en.wikipedia.org/wiki/Least_squares>`_ regression provides a good approximation to the Maximum Likelihood Estimator (|MLE|_) of the "flux" :math:`F`.
In practice there are other contributors to flux uncertainties, such as background estimation errors or contamination by neighboring objects, but they are not easy to quantify, and we shall ignore them in the context of this exposure time calculator.


Forced photometry
~~~~~~~~~~~~~~~~~
Let's start assuming we know the position of the source; hence the only fitted parameter is its amplitude, represented by the "flux" :math:`F`. Let :math:`\vec{\phi}` be the source image model (the |PSF| for point sources, or the |PSF| convolved with a light distribution model for extended sources), normalized such that :math:`\sum_i \phi_i = 1`.
The expected source contribution in pixel :math:`i` is then :math:`F\phi_i`.

Before background subtraction, the pixel value may be written as

.. math::
  :label: pixel_model

  Y_i = N_i + R_i,

where

.. math::

  N_i \sim \operatorname{Poisson}(B_i + F\phi_i)

is the contribution from photons,

.. math::

  R_i \sim \mathcal{N}(0,\sigma_r^2)

the readout noise, and

.. math::

  B_i = \sigma_b^2 t

the expected background contribution.
After subtracting the expected background, :math:`I_i = Y_i - B_i`, we have

.. math::
  :label: pixel_expectation

  \esp{I_i} = F\phi_i,

and

.. math::
  :label: pixel_variance

  V_i(F) = \var{I_i} = \sigma_r^2 + \sigma_b^2 t + F\phi_i.

The exact likelihood of :math:`Y_i` is the convolution of a `Poisson distribution <https://en.wikipedia.org/wiki/Poisson_distribution>`_ with a Gaussian readout noise distribution.
Its `Cramér-Rao bound <https://en.wikipedia.org/wiki/Cram%C3%A9r%E2%80%93Rao_bound>`_ has no simple closed form in general.
For the purpose of this |ETC|, we use an inverse-variance-weighted Gaussian approximation to the exact Poisson+Gaussian likelihood.
The inverse-variance-weighted estimating equation is obtained by minimizing

.. math::
  :label: weighted_chi2

  \chi^2(F) = \sum_i \frac{\left(I_i - F\phi_i\right)^2} {V_i(F)},

where :math:`V_i(F)` is the expected variance used to weight the residuals.
The flux is therefore estimated by nulling

.. math::
  :label: estimating_equation

  U(F) = \sum_i \frac{\phi_i\left(I_i - F\phi_i\right)}{V_i(F)} = 0.

If the weights are kept fixed during one least-squares step, this gives the usual inverse-variance-weighted flux estimator :cite:`Naylor1998`:

.. math::
  :label: weighted_flux_estimator

  \hat{F} = \frac{\sum_i \phi_i I_i / V_i}{\sum_i \phi_i^2 / V_i}.

In practice :math:`V_i` may be updated iteratively using the current value of :math:`F`.

At the true value of :math:`F`,

.. math::

  \esp{I_i - F\phi_i} = 0,

so :math:`\esp{U(F)} = 0`.
The `Fisher information <https://en.wikipedia.org/wiki/Fisher_information>`_ associated with this optimal high-count approximation is

.. math::
  :label: fisher_flux

  \begin{aligned}
    {\cal I}(F) &= \var{U(F)} \\
                &= \sum_i \frac{\phi_i^2}{V_i(F)^2} \var{I_i} \\
                &= \sum_i \frac{\phi_i^2}{V_i(F)}.
  \end{aligned}

Hence

.. math::
  :label: fisher_flux_expanded

  {\cal I}(F) \simeq \sum_i \frac{\phi_i^2}{\sigma_r^2 + \sigma_b^2 t + F\phi_i}.

For :math:`\sigma_r = 0`, this expression coincides with the exact Fisher information of the Poisson distribution.
With non-zero readout noise, it is the usual Poisson+Gaussian approximation.
The Cramér-Rao bound gives

.. math::
  :label: flux_variance_bound

  \var{\hat{F}} \gtrsim \frac{1}{{\cal I}(F)} = \left[
    \sum_i \frac{\phi_i^2}{\sigma_r^2 + \sigma_b^2 t + F\phi_i}
  \right]^{-1}.

Therefore, plugging into :eq:`snr` we obtain the upper bound

.. math::
  :label: snrbound

  \begin{aligned}
    \mathrm{SNR} &\lesssim\, F\, \sqrt{
      \sum_i \frac{\phi_i^2}{\sigma_r^2 + \sigma_b^2 t + F\phi_i}} \\
                 &\lesssim\,f.t\, \sqrt{
      \sum_i \frac{\phi_i^2}{\sigma_r^2 + \left(\sigma_b^2 + f\phi_i\right)t}}.
  \end{aligned}

:math:`\var{\hat{F}}` approaches the Cramér-Rao bound at sufficiently large |SNR| or in the background-dominated Gaussian regime.
At very low |SNR|, especially if the flux is constrained to be non-negative or if the source position is fitted simultaneously (see below), the actual uncertainty distribution may be asymmetric or biased, and :eq:`snrbound` should be regarded as an optimistic lower bound rather than as a close estimation.
Remember also that it does not take into account systematic uncertainty terms such as imperfect background subtraction, correlated noise, model mismatch, source blending, or flat-field errors.

Free model coordinates
~~~~~~~~~~~~~~~~~~~~~~
If the source coordinates are also left as free parameters, the relevant bound is no longer the reciprocal of the flux-only Fisher information.
Instead, one must use the inverse of the `Fisher matrix <https://en.wikipedia.org/wiki/Fisher_information#Matrix_form>`_ :math:`\boldsymbol{\cal I}` for :math:`\vec{\theta} = (F,x_0,y_0)`: in the same approximation,

.. math::
   :label: joint_fisher

   {\cal I}_{\alpha\beta} \simeq \sum_i \frac{1}{V_i} \frac{\partial \mu_i}{\partial \theta_\alpha} \frac{\partial \mu_i}{\partial \theta_\beta},

where

.. math::

   \mu_i = B_i + F\phi_i(x_0,y_0),

and

.. math::

   \frac{\partial \mu_i}{\partial F} = \phi_i,

.. math::

   \frac{\partial \mu_i}{\partial x_0} = F\frac{\partial \phi_i}{\partial x_0},

.. math::

   \frac{\partial \mu_i}{\partial y_0} = F\frac{\partial \phi_i}{\partial y_0}.

The bound on the flux variance is then

.. math::
   :label: joint_flux_bound

   \var{\hat{F}} \geq \left(\boldsymbol{\cal I}^{-1}\right)_{FF}.

Equivalently, writing

.. math::

   \mathbf{c} = \begin{pmatrix}
     {\cal I}_{Fx} \\
     {\cal I}_{Fy}
   \end{pmatrix},

and

.. math::

   \mathbf{Q} = \begin{pmatrix}
     {\cal I}_{xx} & {\cal I}_{xy} \\
     {\cal I}_{xy} & {\cal I}_{yy}
   \end{pmatrix},

one obtains

.. math::
   :label: schur_flux_bound

   \var{\hat{F}} \geq \frac{1}{{\cal I}_{FF} - \mathbf{c}^{\mathsf T}\mathbf{Q}^{-1}\mathbf{c}}.

The correction term is positive, so fitting the position can only degrade the flux uncertainty.
For an isolated source with a centrally symmetric model (and a symmetric fitting domain), the flux-position cross-terms vanish by symmetry: :math:`{\cal I}_{Fx} = {\cal I}_{Fy} = 0`.
In that ideal case,

.. math::

   \left(\boldsymbol{\cal I}^{-1}\right)_{FF} = \frac{1}{{\cal I}_{FF}},

and the flux |SNR| bound reduces to :eq:`snrbound`.
In real data, departures from symmetry, masking, undersampling, neighboring sources, or spatially varying noise can make the cross-terms non-zero, in which case fitting the position increases the bound on :math:`\var{\hat{F}}`.


Aperture photometry
"""""""""""""""""""

Aperture photometry is another way of estimating the source flux.
It is suboptimal compared to model-fitting, except in the regime where photon noise from the source itself dominates, in which case both perform identically.
However, it does not require a model and is much less compute-intensive.
For sources with unknown light profiles, it is generally the safest option.


