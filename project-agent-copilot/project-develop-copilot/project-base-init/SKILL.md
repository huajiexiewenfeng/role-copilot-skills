---
name: project-base-init
description: Use when initializing or refreshing an independent Base Graph repository for Project Develop Copilot, including explaining the Base Graph purpose, creating the Base Graph `.llm-wiki` structure, setting `graph_role: base`, creating catalog and overview templates, and guiding first project discovery without treating the Base repo as a business project.
---

# Project Base Init

## Purpose

`project-base-init` initializes an independent Base Graph repository.

Use it when the user creates or refreshes a dedicated repository whose job is to coordinate many project-local `.llm-wiki` directories. Do not use ordinary `project-init` for this case: a Base Graph repo is not a business project and must not receive business-project lifecycle files, edges, candidates, requirements, bugs, or module discovery output.

## Required Opening Explanation

Before writing files, briefly explain this meaning to the user:

```text
Base Graph is an optional governance and navigation layer for multiple project-local `.llm-wiki` directories.

It owns:
- a machine-local registry master for project-id -> local path resolution;
- a committed project catalog of logical project names;
- a committed architecture overview for slow-changing cross-service discussion context.

It does not own:
- precise cross-project edges;
- business project facts;
- shared-edges.md;
- relation-policy.md;
- source-code truth;
- another project's `.llm-wiki` content.

Precise relationship facts stay in each business project's `.llm-wiki/project-graph/edges.md`.
```

Keep the explanation short and then proceed. Do not replace this with a long free-form design discussion unless the user explicitly asks to redesign Base Graph.

## First Checks

1. Resolve the repository root.
2. Check that the root is a Git repository or ask whether to initialize files anyway.
3. Confirm the user wants a Base Graph repository, not a business project `.llm-wiki`.
4. If the current root looks like a normal code repository, warn that `project-base-init` is for a dedicated Base Graph repo and ask one concise confirmation before writing.
5. Do not scan source code, modules, Maven files, controllers, topics, SQL, or configs. Base init is structure bootstrap only.

## Files To Create

Create or refresh this structure:

```text
.llm-wiki/
  registry.local.json
  base-graph/
    manifest.json
    project-catalog.md
    overview.md
  decisions/
    README.md
  handoff/
    README.md
  log.md
```

Also ensure `.gitignore` contains:

```gitignore
.llm-wiki/registry.local.json
```

`registry.local.json` is local resolver configuration. It is allowed in the Base repo but must stay ignored by Git.

## Manifest Template

Write `.llm-wiki/base-graph/manifest.json`:

```json
{
  "$schema_version": 2,
  "graph_role": "base",
  "graph_id": "<repo-or-user-provided-id>",
  "name": "<display name>",
  "default_stale_days": 30,
  "project_catalog": "project-catalog.md",
  "overview": "overview.md"
}
```

Use a stable `graph_id` derived from the repository name when the user does not provide one. Do not include machine-local paths.

## Registry Template

Write `.llm-wiki/registry.local.json` only as local configuration:

```json
{
  "$schema_version": 1,
  "projects": {}
}
```

If an existing registry exists, preserve existing mappings unless the user asks to repair them.

## Project Catalog Template

Write `.llm-wiki/base-graph/project-catalog.md`:

```markdown
# Project Catalog

This file stores logical project identities and slow-changing ownership hints. It must not store local filesystem paths.

| project_id | display_name | domain | owner | repo | status | notes |
|---|---|---|---|---|---|---|
```

## Overview Template

Write `.llm-wiki/base-graph/overview.md`:

```markdown
# Base Graph Overview

## Purpose

This page gives a slow-changing cross-project architecture view for discussion and impact discovery.

## Domains

| domain | projects | notes |
|---|---|---|

## Key Cross-Service Flows

| flow | projects | summary | evidence |
|---|---|---|---|

## Common Entry Points

| topic | starting_project | related_projects | notes |
|---|---|---|---|

## Open Questions

- 
```

## Supporting Files

Write `.llm-wiki/decisions/README.md`:

```markdown
# Base Graph Decisions

Record slow-changing architecture or governance decisions for the Base Graph. Do not store business-project implementation truth here.
```

Write `.llm-wiki/handoff/README.md`:

```markdown
# Base Graph Handoff

Store suggested Base Graph updates from business-project sessions. Apply them only from the Base Graph repo or explicit Base write mode.
```

Write `.llm-wiki/log.md`:

```markdown
# Base Graph Log

| date | action | notes |
|---|---|---|
```

## Bootstrap Guidance

After initialization, tell the user how other project sessions can discover this Base Graph:

```text
Set LLM_WIKI_BASE_GRAPH_PATH to this repository path, or create ~/.llm-wiki/base-graph.local.json:

{
  "$schema_version": 1,
  "base_graph_path": "<absolute-path-to-this-base-graph-repo>"
}
```

Do not write the Base path into business project committed wiki files.

## First Project Discovery

Base discovery is not automatic source scanning. To add the first project, ask for:

- `project_id`;
- local project root path;
- optional display name, domain, owner, repository URL.

Then:

1. Write the local path mapping to Base `.llm-wiki/registry.local.json`.
2. Add or update the logical project row in `.llm-wiki/base-graph/project-catalog.md`.
3. If the project already has `.llm-wiki`, read only these lightweight files when present:
   - `.llm-wiki/index.md`
   - `.llm-wiki/README.md`
   - `.llm-wiki/project/overview.md`
   - `.llm-wiki/modules/index.md`
   - `.llm-wiki/project-graph/edges.md`
   - `.llm-wiki/cross-refs/index.md`
4. Use those pages only to propose catalog and overview notes.
5. If the project has no `.llm-wiki`, tell the user to run `project-init` in that business project first.

Do not write into the business project during Base discovery.

## Explicit Non-Goals

Do not create any of these files in the Base repo:

- `.llm-wiki/project-graph/edges.md`
- `.llm-wiki/project-graph/candidates.md`
- `.llm-wiki/cross-refs/index.md`
- `shared-edges.md`
- `relation-policy.md`
- business project `manifest.json`
- requirements, bugs, modules, sources, dashboard, or working-context pages

Do not write remote or business project files from Base init.

## Output

End with:

- Base Graph path;
- files created or refreshed;
- whether registry was created or preserved;
- bootstrap instruction;
- next suggested action, usually "provide the first project_id and local path for discovery" or "run project-init in a business project first".
