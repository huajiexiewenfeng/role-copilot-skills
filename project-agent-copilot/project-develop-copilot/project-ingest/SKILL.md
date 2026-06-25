---
name: project-ingest
description: Use when adding PRDs, links, Markdown, PDF, Word, logs, meeting notes, customer feedback, or temporary project materials into a project LLM Wiki as batch-organized source proxies, full source copies when appropriate, manifests, and ingest index entries.
---

# Project Ingest

## Purpose

Capture project source material so future development flows can discover it.

This skill creates `.llm-wiki/ingest/index.md` entries, batch-organized `.llm-wiki/sources/proxies/` pages, and when safe/appropriate, `.llm-wiki/sources/originals/` full source copies. It indexes and summarizes source material while keeping traceable links to the original source and the wiki-local copy used by the team.

## Relationship to Project Session Extract

Use `project-session-extract` instead of `project-ingest` when the input is a historical AI/team chat, transcript, exported session, colleague conversation, or old agent handoff.

If a session contains real PRD, design document, URL, log, or meeting note links, `project-session-extract` should identify them as source candidates. Confirmed source documents may then be ingested through `project-ingest`.

## Owned Gates

- Context Recovery Gate
- Finish Sync Gate when ingest updates source indexes, source proxies, artifacts, or log entries

## Required Shared References

Read these role-level references:

- `../references/north-star.md`
- `../references/ingest-mvp.md`
- `../references/tool-bridge.md`
- `../references/llm-wiki-mvp.md`
- `../references/templates.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root. If no shared `references/` directory is available, continue in degraded mode using the minimum rules in this skill; report the missing deep references and keep source records conservative.

Reference availability policy:

- Shared references are deep references, not startup requirements.
- Do not stop solely because `../references/` is missing.
- In degraded mode, ingest can still create a batch entry, source proxy summary, optional full-source copy for safe Markdown, and `.llm-wiki/log.md` entry.
- Do not deep-read large, binary, remote, or sensitive sources without confirmation.

## Workflow

1. Resolve `project_root`.
2. Resolve output language using `llm-wiki-mvp.md` and `north-star.md`; preserve existing `.llm-wiki` page language on refresh/update.
3. Resolve the source path, URL, or pasted material.
4. Normalize the source identity before writing wiki metadata: use repository-relative paths for in-project files, stable labels such as `external/<source-set>/<filename>` for external local folders, and URLs for remote sources. Do not write workstation-specific absolute paths into long-lived wiki indexes or source proxy metadata.
5. Classify source type and sensitivity.
6. Check whether the source already appears in `.llm-wiki/ingest/index.md`; if the normalized source identity, URL, size, modified time, title, source proxy, or full source copy changed, mark existing entry `stale` before updating.
7. Ask before deep-reading binary, large, remote, or sensitive-looking sources.
8. Use confirmation prompts:
   - PDF/Word: `This is a binary document. Should I summarize it now, or index the path only?`
   - URL: `Should I fetch and summarize this URL, or only record the link?`
   - logs: `Should I summarize symptoms only and avoid copying raw log lines?`
   - sensitive-looking file: `This may contain sensitive data. Should I record path only?`
9. Choose processing mode:
   - Markdown: `summary + full-source-copy` ingest when safe.
   - URL: `summary` ingest when accessible; full-source-copy only when fetched material is stable, allowed, and not sensitive.
   - PDF/Word: path index first; ask before deep reading or copying.
   - logs or sensitive material: `cautious-summary` or `path-only`.
10. Allocate an ingest batch id using `YYYYMMDD-NNN`, incrementing `NNN` for each ingest batch on the same date.
11. Create or update `.llm-wiki/ingest/index.md`; when a full source copy exists, use the wiki-local archived path as the primary `Source` entry, not the external local absolute path.
12. Create source proxies under `.llm-wiki/sources/proxies/<batch-id>/`.
13. For safe Markdown full-source-copy ingest, copy originals under `.llm-wiki/sources/originals/<batch-id>/`.
14. Create or update `.llm-wiki/sources/originals/<batch-id>/manifest.md` when full source copies exist.
15. Link the source proxy to `contexts/project/sources.md` when it is project-level material, or to the selected module/domain `sources.md` when it clearly belongs to a scope.
16. Link to requirement, bug, module, or open question when clear.
17. Do not make the source active by default; mark it `candidate` unless the user request or current task clearly activates it.
18. Report source proxy path, full source copy path when present, batch manifest, ingest status, gaps, and suggested next action.

## Processing Rules

- `path-only`: store source metadata, no summary.
- `summary`: write a short source proxy summary and key points.
- `summary + full-source-copy`: write a short source proxy summary and store a wiki-local full source copy for team-shared Markdown materials.
- `cautious-summary`: summarize symptoms or intent without copying sensitive raw content.
- `needs-confirmation`: record source and ask before deep reading.

## Batch Storage Rules

Use batch-organized storage so repeated ingest runs remain readable and traceable.

```text
.llm-wiki/sources/
  README.md
  registry.md
  proxies/
    README.md
    <batch-id>/
      001-title-slug.md
      002-title-slug.md
  originals/
    README.md
    <batch-id>/
      manifest.md
      001-title-slug.md
      002-title-slug.md
```

Rules:

- Batch id format: `YYYYMMDD-NNN`, for example `20260605-001`.
- Source id format: `<batch-id>-III`, for example `20260605-001-002`.
- Proxy filename format: `III-title-slug.md`.
- Full source copy filename format: `III-title-slug.md`.
- Proxy and original must use the same sequence number and slug.
- Preserve readable source titles in the slug, but remove unnecessary date prefixes when the batch already provides the ingest date.
- If two files in the same batch would produce the same filename, append `-1`, `-2`, etc. before `.md`.
- Keep `.llm-wiki/sources/` root uncluttered; only keep `README.md`, `registry.md`, and subdirectories there.
- Do not write personal absolute paths such as `D:\workspace\...` or `C:\Users\...` into `.llm-wiki/ingest/index.md`, source proxy metadata, module `sources.md`, source registry, or batch manifests.
- For files under the project repository, record repository-relative paths such as `docs/plans/example.md`.
- For external local folders copied into the wiki, assign a stable source-set label such as `external/adapter-dji-docs` and record `external/adapter-dji-docs/<original-filename>` as the original source label.
- When a full source copy exists, prefer the wiki-local archived path such as `sources/originals/<batch-id>/001-title-slug.md` as the `Source` value in `.llm-wiki/ingest/index.md`.
- Preserve the copied original document body as source material; do not rewrite paths inside the body unless the user explicitly asks for source-content normalization.

## Source Proxy Metadata

For project-relative Markdown sources, include an exact `original_path` metadata line in every source proxy and any generated requirement so `orphan-design-doc` can match by exact repo-relative path:

```markdown
- original_path: `docs/plans/example.md`
```

When the ingested source discusses cross-service behavior, include either `## Project Graph Evidence` with valid edge ids or `## Project Graph Gaps`. Do not invent edges; write Gaps when no confirmed source-backed edge exists.

Each source proxy should include these metadata lines near the top when available:

```markdown
- Source id: `<batch-id>-III`
- Original source: `<normalized-source-label-or-url>`
- Full source copy: `.llm-wiki/sources/originals/<batch-id>/III-title-slug.md`
- Type: `<source-type>`
- Processing mode: `<processing-mode>`
- Status: `candidate`
- Related module: `<module-or-scope>`
```

Omit `Full source copy` only when the processing mode is `path-only`, `summary`, `cautious-summary`, or `needs-confirmation` and no full copy was created.

## Batch Manifest

Create `.llm-wiki/sources/originals/<batch-id>/manifest.md` for every batch that has full source copies.

The manifest should include:

```markdown
# Ingest Batch Manifest: <batch-id>

- Batch: `<batch-id>`
- Date: YYYY-MM-DD
- Processing mode: Markdown summary + full-source-copy ingest
- Source count: N
- Naming rule: proxy and original use the same source id sequence and slug; same-batch filename conflicts append `-1`, `-2`.

## Sources

| Source id | Original source | Proxy | Archived file | Type | Scope |
|---|---|---|---|---|---|
```

Use paths relative to the manifest where practical, for example `../../proxies/<batch-id>/001-title-slug.md`. The `Original source` column should contain the normalized source label or URL, not a workstation-specific absolute path.

## Manual Inbox

Users may manually copy source materials into:

```text
docs/ingest/
.llm-wiki/ingest/inbox/
```

Those files are reconciled by `project-init refresh`. `project-ingest` remains the explicit one-off intake path when the user names a specific source.

Manual copied transcript files may be routed to `project-session-extract` when their content is primarily conversation rather than source documentation.

## Final Report

Report:

```text
Source:
Normalized source:
Type:
Processing mode:
Ingest status:
Source proxy:
Full source copy:
Batch manifest:
Related requirement/bug/module:
Sensitivity notes:
Gaps:
Next action:
```

## Safety

- Do not copy secrets, credentials, customer data, internal endpoints, or production log details into `.llm-wiki`.
- Do not create full source copies for sensitive-looking material unless the user explicitly confirms it is safe.
- Do not move or delete original source files.
- Do not leak local workstation paths into team-shared wiki metadata; normalize them before writing indexes, proxies, manifests, registries, or module source lists.
- Do not turn every ingested source into active development context.
