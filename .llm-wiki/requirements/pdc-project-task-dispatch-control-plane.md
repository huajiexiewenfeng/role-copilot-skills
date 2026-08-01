# Change Brief: pdc-project-task-dispatch-control-plane

## Summary

- title: Project Task Dispatch Lightweight Control Plane
- status: completed
- flow_id: `pdc-project-task-dispatch-control-plane`
- parent_flow_id: `project-task-dispatch`

## Why

`project-task-dispatch` can route complete work packages and validate final
Development receipts, but the coordinating task has no small, deterministic way
to track several project tasks between dispatch and final completion. Humans must
reconstruct current phase, blockers, evidence, and next steps from multiple task
conversations.

## Scope

- active:
  - Define four authoritative task states and a finite legal transition table.
  - Define a strict child-to-parent progress receipt with a short summary,
    evidence references, next step, blocker flag, and parent-decision flag.
  - Make the coordinating task the only authority that accepts receipts and
    changes task state.
  - Produce a concise deterministic projection with blocked work first.
  - Add pure-function tests, including a small two-project read-only fixture.
- reference-only:
  - Existing dispatch routing, task-package transport, and Development final
    receipt contracts.
- excluded:
  - Databases or durable event stores.
  - Web/HTML dashboards.
  - Automatic cross-thread synchronization.
  - WALK integration.
  - A general workflow engine.

## Design

### States

```text
PENDING
IN_PROGRESS
BLOCKED
COMPLETED
```

Legal changes are deliberately finite. `COMPLETED` is terminal. Repeated
`IN_PROGRESS` and `BLOCKED` receipts refresh evidence and next-step information
without constituting a state transition.

### Child Receipt

A child submits a strict, JSON-compatible observation containing:

```text
taskId
requestedState
summary
evidenceRefs[]
nextStep
blocked
needsParentDecision
blocker
```

`requestedState` is a proposal, never an authoritative state mutation. Unknown
fields such as `authoritativeState` or `globalOverview` are rejected.

### Parent Authority And Projection

The coordinating task creates pending task records, validates receipts, applies
legal transitions, and builds the projection. Children cannot write the global
projection. The projector is pure and deterministic: it sorts blocked work
first, then in-progress, pending, and completed work, with stable project/task
tie-breaking.

The standardized receipt and projection are intentionally suitable as a future
interface for WALK or a graphical dashboard. Those adapters are not part of this
delivery.

## Acceptance

- The only states are `PENDING`, `IN_PROGRESS`, `BLOCKED`, and `COMPLETED`.
- Illegal transitions and updates after `COMPLETED` fail deterministically.
- Child receipts are strict, minimal, and cannot contain global state/projection
  mutations.
- Only parent-side reduction changes an authoritative task record.
- Projection output is stable for identical tasks regardless of input order and
  exposes state, blocker, evidence, parent-decision need, and next step.
- Existing task-package, dispatch routing, and Development final receipt tests
  remain compatible.
- No real task is created by automated tests.

## Plan

- active_plan: inline
- status: confirmed
- evidence: coordinating task explicitly requested implementation when scope is
  clear.

## Verification Plan

- Write focused failing tests before the control-plane implementation.
- Verify the RED result is caused by the missing control-plane module/contract.
- Implement the smallest pure-function state reducer and projector.
- Run child skill tests and the parent integration contract.
- Run repository diff/encoding checks before a local commit.

## External Dependencies

- none

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | Current dispatch skill, package script, Development receipt, and tests | 2026-08-01 |
| design | done | Finite states, strict receipt, parent authority, deterministic projection | 2026-08-01 |
| plan | done | Inline TDD plan authorized by coordinating task | 2026-08-01 |
| development | done | Pure receipt validator, immutable reducer, and deterministic projector | 2026-08-01 |
| testing | done | passed-agent-local: child 25/25, directed parent 3/3, parent collection 177/177, Skill validation/package and scoped diff check | 2026-08-01 |
| archive | done | `../handoff/pdc-project-task-dispatch-control-plane-handoff.md` | 2026-08-01 |

## Open Questions

- none
