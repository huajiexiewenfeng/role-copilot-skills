# PDC Task Control Plane 2.0

## Authority

| Fact | Authority |
|---|---|
| native task/turn active, idle, final, attention, error, history | Codex thread runtime |
| Dispatch, Project Session, work item, dependency, acceptance, finding, approval | `manifest.json` |
| branch, HEAD, dirty state, diff, tests | Git/filesystem evidence |
| wait cursor and last native observation | `runtime-cache.json` |

The Manager Session is the only writer of the PDC management directory. Worker
and Reviewer Sessions communicate only through native commentary/final and
Manager messages. The directory is not a queue.

## Registry and identity

`dispatchId` contains Project Sessions keyed by `projectSessionKey`; work items
use stable `taskId` and reference one Project Session. A `threadId + hostId`
binds a PDC Session to a user-visible Codex task. `clientThreadId` represents
only queued creation and cannot be waited/read/sent.

Default cardinality is one `WRITE` Worker for each `projectId` in a Dispatch.
Multiple same-Project work items share it and execute in serial batches.

## Work item states

```text
READY
WAITING_DEPENDENCY
ASSIGNED
SUBMITTED
REVIEWING
CHANGES_REQUESTED
APPROVED
BLOCKED
STALE
```

Native `active/idle/error/attention` is never copied into this state field.
Allowed normal transitions are:

```text
WAITING_DEPENDENCY --DEPENDENCIES_SATISFIED--> READY
READY --WORK_ASSIGNED--> ASSIGNED
ASSIGNED --WORKER_SUBMITTED--> SUBMITTED
SUBMITTED --REVIEW_STARTED--> REVIEWING
REVIEWING --REVIEW_APPROVED--> APPROVED
REVIEWING --REVIEW_CHANGES_REQUESTED--> CHANGES_REQUESTED
CHANGES_REQUESTED --WORKER_RESUBMITTED--> SUBMITTED
```

Any non-approved item can raise a structured blocker. Resolution derives
WAITING_DEPENDENCY, READY, ASSIGNED, or SUBMITTED from current evidence.
Contract/baseline/upstream invalidation moves assigned or reviewed work to
STALE; Manager explicitly requeues it.

The following are forbidden: `ASSIGNED→APPROVED`, `SUBMITTED→APPROVED`,
`CHANGES_REQUESTED→APPROVED`, native idle→SUBMITTED, or Worker “completed”→APPROVED.

## Reducer order

1. Load and validate schema version and revision.
2. Validate event identity, current state, guard, and external evidence.
3. Apply one transition.
4. Recompute dependency states and Dispatch aggregate.
5. Increment revision and atomically replace `manifest.json` using an optimistic
   previous-revision check.
6. Regenerate Markdown/SVG/PNG and emit a Manager snapshot only for meaningful change.

Use `scripts/manifest_v2.py` and `scripts/task_control.py`; do not manually repair
state JSON. A repeated cursor/final must be idempotently ignored.

## Approval Gate

Approval requires exact Project/repository/branch, explainable baseline/final
HEAD, authorized changed files, required acceptance PASS/authorized WAIVED,
actual passing/waived tests, no OPEN finding, current contract revision,
APPROVED dependencies, verified commit/HEAD, and verified cross-repository side
effects. A Worker final supplies a delivery candidate only.

## Aggregate Dispatch

- `DRAFT`: no work started.
- `ACTIVE`: required work remains with a path forward.
- `BLOCKED`: no required path can advance and at least one required item is blocked.
- `APPROVED`: all required work approved and final cross-repository check passed.
- `CLOSED`: Manager closeout completed and requested lifecycle policy actions
  succeeded. Real Sessions may remain visible and unarchived.

`ATTENTION` is a derived view flag from native attention, blocker, or OPEN finding.
