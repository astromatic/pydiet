"""
Configuration settings for the application.
"""
# Copyright CEA/CFHT/CNRS/UParisSaclay
# Licensed under the MIT licence

from __future__ import annotations

from os import cpu_count, path
from typing import Any, Literal, Tuple

from astropy import units as u #type: ignore[import-untyped]
import numpy as np
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ... import package
from ..types.quantity import AnnotatedQuantity
from .fields import SField

# Enable imperial units such as inches
u.imperial.enable()


class HostSettings(BaseSettings):
    host: str = SField(
        short='H',
        default="localhost",
        description="Host name or IP address"
        )
    port: int = SField(
        short='p',
        default=8009,
        ge=1,
        le=65535,
        description="Port"
        )
    root_path: str = SField(
        short='R',
        default="",
        description="ASGI root_path"
        )
    access_log: bool = SField(
        short='a',
        default=False,
        description="Display access log"
        )
    reload: bool = SField(
        short='r',
        default=False,
        description="Enable auto-reload (turns off multiple workers)"
        )
    workers: int = SField(
        short='w',
        default=4 if package.isonlinux else 1,
        ge=1,
        description="Number of workers"
        )

    model_config = SettingsConfigDict(
        env_prefix = f"{package.name}_",
        extra = 'ignore',
    )


class ServerSettings(BaseSettings):
    api_path : str = SField(
        default="/api",
        description="Endpoint URL for the webservice API"
        )
    banner_template: str = SField(
        default="banner.html",
        description="Name of the HTML template file for the service banner"
        )
    base_template: str = SField(
        default="base.html",
        description="Name of the HTML template file for the web client"
        )
    browser: bool = SField(
        short='b',
        default=False,
        description="Start browser when launching the server"
        )
    client_dir: str = SField(
        default=path.join(package.src_dir, "client"),
        description="Directory containing the web client code, style and media"
        )
    data_dir: str = SField(
        default=path.join(package.root_dir, "data"),
        description="Data root directory"
        )
    doc_dir: str = SField(
        default=path.join(package.root_dir, "doc/html"),
        description="HTML documentation root directory (after build)"
        )
    doc_path: str = SField(
        default="/manual",
        description="Endpoint URL for the root of the HTML documentation"
        )
    extra_dir: str = SField(
        default=".",
        description="Extra data root directory"
        )
    template_dir: str = SField(
        default=path.join(package.src_dir, "templates"),
        description="Directory containing templates"
        )
    userdoc_url: str = SField(
        default = doc_path.default + "/", #type: ignore
        description="Endpoint URL for the user's HTML documentation"
        )

    model_config = SettingsConfigDict(
        env_prefix = f"{package.name}_",
        extra = 'ignore',
    )



ncpu = cpu_count()



class EngineSettings(BaseSettings):
    thread_count: int = SField(
        short='t',
        default = ncpu // 2 if ncpu is not None else 4,
        ge=0,
        le=1024,
        description="Number of engine threads"
        )

    model_config = SettingsConfigDict(
        env_prefix = f"{package.name}_",
        extra = 'ignore',
    )



class MiscSettings(BaseSettings):
    """
    Miscellaneous settings.
    """
    verbose: bool = SField(
        short='v',
        default=True,
        description="Verbose output"
        )

    model_config = SettingsConfigDict(
        env_prefix = f"{package.name}_",
        extra = 'ignore',
        arbitrary_types_allowed = True
    )


class AppSettings(BaseSettings):
    host: BaseSettings = HostSettings()
    server: BaseSettings = ServerSettings()
    engine: BaseSettings = EngineSettings()
    misc: BaseSettings = MiscSettings()

