"""In-process event subscription registry used by SSE and webhook clients."""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import threading
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.request import Request, urlopen


@dataclass(frozen=True, slots=True)
class Subscription:
    id: str
    event_types: tuple[str, ...]
    subject: str | None
    transport: str
    target: str | None
    secret: str | None
    status: str = "active"

    def as_dict(self) -> dict[str, object]:
        return {"id": self.id, "event_types": list(self.event_types), "subject": self.subject, "transport": self.transport, "target": self.target, "status": self.status}


class SubscriptionRegistry:
    """Bounded registry; webhook secrets are never returned after creation."""

    def __init__(self, max_subscriptions: int = 256) -> None:
        self._max = max_subscriptions
        self._items: dict[str, Subscription] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _validate_target(target: str) -> str:
        parsed = urlparse(target)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError("webhook target must be an absolute HTTP(S) URL without credentials")
        if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("webhook HTTP targets must be loopback; use HTTPS for remote targets")
        return target

    def create(self, *, event_types: list[str], subject: str | None, transport: str, target: str | None) -> Subscription:
        if transport not in {"sse", "webhook"}:
            raise ValueError("transport must be sse or webhook")
        if len(event_types) > 32 or any(not isinstance(x, str) or not x or len(x) > 128 for x in event_types):
            raise ValueError("event_types must contain at most 32 non-empty names")
        if target is not None and transport == "webhook":
            target = self._validate_target(target)
        if transport == "webhook" and not target:
            raise ValueError("webhook target is required")
        with self._lock:
            if len(self._items) >= self._max:
                raise ValueError("subscription capacity reached")
            subscription_id = "sub_" + secrets.token_urlsafe(18)
            secret = secrets.token_urlsafe(32) if transport == "webhook" else None
            item = Subscription(subscription_id, tuple(sorted(set(event_types))), subject, transport, target, secret)
            self._items[subscription_id] = item
            return item

    def list(self) -> list[Subscription]:
        with self._lock:
            return list(self._items.values())

    def delete(self, subscription_id: str) -> None:
        with self._lock:
            if subscription_id not in self._items:
                raise KeyError(subscription_id)
            del self._items[subscription_id]

    def matching(self, event: dict[str, object]) -> list[Subscription]:
        event_type = str(event.get("event_type", ""))
        subject = str(event.get("subject", ""))
        with self._lock:
            return [x for x in self._items.values() if (not x.event_types or event_type in x.event_types) and (x.subject is None or x.subject == subject)]

    @staticmethod
    def signed_headers(body: bytes, secret: str) -> dict[str, str]:
        digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return {"X-SI-Signature": f"sha256={digest}", "X-SI-Webhook-Version": "v1"}

    def deliver(self, event: dict[str, object], *, timeout: float = 3.0) -> None:
        body = json.dumps(event, sort_keys=True, separators=(",", ":")).encode()
        for item in self.matching(event):
            if item.transport != "webhook" or not item.target or not item.secret:
                continue
            request = Request(item.target, data=body, headers={"Content-Type": "application/json", **self.signed_headers(body, item.secret)}, method="POST")
            try:
                with urlopen(request, timeout=timeout) as response:
                    response.read(1)
            except Exception:
                # Delivery is best-effort and never changes SI Core state.
                continue

    def public(self, item: Subscription) -> dict[str, object]:
        return item.as_dict()
