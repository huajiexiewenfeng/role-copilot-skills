# Project Graph

Project Graph is the fact model for cross-project relationships in a project-local `.llm-wiki`.

Use it with `cross-project-refs.md` and `base-graph.md`. This file owns schema, fingerprints, canonical direction, candidate proposal, human edge confirmation, and pin rules. `cross-project-refs.md` owns registry resolution, read-only boundary checks, and the stale threshold. `base-graph.md` owns optional Base Graph bootstrap, registry master, catalog, overview, and Base write boundaries.

## Files

```text
.llm-wiki/
  registry.local.json
  cross-refs/
    index.md
  project-graph/
    edges.md
    candidates.md
    proposals.md
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
| Proposal | `project-graph/proposals.md` | required review queue for auto-edge proposals | never |
| Fact | `project-graph/edges.md` | only place where contract facts are stored | only if `source-verified` or `runtime-verified` and fresh |
| Pin | `cross-refs/index.md` | team-confirmed navigation entry referencing `edge_id` | follows referenced edge |

Confirmed facts such as `contract_summary`, `verification_status`, and `last_verified` must exist only in `edges.md`. Proposal rows may carry proposed summaries and evidence fields, but they are not confirmed facts until `project-graph-human-edge` accepts the proposal and writes the edge.

## Thresholds

- `default_stale_days = 30`: edge verification freshness threshold, defined in `cross-project-refs.md`.
- `default_candidate_pending_days = 90`: scan-origin candidate aging threshold. This is independent from edge freshness; it cleans old guesses, not verified facts.

## `edges.md`

```markdown
# Project Graph Edges

| edge_id | fingerprint | type | source | from_project | from_anchor | to_project | to_anchor | contract_summary | verification_status | last_verified |
|---|---|---|---|---|---|---|---|---|---|---|
| edge-001 | `http:order-service:ordercallbackcontroller:payment-service:paymentnotifycontroller` | http | manual | order-service | `OrderCallbackController` | payment-service | `PaymentNotifyController` | POST /pay/callback, idempotency key orderId | unverified |  |
```

Field rules:

- `edge_id`: stable within the current project; it does not need to match remote projects.
- `fingerprint`: stable de-duplication key.
- `type`: `feign`, `mqtt`, `http`, `rpc`, `db`, `config`, `dependency`, `dto`, or `other`.
- `source`: `auto` or `manual`. `auto` means promoted from an accepted proposal; `manual` means entered through `project-graph-human-edge` without an auto proposal.
- `from_project` and `to_project`: logical project ids only; never `unknown`.
- anchors: class, interface, topic, config key, table, wiki-relative path, or source-relative path. Do not use local absolute paths. Wiki anchors must not start with `.llm-wiki/`.
- repo-level dependency anchors use `maven:groupId:artifactId`, `gradle:group:name`, `repo:<name>`, or `module:<name>`; avoid `anchor == project` fallback unless no better coordinate exists.
- `verification_status`: `unverified`, `source-verified`, or `runtime-verified`.
- `last_verified`: date produced by the actual verification action; do not accept user hand-filled dates.
- Do not persist `stale`; derive staleness from `last_verified` using the threshold in `cross-project-refs.md`.

`imported` is intentionally not part of the first implementation. If future work imports edges from another tool or file, define that import workflow and add the enum in the same change.

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

- `unverified`: confirmed by human intent but not yet verified from source or runtime evidence.
- `source-verified`: file, class, method, or endpoint evidence was checked. When a remote project is involved, evidence is required from both local and remote sides.
- `runtime-verified`: source evidence was checked and runtime evidence such as logs, traces, live API behavior, or deployed configuration confirmed the relationship.

Only `source-verified` or `runtime-verified` and fresh edges can drive `project-fix` or `project-develop` decisions. `unverified`, proposals, and candidates are clues only.

Human edge confirmation defaults to `unverified`. Do not accept a user-supplied `verification_status` or `last_verified` as fact. To write `source-verified` or `runtime-verified`, run the cross-project boundary check and verify the matching evidence in the current session. Set `last_verified` from the verification date.

## `candidates.md`

```markdown
# Project Graph Candidates

| candidate_id | candidate_fingerprint | relation | source | local_anchor | remote_project | remote_anchor | evidence | confidence | status | edge_id | discovered_at | last_seen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

`relation`: `feign-client`, `http-client`, `http-callback`, `mqtt-publish`, `mqtt-subscribe`, `rpc-client`, `db-read`, `db-write`, `config-consume`, `dependency-use`, `dto-similar`, or `other`.

`source`: `scan` or `manual`.

- Scanner findings write `source: scan`.
- User-confirmed or agent-written candidates from human graph maintenance write `source: manual`.

`status`: `pending`, `proposed`, `rejected`, `blocked`, or `promoted`. New candidates that have not been proposed, promoted, rejected, or blocked are `pending` by default. `proposed` means an auto-edge proposal exists but no confirmed edge has been written.

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
- `proposed` is not promoted automatically; check that the related proposal row still exists and remains reviewable.
- `pending` candidates with `source = scan` whose `last_seen` is older than `default_candidate_pending_days` are archived by `project-maintain`: move the row to the `Archived Candidates` section of `scan-report.md`, then remove it from `candidates.md`.
- `source = manual` candidates are never auto-archived by the pending timeout rule.
- Candidate archival is a maintenance-only action. It runs only during `project-maintain` audit or `graph-scan` cleanup, never during `project-query`, `project-fix`, or `project-develop`.

## `proposals.md`

Required review queue:

```markdown
# Project Graph Proposals

| proposal_id | source_candidate_id | proposed_edge_id | fingerprint | type | source | from_project | from_anchor | to_project | to_anchor | contract_summary | verification_status | verification_evidence | proposed_cross_ref_id | proposed_local_entry | proposed_why_pinned | human_status | human_note | created_at | updated_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

Field rules:

- `proposal_id`: stable within the current project.
- `source_candidate_id`: optional back-link to `project-graph/candidates.md`; when present, it must resolve.
- `proposed_edge_id`: the edge id that `project-graph-human-edge` will write if the proposal is accepted.
- `fingerprint`: proposed confirmed-edge fingerprint, generated from edge type and canonical anchors.
- `type`: same values as `edges.md`.
- `source`: `scan` or `manual`, preserving the candidate or discovery source that led to the proposal.
- anchors: same anchor rules as `edges.md`; do not use local absolute paths.
- `verification_status`: `unverified`, `source-verified`, or `runtime-verified`.
- `verification_evidence`: concise file, class, method, endpoint, config, log, trace, or runtime evidence summary.
- `human_status`: `pending`, `accepted`, `rejected`, or `needs-more-evidence`.
- `proposed_cross_ref_id`, `proposed_local_entry`, and `proposed_why_pinned`: suggested pin fields only; no pin is confirmed until `project-graph-human-edge` writes `cross-refs/index.md`.

Proposal rows are not facts. `project-graph-auto-edge` may create or update proposal rows and may move a candidate from `pending` to `proposed`, but it must not write `edges.md` or `cross-refs/index.md`.

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
- Every confirmed edge written by `project-graph-human-edge` must upsert one pin row unless the human instruction explicitly says to skip the pin; the skip reason must be written in `.llm-wiki/log.md`.
- If a pinned edge becomes stale or loses required verification, keep the pin but report the referenced edge status.

## Manual Registration

Human edge confirmation is owned by `project-graph-human-edge`.

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
3. Create or update `project-graph/edges.md` with `source: manual` when there is no accepted auto proposal, or `source: auto` when accepting a proposal.
4. Use `verification_status: unverified` by default.
5. Upsert one `cross-refs/index.md` pin row unless the human instruction explicitly says to skip the pin.
6. If the pin is skipped, write the explicit skip reason in `.llm-wiki/log.md`.
7. Do not write remote projects.
8. To set `source-verified` or `runtime-verified`, run the cross-project boundary check and verify evidence in-session.

## Candidate Promotion

```text
candidate
  -> project-graph-auto-edge verifies proposal evidence
  -> write proposals.md only
  -> update candidate status: proposed
  -> project-graph-human-edge accepts or rejects
  -> write edges.md with source: auto or manual
  -> update candidate status: promoted only after confirmed edge write
  -> write candidate.edge_id only after confirmed edge write
  -> upsert cross-refs pin unless explicitly skipped
```

Promotion requirements:

- `remote_project` is not `unknown`;
- canonical direction is known;
- edge fingerprint is generated from edge type and canonical anchors;
- verification evidence is recorded;
- candidate is back-linked to the edge.

`project-graph-auto-edge` may move `pending -> proposed`. Only `project-graph-human-edge` may move a candidate to `promoted` and assign `edge_id`.

## Validation Rules

- `proposals.md` rows must have unique `proposal_id` and unique `fingerprint` among open pending proposals.
- `source_candidate_id` must resolve to `candidates.md` when present.
- Accepted proposals must resolve to an `edges.md` row via `proposed_edge_id`.
- Confirmed edge `fingerprint` values must remain unique in `edges.md`.
- Confirmed edge `edge_id` values referenced by `cross-refs/index.md` must resolve.
- Confirmed edges must have a cross-ref pin unless a log entry records an explicit skip.
- No committed graph row may contain an absolute local path; use repo-relative anchors and project ids.

## Scan Files

Scanning is an optional scale feature, not the baseline contract feature. `project-init` may create the `scan-report.md` placeholder earlier; it stays empty until a scan runs.

- `scan-report.md`: team-readable scan summary; may be committed.
- `scan-state.local.json`: machine-local incrementality state; must be ignored.

Scanner findings must include `relation`; do not output only `type`.

Current project `candidates.md` may contain only relationships where one side is the current project. External-to-external relationships go to `scan-report.md` or a Base-derived view, not current candidates.

`scan-report.md` must preserve an audit section for candidate cleanup:

```markdown
## Archived Candidates

| candidate_fingerprint | relation | local_anchor | remote_project | remote_anchor | last_seen | archived_on | reason |
|---|---|---|---|---|---|---|---|
```

Rules:

- `Archived Candidates` is a retained section. Updating the scan report must not silently delete it.
- Archive rows are de-duplicated by `candidate_fingerprint`.
- The timeout reason is `pending-timeout-90d`.
- If a previously archived relationship is found again by a later scan, write it as a new `pending` row in `candidates.md`; do not resurrect archived state.
