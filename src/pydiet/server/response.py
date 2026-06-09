"""
Computation module
"""
# Copyright CFHT
# Licensed under the MIT licence

from math import pi, sqrt
from os import PathLike
from typing import IO, Optional

from astropy import units as u  #type: ignore[import-untyped]
from pydantic import BaseModel, Field
from synphot import Observation, SpectralElement  #type: ignore[import-untyped]

from .image import Image
from .models import (
    ETCQueryModel,
    ETCResponseModel,
    FiltersModel,
    SBSEDModel,
    SEDModel,
    TransmissionModel,
    spectral_to_arrays
)
from .models.types import FilterID, MirrorID
from .data import instruments
from .datafiles import (
    get_emission_from_transmission,
    get_transmission
)
from .photsys import PhotSys


def spectrum_from_airmass(
        models: dict[str, SBSEDModel | SEDModel | TransmissionModel],
        am: float = 1.,
        extra: Optional[dict[str, str|float]] = None) -> SpectralElement:
    # Build a dictionary of emission or transmission spectra
    am_spectra = {
        model.vars['am'] : model.spectral  #type: ignore[index]
        for model in models.values()
        if extra is None or all(
            model.vars[e]==extra[e]  #type: ignore[index]
            for e in extra
        )
    }
    ams = sorted(list(am_spectra.keys()))
    # bracket the requested airmass for interpolation
    aml = float(ams[0])
    amp = float(ams[-1])
    for aa in ams:
        a = float(aa)
        if a >= am:
            amp = a
            break
        else:
            aml = a
    # Linear interpolation
    fac = (am - aml) / (amp - aml) if am < amp else 1.
    return am_spectra[aml] * (1. - fac) +  am_spectra[amp] * fac  #type: ignore[operator]


def get_response(
        q: ETCQueryModel,
        filter: Optional[IO[bytes] | PathLike | str]=None,
        ui: bool=False) -> ETCResponseModel:
    if filter is not None:
        # Read the uploaded filter transmission file
        filter_transmission = get_transmission(filter, id='upload')
        # Compute filter emission based on transmission (and dummy temperature/area)
        emission = get_emission_from_transmission(
            filter_transmission,
            temperature=273. * u.K,
            id='upload'
        )
        # Make a copy of the instrument while adding the uploaded filter
        filters = instruments[q.instrument].filters
        instrument = instruments[q.instrument].model_copy(
            update={
                'filters': FiltersModel(
                    transmissions = filters.transmissions | {
                        'upload' : filter_transmission
                    },
                    emissions = filters.emissions | {'upload' : emission}
                )
            }
        )
        # Update composite transmissions and emission curves
        instrument._update_cache()
    else:
        instrument = instruments[q.instrument]

    telescope = instrument.telescope
    detector = instrument.detector
    config_id = f"{MirrorID(q.mirror).value}+{FilterID(q.filter).value}" \
        if q.filter != "" else q.filter
    cache = instrument.cache
    instrument_transmission = cache.transmissions[config_id]

	# Pure atmospheric transmission at observing site at a given airmass
    atmosphere_spec = spectrum_from_airmass(
        instrument.site.sky_transmissions,
        am=q.airmass
    ) * q.transparency
	# Pure instrumental transmission (no atmosphere here)
    instru_spec = instrument_transmission.spectral
    # Compute full transmission by multiplying instrument by atmosphere
    full_spec = instru_spec * atmosphere_spec
    # Compute effective collecting area, compensating for possible obstruction
    area = instrument.telescope.collecting_area - instrument.obstruction_area

    # Make virtual observation
    gain = detector.gain.value
    lambda_pivot = full_spec.pivot()
    dlambda_rect = full_spec.rectwidth()
    t_peak = full_spec.tpeak()

    # Actual source
    # Get photometric system
    photsys = PhotSys(q.unit, lambda_pivot, dlambda_rect)
    if full_spec.tpeak() > 0.:
		# Instrument/filter response is non-zero over the domain
        if photsys.spectrum is None:
        	# We're dealing with photons per second -> No conversion needed
            source_rate = photsys.photon_rate(q.brightness)
            zp = 0. * u.mag
        else:
        	# A reference spectrum is involved
            # Compute the number of source photons per second
            ct_ref = Observation(
                photsys.spectrum,
                full_spec
            ).countrate(area=area, binned=False)
            source_rate = ct_ref.to_value(u.ct / u.s) \
                * photsys.photon_rate(q.brightness)
     		# Compute "full" zero-point including atmosphere and stuff
            zp = u.Magnitude(1. * u.ct / u.s) - u.Magnitude(ct_ref / gain)
    else:
		# Mismatched instrument/filter responses: 0 transmission over the domain
        source_rate = 0.
        zp = -100. * u.mag

    # Compute pure instrumental zero-point in the AB system

    # Background
    if q.sky == 'specify':
    	# Sky surface brightness is provided by user
        sky_photsys = PhotSys(q.sky_unit, lambda_pivot, dlambda_rect)
        sky_spectrum = sky_photsys.spectrum
        sky_photon_rate = sky_photsys.photon_rate(q.sky_brightness)
        if sky_spectrum is not None:
			# A reference spectrum is involved
            if q.sky_unit == 'fmegajy':
	            # If in Jy per str, convert to arcsec2
                sky_photon_rate *= 2.350e-11
            sky_spectrum *= sky_photon_rate
    else:
        # Sky spectrum is taken from tabulated data
        # at a given airmass and solar flux
        sky_spectrum = spectrum_from_airmass(
            instrument.site.sky_emissions,
            am=q.airmass,
            extra={'sky': q.sky, 'solar': q.solar}
        )
    if sky_spectrum is not None:
        # We have a sky spectrum: compute background count rate
        # through instrument transmission
        if cache.tpeaks[config_id] > 0.:
    		# Instrument/filter response is non-zero over the domain
            bkg_rate_arcsec2 = Observation(
                sky_spectrum,
                instru_spec,
                force='extrap'
            ).countrate(
                area=area,
                binned=False
            ).to_value(u.ct / u.s) \
		    # Add instrumental thermal background component
            + cache.emissions_ct[config_id]
            bkg_rate = bkg_rate_arcsec2 \
                * detector.scale[0].to_value(u.arcsec / u.pix) \
                * detector.scale[1].to_value(u.arcsec / u.pix)
        else:
            bkg_rate = 0.
            mag_bkgsb = 100. * u.mag

        # Compute number of background electrons per pixel per second
        # We explicitely assume that counts are per arcsec2
    else:
        # Counts directly provided by user
        bkg_rate = sky_photon_rate
    mag_bkgsb = u.Magnitude(cache.zp_abmags[config_id]) + u.Magnitude(
        bkg_rate_arcsec2 * u.ct / u.s / gain
    ) if bkg_rate > 0. else 100. * u.mag
    

    # Instantiate image model
    img = Image(
        source=q.source,
        psf_fwhm=q.seeing * u.arcsec,
        psf_beta=3.2,
        sersic_radius=q.sersic_radius,
        sersic_index=q.sersic_index,
        pixel_scale=detector.scale,
        rate=source_rate,
        bkg_rate=bkg_rate,
        # Use RON 'counts' instead of electrons for compatibility with synphot
        ron=detector.ron.to_value('electron'),
        gain=gain,
        photometry=q.photometry,
        aperture=q.aperture
    )

    sexposures = sqrt(q.exposures * 2. / pi) if \
        q.stacking == 'median' and q.exposures > 2 else sqrt(q.exposures)
       
    if q.compute == 'etime':
        snr = q.snr / sexposures
        # Compute exposure time (solution to a second degree equation) in s
        etime = img.etime(snr)
    else:
        etime = q.etime
        snr = img.snr(etime)

    if ui:
        full_wave, full_response = spectral_to_arrays(full_spec)
        atmosphere_wave, atmosphere_response = spectral_to_arrays(atmosphere_spec)

    return ETCResponseModel(
            instrument = instrument.name,
            filter = instrument_transmission.name,
            compute = q.compute,
            zp = zp.value,
            snr = snr * sexposures,
            etime = etime,
            etime_skysat = img.etime_bkg_sat(),
            etime_sourcesat = img.etime_source_sat(),
            ttime = q.exposures * (etime + instrument.overhead.to_value(u.s)),
            bkg_mag = mag_bkgsb.value,
            bkg_rate = bkg_rate,
            lambda_pivot = lambda_pivot.to_value(u.nm),
            bandwidth_rect = dlambda_rect.to_value(u.nm),
            cutout = img.gif(etime, exposures=q.exposures) if ui else None,
            filter_transmission = TransmissionModel(
                id = instrument_transmission.id,
                name = instrument_transmission.name,
                wave_range = instrument.wavelength_range,
                wave = full_wave,
                response = full_response
            ).model_dump_json(
                exclude={'spectral'}
            ) if ui else None,
            atmosphere_transmission =  TransmissionModel(
                id = 'atmosphere',
                name = "Atmosphere",
                wave_range = instrument.wavelength_range,
                wave = atmosphere_wave,
                response = atmosphere_response
            ).model_dump_json() if ui else None
    )


