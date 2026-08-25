"""Tests for the synchronous Python API client."""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from types import SimpleNamespace

import httpx
import pytest
from pydantic import ValidationError

from pydiet.api_client.client import Client
from pydiet.server.models.default import default_filter, default_instrument, default_mirror
from pydiet.server.models.query import ETCQueryModel


def query():
    return ETCQueryModel(
        instrument=default_instrument.id,
        filter=default_filter.id,
        mirror=default_mirror.id,
    )


class FakeClient:
    response = None
    error = None
    request = None

    def __init__(self, **kwargs):
        self.options = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, url, params):
        type(self).request = (url, params)
        if self.error:
            raise self.error
        return self.response


def response(payload, *, status=200, json_error=None):
    request = httpx.Request("GET", "https://example.test/api/demo")
    raw = httpx.Response(status, request=request, json=payload)
    if json_error:
        raw.json = lambda: (_ for _ in ()).throw(json_error)  # type: ignore[method-assign]
    return raw


def test_client_success_and_default_url(monkeypatch):
    # Validate request construction, response parsing, and the configured URL.
    payload = {"instrument": "Demo", "filter": "g", "compute": "etime"}
    FakeClient.response = response(payload)
    FakeClient.error = None
    monkeypatch.setattr(httpx, "Client", FakeClient)
    client = Client("https://example.test/api")
    result = client.query(query(), timeout=3)
    assert result.instrument == "Demo"
    assert FakeClient.request[0].endswith(f"/{default_instrument.id}")
    assert "instrument" not in FakeClient.request[1]
    assert Client().api_url.startswith("http://")


def test_client_error_translation(monkeypatch):
    # Confirm transport, HTTP, JSON, and schema failures become RuntimeError.
    monkeypatch.setattr(httpx, "Client", FakeClient)
    client = Client("https://example.test/api")

    FakeClient.response = response({"detail": "bad"}, status=400)
    FakeClient.error = None
    with pytest.raises(RuntimeError, match="HTTP error 400"):
        client.query(query())

    FakeClient.error = httpx.ConnectError("offline")
    with pytest.raises(RuntimeError, match="Transport error"):
        client.query(query())

    FakeClient.error = None
    FakeClient.response = response({}, json_error=ValueError("bad json"))
    with pytest.raises(RuntimeError, match="not valid JSON"):
        client.query(query())

    FakeClient.response = response({"instrument": "Demo"})
    with pytest.raises(RuntimeError, match="Invalid response schema"):
        client.query(query())
