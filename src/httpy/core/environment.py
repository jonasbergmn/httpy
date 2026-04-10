from dataclasses import dataclass


@dataclass
class HttpyEnvironment:
    name: str
    configs: dict[str, str]
