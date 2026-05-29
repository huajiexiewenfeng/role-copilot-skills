---
name: project-ingest
description: Use when adding PRDs, links, Markdown, PDF, Word, logs, meeting notes, customer feedback, or temporary project materials into a project LLM Wiki as source proxies and ingest index entries.
---

# Project Ingest

## Purpose

Capture project source material so future development flows can discover it.

This skill creates `.llm-wiki/ingest/index.md` entries and `.llm-wiki/sources/` proxy pages. It does not replace PRDs, issues, design docs, logs, or files; it indexes and summarizes them.

## Required Shared References

Read these role-level references:

- `../references/ingest-mvp.md`
- `../references/tool-bridge.md`
- `../references/llm-wiki-mvp.md`
- `../references/templates.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root.

## Workflow

1. Resolve `project_root`.
2. Resolve the source path, URL, or pasted material.
3. Classify source type and sensitivity.
4. Ask before deep-reading binary, large, or sensitive-looking sources.
5. Choose processing mode:
   - Markdown: summary ingest
   - URL: summary ingest when accessible
   - PDF/Word: path index first
   - logs or sensitive material: cautious summary or path index only
6. Create or update `.llm-wiki/ingest/index.md`.
7. Create a source proxy in `.llm-wiki/sources/`.
8. Link to requirement, bug, module, or open question when clear.
9. Report source proxy path, ingest status, gaps, and suggested next action.

## Safety

- Do not copy secrets, credentials, customer data, internal endpoints, or production log details into `.llm-wiki`.
- Do not move or delete original source files.
- Do not turn every ingested source into active development context.
