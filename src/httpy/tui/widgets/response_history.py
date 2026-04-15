import json

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static, ListView, ListItem, Label

from rich.text import Text

from httpy.core.response import HttpyResponse
from httpy.io import load_responses


class ResponseHistory(Widget):
    class ResponseSelected(Message):
        def __init__(self, response: HttpyResponse) -> None:
            super().__init__()
            self.response = response

    _responses: list[HttpyResponse] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="response-history-container"):
            yield Static("Recent Responses", classes="panel-title")
            yield ListView(id="response-history-list")

    def load_for_template(self, project_name: str, template_id: str) -> None:
        self._responses = load_responses(project_name, template_id)
        self._render_list()

    def _render_list(self) -> None:
        list_view = self.query_one("#response-history-list", ListView)
        list_view.clear()

        for response in reversed(self._responses):
            if 200 <= response.status_code < 300:
                color = "green"
            elif 300 <= response.status_code < 400:
                color = "yellow"
            elif 400 <= response.status_code < 500:
                color = "dark_orange"
            else:
                color = "red"

            label = Text.assemble(
                (f"[{response.status_code}] ", f"bold {color}"),
                (self._body_preview(response.body), ""),
            )
            list_view.append(ListItem(Label(label)))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = len(self._responses) - 1 - event.list_view.index
        if 0 <= index < len(self._responses):
            self.post_message(self.ResponseSelected(self._responses[index]))

    @staticmethod
    def _body_preview(body: str, max_len: int = 60) -> str:
        stripped = body.strip().replace("\n", " ")
        if len(stripped) > max_len:
            return stripped[:max_len] + "…"
        return stripped
