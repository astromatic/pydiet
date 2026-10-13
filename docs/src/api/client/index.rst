JavaScript client
=================

The browser client loads instruments, submits calculations, and displays
the results. These pages describe its exported JavaScript
functions and constants, including their JSDoc examples.

The modules live in ``src/pydiet/web_client/js`` and run in a browser with the
page structure provided by the Jinja2 templates. ``main.js`` initializes the
client; it has no exported API.

.. toctree::
   :maxdepth: 2

   url
   fetch
   dom
   instrument
   etc
   plot
   settings
   theme
   health

