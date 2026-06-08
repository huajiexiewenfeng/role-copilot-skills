---
name: project-finish
description: Use when finishing verified project work, syncing actual changes back to LLM Wiki, updating requirement or bug status, recording verification, and preparing handoff.
---

# Project Finish

## Purpose

Finish project work by syncing verified implementation knowledge back into `.llm-wiki`, artifact registry, and progress dashboard when enabled, then preparing a concise handoff.

This skill does not perform broad code review. Use `project-review` for review readiness and drift findings.

## When to Use

Use when the user says:

- finish, done, sync, update status, prepare handoff
- work is implemented and verification is available or limited
- update wiki, requirement status, bug status, artifact registry, or progress dashboard
- summarize what changed and what remains risky

## When Not to Use

- Do not use before implementation or verification exists.
- Do not use for initial project setup; use `project-init`.
- Do not use for bug diagnosis; use `project-fix`.
- Do not use as a substitute for findings-first review.

## Owned Gates

- Verification Gate
- Knowledge Sync Gate
- Artifact Sync Gate
- Progress Dashboard Sync Gate

## Required First Check

1. Resolve project root.
2. Verify `../references/` exists and contains `flow-record.md`, `progress-dashboard.md`, and `templates.md`. If missing, stop and tell the user the child skill install is incomplete; install the top-level `project-develop-copilot` package or restore the shared `references/` directory before continuing lifecycle work.
3. Identify active Change Brief, Bug Brief, or working-context.
4. Check verification evidence or accepted limitation.
5. Inspect changed files.
6. Decide affected wiki pages, artifacts, dashboard sections, and handoff path.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/flow-record.md`
- `../references/session-digest.md`
- `../references/progress-dashboard.md`
- `../references/progress-dashboard-template.html`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md`
- `../references/templates.md`

Workflow:

1. Resolve project root and lifecycle session.
2. Confirm verification evidence: tests, compile, lint, manual verification, or explicit accepted limitation.
3. Use verification-before-completion when available before claiming completion.
4. Summarize actual code and behavior changes.
5. Map changed files to affected wiki pages.
6. Update only affected `.llm-wiki` pages.
7. Mark related working-context, Change Brief, or Bug Brief Flow Record steps as verified, done, blocked, or skipped using evidence-backed step rules.
8. When finishing work linked to a Session Digest, update the related requirement, bug, or Flow Record first. If digest `candidate` items are now confirmed or rejected by implementation evidence, record that outcome in the digest or `.llm-wiki/log.md` when useful.
9. Record verification limitation and residual risk when verification was partial or blocked.
10. Register important specs, plans, reports, verification notes, and dashboard as artifacts.
11. If dashboard is registered or `.llm-wiki/dashboard/progress.html` exists, update only evidence-backed dashboard data/sections.
12. If dashboard is expected but missing, recreate it from `../references/progress-dashboard-template.html` and mark status conservatively.
13. Prepare or update the handoff in `.llm-wiki/handoff/<flow-id>-handoff.md` unless the project already has a more specific handoff filename for that same `flow_id`.
14. Report implementation summary, verification, sync updates, residual risk, and next action.

## Mode / Entry Selection

| Mode | Use when |
|---|---|
| `verified-finish` | verification passed and sync can mark work verified/done |
| `partial-finish` | verification is partial or blocked but user accepts limitation |
| `status-sync` | user wants wiki/artifact/dashboard state updated from known evidence |
| `handoff-only` | user wants summary without changing files |

## Inputs

- active Change Brief, Bug Brief, or working-context
- changed files or git diff
- verification command output or manual verification notes
- related Session Digest when historical session context influenced the work
- artifact paths
- dashboard path when enabled

## Outputs

Report:

```text
Implementation summary:
Verification:
Wiki updates:
Artifact updates:
Dashboard updates:
Session Digest updates:
Residual risk:
Next action:
```

Changed file mapping:

```text
Changed file:
Module:
Related requirement:
Related bug:
Related source proxy:
Wiki pages to update:
Reason:
```

Flow Record update mapping:

```text
flow_id:
development:
  status:
  evidence:
testing:
  status:
  evidence:
archive:
  status:
  evidence:
unsupported_done_claims_downgraded:
```

Rules:

- `development` can be `done` only when changed files or implementation evidence are recorded.
- `testing` can be `done` only when verification passed or an explicit accepted limitation is recorded.
- `archive` can be `done` only when a handoff, done note, release/deploy note, or accepted closure exists. Project handoffs belong under `.llm-wiki/handoff/`, not `.llm-wiki/working-context/`.
- Partial verification should mark `testing` as `blocked`, `active`, or `done with limitation` in notes, not silently complete.

## Handoff Path Rule

Default handoff path:

```text
.llm-wiki/handoff/<flow-id>-handoff.md
```

Use a descriptive suffix only when it preserves the same `flow_id`, for example:

```text
.llm-wiki/handoff/<flow-id>-implementation-handoff.md
```

Do not store final handoff artifacts in `.llm-wiki/working-context/`. Working context is for scoped planning and execution notes; handoff is the archive/continuation entry point. After moving or creating handoff, update Flow Record `archive` evidence, artifact registry, and dashboard links to the `.llm-wiki/handoff/` path.

## Context Handoff

Accept router or stage handoff with lifecycle session, active sources, scope, artifacts, verification notes, and constraints.

## Return Handoff

Return:

```markdown
## Return Handoff

- stage_or_bridge_used: project-finish
- result_summary:
- changed_assumptions:
- recommended_scope_changes:
- artifacts:
- verification_notes:
- lifecycle_updates_needed:
- next_gate:
```

## Boundaries

- Do not claim work is complete without verification evidence or an explicit limitation.
- Do not write large implementation narratives into `.llm-wiki`.
- Do not update unrelated modules or sources.
- Do not update dashboard without evidence links.
- Do not mark Flow Record `testing` or `archive` done without verification or handoff evidence.
- Do not leave dashboard or artifact registry links pointing at old handoff paths after moving a handoff.
- Do not rewrite dashboard layout when a small `dashboardData` or marked-section update is enough.
- Do not hide residual risk when tests could not run.

## Common Mistakes

- Marking done when verification is partial.
- Updating every wiki page instead of affected pages.
- Writing final handoff into `.llm-wiki/working-context/` instead of `.llm-wiki/handoff/`.
- Updating Flow Record without updating artifact registry and dashboard links to the same evidence path.
- Forgetting artifact registry entries for plans/reports/dashboards.
- Letting dashboard become the only status record.
- Skipping review when the user asked for merge readiness.
