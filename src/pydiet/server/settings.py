"""
Configuration settings for the application.
"""
# Copyright CEA/CFHT/CNRS/UParisSaclay
# Licensed under the MIT licence

from os import cpu_count, path
from typing import Tuple

from astropy import units as u
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


from .. import package

class HostSettings(BaseSettings):
    host: str = Field(
        short='H',
        default="localhost",
        description="Host name or IP address"
        )
    port: int = Field(
        short='p',
        default=8009,
        ge=1,
        le=65535,
        description="Port"
        )
    root_path: str = Field(
        short='R',
        default="",
        description="ASGI root_path"
        )
    access_log: bool = Field(
        short='a',
        default=False,
        description="Display access log"
        )
    reload: bool = Field(
        short='r',
        default=False,
        description="Enable auto-reload (turns off multiple workers)"
        )
    workers: int = Field(
        short='w',
        default=4 if package.isonlinux else 1,
        ge=1,
        description="Number of workers"
        )

    class Config:
        env_prefix = f"{package.name}_"
        extra = 'ignore'


class ServerSettings(BaseSettings):
    api_path : str = Field(
        default="/api",
        description="Endpoint URL for the webservice API"
        )
    banner_template: str = Field(
        default="banner.html",
        description="Name of the HTML template file for the service banner"
        )
    base_template: str = Field(
        default="base.html",
        description="Name of the HTML template file for the web client"
        )
    browser: bool = Field(
        short='b',
        default=False,
        description="Start browser when launching the server"
        )
    client_dir: str = Field(
        default=path.join(package.src_dir, "client"),
        description="Directory containing the web client code, style and media"
        )
    data_dir: str = Field(
        default=".",
        description="Data root directory"
        )
    doc_dir: str = Field(
        default=path.join(package.root_dir, "doc/html"),
        description="HTML documentation root directory (after build)"
        )
    doc_path: str = Field(
        default="/manual",
        description="Endpoint URL for the root of the HTML documentation"
        )
    extra_dir: str = Field(
        default=".",
        description="Extra data root directory"
        )
    template_dir: str = Field(
        default=path.join(package.src_dir, "templates"),
        description="Directory containing templates"
        )
    userdoc_url: str = Field(
        default = doc_path.default + "/", #type: ignore
        description="Endpoint URL for the user's HTML documentation"
        )

    class Config:
        env_prefix = f"{package.name}_"
        extra = 'ignore'


ncpu = cpu_count()


class EngineSettings(BaseSettings):
    thread_count: int = Field(
        short='t',
        default = ncpu // 2 if ncpu is not None else 4,
        ge=1,
        le=1024,
        description="Number of engine threads"
        )

    class Config:
        env_prefix = f"{package.name}_"
        extra = 'ignore'


class AppSettings(BaseSettings):
    host: BaseSettings = HostSettings()
    server: BaseSettings = ServerSettings()
    engine: BaseSettings = EngineSettings()


