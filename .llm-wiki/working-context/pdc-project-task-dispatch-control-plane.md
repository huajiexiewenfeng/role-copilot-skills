# Working Context: pdc-project-task-dispatch-control-plane

## Scope Lock

- active:
  - `project-task-dispatch/SKILL.md`
  - `project-task-dispatch/references/development-receipt.md`
  - `project-task-dispatch/references/task-control-plane.md`
  - `project-task-dispatch/scripts/task_control.py`
  - focused child tests and parent integration file inventory
  - requirement and Wiki index for this flow
- read-only:
  - existing task package builder, route protocol, templates, and evals
- excluded:
  - unrelated dirty files in `references/session-digest-implementation-plan.zh.md`
  - unrelated `internal-trial-guides/`
  - installed workstation copy of the skill
  - databases, dashboards, WALK adapters, automatic thread synchronization

## File Map

| File | Responsibility |
|---|---|
| `references/task-control-plane.md` | Human-readable state, receipt, authority, and projection contract |
| `scripts/task_control.py` | Pure state validation, immutable reduction, and deterministic projection |
| `tests/test_task_control.py` | State, schema, authority, projection, and two-project fixture tests |
| `tests/test_skill_contract.py` | Progressive disclosure and documentation contract |
| parent integration contract | Exact shipped child-skill file inventory |

## TDD Evidence

- RED: focused suite failed 8/8 because `scripts/task_control.py` did not exist.
- GREEN: focused suite passed 8/8 after the minimal pure-function implementation.
- Contract RED: skill entrypoint test failed because it did not reference
  `task-control-plane.md`.
- Contract GREEN: entrypoint/reference suite passed 10/10 after progressive
  disclosure was wired.

## Verification Result

- Official child tests: 25/25 passed.
- Directed parent integration contract: 3/3 passed.
- Full parent collection: 177/177 passed.
- Skill Creator `quick_validate.py`: valid.
- Skill Creator package build: succeeded in a temporary directory.
- Scoped `git diff --check`: clean; unrelated dirty files were excluded.
- Verification authority: passed-agent-local; no CI or independent reviewer run.
- Local commit: required by the final Development receipt; no push.
