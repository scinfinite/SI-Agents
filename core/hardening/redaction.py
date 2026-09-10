"""Conservative secret-like value redaction for logs and telemetry."""

import re
from collections.abc import Mapping

_SECRET_KEY = re.compile(r"(?:token|secret|password|passwd|api[_-]?key|authorization|credential)", re.I)
_BEARER = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")


def redact(value: object) -> object:
    """Return a recursively redacted, logging-safe representation."""
    if isinstance(value, Mapping):
        return {
            str(key): "[REDACTED]" if _SECRET_KEY.search(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return type(value)(redact(item) for item in value)
    if isinstance(value, str):
        return _BEARER.sub("Bearer [REDACTED]", value)
    return value
