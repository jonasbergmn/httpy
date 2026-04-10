from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static, TextArea

from httpy.core.project import HttpyProject
from httpy.core.template import HttpyRequestTemplate
from httpy.io import save_template


HTTP_METHODS = [
    ("GET", "GET"),
    ("POST", "POST"),
    ("PUT", "PUT"),
    ("PATCH", "PATCH"),
    ("DELETE", "DELETE"),
    ("HEAD", "HEAD"),
    ("OPTIONS", "OPTIONS"),
]


class NewTemplateScreen(ModalScreen[HttpyRequestTemplate | None]):
    CSS = """
    NewTemplateScreen {
        align: center middle;
    }
    #new-template-dialog {
        width: 80;
        height: auto;
        max-height: 40;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    """

    def __init__(self, project: HttpyProject) -> None:
        super().__init__()
        self._project = project

    def compose(self) -> ComposeResult:
        with Vertical(id="new-template-dialog"):
            yield Static("New Request Template", classes="panel-title")
            yield Label("Name")
            yield Input(placeholder="Request name", id="new-tmpl-name")
            yield Label("Method")
            yield Select(HTTP_METHODS, value="GET", id="new-tmpl-method")
            yield Label("URL")
            yield Input(
                placeholder="https://api.example.com/endpoint",
                id="new-tmpl-url",
            )
            yield Label("Headers (one per line: Key: Value)")
            yield TextArea(id="new-tmpl-headers")
            yield Label("Parameters (one per line: key=value)")
            yield TextArea(id="new-tmpl-params")
            yield Label("Body")
            yield TextArea(id="new-tmpl-body")
            with Horizontal(classes="button-row"):
                yield Button(
                    "Create", variant="primary", id="btn-create-template"
                )
                yield Button(
                    "Cancel", variant="default", id="btn-cancel-template"
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-create-template":
            name = self.query_one("#new-tmpl-name", Input).value
            if not name:
                self.notify("Template name is required", severity="warning")
                return

            method = str(self.query_one("#new-tmpl-method", Select).value)
            url = self.query_one("#new-tmpl-url", Input).value

            headers: dict[str, str] = {}
            headers_text = self.query_one("#new-tmpl-headers", TextArea).text.strip()
            if headers_text:
                for line in headers_text.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        headers[key.strip()] = value.strip()

            parameters: dict[str, str] = {}
            params_text = self.query_one("#new-tmpl-params", TextArea).text.strip()
            if params_text:
                for line in params_text.split("\n"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        parameters[key.strip()] = value.strip()

            body = self.query_one("#new-tmpl-body", TextArea).text

            template = HttpyRequestTemplate(
                name=name,
                method=method,
                url=url,
                headers=headers,
                parameters=parameters,
                body=body,
            )
            save_template(self._project.name, template)
            self.dismiss(template)
        elif event.button.id == "btn-cancel-template":
            self.dismiss(None)
