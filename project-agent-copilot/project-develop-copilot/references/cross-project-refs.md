# Cross-Project Refs

Cross-Project Refs define how a project-local `.llm-wiki` safely resolves another local project's wiki/source for evidence.

Schema for edges, candidates, pins, fingerprints, manual registration, and candidate promotion lives in `project-graph.md`. Optional Base Graph bootstrap and Base write boundaries live in `base-graph.md`. This file owns registry resolution, the read-only boundary check, and staleness threshold.

## Principles

- Store physical local paths only in ignored registry or bootstrap files.
- Store shared relationship facts only in `project-graph/edges.md`.
- Store team navigation pins only in `cross-refs/index.md`.
- Do not copy remote project content into the current project as truth.
- Treat remote project wiki, source, config, Briefs, and registry as read-only.
- Use source verification before making fix or development decisions that depend on a remote contract.

## Registry Files

Preferred local registry:

```text
.llm-wiki/registry.local.json
```

Legacy local registry, read for compatibility:

```text
.llm-wiki/cross-refs/registry.local.json
```

Legacy global fallback, read-only compatibility only:

```text
~/.llm-wiki/registry.json
```

Base Graph machine-level registry, when Base is discoverable through `base-graph.md` bootstrap:

```text
<base-graph>/.llm-wiki/registry.local.json
```

All local registry files must be ignored:

```gitignore
.llm-wiki/registry.local.json
.llm-wiki/cross-refs/registry.local.json
```

`scan-state.local.json` is also local-only:

```gitignore
.llm-wiki/project-graph/scan-state.local.json
```

## Registry Schema

```json
{
  "$schema_version": 1,
  "projects": {
    "payment-service": {
      "path": "<local-path-to-payment-service>",
      "wiki": ".llm-wiki",
      "added": "2026-06-12"
    }
  }
}
```

Rules:

- `path` is the local root of the remote project.
- `wiki` is relative to `path`, defaults to `.llm-wiki`, must not be absolute, and must not end with a slash.
- Resolve wiki anchors with path-join semantics:

```text
project_root = registry.projects[remote_project].path
wiki_root = path_join(project_root, registry.projects[remote_project].wiki)
resolved_remote_anchor = path_join(wiki_root, remote_anchor)
```

- `wiki_root` and `resolved_remote_anchor` must remain inside `project_root`.
- Reject or report anchors that are absolute, start with `.llm-wiki/`, or escape with `../`.
- Local paths must never be written into committed wiki files.

## Registry Resolution Order

1. Current project `.llm-wiki/registry.local.json`.
2. Legacy current project `.llm-wiki/cross-refs/registry.local.json`.
3. Base Graph `.llm-wiki/registry.local.json`, when Base is discoverable.
4. Legacy global fallback `~/.llm-wiki/registry.json` as read-only compatibility.

Compatibility rules:

- Current project registry is the project-level override and no-Base fallback.
- Base Graph registry is the machine-level default registry.
- If only the legacy registry exists, `project-maintain` should recommend migration; repair mode may copy it to the preferred path after confirmation, but must not delete the legacy file.
- If current, legacy, Base, or global registries conflict for a project id, report the conflict and do not silently merge.
- New implementations must not create or prefer `~/.llm-wiki/registry.json`.
- When asking for a missing local path and Base is discoverable, write Base Graph `.llm-wiki/registry.local.json` after user confirmation.
- When Base is not discoverable, write only the current project's preferred `.llm-wiki/registry.local.json` after user confirmation.

Writing registry files is local resolver configuration. Base Graph `registry.local.json` is a local-config exception and is not the same as writing Base tracked architecture files.

## Staleness

Default verification freshness threshold: 30 days.

Derived staleness:

- `fresh`: `last_verified` exists and is within the threshold.
- `expired`: `last_verified` is older than the threshold.
- `unknown`: `last_verified` is missing or unparsable.

Do not write `stale` into `verification_status`. Reports and Briefs may include `derived_staleness: fresh | expired | unknown`.

## Cross-Project Boundary Check

Before reading another project's wiki or source interactively, output:

```markdown
- remote_project:
- resolved_path:
- reason:
- scope: read-only
- anchors_to_read:
- verification_required: source | wiki-only-allowed
```

Selection rules:

- `project-query` may use `wiki-only-allowed` for ownership and clue-finding answers, but must label evidence as wiki-only.
- `project-fix` and `project-develop` must use `source` when a fix or implementation decision depends on a remote contract.
- Manual edge registration starts as `draft`; writing `wiki-checked` or `source-verified` requires this boundary check and matching evidence in the current session.
- If no registry mapping exists, ask the user for the local path and write only the current project's preferred registry after confirmation.

Batch graph scanning does not emit one boundary check per project. Its `scan-report.md` must record scanned projects, scan scope, scanner version, and read-only scope.

## Remote Read Scope

Default remote read scope:

1. The named remote wiki anchor.
2. One-hop Markdown links explicitly present on that page.
3. Exact source files, classes, interfaces, topics, config keys, or contract files named by that page or by the user.

Do not by default:

- scan the whole remote repository by keyword;
- recursively crawl the remote wiki;
- write to the remote project;
- create reverse pins or reverse edges in the remote project.

Ask for user confirmation before expanding scope.

## Write Boundary

Allowed current-project writes:

- `.llm-wiki/project-graph/edges.md`
- `.llm-wiki/project-graph/candidates.md`
- `.llm-wiki/project-graph/scan-report.md`
- `.llm-wiki/project-graph/scan-state.local.json`
- `.llm-wiki/cross-refs/index.md`
- `.llm-wiki/registry.local.json`
- `.gitignore`
- current-project Bug Brief / Change Brief

Allowed Base local-config write, after user confirmation:

- Base Graph `.llm-wiki/registry.local.json`

Forbidden remote-project writes:

- remote `.llm-wiki`
- remote source
- remote config
- remote Briefs
- remote registry

Forbidden Base tracked-file writes from a business-project session:

- Base `base-graph/overview.md`
- Base `base-graph/project-catalog.md`
- Base `decisions/`
- Base `handoff/`
- any other committed Base fact file

If remote project changes are needed, generate a Context Handoff and ask the user to start a lifecycle session in the remote project. If Base tracked-file changes are needed, generate a Base Handoff unless cwd is Base or explicit Base write mode is active.
