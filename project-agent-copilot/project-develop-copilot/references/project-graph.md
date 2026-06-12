# Project Graph

Project Graph is the fact model for cross-project relationships in a project-local `.llm-wiki`.

Use it with `cross-project-refs.md`. This file owns schema, fingerprints, canonical direction, manual registration, candidate promotion, and pin rules. `cross-project-refs.md` owns registry resolution, read-only boundary checks, and the stale threshold.

## Files

```text
.llm-wiki/
  registry.local.json
  cross-refs/
    index.md
  project-graph/
    edges.md
    candidates.md
    scan-report.md
    scan-state.local.json
```

Ignored local files:

```gitignore
.llm-wiki/registry.local.json
.llm-wiki/cross-refs/registry.local.json
.llm-wiki/project-graph/scan-state.local.json
```

## Layers

| Layer | File | Role | Decision authority |
|---|---|---|---|
| Candidate | `project-graph/candidates.md` | discovered or suspected relationship | never |
| Fact | `project-graph/edges.md` | only place where contract facts are stored | only if `source-verified` and fresh |
| Pin | `cross-refs/index.md` | team-confirmed navigation entry referencing `edge_id` | follows referenced edge |

Facts such as `contract_summary`, `verification_status`, and `last_verified` must exist only in `edges.md`.

## `edges.md`

```markdown
# Project Graph Edges

| edge_id | fingerprint | type | source | from_project | from_anchor | to_project | to_anchor | contract_summary | verification_status | last_verified |
|---|---|---|---|---|---|---|---|---|---|---|
| edge-001 | `http:order-service:ordercallbackcontroller:payment-service:paymentnotifycontroller` | http | manual | order-service | `OrderCallbackController` | payment-service | `PaymentNotifyController` | POST /pay/callback, idempotency key orderId | draft |  |
```

Field rules:

- `edge_id`: stable within the current project; it does not need to match remote projects.
- `fingerprint`: stable de-duplication key.
- `type`: `feign`, `mqtt`, `http`, `rpc`, `db`, `config`, `dependency`, `dto`, or `other`.
- `source`: `manual`, `scan`, or `imported`.
- `from_project` and `to_project`: logical project ids only; never `unknown`.
- anchors: class, interface, topic, config key, table, wiki-relative path, or source-relative path. Do not use local absolute paths. Wiki anchors must not start with `.llm-wiki/`.
- `verification_status`: `draft`, `wiki-checked`, `source-verified`, or `blocked`.
- `last_verified`: date produced by the actual verification action; do not accept user hand-filled dates.
- Do not persist `stale`; derive staleness from `last_verified` using the threshold in `cross-project-refs.md`.

## Edge Fingerprint

Use `:` as delimiter.

```text
fingerprint = type : from_project : normalize(from_anchor) : to_project : normalize(to_anchor)
```

`normalize()`:

- lowercase;
- trim whitespace;
- for Java classes, interfaces, and file anchors, use the simple name without package, directory, or extension;
- for topics, config keys, and table names, keep the literal lowercased value;
- replace internal `:` with `-`;
- collapse repeated whitespace to `-`.

## Canonical Direction

The direction has meaning. Do not reverse `from_project` and `to_project` just to make the current project appear first.

| type | canonical direction |
|---|---|
| `feign`, `http`, `rpc` | caller/client -> provider/server |
| `mqtt` | publisher -> subscriber; split multiple subscribers into multiple edges |
| `db` | writer/owner -> reader/consumer; if unclear, keep a candidate |
| `config` | owner/producer -> consumer; if unclear, keep a candidate |
| `dependency` | depender -> dependency |
| `dto` | producer/owner -> consumer; if unclear, keep a candidate |
| `other` | explain the direction in `contract_summary`; if unclear, keep a candidate |

## Verification Status

`verification_status` is not an ordered enum.

- `draft`: registered or discovered but not verified.
- `wiki-checked`: remote wiki was checked; this is a clue only.
- `source-verified`: remote source or authoritative contract was checked; can support decisions only when fresh.
- `blocked`: verification could not be completed.

Only `source-verified` and fresh edges can drive `project-fix` or `project-develop` decisions. `wiki-checked`, `draft`, and candidates are clues only.

Manual registration defaults to `draft`. Do not accept a user-supplied `verification_status` or `last_verified` as fact. To write `wiki-checked` or `source-verified`, run the cross-project boundary check and verify the matching evidence in the current session. Set `last_verified` from the verification date.

## `candidates.md`

```markdown
# Project Graph Candidates

| candidate_id | candidate_fingerprint | relation | local_anchor | remote_project | remote_anchor | evidence | confidence | status | edge_id | discovered_at | last_seen |
|---|---|---|---|---|---|---|---|---|---|---|---|
```

`relation`: `feign-client`, `http-client`, `http-callback`, `mqtt-publish`, `mqtt-subscribe`, `rpc-client`, `db-read`, `db-write`, `config-consume`, `dependency-use`, `dto-similar`, or `other`.

Candidate fingerprint:

```text
candidate_fingerprint = relation : normalize(local_anchor) : remote_project : normalize(remote_anchor)
```

Rules:

- Use the same `normalize()` rules as edge fingerprints.
- If `remote_project` is unknown, write literal `unknown`.
- If `remote_anchor` is empty or unknown, write literal `unknown-anchor`.
- A candidate with `remote_project = unknown` cannot be promoted to an edge.
- Do not reuse `candidate_fingerprint` as edge `fingerprint`; promotion must generate a canonical edge fingerprint.

Relation to edge type:

| relation | edge type |
|---|---|
| `feign-client` | `feign` |
| `http-client`, `http-callback` | `http` |
| `mqtt-publish`, `mqtt-subscribe` | `mqtt` |
| `rpc-client` | `rpc` |
| `db-read`, `db-write` | `db` |
| `config-consume` | `config` |
| `dependency-use` | `dependency` |
| `dto-similar` | `dto` |
| `other` | `other` |

Noise rules:

- One row per `candidate_fingerprint`.
- Re-seeing an existing candidate updates `last_seen`, evidence summary, and confidence; do not append a duplicate row.
- `rejected` remains rejected and increments suppressed count in `scan-report.md` unless evidence materially changes.
- `promoted` is not recreated; check its `edge_id` still exists.
- `blocked` only updates `last_seen`.

## `cross-refs/index.md`

Pin layer only:

```markdown
# Cross-Project Integration Points

| id | edge_id | local_entry | why_pinned | owner_note |
|---|---|---|---|---|
```

Rules:

- `edge_id` must point to the current project's `project-graph/edges.md`.
- `local_entry` is a human/agent navigation hint.
- Do not store `contract_summary`, `verification_status`, `last_verified`, `remote_project`, or `remote_anchor`.
- If a pinned edge becomes stale or blocked, keep the pin but report the referenced edge status.

## Manual Registration

Manual edge registration is owned by `project-maintain` graph maintenance.

Minimum user-provided inputs:

```text
type:
from_project:
from_anchor:
to_project:
to_anchor:
contract_summary:
```

Process:

1. Confirm canonical direction.
2. If direction is unclear, ask a targeted question or write a candidate instead of an edge.
3. Create or update `project-graph/edges.md` with `source: manual` and `verification_status: draft` by default.
4. If the user asks to pin, write `cross-refs/index.md` with only `edge_id` and navigation fields.
5. Do not write remote projects.
6. To set `wiki-checked` or `source-verified`, run the cross-project boundary check and verify evidence in-session.

## Candidate Promotion

```text
candidate
  -> verify wiki/source
  -> write edges.md with source: scan
  -> update candidate status: promoted
  -> write candidate.edge_id
  -> optionally propose cross-refs pin
```

Promotion requirements:

- `remote_project` is not `unknown`;
- canonical direction is known;
- edge fingerprint is generated from edge type and canonical anchors;
- verification evidence is recorded;
- candidate is back-linked to the edge.

## Scan Files

Scanning behavior is Phase 3 only. `project-init` may create the `scan-report.md` placeholder earlier; it stays empty until a scan runs.

- `scan-report.md`: team-readable scan summary; may be committed.
- `scan-state.local.json`: machine-local incrementality state; must be ignored.

Scanner findings must include `relation`; do not output only `type`.
