# Lightweight Task Control Plane

## Purpose

Give the coordinating task one deterministic view of multi-project work without
adding persistence, automatic thread synchronization, or a workflow platform.
Use it for Development progress and for Dispatch only when the user explicitly
asks the parent to wait for or aggregate child results.

## Authority Boundary

The coordinating task is the sole authority for task state and the aggregate
projection. A child submits an observation with a requested state. The parent
validates the observation and decides whether to apply it.

A child must never send an authoritative state record, mutate another task, or
publish a replacement global projection.

## States And Transitions

```text
PENDING -> IN_PROGRESS | BLOCKED
IN_PROGRESS -> BLOCKED | COMPLETED
BLOCKED -> IN_PROGRESS | COMPLETED
COMPLETED -> terminal
```

An `IN_PROGRESS` or `BLOCKED` receipt may refresh the same current state. This
updates evidence, blocker, and next-step information but does not create a new
transition.

After a child task is successfully created and delivered, the parent calls
`start_task` to apply the parent-owned `PENDING -> IN_PROGRESS` transition. A
one-shot child may then request `COMPLETED` in its first receipt.

## Progress Receipt

The receipt uses one exact, versioned JSON envelope:

```text
TASK_CONTROL_RECEIPT_BEGIN
{"schemaVersion": 1, "taskId": "stable-child-task-id", "requestedState": "IN_PROGRESS", "summary": "one short result", "evidenceRefs": ["thread:child-task-id#message"], "nextStep": "one concrete next action", "blocked": false, "needsParentDecision": false, "blocker": null}
TASK_CONTROL_RECEIPT_END
```

Rules:

- The receipt must be the first content in every tracked child update. Optional
  human-readable details may follow `TASK_CONTROL_RECEIPT_END`.
- Emit exactly one envelope. Keep both markers exact and on their own lines.
- Emit a JSON object, not YAML, Markdown fields, or a fenced code block.
- `schemaVersion` is required and must equal `1`.
- Every field is required and unknown fields are rejected.
- `evidenceRefs` contains at least one non-empty reference.
- `blocked=true` exactly when `requestedState=BLOCKED`.
- A blocked receipt has a non-empty `blocker`.
- `needsParentDecision=true` is valid only for a blocked receipt.
- Non-blocked receipts use `blocker: null`.
- `requestedState` is a proposal. The parent reducer remains authoritative.
- Keep the JSON payload within 8192 characters. Summarize long dirty-file lists
  by count and a few evidence references instead of embedding every path.

The parent passes raw task text to `parse_receipt_text`. The parser rejects
missing, duplicate, truncated, malformed, oversized, and unsupported-version
envelopes before the reducer sees the receipt.

## Tracked Dispatch

Dispatch remains untracked by default. If the user explicitly asks to wait for,
collect, or return child results, keep Dispatch mode and set `awaitResult=true`.
Tracked Dispatch uses this envelope, `wait_threads`, parent validation, and the
same deterministic projection. It does not require project-local tests or a
local commit.

The final Development receipt remains defined by `development-receipt.md`.
Progress receipts complement it; they do not replace commit and project-local
test validation.

## Parent Projection

The parent projection contains fixed state counts and one concise row per task:

```text
taskId
project
title
state
summary
evidenceRefs
nextStep
blocked
needsParentDecision
blocker
```

Rows are deterministic: `BLOCKED`, `IN_PROGRESS`, `PENDING`, `COMPLETED`, then
project and task ID. This makes blockers and pending decisions visible without a
graphical dashboard.

## Future Boundary

The standardized receipt and projection may later become an adapter boundary for
WALK or a graphical interface. This delivery intentionally has no database,
WALK adapter, Web/HTML dashboard, automatic cross-thread synchronization, or
general workflow engine.
