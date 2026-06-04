---
name: project-init
description: Use when initializing or refreshing a project-local LLM Wiki, adopting a repository, discovering modules, preparing tool bridges, or migrating legacy docs/ai-coding context into the project development context structure.
---

# Project Init

## Purpose

Initialize or refresh project-local development context for Project Develop Copilot.

This skill creates a usable `.llm-wiki` skeleton, discovers modules conservatively, records tool bridge markers, and migrates legacy `docs/ai-coding` as read-only source context. It does not modify production code.

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

- Context Discovery Gate
- Knowledge Sync Gate
- Artifact Sync Gate when init produces important context artifacts

## Required First Check

1. Resolve `project_root`.
2. Report root evidence before writing:
   - user-provided path
   - current working directory
   - `.git`
   - root build file
   - `docs/ai-coding`
   - existing `.llm-wiki`
   - confidence: `high`, `medium`, or `low`
3. If root confidence is `medium` or `low`, ask the user to confirm before writing `.llm-wiki`.
4. Check whether `.llm-wiki` exists.
5. Decide `init` vs `refresh`.
6. Check for legacy `docs/ai-coding/`.
7. Treat graph outputs as optional supporting context only when explicitly active or requested.
8. Preserve useful existing `.llm-wiki` content before writing updates.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/domain-skill-contract.md`
- `../references/tool-bridge.md`
- `../references/legacy-ai-coding-migration.md`

Workflow:

1. Resolve project root.
2. Inspect project markers under the resolved project root only: `.git`, build files, `docs/`, `.llm-wiki/`, legacy `docs/ai-coding/`, and explicitly active graph outputs.
3. Create missing `.llm-wiki` directories and starter files.
4. Ensure `.llm-wiki/working-context/` exists.
5. Create or update `.llm-wiki/modules/index.md`.
6. Detect modules conservatively from build files and top-level service directories.
7. Mark modules as `active`, `reference-only`, `discovered`, or `unknown`.
8. Do not automatically record `.codegraph/`, `graphify-out/`, `GRAPH_REPORT.md`, or generated graph files merely because they exist; register them only when user-requested, already maintained in `.llm-wiki`, or explicitly active in project docs.
9. Summarize legacy `docs/ai-coding` into `.llm-wiki` without deleting or rewriting legacy files.
10. Produce a context completion plan with recommended scoped contexts, missing architecture/source-map facts, source evidence, and suggested next action.
11. Preserve existing statuses unless evidence or user instruction changes them.
12. Write a `.llm-wiki/log.md` entry.
13. Return a concise handoff with the current init completion level.

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
- Do not require codegraph generation.
- Do not silently switch into a child module just because it has richer build files; record it as a module under the chosen root unless the user confirms it is the root.
- Do not write facts from another checkout or previous conversation into the current `.llm-wiki`.
- Do not route directly to feature development as the default init next action when scoped module context is missing.

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
- Marking every discovered module active.
- Rewriting existing wiki content destructively.
- Treating legacy AI docs as authoritative.
- Registering stale graph output when the user said to ignore it.
- Claiming full feature readiness after only project navigation init.
