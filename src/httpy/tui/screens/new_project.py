from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from httpy.core.project import HttpyProject
from httpy.core.request_handler import HttpyRequestHandler
from httpy.io import save_project


class NewProjectScreen(ModalScreen[HttpyProject | None]):
    CSS = """
    NewProjectScreen {
        align: center middle;
    }
    #new-project-dialog {
        width: 60;
        height: auto;
        max-height: 20;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="new-project-dialog"):
            yield Static("New Project", classes="panel-title")
            yield Label("Project Name")
            yield Input(placeholder="My Project", id="new-project-name")
            yield Label("Description")
            yield Input(placeholder="Project description", id="new-project-desc")
            yield Button("Create", variant="primary", id="btn-create-project")
            yield Button("Cancel", variant="default", id="btn-cancel-project")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-create-project":
            name = self.query_one("#new-project-name", Input).value
            desc = self.query_one("#new-project-desc", Input).value
            if not name:
                self.notify("Project name is required", severity="warning")
                return
            project = HttpyProject(
                name=name,
                description=desc,
                request_handler=HttpyRequestHandler(),
            )
            save_project(project)
            self.dismiss(project)
        elif event.button.id == "btn-cancel-project":
            self.dismiss(None)
