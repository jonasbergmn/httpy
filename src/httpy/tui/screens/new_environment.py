from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from httpy.core.environment import HttpyEnvironment
from httpy.core.project import HttpyProject
from httpy.io import save_project
from httpy.tui.widgets.environment_editor import ConfigRow


class NewEnvironmentScreen(ModalScreen[HttpyEnvironment | None]):
    CSS = """
    NewEnvironmentScreen {
        align: center middle;
    }
    #new-env-dialog {
        width: 70;
        height: auto;
        max-height: 30;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    """

    def __init__(self, project: HttpyProject) -> None:
        super().__init__()
        self._project = project

    def compose(self) -> ComposeResult:
        with Vertical(id="new-env-dialog"):
            yield Static("New Environment", classes="panel-title")
            yield Label("Name")
            yield Input(placeholder="Environment name", id="new-env-name")
            yield Static("Configuration Variables", classes="section-title")
            yield Vertical(id="new-env-config-rows")
            yield Button("+ Add Variable", variant="default", id="btn-add-env-config")
            with Horizontal(classes="button-row"):
                yield Button("Create", variant="primary", id="btn-create-env")
                yield Button("Cancel", variant="default", id="btn-cancel-env")

    def on_mount(self) -> None:
        container = self.query_one("#new-env-config-rows", Vertical)
        container.mount(ConfigRow())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-add-env-config":
            container = self.query_one("#new-env-config-rows", Vertical)
            container.mount(ConfigRow())
        elif event.button.id == "btn-create-env":
            name = self.query_one("#new-env-name", Input).value
            if not name:
                self.notify("Environment name is required", severity="warning")
                return

            configs: dict[str, str] = {}
            for row in self.query(ConfigRow):
                key, value = row.get_pair()
                if key:
                    configs[key] = value

            environment = HttpyEnvironment(name=name, configs=configs)
            self._project.environments.append(environment)
            save_project(self._project, include_templates=False)
            self.dismiss(environment)
        elif event.button.id == "btn-cancel-env":
            self.dismiss(None)
