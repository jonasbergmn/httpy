from httpy.core.template import (
    HttpyRequestTemplate,
)
from httpy.core.request import HttpyRequest
from httpy.core.response import HttpyResponse
from httpy.core.environment import HttpyEnvironment
from httpy.core.request_handler import HttpRequestHandlerProtocol


class HttpyProject:
    name: str
    description: str
    environments: list[HttpyEnvironment]
    templates: list[HttpyRequestTemplate]

    def __init__(
        self,
        name: str,
        description: str,
        request_handler: HttpRequestHandlerProtocol,
        environments: list[HttpyEnvironment] | None = None,
        templates: list[HttpyRequestTemplate] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.request_handler = request_handler
        self.templates = templates if templates else []
        self.environments = environments if environments else []

    def make_request(
        self,
        template: HttpyRequestTemplate,
        environment: HttpyEnvironment,
    ) -> HttpyRequest:
        url = template.url
        headers = {k: v for k, v in template.headers.items()}
        body = template.body

        for key, value in environment.configs.items():
            placeholder = f"{{{{{key}}}}}"
            url = url.replace(placeholder, value)
            headers = {k: v.replace(placeholder, value) for k, v in headers.items()}
            body = body.replace(placeholder, value)

        return HttpyRequest(
            method=template.method,
            url=url,
            headers=headers,
            parameters=template.parameters,
            body=body,
        )

    def execute_request(self, request: HttpyRequest) -> HttpyResponse:
        return self.request_handler.send_request(request)
