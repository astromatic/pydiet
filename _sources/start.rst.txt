.. File start.rst

.. include:: global.rst

.. _chap_start:

Getting started
===============

Planning an imaging observation? |PyDIET| helps you estimate the exposure time needed to reach a target |SNR|, or the |SNR| you can expect from a given exposure.
CFHT runs it at `pydiet.cfht.hawaii.edu <https://pydiet.cfht.hawaii.edu/>`_.
You can also run it on your computer, host it for other observers, or adapt it to your own imaging system.
Its complete :ref:`web API <chap_webapi>` lets you bring the calculator into your scripts and observing tools, with a Python client included.


Try it in your browser
----------------------

The quickest way to get a feel for the calculator is to open the `CFHT service <https://pydiet.cfht.hawaii.edu/>`_.
Choose MegaCam or WIRCam, select a filter, and enter your source brightness and observing conditions.
Then ask for an exposure time or |SNR| and explore how the result changes with seeing, sky brightness, or the number of exposures.
The :ref:`chap_interface` chapter walks through the form and results.


Run it on your computer
-----------------------

For a local copy, install `Python <https://www.python.org/>`_ 3.10 or later, `Git <https://git-scm.com/>`_, and Python's virtual-environment support.
In a terminal, download the source and install it with `pip <https://pip.pypa.io/en/stable/>`_ in a virtual environment:

.. code-block:: console

   git clone https://github.com/astromatic/pydiet.git
   cd pydiet
   python3 -m venv .venv
   . .venv/bin/activate
   python -m pip install .

With the environment active, start the calculator and open your browser with:

.. code-block:: console

   pydiet -b

The ``-b`` option opens the web interface once the local server is ready.
You can also visit ``http://localhost:8010/`` yourself.
Keep the terminal open while using the calculator, and press :kbd:`Ctrl-C` when you are finished.
The supplied instrument data and web client are included; :ref:`chap_deploy` explains how to build the local manual and configure the server.


Share it or make it your own
----------------------------

To give colleagues access to the calculator, install it on your own server.
The :ref:`chap_deploy` chapter covers Python and Docker installations, persistent services, HTTPS reverse proxies, and performance tips.

To use another camera, telescope, or observing site, start with the supplied configuration and replace the instrument characteristics and spectra with your own.
You can also tailor the input form, result panels, and styling to suit your observers.
Follow :ref:`chap_customize` for the data configuration reference and interface examples.
