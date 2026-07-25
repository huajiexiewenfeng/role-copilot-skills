---
name: project-graph-visualize
description: Use when the user asks to generate, rebuild, refresh, update, preview, or validate an interactive HTML visualization of a Base Graph or Project Graph, including “生成 Base Graph 可视化”, “刷新 Project Graph HTML”, “更新 graph.html”, “查看整个跨项目关系图”, and similar graph/dashboard requests.
---

# Project Graph Visualize

## Purpose

Generate a standalone offline HTML projection of:

- the Base Graph catalog and overview flows;
- confirmed edges from project-local `project-graph/edges.md`;
- candidates and proposals as non-fact workflow layers;
- missing Project Graph file-layer status for registered projects.

The HTML is a read-only projection. Source Markdown remains authoritative.

## Mechanical generation mode

This is a deterministic artifact-generation task.

- Execute directly after resolving the Base Graph root.
- Do not invoke brainstorming, writing-plans, project-develop, or project-finish.
- Do not create Change Brief, Flow Record, working-context, handoff, artifact registry, design spec, or implementation plan.
- Do not commit unless the user explicitly asks.
- Keep normal permission checks and fresh verification.

## Preconditions

Resolve the Base Graph root in this order:

1. user-provided path;
2. current working directory when `.llm-wiki/base-graph/manifest.json` exists;
3. `LLM_WIKI_BASE_GRAPH_PATH`;
4. `~/.llm-wiki/base-graph.local.json`.

Require:

```json
{
  "graph_role": "base"
}
```

If the root is a business project rather than a Base Graph repository, stop and report the mismatch. Do not initialize or modify it.

## Write boundary

Default output:

```text
<base-root>/.llm-wiki/base-graph/graph.html
```

Allowed writes:

- the requested HTML output only.

Read-only inputs:

- Base `manifest.json`, `project-catalog.md`, `overview.md`, and `registry.local.json`;
- registered projects' `.llm-wiki/project-graph/*.md`.

Never write registered business projects. Never serialize Registry local paths.

## Generate or refresh

Run the bundled builder:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill-root>\scripts\build-graph-visualization.ps1" -BaseRoot "<base-root>"
```

For a different destination:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill-root>\scripts\build-graph-visualization.ps1" -BaseRoot "<base-root>" -OutputPath "<output.html>"
```

Then run validation:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill-root>\scripts\validate-graph-visualization.ps1" -BaseRoot "<base-root>" -HtmlPath "<output.html>"
```

## Validate only

When the user asks only to check an existing visualization, do not regenerate it. Run the validator against the requested HTML.

## Output contract

Report:

- output path;
- Base project, confirmed edge, candidate, and proposal counts;
- projects whose Project Graph file layer is missing;
- validation result;
- whether browser preview was performed.

Preview in a browser only when the user asks to open/preview it or when runtime diagnosis is necessary.

## Failure handling

- Missing Base manifest: report “not a Base Graph root”.
- Missing Registry: stop; do not invent project paths.
- Missing project Wiki or Project Graph directory: preserve the project and mark its graph status as missing.
- Malformed Markdown rows: fail validation with the source file and row count; do not silently promote or infer facts.
- Local path found in HTML: fail and do not report success.

## Routing boundaries

- Architecture questions without generation → `project-query`.
- Base repository initialization or catalog refresh → `project-base-init`.
- Candidate discovery → `project-graph-candidates-scan`.
- Proposal creation → `project-graph-auto-edge`.
- Edge confirmation or registration → `project-graph-human-edge`.
- Graph consistency repair → `project-maintain`.

## Common mistakes

- Treating Base Overview flows as confirmed edges.
- Calling projects with missing graph files “zero-edge initialized graphs”.
- Writing lifecycle documents for a mechanical refresh.
- Copying workstation paths into the generated snapshot.
- Updating remote Project Graph files while generating the view.
