from dataclasses import dataclass


@dataclass
class HttpyRequestTemplate:
    name: str
    method: str
    url: str
    headers: dict[str, str]
    parameters: dict[str, str]
    body: str
