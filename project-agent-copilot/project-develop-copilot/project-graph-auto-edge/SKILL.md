---
name: project-graph-auto-edge
description: Use when turning Project Graph candidates into source-backed edge proposals through Base Graph lookup and local/remote read-only verification, including Chinese prompts like 自动生成 edge proposal, 自动登记边候选, auto-edge, or 通过 base-graph 找项目类方法但先给人确认.
---

# Project Graph Auto Edge

## Purpose

Turn Project Graph candidates into evidence-backed edge proposals for human review. This skill may write `proposals.md` and mark candidates as `proposed`, but it must not write confirmed edges or cross-ref pins.

Use it when the user asks the agent to resolve a candidate through Base Graph, find the corresponding project/class/method/interface, or automatically prepare an edge while keeping human confirmation in the loop.

## Initialization Gate

Run after resolving the current project root and before reading a candidate or writing proposal state.

- `wiki_required: true`
- `on_missing_wiki: route project-init`
- `pending_primary_stage: project-graph-auto-edge`
- Preserve the user's requested candidate or relationship as `pending_intent`.
- If `<project_root>/.llm-wiki/` is absent, stop and return a Context Handoff to `project-init`; resume only after the router receives initialization readiness and a supported next gate.
- Do not create a partial `.llm-wiki/`, proposal, candidate update, scan report, or log inside this child as a substitute for initialization.

On the missing-wiki branch, emit this minimal handoff:

```text
bootstrap_handoff:
  project_root: <resolved project root>
  pending_intent: <preserved candidate or relationship request>
  pending_primary_stage: project-graph-auto-edge
  requested_stage_or_bridge: project-init
  current_gate: Initialization Gate
```

## Required Reads

Read only as much as needed for the target candidate or request:

- `../references/project-graph.md`
- `../references/cross-project-refs.md`
- `../references/base-graph.md`, when Base Graph resolution is needed
- `.llm-wiki/project-graph/candidates.md`
- `.llm-wiki/project-graph/proposals.md`, when present
- `.llm-wiki/project-graph/edges.md`, to avoid duplicate fingerprints and choose the next proposed edge id
- `.llm-wiki/cross-refs/index.md`, to avoid proposed pin id collisions
- Base Graph locator and catalog when a candidate references a remote project or `remote_project=unknown`
- local source/config/wiki anchors needed to verify caller, topic, endpoint, or config evidence
- remote source/config/wiki anchors read-only when Base Graph resolves a canonical project

## Allowed Writes

Current project only:

- `.llm-wiki/project-graph/proposals.md`
- `.llm-wiki/project-graph/candidates.md`, only for `pending -> proposed` status updates and proposal notes allowed by `project-graph.md`
- `.llm-wiki/project-graph/scan-report.md`, only to add a proposal summary when the file already exists and the update helps auditability
- `.llm-wiki/log.md`

## Forbidden Writes

- `.llm-wiki/project-graph/edges.md`
- `.llm-wiki/cross-refs/index.md`
- remote project wiki, source, config, Briefs, registry, or graph files
- Base Graph tracked files

If a proposal looks ready to confirm, stop and tell the user to run `project-graph-human-edge` to accept it.

## Process

1. Resolve the current project root and run the Initialization Gate.
2. Resolve the target candidate by id, fingerprint, or user-described signal.
3. Read the Project Graph contract and existing candidates/proposals/edges.
4. If the candidate has `remote_project=unknown` or a non-canonical hint, resolve a canonical project id through Base Graph when available.
5. Verify local evidence from repo-relative files, classes, methods, endpoints, topics, config keys, or wiki anchors.
6. Verify remote evidence read-only when a remote project is resolved. Use exact anchors when possible; do not scan whole remote repositories by default.
7. Classify proposal `verification_status`:
   - `source-verified`: local and remote source/endpoint/topic evidence both match in this session.
   - `runtime-verified`: runtime/log evidence proves the relation in addition to source evidence.
   - `unverified`: evidence is incomplete or wiki-only.
8. Generate a stable `fingerprint` using the confirmed direction from `project-graph.md`.
9. Select the next `proposal_id` and a `proposed_edge_id`. The proposed edge id is not a confirmed reservation; `project-graph-human-edge` must re-check collisions before writing.
10. Fill proposed cross-ref fields: `proposed_cross_ref_id`, `proposed_local_entry`, and `proposed_why_pinned`.
11. Write or update one `proposals.md` row with `human_status=pending` unless the user explicitly asks to flag it as `needs-more-evidence`.
12. Move the linked candidate from `pending` to `proposed`; keep `edge_id` empty.
13. Append a concise log entry with proposal id, candidate id, canonical project id, verification status, and evidence summary.

## Proposal Rules

- Proposal `source` is origin metadata: `scan` for scanner-origin candidates, `manual` for user-supplied candidate material.
- Proposal `source` must not be copied to `edges.source`.
- Accepted auto-edge proposals become confirmed edges with `source=auto` only when `project-graph-human-edge` accepts them.
- Proposal `verification_status` is proposed evidence metadata, not a confirmed fact.
- Do not invent anchors. If either side cannot be resolved, write an unverified proposal only when it is still useful for human review; otherwise mark the candidate `blocked` only if the Project Graph contract allows it and the reason is clear.

## Output

Report:

- `proposal_id`
- `source_candidate_id`
- canonical `from_project -> to_project`
- local evidence read
- remote evidence read or reason it stayed unresolved
- `verification_status`
- proposed cross-ref fields
- files changed
- next command, usually `project-graph-human-edge accept <proposal_id>` or a request for missing evidence

Mini example:

```text
cand-20260623-009 -> prop-20260623-001
proposed_edge_id=edge-20260623-001
human_status=pending
candidate.status=proposed
edges.md unchanged
cross-refs/index.md unchanged
```
