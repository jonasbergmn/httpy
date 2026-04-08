from dataclasses import dataclass
import json
from pathlib import Path
import os


_basepath = Path("projects")


def set_basepath(path: str | Path) -> None:
    global _basepath
    match path:
        case str():
            _basepath = Path(path)
        case Path():
            _basepath = path


@dataclass
class HttpyEnvironment:
    name: str
    configs: dict[str, str]


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


class HttpyProject:
    name: str
    description: str
    environments: list[HttpyEnvironment]
    templates: list[HttpyRequestTemplate]

    def __init__(
        self,
        name: str,
        description: str,
        environments: list[HttpyEnvironment] | None = None,
        templates: list[HttpyRequestTemplate] | None = None,
    ) -> None:
        self.name = name
        self.description = description
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
        return HttpyResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body='{"message": "This is a mock response"}',
        )


def create_project(name: str, description: str) -> HttpyProject:
    environment = HttpyEnvironment(name="Default", configs={})
    project = HttpyProject(
        name=name, description=description, environments=[environment]
    )
    return project


def clean_name(name: str) -> str:
    return name.lower().replace(" ", "_")


def make_project_path(project_name: str) -> Path:
    os.makedirs(_basepath / clean_name(project_name), exist_ok=True)
    return _basepath / clean_name(project_name) / "project.json"


def save_project(project: HttpyProject) -> Path:
    project_path = make_project_path(project.name)
    project_json = {
        "name": project.name,
        "description": project.description,
        "environments": [
            {"name": env.name, "configs": env.configs} for env in project.environments
        ],
    }
    with open(project_path, "w") as f:
        json.dump(project_json, f, indent=4)

    return project_path


def load_project(project_name: str) -> HttpyProject:
    project_json = make_project_path(project_name)
    with open(project_json, "r") as f:
        data = json.load(f)
    environments = [
        HttpyEnvironment(name=env["name"], configs=env["configs"])
        for env in data.get("environments", [])
    ]

    return HttpyProject(
        name=data["name"],
        description=data["description"],
        environments=environments,
    )


def make_template_path(project_name: str, template_name: str) -> Path:
    os.makedirs(_basepath / clean_name(project_name) / "templates", exist_ok=True)
    return (
        _basepath
        / clean_name(project_name)
        / "templates"
        / f"{clean_name(template_name)}.json"
    )


def save_template(project_name: str, template: HttpyRequestTemplate) -> Path:
    template_path = make_template_path(project_name, template.name)
    template_json = json.dumps(
        {
            "name": template.name,
            "method": template.method,
            "url": template.url,
            "headers": template.headers,
            "parameters": template.parameters,
            "body": template.body,
        },
        indent=4,
    )
    with open(template_path, "w") as f:
        f.write(template_json)

    return template_path


def load_template(project_name: str, template_name: str) -> HttpyRequestTemplate:
    template_json = make_template_path(project_name, template_name)
    with open(template_json, "r") as f:
        data = json.load(f)

    return HttpyRequestTemplate(
        name=data["name"],
        method=data["method"],
        url=data["url"],
        headers=data["headers"],
        parameters=data["parameters"],
        body=data["body"],
    )
