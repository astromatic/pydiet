.. File data.rst

.. include:: global.rst

.. _chap_data:

Data
====

|PyDIET| uses precomputed spectra to model the light reaching the detector.

|CFHT| This chapter describes the spectra supplied with the CFHT configuration and explains how they were obtained.

Atmosphere
----------

Transmission
~~~~~~~~~~~~

Atmospheric transmission is precomputed as a function of wavelength for a set of airmasses using the `MODTRAN radiative transfer code <https://modtran.spectral.com/>`_.

Transmission curves cover 200 to 5000 nm in steps of 0.5 nm, for airmasses between 1 and 5.

|CFHT| For Mauna Kea Observatories (MKO), we used a tropical atmosphere model at an altitude of 4204 m, with default settings except for the CO₂ concentration, which was set to 430 ppm.
The O₃ and H₂O concentrations appear broadly compatible with the `findings <https://pyextinction.readthedocs.io/en/latest/>`_ of :cite:`Buton2013`.

.. _fig_mko_transmission:

.. figure:: figures/mko_transmission.*
   :alt: Atmospheric throughput at various airmasses
   :align: center

   Atmospheric transmission as a function of wavelength at the MKO site for different airmasses.
   For clarity, only wavelengths below 2800 nm are shown.


Emission
~~~~~~~~

Atmospheric emission is also precomputed, using the `ESO Sky Model Calculator (SKYCALC) <https://www.eso.org/observing/etc/skycalc>`_ :cite:`Noll2012,Jones2013`.
The model includes airglow, scattered moonlight and starlight, zodiacal light, thermal emission, and light pollution.
At each airmass, emission spectra are provided for three lunar conditions: dark (no Moon), grey (a 66.4° phase angle), and bright (a 101.5° phase angle).
For the grey and bright models, the Moon is at 45° elevation and 45° from the line of sight.
Each lunar condition is combined with three levels of solar activity: low (70 SFU), average (130 SFU), and high (200 SFU).

|CFHT| SKYCALC does not offer a model for MKO, so the supplied emission spectra use its Cerro Armazones model.
Among the available sites, Cerro Armazones is the closest match in altitude (3060 m) and absolute latitude, although it lies in the southern hemisphere.
Comparisons with CFHT observations show good agreement with these predictions (see :ref:`chap_validation`).

.. _fig_mko_emission:

.. figure:: figures/mko_emission.*
   :alt: Atmospheric emission for dark, grey, and bright nights
   :align: center

   Sky brightness as a function of wavelength for the MKO configuration under dark, grey, and bright lunar conditions (see text), with average solar activity (130 SFU) and airmass 1.2.
   For clarity, only wavelengths below 2800 nm are shown.


Filter curves
-------------

|CFHT| The CFHT filter curves in |PyDIET| originate from the `MegaCam <https://www.cfht.hawaii.edu/Instruments/Filters/megaprime.html>`_ and `WIRCam <https://www.cfht.hawaii.edu/Instruments/Filters/wircam.html>`_ instrument filter pages.
They were converted to `Synphot-compliant FITS throughput tables <https://www.stsci.edu/hst/instrumentation/reference-data-for-calibration-and-tools/synphot-throughput-tables>`_ using the provided `extract_filter.py <https://github.com/astromatic/pydiet/blob/main/utils/extract_filter.py>`_ Python script.
:numref:`fig_megacam_ugriz_filters`, :numref:`fig_megacam_other_filters`, :numref:`fig_wircam_yjhk_filters`, and :numref:`fig_wircam_other_filters` show the total throughput as a function of wavelength for all the supported filters.

.. _fig_megacam_ugriz_filters:

.. figure:: figures/megacam_filters_ugriz.*
   :alt: Total throughput for MegaCam ugriz filters
   :align: center

   Total throughput as a function of wavelength for the MegaCam ugriz filters at airmass 1.2, including the atmosphere and instrument. Instrumental throughput is shown in grey.

.. _fig_megacam_other_filters:

.. figure:: figures/megacam_filters_other.*
   :alt: Total throughput for other MegaCam filters
   :align: center

   Same as :numref:`fig_megacam_ugriz_filters` for the other MegaCam filters.

.. _fig_wircam_yjhk_filters:

.. figure:: figures/wircam_filters_yjhk.*
   :alt: Total throughput for WIRCam YJHKs filters
   :align: center

   Total throughput as a function of wavelength for the WIRCam YJHKₛ filters at airmass 1.2, including the atmosphere and instrument. Instrumental throughput is shown in grey.

.. _fig_wircam_other_filters:

.. figure:: figures/wircam_filters_other.*
   :alt: Total throughput for other WIRCam filters
   :align: center

   Same as :numref:`fig_wircam_yjhk_filters` for the other WIRCam filters.

Telescope mirrors
-----------------

Mirror ageing
~~~~~~~~~~~~~

The mirror contribution to the instrumental response is represented by a wavelength-dependent throughput (reflectance) curve :math:`T_\mathrm{mir}(\lambda)`.
|PyDIET| can use several throughput curves for :math:`T_\mathrm{mir}(\lambda)`, representing a pristine mirror (the reference) and different stages of surface degradation.
The supplied ``degrade_mirror.py`` script generates these curves from a pristine reflectance curve before they are loaded into |PyDIET|.

The degradation model in `degrade_mirror.py` follows the two-factor description of :cite:`Okita2019`, in which the loss of reflectance is described as the product of:

* an achromatic loss term, independent of wavelength;
* a wavelength-dependent scattering term caused by the growth of surface roughness.

If :math:`T_\mathrm{mir}^{(0)}(\lambda)` is the pristine mirror reflectance/throughput, the aged
mirror throughput at time :math:`t` after recoating is

.. math::
  :label:

  T_\mathrm{mir}(\lambda, t) =  T_\mathrm{mir}^{(0)}(\lambda) D(\lambda, t),

where :math:`D(\lambda, t)` is the relative degradation factor.
The script uses

.. math::
  :label:

  D(\lambda, t) = \alpha(t)\exp\left[-\left<\cos^2\theta_i\right>\left({4\pi\sigma(t) \over \lambda}\right)^2\right],

where

.. math::
  :label:

  \alpha(t) = \exp(-At)

and

.. math::
  :label:

  \sigma(t) = \sigma_0 + S t.

Here :math:`A` is the achromatic loss rate, :math:`\sigma_0` is the initial RMS surface roughness just after coating, :math:`S` is the rate at which the RMS
roughness increases with time, and :math:`\theta_i` is the angle of incidence on the mirror.

The achromatic factor :math:`\alpha(t)` lowers the mirror reflectance by the same multiplicative amount at all wavelengths.
It represents grey losses such as uniform contamination or coating ageing.

The exponential scattering term produces a chromatic loss.
Since it depends on :math:`(\sigma/\lambda)^2`, the effect is stronger at short wavelengths.
As the surface roughness grows with time, the blue part of the mirror response therefore degrades faster than the red and near-infrared part.

The default parameters used by the |PyDIET| mirror-degradation utility are :math:`A = 0.023~\mathrm{yr}^{-1}`, :math:`\sigma_0 = 10~\mathrm{\AA}`, :math:`S = 40~\mathrm{\AA},\mathrm{yr}^{-1}`, and :math:`\left<\cos^2\theta_i\right> = 0.9974`.

The degraded mirror curve is produced by multiplying the tabulated pristine throughput by :math:`D(\lambda,t)`.
The resulting curve is then used like any other mirror throughput curve in the instrumental response:

.. math::

  T_\mathrm{inst}(\lambda) = R(\lambda,t) T_\mathrm{optics}(\lambda) T_\mathrm{filter}(\lambda) T_\mathrm{detector}(\lambda).

Consequently, mirror ageing affects the magnitude zero-point through the reference-source count rate.
A degraded mirror lowers the detected count rate from both astronomical sources and sky background.
The zero-point becomes fainter because a source of a given magnitude produces fewer detected counts per second.

The chromatic part of the degradation also means that the zero-point change is filter-dependent.
Blue filters are affected more strongly than red or near-infrared filters, because scattering losses scale approximately as :math:`\lambda^{-2}` for a given roughness.


