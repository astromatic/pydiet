.. File methods.rst

.. include:: global.rst

.. _chap_methods:

Methods
=======

|PyDIET| is a simulation-based |ETC|, and uses different computational models to reproduce the observations (:numref:`fig_workflow`).
This section describes the main methods and quantities involved in the process.

.. _fig_workflow:

.. figure:: figures/workflow.*
   :alt: |PyDIET| workflow
   :align: center

   Schematic view of the |PyDIET| simulation workflow.

Signal-to-Noise ratio
---------------------

The Signal-to-noise ratio, or simply |SNR|_, is defined in |PyDIET| as the ratio between the source "flux" :math:`F` (actually the number of source photons collected in the detector during the observation) and its expected uncertainty :math:`\sqrt{\var{F}}`:

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
  :label:

  N_i \sim \operatorname{Poisson}(B_i + F\phi_i)

is the contribution from photons,

.. math::
  :label:

  R_i \sim \mathcal{N}(0,\sigma_r^2)

the readout noise, and

.. math::
  :label:

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
  :label:

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

Therefore, plugging into :eq:`snr` we obtain the upper bound at given exposure time :math:`t`:

.. math::
  :label: snr_model

  \begin{aligned}
    \mathrm{SNR} &\lesssim\, F\, \sqrt{
      \sum_i \frac{\phi_i^2}{\sigma_r^2 + \sigma_b^2 t + F\phi_i}} \\
                 &\lesssim\,f.t\, \sqrt{
      \sum_i \frac{\phi_i^2}{\sigma_r^2 + \left(\sigma_b^2 + f\phi_i\right)t}}.
  \end{aligned}

:math:`\var{\hat{F}}` approaches the Cramér-Rao bound at sufficiently large |SNR| or in the background-dominated Gaussian regime.
At very low |SNR|, especially if the flux is constrained to be non-negative or if the source position is fitted simultaneously (see below), the actual uncertainty distribution may be asymmetric or biased, and :eq:`snr_model` should be regarded as an optimistic lower bound rather than as a close estimation.
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
  :label:

   \mu_i = B_i + F\phi_i(x_0,y_0),

and

.. math::
  :label:

   \frac{\partial \mu_i}{\partial F} = \phi_i,

.. math::
  :label:

   \frac{\partial \mu_i}{\partial x_0} = F\frac{\partial \phi_i}{\partial x_0},

.. math::
  :label:

   \frac{\partial \mu_i}{\partial y_0} = F\frac{\partial \phi_i}{\partial y_0}.

The bound on the flux variance is then

.. math::
  :label: joint_flux_bound

   \var{\hat{F}} \geq \left(\boldsymbol{\cal I}^{-1}\right)_{FF}.

Equivalently, writing

.. math::
  :label:

   \mathbf{c} = \begin{pmatrix}
     {\cal I}_{Fx} \\
     {\cal I}_{Fy}
   \end{pmatrix},

and

.. math::
  :label:

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
  :label:

   \left(\boldsymbol{\cal I}^{-1}\right)_{FF} = \frac{1}{{\cal I}_{FF}},

and the flux |SNR| bound reduces to :eq:`snr_model`.
In real data, departures from symmetry, masking, undersampling, neighboring sources, or spatially varying noise can make the cross-terms non-zero, in which case fitting the position increases the bound on :math:`\var{\hat{F}}`.


Aperture photometry
"""""""""""""""""""

Aperture photometry is another way of estimating the source flux.
It is suboptimal compared to model-fitting.
However, it is much less compute-intensive and does not require a model.
This is a useful feature, as the model-fitting accuracy of bright, unsaturated stars, may sometimes be limited by that of the |PSF| model.
For sources with unknown light profiles, aperture photometry is generally the safest option.

For an aperture :math:`{\cal A}`, the |SNR| is 

.. math::
  :label: snr_aper

  \mathrm{SNR}({\cal A}) = \frac{f.t\sum_{i\in{\cal A}} \,\phi_i}{\sqrt{
      \sum_{i\in{\cal A}} \sigma_r^2 + \left(\sigma_b^2 + f\phi_i\right)t
  }}.


Optimal aperture
~~~~~~~~~~~~~~~~

The optimal-aperture option chooses the radius :math:`r=r_\mathrm{opt}` of the circular aperture :math:`{\cal A}(r)` that maximizes the expected aperture signal-to-noise ratio :math:`SNR({\cal A})` in :eq:`snr_aper`:

.. math::
  :label:

   r_\mathrm{opt} = \underset{r}{\operatorname{arg\,max}}\,\mathrm{SNR}({\cal A}(r)).

The minimization is performed numerically over the allowed range of aperture radii, from zero to the radius of the circular simulation mask.

The optimal aperture depends on the exposure time and noise regime.
|PyDIET| therefore recomputes the optimal aperture every time the signal-to-noise ratio is evaluated.

For stars, the optimal aperture depends on the seeing, sky background, source brightness, and exposure time.
For galaxies, the same calculation is applied to the seeing-convolved Sérsic model (see :ref:`sersic`).
The optimal aperture depends on the Sérsic radius, Sérsic index, seeing, sky background, source brightness, and exposure time.


Aperture enclosing 96% of the flux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The large-aperture option is defined as the circular aperture enclosing 96% of the model source flux.

|PyDIET| computes the enclosed model-flux fraction

.. math::
  :label:

  f(r^2) = \sum_{r_i \leq r} \phi_i,

where :math:`r_i` is the distance of pixel :math:`i` from the source center on the internal raster grid.

The aperture radius is obtained by solving

.. math::
  :label: f096

   f(r_{96}^2) = 0.96.

In the |PyDIET| implementation, :math:`f096` is solved numerically with a Brent root finder.
The search interval extends from the center of the image to the edge of the circular simulation mask.

The 96% aperture is close to a total-flux aperture.
It captures most of the model flux, but it is not generally the aperture with the highest signal-to-noise ratio, because the outer parts of the aperture may contain more noise than useful source signal.
In background-dominated conditions, the 96% flux aperture is usually larger than the optimal aperture. 
The outer wings of the source profile contain little signal but contribute sky noise, so including them lowers the signal-to-noise ratio.
In source-dominated or very high signal-to-noise regimes, it may become smaller, because the penalty for including more of the source profile is reduced.


Exposure time
-------------

The main purpose of an |ETC| is obviously to provide exposure times.
|PyDIET| computes the exposure time for a given |SNR| using iterative `root finding <https://en.wikipedia.org/wiki/Root-finding_algorithm>`_ applied to :eq:`snr_model` or :eq:`snr_aper`, more specifically, Brent's method :cite:`Brent1973`.

Source models
-------------

|PyDIET| currently implements three source models: point sources, galaxies, and flat extended sources.
The role of the source model is to define the expected spatial distribution of source photons over the detector pixels.

For compact and galaxy-like sources, the source model is represented by a discrete image :math:`\phi_i`, normalized as

.. math::
  :label: source-model-normalization

  \sum_i \phi_i = 1,

where :math:`i` runs over image pixels (or oversampled sub-pixels, depending on image sampling).
If the total detected source rate is :math:`f`, in photons per second, the expected source contribution in pixel :math:`i` during an exposure time :math:`t` is therefore

.. math::
  :label: source-counts-source-model

  f.t.\phi_i.

For flat extended sources, the model is instead expressed as a surface brightness: the source rate is then interpreted per unit angular area rather than as the total rate of a finite object.

Point-source model
""""""""""""""""""

A point source is modeled as an unresolved object observed through the |PSF|.
|PyDIET| uses a circular `Moffat profile <https://en.wikipedia.org/wiki/Moffat_distribution>`_ :cite:`Moffat1969`,

.. math::
   :label: moffat-profile

   M(r) = \left(1 + \frac{r^2}{\alpha^2}\right)^{-\beta},

where :math:`r` is the angular distance from the source centre, :math:`\alpha` the Moffat scale radius, and :math:`\beta` the strength of the wings.
The Moffat scale radius is set by the requested |FWHM|.
Since :math:`M(\mathrm{FWHM}/2) = M(0)/2`, one obtains

.. math::
   :label: moffat-alpha-fwhm

   \alpha^2 = \frac{\mathrm{FWHM}^2}{4\left(2^{1/\beta} - 1\right)}.

|PyDIET| considers the Moffat :math:`\beta` parameter as an instrumental feature; it is set in the instrument section of the data configuration file.
The default value is :math:`\beta = 3.2`, corresponding to the best-fitting value for MegaCam observations.

The Moffat model is rasterized on the internal image grid, truncated inside the circular simulation domain, and normalized numerically:

.. math::
   :label: point-source-normalized

   \phi_i = \frac{M(r_i)} {\sum_j M(r_j)},

giving the final rasterized point-source image model.

.. _sersic:

Galaxy model
""""""""""""

A galaxy is modeled as a circular `Sérsic profile <https://en.wikipedia.org/wiki/S%C3%A9rsic_profile>`_ :cite:`Sersic1963,Ciotti1999,Graham2005` convolved with the seeing PSF.
Before convolution, the intrinsic surface-brightness profile is

.. math::
  :label: sersic-profile

  S(r) = \exp\left\{-b_n\left[\left(\frac{r}{R_\mathrm{e}}\right)^{1/n} - 1\right]\right\},

where :math:`R_\mathrm{e}` is the effective radius and :math:`n` the Sérsic index.

The effective radius :math:`R_\mathrm{e}` is the radius enclosing half of the intrinsic Sérsic-model flux.
The Sérsic index controls the concentration of the profile.
Values close to :math:`n=1` correspond to disk-like profiles, whereas larger values produce more centrally concentrated profiles with more extended wings, such as in ellipticals or galaxy bulges.
For numerical stability reasons, the current implementation enforces limits on the Sérsic index: :math:`0.36 \leq n \leq 10`.

The observed galaxy model is obtained by convolving the intrinsic Sérsic profile with the |PSF| model,

.. math::
  :label: sersic-convolved

  G(r) = (S * P)(r),

where :math:`*` denotes convolution.
The convolution is performed on the rasterized model using Fourier transforms.

The final galaxy image model is then truncated inside the circular simulation
domain and normalized numerically:

.. math::
  :label: galaxy-normalized

  \phi_i = \frac{G_i} {\sum_j G_j}.

The total source rate :math:`f` is therefore the total detected photon rate of the galaxy.

Flat extended-source model
""""""""""""""""""""""""""

The extended-source model represents a flat source with constant surface brightness.
It is not normalized to unit total flux, because the source is not treated as a finite object.
Instead, the input brightness is interpreted per unit angular area.

Let :math:`a_i` be the angular area of pixel :math:`i`, in arcsec\ :sup:`2`.
For a flat source with detected surface photon rate :math:`f_\Omega`, in photons s\ :sup:`-1` arcsec\ :sup:`-2`, the expected source contribution in pixel :math:`i` during an exposure time :math:`t` is

.. math::
  :label: extended-source-counts

  f_\Omega . t . a_i.

For a regular detector grid, all pixels have the same angular area :math:`a_\mathrm{pix}`.
The model image is therefore simply rasterized as

.. math::
  :label: extended-source-image

  \phi_i = a_\mathrm{pix}

inside a large disk, and zero outside it.
Convolving a constant surface-brightness field by a normalized |PSF| gives the same constant surface brightness.
Therefore, the seeing parameter has no direct effect on the mathematical model of an extended (flat) source.


Synthetic photometry
--------------------

|PyDIET| converts source brightnesses and sky surface brightnesses into detected count rates before evaluating the signal-to-noise ratio.
This conversion is performed by integrating reference spectra or sky spectra through the selected instrumental and atmospheric responses.


Transmission
""""""""""""

Let :math:`T_\mathrm{inst}(\lambda)` be the instrumental response, including the selected mirror state, telescope/instrument optics, filter transmission, and detector response. Let :math:`T_\mathrm{atm}(\lambda; X)` be the atmospheric transmission at airmass :math:`X`, and let :math:`\tau` be the additional transparency factor entered by the user.
The full source transmission used for source count rates is

.. math::
  :label:

  T_\mathrm{full}(\lambda) = T_\mathrm{inst}(\lambda) T_\mathrm{atm}(\lambda; X) \tau .

The effective collecting area is

.. math::
  :label:

  A_\mathrm{eff} = A_\mathrm{tel} - A_\mathrm{obs},

where :math:`A_\mathrm{tel}` is the telescope collecting area and :math:`A_\mathrm{obs}` is the obstructed area, which is often instrument-dependent (especially for prime-focus cameras).


Magnitude zero-point
""""""""""""""""""""

For a given filter and instrument configuration, |PyDIET| computes a photometric zero-point from the count rate of a reference source.

For `AB magnitudes <https://en.wikipedia.org/wiki/AB_magnitude>`_, the reference spectrum is the constant-flux-density :math:`m_\mathrm{AB}=0` spectrum.
For Vega magnitudes, the reference spectrum is the Vega spectrum.
In both cases, the reference count rate is computed by integrating the reference spectrum through the relevant transmission curve.

For the full atmospheric response, the reference count rate is

.. math::
  :label:

   f_0 = \int R_{0,\lambda}(\lambda) T_\mathrm{full}(\lambda) A_\mathrm{eff}{\lambda \over hc}\,d\lambda ,

where :math:`R_{0,\lambda}` is the chosen reference spectrum.
|PyDIET| uses the  :meth:`~synphot.observation.Observation.countrate` method of the `SynPhot <https://synphot.readthedocs.io>`_ :mod:`~synphot.observation` module to evaluate this integral.

If the detector gain is :math:`g`, in electrons per ADU, the corresponding count rate in ADU per second is

.. math::
  :label:

   C_0 = {f_0 \over g}.

The magnitude zero-point is then

.. math::
  :label:

   \mathrm{ZP} = 2.5 \log_{10} C_0 .

Equivalently, a source producing a measured count rate :math:`C`, in ADU per second, has magnitude

.. math::
  :label:

   m = \mathrm{ZP} - 2.5 \log_{10} C .


|PyDIET| reports two related zero-points:

* The full AB zero-point, including atmosphere and transparency.
  This is the zero-point corresponding to :math:`T_\mathrm{full}`.

* The instrumental AB zero-point (accessible through the web API), computed from :math:`T_\mathrm{inst}` only, without atmospheric transmission.
  This value is cached for each mirror/filter configuration and is used in particular to express the sky background as an AB surface brightness.

For a source magnitude :math:`m`, the detected source count rate is

.. math::
  :label:

   f = f_0 10^{-0.4m} .

For flux-density units, |PyDIET| converts the input value to the equivalent multiplicative factor relative to the AB reference spectrum.
For integrated physical fluxes, the conversion uses the pivot wavelength and equivalent rectangular bandwidth of the full transmission curve.

Sky background
""""""""""""""

The sky background enters the SNR model as a count rate per detector pixel.
|PyDIET| supports two cases:

* a predefined sky model selected from tabulated sky spectra;
* a user-specified sky brightness.

For the predefined sky modes, PyDIET selects a tabulated sky-emission spectrum according to:

* the sky state, for example dark, grey, or bright;
* the solar-activity level;
* the observing airmass.

The sky spectrum is interpolated linearly between the available tabulated airmass values.
The result is a sky surface-brightness spectrum,

.. math::
  :label:

   I_\mathrm{sky}(\lambda; X, s, q),

where :math:`X` is the airmass, :math:`s` the sky state, and :math:`q` the solar-activity state.

This sky-emission spectrum is already a surface brightness at the observing site.
It is therefore propagated only through the instrumental response, leaving out the transmission of the atmosphere.
The sky count rate per square arcsecond is

.. math::
  :label:

   B_\Omega = \int I_\mathrm{sky}(\lambda) T_\mathrm{inst}(\lambda) A_\mathrm{eff} {\lambda \over hc}\, d\lambda + B_\mathrm{therm} .

The term :math:`B_\mathrm{therm}` is the instrumental thermal-emission contribution for the selected mirror and filter configuration.
It includes thermal emission terms associated with the telescope, optics, filter, and detector model.

When the sky background is specified manually, |PyDIET| converts the user input into a detector count rate per pixel.

|PyDIET| reports the sky background both as a count rate per pixel (accessible through the web API) and as an AB surface brightness.

If the detector pixel scale is :math:`p_x \times p_y`, in arcseconds per pixel, the value passed to the image model as the background rate per pixel is then

.. math::
  :label:

   B_\mathrm{pix} = B_\Omega p_x p_y .

The reported AB sky surface brightness is derived from the instrumental AB zero-point:

.. math::
  :label:

   \mu_\mathrm{sky,AB} = \mathrm{ZP}_\mathrm{inst,AB} - 2.5 \log_{10}\left( {B_\Omega \over g}\right).

The instrumental zero-point is used here because the sky-emission spectrum is already the sky brightness at the observing site; it should not be attenuated by the atmosphere a second time.

