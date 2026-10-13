.. File customize.rst

.. include:: global.rst

.. _chap_customize:

Customization
=============

To make |PyDIET| your own, start with your instrument's characteristics, then give the calculator a matching interface.
The physical model lives in ``src/pydiet/data/data_config.toml``, in `TOML <https://toml.io/en/>`_ format.
`Jinja2 <https://jinja.palletsprojects.com/>`_ templates under ``src/pydiet/templates`` define the |ETC| form and results, while ``src/pydiet/web_client/css/style.css`` controls their appearance.

The supplied MegaCam and WIRCam configurations provide working examples to build on.
You can add a filter, adapt a camera, or replace the observing site by supplying your own measurements and spectra.
This chapter walks through those changes and the corresponding interface adjustments; :ref:`chap_data` explains the supplied spectra, and :ref:`chap_deploy` covers installation.


Preparing a custom installation
-------------------------------

Give your custom files a home outside the installed package so they survive upgrades.
One convenient layout is:

.. code-block:: text

   /srv/pydiet-custom/
       data/
           data_config.toml
           sites/
           telescopes/
           instruments/
       templates/
           common/
           mycamera/
               etc_form.html
               etc_results.html
       client/
           css/
           dist/
           images/
       extra/

Copy the supplied ``data`` and ``templates`` directories, along with the web client's ``css``, ``dist``, and ``images`` directories, into this layout.
Keep ``dist/pydiet.js``: it handles instrument selection, form submission, and result display.
You can leave ``extra`` empty.
Then point the copied TOML file at your data directory:

.. code-block:: toml

   path = "/srv/pydiet-custom/data"

Tell the server where to find these copies through its INI configuration:

.. code-block:: ini

   [server]
   data_config = /srv/pydiet-custom/data/data_config.toml
   data_dir = /srv/pydiet-custom/data
   template_dir = /srv/pydiet-custom/templates
   client_dir = /srv/pydiet-custom/client
   extra_dir = /srv/pydiet-custom/extra

Start the server with ``pydiet --config /path/to/pydiet.conf``.
There are two data paths to keep in mind: the engine reads spectra under the TOML ``path``, while the server's ``data_dir`` is a separate setting.
A relative TOML ``path`` is resolved against the installed ``pydiet`` package directory.
An absolute path, as above, avoids ambiguity when keeping your data outside the package.

Restart the server after changing the TOML file or spectral data: instrument models and derived quantities are loaded at startup.
Reload the browser after changing templates or CSS, bypassing its cache if necessary.
When editing a source checkout instead, ensure that the running installation uses it, or reinstall the package after making changes.


Data configuration
------------------

Think of the TOML file as a collection of sites, telescopes, and cameras.
Each has its own table in ``[[sites]]``, ``[[telescopes]]``, or ``[[instruments]]``; a camera connects to its site and telescope through their ``id`` values.
Choose unique, simple IDs such as ``mysite``, ``mytelescope``, and ``mycamera``.
Instrument IDs also name URLs and template directories, and every referenced site and telescope must have a definition.

Physical quantities are quoted strings with units understood by `Astropy <https://www.astropy.org/>`_, such as ``"2.5 m2"`` or ``"[0.3, 0.3] arcsec/pix"``.
Dimensionless parameters, such as ``psf_beta`` and ``vars.am``, are TOML numbers; flags such as ``default`` are TOML booleans.
Write the two-element quantities ``wavelength_range`` and detector ``scale`` as strings containing an array and a common unit.

Configuration reference
~~~~~~~~~~~~~~~~~~~~~~~

Use these tables as a reference while editing your configuration.
Entries are required unless a default or limitation is stated; nested paths are appended to their parent's path.

.. list-table:: Top-level and shared entries
   :header-rows: 1
   :widths: 30 25 45

   * - Entry
     - Value or example
     - Meaning
   * - ``path``
     - ``"/srv/pydiet-custom/data"``
     - Existing root directory for spectral files.
   * - ``sites``, ``telescopes``, ``instruments``
     - Arrays of tables
     - Site, telescope, and instrument definitions. Supply at least one of each for a working calculator.
   * - ``id``
     - ``"mycamera"``
     - Identifier within the corresponding object collection.
   * - ``name``, ``description``
     - Strings
     - Display name and descriptive text.
   * - ``default``
     - Boolean; default ``false``
     - Selects the preferred instrument. The server chooses the first marked instrument, or the first entry if none is marked. Site and telescope selection uses the instrument's IDs, not these objects' ``default`` flags.
   * - ``path`` in an object table
     - ``"instruments/mycamera"``
     - Object's directory, relative to the root path.
   * - ``transmission``, ``emission``
     - Nested tables
     - Spectral transmission and emission definitions, detailed below. Instruments use these tables within their optics, filters, and detector components.

.. list-table:: Sites and telescopes
   :header-rows: 1
   :widths: 30 25 45

   * - Entry
     - Value or example
     - Meaning
   * - ``sites.altitude``
     - ``"2400 m"``
     - Required site altitude, at least -1000 m. Currently validated but not used to generate or alter atmospheric spectra.
   * - ``sites.transmission``
     - Transmission table
     - Atmospheric transmission spectra, with a numeric ``am`` in each file's ``vars`` table.
   * - ``sites.emission``
     - Emission table
     - Sky surface-brightness spectra, indexed by ``am``, ``sky``, and ``solar`` in each file's ``vars`` table.
   * - ``telescopes.collecting_area``
     - ``"2.5 m2"``
     - Positive geometric collecting area, including the central obstruction and spider area. The instrument's explicit or inherited obstruction is subtracted in calculations.
   * - ``telescopes.obstruction_area``
     - ``"0.2 m2"``
     - Positive telescope obstruction area, used when an instrument omits its own ``obstruction_area``.
   * - ``telescopes.transmission``
     - Transmission table
     - One combined mirror-throughput curve per selectable mirror condition. Use explicit file IDs matching the form's ``mirror`` choices.
   * - ``telescopes.emission``
     - Emission table
     - Mirror emission, either read from files or derived from transmission and temperature.

.. list-table:: Instruments and detectors
   :header-rows: 1
   :widths: 30 25 45

   * - Entry
     - Value or example
     - Meaning
   * - ``instruments.site_id``, ``instruments.telescope_id``
     - ``"mysite"``, ``"mytelescope"``
     - IDs of the site and telescope definitions used by this instrument.
   * - ``instruments.wavelength_range``
     - ``"[350, 1000] nm"``
     - Two positive wavelengths defining the range of the serialized transmission curves used for display.
   * - ``instruments.obstruction_area``
     - ``"0.3 m2"``
     - Optional positive obscured area for this instrument; defaults to the referenced telescope's ``obstruction_area``. An explicit value overrides that default. Keep the effective obstruction smaller than the collecting area.
   * - ``instruments.overhead``
     - ``"20 s"``
     - Nonnegative overhead per exposure. Total time is ``exposures * (exposure_time + overhead)``.
   * - ``instruments.psf_beta``
     - Number; default ``3.2``
     - Moffat |PSF| shape parameter, greater than 1 and at most 10. Seeing FWHM is a separate query input.
   * - ``instruments.optics``
     - ``path``, ``transmission``, ``emission``
     - Optical components between telescope mirrors and filters. Multiple transmission files are successive optical elements.
   * - ``instruments.filters``
     - ``path``, ``transmission``, ``emission``
     - Alternative filters. Each transmission file is one filter, with an explicit ``id`` and a useful display ``name``.
   * - ``instruments.detector.path``
     - ``"detector"``
     - Detector data directory relative to the instrument path.
   * - ``instruments.detector.gain``
     - ``"2 electron/adu"``
     - Positive conversion factor in electrons per ADU.
   * - ``instruments.detector.ron``
     - ``"4 electron"``
     - Nonnegative RMS readout noise.
   * - ``instruments.detector.scale``
     - ``"[0.3, 0.3] arcsec/pix"``
     - Two positive angular pixel scales, one for each axis.
   * - ``instruments.detector.full_well``
     - ``"240000 electron"``
     - Positive full-well capacity in electrons; defaults to ``"1000000 electron"``. Dividing by the gain gives the corresponding saturation limit in ADUs.
   * - ``instruments.detector.range``
     - ``"65536 adu"``
     - Digital range in ADUs, greater than one; defaults to ``"65536 adu"``. The highest representable level is one ADU below this value.
   * - ``instruments.detector.bias``
     - ``"1200 adu"``
     - Nonnegative bias level in ADUs; defaults to ``"0 adu"``. Subtracted from the highest digital level to obtain the available signal headroom.
   * - ``instruments.detector.transmission``
     - Transmission table
     - Quantum efficiency. Supply one file without an ``id``; the engine currently looks up the detector curve using the generated key ``"0"``.
   * - ``instruments.detector.emission``
     - Emission table
     - Required by the schema, but detector emission is not currently included in the calculation. Use ``{}`` for an empty table if appropriate.

.. list-table:: Transmission and emission tables
   :header-rows: 1
   :widths: 30 25 45

   * - Entry
     - Value or example
     - Meaning
   * - ``transmission.path``, ``emission.path``
     - String; default ``""``
     - Directory relative to the containing site, telescope, optics, filter, or detector directory.
   * - ``transmission.files``, ``emission.files``
     - Array of inline tables; default ``[]``
     - Spectral-file descriptions. A working instrument needs transmission curves for its mirrors, optics, filters, detector, and atmosphere.
   * - ``files[].file``
     - ``"my_r.fits"``
     - Filename relative to the spectral table's path. Required for each file entry.
   * - ``files[].id``
     - String; default ``""``
     - Identifier for a filter or mirror condition. If omitted, the loader uses a numeric dictionary key such as ``"0"``.
   * - ``files[].name``, ``files[].description``
     - Strings; default ``""``
     - Display name and description for the spectral model.
   * - ``files[].default``
     - Boolean; default ``false``
     - Preferred filter or mirror condition for the default instrument's API queries. The browser also uses filter defaults when no valid selection is saved. Atmospheric spectra are selected by query parameters, not by this flag.
   * - ``files[].vars``
     - Inline table; default ``{}``
     - Model parameters. Atmosphere uses ``am``; sky emission also uses ``sky`` and ``solar``. Filter ``scale`` multiplies its transmission, with an implicit value of 1.
   * - ``emission.temperatures``
     - List of quantities; default ``["283 K"]``
     - Positive component temperatures for thermal emission derived from throughput when emission files are absent.
   * - ``emission.blackbody_fractions``
     - List of numbers; default ``[0.0]``
     - Values from 0 to 1 used in the derived emissivity ``1 + (fraction - 1) * transmission``.

For mirrors, optics, and filters, you can supply emission files or let |PyDIET| derive thermal emission from throughput and temperature.
In the latter case, temperatures and blackbody fractions follow transmission-file order, with the last value reused when a list runs short; keep both lists nonempty.
If you supply emission files, match filter and mirror IDs to their transmission IDs, and keep optics emission files in transmission order.
The sky needs its own emission spectra: site temperature and altitude do not generate them.

The detector saturation threshold in ADUs is ``min(range - 1 - bias, full_well / gain)``.
Whichever fills first—the remaining digital range above the bias or the full well—sets the limit.
Use your detector's specifications or measurements for these parameters and the gain, keeping the bias below ``range - 1`` to leave room for signal.
The defaults allow older configurations to run, but measured values give more useful saturation estimates.


Adding a filter or instrument
-----------------------------

Adding a filter
~~~~~~~~~~~~~~~

A new filter is a good first customization: add its transmission table to the instrument's filter directory, then list it in ``[instruments.filters.transmission].files``.
For a camera with a single custom ``r`` filter, the entry would look like this:

.. code-block:: toml

   [instruments.filters.transmission]
   files = [
       {id = "my_r", name = "My r", file = "my_r.fits", default = true}
   ]

Replace the corresponding table in your copied instrument definition with this fragment.
The filename is resolved through the root, instrument, filter, and transmission paths.
For example, with ``path = "instruments/mycamera"`` on the instrument, ``path = "filters"`` on its filter component, and no transmission path, the file is ``/srv/pydiet-custom/data/instruments/mycamera/filters/my_r.fits``.

Transmission files are tables with ``WAVELENGTH`` and ``THROUGHPUT`` columns.
Wavelengths must carry physical wavelength units; throughput is a dimensionless fraction, rather than a percentage.
Use increasing wavelengths, enough sampling to resolve the bandpass, and coverage sufficient for the calculations you intend to perform.
These tables are read into `Synphot <https://synphot.readthedocs.io/en/stable/>`_ spectral elements.
Keep atmospheric transmission, mirror reflectance, optics throughput, filter transmission, and detector quantum efficiency separate to avoid counting a component twice.

The repository's ``utils/extract_filter.py`` converts ASCII tables to this format.
For an input with wavelength in nm and throughput in percent, run from the repository root:

.. code-block:: console

   python utils/extract_filter.py filter_percent.txt my_r.fits \
       --wunit nm --multiply 0.01 --filter my_r

Use an ASCII table whose first column is named ``col1`` and whose second column contains the response.
The converter averages all columns after ``col1`` if more than one response column is present.
Omit ``--multiply 0.01`` when your response is already a fraction.
Copy the resulting FITS file into the configured directory.

After a server restart and browser reload, the client loads your filter into the menu through ``/api/instruments``; no manual menu edit is needed.
The browser keeps a valid saved choice; otherwise, it selects the first filter marked ``default = true``, or the first filter if none is marked.
It replaces saved choices that refer to removed filters automatically.
If supplying explicit filter emission files, add a matching emission entry with the same ID; otherwise the filter's thermal emission is derived from its throughput and configured temperature.

Adding an instrument and telescope
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a new camera, copy a complete ``[[instruments]]`` block, including its optics, filters, detector, and nested tables.
Change its ``id``, ``name``, ``description``, and ``path``, then update ``site_id`` and ``telescope_id``.
Set the collecting and obstructed areas, pixel scales, gain, readout noise, full-well capacity, digital range, bias, overhead, and |PSF| shape from your instrument's measurements.
Replace the spectral files, and check that the resulting throughput is physically plausible.
Changing ``wavelength_range`` alone does not trim the spectra used by the engine; supply appropriately bounded input spectra.

If you also need a new telescope, copy a complete ``[[telescopes]]`` block and replace its geometry and combined mirror curves.
Each mirror file is an alternative mirror condition, not another mirror in a serial optical train.
For a multi-mirror telescope, supply the combined throughput for each condition.
Keep ``collecting_area`` as the full geometric area, and put the telescope's default blocked area in ``telescopes.obstruction_area``.
Omit ``instruments.obstruction_area`` to inherit that value, or supply it to override the blocked area for a particular instrument.
The effective collecting area is ``telescopes.collecting_area - obstruction_area``, using the resolved instrument obstruction.
For example, a telescope with ``collecting_area = "2.5 m2"`` and ``obstruction_area = "0.2 m2"`` provides an effective area of 2.3 m² to an instrument that omits its own obstruction.
An instrument override of ``obstruction_area = "0.3 m2"`` gives 2.2 m² instead.
The inherited value is resolved at startup and used in both cached instrumental quantities and subsequent calculations.

Choose one default instrument and supply explicit filter and mirror values in requests for other instruments.
The API's omitted filter and mirror defaults come from the default instrument, and may not be valid for a different instrument.
The web interface also needs a template directory named after the new instrument's ID, as described below.


Changing the observing site
---------------------------

Moving the calculator to another observatory starts with the atmosphere.
Copy a complete ``[[sites]]`` block, give it a new ID, and point your instrument's ``site_id`` to it.
Then replace the transmission and sky emission files with models or measurements for your site: changing its name or altitude alone does not recompute the spectra.
Set typical seeing and transparency separately as initial values in the form; observers can adjust them for each calculation.

For atmospheric transmission, each file entry needs ``vars = {am = ...}``.
For sky emission, each file needs an airmass and the sky and solar-activity labels used by the query.
For example, this fragment describes two sky spectra for dark time and average solar activity:

.. code-block:: toml

   [sites.emission]
   path = "emission"
   files = [
       {vars = {am = 1.0, sky = "dark", solar = "average"}, file = "dark_am1.fits"},
       {vars = {am = 2.0, sky = "dark", solar = "average"}, file = "dark_am2.fits"}
   ]

Sky files contain ``WAVELENGTH`` and ``PHOTLAM`` columns with units.
The ``PHOTLAM`` column must contain spectral surface brightness that Astropy can convert to Jy per square arcsecond using its wavelength-dependent spectral-density equivalency.
Photon flux density per unit wavelength and per square arcsecond is one suitable representation.
It is not an integrated broad-band sky magnitude.

The engine first selects emission files whose ``sky`` and ``solar`` labels match the query, then interpolates linearly between the surrounding airmasses.
Above the largest tabulated airmass it retains the last spectrum; below the smallest it scales the first spectrum toward zero at airmass zero.
Provide a grid spanning the airmasses you expect to use, for both transmission and each supported sky/solar combination.
Missing sky/solar combinations cause calculation failures rather than selecting another combination automatically.
The supported sky labels are ``dark``, ``grey``, and ``bright``; solar labels are ``low``, ``average``, and ``high``.
The query also supports ``sky = "specify"`` for a user-supplied broad-band sky brightness.

Offer observers only the conditions covered by your data, with initial values that work together.
For the example above, that means dark sky and average solar activity; add the other spectral grids before expanding the menus.


Customizing the web interface
-----------------------------

With the physical model in place, you can tailor what observers see.
The interface uses `Ionic <https://ionicframework.com/docs/>`_ components in Jinja2 templates, with separate files for the form and results.
The browser requests ``/ui/<instrument>/etc_form`` to build the form, and ``/ui/<instrument>/etc_results/query`` to display a calculation.
The server resolves these to ``<instrument>/etc_form.html`` and ``<instrument>/etc_results.html`` within ``template_dir``.
For a new ``mycamera`` instrument, copy the two files from ``megacam`` or ``wircam`` into ``templates/mycamera`` and edit the copies.

.. list-table:: Interface files
   :header-rows: 1
   :widths: 40 60

   * - File, relative to the configured directory
     - Purpose
   * - ``templates/common/base.html``
     - Page structure, title, navigation, footer, stylesheet links, and client script.
   * - ``templates/common/settings.html``
     - Theme and instrument selectors.
   * - ``templates/<instrument>/etc_form.html``
     - Input controls, initial values, units, explanatory text, and instrument images.
   * - ``templates/<instrument>/etc_results.html``
     - Result labels, numeric formatting, units, layout, plots, and source preview.
   * - ``templates/common/terms.html``, ``templates/common/privacy.html``
     - Legal and privacy text to review for your service.
   * - ``client/css/style.css``
     - Shared styles, light and dark colors, and component overrides.
   * - ``client/images/<instrument>/``
     - ``logo.png`` and ``background.jpg`` referenced by the supplied forms.

The component templates receive ``instrument`` as an ID string, ``root_path`` as the external URL prefix, and ``package`` as package metadata.
Result templates additionally receive ``r``, the computed response object.
Form templates do not receive the instrument model itself; the browser obtains the models separately through the instruments API.
Keep ``{{ root_path }}`` in local asset URLs so that the interface also works behind a proxy with a URL prefix.

Changing the ETC form
~~~~~~~~~~~~~~~~~~~~~

Start with the small details that make a form feel familiar: labels, typical observing conditions, help text, and layout.
These live in ``etc_form.html``.
For example, this seeing control starts at 1 arcsecond:

.. code-block:: html+jinja

   <ion-input name="seeing" label="Seeing FWHM [arcsec]"
       label-placement="floating" fill="solid" type="number"
       min="0.1" max="20.0" step="0.01" value="1.0"></ion-input>

Keep ``name="seeing"`` when changing the label: the name tells the API which value it is receiving.
Browser-side bounds do not change the server's validation rules.
Similarly, changing an input's displayed units does not change how its numeric value is interpreted; keep labels consistent with the query model.
For supported fields, choices, and units, consult the interactive API documentation at ``/docs`` and ``src/pydiet/server/models/query.py``.
Adding a new physical input requires engine and query-model support, beyond a template change.

Preserve the hooks used by the bundled client: ``id="etc-form"``, ``id="select-filters"``, and ``name="filter"``.
Keep ``name="filter_upload"`` if retaining filter uploads.
The supplied inline event handlers also depend on classes such as ``snr``, ``galaxy``, ``photometry``, ``brightness``, ``stacking``, and ``filter-upload``.
When simplifying the form, update or remove handlers that refer to controls you remove.
Supply a hidden input with a supported value when fixing a setting that would otherwise fall back to an unsuitable API default.

Mirror, sky, and solar menus in the supplied templates are hard-coded.
Change their option values to match your mirror IDs and the available atmospheric models.
The instrument selector and filter list are populated from the API, while many other form defaults are independent of TOML ``default`` flags.
The browser remembers instrument and filter selections, so test changed defaults with cleared site storage or a fresh browser profile.

Changing result presentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Put the results most useful to your observers first.
In ``etc_results.html``, you can reorder rows, adjust labels and precision, or display another value from the response model.
For example, add this row to show the instrumental zero-point:

.. code-block:: html+jinja

   <ion-row class="etc-summary">
     <ion-col>Instrumental zero-point (per second)</ion-col>
     <ion-col size="4">{{ '{:.2f}'.format(r.zp_instru) }} mag<sub>AB</sub></ion-col>
   </ion-row>

The main result values are ``r.snr``, ``r.etime``, ``r.ttime``, ``r.zp``, ``r.zp_instru``, ``r.bkg_mag``, ``r.bkg_rate``, ``r.lambda_pivot``, and ``r.bandwidth_rect``.
Times are in seconds, wavelengths and bandwidths in nm, zero-points in AB magnitudes, and background surface brightness in AB magnitudes per square arcsecond.
Saturation estimates are ``r.etime_skysat`` and ``r.etime_sourcesat``; they use the threshold set by the detector's full-well capacity, digital range, bias, and gain.
See ``src/pydiet/server/models/response.py`` for the complete response fields and their meanings.

Retain the ``etc-results-modal`` ID if keeping the existing close button.
If keeping the transmission plot, preserve its canvas ID and the call to ``plot_filter`` with the JSON-encoded transmission fields.
The source preview uses ``r.cutout`` as an image URL.
These display assets are generated for UI calculations; ordinary API calculations do not include them by default.

Changing CSS and branding
~~~~~~~~~~~~~~~~~~~~~~~~~

Give the form and results a consistent appearance in ``client/css/style.css``.
Use the template's ``ion-col`` sizes for the responsive grid, and CSS for spacing, typography, and colors.
For example, a few rules make the zero-point row above stand out:

.. code-block:: css

   .etc-summary {
     font-weight: 600;
     border-top: 1px solid var(--ion-color-medium);
     padding-top: 0.5rem;
   }

The stylesheet uses ``body.dark`` for dark-mode overrides.
Check both light and dark themes, and use Ionic's component CSS properties where ordinary selectors cannot reach a component's internal elements.
Replace the instrument images in ``client/images/mycamera`` or update their template URLs.
Edit ``common/base.html`` to change the page title, header, footer, and observatory link; ``base_template`` can select an alternative page template.
Retain the client script, ``root_path`` metadata, and the ``content-slot`` and ``modal-slot`` containers used to insert forms and results.

To keep your styling easy to maintain, you can put it in a separate ``client/css/custom.css`` file.
Load it from a new ``common/custom_base.html`` template using the base template's existing head block:

.. code-block:: html+jinja

   {% extends "common/base.html" %}
   {% block headcontent %}
     {{ super() }}
     <link rel="stylesheet" href="{{ root_path }}/client/css/custom.css" />
   {% endblock headcontent %}

Then set ``base_template = common/custom_base.html`` in the server configuration's ``[server]`` section.
Template and CSS changes do not require rebuilding the JavaScript bundle.
If changing client JavaScript as well, rebuild ``dist/pydiet.js`` from the corresponding sources and deploy the updated bundle.


Checking the customized calculator
----------------------------------

Try the calculator as an observer would, starting with a server restart and a fresh browser load.
Check the logs for missing files, invalid units, unresolved IDs, and spectral-model errors, then look for your instrument and filters in ``/api/instruments`` and the interface.
Work through every offered filter, mirror, sky, and solar combination, including the edges of your airmass grid.
Try both exposure-time and |SNR| calculations, representative source types, and any file-upload options.

The most useful check is a comparison with real observations: compare predicted zero-points, sky brightnesses, exposure times, and |SNR| with your instrument's measured performance.
Check the effects of overheads and pixel scales, and compare saturation estimates with your detector's capacity, digital range, bias, and gain.
Finish by trying a narrow screen and both themes, including a deployment under a URL prefix if you use one.

