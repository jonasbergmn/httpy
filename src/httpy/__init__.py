import logging

from httpy.models import (
    Environment,
    Project,
    Request,
    RequestTemplate,
    Response,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="[ %(name)-20s ] [ %(levelname)-8s ] - %(message)s",
)

__all__ = [
    "Environment",
    "Project",
    "Request",
    "RequestTemplate",
    "Response",
]
