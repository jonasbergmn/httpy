import json

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Collapsible, Static, RichLog

from rich.syntax import Syntax
from rich.text import Text

from httpy.core.response import HttpyResponse


class ResponseViewer(Widget):
    def compose(self) -> ComposeResult:
        with Vertical(id="response-container"):
            yield Static("Response", classes="panel-title")
            yield Static("", id="response-status")
            with Collapsible(title="Response Headers", collapsed=True):
                yield RichLog(id="response-headers", wrap=True, markup=True)
            yield Static("Body", classes="section-title")
            with VerticalScroll(id="response-body-scroll"):
                yield RichLog(id="response-body", wrap=True, markup=True)

    def show_response(self, response: HttpyResponse) -> None:
        status = self.query_one("#response-status", Static)
        status_code = response.status_code

        if 200 <= status_code < 300:
            color = "green"
        elif 300 <= status_code < 400:
            color = "yellow"
        elif 400 <= status_code < 500:
            color = "dark_orange"
        else:
            color = "red"

        status.update(Text(f"  Status: {status_code}", style=f"bold {color}"))

        headers_log = self.query_one("#response-headers", RichLog)
        headers_log.clear()
        for key, value in response.headers.items():
            headers_log.write(Text.assemble(
                (f"{key}: ", "bold cyan"),
                (value, ""),
            ))

        body_log = self.query_one("#response-body", RichLog)
        body_log.clear()

        content_type = response.headers.get(
            "Content-Type", response.headers.get("content-type", "")
        )

        if "json" in content_type or self._looks_like_json(response.body):
            try:
                formatted = response.render_json()
                body_log.write(Syntax(formatted, "json", theme="monokai"))
            except (json.JSONDecodeError, ValueError):
                body_log.write(response.body)
        elif "html" in content_type:
            body_log.write(Syntax(response.body, "html", theme="monokai"))
        elif "xml" in content_type:
            body_log.write(Syntax(response.body, "xml", theme="monokai"))
        else:
            body_log.write(response.body)

    @staticmethod
    def _looks_like_json(body: str) -> bool:
        stripped = body.strip()
        return (stripped.startswith("{") and stripped.endswith("}")) or (
            stripped.startswith("[") and stripped.endswith("]")
        )
