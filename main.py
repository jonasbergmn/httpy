import json

from httpy import (
    HttpyEnvironment,
    HttpyProject,
    HttpyRequestTemplate,
    HttpyResponse,
    render_response_body,
)

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
