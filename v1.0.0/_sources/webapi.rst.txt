.. File webapi.rst

.. include:: global.rst

.. _chap_webapi:

Using the web API
=================

Want to compare a range of source magnitudes, plan a sequence of observations, or bring |PyDIET| into your own tools?
The web API gives scripts access to the same calculator used by the browser interface, with results returned as JSON.
You can use the CFHT service or a :ref:`local installation <chap_start>`.


Explore before you script
-------------------------

Open the `interactive API documentation <https://pydiet.cfht.hawaii.edu/docs>`_ on the CFHT service, or visit ``http://localhost:8010/docs`` with a local server running.
You can also reach it through **Settings** in the web interface.
Expand an endpoint, choose **Try it out**, enter your observing parameters, and inspect the response.
It is a convenient way to build your first request and see the generated curl command.

The running service supplies its own `OpenAPI <https://www.openapis.org/>`_ description at ``/openapi.json`` and an alternative reference view at ``/redoc``.
Use these for parameter names, defaults, allowed values, and request formats: they reflect the version and instrument configuration you are actually using.


Make your first request
-----------------------

With a local server running on the default port, ask which instruments are available:

.. code-block:: console

   curl --fail http://localhost:8010/api/instruments

Replace ``http://localhost:8010`` with ``https://pydiet.cfht.hawaii.edu`` to query the CFHT service.
The main endpoints, with the default ``/api`` prefix, are:

* ``GET /api/health``: check that the server responds; a successful response is ``{"ok":true}``.
* ``GET /api/instruments``: discover the configured instruments and their available options.
* ``GET /api/{instrument}``: run a calculation using URL query parameters.
* ``POST /api/{instrument}``: run a calculation using form fields, with an optional filter-curve upload.

For a calculation, select an instrument and filter from the running service, then use the interactive documentation to set the source, observing conditions, and target exposure time or |SNR|.
The :ref:`web interface guide <chap_interface>` explains the scientific meaning of these choices.
For POST requests, send form data rather than a JSON request body.

If your installation uses a URL prefix or a different ``api_path``, adjust the request URLs accordingly; see :ref:`chap_deploy`.
When saving results, also record the |PyDIET| version, instrument configuration, and input parameters so you can interpret and compare them later.


Use the Python client
----------------------

Working in Python? The package includes :class:`~pydiet.api_client.client.Client`, which sends the request and returns a validated :class:`~pydiet.server.models.response.ETCResponseModel`.
After :ref:`installing PyDIET <chap_start>`, try estimating the exposure time for a 22nd-magnitude point source in MegaCam's g band:

.. code-block:: python

   from pydiet.api_client.client import Client
   from pydiet.server.models.query import ETCQueryModel

   client = Client("https://pydiet.cfht.hawaii.edu/api")
   query = ETCQueryModel(
       instrument="megacam",
       filter="g",
       compute="etime",
       source="point_source",
       brightness=22.0,
       unit="abmag",
       snr=5.0,
   )
   result = client.query(query)
   print(f"Exposure time: {result.etime:.1f} s")

The other observing parameters keep their model defaults.
For a local server, use ``Client("http://localhost:8010/api")`` instead.
To calculate |SNR| for a fixed exposure, set ``compute="snr"`` and supply ``etime`` in seconds.

The query model validates inputs against your locally installed instrument configuration, so keep it consistent with the server's configuration.
Requests use GET; the client's default timeout is 10 seconds, adjustable with ``client.query(query, timeout=30.0)``.
Request or response failures raise ``RuntimeError``.
See :doc:`api/python_client` for the client reference and the interactive OpenAPI documentation for calculation parameters.
