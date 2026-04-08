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
class Environment:
    name: str
    configs: dict[str, str]


@dataclass
class Response:
    status_code: int
    headers: dict[str, str]
    body: str


@dataclass
class Request:
    method: str
    url: str
    headers: dict[str, str]
    parameters: dict[str, str]
    body: str


@dataclass
class RequestTemplate:
    name: str
    method: str
    url: str
    headers: dict[str, str]
    parameters: dict[str, str]
    body: str


class Project:
    name: str
    description: str
    environments: list[Environment]
    templates: list[RequestTemplate]

    def __init__(
        self,
        name: str,
        description: str,
        environments: list[Environment] | None = None,
        templates: list[RequestTemplate] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.templates = templates if templates else []
        self.environments = environments if environments else []

    def make_request(
        self,
        template: RequestTemplate,
        environment: Environment,
    ) -> Request:
        url = template.url
        headers = {k: v for k, v in template.headers.items()}
        body = template.body

        for key, value in environment.configs.items():
            placeholder = f"{{{{{key}}}}}"
            url = url.replace(placeholder, value)
            headers = {k: v.replace(placeholder, value) for k, v in headers.items()}
            body = body.replace(placeholder, value)

        return Request(
            method=template.method,
            url=url,
            headers=headers,
            parameters=template.parameters,
            body=body,
        )

    def execute_request(self, request: Request) -> Response:
        return Response(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body='{"message": "This is a mock response"}',
        )


def clean_name(name: str) -> str:
    return name.lower().replace(" ", "_")


def make_project_path(project_name: str) -> Path:
    os.makedirs(_basepath / clean_name(project_name), exist_ok=True)
    return _basepath / clean_name(project_name) / "project.json"


def make_template_path(project_name: str, template_name: str) -> Path:
    os.makedirs(_basepath / clean_name(project_name) / "templates", exist_ok=True)
    return (
        _basepath
        / clean_name(project_name)
        / "templates"
        / f"{clean_name(template_name)}.json"
    )


def make_templates_path(project_name: str) -> Path:
    os.makedirs(_basepath / clean_name(project_name) / "templates", exist_ok=True)
    return _basepath / clean_name(project_name) / "templates"


def save_template(project_name: str, template: RequestTemplate) -> Path:
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


def load_template(project_name: str, template_name: str) -> RequestTemplate:
    template_json = make_template_path(project_name, template_name)
    with open(template_json, "r") as f:
        data = json.load(f)

    return RequestTemplate(
        name=data["name"],
        method=data["method"],
        url=data["url"],
        headers=data["headers"],
        parameters=data["parameters"],
        body=data["body"],
    )


def load_templates(project_name: str) -> list[RequestTemplate]:
    templates_dir = make_templates_path(project_name)

    templates: list[RequestTemplate] = []
    for template_file in templates_dir.glob("*.json"):
        template = load_template(project_name, template_file.stem)
        templates.append(template)

    return templates


def save_project(project: Project, include_templates: bool = False) -> Path:
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

    if include_templates:
        for template in project.templates:
            save_template(project.name, template)

    return project_path


def load_project(project_name: str, include_templates: bool = False) -> Project:
    project_json = make_project_path(project_name)
    with open(project_json, "r") as f:
        data = json.load(f)
    environments = [
        Environment(name=env["name"], configs=env["configs"])
        for env in data.get("environments", [])
    ]

    if include_templates:
        templates = load_templates(project_name)

        return Project(
            name=data["name"],
            description=data["description"],
            environments=environments,
            templates=templates,
        )

    return Project(
        name=data["name"],
        description=data["description"],
        environments=environments,
    )
