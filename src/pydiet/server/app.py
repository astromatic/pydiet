"""
Application module
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence
from io import BytesIO
from logging import getLogger
from os.path import abspath, exists, join
from typing import Annotated, get_args, Literal, Optional, Tuple
from urllib.parse import urlencode

from fastapi import (
    Body,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    Request,
    UploadFile,
    responses,
    status
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel, ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError

from .. import package
from .config import config_filename, settings
from .response import get_response

from .models import (
    ETCQueryModel,
    ETCResponseModel,
    ETCValidationError
)

from .data import winstruments



def create_app() -> FastAPI:
    """
    Create FASTAPI application
    """

    banner_template = settings["banner_template"]
    base_template = settings["base_template"]
    template_dir = abspath(settings["template_dir"])
    client_dir = abspath(settings["client_dir"])
    data_dir = abspath(settings["data_dir"])
    extra_dir = abspath(settings["extra_dir"])
    doc_dir = settings["doc_dir"]
    doc_path = settings["doc_path"]
    userdoc_url = settings["userdoc_url"]
    api_path = settings["api_path"]

    logger = getLogger("uvicorn.error")

    # Provide an endpoint for the user's manual (if it exists)
    if config_filename:
        logger.info(f"Configuration read from {config_filename}.")
    else:
        logger.warning(
            f"Configuration file not found: {config_filename}!"
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
    if exists(doc_dir):
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
        directory=join(package.src_dir, template_dir)
    )


    @app.exception_handler(ETCValidationError)
    async def handle_validation_exception(request: Request, exc: ETCValidationError):
        """
        Propagate value errors from custom validators.

        Returns
        -------
        response: byte stream
            `JSON response <https://fastapi.tiangolo.com/advanced/custom-response/#jsonresponse>`_
            containing the error diagnostic.
        """
        dico = exc.args[0]
        raise RequestValidationError(
            errors=(
                ValidationError.from_exception_data(
                    "ValueError",
                    [
                        InitErrorDetails(
                            type=dico["type"],
                            loc=dico["loc"],
                            input=dico["input"],
                            ctx={"expected": dico["expected"]}
                        )
                    ]
                )
            ).errors()
        )


    @app.get(api_path + "/health", tags=["Web API"])
    async def get_health():
        return {"ok": True}


    @app.get(api_path + "/instruments", tags=["Web API"])
    async def get_api_instruments():
        """
        Endpoint for instrument list.

        Returns
        -------
        response: byte stream
            `JSON response <https://fastapi.tiangolo.com/advanced/custom-response/#jsonresponse>`_
            with the list of supported instruments
        """
        return JSONResponse(
            content=jsonable_encoder(winstruments)
        )


    # PyDIET web API endpoint with GET query string
    @app.get(api_path + "/{instrument}", tags=["Web API"])
    async def get_api_query(
            request: Request,
            instrument: str = Path(     
                title="Instrument ID",
                description="Instrument ID"
            ),
            query: ETCQueryModel = Depends()):
        """
        GET Endpoint for exposure type calculator JSON output.

        Returns
        -------
        response: byte stream
            `JSON response <https://fastapi.tiangolo.com/advanced/custom-response/#jsonresponse>`_
            containing the computed ETC data.
        """
        return get_response(query).model_dump(exclude_none=True)


    # PyDIET web API endpoint with POST query (for uploading filter curves)
    @app.post(api_path + "/{instrument}", tags=["Web API"])
    async def post_api_query(
            request: Request,
            instrument: str = Path(     
                title="Instrument ID",
                description="Instrument ID"
            ),
            filter_upload: UploadFile | None = File(None)):
        """
        POST Endpoint for exposure type calculator JSON output, with optional
        filter curve upload.

        Returns
        -------
        response: byte stream
            `JSON response <https://fastapi.tiangolo.com/advanced/custom-response/#jsonresponse>`_
            containing the computed ETC data.
        """
        form = await request.form()
        # Remove the filter upload field
        data = dict(form)
        data.pop("filter_upload", None)
        query = ETCQueryModel.model_validate(data)
        return get_response(
                    query,
                    filter=None if filter_upload is None else filter_upload.file
        ).model_dump(exclude_none=True)


    # PyDIET UI component endpoint with GET query string
    @app.get("/ui/{instrument}/{component}/query", tags=["UI"], response_class=HTMLResponse)
    async def get_ui_component_query(
            request: Request,
            instrument: str = Path(     
                title="Instrument ID",
                description="Instrument ID"
            ),
            component: str = Path(
                title="Component name",
                description="Name of the UI component"
            ),
            query: ETCQueryModel = Depends()):
        """
        Endpoint for UI component with ETC query string.
        Use "common" as instrument for components shared by all instruments.

        Returns
        -------
        response: byte stream
            `HTML response <https://fastapi.tiangolo.com/advanced/custom-response/#htmlresponse>`_
            with UI component.
        """
        return templates.TemplateResponse(
            request = request,
            name = join(instrument, component + ".html"),
            context = {
                "root_path": request.scope.get("root_path"),
                "package": package,
                "instrument": instrument,
                "r": get_response(query, ui=True)
            }
        )

    # PyDIET UI component endpoint with POST query (for uploading filter curves)
    @app.post("/ui/{instrument}/{component}/query", tags=["UI"], response_class=HTMLResponse)
    async def post_ui_component_query(
            request: Request,
            instrument: str = Path(     
                title="Instrument ID",
                description="Instrument ID"
            ),
            component: str = Path(
                title="Component name",
                description="Name of the UI component"
            ),
            filter_upload: UploadFile | None = File(None)):
        """
        Endpoint for UI component with ETC query string.
        Use "common" as instrument for components shared by all instruments.

        Returns
        -------
        response: byte stream
            `HTML response <https://fastapi.tiangolo.com/advanced/custom-response/#htmlresponse>`_
            with UI component.
        """
        form = await request.form()
        # Remove the filter upload field
        data = dict(form)
        data.pop("filter_upload", None)
        query = ETCQueryModel.model_validate(data)
        return templates.TemplateResponse(
            request = request,
            name = join(instrument, component + ".html"),
            context = {
                "root_path": request.scope.get("root_path"),
                "package": package,
                "instrument": instrument,
                "r": get_response(
                    query,
                    filter=None if filter_upload is None else filter_upload.file,
                    ui=True
                )
            }
        )


    # PyDIET UI component endpoint without a query string
    @app.get("/ui/{instrument}/{component}", tags=["UI"], response_class=HTMLResponse)
    async def get_ui_component(
            request: Request,
            instrument: str = Path(     
                title="Instrument ID",
                description="Instrument ID"
            ),
            component: str = Path(
                title="Component name",
                description="Name of the UI component"
            )):
        """
        Endpoint for UI component without an ETC query string.
        Use "common" as instrument for components shared by all instruments.

        Returns
        -------
        response: byte stream
            `HTML response <https://fastapi.tiangolo.com/advanced/custom-response/#htmlresponse>`_
            with UI component.
        """
        return templates.TemplateResponse(
            request = request,
            name = join(instrument, component + ".html"),
            context = {
                "root_path": request.scope.get("root_path"),
                "package": package,
                "instrument": instrument
            }
        )


    # Default PyDIET client endpoint
    @app.get("/", tags=["UI"], response_class=HTMLResponse)
    async def get_ui(request: Request):
        """
        Main web user interface.
        """
        return templates.TemplateResponse(
            request = request,
            name = base_template,
            context = {
                "root_path": request.scope.get("root_path"),
                "doc_url": userdoc_url,
                "package": package
            }
        )

    return app
