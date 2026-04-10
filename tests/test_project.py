from httpy.io import (
    save_project,
    load_project,
    make_project_path,
)
from httpy.core import set_basepath
from httpy.core.request_handler import HttpyRequestHandler

import pytest
from pathlib import Path

from httpy.core.project import HttpyProject


@pytest.fixture(autouse=True, scope="function")
def set_basepath_for_tests(tmp_path: Path):
    set_basepath(tmp_path)


@pytest.fixture
def default_project() -> HttpyProject:
    return HttpyProject(
        "Test Project",
        "A test project",
        HttpyRequestHandler(),
    )


@pytest.fixture
def saved_project_name(tmp_path: Path, default_project: HttpyProject) -> str:
    save_project(default_project)
    return default_project.name


def test_create_project():
    project = HttpyProject("Test Project", "A test project", HttpyRequestHandler())

    assert project.name == "Test Project"
    assert project.description == "A test project"


def test_save_project(
    tmp_path: Path,
    default_project: HttpyProject,
):
    save_project(default_project)

    project_file = make_project_path(default_project.name)
    assert project_file.exists()


def test_load_project(
    saved_project_name: str,
):
    assert make_project_path(saved_project_name).exists()

    loaded_project = load_project(saved_project_name)

    assert loaded_project.name == loaded_project.name
    assert loaded_project.description == loaded_project.description
    assert len(loaded_project.environments) == len(loaded_project.environments)
