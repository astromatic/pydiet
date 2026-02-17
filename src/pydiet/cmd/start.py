#! /usr/bin/python3
"""
Start script (renamed as :program:`pydiet`).
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence
from sys import exit
from threading import Thread
from time import sleep
import socket
from urllib.request import urlopen
from urllib.error import URLError
import webbrowser

from uvicorn import Config, Server

from pydiet.server import config


def wait_until_port_open(host: str, port: int):
    while True:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.05)


def main() -> int:
    """
    Set up configuration and start the PyDIET server.
    """
    # Configure the server
    server = Server(
        Config(
            app="pydiet.server.app:create_app",
            host=config.settings["host"],
            port=config.settings["port"],
            root_path=config.settings["root_path"],
            access_log=config.settings["access_log"],
            workers=config.settings["workers"],
            reload=config.settings["reload"],
            factory=True
        )
    )

    # Run main server process in a thread to make it non-blocking
    thread = Thread(target=server.run, daemon=True)
    thread.start()
    
    if config.settings["browser"]:
        # Start browser only when the server is operational
        link =  f"http://{config.settings['host']}:{config.settings['port']}"
        f"{config.settings['root_path'] or ''}"
        while True:
            try:
                # succeeds only when server is actually up
                urlopen(
                    f"{link}{config.settings['api_path']}/health",
                    timeout=2
                )
                break
            except URLError:
                sleep(0.5)
        webbrowser.open(link)

    # Back to main thread
    thread.join()

    return 0

if __name__ == "__main__":
    exit(main())

