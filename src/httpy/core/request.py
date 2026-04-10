from dataclasses import dataclass


@dataclass
class HttpyRequest:
    method: str
    url: str
    headers: dict[str, str]
    parameters: dict[str, str]
    body: str
