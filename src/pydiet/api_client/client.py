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
    def __init__(self, api_url: Optional[str]=None) -> None:
        self.api_url = f"http://{settings['host']}" \
            f":{settings['port']}{settings['api_path']}" if api_url is None \
            else api_url


    def query(
            self,
            query: ETCQueryModel,
            timeout: float=10.) -> ETCResponseModel:
        headers: dict[str, str] = {"Accept": "application/json"}
        print(f"{self.api_url}/{query.instrument}")
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


