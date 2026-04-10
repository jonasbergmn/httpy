import json
from pathlib import Path
import os

from httpy.core import (
    get_basepath,
)
from httpy.core.template import HttpyRequestTemplate
from httpy.core.environment import HttpyEnvironment
from httpy.core.project import HttpyProject
from httpy.core.request_handler import HttpRequestHandlerProtocol, HttpyRequestHandler


def clean_name(name: str) -> str:
    return name.lower().replace(" ", "_")


def make_project_path(project_name: str) -> Path:
    os.makedirs(get_basepath() / clean_name(project_name), exist_ok=True)
    return get_basepath() / clean_name(project_name) / "project.json"


def make_template_path(project_name: str, template_name: str) -> Path:
    os.makedirs(get_basepath() / clean_name(project_name) / "templates", exist_ok=True)
    return (
        get_basepath()
        / clean_name(project_name)
        / "templates"
        / f"{clean_name(template_name)}.json"
    )


def make_templates_path(project_name: str) -> Path:
    os.makedirs(get_basepath() / clean_name(project_name) / "templates", exist_ok=True)
    return get_basepath() / clean_name(project_name) / "templates"


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


def load_templates(project_name: str) -> list[HttpyRequestTemplate]:
    templates_dir = make_templates_path(project_name)

    templates: list[HttpyRequestTemplate] = []
    for template_file in templates_dir.glob("*.json"):
        template = load_template(project_name, template_file.stem)
        templates.append(template)

    return templates


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
