from httpy.models import (
    Project,
    Environment,
    RequestTemplate,
    save_project,
    load_project,
)


if __name__ == "__main__":
    default_environment = Environment(
        name="Default",
        configs={
            "API_KEY": "1234567890abcdef",
            "BASE_URL": "https://api.example.com",
            "user_id": "42",
        },
    )

    template_one = RequestTemplate(
        name="Get User Info",
        method="GET",
        url="{{BASE_URL}}/users/{{user_id}}",
        headers={"Authorization": "Bearer {{API_KEY}}"},
        parameters={},
        body="",
    )

    template_two = RequestTemplate(
        name="Get User Info Details",
        method="GET",
        url="{{BASE_URL}}/users/{{user_id}}/details",
        headers={"Authorization": "Bearer {{API_KEY}}"},
        parameters={},
        body="",
    )

    project = Project(
        name="My API Project",
        description="A project for testing HTTP requests",
        environments=[default_environment],
        templates=[template_one, template_two],
    )

    project_path = save_project(project, include_templates=True)
    project = load_project(project.name, include_templates=True)

    request = project.make_request(template_one, default_environment)
...
