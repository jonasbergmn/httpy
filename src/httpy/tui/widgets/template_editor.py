from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Select, Static, TextArea

from httpy.core.environment import HttpyEnvironment
from httpy.core.project import HttpyProject
from httpy.core.response import HttpyResponse
from httpy.core.template import HttpyRequestTemplate
from httpy.io import save_template, save_response
import asyncio


HTTP_METHODS = [
    ("GET", "GET"),
    ("POST", "POST"),
    ("PUT", "PUT"),
    ("PATCH", "PATCH"),
    ("DELETE", "DELETE"),
    ("HEAD", "HEAD"),
    ("OPTIONS", "OPTIONS"),
]


class TemplateEditor(Widget):
    class RequestSent(Message):
        def __init__(self, response: HttpyResponse) -> None:
            super().__init__()
            self.response = response

    class TemplateSaved(Message):
        pass

    _template: HttpyRequestTemplate | None = None
    _project: HttpyProject | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(classes="sticky-bar"):
            yield Button(
                "Send Request (Ctrl+S)", variant="success", id="btn-send-request"
            )
        with VerticalScroll(id="template-form"):
            yield Static("Template Editor", classes="panel-title")
            yield Label("Name")
            yield Input(placeholder="Request name", id="tmpl-name")
            with Horizontal(classes="form-row"):
                with Vertical(classes="method-select"):
                    yield Label("Method")
                    yield Select(HTTP_METHODS, value="GET", id="tmpl-method")
                with Vertical(classes="url-input"):
                    yield Label("URL")
                    yield Input(
                        placeholder="https://api.example.com/{{BASE_URL}}/endpoint",
                        id="tmpl-url",
                    )
            yield Label("Headers (one per line: Key: Value)")
            yield TextArea(id="tmpl-headers")
            yield Label("Parameters (one per line: key=value)")
            yield TextArea(id="tmpl-params")
            yield Label("Body")
            yield TextArea(id="tmpl-body")
            yield Label("Environment")
            yield Select([], id="tmpl-env-select", allow_blank=True)
            with Horizontal(classes="button-row"):
                yield Button("Save", variant="primary", id="btn-save-template")

    def load_template(
        self, template: HttpyRequestTemplate, project: HttpyProject
    ) -> None:
        self._template = template
        self._project = project

        self.query_one("#tmpl-name", Input).value = template.name
        self.query_one("#tmpl-method", Select).value = template.method
        self.query_one("#tmpl-url", Input).value = template.url

        headers_text = "\n".join(f"{k}: {v}" for k, v in template.headers.items())
        self.query_one("#tmpl-headers", TextArea).text = headers_text

        params_text = "\n".join(f"{k}={v}" for k, v in template.parameters.items())
        self.query_one("#tmpl-params", TextArea).text = params_text
        self.query_one("#tmpl-body", TextArea).text = template.body

        env_options = [(env.name, env.name) for env in project.environments]
        env_select = self.query_one("#tmpl-env-select", Select)
        env_select.set_options(env_options)
        if project.environments:
            env_select.value = project.environments[0].name

    def _build_template_from_form(self) -> HttpyRequestTemplate:
        name = self.query_one("#tmpl-name", Input).value
        method = str(self.query_one("#tmpl-method", Select).value)
        url = self.query_one("#tmpl-url", Input).value

        headers: dict[str, str] = {}
        headers_text = self.query_one("#tmpl-headers", TextArea).text.strip()
        if headers_text:
            for line in headers_text.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip()] = value.strip()

        parameters: dict[str, str] = {}
        params_text = self.query_one("#tmpl-params", TextArea).text.strip()
        if params_text:
            for line in params_text.split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    parameters[key.strip()] = value.strip()

        body = self.query_one("#tmpl-body", TextArea).text

        template_id = self._template.id if self._template else None
        if template_id:
            return HttpyRequestTemplate(
                name=name,
                method=method,
                url=url,
                headers=headers,
                parameters=parameters,
                body=body,
                id=template_id,
            )
        return HttpyRequestTemplate(
            name=name,
            method=method,
            url=url,
            headers=headers,
            parameters=parameters,
            body=body,
        )

    def action_send_request(self) -> None:
        self._send_request()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save-template":
            self._save_template()
        elif event.button.id == "btn-send-request":
            self._send_request()

    def _save_template(self) -> None:
        if self._project is None:
            self.notify("No project selected", severity="warning")
            return

        template = self._build_template_from_form()
        self._template = template
        save_template(self._project.name, template)
        self.notify(f"Template '{template.name}' saved")
        self.post_message(self.TemplateSaved())

    def _send_request(self) -> None:
        if self._project is None:
            self.notify("No project selected", severity="warning")
            return

        env_name = self.query_one("#tmpl-env-select", Select).value
        if env_name is None or env_name == Select.BLANK:
            self.notify("Select an environment first", severity="warning")
            return

        environment = next(
            (e for e in self._project.environments if e.name == env_name), None
        )
        if environment is None:
            self.notify(f"Environment '{env_name}' not found", severity="error")
            return

        template = self._build_template_from_form()
        project = self._project

        self.notify("Sending request...", severity="information")
        self.run_worker(
            self._execute_request(project, template, environment),
            name="send-request",
            exclusive=True,
        )

    async def _execute_request(
        self,
        project: HttpyProject,
        template: HttpyRequestTemplate,
        environment: HttpyEnvironment,
    ) -> None:
        try:
            request = project.make_request(template, environment)
            response = await asyncio.to_thread(project.execute_request, request)
            save_response(project.name, template.id, response)
            self.post_message(self.RequestSent(response))
        except Exception as e:
            self.notify(f"Request failed: {e}", severity="error")
