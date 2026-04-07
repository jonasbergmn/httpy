from dataclasses import dataclass
import json
import logging
from typing import Callable

logging.basicConfig(
    level=logging.DEBUG,
    format="[ %(name)-20s ] [ %(levelname)-8s ] - %(message)s",
)

logging.info("Starting HTTPy application")


def _make_logger(name: str, fmt: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter(fmt))
    logger.addHandler(h)
    return logger


request_logger = _make_logger(
    "httpy.request",
    "[ %(name)-20s ] [ %(levelname)-8s ] - %(message)s - %(request)s",
)

response_logger = _make_logger(
    "httpy.response",
    "[ %(name)-20s ] [ %(levelname)-8s ] - %(message)s - %(status_code)d - %(body)s",
)


@dataclass
class HttpyResponse:
    status_code: int
    headers: dict[str, str]
    body: str


@dataclass
class HttpyRequest:
    method: str
    url: str
    headers: dict[str, str]
    parameters: dict[str, str]
    body: str


@dataclass
class HttpyRequestTemplate:
    name: str
    method: str
    url: str
    headers: dict[str, str]
    parameters: dict[str, str]
    body: str


@dataclass
class HttpyEnvironment:
    name: str
    configs: dict[str, str]


@dataclass
class HttpyProject:
    name: str
    description: str
    environments: list[HttpyEnvironment]
    requests: list[HttpyRequestTemplate]


def replace_placeholders(
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


def render_response_body(
    response: HttpyResponse, render_func: Callable[[HttpyResponse], str]
) -> str:
    rendered_response = render_func(response)
    response_logger.info(
        "Rendering response body.",
        extra={"body": rendered_response, "status_code": response.status_code},
    )
    return rendered_response


def execute_request(
    template: HttpyRequestTemplate,
    environment: HttpyEnvironment,
) -> None:
    request = replace_placeholders(template, environment)
    request_logger.info(
        f"Executing {request.method} request to {request.url}",
        extra={"request": request},
    )


def load_project_from_json(file_path: str) -> "HttpyProject":
    with open(file_path, "r") as f:
        data = json.load(f)
    return HttpyProject(
        name=data["name"],
        description=data["description"],
        environments=[
            HttpyEnvironment(name=env["name"], configs=env["configs"])
            for env in data["environments"]
        ],
        requests=[
            HttpyRequestTemplate(
                name=req["name"],
                method=req["method"],
                url=req["url"],
                headers=req["headers"],
                body=req["body"],
                parameters=req["parameters"],
            )
            for req in data["request_templates"]
        ],
    )


def write_project_to_json(project: HttpyProject, file_path: str) -> None:
    with open(file_path, "w") as f:
        json.dump(project, f, default=lambda x: x.__dict__, indent=4)


if __name__ == "__main__":
    project = HttpyProject(
        name="My HTTPy Project",
        description="A sample HTTPy project",
        environments=[
            HttpyEnvironment(
                name="Development",
                configs={"base_url": "http://localhost:8000", "token": "dev-token-123"},
            )
        ],
        requests=[
            HttpyRequestTemplate(
                name="Get Users",
                method="GET",
                url="{{base_url}}/users",
                headers={"Authorization": "Bearer {{token}}"},
                body="",
                parameters={},
            )
        ],
    )

    response = HttpyResponse(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body='{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}',
    )

    rendered_body = render_response_body(
        response, lambda x: json.dumps(json.loads(x.body), indent=4)
    )
