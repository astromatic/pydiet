.. File deploy.rst

.. include:: global.rst

.. _chap_deploy:

Deploying the ETC
=================

You can run |PyDIET| on your own computer or make it available to other observers on a shared server.
Its `FastAPI <https://fastapi.tiangolo.com/>`_ application, served by `Uvicorn <https://uvicorn.dev/>`_, provides the web interface, calculation API, and locally built manual in one service.
Choose a Python installation or a `Docker <https://www.docker.com/>`_ container below, then add a reverse proxy if you want to share it over HTTPS.
The examples use the supplied instrument data and the default port, ``8010``.

For personal use, bind to ``127.0.0.1`` to keep access on your computer.
For a shared installation, let `Apache httpd <https://httpd.apache.org/>`_ or `nginx <https://nginx.org/>`_ accept HTTPS connections and forward them to |PyDIET| over a private HTTP connection.
The proxy examples place both services on the same host, using ``pydiet.example.org`` as a dedicated hostname.
Replace that hostname and the certificate paths with your own.


Installation without Docker
---------------------------

Start with `Python <https://www.python.org/>`_ 3.10 or later, `Git <https://git-scm.com/>`_, and Python's virtual-environment support.
From a directory where you keep application sources, create an environment and install |PyDIET| with `pip <https://pip.pypa.io/en/stable/>`_:

.. code-block:: console

   git clone https://github.com/astromatic/pydiet.git
   cd pydiet
   python3 -m venv .venv
   . .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install .

The instrument data and web client come with the repository, so you can start the calculator straight away.
To include a local HTML manual, also install `Node.js <https://nodejs.org/>`_ and `npm <https://docs.npmjs.com/>`_, then build the manual with `Sphinx <https://www.sphinx-doc.org/>`_, `JSDoc <https://jsdoc.app/>`_, and `make <https://www.gnu.org/software/make/>`_:

.. code-block:: console

   python -m pip install '.[doc]'
   npm install --global jsdoc
   make -C docs inline
   python -m pip install .

The final installation step packages the generated manual with the application.
You can skip the manual build for a smaller setup; calculations and the interface still work, with the manual link disabled if its directory is absent.

Starting the server
~~~~~~~~~~~~~~~~~~~

Give the server a directory for any files you want to publish through ``/extra``—an empty one is fine—then start it:

.. code-block:: console

   mkdir -p "$HOME/pydiet-extra"
   pydiet --host 127.0.0.1 --port 8010 --workers 1 \
       --extra_dir "$HOME/pydiet-extra" --browser

Your browser should open at ``http://127.0.0.1:8010/``; you can also visit that address yourself.
Leave out ``--browser`` when running a background service, and use :kbd:`Ctrl-C` to stop a foreground server.
A quick `curl <https://curl.se/>`_ request checks that the API is ready:

.. code-block:: console

   curl --fail http://127.0.0.1:8010/api/health

A successful health check returns ``{"ok":true}``.
Next, try a calculation in the interface, explore the API at ``/docs``, or open the built manual at ``/manual/index.html``.

.. note::

   Files in ``extra_dir`` are public through ``/extra``; by default, this is the current working directory.
   Set a dedicated directory for a shared installation and keep private files, including configuration, elsewhere.
   |PyDIET| has no login mechanism, so use the proxy or your network to restrict a private service to its intended users.

Configuration
~~~~~~~~~~~~~

Once the server is running, collect its settings in an INI file to make the setup easy to repeat.
You can also use ``PYDIET_`` environment variables or command-line options; the INI file overrides the environment, and command-line options take precedence over both.
Use ``pydiet --help`` for the full list.
For a small shared installation, save this as ``/etc/pydiet/pydiet.conf``:

.. code-block:: ini

   [host]
   host = 127.0.0.1
   port = 8010
   workers = 1
   reload = false
   access_log = false

   [server]
   browser = false
   extra_dir = /var/lib/pydiet/extra

Create a readable ``extra_dir`` directory, then launch with ``pydiet --config /etc/pydiet/pydiet.conf``.
Settings you leave out keep their defaults.
Use an explicit configuration path for a service: the default printed by ``pydiet --help`` depends on the account running the command.
To see which settings are in effect, add ``--show_config``; it prints them before starting the server.

To use your own instrument, set ``data_config`` to your TOML file in ``[server]`` and set that file's top-level ``path`` to the spectral-data directory.
The server's ``data_dir`` is a separate setting; :ref:`chap_customize` shows how to arrange the data, templates, and styles together.
Use absolute paths for a service, and restart it after changing data, templates, or configuration.

Running as a system service
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a server that starts at boot and runs without an open terminal, use a service manager.
On `Linux <https://www.kernel.org/>`_ with `systemd <https://systemd.io/>`_, place the checkout and virtual environment under ``/opt/pydiet``.
Create an unprivileged ``pydiet`` account, the configuration above, and a readable ``/var/lib/pydiet/extra`` directory.
Ensure that account can read and traverse the installation and data directories, then save this as ``/etc/systemd/system/pydiet.service``:

.. code-block:: ini

   [Unit]
   Description=PyDIET exposure time calculator
   After=network.target

   [Service]
   Type=simple
   User=pydiet
   Group=pydiet
   WorkingDirectory=/var/lib/pydiet
   ExecStart=/opt/pydiet/.venv/bin/pydiet --config /etc/pydiet/pydiet.conf
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target

Enable the service at boot, start it now, and check its status and logs:

.. code-block:: console

   sudo systemctl daemon-reload
   sudo systemctl enable --now pydiet
   sudo systemctl status pydiet
   sudo journalctl -u pydiet -f


Installation with Docker
------------------------

If you prefer a container, install Docker with the `Compose <https://docs.docker.com/compose/>`_ plugin and build the supplied Dockerfile from the repository root:

.. code-block:: console

   docker build -t pydiet:latest -f docker/Dockerfile .

The image includes the HTML manual and activates its Python environment on startup.
Supply the server command when launching the container:

.. code-block:: console

   docker run -d --name pydiet --restart unless-stopped \
       -p 127.0.0.1:8010:8010 \
       pydiet:latest pydiet --host 0.0.0.0 --port 8010 \
       --workers 1 --extra_dir /tmp

The two addresses serve different purposes: ``0.0.0.0`` lets Docker reach the process *inside* the container, while ``127.0.0.1`` keeps the published port on the host's loopback interface.
You can then connect locally or through a reverse proxy on that host.
Here ``/tmp`` provides an initially empty ``extra_dir``; keep private files out of it.
To publish your own extra files, mount a dedicated directory read-only and give ``--extra_dir`` its container path.

Use the earlier ``curl`` command to check the health endpoint.
To follow the logs or stop the container, run:

.. code-block:: console

   docker logs -f pydiet
   docker stop pydiet

For a setup you can launch again with one command, save this Compose file as ``compose.local.yml`` at the repository root:

.. code-block:: yaml

   services:
     pydiet-service:
       image: pydiet:latest
       build:
         context: .
         dockerfile: docker/Dockerfile
       restart: unless-stopped
       ports:
         - "127.0.0.1:8010:8010"
       command:
         - pydiet
         - --host
         - 0.0.0.0
         - --workers
         - "1"
         - --extra_dir
         - /tmp

Build and start it, follow its logs, or shut it down with:

.. code-block:: console

   docker compose -f compose.local.yml up -d --build
   docker compose -f compose.local.yml logs -f
   docker compose -f compose.local.yml down

Use the explicit filename above with the reverse-proxy examples: the repository's ``docker-compose.yml`` publishes host port ``80`` on all interfaces and uses the default worker count.
Keep custom data outside the container, since recreating it replaces its files.
Mount your data directory and INI file read-only, then pass ``--config`` with the INI file's *container* path.
Paths in both the INI and TOML files must describe locations inside the container.


Reverse proxy
-------------

To share the calculator over HTTPS, put Apache httpd or nginx in front of it.
You will need a DNS record for your hostname and a valid TLS certificate.
Choose either example below: both redirect HTTP to HTTPS and forward the interface, API, and static files to the loopback server.
Start with the illustrated 120-second timeouts, then adjust them to suit representative calculations.

The proxy passes along the original scheme and client address in forwarded headers, which Uvicorn accepts only from trusted peers.
For a native server, a proxy connecting from ``127.0.0.1`` is trusted by default.
With Docker's bridge networking, the peer seen by Uvicorn may instead be the Docker bridge gateway.
Set ``FORWARDED_ALLOW_IPS`` in the container environment to the actual proxy peer address if necessary; do not use a wildcard to trust arbitrary peers.
Keep the backend port private.

Apache httpd
~~~~~~~~~~~~

Enable `mod_proxy <https://httpd.apache.org/docs/2.4/mod/mod_proxy.html>`_, `mod_proxy_http <https://httpd.apache.org/docs/2.4/mod/mod_proxy_http.html>`_, `mod_headers <https://httpd.apache.org/docs/2.4/mod/mod_headers.html>`_, `mod_ssl <https://httpd.apache.org/docs/2.4/mod/mod_ssl.html>`_, and `mod_alias <https://httpd.apache.org/docs/2.4/mod/mod_alias.html>`_.
Then add these virtual hosts to your Apache configuration:

.. code-block:: apache

   <VirtualHost *:80>
       ServerName pydiet.example.org
       Redirect permanent / https://pydiet.example.org/
   </VirtualHost>

   <VirtualHost *:443>
       ServerName pydiet.example.org
       SSLEngine on
       SSLCertificateFile /etc/letsencrypt/live/pydiet.example.org/fullchain.pem
       SSLCertificateKeyFile /etc/letsencrypt/live/pydiet.example.org/privkey.pem

       ProxyRequests Off
       ProxyPreserveHost On
       RequestHeader unset X-Forwarded-For
       RequestHeader set X-Forwarded-Proto "https"
       ProxyPass "/" "http://127.0.0.1:8010/" connectiontimeout=5 timeout=120
       ProxyPassReverse "/" "http://127.0.0.1:8010/"
   </VirtualHost>

Apache adds the client address to ``X-Forwarded-For`` after the incoming value is removed.
Test the configuration with ``apachectl configtest`` (``apache2ctl configtest`` on some distributions), then reload the Apache service.
See the `Apache reverse-proxy documentation <https://httpd.apache.org/docs/2.4/mod/mod_proxy.html>`_ for directive details.

nginx
~~~~~

Add the following server blocks inside nginx's ``http`` configuration:

.. code-block:: nginx

   server {
       listen 80;
       server_name pydiet.example.org;
       return 301 https://pydiet.example.org$request_uri;
   }

   server {
       listen 443 ssl;
       server_name pydiet.example.org;
       ssl_certificate /etc/letsencrypt/live/pydiet.example.org/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/pydiet.example.org/privkey.pem;

       # Adjust if uploaded filter files exceed this size.
       client_max_body_size 20m;

       location / {
           proxy_pass http://127.0.0.1:8010;
           proxy_http_version 1.1;
           proxy_set_header Connection "";
           proxy_set_header Host $host;
           proxy_set_header X-Forwarded-For $remote_addr;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_connect_timeout 5s;
           proxy_read_timeout 120s;
           proxy_send_timeout 120s;
       }
   }

Test with ``sudo nginx -t`` and reload with ``sudo systemctl reload nginx`` on systemd installations.
See the `nginx proxy module documentation <https://nginx.org/en/docs/http/ngx_http_proxy_module.html>`_ for directive details.
Whichever proxy you choose, visit ``https://pydiet.example.org/api/health``, then open the interface and try a calculation.
Try a file upload too if your observers will use custom filters.

Serving under a URL prefix
~~~~~~~~~~~~~~~~~~~~~~~~~~

If your calculator shares a hostname with other services, you can give it a path such as ``https://example.org/pydiet/``.
Start the backend with ``--root_path /pydiet`` (without a trailing slash), and have the proxy remove that prefix before forwarding requests.
For Apache, replace the root ``ProxyPass`` and ``ProxyPassReverse`` rules with:

.. code-block:: apache

   ProxyPass "/pydiet/" "http://127.0.0.1:8010/" connectiontimeout=5 timeout=120
   ProxyPassReverse "/pydiet/" "http://127.0.0.1:8010/"

For nginx, replace ``location /`` with ``location /pydiet/`` and use ``proxy_pass http://127.0.0.1:8010/;``.
The trailing slash on that upstream URL makes nginx replace the matching prefix.
Retain the other proxy headers and timeout settings, and configure a redirect from ``/pydiet`` to ``/pydiet/``.
Keep ``api_path`` at ``/api``; ``root_path`` supplies the external prefix for the web client's URLs.
The public health endpoint is then ``/pydiet/api/health``.


Performance
-----------

Start small and measure with the calculations your observers actually run.
A few settings help you make the most of the machine:

* **Match workers to demand.** Start with ``--workers 1`` for personal use or a small machine.
  The default is four workers on Linux and one on other platforms.
  Each worker loads instrument data and prepares its own cached quantities, increasing both startup cost and memory use.
  More workers can serve simultaneous calculations, but need more memory; check response times and memory use as you increase the count.

* **Restart when you update.** Keep ``reload = false`` for a persistent service.
  Automatic ``--reload`` is useful during development, but disables multiple workers.

* **Let the server finish starting.** Each worker loads instrument data at startup.
  Wait for the health endpoint, then try representative point-source and galaxy calculations before judging performance.
  Use local storage for the data and leave enough memory for all workers without swapping.

* **Let the proxy help with delivery.** Enable compression for text assets; for a busy installation, consider serving ``/client/`` and the built manual directly from the proxy.
  Keep those files synchronized with the installed package, preserve any URL prefix, and avoid long cache lifetimes for assets whose filenames do not change between releases.
  Keep calculation and health responses uncached.

* **Watch a realistic workload.** Monitor CPU use, resident memory, proxy logs, and calculation latency with your expected number of simultaneous users.
  Enable ``--access_log`` temporarily when diagnosing requests; the proxy can provide routine access logs.
  A larger timeout allows a slow request to finish but does not make its calculation faster.


