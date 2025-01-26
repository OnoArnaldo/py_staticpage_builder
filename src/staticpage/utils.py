import typing as _
from datetime import datetime, UTC


def datetime_now(pattern: str = "%d/%m/%Y") -> str:
    return datetime.now(UTC).strftime(pattern)


def static_url(static_path: str) -> _.Callable:
    def _static(path: str) -> str:
        path = path.lstrip("/")
        return f"{static_path}/{path}"

    return _static
