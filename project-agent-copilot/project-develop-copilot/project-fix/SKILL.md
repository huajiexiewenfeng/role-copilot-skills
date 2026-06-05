---
name: project-fix
description: Use when diagnosing or fixing a project bug, error, failed test, regression, incident, log symptom, or unexpected behavior with scoped project context and LLM Wiki bug summaries.
---

# Project Fix

## Purpose

Diagnose and fix bugs through scoped context, evidence, reproduction, implementation, verification, and bug knowledge sync.

This skill owns the bug stage of Project Develop Copilot. It does not own top-level routing, final completion claims, or broad review.

## When to Use

Use when the user reports or wants to fix:

- bug, error, exception, failed test, regression, incident, runtime symptom, unexpected behavior, or log evidence
- suspected bug in a scoped module or service
- bug work that may need systematic debugging, TDD, or verification bridges

## When Not to Use

- Do not use for feature requests without a bug symptom; use `project-develop`.
- Do not use for lightweight explanation of a log unless the user does not want lifecycle state.
- Do not use for final sync after a fix is complete; use `project-finish`.
- Do not use for merge-readiness review; use `project-review`.

## Owned Gates

- Context Enrichment Gate
- Bug Evidence Gate
- Context Lock Gate
- External Skill Bridge Gate
- Verification Gate before fix completion claims

## Required First Check

1. Resolve project root.
2. Create or resume Bug Brief.
3. Capture or ingest external bug source.
4. Identify active, read-only, candidate, and excluded scopes.
5. Run Bug Evidence Gate before broad diagnosis or edits.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/bug-brief.md`
- `../references/flow-record.md`
- `../references/scoped-working-context.md`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md`
- `../references/templates.md`

Workflow:

1. Resolve project root and Bug Brief.
2. Capture source, symptom, expected behavior, evidence, and likely scope.
3. Create or update the Bug Brief Flow Record with source evidence.
4. Run Context Enrichment Gate.
5. Reproduce the issue or state why reproduction is not currently possible.
6. Bridge to systematic-debugging only after evidence and scoped context are captured.
7. Diagnose likely cause before changing code and update the Flow Record `design` step when diagnosis evidence exists.
8. Use test-driven-development for regression coverage when feasible.
9. Record or confirm the fix plan and update the Flow Record `plan` step before edits.
10. Run Context Lock Gate before edits.
11. If the fix needs candidate or excluded scope, run scope escalation before editing.
12. Fix only active scopes unless escalation is justified.
13. Verify the fix or record limitation.
14. Update Bug Brief, Flow Record, and working-context after verification.
15. Return diagnosis, verification, Flow Record updates, residual risk, and next gate.

## Mode / Entry Selection

| Mode | Use when |
|---|---|
| `evidence-intake` | symptom or log exists but scope/reproduction is unclear |
| `reproduction` | issue needs a command, test, or manual steps |
| `diagnosis` | evidence exists and likely cause must be found |
| `fix` | scope is locked and user asked to fix |
| `verification` | fix exists and result must be checked |

## Inputs

- Bug Brief or bug id
- log, error, failed test, incident report, or user description
- project root
- active and candidate scopes
- recent changes or git diff when relevant

## Outputs

Final report:

```text
Diagnosis:
Fix:
Files changed:
Scope escalation:
Regression coverage:
Verification:
Bug Brief updates:
Flow Record updates:
Artifacts:
Residual risk:
Next action:
```

## Context Handoff

Before systematic-debugging, TDD, or other external bridges, provide:

```markdown
## Context Handoff

- lifecycle_session:
- user_intent:
- active_sources:
- active_scope:
- read_only_scope:
- candidate_scope:
- excluded_scope:
- current_gate:
- requested_stage_or_bridge:
- constraints:
```

## Return Handoff

After debugging, fixing, or verification, return:

```markdown
## Return Handoff

- stage_or_bridge_used: project-fix
- result_summary:
- changed_assumptions:
- recommended_scope_changes:
- artifacts:
- verification_notes:
- lifecycle_updates_needed:
- next_gate:
```

## Boundaries

- Do not patch randomly before diagnosis.
- Do not expand write scope without evidence or user confirmation.
- Do not let systematic-debugging own project scope.
- Do not claim fixed without verification or explicit limitation.
- Do not copy sensitive raw logs into `.llm-wiki`.

## Common Mistakes

- Jumping straight into external debugging without Bug Brief.
- Editing candidate scope before escalation.
- Treating reproduction-blocked as reproduced.
- Forgetting residual risk when verification cannot run.
- Updating dashboard as fixed before verification evidence exists.
