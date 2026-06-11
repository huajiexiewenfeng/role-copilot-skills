# Cross-Project Refs

Cross-Project Refs let one project-local `.llm-wiki` point to another project-local `.llm-wiki` for cross-service evidence, without copying remote truth into the current project.

Use this reference when a requirement, bug, or query crosses service boundaries such as Feign, MQTT topics, HTTP APIs, RPC, shared databases, or shared configuration.

## Principles

- Store only indexes and investigation clues in the current project.
- Do not copy remote project content or treat it as current-project truth.
- Keep logical project ids separate from physical local paths.
- Store physical local paths only in ignored local registry files.
- Treat remote project wiki and source as read-only unless the user explicitly starts a separate lifecycle session in that project.
- Use source verification before making implementation or fix decisions that depend on a remote contract.

## Files

```text
.llm-wiki/
  cross-refs/
    index.md
    registry.local.json
```

`registry.local.json` must be ignored:

```gitignore
.llm-wiki/cross-refs/registry.local.json
```

## `cross-refs/index.md`

`index.md` is team-shared and may be committed. It records integration points from the current project to other logical project ids.

Template:

```markdown
# Cross-Project Integration Points

| id | type | local_anchor | remote_project | remote_anchor | contract_summary | verification_status | last_verified |
|---|---|---|---|---|---|---|---|
| xref-001 | feign | code:src/main/java/.../OrderClient.java | payment-service | modules/payment-api.md | POST /pay/callback, idempotency key orderId | source-verified | 2026-06-10 |
| xref-002 | mqtt | code:DeviceEventListener | device-gateway | requirements/mqtt-topics.md | topic: device/+/event, QoS 1 | source-verified | 2026-05-28 |

## Notes

- xref-002: remote project changed payload shape in 2026-05; re-check before message bug decisions.
```

Field rules:

- `type`: one of `feign`, `mqtt`, `http`, `rpc`, `db`, `config`, `other`.
- `local_anchor`: current-project code, config, topic, or wiki anchor. Prefer prefixes such as `code:`, `wiki:`, `config:`, or `topic:`.
- `remote_project`: logical project id only. Do not write local paths.
- `remote_anchor`: path relative to the remote wiki root. Do not include `.llm-wiki/`; do not write absolute paths.
- `contract_summary`: short summary only, not the full contract.
- `verification_status`: one of `draft`, `wiki-checked`, `source-verified`, `blocked`.
- `last_verified`: date when the contract was last checked against remote wiki and/or source.

Do not persist `stale` as a `verification_status`. Staleness is derived from `last_verified`.

## Verification Status

| Status | Meaning |
|---|---|
| `draft` | Registered but not verified. |
| `wiki-checked` | Remote wiki was checked, but remote source was not checked. |
| `source-verified` | Remote wiki and source were checked, and the contract can support decisions. |
| `blocked` | The remote path, wiki, source, permission, or anchor was unavailable. |

Trust order from strongest to weakest:

```text
source-verified > wiki-checked > draft > blocked
```

Rules:

- `wiki-checked` is an investigation clue. Do not base fix or development decisions on it alone.
- `source-verified` is required before code or contract decisions depend on remote behavior.
- `blocked` must include the blocking reason in Bug Brief or Change Brief notes.
- Written Bug Brief or Change Brief status must not be stronger than the evidence actually checked.

## Staleness

Default verification freshness threshold: 30 days.

Derived staleness:

- `fresh`: `last_verified` exists and is within 30 days.
- `expired`: `last_verified` is older than 30 days.
- `unknown`: `last_verified` is missing or unparsable.

Use derived staleness in reports and lifecycle briefs as `derived_staleness`. Do not write it back into `verification_status`.

## `registry.local.json`

`registry.local.json` maps logical project ids to local physical paths. It is local-only and must not be committed.

Schema:

```json
{
  "$schema_version": 1,
  "projects": {
    "payment-service": {
      "path": "<local-path-to-payment-service>",
      "wiki": ".llm-wiki",
      "added": "2026-06-11"
    }
  }
}
```

Rules:

- `path` is the local root of the remote project.
- `wiki` is a relative path from `path`, defaulting to `.llm-wiki`.
- `wiki` must not be absolute.
- Resolve anchors with path-join semantics:

```text
project_root = registry.projects[remote_project].path
wiki_root = path_join(project_root, registry.projects[remote_project].wiki)
resolved_remote_anchor = path_join(wiki_root, remote_anchor)
```

- `wiki_root` and `resolved_remote_anchor` must remain inside `project_root`.
- Reject or report `remote_anchor` values that are absolute, start with `.llm-wiki/`, or escape with `../`.

Optional global fallback:

```text
~/.llm-wiki/registry.json
```

Resolution order:

1. Current project `.llm-wiki/cross-refs/registry.local.json`.
2. Optional global fallback `~/.llm-wiki/registry.json`.

The global fallback is read-only unless the user explicitly asks to write it.

## Cross-Project Boundary Gate

Before reading a remote project wiki, output:

```markdown
- remote_project:
- resolved_path:
- reason:
- scope: read-only
- anchors_to_read:
- verification_required:
```

`verification_required` choices:

- `source`: required for `project-fix` or `project-develop` decisions that depend on the remote contract.
- `wiki-only-allowed`: allowed for `project-query` when answering ownership, upstream/downstream, or clue-finding questions; clearly state that source verification was not performed.
- `user-confirm`: required before expanding remote read scope, writing local registry mappings, or proceeding when evidence is insufficient.

## Remote Read Scope

Default remote read scope:

1. The `remote_anchor` page.
2. One-hop Markdown links explicitly present on that page.
3. Exact source files, classes, interfaces, topics, or config keys named by that page.

Do not:

- scan the whole remote repository by keyword by default;
- recursively crawl the remote wiki;
- write to the remote project;
- create reverse cross-refs in the remote project.

Ask for user confirmation before expanding scope.

## Lifecycle Outputs

For Bug Briefs, write remote findings under:

```markdown
## External Findings

- project-id:
- xref-id:
- evidence:
- verification_status:
- derived_staleness:
- conclusion:
- impact_on_current_project:
- suggested_handoff:
```

For Change Briefs, write remote dependencies under:

```markdown
## External Dependencies

- project-id:
- xref-id:
- dependency_type:
- required_contract:
- evidence:
- verification_status:
- derived_staleness:
- impact_on_change:
- fallback_or_handoff:
```

Keep these sections in the current project. If remote changes are required, generate a context handoff and ask the user to start a lifecycle session in the remote project.
