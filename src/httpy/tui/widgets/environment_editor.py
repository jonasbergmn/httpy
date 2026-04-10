from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static

from httpy.core.environment import HttpyEnvironment
from httpy.core.project import HttpyProject
from httpy.io import save_project


class ConfigRow(Widget):
    DEFAULT_CSS = """
    ConfigRow {
        height: auto;
    }
    """

    def __init__(self, key: str = "", value: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._key = key
        self._value = value

    def compose(self) -> ComposeResult:
        with Horizontal(classes="config-row"):
            yield Input(value=self._key, placeholder="Key", classes="config-key")
            yield Input(value=self._value, placeholder="Value", classes="config-value")
            yield Button("✕", variant="error", classes="config-remove-btn")

    def get_pair(self) -> tuple[str, str]:
        key = self.query("Input.config-key").first(Input).value
        value = self.query("Input.config-value").first(Input).value
        return key, value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if "config-remove-btn" in event.button.classes:
            self.remove()


class EnvironmentEditor(Widget):
    class EnvironmentSaved(Message):
        pass

    _environment: HttpyEnvironment | None = None
    _project: HttpyProject | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="env-form"):
            yield Static("Environment Editor", classes="panel-title")
            yield Label("Name")
            yield Input(placeholder="Environment name", id="env-name")
            yield Static("Configuration Variables", classes="section-title")
            yield Vertical(id="config-rows")
            yield Button("+ Add Variable", variant="default", id="btn-add-config")
            yield Button("Save Environment", variant="primary", id="btn-save-env")

    def load_environment(
        self, environment: HttpyEnvironment, project: HttpyProject
    ) -> None:
        self._environment = environment
        self._project = project

        self.query_one("#env-name", Input).value = environment.name

        container = self.query_one("#config-rows", Vertical)
        container.remove_children()
        for key, value in environment.configs.items():
            container.mount(ConfigRow(key=key, value=value))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-add-config":
            container = self.query_one("#config-rows", Vertical)
            container.mount(ConfigRow())
        elif event.button.id == "btn-save-env":
            self._save_environment()

    def _save_environment(self) -> None:
        if self._project is None:
            self.notify("No project selected", severity="warning")
            return

        name = self.query_one("#env-name", Input).value
        if not name:
            self.notify("Environment name is required", severity="warning")
            return

        configs: dict[str, str] = {}
        for row in self.query(ConfigRow):
            key, value = row.get_pair()
            if key:
                configs[key] = value

        new_env = HttpyEnvironment(name=name, configs=configs)

        found = False
        for i, env in enumerate(self._project.environments):
            if self._environment and env.name == self._environment.name:
                self._project.environments[i] = new_env
                found = True
                break

        if not found:
            self._project.environments.append(new_env)

        self._environment = new_env
        save_project(self._project, include_templates=False)
        self.notify(f"Environment '{name}' saved")
        self.post_message(self.EnvironmentSaved())
