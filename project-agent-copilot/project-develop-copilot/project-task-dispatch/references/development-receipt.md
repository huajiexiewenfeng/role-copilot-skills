# Development Receipt

Development mode tracks every child through project-local implementation,
verification, and local commit. Dispatch mode does not use this receipt.

During execution, progress and blocker updates use the strict receipt from
`task-control-plane.md`. That progress receipt updates the coordinating task's
projection only after parent validation. It does not replace this final
Development receipt.

Emit each progress receipt as the receipt-first JSON envelope defined by the
control-plane reference. Human-readable detail may follow the envelope but may
not precede it.

## Required Schema

```yaml
status: COMPLETED | BLOCKED | FAILED | NO_CHANGE_REQUIRED
project: logical-project-id
target_workdir: absolute-path
branch: branch-name
commits:
  - commit-sha
changes:
  - concise change summary
tests:
  - command: exact project-local test command
    result: PASSED | FAILED
contract_changes:
  - none or explicit differences
artifacts:
  - generated artifact or document
blockers:
  - none or blocker details
```

Every field is required. Use a literal `none` item when a list has no applicable
value.

## Validation

### COMPLETED

- Requires at least one local commit containing only task-owned changes.
- Every required project-local test must be listed and pass.
- Contract differences must be explicit, including `none`.
- No commit is pushed.
- No cross-project integration tests are required.

### NO_CHANGE_REQUIRED

- Explains the evidence proving no code or document change is needed.
- Creates no empty commit.
- Requires parent or user acceptance before the batch is complete.

### BLOCKED or FAILED

- Includes actionable blockers or failure evidence.
- Prevents dependent downstream tasks from starting.
- Does not stop independent dependency chains.

## Parent Validation

The parent may request one follow-up when required fields are missing. It checks
the target root, branch, commit existence, project-local test evidence, contract
differences, and blockers. It does not perform cross-project integration tests.

Overall Development status:

```text
COMPLETED
  Every required child has a valid COMPLETED receipt, or an explicitly accepted
  NO_CHANGE_REQUIRED receipt.

INCOMPLETE
  Any child is blocked, failed, missing a commit, has failing tests, lacks a
  required receipt field, or has an unaccepted no-change result.
```

Control-plane mapping:

- a validated `COMPLETED` final receipt may support a child
  `requestedState=COMPLETED` update;
- `BLOCKED` and `FAILED` final receipts remain `BLOCKED` in the lightweight
  projection with evidence and a next step;
- `NO_CHANGE_REQUIRED` remains `BLOCKED` with
  `needsParentDecision=true` until the parent or user accepts it;
- only the coordinating task accepts the receipt and changes authoritative task
  state.
