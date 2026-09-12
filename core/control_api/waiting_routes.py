"""Durable-wait Control API adapter; SI Core remains the authority."""
from __future__ import annotations

import json
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from core.waiting import ScheduleSpec, WaitKind, WaitState, WaitingService


def install_waiting_routes(handler_cls):
    """Install wait routes without duplicating the Control API transport."""
    if getattr(handler_cls, "_waiting_routes_installed", False):
        return handler_cls
    original_get = handler_cls.do_GET
    original_post = handler_cls.do_POST

    def waiting_service(handler):
        server = handler.server
        service = getattr(server, "waiting_service", None)
        if service is None:
            service = WaitingService(server.control_service.root / ".si" / "waiting.v1.sqlite3")
            server.waiting_service = service
        return service

    def identity(handler):
        subject = handler.headers.get("X-SI-Subject", "").strip()
        project = handler.headers.get("X-SI-Project", "").strip()
        if not subject or not project:
            raise PermissionError("X-SI-Subject and X-SI-Project are required")
        return subject[:512], project[:512]

    def get(handler):
        path = urlparse(handler.path).path.rstrip("/")
        if not path.startswith("/api/v1/waits"):
            return original_get()
        subject, project = identity(handler)
        service = waiting_service(handler)
        if path == "/api/v1/waits":
            params = parse_qs(urlparse(handler.path).query)
            limit = int(params.get("limit", ["100"])[0])
            state_value = params.get("state", [None])[0]
            state = WaitState(state_value) if state_value else None
            handler._send(200, [item.as_dict() for item in service.list(subject_id=subject, project_id=project, state=state, limit=limit)])
            return
        suffix = path.removeprefix("/api/v1/waits/")
        if suffix.endswith("/events"):
            wait_id = suffix.removesuffix("/events")
            handler._send(200, service.events(wait_id, subject_id=subject, project_id=project))
            return
        handler._send(200, service.get(suffix, subject_id=subject, project_id=project).as_dict())

    def post(handler):
        path = urlparse(handler.path).path.rstrip("/")
        if not path.startswith("/api/v1/waits"):
            return original_post()
        subject, project = identity(handler)
        service = waiting_service(handler)
        payload = handler._read_json()
        if path == "/api/v1/waits":
            kind = WaitKind(str(payload.get("kind", "timer")))
            wake_at = datetime.fromisoformat(str(payload["wake_at"]))
            deadline = datetime.fromisoformat(str(payload["deadline"])) if payload.get("deadline") else None
            schedule_payload = payload.get("schedule")
            schedule = None
            if isinstance(schedule_payload, dict):
                schedule = ScheduleSpec(
                    kind=WaitKind(str(schedule_payload["kind"])),
                    interval_seconds=schedule_payload.get("interval_seconds"),
                    cron=schedule_payload.get("cron"),
                    max_occurrences=schedule_payload.get("max_occurrences"),
                )
            record = service.create(
                subject_id=subject,
                project_id=project,
                kind=kind,
                wake_at=wake_at,
                deadline=deadline,
                priority=int(payload.get("priority", 0)),
                schedule=schedule,
                trigger=payload.get("trigger"),
                payload=payload.get("payload", {}),
            )
            handler._send(201, record.as_dict())
            return
        suffix = path.removeprefix("/api/v1/waits/")
        if suffix.endswith("/wake"):
            wait_id = suffix.removesuffix("/wake")
            record = service.wake(wait_id, subject_id=subject, project_id=project, trigger=str(payload.get("trigger", "")))
            handler._send(200, record.as_dict())
            return
        if suffix.endswith("/cancel"):
            wait_id = suffix.removesuffix("/cancel")
            record = service.cancel(wait_id, subject_id=subject, project_id=project, reason=str(payload.get("reason", "")))
            handler._send(200, record.as_dict())
            return
        if suffix.endswith("/claim"):
            limit = int(payload.get("limit", 1))
            handler._send(200, [item.as_dict() for item in service.claim_ready(subject_id=subject, project_id=project, limit=limit)])
            return
        if suffix.endswith("/complete"):
            wait_id = suffix.removesuffix("/complete")
            revision = payload.get("expected_revision")
            record = service.complete(wait_id, subject_id=subject, project_id=project, expected_revision=revision if isinstance(revision, int) else None)
            handler._send(200, record.as_dict())
            return
        handler._send(404, {"error": "not_found", "message": "route not found", "request_id": handler._request_id()})

    def wrapped_get(handler):
        try:
            return get(handler)
        except PermissionError as exc:
            handler._send(403, {"error": "forbidden", "message": str(exc), "request_id": handler._request_id()})
        except KeyError:
            handler._send(404, {"error": "not_found", "message": "wait not found", "request_id": handler._request_id()})
        except (TypeError, ValueError, OverflowError) as exc:
            handler._send(400, {"error": "invalid_request", "message": str(exc), "request_id": handler._request_id()})

    def wrapped_post(handler):
        try:
            return post(handler)
        except PermissionError as exc:
            handler._send(403, {"error": "forbidden", "message": str(exc), "request_id": handler._request_id()})
        except KeyError:
            handler._send(404, {"error": "not_found", "message": "wait not found", "request_id": handler._request_id()})
        except (TypeError, ValueError, OverflowError, json.JSONDecodeError) as exc:
            handler._send(400, {"error": "invalid_request", "message": str(exc), "request_id": handler._request_id()})

    handler_cls.do_GET = wrapped_get
    handler_cls.do_POST = wrapped_post
    handler_cls._waiting_routes_installed = True
    return handler_cls
