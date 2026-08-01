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
    {
        "schemaVersion",
        "taskId",
        "requestedState",
        "summary",
        "evidenceRefs",
        "nextStep",
        "blocked",
        "needsParentDecision",
        "blocker",
    }
)

RECEIPT_SCHEMA_VERSION = 1
RECEIPT_BEGIN = "TASK_CONTROL_RECEIPT_BEGIN"
RECEIPT_END = "TASK_CONTROL_RECEIPT_END"
MAX_RECEIPT_JSON_CHARS = 8192

LEGAL_TRANSITIONS = {
    TaskState.PENDING: frozenset({TaskState.IN_PROGRESS, TaskState.BLOCKED}),
    TaskState.IN_PROGRESS: frozenset(
        {TaskState.BLOCKED, TaskState.COMPLETED}
    ),
    TaskState.BLOCKED: frozenset(
        {TaskState.IN_PROGRESS, TaskState.COMPLETED}
    ),
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
        task_id=_required_text(task_id, "task_id"),
        project=_required_text(project, "project"),
        title=_required_text(title, "title"),
        state=TaskState.PENDING,
        summary="",
        evidence_refs=(),
        next_step="Await child task progress.",
        blocked=False,
        needs_parent_decision=False,
        blocker=None,
    )


def start_task(task: TaskRecord) -> TaskRecord:
    if task.state is not TaskState.PENDING:
        raise ValueError("only PENDING tasks can be started")
    return replace(
        task,
        state=TaskState.IN_PROGRESS,
        summary="Task started.",
        next_step="Await child task result.",
    )


def parse_receipt(payload: Mapping[str, object]) -> ChildReceipt:
    if not isinstance(payload, Mapping):
        raise ValueError("receipt must be an object")
    actual_fields = frozenset(payload.keys())
    unknown = actual_fields - RECEIPT_FIELDS
    if unknown:
        raise ValueError(
            "unknown receipt fields: " + ", ".join(sorted(map(str, unknown)))
        )
    missing = RECEIPT_FIELDS - actual_fields
    if missing:
        raise ValueError(
            "missing receipt fields: " + ", ".join(sorted(missing))
        )

    schema_version = payload["schemaVersion"]
    if (
        type(schema_version) is not int
        or schema_version != RECEIPT_SCHEMA_VERSION
    ):
        raise ValueError(f"unsupported schemaVersion: {schema_version}")

    raw_state = payload["requestedState"]
    try:
        requested_state = TaskState(raw_state)
    except (TypeError, ValueError) as error:
        raise ValueError(f"unsupported requestedState: {raw_state}") from error
    if requested_state is TaskState.PENDING:
        raise ValueError("a child cannot request PENDING")

    raw_evidence = payload["evidenceRefs"]
    if not isinstance(raw_evidence, list) or not raw_evidence:
        raise ValueError("evidenceRefs must be a non-empty list")
    evidence_refs = tuple(
        _required_text(reference, "evidenceRefs item")
        for reference in raw_evidence
    )

    blocked = payload["blocked"]
    needs_parent_decision = payload["needsParentDecision"]
    if type(blocked) is not bool:
        raise ValueError("blocked must be a boolean")
    if type(needs_parent_decision) is not bool:
        raise ValueError("needsParentDecision must be a boolean")
    if blocked != (requested_state is TaskState.BLOCKED):
        raise ValueError("blocked must match requestedState=BLOCKED")

    raw_blocker = payload["blocker"]
    if blocked:
        blocker = _required_text(raw_blocker, "blocked receipt requires a blocker")
    else:
        if raw_blocker is not None:
            raise ValueError("non-blocked receipt must use blocker=null")
        blocker = None
    if needs_parent_decision and not blocked:
        raise ValueError("parent decision is valid only for a blocked receipt")

    return ChildReceipt(
        schema_version=schema_version,
        task_id=_required_text(payload["taskId"], "taskId"),
        requested_state=requested_state,
        summary=_required_text(payload["summary"], "summary"),
        evidence_refs=evidence_refs,
        next_step=_required_text(payload["nextStep"], "nextStep"),
        blocked=blocked,
        needs_parent_decision=needs_parent_decision,
        blocker=blocker,
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

    begin_index = raw_text.find(RECEIPT_BEGIN)
    end_index = raw_text.find(RECEIPT_END)
    if end_index < begin_index:
        raise ValueError("malformed receipt envelope")
    if raw_text[:begin_index].strip():
        raise ValueError("receipt envelope must be the first content")

    json_start = begin_index + len(RECEIPT_BEGIN)
    if json_start >= len(raw_text) or raw_text[json_start] not in "\r\n":
        raise ValueError("receipt marker must be on its own line")
    if end_index == 0 or raw_text[end_index - 1] not in "\r\n":
        raise ValueError("receipt marker must be on its own line")
    after_end = end_index + len(RECEIPT_END)
    if after_end < len(raw_text) and raw_text[after_end] not in "\r\n":
        raise ValueError("receipt marker must be on its own line")
    encoded_receipt = raw_text[json_start:end_index].strip()
    if len(encoded_receipt) > MAX_RECEIPT_JSON_CHARS:
        raise ValueError(
            f"receipt JSON exceeds {MAX_RECEIPT_JSON_CHARS} characters"
        )
    try:
        payload = json.loads(encoded_receipt)
    except json.JSONDecodeError as error:
        raise ValueError("invalid receipt JSON") from error
    return parse_receipt(payload)


def apply_receipt(task: TaskRecord, receipt: ChildReceipt) -> TaskRecord:
    if task.task_id != receipt.task_id:
        raise ValueError("receipt taskId does not match the authoritative task")
    if task.state is TaskState.COMPLETED:
        raise ValueError("COMPLETED is terminal")

    is_snapshot_refresh = (
        task.state is receipt.requested_state
        and task.state in {TaskState.IN_PROGRESS, TaskState.BLOCKED}
    )
    if (
        not is_snapshot_refresh
        and receipt.requested_state not in LEGAL_TRANSITIONS[task.state]
    ):
        raise ValueError(
            "illegal task transition: "
            f"{task.state.value} -> {receipt.requested_state.value}"
        )

    return replace(
        task,
        state=receipt.requested_state,
        summary=receipt.summary,
        evidence_refs=receipt.evidence_refs,
        next_step=receipt.next_step,
        blocked=receipt.blocked,
        needs_parent_decision=receipt.needs_parent_decision,
        blocker=receipt.blocker,
    )


def build_projection(tasks: list[TaskRecord]) -> dict:
    seen_task_ids: set[str] = set()
    for task in tasks:
        if task.task_id in seen_task_ids:
            raise ValueError(f"duplicate taskId: {task.task_id}")
        seen_task_ids.add(task.task_id)

    ordered = sorted(
        tasks,
        key=lambda task: (
            PROJECTION_ORDER[task.state],
            task.project.casefold(),
            task.task_id.casefold(),
        ),
    )
    counts = {state.value: 0 for state in TaskState}
    for task in ordered:
        counts[task.state.value] += 1

    return {
        "counts": counts,
        "blockedCount": counts[TaskState.BLOCKED.value],
        "needsParentDecisionCount": sum(
            1 for task in ordered if task.needs_parent_decision
        ),
        "tasks": [
            {
                "taskId": task.task_id,
                "project": task.project,
                "title": task.title,
                "state": task.state.value,
                "summary": task.summary,
                "evidenceRefs": list(task.evidence_refs),
                "nextStep": task.next_step,
                "blocked": task.blocked,
                "needsParentDecision": task.needs_parent_decision,
                "blocker": task.blocker,
            }
            for task in ordered
        ],
    }
