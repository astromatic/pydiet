"""Tests for command-line server startup helpers."""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from urllib.error import URLError

from pydiet.cmd import start


def test_start_server_forwards_uvicorn_options(monkeypatch):
    # Ensure the public startup wrapper forwards options to Uvicorn.
    calls = []
    monkeypatch.setattr(start, "run", lambda *args, **kwargs: calls.append((args, kwargs)))
    assert start.start_server(port=9000, reload=False) is None
    assert calls[0][1]["port"] == 9000
    assert calls[0][1]["factory"] is True


def test_browser_wait_retries_then_opens(monkeypatch):
    # Simulate one failed health check before the browser opens successfully.
    attempts = iter([URLError("offline"), object()])

    def urlopen(*args, **kwargs):
        result = next(attempts)
        if isinstance(result, Exception):
            raise result
        return result

    opened = []
    monkeypatch.setattr(start, "urlopen", urlopen)
    monkeypatch.setattr(start, "sleep", lambda delay: None)
    monkeypatch.setattr(start.webbrowser, "open", opened.append)
    start.open_browser_when_ready("localhost", 8010, "/root", "/api")
    assert opened == ["http://localhost:8010/root"]


def test_main_starts_server_without_browser(monkeypatch):
    # Verify the CLI entry point starts the server without creating a watcher.
    calls = []
    monkeypatch.setitem(start.config.settings, "browser", False)
    monkeypatch.setattr(start, "start_server", lambda **kwargs: calls.append(kwargs))
    assert start.main() == 0
    assert calls and calls[0]["port"] == start.config.settings["port"]
