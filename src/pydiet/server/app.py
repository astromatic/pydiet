import io
from typing import Literal
from fastapi import FastAPI, HTTPException, Path, Query, Request, responses, status
from pydantic import BaseModel

from .compute import make_image
from .. import package

filters = {
    'megacam': ('u', 'g', 'r', 'i', 'z'),
    'wircam': ('Y', 'J', 'H', 'K')
}

filter_set = filters['megacam'] + filters['wircam']

def create_app() -> FastAPI:

    app = FastAPI(
        title=package.title,
        description=package.description,
        version=package.version,
        contact={
            "name":  f"{package.contact_name} ({package.contact_affiliation})",
            "url":   package.url,
            "email": package.contact_email
        },
        license_info={
            "name": package.license_name,
            "url":  package.license_url
        }
    )

    @app.get("/etc/{instrument}", tags=["ETC results"])
    async def read_instrument(
            instrument: Literal['megacam', 'wircam'] = Path(
                title="Instrument ID",
                description="CFHT instrument ID"
            ),
            filter: Literal[filter_set] = Query(
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
            return responses.StreamingResponse(
                io.BytesIO(png.tobytes()),
                media_type="image/png"
            )
        else:
            return {
                "exptime": 10**(0.4*(maglim-26.0)) * 10.0 * snr**2
            }

    return app
