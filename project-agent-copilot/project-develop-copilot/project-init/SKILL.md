---
name: project-init
description: Use when initializing or refreshing a project-local LLM Wiki, adopting a repository, discovering modules, preparing tool bridges, or migrating legacy docs/ai-coding context into the project development context structure.
---

# Project Init

## Purpose

Initialize or refresh project-local development context for Project Develop Copilot.

This skill creates a usable, stable `.llm-wiki` project-context structure, discovers modules conservatively, records tool bridge markers, and migrates legacy `docs/ai-coding` as read-only source context. It follows the project/user language context for generated prose and does not modify production code.

It also produces a context completion plan. Init should not imply the agent fully understands every module. Whole-repository init normally reaches project navigation readiness, then guides the user to complete source-backed scoped contexts before feature or bug work.

## When to Use

Use when the router or user needs to:

- adopt a repository into Project Develop Copilot
- create `.llm-wiki` for the first time
- refresh stale project context
- discover modules and service boundaries
- prepare tool bridge markers such as existing `.codegraph/`
- migrate useful legacy `docs/ai-coding` context into `.llm-wiki`

## When Not to Use

- Do not use for ordinary feature development after project context already exists.
- Do not use for bug diagnosis unless the project context is missing or stale.
- Do not use for source ingest of one PRD/log/PDF; use `project-ingest`.
- Do not use to edit production code.

## Owned Gates

- Context Recovery Gate
- Finish Sync Gate when init produces wiki starters, artifact entries, or dashboard starter/projection files

## Required First Check

1. Resolve `project_root`.
2. Resolve optional shared references from `../references/` or local `references/`. If `domain-skill-contract.md`, `progress-dashboard.md`, or `progress-dashboard-template.html` is missing, continue in degraded mode using the minimum rules in this skill; report the missing deep references and skip template-dependent dashboard generation unless a safe starter can be produced.
3. Report root evidence before writing:
   - user-provided path
   - current working directory
   - `.git`
   - root build file
   - `docs/ai-coding`
   - existing `.llm-wiki`
   - confidence: `high`, `medium`, or `low`
4. If root confidence is `medium` or `low`, ask the user to confirm before writing `.llm-wiki`.
5. Check whether `.llm-wiki` exists.
6. Decide `init` vs `refresh`.
7. Check for legacy `docs/ai-coding/`.
8. Treat graph outputs as optional supporting context only when explicitly active or requested.
9. Preserve useful existing `.llm-wiki` content before writing updates.
10. Detect the project language before writing generated prose:
   - prefer the user conversation language when clear;
   - otherwise prefer the dominant language of existing project docs and legacy context;
   - keep code identifiers, paths, command names, status ids, and protocol terms unchanged;
   - if the project is bilingual, use the user-facing language for prose and preserve technical English terms inline.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/domain-skill-contract.md`
- `../references/tool-bridge.md`
- `../references/legacy-ai-coding-migration.md`
- `../references/progress-dashboard.md`
- `../references/progress-dashboard-template.html`

Reference availability policy:

- Shared references are deep references, not startup requirements.
- Do not stop solely because `../references/` is missing.
- In degraded mode, still perform root evidence checks, create/preserve the standard `.llm-wiki` structure, and write conservative starter files.
- If the dashboard template is unavailable, do not invent unsupported dashboard data; create only a minimal placeholder or report that dashboard generation was skipped.

Workflow:

1. Resolve project root.
2. Inspect project markers under the resolved project root only: `.git`, build files, `docs/`, `.llm-wiki/`, legacy `docs/ai-coding/`, and explicitly active graph outputs.
3. Create missing `.llm-wiki` standard directories and starter files. Do not use an ad-hoc minimal layout when the project development lifecycle expects the standard structure.
4. Ensure the standard `.llm-wiki` directory structure exists; create missing directories without deleting extra existing directories.
5. Create or update `.llm-wiki/modules/index.md`.
6. Create `.llm-wiki/modules/<scope>/` only for user-selected or clearly active scopes that need source-backed context.
7. Detect modules conservatively from build files and top-level service directories.
8. Mark modules as `active`, `reference-only`, `discovered`, or `unknown`.
9. Do not automatically record `.codegraph/`, `graphify-out/`, `GRAPH_REPORT.md`, or generated graph files merely because they exist; register them only when user-requested, already maintained in `.llm-wiki`, or explicitly active in project docs.
10. Summarize legacy `docs/ai-coding` into `.llm-wiki` without deleting or rewriting legacy files.
11. Create `.llm-wiki/dashboard/progress.html` from `../references/progress-dashboard-template.html` when missing, using the detected project language for visible labels when practical.
12. Register the dashboard in `.llm-wiki/artifacts/index.md` when the artifact registry exists; if the registry does not exist yet, create the standard artifact registry starter.
13. Produce a context completion plan with recommended scoped contexts, missing architecture/source-map facts, source evidence, and suggested next action.
14. Preserve existing statuses unless evidence or user instruction changes them.
15. Write a `.llm-wiki/log.md` entry.
16. Return a concise handoff with the current init completion level.
17. If this is a refresh, never downgrade an existing richer wiki structure to a smaller skeleton.

## Language Policy

Generated `.llm-wiki` prose must follow the actual project and user language context.

- If the user asks in Chinese and project docs are Chinese or bilingual, write wiki prose in Chinese.
- If the repository docs are primarily English and the user has not asked for another language, write prose in English.
- Preserve exact code identifiers, module names, paths, commands, protocol terms, status ids, and lifecycle level names.
- For mixed-language projects, use the user's language for explanations and keep technical English terms inline where that is clearer.
- Do not silently fall back to English templates when the surrounding context is Chinese.

## Standard `.llm-wiki` Structure

A project init must create or preserve this standard structure. Some directories may contain only a `README.md` or `.gitkeep` starter during init, but the directories themselves should exist so later lifecycle skills have stable targets.

```text
.llm-wiki/
  README.md
  log.md
  project/
  requirements/
  ingest/
  modules/
  sources/
  artifacts/
  cross-refs/
  project-graph/
  dashboard/
  session-digests/
  migration/
  working-context/
  decisions/
  verification/
  handoff/
```

Minimum starter files:

- `.llm-wiki/README.md`: root evidence, init mode, current level, and key artifacts.
- `.llm-wiki/project/overview.md`: project-level orientation and source-of-truth notes.
- `.llm-wiki/requirements/README.md`: requirement intake/status landing area.
- `.llm-wiki/ingest/README.md`: imported PRD/log/doc/source-proxy landing area.
- `.llm-wiki/modules/index.md`: module inventory table.
- `.llm-wiki/modules/<scope>/README.md`: scoped-context landing area only for selected or clearly active scopes.
- `.llm-wiki/sources/registry.md`: source and supporting-context registry.
- `.llm-wiki/artifacts/index.md`: specs, plans, reports, verification notes, generated pages, and dashboard registry.
- `.llm-wiki/cross-refs/index.md`: cross-project pin layer; stores team-confirmed entry points that reference `project-graph/edges.md` by `edge_id` only.
- `.llm-wiki/project-graph/edges.md`: unique cross-project relationship fact table.
- `.llm-wiki/project-graph/candidates.md`: candidate/discovered relationship table; candidates do not drive decisions.
- `.llm-wiki/project-graph/scan-report.md`: latest graph scan summary placeholder.
- `.llm-wiki/dashboard/progress.html`: static project progress dashboard generated from the skill template.
- `.llm-wiki/session-digests/README.md`: recallable Session Digest landing area for historical chat/session summaries.
- `.llm-wiki/migration/legacy-ai-coding.md`: legacy docs/ai-coding migration index when present.
- `.llm-wiki/working-context/README.md`: active task scratch area.
- `.llm-wiki/decisions/README.md`: durable project decisions landing area.
- `.llm-wiki/verification/README.md`: verification commands, gaps, and evidence landing area.
- `.llm-wiki/handoff/README.md`: handoff summaries and return handoffs.
- `.llm-wiki/context-completion-plan.md`: recommended scoped contexts and missing facts.

Refresh rules:

- Preserve existing directories and richer files even if they are not listed above.
- Add missing standard directories/files without flattening, renaming, or deleting user-created structure.
- Create or preserve `.llm-wiki/cross-refs/index.md` with the pin-layer Cross-Project Integration Points template when missing.
- Create or preserve `.llm-wiki/project-graph/edges.md`, `.llm-wiki/project-graph/candidates.md`, and `.llm-wiki/project-graph/scan-report.md` with empty templates when missing.
- Ensure `.gitignore` contains `.llm-wiki/registry.local.json`, `.llm-wiki/cross-refs/registry.local.json`, and `.llm-wiki/project-graph/scan-state.local.json` exactly once so local project-path mappings and scan state do not enter git.
- Do not create `.llm-wiki/registry.local.json` or `.llm-wiki/cross-refs/registry.local.json` during init unless the user provides a remote project path and confirms storing it as local-only configuration.
- Create or preserve `.llm-wiki/session-digests/` for confirmed Session Digests. Do not scan it as raw source material; treat it as recall context by default, not project truth.
- When `.llm-wiki/session-digests/` exists, include it in context discovery for recall and duplicate avoidance. Do not promote digest items to requirement, bug, module, Flow Record, dashboard, scope, or verification truth without explicit Lifecycle Promotion confirmation.
- If an older project uses a different but richer lifecycle layout, record it in `project/overview.md` or `sources/registry.md` and ask before reorganizing.
- If `.llm-wiki/dashboard/progress.html` already exists, preserve its layout and update only the structured data/status sections needed by `progress-dashboard.md`.

## Mode / Entry Selection

| Mode | Use when |
|---|---|
| `init` | no `.llm-wiki` exists or user asks to adopt a repository |
| `refresh` | `.llm-wiki` exists and user asks to rescan, context changed, or docs/modules were added |
| `migration-check` | legacy `docs/ai-coding` exists and should be indexed as source context |

## Inputs

- project root or repository path
- existing `.llm-wiki`
- build files and top-level directories
- legacy `docs/ai-coding`
- existing `.codegraph` or graph output paths
- user-selected active modules when provided

## Outputs

Report:

```text
Project root:
Mode:
Created:
Updated:
Preserved:
Modules:
Codegraph context:
Legacy migration:
Context completion level:
Recommended scoped contexts:
Open questions:
Next action:
```

Module index minimum:

```markdown
| Module | Path | Type | Context | Status | Notes |
|---|---|---|---|---|---|
```

Cross-project refs minimum:

```markdown
# Cross-Project Integration Points

| id | edge_id | local_entry | why_pinned | owner_note |
|---|---|---|---|---|

## Notes

- This is a pin layer only. Store facts in `.llm-wiki/project-graph/edges.md`.
- Do not copy `contract_summary`, `verification_status`, `last_verified`, `remote_project`, or `remote_anchor` here.
```

Project Graph edges minimum:

```markdown
# Project Graph Edges

| edge_id | fingerprint | type | source | from_project | from_anchor | to_project | to_anchor | contract_summary | verification_status | last_verified |
|---|---|---|---|---|---|---|---|---|---|---|

## Notes

- This is the unique cross-project relationship fact table.
- Manual registration defaults to `verification_status: draft`.
- Do not write `stale`; derive staleness from `last_verified`.
```

Project Graph candidates minimum:

```markdown
# Project Graph Candidates

| candidate_id | candidate_fingerprint | relation | local_anchor | remote_project | remote_anchor | evidence | confidence | status | edge_id | discovered_at | last_seen |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Notes

- Candidates are clues only and must not drive fix or development decisions.
```

Project Graph scan report minimum:

```markdown
# Project Graph Scan Report

- scanned_at:
- scanner_version:
- scanned_projects:
- scan_scope:
- read_only_scope:
- new_candidates:
- updated_candidates:
- suppressed_candidates:
- changed_edges:
- stale_edges:
- blocked_items:

## Notes

-
```

## Context Handoff

When called by the root router, accept:

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

Return:

```markdown
## Return Handoff

- stage_or_bridge_used: project-init
- result_summary:
- changed_assumptions:
- recommended_scope_changes:
- artifacts:
- verification_notes:
- lifecycle_updates_needed:
- next_gate:
```

## Boundaries

- Do not modify production code.
- Do not delete, move, or rewrite legacy `docs/ai-coding`.
- Do not deep-read every module in a monorepo.
- Do not treat generated AI docs as source of truth.
- Do not overwrite existing `.llm-wiki` summaries without preserving useful user or agent decisions.
- Do not generate English prose by default when the project/user context is Chinese or another non-English language.
- Do not omit standard lifecycle directories such as `requirements/`, `ingest/`, `project/`, `modules/`, `decisions/`, `verification/`, or `handoff/` during init.
- Do not require codegraph generation.
- Do not silently switch into a child module just because it has richer build files; record it as a module under the chosen root unless the user confirms it is the root.
- Do not write facts from another checkout or previous conversation into the current `.llm-wiki`.
- Do not route directly to feature development as the default init next action when scoped module context is missing.
- Do not create a separate project-root `scope-context/`, `contexts/`, or new `docs/ai-coding/<scope>/` tree as the primary context store. Project-level context belongs in `.llm-wiki`; scope-level context belongs under `.llm-wiki/modules/<scope>/`; task-level context belongs in `.llm-wiki/working-context/<change-id>.md`.

## Init Completion Levels

| Level | Name | Meaning | Feature-ready? |
|---|---|---|---|
| 1 | project-navigation-ready | Global project context, module index, and source registry exist. | No |
| 2 | context-completion-plan-ready | Recommended scoped contexts and missing architecture/source-map facts are listed. | No |
| 3 | scoped-context-ready | A selected module/domain context has source-backed architecture, source map, rules, and gaps. | Usually |
| 4 | feature-ready | A concrete requirement/bug has active scope, sources, verification plan, and working context. | Yes |

Whole-repository init should normally finish at Level 1 or Level 2 unless the user explicitly selects a scope to complete.

## Context Completion Plan

After global project context exists, recommend scoped contexts using this shape:

```markdown
| Scope | Why | Active Paths | Reference Paths | Status | Missing Facts | Suggested Next Action |
|---|---|---|---|---|---|---|
```

Good candidates include modules with existing `docs/ai-coding/<scope>/`, protocol-heavy modules, deployment owners, persistence-contract modules, cross-service API owners, and recurring feature areas from user/project docs.

Do not claim a recommended scope is feature-ready until source-backed architecture and source maps exist.

## Wrong-Root Recovery

If the user corrects the project root after `.llm-wiki` was written:

1. Treat it as a blocker.
2. Stop using facts from the wrong root.
3. Initialize or refresh `.llm-wiki` under the corrected root.
4. Verify the corrected wiki contains no obvious foreign project names, module names, or paths.
5. Report wrong wiki locations separately and ask before deleting them.
6. Run `project-review` style checks for wiki drift, scope drift, and unrelated writes before claiming recovery is complete.

## Common Mistakes

- Turning init into full codebase analysis.
- Using English boilerplate in a Chinese project or conversation.
- Creating a smaller ad-hoc `.llm-wiki` layout that breaks lifecycle skills expecting standard directories.
- Marking every discovered module active.
- Rewriting existing wiki content destructively.
- Treating legacy AI docs as authoritative.
- Registering stale graph output when the user said to ignore it.
- Claiming full feature readiness after only project navigation init.
