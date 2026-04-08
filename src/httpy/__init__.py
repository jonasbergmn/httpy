import logging

from httpy.models import (
    HttpyEnvironment,
    HttpyProject,
    HttpyRequest,
    HttpyRequestTemplate,
    HttpyResponse,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="[ %(name)-20s ] [ %(levelname)-8s ] - %(message)s",
)

__all__ = [
    "HttpyEnvironment",
    "HttpyProject",
    "HttpyRequest",
    "HttpyRequestTemplate",
    "HttpyResponse",
]
