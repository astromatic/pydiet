#! /usr/bin/python3
"""
Start script (renamed as :program:`pydiet`).
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence
from sys import exit
from threading import Thread
from time import sleep
from urllib.request import urlopen
from urllib.error import URLError
import webbrowser

from uvicorn import run

from pydiet.server import config


def start_server(
        app: str="pydiet.server.app:create_app",
        host: str="localhost",
        port: int=8010,
        root_path: str="",
        workers: int=4,
        access_log: bool=False,
        reload: bool=True
    ) -> None:
    """
    Start the Uvicorn server in application factory mode.
    
    Parameters
    ----------
    app: str, optional
        Name of the ASGI app callable.
    host: str, optional
        Host name or IP address.
    port: int, optional
        Port.
    root_path: str | ~pathlib.Path, optional
        ASGI root_path.
    workers: int, optional
        Number of workers.
    access_log: bool, optional
        Display access log.
    reload: bool, optional
        Enable auto-reload (turns off multiple workers).

    Returns
    -------
    None
        This function returns after the Uvicorn server stops.
    """
    run(
        app,
        host=host,
        port=port,
        root_path=root_path,
        access_log=access_log,
        workers=workers,
        reload=reload,
        factory=True
    )
    return


def open_browser_when_ready(
        host: str, port: int, root_path: str, api_path: str) -> None:
    """
    Open the web client once the server health endpoint responds.

    Parameters
    ----------
    host: str
        Server host name or IP address.
    port: int
        Server port.
    root_path: str
        ASGI root path included in the browser URL.
    api_path: str
        API path containing the ``/health`` endpoint.

    Notes
    -----
    Connection failures are retried every half second without a retry limit.
    """
    link =  f"http://{host}:{port}{root_path or ''}"
    f"{config.settings['root_path'] or ''}"
    while True:
        try:
            # succeeds only when server is actually up
            urlopen(f"{link}{api_path}/health", timeout=2)
            break
        except URLError:
            sleep(0.5)
    webbrowser.open(link)


def main() -> int:
    """
    Set up configuration and start the PyDIET server.

    Returns
    -------
    status: int
        Zero after the server stops normally.
    """
    if config.settings["browser"]:
        # Start watcher thread to open browser when server is ready
        Thread(
            target=open_browser_when_ready,
            args=(
                config.settings["host"],
                config.settings["port"],
                config.settings["root_path"],
                config.settings["api_path"]
            ),
            daemon=True,
        ).start()

    # Start the server itself
    start_server(
        host=config.settings["host"],
        port=config.settings["port"],
        root_path=config.settings["root_path"],
        access_log=config.settings["access_log"],
        reload=config.settings["reload"],
        workers=config.settings["workers"]
    )
    return 0

if __name__ == "__main__":
    exit(main())
