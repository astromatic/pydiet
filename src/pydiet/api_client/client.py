#! /usr/bin/python3
"""
Python client functions for harvesting results from the PyDIET ETC
"""
# Copyright (c) 2024 - 2026 CFHT/CNRS/CEA-AIM/OSUPS-UParisSaclay
# Licensed under the MIT licence

from typing import Optional

import httpx
from pydantic import ValidationError

from ..server.models.query import ETCQueryModel
from ..server.models.response import ETCResponseModel
from ..server.config import settings


class Client:
    """
    Class for the Python client API.

    Parameters
    ----------
    api_url: str, optional
        API root URL (defaults to "api_path" setting).

    Attributes
    ----------
    api_url: str
        Root URL used for ETC requests.

    Examples
    --------
    >>> from .client import Client
    >>> client = Client("https://etc.example/api")
    >>> client.api_url
    'https://etc.example/api'
    """
    def __init__(self, api_url: Optional[str]=None) -> None:
        self.api_url = f"http://{settings['host']}" \
            f":{settings['port']}{settings['api_path']}" if api_url is None \
            else api_url


    def query(
            self,
            query: ETCQueryModel,
            timeout: float=10.) -> ETCResponseModel:
        """
        Query the ETC API.

        Parameters
        ----------
        query: ETCQueryModel
            Validated ETC query. Its ``instrument`` field selects the endpoint;
            the remaining non-null fields are sent as query parameters.
        timeout: float, optional
            HTTP timeout in seconds.

        Returns
        -------
        response: ETCResponseModel
            Validated ETC response.

        Raises
        ------
        RuntimeError
            If the request fails, the server returns an error response, the
            response is not JSON, or its JSON does not match the response model.
        """
        headers: dict[str, str] = {"Accept": "application/json"}
        try:
            with httpx.Client(timeout=timeout, headers=headers) as client:
                response = client.get(
                    f"{self.api_url}/{query.instrument}",
                    params=query.model_dump(
                        exclude={"instrument"},
                        exclude_none=True,
                        mode="json"
                    )
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"HTTP error {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Transport error: {exc}") from exc
        except ValueError as exc:
            raise RuntimeError("Response was not valid JSON") from exc

        try:
            return ETCResponseModel.model_validate(payload)
        except ValidationError as exc:
            raise RuntimeError(f"Invalid response schema: {exc}") from exc

