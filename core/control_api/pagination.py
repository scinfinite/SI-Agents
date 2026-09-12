"""Bounded, filter-bound cursor pagination for SDK-facing collections."""
from __future__ import annotations

import base64
import hashlib
import json
from typing import Any, Iterable, Mapping

MAX_PAGE = 1000


def _fingerprint(params: Mapping[str, str]) -> str:
    payload = json.dumps(dict(sorted(params.items())), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def encode_cursor(offset: int, params: Mapping[str, str]) -> str:
    raw = json.dumps({"offset": offset, "fingerprint": _fingerprint(params)}, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(cursor: str, params: Mapping[str, str]) -> int:
    if len(cursor) > 256:
        raise ValueError("cursor is too long")
    try:
        raw = base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4))
        payload = json.loads(raw.decode())
        offset = int(payload["offset"])
        fingerprint = str(payload["fingerprint"])
    except (ValueError, TypeError, KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid cursor") from exc
    if offset < 0 or offset > 1_000_000:
        raise ValueError("invalid cursor offset")
    if fingerprint != _fingerprint(params):
        raise ValueError("cursor does not match query")
    return offset


def paginate(items: Iterable[Mapping[str, Any]], *, limit: int, cursor: str | None, params: Mapping[str, str]) -> dict[str, Any]:
    if not 1 <= limit <= MAX_PAGE:
        raise ValueError(f"limit must be between 1 and {MAX_PAGE}")
    values = list(items)
    offset = decode_cursor(cursor, params) if cursor else 0
    page = values[offset : offset + limit]
    next_cursor = encode_cursor(offset + limit, params) if offset + limit < len(values) else None
    return {"items": page, "next_cursor": next_cursor, "limit": limit}


def filter_items(items: Iterable[Mapping[str, Any]], query: str | None, filters: Mapping[str, str]) -> list[Mapping[str, Any]]:
    if query:
        needle = query.casefold().strip()
        if len(needle) > 256:
            raise ValueError("query is too long")
    result = []
    for item in items:
        if query:
            haystack = " ".join(str(value) for value in item.values() if isinstance(value, (str, int, float))).casefold()
            if needle not in haystack:
                continue
        if any(str(item.get(key, "")) != value for key, value in filters.items()):
            continue
        result.append(item)
    return result
