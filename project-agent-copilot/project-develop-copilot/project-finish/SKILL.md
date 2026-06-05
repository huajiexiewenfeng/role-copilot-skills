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
2. Identify active Change Brief, Bug Brief, or working-context.
3. Check verification evidence or accepted limitation.
4. Inspect changed files.
5. Decide affected wiki pages, artifacts, and dashboard sections.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
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
7. Mark related working-context and Change Brief Flow Record steps as verified, done, blocked, or skipped.
8. Record verification limitation and residual risk when verification was partial or blocked.
9. Register important specs, plans, reports, verification notes, and dashboard as artifacts.
10. If dashboard is registered or `.llm-wiki/dashboard/progress.html` exists, update only evidence-backed dashboard data/sections.
11. If dashboard is expected but missing, recreate it from `../references/progress-dashboard-template.html` and mark status conservatively.
12. Report implementation summary, verification, sync updates, residual risk, and next action.

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
- Do not rewrite dashboard layout when a small `dashboardData` or marked-section update is enough.
- Do not hide residual risk when tests could not run.

## Common Mistakes

- Marking done when verification is partial.
- Updating every wiki page instead of affected pages.
- Forgetting artifact registry entries for plans/reports/dashboards.
- Letting dashboard become the only status record.
- Skipping review when the user asked for merge readiness.
