---
name: project-init
description: Use when initializing or refreshing a project-local LLM Wiki, adopting a repository, discovering modules, or migrating legacy docs/ai-coding context into the project development context structure.
---

# Project Init

## Purpose

Initialize or refresh project-local development context for the project development skill collection.

This skill creates a usable `.llm-wiki` skeleton, discovers modules conservatively, and migrates legacy `docs/ai-coding` as read-only source context. It does not modify production code.

## Required Shared References

Read these role-level references:

- `../references/lifecycle-mvp.md`
- `../references/llm-wiki-mvp.md`
- `../references/legacy-ai-coding-migration.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root.

## Workflow

1. Resolve `project_root`.
2. Inspect project markers:
   - `.git`
   - build files
   - `docs/`
   - existing `.llm-wiki/`
   - legacy `docs/ai-coding/`
   - `.codegraph/`
3. Create missing `.llm-wiki` directories and starter files.
4. Ensure `.llm-wiki/working-context/` exists for future complex or cross-module work.
5. Create or update `.llm-wiki/modules/index.md`.
6. Mark only explicitly selected or clearly relevant modules as `active`.
7. Mark reference modules as `reference-only`.
8. Mark other modules as `discovered`.
9. Summarize legacy `docs/ai-coding` into `.llm-wiki` without deleting or rewriting legacy files.
10. Write a `.llm-wiki/log.md` entry.
11. Report created files, discovered modules, migrated context, and open questions.

## Safety

- Do not modify production code.
- Do not delete, move, or rewrite legacy `docs/ai-coding`.
- Do not deep-read every module in a monorepo.
- Do not treat generated AI docs as source of truth.
