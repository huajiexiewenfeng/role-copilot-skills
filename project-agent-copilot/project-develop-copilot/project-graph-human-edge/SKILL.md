---
name: project-graph-human-edge
description: Use when a human confirms, rejects, or manually enters Project Graph edges and cross-ref pins, including Chinese prompts like 人工登记 edge, human-edge, 确认 proposal, 手动登记跨项目关系, or 接受/拒绝 edge proposal.
---

# Project Graph Human Edge

## Purpose

Confirm, reject, or manually enter Project Graph edges under human control. This is the only Project Graph maintenance skill allowed to write confirmed edges and cross-ref pins.

Use it when the user says to accept or reject a proposal, manually register a cross-project relation, confirm an auto-edge result, or write a known edge and pin it for navigation.

## Required Reads

Read only as much as needed for the requested edge action:

- `../references/project-graph.md`
- `../references/cross-project-refs.md`
- `.llm-wiki/project-graph/edges.md`
- `.llm-wiki/project-graph/candidates.md`
- `.llm-wiki/project-graph/proposals.md`, when accepting or rejecting a proposal
- `.llm-wiki/cross-refs/index.md`
- `.llm-wiki/log.md`, when checking prior skip reasons or appending results
- source/config/wiki evidence files when manually entering an edge without an existing proposal

## Allowed Writes

Current project only:

- `.llm-wiki/project-graph/edges.md`
- `.llm-wiki/project-graph/proposals.md`
- `.llm-wiki/project-graph/candidates.md`
- `.llm-wiki/cross-refs/index.md`
- `.llm-wiki/log.md`

## Forbidden Writes

- remote project wiki, source, config, Briefs, registry, or graph files
- Base Graph catalog, overview, decisions, or other tracked Base files unless the user explicitly invokes a Base Graph skill from the Base Graph context
- machine-local registry files unless the user explicitly asks for resolver configuration and the cross-project reference contract allows it

## Accept Proposal Flow

1. Resolve the proposal id and read linked candidate/edge/pin state.
2. Re-check fingerprint uniqueness in `edges.md` and proposal uniqueness among unresolved proposals.
3. Confirm that project ids and anchors are logical, repo-relative, and not absolute local paths.
4. If accepting an auto-edge proposal, write or upsert the confirmed edge row with `source=auto`.
5. Copy accepted `verification_status`, `verification_evidence`, `contract_summary`, anchors, and `last_verified` according to `project-graph.md`; after acceptance these become confirmed facts in `edges.md`.
6. Set proposal `human_status=accepted` and record a human note when supplied.
7. If a source candidate exists, set candidate `status=promoted` and `edge_id=<confirmed edge id>`.
8. Upsert one `cross-refs/index.md` row using proposed cross-ref fields unless the human instruction explicitly says to skip the pin.
9. If the human skips the pin, append the skip reason to `.llm-wiki/log.md`.
10. Append a log entry with edge id, proposal id, candidate id, verification status, and cross-ref action.

## Reject Proposal Flow

1. Resolve the proposal id and linked candidate.
2. Set proposal `human_status=rejected` and record the human reason.
3. Do not write `edges.md`.
4. Do not write `cross-refs/index.md`.
5. If a linked candidate is `proposed`, set it to `rejected` or `blocked` according to the human reason and keep `edge_id` empty.
6. Append a log entry with proposal id, candidate id, and reason.

## Manual Edge Entry Flow

1. Require human-supplied or source-verified `type`, `from_project`, `from_anchor`, `to_project`, `to_anchor`, and `contract_summary`.
2. Verify source evidence when the user requests `source-verified` or when the edge will drive fix/develop decisions.
3. Generate the edge fingerprint from the canonical direction in `project-graph.md`.
4. Write or update `edges.md` with `source=manual`.
5. Upsert a `cross-refs/index.md` pin by default unless the user explicitly says to skip it.
6. Create a manual candidate only if the human asks to preserve the discovery trail; otherwise direct manual edge registration does not need a candidate.
7. Append a log entry with edge id, verification status, cross-ref action, and any skipped pin reason.

## Validation

Before reporting success, check:

- edge ids and fingerprints are unique
- accepted proposals resolve to confirmed edges
- promoted candidates resolve to confirmed edges
- rejected or blocked candidates keep `edge_id` empty
- cross-ref pins reference existing edge ids
- every confirmed edge has a cross-ref pin unless a log entry records an explicit skip
- no committed graph row contains an absolute local path
- remote project files were not written

## Output

Report:

- action: accepted, rejected, or manual edge written
- confirmed `edge_id`, when any
- `proposal_id` and `candidate_id`, when any
- cross-ref id or explicit skip reason
- changed files
- validation result