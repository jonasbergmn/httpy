from dataclasses import dataclass, field
import uuid


@dataclass
class HttpyRequestTemplate:
    name: str
    method: str
    url: str
    headers: dict[str, str]
    parameters: dict[str, str]
    body: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
