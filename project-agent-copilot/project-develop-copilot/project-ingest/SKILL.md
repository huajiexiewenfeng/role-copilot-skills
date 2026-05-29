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

- `../references/north-star.md`
- `../references/ingest-mvp.md`
- `../references/tool-bridge.md`
- `../references/llm-wiki-mvp.md`
- `../references/templates.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root.

## Workflow

1. Resolve `project_root`.
2. Resolve the source path, URL, or pasted material.
3. Classify source type and sensitivity.
4. Check whether the source already appears in `.llm-wiki/ingest/index.md`; if the path, URL, size, modified time, or title changed, mark existing entry `stale` before updating.
5. Ask before deep-reading binary, large, remote, or sensitive-looking sources.
6. Use confirmation prompts:
   - PDF/Word: `This is a binary document. Should I summarize it now, or index the path only?`
   - URL: `Should I fetch and summarize this URL, or only record the link?`
   - logs: `Should I summarize symptoms only and avoid copying raw log lines?`
   - sensitive-looking file: `This may contain sensitive data. Should I record path only?`
5. Choose processing mode:
   - Markdown: summary ingest
   - URL: summary ingest when accessible
   - PDF/Word: path index first
   - logs or sensitive material: cautious summary or path index only
7. Create or update `.llm-wiki/ingest/index.md`.
8. Create a source proxy in `.llm-wiki/sources/`.
9. Link to requirement, bug, module, or open question when clear.
10. Do not make the source active by default; mark it `candidate` unless the user request or current task clearly activates it.
11. Report source proxy path, ingest status, gaps, and suggested next action.

## Processing Rules

- `path-only`: store source metadata, no summary.
- `summary`: write a short source proxy summary and key points.
- `cautious-summary`: summarize symptoms or intent without copying sensitive raw content.
- `needs-confirmation`: record source and ask before deep reading.

## Final Report

Report:

```text
Source:
Type:
Processing mode:
Ingest status:
Source proxy:
Related requirement/bug/module:
Sensitivity notes:
Gaps:
Next action:
```

## Safety

- Do not copy secrets, credentials, customer data, internal endpoints, or production log details into `.llm-wiki`.
- Do not move or delete original source files.
- Do not turn every ingested source into active development context.
