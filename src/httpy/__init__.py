import logging

from httpy.core.template import (
    HttpyRequestTemplate,
)
from httpy.core.request import HttpyRequest
from httpy.core.response import HttpyResponse
from httpy.core.environment import HttpyEnvironment
from httpy.core.project import HttpyProject

logging.basicConfig(
    level=logging.INFO,
    format="[ %(name)-20s ] [ %(levelname)-8s ] - %(message)s",
)

__all__ = [
    "HttpyEnvironment",
    "HttpyProject",
    "HttpyRequest",
    "HttpyRequestTemplate",
    "HttpyResponse",
]
