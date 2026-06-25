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
- Finish Sync Gate

## Required First Check

1. Resolve project root.
2. Resolve optional shared references from `../references/` or local `references/`. If `flow-record.md`, `progress-dashboard.md`, or `templates.md` is missing, continue in degraded mode using the minimum rules in this skill; report the missing deep references and update only evidence-backed wiki state.
3. Identify active Change Brief, Bug Brief, or working-context.
4. Check verification evidence, provenance, raw output, and whether any accepted limitation has a non-agent acceptor.
5. Inspect changed files, including whether production code and tests/mocks changed together.
6. Decide whether the Verification Gate test-integrity sub-check is required before updating testing status.
7. Decide affected wiki pages, artifacts, dashboard sections, and handoff path.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/flow-record.md`
- `../references/session-digest.md`
- `../references/progress-dashboard.md`
- `../references/progress-dashboard-template.html`
- `../references/base-graph.md`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md`
- `../references/templates.md`

Reference availability policy:

- Shared references are deep references, not startup requirements.
- Do not stop solely because `../references/` is missing.
- In degraded mode, finish sync may update Change Brief, Bug Brief, Flow Record, log, and handoff with compact Markdown, but must not generate unsupported dashboard claims.
- Dashboard updates require either the dashboard reference/template or a clear existing dashboard data contract.

Workflow:

1. Resolve project root and lifecycle session.
2. Confirm verification evidence: tests, compile, lint, manual verification, or explicit accepted limitation.
   - Record verification provenance: executor, command/check, raw output reference, exit code, scope, authority, trust level, limitation acceptor, and residual risk.
   - Treat agent-written summaries as supporting notes, not as independent authority.
   - An agent may propose a limitation, but must not self-accept it. `accepted limitation` requires user, project owner, CI policy, or external reviewer acceptance.
3. Use verification-before-completion when available before claiming completion.
4. Summarize actual code and behavior changes.
5. Map changed files to affected wiki pages.
6. If production code and tests/mocks/fixtures/expected values changed together, run the Verification Gate test-integrity sub-check before marking testing done.
7. Update only affected `.llm-wiki` pages.
8. Update the related working-context, Change Brief, or Bug Brief Flow Record first. Flow Record is the lifecycle status authority; dashboard, handoff, and log entries must be generated from it or linked back to it.
9. Mark Flow Record steps as verified, done, blocked, or skipped using evidence-backed step rules and trust level.
10. When finishing work linked to a Session Digest, update related requirement, bug, or Flow Record only if selected digest items were explicitly promoted into that lifecycle object. If recall-context items are now confirmed or rejected by implementation evidence, record that outcome in the digest or `.llm-wiki/log.md` when useful without silently changing project truth.
11. Record verification limitation and residual risk when verification was partial or blocked.
12. Register important specs, plans, reports, verification notes, handoffs, and dashboard as artifacts.
13. If dashboard is registered or `.llm-wiki/dashboard/progress.html` exists, rebuild or refresh only evidence-backed dashboard data/sections from Flow Record plus artifact registry evidence.
14. If dashboard is expected but missing, recreate it from `../references/progress-dashboard-template.html` and mark status conservatively.
15. Prepare or update the handoff in `.llm-wiki/handoff/<flow-id>-handoff.md` unless the project already has a more specific handoff filename for that same `flow_id`; treat handoff as archive/continuation summary, not as the status authority.
   - If finishing work changed service responsibility, architecture overview, cross-service ownership, or Base catalog/overview expectations, generate a Base Graph Handoff or update suggestion.
   - Do not write Base tracked files from a business-project session. Only write Base files when cwd is the Base Graph repo with `graph_role: base` or when the user explicitly enters Base write mode from `base-graph.md`.
16. Write a concise `.llm-wiki/log.md` audit entry when sync changes durable state.
17. Report implementation summary, verification, sync updates, residual risk, and next action.

## LLM Wiki Doctor Finish Check

When a repo contains `.llm-wiki/tools/llm_wiki_doctor.py`, run it during project-finish after affected wiki pages are synced and before preparing handoff:

```text
python .llm-wiki/tools/llm_wiki_doctor.py --root . --changed --format text --fail-on error
```

Record the command, exit code, WARN count, ERROR count, and unresolved WARN rationale in the handoff. Do not use `--flow`; associate findings with the current flow in the handoff text. WARN findings are visible Phase 1 measurement output and do not fail project-finish unless policy explicitly promotes a check to ERROR.
## Mode / Entry Selection

| Mode | Use when |
|---|---|
| `verified-finish` | verification passed with usable provenance and sync can mark work verified/done |
| `partial-finish` | verification is partial or blocked and the user/project owner/reviewer accepts limitation |
| `status-sync` | user wants wiki/artifact/dashboard state updated from known evidence |
| `handoff-only` | user wants summary without changing files |

## Inputs

- active Change Brief, Bug Brief, or working-context
- changed files or git diff
- verification command output or manual verification notes
- verification provenance: executor, raw output reference, exit code, scope, authority, trust level, limitation acceptor
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
  trust_level:
  limitation_acceptor:
archive:
  status:
  evidence:
unsupported_done_claims_downgraded:
```

Rules:

- `development` can be `done` only when changed files or implementation evidence are recorded.
- `testing` can be `done` only when verification passed with provenance or an explicit accepted limitation is recorded with a non-agent acceptor.
- `testing` should use a conservative note such as `passed-agent-local`, `needs-review`, `blocked`, or `done with user-accepted limitation` when verification authority is not CI-backed/reviewer-backed.
- `archive` can be `done` only when a handoff, done note, release/deploy note, or accepted closure exists. Project handoffs belong under `.llm-wiki/handoff/`, not `.llm-wiki/working-context/`.
- Partial verification should mark `testing` as `blocked`, `active`, or `done with limitation` in notes, not silently complete.
- If tests, mocks, fixtures, snapshots, or expected values changed with production code, do not mark testing done until the Verification Gate records assertion strength and over-mocking risk.
- Dashboard, handoff, and log entries must not introduce stronger status than the Flow Record supports.

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

## Base Graph Handoff

When Base Graph overview or catalog should change but the current session is a business-project session, generate this handoff instead of editing Base tracked files:

```markdown
## Base Graph Handoff

- source_project:
- reason:
- affected_projects:
- suggested_catalog_changes:
- suggested_overview_changes:
- evidence:
- verification_status:
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
- Do not self-accept a limitation. Agent-proposed limitations stay proposed until accepted by the user, project owner, CI policy, or external reviewer.
- Do not promote agent-local verification to final verified/pre-merge confidence without raw output provenance plus CI, reviewer, or explicit user acceptance.
- Do not write large implementation narratives into `.llm-wiki`.
- Do not update unrelated modules or sources.
- Do not update dashboard without evidence links.
- Do not update dashboard status before updating the matching Flow Record status.
- Do not mark Flow Record `testing` or `archive` done without verification or handoff evidence.
- Do not leave dashboard or artifact registry links pointing at old handoff paths after moving a handoff.
- Do not rewrite dashboard layout when a small `dashboardData` or marked-section update is enough.
- Do not hide residual risk when tests could not run.
- Do not weaken tests, mocks, fixtures, snapshots, or expected values to bypass a failing verification command without recording the Verification Gate test-integrity risk.

## Common Mistakes

- Marking done when verification is partial.
- Treating an agent-written verification note as an external audit.
- Writing `accepted limitation` without recording who accepted it.
- Marking tests done after changing mocks or expectations without checking test integrity.
- Updating every wiki page instead of affected pages.
- Writing final handoff into `.llm-wiki/working-context/` instead of `.llm-wiki/handoff/`.
- Updating Flow Record without updating artifact registry and dashboard links to the same evidence path.
- Forgetting artifact registry entries for plans/reports/dashboards.
- Letting dashboard become the only status record.
- Skipping review when the user asked for merge readiness.
