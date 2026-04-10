from dataclasses import dataclass
import json
from typing import Callable


@dataclass
class HttpyResponse:
    status_code: int
    headers: dict[str, str]
    body: str

    def render_json(self) -> str:
        parsed = json.loads(self.body)
        return json.dumps(parsed, indent=4)

    def render_custom(self, render_function: Callable[[str], str]) -> str:
        return render_function(self.body)
