"""Pure planning helpers for Codex native task/thread calls.

The Manager Agent executes the calls. This module deliberately does not speak
to Codex or recreate a thread runtime.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping


MAX_WAIT_TARGETS = 8


def build_create_request(session: Mapping[str, Any], prompt: str, *, model: str | None = None, thinking: str | None = None) -> dict[str, Any]:
    if session["binding"]["state"] != "UNBOUND":
        raise ValueError("create_thread is allowed only for an UNBOUND Project Session")
    if session["writePolicy"] == "WRITE" and not session.get("projectId"):
        raise ValueError("writable Project Session requires an exact saved projectId")
    if session.get("routeMode") == "BASE_PATH_FALLBACK" and (
        session["writePolicy"] != "READ_ONLY" or not session.get("targetWorkdir")
    ):
        raise ValueError("BASE_PATH_FALLBACK requires READ_ONLY and targetWorkdir")
    request: dict[str, Any] = {
        "target": {
            "type": "project",
            "projectId": session["projectId"],
            "environment": {"type": "local"},
        },
        "title": session["binding"]["title"],
        "prompt": prompt,
    }
    if model is not None:
        request["model"] = model
    if thinking is not None:
        request["thinking"] = thinking
    return request


def apply_create_result(session: Mapping[str, Any], result: Mapping[str, Any]) -> dict[str, Any]:
    updated = {**session, "binding": dict(session["binding"])}
    thread_id = result.get("threadId")
    host_id = result.get("hostId")
    client_thread_id = result.get("clientThreadId")
    if thread_id and host_id:
        updated["binding"].update(
            {"state": "BOUND", "threadId": thread_id, "hostId": host_id, "clientThreadId": None}
        )
    elif client_thread_id:
        updated["binding"].update(
            {"state": "CREATE_PENDING", "threadId": None, "hostId": None, "clientThreadId": client_thread_id}
        )
    else:
        raise ValueError("create result must contain threadId+hostId or clientThreadId")
    return updated


def build_wait_batches(
    sessions: Iterable[Mapping[str, Any]], runtime_threads: Mapping[str, Mapping[str, Any]], timeout_ms: int = 60_000
) -> list[dict[str, Any]]:
    if timeout_ms < 0:
        raise ValueError("timeout_ms must be non-negative")
    targets: list[dict[str, Any]] = []
    for session in sessions:
        binding = session["binding"]
        if binding["state"] != "BOUND":
            continue
        key = session["projectSessionKey"]
        target = {"threadId": binding["threadId"], "hostId": binding["hostId"]}
        cursor = runtime_threads.get(key, {}).get("afterCursor")
        if cursor is not None:
            target["afterCursor"] = cursor
        targets.append(target)
    return [
        {"targets": targets[index:index + MAX_WAIT_TARGETS], "timeoutMs": timeout_ms}
        for index in range(0, len(targets), MAX_WAIT_TARGETS)
    ]


def should_deep_read(observation: Mapping[str, Any], *, review_boundary: bool = False) -> bool:
    return bool(
        review_boundary
        or observation.get("nativeStatus") in {"attention", "error"}
        or observation.get("latestTurnStatus") in {"completed", "failed", "cancelled"}
    )


def build_continue_request(session: Mapping[str, Any], message: str) -> dict[str, Any]:
    binding = session["binding"]
    if binding["state"] != "BOUND":
        raise ValueError("send_message_to_thread requires a BOUND Project Session")
    return {"threadId": binding["threadId"], "hostId": binding["hostId"], "prompt": message}


def lifecycle_actions(
    manifest: Mapping[str, Any], *, explicit_pin_requested: bool | None = None,
    explicit_archive_requested: bool = False,
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for session in manifest["projectSessions"]:
        binding = session["binding"]
        if binding["state"] != "BOUND":
            continue
        if explicit_pin_requested is not None:
            actions.append({
                "operation": "set_thread_pinned", "threadId": binding["threadId"],
                "pinned": explicit_pin_requested,
            })
        if manifest["status"] == "CLOSED" and explicit_archive_requested:
            actions.append({
                "operation": "set_thread_archived", "threadId": binding["threadId"],
                "hostId": binding["hostId"], "archived": True,
            })
    return actions


def recovery_plan(manifest: Mapping[str, Any], listed_thread_ids: set[str], archived_thread_ids: set[str]) -> list[dict[str, Any]]:
    """Reconcile only by durable threadId; titles are display metadata."""
    result = []
    known = listed_thread_ids | archived_thread_ids
    for session in manifest["projectSessions"]:
        binding = session["binding"]
        if binding["state"] == "CREATE_PENDING":
            result.append({"projectSessionKey": session["projectSessionKey"], "action": "AWAIT_USER_OR_NATIVE_RESOLUTION", "clientThreadId": binding["clientThreadId"]})
        elif binding["state"] == "BOUND" and binding["threadId"] not in known:
            result.append({"projectSessionKey": session["projectSessionKey"], "action": "MARK_MISSING", "threadId": binding["threadId"]})
        elif binding["state"] == "BOUND":
            result.append({"projectSessionKey": session["projectSessionKey"], "action": "REBUILD_CACHE", "threadId": binding["threadId"], "hostId": binding["hostId"]})
    return result


def user_navigation_request(session: Mapping[str, Any], *, explicitly_requested: bool) -> dict[str, Any] | None:
    if not explicitly_requested:
        return None
    binding = session["binding"]
    if binding["state"] != "BOUND":
        raise ValueError("cannot navigate to an unbound Project Session")
    return {"operation": "navigate_to_codex_page", "threadId": binding["threadId"]}
