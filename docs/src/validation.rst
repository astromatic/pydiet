.. File validation.rst

.. include:: global.rst

.. _chap_validation:

Model validation
================

The quantities predicted by |PyDIET| can be checked against measurements from science and calibration exposures.
Such comparisons must use the same filter, exposure time, observing conditions, and instrument configuration in the model and in the observations.
In what follows, we compare the photometric zero-points and the measured sky background with the corresponding |PyDIET| predictions.

Photometric zero-point
----------------------

|CFHT| The photometric zero-point describes the conversion between a source magnitude and the signal recorded by the instrument in a one-second exposure. 
A higher zero-point corresponds to greater sensitivity: a source of fixed magnitude produces more detected signal and consequently reaches a higher |SNR|, all else being equal.
Changes in atmospheric transparency and instrumental throughput can therefore appear as changes in the measured zero-point.

The Elixir pipeline :cite:`Magnier2004` derives MegaCam magnitude zero-points from photometric exposures on a nightly basis, by comparing measured count rates for suitable stars (SNLS tertiary standards :cite:`Regnault2009,Betoule2013`) with calibrated catalogue magnitudes.
After applying the same photometric conventions and selecting observations of appropriate quality, these values can be compared against |PyDIET| predictions for the matching filter, airmass, and instrumental state.

:numref:`fig_zp_difference_vs_airmass` shows such a comparison for MegaCam filters over the period 2015-2025, as a function of airmass.
As can be seen, the agreement is typically within 1-2% at all airmasses for filters with sufficient coverage, with the notable exception of the **u**, **CaHK**, and **i** filters, for which |PyDIET| seems to overestimate the instrumental throughput by about 10 to 20%.
The reason for this discrepancy remains unclear.
We have therefore added an empirical photometric correction based on the observed median offset in the |PyDIET| data configuration file for CFHT.

.. _fig_zp_difference_vs_airmass:

.. figure:: figures/zp_difference_vs_airmass.*
   :alt: Difference between the measured MegaCam magnitude zero-points and the PyDIET predictions as a function of airmass.
   :align: center

   Difference between the AB magnitude zero-points measured by the Elixir pipeline and the PyDIET predictions as a function of airmass, for various filters of the MegaCam instrument.
   Each point represents a photometric night.
   Mirror state is indicated by a color: blue, pristine; orange, average; red, degraded.
   The median difference and its uncertainty are shown in the lower left of each plot.


Sky background
--------------

|CFHT| The sky background contributes photon noise to an observation and therefore limits the |SNR|, especially for faint sources.
A brighter sky produces more noise and lowers the |SNR| for otherwise identical observations.
Its level varies with quantities such as filter, airmass, lunar illumination, solar activity, and time-dependent instrumental throughput.

The background rate can be measured in reduced exposures from source-free pixels or source-masked regions, after accounting for detector signatures and the exposure time.
These measurements can then be compared with |PyDIET| predictions evaluated for the observing conditions recorded for each exposure.

Time dependency
~~~~~~~~~~~~~~~

Solar activity and mirror degradation are the two main factors that prevent sky background rates from remaining stable from run to run.
Using `solar activity records <https://www.spaceweather.gov/>`_ in the form of monthly means of solar radio fluxes, and telescope mirror recoating logs, one can configure |PyDIET| accordingly and compare the predicted sky background rates to those measured on individual exposures in a given filter.
Such comparisons (:numref:`fig_sky_solar_gri`) show good agreement between the observed variations and those predicted by the model. 

.. _fig_sky_solar_gri:

.. figure:: figures/sky_solar_gri.*
   :alt: Sky background rate in the MegaCam gri filter as a function of time.
   :align: center

   Measured sky background rate in the MegaCam gri filter (in ADU/s) as a function of time (blue points), compared to the monthly average solar activity (orange line) and the |PyDIET| prediction (green line).
   The measurements only include photometric exposures taken during dark nights at airmass < 1.4.
   The |PyDIET| model assumes an airmass of 1.2, and accounts for both interpolated solar activity, and mirror ageing.

Filter dependency
~~~~~~~~~~~~~~~~~

|CFHT| The Elixir pipeline also tracks the sky background level on all exposures, based on the empirical estimation from the SExtractor package :cite:`Bertin1996`.

.. _fig_back_predicted_vs_measured:

.. figure:: figures/back_predicted_vs_measured.*
   :alt: Predictions for the sky background count rates vs measured background rates .
   :align: center

   |PyDIET| predictions for the sky background count rates vs measured background rates (in ADU/s).
   Discrepant zero-points in the u, CaHK, and i filters are corrected, as explained in the previous section.
   Each point represents a photometric night.
   The presence of the Moon is indicated by a color: blue, no moon; orange, the moon is up.


Signal-to-Noise Ratio
---------------------

The achieved |SNR| reflects both sides of the comparison: the zero-point sets
the detected source signal, while the sky background contributes to its noise.
It also depends on the source brightness, exposure time, image quality,
detector noise, and the method used to measure the source flux.

An observational |SNR| can be estimated from the measured flux and its
photometric uncertainty, or from the scatter of repeated measurements of
similar sources.  Comparing these values with |PyDIET| predictions for the same
sources and observing conditions provides an end-to-end validation of the
model.  Trends with source magnitude, exposure time, or observing conditions
can reveal whether discrepancies originate mainly in the predicted source
signal, background level, or noise model.
