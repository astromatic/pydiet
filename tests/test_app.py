"""Tests for FastAPI application construction and basic routes."""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

import asyncio

from pydiet.server import app as app_module


def test_health_instruments_and_ui_routes(tmp_path, monkeypatch):
    # Build the app without documentation and verify core API route registration.
    for key in ("client_dir", "data_dir", "extra_dir", "template_dir"):
        directory = tmp_path / key
        directory.mkdir()
        monkeypatch.setitem(app_module.settings, key, str(directory))
    monkeypatch.setitem(app_module.settings, "doc_dir", str(tmp_path / "missing-docs"))

    app = app_module.create_app()
    health_route = next(route for route in app.routes if route.path == "/api/health")
    assert asyncio.run(health_route.endpoint()) == {"ok": True}
    assert any(route.path == "/api/instruments" for route in app.routes)


def test_app_mounts_existing_documentation(tmp_path, monkeypatch):
    # Ensure an existing documentation directory is mounted by the app factory.
    for key in ("client_dir", "data_dir", "extra_dir", "template_dir", "doc_dir"):
        directory = tmp_path / key
        directory.mkdir()
        monkeypatch.setitem(app_module.settings, key, str(directory))
    app = app_module.create_app()
    assert any(route.name == "manual" for route in app.routes)
