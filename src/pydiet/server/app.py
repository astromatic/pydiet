"""
Application module
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence
from io import BytesIO
from logging import getLogger
from os.path import abspath, exists, join
from typing import get_args, Literal, Tuple
from urllib.parse import urlencode

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Path,
    Query,
    Request,
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
from .compute import  etc_response, make_image

from .models import ETCQueryModel, ETCResponseModel, ETCValidationError


from .models.data import default_instrument, filters, instruments
from .models.types import InstrumentID


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
    async def validation_exception_handler(request: Request, exc: ETCValidationError):
        """
        Propagate value errors from custom validators.

        Returns
        -------
        response: byte stream
            [JSON response](https://fastapi.tiangolo.com/advanced/custom-response/#jsonresponse)
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


    @app.get("/etc/instruments", tags=["ETC instruments"])
    async def read_instruments():
        """
        Instrument list endpoint.

        Returns
        -------
        response: byte stream
            [JSON response](https://fastapi.tiangolo.com/advanced/custom-response/#jsonresponse)
            with the list of supported instruments
        """
        return JSONResponse(
            content=jsonable_encoder(instruments, exclude={'response'})
        )


    @app.get("/etc/{instrument}/{rtype}", tags=["ETC results"], response_class=HTMLResponse)
    async def etc_query(
            request: Request,
            instrument: str = Path(     
                title="Instrument ID",
                description="Instrument ID"
            ),
            rtype: Literal['data', 'image'] = Path(
                title="Response type",
                description="Type of response: image or data"
            ),
            query: ETCQueryModel = Depends()
        ):
        """
        Exposure type calculator endpoint.

        Returns
        -------
        response: byte stream
            [Streaming](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse>)
            or [JSON](https://fastapi.tiangolo.com/advanced/custom-response/#jsonresponse)
            response containing the exposure data.
        """
        r = etc_response(query)
        if rtype == 'image':
            png = make_image(r)
            return StreamingResponse(
                BytesIO(png.tobytes()),
                media_type="image/png"
            )
        else:
          return r.model_dump_json()
    # PyDIET UI ETC results endpoint
    @app.get("/ui/{instrument}/etc_results", tags=["UI"], response_class=HTMLResponse)
    async def etc_results(
            request: Request,
            instrument: str = Path(     
                title="Instrument ID",
                description="Instrument ID"
            ),
            r: ETCResponseModel = Depends()):
        """
        UI ETC results endpoint.
        """
        return templates.TemplateResponse(
            join(instrument, "etc_results.html"),
            {
                "request": request,
                "root_path": request.scope.get("root_path"),
                "package": package.title,
                "etime": r.etime,
                "instrument": instrument,
                "rstring": urlencode(r.model_dump())
            }
        )
    # PyDIET main UI component endpoint
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
    # PyDIET instrument-dependent UI component endpoint
    @app.get("/ui/{instrument}/{component}", tags=["UI"], response_class=HTMLResponse)
    async def component(request: Request, instrument: str, component: str):
        """
        UI instrument-dependent component endpoint.
        """
        return templates.TemplateResponse(
            join(instrument, component + ".html"),
            {
                "request": request,
                "root_path": request.scope.get("root_path"),
                "package": package.title
            }
        )

    # Default PyDIET client endpoint
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
                "package": package.title,
            }
        )

    return app
