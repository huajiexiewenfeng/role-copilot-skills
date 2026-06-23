# Project Graph Maintenance Skills Design

Date: 2026-06-23
Status: design approved for spec review
Scope: `project-agent-copilot/project-develop-copilot` skill family

## Goal

Add three explicit Project Graph maintenance skills so users and agents can call the exact lifecycle action they intend:

- `project-graph-candidates-scan`
- `project-graph-auto-edge`
- `project-graph-human-edge`

The design separates discovery, automatic edge proposal, and human-confirmed edge registration. It keeps `edges.md` as the fact table, keeps candidates as non-authoritative clues, and makes `cross-refs/index.md` an automatically maintained navigation layer when confirmed edges are written.

## Non-Goals

- Do not replace `project-maintain`; it should route to these focused skills.
- Do not allow candidate scan results to drive `project-fix` or `project-develop` decisions.
- Do not write remote project files or reverse edges from a business-project session.
- Do not automatically write confirmed `edges.md` rows from scanner output.
- Do not run Base Graph fleet-wide scans by default.

## Architecture

Project Graph maintenance is split into three skills.

### `project-graph-candidates-scan`

Scans the current project for cross-project relationship clues and updates only candidate/scan files.

Default scope:

- Current project only.
- Optional module or relation-type filter when requested.
- No broad remote repository scan.

Writable files:

- `.llm-wiki/project-graph/candidates.md`
- `.llm-wiki/project-graph/scan-report.md`
- `.llm-wiki/project-graph/scan-state.local.json`
- `.llm-wiki/log.md`

Forbidden writes:

- `.llm-wiki/project-graph/edges.md`
- `.llm-wiki/project-graph/proposals.md`
- `.llm-wiki/cross-refs/index.md`
- Any remote project file

### `project-graph-auto-edge`

Starts from a candidate and performs targeted verification through Base Graph resolution. It generates an edge proposal, not a confirmed edge.

Default scope:

- Read one candidate from `candidates.md`.
- Resolve canonical remote project id and path through current project registry, legacy registry, global registry, or Base Graph resolver.
- Read only the named local and remote anchors needed for verification.

Writable files:

- `.llm-wiki/project-graph/proposals.md`
- `.llm-wiki/project-graph/candidates.md`
- `.llm-wiki/project-graph/scan-report.md`
- `.llm-wiki/log.md`

Forbidden writes:

- `.llm-wiki/project-graph/edges.md`
- `.llm-wiki/cross-refs/index.md`
- Any remote project file

Important rule: `project-graph-auto-edge` may source-verify a proposed edge, but it must leave `human_status: pending`. It never writes confirmed `edges.md` rows.

### `project-graph-human-edge`

Handles human confirmation, rejection, and manual edge registration.

Writable files:

- `.llm-wiki/project-graph/edges.md`
- `.llm-wiki/project-graph/proposals.md`
- `.llm-wiki/project-graph/candidates.md`
- `.llm-wiki/cross-refs/index.md`
- `.llm-wiki/log.md`

Responsibilities:

- Confirm a pending proposal and write or update `edges.md`.
- Automatically upsert a corresponding `cross-refs/index.md` pin when an edge is confirmed, unless the user explicitly says not to pin.
- Mark the source candidate as `promoted` and write `edge_id`.
- Mark the proposal as `confirmed`, `rejected`, or `needs-change`.
- Register manual edges. Without current-session source or authoritative contract verification, manual edges default to `draft`.

Forbidden behavior:

- Do not accept user-supplied `source-verified` or `last_verified` as fact.
- Do not write `source-verified` unless the current session verified source or authoritative contract evidence.
- Do not write remote reverse edges or pins.

## File Model

### `candidates.md`

Existing table remains the scanner clue layer. Candidate status values become:

- `pending`: scanned clue, not yet verified.
- `proposed`: a proposal exists and awaits human confirmation.
- `promoted`: confirmed edge exists; `edge_id` must resolve.
- `rejected`: rejected clue; future identical scan hits are suppressed unless evidence materially changes.
- `blocked`: verification could not proceed due to missing registry, path, source, permission, or unclear direction.

Only `project-graph-candidates-scan` may archive stale `source=scan + pending` candidates. `manual`, `proposed`, `promoted`, `rejected`, and `blocked` candidates are not timeout-archived.

### `proposals.md`

New review queue for proposed edges.

Recommended schema:

| field | purpose |
|---|---|
| `proposal_id` | Stable proposal id. |
| `source_candidate_id` | Candidate that produced the proposal, when applicable. |
| `proposed_edge_id` | Edge id that would be written on confirmation. |
| `fingerprint` | Canonical edge fingerprint. |
| `type` | Edge type. |
| `source` | `scan`, `manual`, or `imported`. |
| `from_project` | Canonical logical project id. |
| `from_anchor` | Source-side anchor. |
| `to_project` | Canonical logical project id. |
| `to_anchor` | Target-side anchor. |
| `contract_summary` | Short contract or relationship fact. |
| `verification_status` | `source-verified`, `wiki-checked`, `draft`, or `blocked`. |
| `verification_evidence` | Short evidence summary, with source-relative anchors only. |
| `proposed_cross_ref_id` | Pin id to write when confirmed. |
| `proposed_local_entry` | Local navigation hint. |
| `proposed_why_pinned` | Why this edge should be visible from cross-refs. |
| `human_status` | `pending`, `confirmed`, `rejected`, or `needs-change`. |
| `human_note` | Human review note. |
| `created_at` | Creation date. |
| `updated_at` | Last update date. |

### `edges.md`

Confirmed Project Graph fact table. Only `project-graph-human-edge` writes confirmed rows.

Rules:

- Fingerprints must be unique.
- `from_project` and `to_project` must be canonical logical ids.
- Anchors must be source-relative, wiki-relative, class/interface/topic/config/table identifiers, or other durable logical anchors. They must not be workstation-specific absolute paths.
- `verification_status` must be `draft`, `wiki-checked`, `source-verified`, or `blocked`.
- `source-verified` and `wiki-checked` require parseable `last_verified`.

### `cross-refs/index.md`

Navigation pin layer. It is automatically maintained when `edges.md` is written or updated by `project-graph-human-edge`.

Schema remains pin-only:

```text
id | edge_id | local_entry | why_pinned | owner_note
```

Do not store fact fields here:

- `contract_summary`
- `verification_status`
- `last_verified`
- `remote_project`
- `remote_anchor`

Default behavior: every confirmed edge gets one cross-ref pin unless explicitly skipped. If an edge later becomes expired or blocked, keep the pin and report the referenced edge status.

## State Flows

### Scan Flow

```text
project-graph-candidates-scan
  -> candidates.md: pending
  -> scan-report.md: scan summary
```

### Auto Proposal Flow

```text
project-graph-auto-edge cand-xxx
  -> resolve Base Graph canonical ids and paths
  -> read local/remote anchors as read-only
  -> proposals.md: human_status=pending
  -> candidates.md: proposed
```

### Human Confirm Flow

```text
project-graph-human-edge confirm proposal
  -> edges.md: write confirmed edge
  -> cross-refs/index.md: upsert pin
  -> candidates.md: promoted + edge_id
  -> proposals.md: confirmed
  -> log.md: maintenance record
```

### Reject Flow

```text
project-graph-human-edge reject proposal
  -> proposals.md: rejected
  -> candidates.md: rejected or pending, depending on human note
  -> log.md: maintenance record
```

## Trigger Phrases

### `project-graph-candidates-scan`

- `扫描 project graph candidates`
- `做一次 candidates scan`
- `scan current project graph candidates`
- `扫描 <module> 的跨项目候选`
- `扫描 Feign/MQTT/HTTP 关系候选`

### `project-graph-auto-edge`

- `自动 edge cand-xxx`
- `auto edge cand-xxx`
- `把 cand-xxx 做自动 edge`
- `验证 cand-xxx 并生成 proposal`
- `从 candidate 自动生成 edge 草案`

### `project-graph-human-edge`

- `确认 proposal prop-xxx`
- `reject proposal prop-xxx`
- `把 prop-xxx 登记成 edge`
- `人工登记 edge`
- `human edge from A to B`
- `手动登记 <project-a> -> <project-b>`

## Required Reports

### Candidate Scan Result

```text
mode: candidates-scan
project_root:
scan_scope:
new_candidates:
updated_candidates:
suppressed_candidates:
archived_candidates:
blocked_items:
changed_files:
next_recommended_action:
```

### Auto Edge Result

```text
mode: auto-edge
candidate_id:
base_graph_resolution:
remote_project:
remote_read_scope:
verification_result:
proposal_id:
human_status: pending
changed_files:
next_recommended_action:
```

### Human Edge Result

```text
mode: human-edge
action: confirm|reject|manual-register
proposal_id:
edge_id:
cross_ref_id:
candidate_status:
verification_status:
changed_files:
warnings:
```

## Validation Requirements

Every skill must validate the graph files it touches before claiming success.

Common checks:

- Markdown table column counts match headers.
- `candidate_fingerprint` values are unique.
- Edge fingerprints are unique.
- Promoted candidate `edge_id` resolves.
- Cross-ref `edge_id` resolves.
- No committed graph row stores workstation-specific absolute local paths.
- `verification_status` enum is valid.
- `source-verified` and `wiki-checked` rows have parseable `last_verified`.

`project-graph-human-edge` extra checks:

- Each confirmed edge has a cross-ref pin unless explicitly skipped.
- `cross-refs/index.md` does not contain fact fields.

If validation fails, the skill must not report success. It should repair the narrow table problem it introduced or report blocked with file and row evidence.

## Router Integration

`project-maintain` should route graph-specific requests to these skills:

- Candidate discovery -> `project-graph-candidates-scan`
- Candidate verification and proposed edge generation -> `project-graph-auto-edge`
- Proposal confirmation, rejection, and manual edge entry -> `project-graph-human-edge`

`project-query`, `project-fix`, and `project-develop` may consume confirmed fresh `source-verified` edges, but they must not promote candidates or proposals themselves.

## Acceptance Criteria

1. Users can explicitly invoke each of the three Project Graph skills by name or Chinese trigger phrases.
2. Candidate scanning writes candidates and scan reports but never writes confirmed edges.
3. Auto edge generation writes proposals and marks candidates `proposed`, but never writes confirmed edges or cross-refs.
4. Human edge confirmation writes `edges.md`, upserts `cross-refs/index.md`, marks candidates `promoted`, and marks proposals `confirmed`.
5. Manual edge registration defaults to `draft` unless current-session source or authoritative contract verification exists.
6. All remote projects remain read-only during verification.
7. Validation catches duplicate fingerprints, dangling edge refs, malformed status values, missing cross-ref pins, and absolute local path leakage.