---
name: project-ingest
description: Use when adding PRDs, links, Markdown, PDF, Word, logs, meeting notes, customer feedback, or temporary project materials into a project LLM Wiki as source proxies and ingest index entries.
---

# Project Ingest

## Purpose

Capture project source material so future lifecycle work can discover it safely.

This skill creates `.llm-wiki/ingest/index.md` entries and `.llm-wiki/sources/` proxy pages. It indexes and summarizes source material; it does not replace PRDs, issues, design docs, logs, or files.

## When to Use

Use when adding or refreshing:

- PRDs, design docs, Markdown, PDFs, Word files, URLs, logs, meeting notes, or customer feedback
- temporary source material for a requirement or bug
- external evidence that should be discoverable later
- source material that should attach to a Change Brief, Bug Brief, module, or working-context

## When Not to Use

- Do not use for ordinary explanation of a document unless the user wants it indexed.
- Do not use for project initialization; use `project-init`.
- Do not use for implementation planning or bug fixing after the source is already indexed.
- Do not deep-read sensitive, binary, remote, or large sources without confirmation.

## Owned Gates

- Context Discovery Gate
- Knowledge Sync Gate
- Artifact Sync Gate when source material is an important lifecycle artifact

## Required First Check

1. Resolve project root.
2. Resolve the source path, URL, or pasted material.
3. Classify source type and sensitivity.
4. Check whether this source is already indexed.
5. Decide whether it attaches to a lifecycle session or only the project index.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/progress-dashboard.md`
- `../references/tool-bridge.md`
- `../references/templates.md`

Workflow:

1. Resolve source and project root.
2. Classify source type and sensitivity.
3. If the source already appears in `.llm-wiki/ingest/index.md` and path, URL, size, modified time, or title changed, mark existing entry `stale` before updating.
4. Ask before deep-reading binary, large, remote, or sensitive-looking sources.
5. Choose processing mode.
6. Create or update `.llm-wiki/ingest/index.md`.
7. Create a source proxy in `.llm-wiki/sources/`.
8. Link to requirement, bug, module, or open question when clear.
9. Do not make the source active by default; mark it `candidate` unless the user request or current lifecycle clearly activates it.
10. Register important source evidence as artifact when appropriate.
11. Return source proxy path, ingest status, gaps, and next action.

## Mode / Entry Selection

| Mode | Use when |
|---|---|
| `path-only` | source is sensitive, large, binary, remote, or user only wants indexing |
| `summary` | safe text source can be summarized briefly |
| `cautious-summary` | logs or sensitive material should be summarized without raw details |
| `needs-confirmation` | deep read would create privacy, size, or access risk |

Confirmation prompts:

```text
PDF/Word: This is a binary document. Should I summarize it now, or index the path only?
URL: Should I fetch and summarize this URL, or only record the link?
Logs: Should I summarize symptoms only and avoid copying raw log lines?
Sensitive-looking file: This may contain sensitive data. Should I record path only?
```

## Inputs

- source path, URL, pasted material, or description
- project root
- active Change Brief, Bug Brief, or working-context when available
- sensitivity constraints

## Outputs

Report:

```text
Source:
Type:
Processing mode:
Ingest status:
Source proxy:
Related requirement/bug/module:
Sensitivity notes:
Artifacts:
Gaps:
Next action:
```

## Context Handoff

Accept router handoff with lifecycle session, active sources, scope, current gate, and constraints.

## Return Handoff

Return:

```markdown
## Return Handoff

- stage_or_bridge_used: project-ingest
- result_summary:
- changed_assumptions:
- recommended_scope_changes:
- artifacts:
- verification_notes:
- lifecycle_updates_needed:
- next_gate:
```

## Boundaries

- Do not copy secrets, credentials, customer data, internal endpoints, or production log details into `.llm-wiki`.
- Do not move or delete original source files.
- Do not turn every ingested source into active development context.
- Do not make dashboard changes during ordinary ingest unless the source affects visible progress state.

## Common Mistakes

- Copying raw sensitive logs into source proxies.
- Ingesting a source but not linking it to the active lifecycle session.
- Marking a source active just because it was ingested.
- Treating a PRD or PDF as higher authority than source code, tests, or current user decisions.