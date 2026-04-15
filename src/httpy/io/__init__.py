import json
from datetime import datetime, timezone
from pathlib import Path
import os

from httpy.core import (
    get_basepath,
)
from httpy.core.template import HttpyRequestTemplate
from httpy.core.environment import HttpyEnvironment
from httpy.core.project import HttpyProject
from httpy.core.response import HttpyResponse
from httpy.core.request_handler import HttpRequestHandlerProtocol, HttpyRequestHandler


def clean_name(name: str) -> str:
    return name.lower().replace(" ", "_")


# -- path helpers --


def make_project_path(project_name: str) -> Path:
    project_dir = get_basepath() / clean_name(project_name)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir / "project.json"


def make_template_dir(project_name: str, template_id: str) -> Path:
    template_dir = get_basepath() / clean_name(project_name) / clean_name(template_id)
    os.makedirs(template_dir, exist_ok=True)
    return template_dir


def make_template_path(project_name: str, template_id: str) -> Path:
    return make_template_dir(project_name, template_id) / "template.json"


def make_responses_dir(project_name: str, template_id: str) -> Path:
    responses_dir = make_template_dir(project_name, template_id) / "responses"
    os.makedirs(responses_dir, exist_ok=True)
    return responses_dir


# -- template persistence --


def save_template(project_name: str, template: HttpyRequestTemplate) -> Path:
    template_path = make_template_path(project_name, template.id)
    template_json = json.dumps(
        {
            "name": template.name,
            "method": template.method,
            "url": template.url,
            "headers": template.headers,
            "parameters": template.parameters,
            "body": template.body,
            "id": template.id,
        },
        indent=4,
    )
    with open(template_path, "w") as f:
        f.write(template_json)

    return template_path


def load_template(project_name: str, template_id: str) -> HttpyRequestTemplate:
    template_json = make_template_path(project_name, template_id)
    with open(template_json, "r") as f:
        data = json.load(f)

    return HttpyRequestTemplate(
        name=data["name"],
        method=data["method"],
        url=data["url"],
        headers=data["headers"],
        parameters=data["parameters"],
        body=data["body"],
        id=data["id"],
    )


def load_templates(project_name: str) -> list[HttpyRequestTemplate]:
    project_dir = get_basepath() / clean_name(project_name)
    if not project_dir.exists():
        return []

    templates: list[HttpyRequestTemplate] = []
    for child in sorted(project_dir.iterdir()):
        template_file = child / "template.json"
        if child.is_dir() and template_file.exists():
            with open(template_file, "r") as f:
                data = json.load(f)
            templates.append(
                HttpyRequestTemplate(
                    name=data["name"],
                    method=data["method"],
                    url=data["url"],
                    headers=data["headers"],
                    parameters=data["parameters"],
                    body=data["body"],
                    id=data["id"],
                )
            )

    return templates


# -- response persistence --


def save_response(project_name: str, template_id: str, response: HttpyResponse) -> Path:
    responses_dir = make_responses_dir(project_name, template_id)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    response_path = responses_dir / f"{timestamp}.json"
    response_json = json.dumps(
        {
            "status_code": response.status_code,
            "headers": response.headers,
            "body": response.body,
        },
        indent=4,
    )
    with open(response_path, "w") as f:
        f.write(response_json)

    return response_path


def load_responses(project_name: str, template_id: str) -> list[HttpyResponse]:
    responses_dir = make_responses_dir(project_name, template_id)
    responses: list[HttpyResponse] = []
    for response_file in sorted(responses_dir.glob("*.json")):
        with open(response_file, "r") as f:
            data = json.load(f)
        responses.append(
            HttpyResponse(
                status_code=data["status_code"],
                headers=data["headers"],
                body=data["body"],
            )
        )
    return responses


# -- project persistence --


def save_project(project: HttpyProject, include_templates: bool = False) -> Path:
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


def load_project(
    project_name: str,
    include_templates: bool = False,
    request_handler: HttpRequestHandlerProtocol | None = None,
) -> HttpyProject:
    project_json = make_project_path(project_name)
    with open(project_json, "r") as f:
        data = json.load(f)
    environments = [
        HttpyEnvironment(name=env["name"], configs=env["configs"])
        for env in data.get("environments", [])
    ]

    if include_templates:
        templates = load_templates(project_name)

        return HttpyProject(
            name=data["name"],
            description=data["description"],
            request_handler=request_handler or HttpyRequestHandler(),
            environments=environments,
            templates=templates,
        )

    return HttpyProject(
        name=data["name"],
        description=data["description"],
        request_handler=request_handler or HttpyRequestHandler(),
        environments=environments,
    )


def list_projects() -> list[str]:
    basepath = get_basepath()
    if not basepath.exists():
        return []
    return [
        d.name
        for d in sorted(basepath.iterdir())
        if d.is_dir() and (d / "project.json").exists()
    ]
