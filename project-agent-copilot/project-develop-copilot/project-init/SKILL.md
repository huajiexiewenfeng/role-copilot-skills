---
name: project-init
description: Use when initializing or refreshing a project-local LLM Wiki, adopting a repository, discovering modules, preparing tool bridges, or migrating legacy docs/ai-coding context into the project development context structure.
---

# Project Init

## Purpose

Initialize or refresh project-local development context for the project development skill collection.

This skill creates a usable `.llm-wiki` skeleton, discovers modules conservatively, and migrates legacy `docs/ai-coding` as read-only source context. It does not modify production code.

## Required Shared References

Read these role-level references:

- `../references/north-star.md`
- `../references/lifecycle-mvp.md`
- `../references/tool-bridge.md`
- `../references/llm-wiki-mvp.md`
- `../references/legacy-ai-coding-migration.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root.

## Workflow

1. Resolve `project_root`.
2. Decide mode:
   - `init`: no `.llm-wiki` exists or user asks to adopt a repository
   - `refresh`: `.llm-wiki` exists and user asks to rescan, after docs were copied in, or after modules changed
3. Inspect project markers:
   - `.git`
   - build files
   - `docs/`
   - existing `.llm-wiki/`
   - legacy `docs/ai-coding/`
   - `.codegraph/`
4. Create missing `.llm-wiki` directories and starter files.
5. Ensure `.llm-wiki/working-context/` exists for future complex or cross-module work.
6. Create or update `.llm-wiki/modules/index.md`.
7. Detect modules conservatively from build files and top-level service directories.
8. Mark modules:
   - `active`: explicitly selected by user or current task
   - `reference-only`: shared libraries, API contracts, DTOs, SDKs, or direct dependencies
   - `discovered`: found but not in current work
   - `unknown`: found but unclear; ask or leave as gap
9. If `.codegraph/` or generated graph files exist, record them as read-only supporting context in `.llm-wiki/index.md` or `.llm-wiki/modules/index.md`; do not generate codegraph during MVP.
10. Summarize legacy `docs/ai-coding` into `.llm-wiki` without deleting or rewriting legacy files.
11. On refresh, preserve existing statuses unless evidence or user instruction changes them.
12. Write a `.llm-wiki/log.md` entry.
13. Report created files, refreshed files, discovered modules, migrated context, codegraph context, and open questions.

## Required Outputs

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

## Module Index Minimum

Use this shape:

```markdown
| Module | Path | Type | Context | Status | Notes |
|---|---|---|---|---|---|
```

Allowed `Status` values: `active`, `reference-only`, `discovered`, `unknown`.

## Safety

- Do not modify production code.
- Do not delete, move, or rewrite legacy `docs/ai-coding`.
- Do not deep-read every module in a monorepo.
- Do not treat generated AI docs as source of truth.
- Do not overwrite existing `.llm-wiki` summaries without preserving useful user or agent decisions.
