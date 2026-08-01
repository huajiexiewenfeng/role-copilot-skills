# Lightweight Task Control Plane

## Purpose

Give the coordinating task one deterministic view of multi-project work without
adding persistence, automatic thread synchronization, or a workflow platform.

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

## Progress Receipt

```yaml
taskId: stable-child-task-id
requestedState: IN_PROGRESS | BLOCKED | COMPLETED
summary: one short result
evidenceRefs:
  - thread:child-task-id#message
nextStep: one concrete next action
blocked: false
needsParentDecision: false
blocker: null
```

Rules:

- Every field is required and unknown fields are rejected.
- `evidenceRefs` contains at least one non-empty reference.
- `blocked=true` exactly when `requestedState=BLOCKED`.
- A blocked receipt has a non-empty `blocker`.
- `needsParentDecision=true` is valid only for a blocked receipt.
- Non-blocked receipts use `blocker: null`.
- `requestedState` is a proposal. The parent reducer remains authoritative.

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
