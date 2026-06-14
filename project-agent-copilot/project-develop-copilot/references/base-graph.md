# Base Graph Reference

Base Graph is optional. It provides a machine-local registry master plus an architecture overview and project catalog for large cross-service discussions.

Base Graph does not own precise cross-project edges. Precise relationships live in each project-local `project-graph/edges.md` and in scanner-derived views.

Initialize or refresh dedicated Base Graph repositories through `project-base-init`. Do not use ordinary `project-init` for a Base Graph repo, because Base Graph is not a business project and must not receive business lifecycle files, Project Graph edges/candidates, module discovery output, requirements, or bugs.

## Bootstrap

Base Graph is discovered by:

1. `LLM_WIKI_BASE_GRAPH_PATH`
2. `~/.llm-wiki/base-graph.local.json`

Bootstrap file:

```json
{
  "$schema_version": 1,
  "base_graph_path": "D:/code/base-project-graph"
}
```

Rules:

- Bootstrap stores only the local Base Graph path.
- Bootstrap is machine-local and must not be committed to business projects.
- If both env var and bootstrap file exist and disagree, report the conflict and prefer the env var.
- If Base Graph cannot be found, degrade to current-project registry and legacy registry flow.

## Base Registry

Base Graph `.llm-wiki/registry.local.json` is the machine-level default registry.

It is a local configuration exception: a business-project session may write it after user confirmation when resolving paths. This does not allow writing Base `overview.md`, `project-catalog.md`, `decisions/`, `handoff/`, or any other tracked Base files.

Current project `.llm-wiki/registry.local.json` remains the project-level override and no-Base fallback.

## Base Files

```text
.llm-wiki/
  registry.local.json
  base-graph/
    manifest.json
    project-catalog.md
    overview.md
  decisions/
  handoff/
  log.md
```

`manifest.json`:

```json
{
  "$schema_version": 2,
  "graph_role": "base",
  "graph_id": "platform-base",
  "name": "Platform Base Graph",
  "default_stale_days": 30,
  "project_catalog": "project-catalog.md",
  "overview": "overview.md"
}
```

Do not create Base `shared-edges.md` or Base `relation-policy.md`.

## Project Catalog

`base-graph/project-catalog.md` is committed and stores logical project names, not local paths.

Suggested fields:

```markdown
# Project Catalog

| project_id | display_name | domain | owner | repo | status | notes |
|---|---|---|---|---|---|---|
```

## Overview

`base-graph/overview.md` is committed and stores slow-changing architecture narrative:

- domain grouping;
- key cross-service flows;
- common change entry points;
- ownership hints;
- who-to-touch guidance.

It is not a precise edge table and does not require fingerprint-level alignment with code.

## Write Boundary

A business-project session must not write Base tracked files. It may only generate Base Handoff or update suggestions.

Writing Base tracked files requires:

1. cwd is the Base Graph repo and `graph_role = base`; or
2. the user explicitly enters Base write mode.

Base write mode output:

```markdown
- target_graph: base
- resolved_path:
- reason:
- scope: write-current-base
- files_to_update:
```

## Canceled v1 Ideas

- No business project `manifest.json` or `parent` pointer.
- No Base `shared-edges.md`.
- No Base `relation-policy.md`.
- Dashboard is postponed and, if added, is projection only. It must show `generated_by`, `generated_at`, and `partial_view`, and must not become a fact source.
