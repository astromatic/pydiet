"""
Application module
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence
from io import BytesIO
from logging import getLogger
from os import path
from typing import get_args, Literal, Tuple

from fastapi import (
    FastAPI,
    HTTPException,
    Path,
    Query,
    Request,
    responses,
    status
)
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

from .. import package
from . import config
from .compute import make_image

MEGACAM_FILTER = Literal['u', 'g', 'r', 'i', 'z']
WIRCAM_FILTER = Literal['Y', 'J', 'H', 'K']
FILTER = Literal[MEGACAM_FILTER, WIRCAM_FILTER]

filters = {
    'megacam': get_args(MEGACAM_FILTER),
    'wircam': get_args(WIRCAM_FILTER)
}

filter_set = filters['megacam'] + filters['wircam']

def create_app() -> FastAPI:
    """
    Create FASTAPI application
    """

    banner_template = config.settings["banner_template"]
    base_template = config.settings["base_template"]
    template_dir = path.abspath(config.settings["template_dir"])
    client_dir = path.abspath(config.settings["client_dir"])
    data_dir = path.abspath(config.settings["data_dir"])
    extra_dir = path.abspath(config.settings["extra_dir"])
    doc_dir = config.settings["doc_dir"]
    doc_path = config.settings["doc_path"]
    userdoc_url = config.settings["userdoc_url"]
    api_path = config.settings["api_path"]

    logger = getLogger("uvicorn.error")

    # Provide an endpoint for the user's manual (if it exists)
    if config.config_filename:
        logger.info(f"Configuration read from {config.config_filename}.")
    else:
        logger.warning(
            f"Configuration file not found: {config.config_filename}!"
        )

    app = FastAPI(
        title=package.title,
        description=package.description,
        version=package.version,
        contact = {
            "name":  f"{package.contact['name']} ({package.contact['affiliation']})",
            "url":   package.url,
            "email": package.contact['email']
        },
        license_info={
            "name": package.license_name,
            "url":  package.license_url
        }
    )

    """
    origins = [
        "http://halau.cfht.hawaii.edu",
        "https://halau.cfht.hawaii.edu",
        "http://halau",
        "https://halau"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    """

    # Provide a direct endpoint for static files (such as js and css)
    app.mount(
        "/client",
        StaticFiles(directory=client_dir),
        name="client"
    )

    # Provide a direct endpoint for extra static data files (such as json files)
    app.mount(
        "/extra",
        StaticFiles(directory=extra_dir),
        name="extra"
    )

    # Provide an endpoint for the user's manual (if it exists)
    if path.exists(doc_dir):
        logger.info(f"Default documentation found at {doc_dir}.")
        app.mount(
            doc_path,
            StaticFiles(directory=doc_dir),
            name="manual"
        )
    else:
        logger.warning(f"Default documentation not found in {doc_dir}!")
        logger.warning("Has the HTML documentation been compiled ?")
        logger.warning("De-activating documentation URL in built-in web client.")
        userdoc_url = ""

    # Instantiate templates
    templates = Jinja2Templates(
        directory=path.join(package.src_dir, template_dir)
    )

    @app.get("/etc/{instrument}", tags=["ETC results"])
    async def read_instrument(
            instrument: Literal['megacam', 'wircam'] = Path(
                title="Instrument ID",
                description="CFHT instrument ID"
            ),
            filter: FILTER = Query(
                None,
                title="Filter",
                description="Name of the instrument filter",
            ),
            maglim: float = Query(
                None,
                title="Magnitude limit",
                description="AB magnitude limit at the given SNR or exposure time",
                ge=-99.0,
                le=99.0
            ),
            snr: float = Query(
                5.0,
                title="SNR",
                description="Signal-to-Noise Ratio",
                ge=0.0
            ),
            type: Literal['info', 'image'] = Query(
                'info',
                title="Response type",
                description="Response type: information (JSON) or image (PNG)"
            )):
        """
        Exposure type calculator endpoint.

        Returns
        -------
        response: byte stream
            [Streaming response](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse>)
            containing the exposure data.
        """
        if not filter in filters[instrument]:
            raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{filter} filter not available for {instrument}")
        # Return a dummy exposure time
        if type == 'image':
            png = make_image(instrument, filter, snr)
            return StreamingResponse(
                BytesIO(png.tobytes()),
                media_type="image/png"
            )
        else:
            return {
                "exptime": 10**(0.4*(maglim-26.0)) * 10.0 * snr**2
            }

    # PyDIET UI component endpoint
    @app.get("/ui/{component}", tags=["UI"], response_class=HTMLResponse)
    async def component(request: Request, component: str):
        """
        UI component endpoint.
        """
        return templates.TemplateResponse(
            component + ".html",
            {
                "request": request,
                "root_path": request.scope.get("root_path"),
                "package": package.title
            }
        )

    # PyDIET client endpoint
    @app.get("/", tags=["UI"], response_class=HTMLResponse)
    async def pydiet(request: Request):
        """
        Main web user interface.
        """
        return templates.TemplateResponse(
            base_template,
            {
                "request": request,
                "root_path": request.scope.get("root_path"),
                "api_path": api_path,
                "doc_url": userdoc_url,
                "package": package.title
            }
        )

    return app
