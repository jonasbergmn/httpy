from httpy.models import (
    HttpyRequestTemplate,
    make_template_path,
    load_template,
    save_template,
    set_basepath,
)
import pytest
from pathlib import Path


@pytest.fixture(autouse=True, scope="function")
def set_basepath_for_tests(tmp_path: Path):
    set_basepath(tmp_path)


@pytest.fixture
def default_template() -> HttpyRequestTemplate:
    return HttpyRequestTemplate(
        name="Test Template",
        method="GET",
        url="https://example.com/api",
        headers={"Authorization": "Bearer token"},
        parameters={"query": "test"},
        body="",
    )


@pytest.fixture
def saved_template_path(default_template: HttpyRequestTemplate) -> Path:
    project_name = "Test Project"
    template_path = make_template_path(project_name, default_template.name)
    save_template(project_name, default_template)
    return template_path


def test_create_template(default_template: HttpyRequestTemplate):
    assert default_template.name == "Test Template"
    assert default_template.method == "GET"
    assert default_template.url == "https://example.com/api"
    assert default_template.headers == {"Authorization": "Bearer token"}
    assert default_template.parameters == {"query": "test"}
    assert default_template.body == ""


def test_save_template(default_template: HttpyRequestTemplate):
    project_name = "Test Project"

    template_path = make_template_path(project_name, default_template.name)
    save_template(project_name, default_template)

    assert template_path.exists()


def test_load_template(saved_template_path: Path):
    assert saved_template_path.exists()

    project_name = "Test Project"
    template_name = "Test Template"
    loaded_template = load_template(project_name, template_name)

    assert loaded_template.name == "Test Template"
    assert loaded_template.method == "GET"
    assert loaded_template.url == "https://example.com/api"
    assert loaded_template.headers == {"Authorization": "Bearer token"}
    assert loaded_template.parameters == {"query": "test"}
    assert loaded_template.body == ""
