---
name: project-maintain
description: Use when checking, auditing, repairing, linting, or maintaining a project-local `.llm-wiki` or Base Graph Project Graph fleet, especially when requirements, working-context pages, Project Graph edges/candidates, cross-project refs, Base Graph catalog/registry links, artifacts, dashboards, module indexes, Flow Records, logs, links, handoff entries, or wiki visibility may be missing, stale, orphaned, inconsistent, unsafe, or hard to find.
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
- audit Project Graph edges, candidates, proposals, and cross-ref pins for consistency; delegate candidate scanning, proposal generation, and confirmed edge writes to the explicit Project Graph skills
- audit every project registered in a Base Graph for Project Graph completeness, missing directories, broken edges, unresolved pins, registry problems, and cross-project readiness
- apply narrow structural repairs to `.llm-wiki`

## When Not to Use

- Do not use to answer project knowledge questions; use `project-query`.
- Do not use to develop features or change requirements; use `project-develop`.
- Do not use to diagnose or fix product bugs; use `project-fix`.
- Do not use to mark implemented work complete; use `project-finish`.
- Do not use as a code review substitute; use `project-review`.
- Do not maintain a general Obsidian vault unless the user explicitly asks for that separate workflow.

## Owned Gates

- Context Recovery Gate
- Finish Sync Gate when maintenance repairs indexes, artifacts, logs, or dashboard projection data
- Review & Wiki Integrity Gate

## Initialization Gate

Run after resolving the project root and before auditing or repairing project-local wiki state.

- `wiki_required: true`
- `on_missing_wiki: route project-init`
- `pending_primary_stage: project-maintain`
- Preserve the user's original audit or repair request as `pending_intent`.
- If `<project_root>/.llm-wiki/` is absent, stop and return a Context Handoff to `project-init`; resume only after the router receives initialization readiness and a supported next gate.
- Do not create a partial `.llm-wiki/`, maintenance template, graph file, dashboard file, or repair log inside this child as a substitute for initialization.

On the missing-wiki branch, emit this minimal handoff:

```text
bootstrap_handoff:
  project_root: <resolved project root>
  pending_intent: <preserved user request and repair boundary>
  pending_primary_stage: project-maintain
  requested_stage_or_bridge: project-init
  bootstrap_mode: automatic-minimal
  current_gate: Initialization Gate
```

## Required First Check

1. Resolve the project root.
2. Run the Initialization Gate before resolving child references or maintenance state.
3. Resolve optional shared references from either `../references/` in the bundled top-level install or `references/` in a direct child-skill install. If `flow-record.md` or `progress-dashboard.md` is missing, continue in degraded mode using the minimum rules in this skill; report the missing deep references and keep repairs narrow and evidence-backed.
4. Confirm `.llm-wiki` exists in the project root.
5. Decide whether the request is read-only maintenance audit or approved repair.
6. Identify the target scope: whole wiki, one `flow_id`, one module, one dashboard, one page group, or one symptom.
7. Before edits, state the repair scope and keep it narrow.
8. For Base Graph fleet audits, resolve the Base Graph root, read its catalog and local registry, and treat all project repositories as read-only unless the user explicitly approves a per-project repair.

## Core Process

Read as needed:

- `../references/north-star.md`
- `lifecycle-router.md`
- `flow-record.md`
- `progress-dashboard.md`
- `project-graph.md`
- `cross-project-refs.md`
- `base-graph.md`
- `.llm-wiki/README.md`
- `.llm-wiki/log.md`
- `.llm-wiki/base-graph/manifest.json`
- `.llm-wiki/base-graph/project-catalog.md`
- `.llm-wiki/base-graph/overview.md`
- `.llm-wiki/artifacts/index.md`
- `.llm-wiki/cross-refs/index.md`
- `.llm-wiki/cross-refs/registry.local.json`
- `.llm-wiki/registry.local.json`
- `.llm-wiki/project-graph/edges.md`
- `.llm-wiki/project-graph/candidates.md`
- `.llm-wiki/project-graph/scan-report.md`
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
5. Check Flow Record rows against artifact registry and dashboard projection using the authority order: current user/code/verification evidence -> Flow Record -> artifact registry -> log -> dashboard/handoff projection.
6. Check dashboard visible cards, `dashboardData.flowRecords`, flow summaries, and lane counts for agreement.
7. Check module entry points for active or recently changed module-related flows.
8. Check broken relative links and stale references.
9. Check Project Graph and cross-project refs structure, registry ignore status, pin/edge/candidate consistency, derived staleness, and resolvable remote anchors when registry mappings exist.
10. Check for workstation-specific absolute paths and sensitive information patterns in generated wiki pages.
11. Produce a health report with Errors, Warnings, Info, and suggested repairs.
12. If the user requested repair, apply only the approved narrow repairs.
13. Record maintenance repairs in `.llm-wiki/log.md` unless the repair is explicitly dry-run only.

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
| `graph-register` | Legacy alias; delegate manual/confirmed edge writing to `project-graph-human-edge`. |
| `graph-scan` | Legacy alias; delegate candidate discovery to `project-graph-candidates-scan`. |
| `project-graph-register` | Legacy alias; delegate to `project-graph-human-edge`. |
| `project-graph-audit` | The user asks to check Project Graph edges/candidates, cross-project refs, remote anchors, registry mappings, cross-service links, or stale external contract verification. |
| `base-graph-audit` | The user asks to check every project registered in a Base Graph, audit multi-project graph completeness, or verify whether project graphs can route across repositories. |
| `project-graph-audit-all` | Alias for `base-graph-audit`. |
| `wiki-prune` | Doctor reports stale, unreachable, unverifiable, low-value mirror, or unresolved dirty capture findings and the user wants a re-verify/prune plan. |

### Wiki Prune Mode

Use `wiki-prune` when LLM Wiki Doctor reports `freshness-expired`, `stale-source-anchor`, `coarse-stale-source-anchor`, `missing-verified-commit`, `unreachable-verified-commit`, `unverifiable-anchor`, `unresolved-dirty-capture`, low-value mirror content, or repeated placeholder context.

Produce a re-verification list, downgrade stale evidence to clue-only, and suggest archive or prune actions. Do not automatically delete why/intent/dead-end knowledge. Do not rewrite semantic facts such as module responsibility, requirement scope, bug root cause, or Project Graph contracts without current source evidence and explicit approval.

## Delegated Project Graph Write Modes

`project-maintain` audits and repairs Project Graph structure, but it no longer owns the normal write workflow for new relationships.

Delegate explicit graph maintenance requests as follows:

- Candidate discovery or `graph-scan` -> `project-graph-candidates-scan`.
- Base Graph/source-backed proposal generation or `auto-edge` -> `project-graph-auto-edge`.
- Human confirmation, rejection, manual edge registration, or cross-ref pin writing -> `project-graph-human-edge`.

`project-maintain` may still report missing pins, duplicate fingerprints, stale candidates, unsupported statuses, broken anchors, registry conflicts, and Base Graph readiness problems. It must not write new confirmed edges unless the user is explicitly asking for a maintenance repair to an already confirmed edge and the row identity is unambiguous.

## Project Graph Audit

Audit `.llm-wiki/project-graph/` and `.llm-wiki/cross-refs/` when they exist, when cross-service work is active, or when the user asks about Feign, MQTT, HTTP, RPC, shared DB, shared config, upstream/downstream services, or external contracts.

Check:

- `.llm-wiki/project-graph/edges.md`, `.llm-wiki/project-graph/candidates.md`, `.llm-wiki/project-graph/proposals.md`, `.llm-wiki/project-graph/scan-report.md`, and `.llm-wiki/cross-refs/index.md` exist when cross-project relationships are used.
- `.gitignore` contains `.llm-wiki/registry.local.json`, `.llm-wiki/cross-refs/registry.local.json`, and `.llm-wiki/project-graph/scan-state.local.json`.
- Preferred and legacy registry files are not tracked by git.
- Preferred registry `.llm-wiki/registry.local.json` wins over legacy `.llm-wiki/cross-refs/registry.local.json`.
- If preferred and legacy registries conflict for a project id, report the conflict and do not merge silently.
- If Base Graph is discoverable, check whether edge project ids appear in Base `base-graph/project-catalog.md`; missing ids produce a Base Handoff/update suggestion, not an automatic Base edit.
- Base Graph `.llm-wiki/registry.local.json` may be written only as local resolver configuration after user confirmation; Base tracked files remain read-only from a business-project session.
- `cross-refs/index.md` is pin-only. Report `contract_summary`, `verification_status`, `last_verified`, `remote_project`, or `remote_anchor` as redundant fact fields.
- Every pin `edge_id` resolves to a row in `project-graph/edges.md`.
- Edge `fingerprint` values are unique.
- Edge `from_project` and `to_project` are logical ids only and are never `unknown`.
- Edge anchors are not local absolute paths, do not start with `.llm-wiki/`, and do not escape with `../`.
- Edge `verification_status` is one of `unverified`, `source-verified`, or `runtime-verified`; never `stale`. Proposal `verification_status` is proposed evidence metadata until human acceptance writes an edge.
- `last_verified` is present and parseable when an edge uses `source-verified` or `runtime-verified`.
- Derived staleness is `fresh`, `expired`, or `unknown` using the default 30 day threshold from `cross-project-refs.md`.
- If a registry mapping exists, its `path` exists, `wiki` is relative, has no trailing slash, and resolved remote anchors remain inside the remote project root.
- If a registry mapping exists and a resolved edge anchor is missing, report it; do not scan the whole remote project by keyword.
- Candidate `candidate_fingerprint` values are unique.
- Candidate and proposal `source` are `scan` or `manual`; confirmed edge `source` is `auto` or `manual`.
- `remote_project = unknown` candidates are not promoted to edges.
- `promoted` candidates have an `edge_id` that resolves. `proposed` candidates have a reviewable unresolved proposal and an empty `edge_id`.
- `pending` candidates with `source = scan` and `last_seen` older than `default_candidate_pending_days` should be archived, not silently kept.
- `pending` candidates with `source = manual` are exempt from automatic pending-timeout archival.

Finding levels:

- Error: pin layer stores fact fields, dangling `edge_id`, duplicate edge fingerprint, edge project is `unknown`, registry is tracked, local path leaked into committed files, anchor is absolute or escapes, or `verification_status` uses unsupported values such as `stale`.
- Warning: `last_verified` is expired or unknown, registry path is missing, remote anchor cannot be resolved, `.gitignore` is missing a local-only line, legacy registry needs migration, or a `pending` scan-origin candidate exceeded `default_candidate_pending_days`.
- Info: no Project Graph exists yet, registry is absent while no active edge needs it, or an edge is intentionally `draft`.

## Base Graph Fleet Audit

Use `base-graph-audit` from a Base Graph repository or when a Base Graph is discoverable through `LLM_WIKI_BASE_GRAPH_PATH` or `~/.llm-wiki/base-graph.local.json`.

Purpose:

- Check whether every project registered in the Base Graph has enough Project Graph structure to participate in cross-project query, bug, and requirement routing.
- Identify missing or malformed local graph files before a `project-query` or `project-fix` session depends on them.
- Verify cross-project readiness without promoting candidates or writing remote project files.

Process:

1. Resolve the Base Graph root and confirm `.llm-wiki/base-graph/manifest.json` has `graph_role: "base"` when the manifest exists.
2. Read `.llm-wiki/base-graph/project-catalog.md`, `.llm-wiki/base-graph/overview.md`, and `.llm-wiki/registry.local.json`.
3. Build the project set from the Base catalog and local registry. If they disagree, report catalog-only and registry-only projects separately.
4. For each resolvable project path, run the Project Graph Audit checks against that project's `.llm-wiki` without changing files.
5. For unresolved project paths, report the project as not locally auditable and include the missing resolver reason.
6. Check that edge `from_project` and `to_project` ids are present in the Base catalog or registry.
7. Check that project-local pins can resolve to local edges and that edge remote ids can resolve through the Base registry.
8. Check whether required graph files are missing for projects that have cross-project candidates, pins, or active Base overview flows.
9. Check source-backed scoped context readiness by looking for project-local source or working-context pages referenced by graph anchors; do not infer source coverage from code search alone.
10. Produce a matrix summary plus per-project errors, warnings, and repair suggestions.

Base fleet finding levels:

- Error: project is registered but path is unresolvable, pin points to a missing edge, edge references a project id absent from Base catalog/registry, local registry is tracked, committed graph files leak local absolute paths, or graph files contain unsupported verification states.
- Warning: graph templates are missing for a project that participates in Base candidate flows, `last_verified` is expired or unknown, remote anchor cannot be resolved through registry, source-backed scoped context appears missing for an active cross-project edge, or catalog and registry project sets disagree.
- Info: project has no Project Graph yet and no Base overview flow depends on it, edge is intentionally `draft`, or project is cataloged but intentionally unavailable on this workstation.

Base fleet repairs:

- Default to read-only.
- Do not write business-project files during a Base fleet audit unless the user explicitly approves repair for named projects.
- Allowed approved repairs are the same narrow Project Graph structural repairs listed below, applied per named project.
- Do not edit Base tracked files from a business-project session. From a Base Graph session, suggest Base catalog updates but still ask before changing tracked Base files.

## Repair Rules

Allowed narrow repairs:

- Add missing artifact registry entries for existing requirement, bug, working-context, report, dashboard, or handoff pages.
- Add missing module README backlinks for affected active or recent flows.
- Add a concise `.llm-wiki/log.md` maintenance entry.
- Fix broken wiki-relative links when the target is unambiguous.
- Add missing dashboard Flow Record cards only when evidence exists in Change Brief, Bug Brief, working-context, or handoff pages.
- Downgrade unsupported dashboard claims to evidence-backed status.
- Rebuild dashboard projection from Flow Record plus artifact registry evidence when dashboard drift is the only issue.
- Repair artifact registry path/status rows when current files prove the registry is stale.
- Create missing `.llm-wiki/project-graph/edges.md`, `.llm-wiki/project-graph/candidates.md`, `.llm-wiki/project-graph/scan-report.md`, and `.llm-wiki/cross-refs/index.md` empty templates.
- Add `.llm-wiki/registry.local.json`, `.llm-wiki/cross-refs/registry.local.json`, and `.llm-wiki/project-graph/scan-state.local.json` to `.gitignore` exactly once.
- Copy legacy registry to preferred registry only in approved repair mode and only when the preferred registry is absent; do not delete the legacy file.
- Rewrite malformed anchors only when the intended target is unambiguous.
- Replace unsupported `verification_status: stale` with the prior verified level only when evidence in the row or notes makes that level clear; otherwise downgrade to `draft` and report the uncertainty.
- Archive stale `pending` scan-origin candidates by moving them from `.llm-wiki/project-graph/candidates.md` to `.llm-wiki/project-graph/scan-report.md` `Archived Candidates` with reason `pending-timeout-90d`; do not archive manual candidates.

Disallowed repairs:

- Do not modify production code, tests, configuration, database schema, or runtime behavior.
- Do not change requirement scope, acceptance criteria, or business decisions without routing to `project-develop`.
- Do not change bug diagnosis or fix strategy without routing to `project-fix`.
- Do not mark testing, archive, or release done without verification or accepted limitation through `project-finish`.
- Do not change Flow Record lifecycle status merely to match dashboard, handoff, or log text.
- Do not promote candidate source material into an active requirement automatically.
- Do not rewrite large groups of wiki pages without explicit confirmation.
- Do not remove sensitive-looking content unless the user approves the exact redaction or replacement.
- Do not write to external project wiki, source, config, registry, or reverse cross-refs.
- Do not create or edit `registry.local.json` unless the user confirms the local path mapping.
- Do not write `source-verified` or `wiki-checked` for a manually registered edge unless the current session performed the corresponding verification.
- Do not archive Project Graph candidates from `project-query`, `project-fix`, `project-develop`, or any external project session; pending-timeout archival belongs only to `project-maintain`.

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

## Project Graph / Cross-Project Refs

## Safety Findings

## Suggested Repairs

## Repair Scope
```

For Base Graph fleet audits, return:

```markdown
# Base Graph Project Graph Fleet Audit - YYYY-MM-DD

## Summary

## Project Matrix

| project_id | path_status | wiki_status | graph_files | pins | edges | candidates | base_ids | source_context | severity |
|---|---|---|---|---|---|---|---|---|---|

## Errors

## Warnings

## Info

## Cross-Project Readiness

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

## LLM Wiki Doctor

Use repo-vendored `.llm-wiki/tools/llm_wiki_doctor.py` when present:

```text
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --all --format text --fail-on error
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --changed --format text --fail-on error
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --base origin/main --format json --fail-on error
```

The doctor owns deterministic validate checks such as `orphan-design-doc`, `missing-graph-evidence`, `invalid-edge-id`, `dangling-cross-ref`, `duplicate-edge-fingerprint`, `leaked-local-path`, alias/token-boundary matching, and structured project-id checks. Project ids and aliases must come from committed `.llm-wiki/project-ids.json`; confirmed edges are used for edge id validation, not as the project vocabulary. Maturity scoring and Chinese advisory reports belong to `llm-wiki-doctor`; approved structural repairs remain in `project-maintain`. Keep `missing-graph-evidence` WARN-only unless a later policy explicitly changes it.
## Boundaries

- `.llm-wiki` is a team-shared project knowledge base. Prefer project-relative and wiki-relative paths.
- Do not persist workstation-specific absolute paths such as `C:\Users\...`, `D:\workspace\...`, `/Users/...`, or `/home/...` in durable wiki pages.
- Do not copy secrets, tokens, private keys, passwords, or long original source material into wiki maintenance reports.
- Keep repairs small and explain what was intentionally left unchanged.
- Treat dashboard as an evidence-backed projection, not the source of truth.
- Treat handoff and log as archive/audit material, not lifecycle status authority.

## Common Mistakes

- Treating "file exists" as enough when the file is not discoverable from artifact, module, dashboard, or log entry points.
- Updating the dashboard but forgetting the Flow Record, artifact registry, or module README.
- Marking a Flow Record lane done because a card exists, without verification evidence.
- Rewriting Flow Record status to match a stale dashboard card.
- Repairing business meaning during a structural maintenance pass.
- Running a full wiki rewrite when one backlink or log entry would solve the visibility problem.
- Applying Obsidian vault assumptions directly to a project `.llm-wiki`; this skill only uses LLM Wiki maintenance ideas as reference.
