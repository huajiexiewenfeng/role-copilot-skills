---
name: project-init
description: Use when initializing or refreshing a project-local LLM Wiki, adopting a repository, discovering modules, preparing tool bridges, or migrating legacy docs/ai-coding context into the project development context structure.
---

# Project Init

## Purpose

Initialize or refresh project-local development context for Project Develop Copilot.

This skill creates a usable `.llm-wiki` skeleton, discovers modules conservatively, records tool bridge markers, and migrates legacy `docs/ai-coding` as read-only source context. It does not modify production code.

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
2. Check whether `.llm-wiki` exists.
3. Decide `init` vs `refresh`.
4. Check for legacy `docs/ai-coding/` and existing `.codegraph/` markers.
5. Preserve useful existing `.llm-wiki` content before writing updates.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/domain-skill-contract.md`
- `../references/tool-bridge.md`
- `../references/legacy-ai-coding-migration.md`

Workflow:

1. Resolve project root.
2. Inspect project markers: `.git`, build files, `docs/`, `.llm-wiki/`, legacy `docs/ai-coding/`, `.codegraph/`.
3. Create missing `.llm-wiki` directories and starter files.
4. Ensure `.llm-wiki/working-context/` exists.
5. Create or update `.llm-wiki/modules/index.md`.
6. Detect modules conservatively from build files and top-level service directories.
7. Mark modules as `active`, `reference-only`, `discovered`, or `unknown`.
8. Record existing `.codegraph/` or generated graph files as read-only supporting context; do not generate codegraph by default.
9. Summarize legacy `docs/ai-coding` into `.llm-wiki` without deleting or rewriting legacy files.
10. Preserve existing statuses unless evidence or user instruction changes them.
11. Write a `.llm-wiki/log.md` entry.
12. Return a concise handoff.

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

## Common Mistakes

- Turning init into full codebase analysis.
- Marking every discovered module active.
- Rewriting existing wiki content destructively.
- Treating legacy AI docs as authoritative.
- Generating codegraph when only recording existing graph context was needed.