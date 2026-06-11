---
name: project-maintain
description: Use when checking, auditing, repairing, linting, or maintaining a project-local `.llm-wiki`, especially when requirements, working-context pages, artifacts, dashboards, module indexes, Flow Records, logs, links, handoff entries, or wiki visibility may be missing, stale, orphaned, inconsistent, unsafe, or hard to find.
---

# Project Maintain

## Purpose

Maintain the structure, discoverability, consistency, and safety of a project-local `.llm-wiki`.

This skill is the project lifecycle equivalent of a wiki maintenance flow. It is inspired by general LLM Wiki maintenance ideas, but it is not an Obsidian vault workflow and does not depend on `obsidian-llm-wiki`. It understands project lifecycle artifacts such as Change Briefs, Bug Briefs, Flow Records, working-context pages, artifact registry entries, module indexes, progress dashboards, logs, and handoffs.

Use it when project knowledge exists but is hard to find, stale, partially linked, or structurally inconsistent.

## When to Use

Use when the user asks to:

- check, audit, lint, maintain, or repair a project `.llm-wiki`
- explain why a requirement, bug, plan, handoff, or dashboard item cannot be found
- find orphan requirement, bug, working-context, source, artifact, module, or handoff pages
- check whether new requirement and execution documents are visible from normal wiki entry points
- check `artifacts/index.md`, `dashboard/progress.html`, module README pages, and `log.md` consistency
- check Flow Record projection, dashboard cards, `dashboardData.flowRecords`, and lane counts
- check broken relative links, stale paths, workstation-specific absolute paths, sensitive information, or garbled generated pages
- apply narrow structural repairs to `.llm-wiki`

## When Not to Use

- Do not use to answer project knowledge questions; use `project-query`.
- Do not use to develop features or change requirements; use `project-develop`.
- Do not use to diagnose or fix product bugs; use `project-fix`.
- Do not use to mark implemented work complete; use `project-finish`.
- Do not use as a code review substitute; use `project-review`.
- Do not maintain a general Obsidian vault unless the user explicitly asks for that separate workflow.

## Owned Gates

- Wiki Root Gate
- Maintenance Scope Gate
- Visibility Chain Gate
- Flow Record Consistency Gate
- Dashboard Consistency Gate
- Safety and Local Path Gate
- Narrow Repair Gate

## Required First Check

1. Resolve the project root.
2. Resolve optional shared references from either `../references/` in the bundled top-level install or `references/` in a direct child-skill install. If `flow-record.md` or `progress-dashboard.md` is missing, continue in degraded mode using the minimum rules in this skill; report the missing deep references and keep repairs narrow and evidence-backed.
3. Confirm `.llm-wiki` exists in the project root.
4. Decide whether the request is read-only maintenance audit or approved repair.
5. Identify the target scope: whole wiki, one `flow_id`, one module, one dashboard, one page group, or one symptom.
6. Before edits, state the repair scope and keep it narrow.

## Core Process

Read as needed:

- `../references/north-star.md`
- `lifecycle-router.md`
- `flow-record.md`
- `progress-dashboard.md`
- `.llm-wiki/README.md`
- `.llm-wiki/log.md`
- `.llm-wiki/artifacts/index.md`
- `.llm-wiki/modules/index.md`
- `.llm-wiki/modules/*/README.md`
- `.llm-wiki/requirements/*.md`
- `.llm-wiki/bugs/*.md`
- `.llm-wiki/working-context/*.md`
- `.llm-wiki/handoff/*.md`
- `.llm-wiki/dashboard/progress.html`
- relevant `.llm-wiki/sources/` and `.llm-wiki/ingest/` indexes

Reference availability policy:

- Shared references are deep references, not startup requirements.
- Do not stop solely because `../references/` or local `references/` is missing.
- In degraded mode, maintenance can still audit visibility chains, links, absolute paths, log entries, Flow Record rows, and dashboard claims from available wiki files.
- Repairs in degraded mode must stay narrow and must not invent dashboard projection rules that are not visible in existing files.

Workflow:

1. Resolve the project root and `.llm-wiki` root.
2. Build a small inventory of lifecycle pages and indexes.
3. Extract visible lifecycle identifiers: `flow_id`, `parent_flow_id`, requirement IDs, bug IDs, artifact IDs, module names, and handoff paths.
4. Check the visibility chain for every target flow.
5. Check Flow Record rows against artifact registry and dashboard projection.
6. Check dashboard visible cards, `dashboardData.flowRecords`, flow summaries, and lane counts for agreement.
7. Check module entry points for active or recently changed module-related flows.
8. Check broken relative links and stale references.
9. Check for workstation-specific absolute paths and sensitive information patterns in generated wiki pages.
10. Produce a health report with Errors, Warnings, Info, and suggested repairs.
11. If the user requested repair, apply only the approved narrow repairs.
12. Record maintenance repairs in `.llm-wiki/log.md` unless the repair is explicitly dry-run only.

## Visibility Chain

For every active Change Brief or Bug Brief, check whether the flow is discoverable through the expected project wiki chain:

```text
requirements/ or bugs/
-> working-context/ when an execution plan or scoped work exists
-> artifacts/index.md
-> dashboard/progress.html when dashboard exists
-> modules/<module>/README.md when a module is affected
-> log.md
-> handoff/ when the flow is archived or handed off
```

A missing link is not always an error. Classify it by impact:

- Error: the missing link makes the flow unreachable, contradicts status, or hides a completed/blocked/active lifecycle state.
- Warning: the flow exists but is hard to find from normal navigation.
- Info: the link is optional for the current phase or intentionally deferred.

## Maintenance Modes

| Mode | Use when |
|---|---|
| `health-check` | The user asks for a general wiki health check or lint. |
| `visibility-audit` | The user says a document exists but cannot be found, or asks whether a new requirement/plan is visible in `.llm-wiki`. |
| `consistency-repair` | The user asks to fix missing indexes, backlinks, logs, artifacts, or dashboard references. |
| `dashboard-audit` | The user asks why the progress dashboard is stale, inconsistent, or missing cards. |
| `safety-audit` | The user asks to check secrets, absolute paths, sensitive content, copied raw material, or garbled pages. |

## Repair Rules

Allowed narrow repairs:

- Add missing artifact registry entries for existing requirement, bug, working-context, report, dashboard, or handoff pages.
- Add missing module README backlinks for affected active or recent flows.
- Add a concise `.llm-wiki/log.md` maintenance entry.
- Fix broken wiki-relative links when the target is unambiguous.
- Add missing dashboard Flow Record cards only when evidence exists in Change Brief, Bug Brief, working-context, or handoff pages.
- Downgrade unsupported dashboard claims to evidence-backed status.

Disallowed repairs:

- Do not modify production code, tests, configuration, database schema, or runtime behavior.
- Do not change requirement scope, acceptance criteria, or business decisions without routing to `project-develop`.
- Do not change bug diagnosis or fix strategy without routing to `project-fix`.
- Do not mark testing, archive, or release done without verification or accepted limitation through `project-finish`.
- Do not promote candidate source material into an active requirement automatically.
- Do not rewrite large groups of wiki pages without explicit confirmation.
- Do not remove sensitive-looking content unless the user approves the exact redaction or replacement.

## Finding Levels

- Error: Broken, dangerous, contradictory, or likely to mislead future project work.
- Warning: Missing, stale, incomplete, or hard-to-find structure that should be repaired soon.
- Info: Useful observation, optional improvement, or intentionally deferred link.

## Output Format

For audits, return:

```markdown
# Project Wiki Health Report - YYYY-MM-DD

## Summary

## Errors

## Warnings

## Info

## Orphan Pages

## Missing Backlinks

## Flow Record Consistency

## Dashboard Consistency

## Safety Findings

## Suggested Repairs

## Repair Scope
```

For repairs, return:

```markdown
## Maintenance Result

- mode:
- project_root:
- wiki_root:
- repaired_pages:
- unchanged_findings:
- downgraded_claims:
- skipped_repairs:
- verification:
- next_route:
```

## Routing Handoff

If maintenance discovers work that belongs to another lifecycle stage, route instead of silently repairing it:

```markdown
## Context Handoff

- lifecycle_session:
- user_intent:
- affected_flow_id:
- affected_module:
- maintenance_finding:
- evidence:
- recommended_stage:
- constraints:
```

Recommended routes:

- Missing requirement or changed acceptance criteria -> `project-develop`
- Bug evidence or failed verification -> `project-fix`
- Implemented work needing status sync or handoff -> `project-finish`
- Merge-readiness or code risk -> `project-review`
- Source material missing from wiki -> `project-ingest`

## Boundaries

- `.llm-wiki` is a team-shared project knowledge base. Prefer project-relative and wiki-relative paths.
- Do not persist workstation-specific absolute paths such as `C:\Users\...`, `D:\workspace\...`, `/Users/...`, or `/home/...` in durable wiki pages.
- Do not copy secrets, tokens, private keys, passwords, or long original source material into wiki maintenance reports.
- Keep repairs small and explain what was intentionally left unchanged.
- Treat dashboard as an evidence-backed projection, not the source of truth.

## Common Mistakes

- Treating "file exists" as enough when the file is not discoverable from artifact, module, dashboard, or log entry points.
- Updating the dashboard but forgetting the artifact registry or module README.
- Marking a Flow Record lane done because a card exists, without verification evidence.
- Repairing business meaning during a structural maintenance pass.
- Running a full wiki rewrite when one backlink or log entry would solve the visibility problem.
- Applying Obsidian vault assumptions directly to a project `.llm-wiki`; this skill only uses LLM Wiki maintenance ideas as reference.
