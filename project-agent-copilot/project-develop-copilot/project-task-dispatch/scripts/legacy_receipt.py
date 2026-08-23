"""Compatibility parser for active project-task-dispatch 1.x runs.

New v2 Project Worker Sessions do not receive this protocol. A legacy
COMPLETED receipt is only a delivery candidate; callers must still run the v2
Review Gate before approval.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from enum import Enum
from typing import Mapping


class TaskState(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"


@dataclass(frozen=True)
class ChildReceipt:
    schema_version: int
    task_id: str
    requested_state: TaskState
    summary: str
    evidence_refs: tuple[str, ...]
    next_step: str
    blocked: bool
    needs_parent_decision: bool
    blocker: str | None


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    project: str
    title: str
    state: TaskState
    summary: str
    evidence_refs: tuple[str, ...]
    next_step: str
    blocked: bool
    needs_parent_decision: bool
    blocker: str | None


RECEIPT_FIELDS = frozenset(
    {"schemaVersion", "taskId", "requestedState", "summary", "evidenceRefs", "nextStep", "blocked", "needsParentDecision", "blocker"}
)
RECEIPT_SCHEMA_VERSION = 1
RECEIPT_BEGIN = "TASK_CONTROL_RECEIPT_BEGIN"
RECEIPT_END = "TASK_CONTROL_RECEIPT_END"
MAX_RECEIPT_JSON_CHARS = 8192
LEGAL_TRANSITIONS = {
    TaskState.PENDING: frozenset({TaskState.IN_PROGRESS, TaskState.BLOCKED}),
    TaskState.IN_PROGRESS: frozenset({TaskState.BLOCKED, TaskState.COMPLETED}),
    TaskState.BLOCKED: frozenset({TaskState.IN_PROGRESS, TaskState.COMPLETED}),
    TaskState.COMPLETED: frozenset(),
}
PROJECTION_ORDER = {
    TaskState.BLOCKED: 0,
    TaskState.IN_PROGRESS: 1,
    TaskState.PENDING: 2,
    TaskState.COMPLETED: 3,
}


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def create_task(task_id: str, project: str, title: str) -> TaskRecord:
    return TaskRecord(
        _required_text(task_id, "task_id"), _required_text(project, "project"),
        _required_text(title, "title"), TaskState.PENDING, "", (),
        "Await child task progress.", False, False, None,
    )


def start_task(task: TaskRecord) -> TaskRecord:
    if task.state is not TaskState.PENDING:
        raise ValueError("only PENDING tasks can be started")
    return replace(task, state=TaskState.IN_PROGRESS, summary="Task started.", next_step="Await child task result.")


def parse_receipt(payload: Mapping[str, object]) -> ChildReceipt:
    if not isinstance(payload, Mapping):
        raise ValueError("receipt must be an object")
    actual = frozenset(payload)
    unknown = actual - RECEIPT_FIELDS
    missing = RECEIPT_FIELDS - actual
    if unknown:
        raise ValueError("unknown receipt fields: " + ", ".join(sorted(map(str, unknown))))
    if missing:
        raise ValueError("missing receipt fields: " + ", ".join(sorted(missing)))
    schema_version = payload["schemaVersion"]
    if type(schema_version) is not int or schema_version != RECEIPT_SCHEMA_VERSION:
        raise ValueError(f"unsupported schemaVersion: {schema_version}")
    try:
        requested_state = TaskState(payload["requestedState"])
    except (TypeError, ValueError) as error:
        raise ValueError(f"unsupported requestedState: {payload['requestedState']}") from error
    if requested_state is TaskState.PENDING:
        raise ValueError("a child cannot request PENDING")
    raw_evidence = payload["evidenceRefs"]
    if not isinstance(raw_evidence, list) or not raw_evidence:
        raise ValueError("evidenceRefs must be a non-empty list")
    evidence = tuple(_required_text(item, "evidenceRefs item") for item in raw_evidence)
    blocked = payload["blocked"]
    parent_decision = payload["needsParentDecision"]
    if type(blocked) is not bool or type(parent_decision) is not bool:
        raise ValueError("blocked and needsParentDecision must be booleans")
    if blocked != (requested_state is TaskState.BLOCKED):
        raise ValueError("blocked must match requestedState=BLOCKED")
    if blocked:
        blocker = _required_text(payload["blocker"], "blocked receipt requires a blocker")
    elif payload["blocker"] is not None:
        raise ValueError("non-blocked receipt must use blocker=null")
    else:
        blocker = None
    if parent_decision and not blocked:
        raise ValueError("parent decision is valid only for a blocked receipt")
    return ChildReceipt(
        schema_version, _required_text(payload["taskId"], "taskId"), requested_state,
        _required_text(payload["summary"], "summary"), evidence,
        _required_text(payload["nextStep"], "nextStep"), blocked, parent_decision, blocker,
    )


def parse_receipt_text(raw_text: str) -> ChildReceipt:
    if not isinstance(raw_text, str):
        raise ValueError("raw receipt text must be a string")
    begin_count = raw_text.count(RECEIPT_BEGIN)
    end_count = raw_text.count(RECEIPT_END)
    if begin_count == 0 and end_count == 0:
        raise ValueError("missing receipt envelope")
    if begin_count > 1 or end_count > 1:
        raise ValueError("duplicate receipt envelope")
    if begin_count == 0 or end_count == 0:
        raise ValueError("truncated receipt envelope")
    begin = raw_text.find(RECEIPT_BEGIN)
    end = raw_text.find(RECEIPT_END)
    if end < begin:
        raise ValueError("malformed receipt envelope")
    if raw_text[:begin].strip():
        raise ValueError("receipt envelope must be the first content")
    json_start = begin + len(RECEIPT_BEGIN)
    if json_start >= len(raw_text) or raw_text[json_start] not in "\r\n":
        raise ValueError("receipt marker must be on its own line")
    if end == 0 or raw_text[end - 1] not in "\r\n":
        raise ValueError("receipt marker must be on its own line")
    after_end = end + len(RECEIPT_END)
    if after_end < len(raw_text) and raw_text[after_end] not in "\r\n":
        raise ValueError("receipt marker must be on its own line")
    encoded = raw_text[json_start:end].strip()
    if len(encoded) > MAX_RECEIPT_JSON_CHARS:
        raise ValueError(f"receipt JSON exceeds {MAX_RECEIPT_JSON_CHARS} characters")
    try:
        return parse_receipt(json.loads(encoded))
    except json.JSONDecodeError as error:
        raise ValueError("invalid receipt JSON") from error


def apply_receipt(task: TaskRecord, receipt: ChildReceipt) -> TaskRecord:
    if task.task_id != receipt.task_id:
        raise ValueError("receipt taskId does not match the authoritative task")
    if task.state is TaskState.COMPLETED:
        raise ValueError("COMPLETED is terminal")
    refresh = task.state is receipt.requested_state and task.state in {TaskState.IN_PROGRESS, TaskState.BLOCKED}
    if not refresh and receipt.requested_state not in LEGAL_TRANSITIONS[task.state]:
        raise ValueError(f"illegal task transition: {task.state.value} -> {receipt.requested_state.value}")
    return replace(
        task, state=receipt.requested_state, summary=receipt.summary,
        evidence_refs=receipt.evidence_refs, next_step=receipt.next_step,
        blocked=receipt.blocked, needs_parent_decision=receipt.needs_parent_decision,
        blocker=receipt.blocker,
    )


def completed_receipt_to_delivery_candidate(receipt: ChildReceipt, submitted_at: str) -> dict:
    if receipt.requested_state is not TaskState.COMPLETED:
        raise ValueError("only a COMPLETED legacy receipt can become a delivery candidate")
    return {
        "submittedAt": submitted_at,
        "summary": receipt.summary,
        "acceptanceIds": [],
        "changedFiles": [],
        "tests": [],
        "branch": "legacy-unverified",
        "head": "0000000",
        "commit": None,
        "risks": ["Legacy receipt evidence requires Manager verification before approval."],
        "legacyEvidenceRefs": list(receipt.evidence_refs),
        "targetState": "SUBMITTED",
    }


def build_projection(tasks: list[TaskRecord]) -> dict:
    seen: set[str] = set()
    for task in tasks:
        if task.task_id in seen:
            raise ValueError(f"duplicate taskId: {task.task_id}")
        seen.add(task.task_id)
    ordered = sorted(
        tasks,
        key=lambda task: (PROJECTION_ORDER[task.state], task.project.casefold(), task.task_id.casefold()),
    )
    counts = {state.value: 0 for state in TaskState}
    for task in ordered:
        counts[task.state.value] += 1
    return {
        "counts": counts,
        "blockedCount": counts[TaskState.BLOCKED.value],
        "needsParentDecisionCount": sum(1 for task in ordered if task.needs_parent_decision),
        "tasks": [
            {
                "taskId": task.task_id, "project": task.project, "title": task.title,
                "state": task.state.value, "summary": task.summary,
                "evidenceRefs": list(task.evidence_refs), "nextStep": task.next_step,
                "blocked": task.blocked, "needsParentDecision": task.needs_parent_decision,
                "blocker": task.blocker,
            }
            for task in ordered
        ],
    }
