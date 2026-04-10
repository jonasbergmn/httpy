from httpy.core.request import HttpyRequest
from httpy.core.response import HttpyResponse
from httpy.utils import make_logger

from typing import Protocol

import requests


class HttpRequestHandlerProtocol(Protocol):
    def send_request(self, request: HttpyRequest) -> HttpyResponse: ...


class HttpyRequestHandler:
    def __init__(self) -> None:
        self._logger = make_logger(
            name="HttpyRequestHandler",
            fmt="[ %(name)-20s ] [ %(levelname)-8s ] - %(message)s",
        )

    def send_request(self, request: HttpyRequest) -> HttpyResponse:
        try:
            response = requests.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                params=request.parameters,
                data=request.body,
            )
            return HttpyResponse(
                status_code=response.status_code,
                headers={k: v for k, v in response.headers.items()},
                body=response.text,
            )
        except requests.RequestException as e:
            self._logger.error(f"Request failed: {e}", exc_info=True)
            raise e
