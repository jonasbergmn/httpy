from pathlib import Path


_basepath = Path("projects")


def set_basepath(path: str | Path) -> None:
    global _basepath
    match path:
        case str():
            _basepath = Path(path)
        case Path():
            _basepath = path


def get_basepath() -> Path:
    return _basepath
