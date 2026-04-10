from httpy.core.template import (
    HttpyRequestTemplate,
)

from httpy.core.environment import HttpyEnvironment
from httpy.io import save_project, load_project
from httpy.core.project import HttpyProject
from httpy.core.request_handler import HttpyRequestHandler

if __name__ == "__main__":
    default_environment = HttpyEnvironment(
        name="Default",
        configs={
            "API_KEY": "1234567890abcdef",
            "BASE_URL": "https://jsonplaceholder.typicode.com",
        },
    )

    template_one = HttpyRequestTemplate(
        name="Get Todo One",
        method="GET",
        url="{{BASE_URL}}/todos/1",
        headers={},
        parameters={},
        body="",
    )

    template_two = HttpyRequestTemplate(
        name="Get Todo Two",
        method="GET",
        url="{{BASE_URL}}/todos/2",
        headers={},
        parameters={},
        body="",
    )

    project = HttpyProject(
        name="My API Project",
        description="A project for testing HTTP requests",
        request_handler=HttpyRequestHandler(),
        environments=[default_environment],
        templates=[template_one, template_two],
    )

    project_path = save_project(project, include_templates=True)
    project = load_project(project.name, include_templates=True)

    request = project.make_request(template_one, default_environment)
    response = project.execute_request(request)

    print(response.render_json())

    request = project.make_request(template_two, default_environment)
    response = project.execute_request(request)

    print(response.render_json())
