# Project Graph Maintenance Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split Project Graph maintenance into three explicit callable child skills: `project-graph-candidates-scan`, `project-graph-auto-edge`, and `project-graph-human-edge`. The workflow must make candidate discovery, evidence-backed proposal generation, and human-confirmed edge writing visibly separate, while keeping `cross-refs/index.md` automatically maintained whenever confirmed edges are written.

**Architecture:** Keep the existing Project Develop Copilot plugin layout. Add three sibling child skill directories under `project-agent-copilot/project-develop-copilot/`. Move the graph write contract into `references/project-graph.md`, keep cross-project lookup rules in `references/cross-project-refs.md`, and update the top-level router plus `project-maintain` so old graph-scan/register wording delegates to the new explicit skills instead of directly owning the workflow.

**Tech Stack:** Markdown skill instructions, existing `.llm-wiki/project-graph/*.md` table schemas, PowerShell validation commands on Windows, existing `npx.cmd skills add . --list` package validation.

---

## Task 1: Extend Project Graph Reference Contract

Update `project-agent-copilot/project-develop-copilot/references/project-graph.md` first. This is the source of truth the three new skills will cite.

- [ ] In the Project Graph files section, add `project-graph/proposals.md` as a required review queue file.
- [ ] Extend candidate statuses from `pending/rejected/blocked/promoted` to `pending/proposed/rejected/blocked/promoted`.
- [ ] Keep the candidate table columns exactly as currently defined, including `source`, and document that `proposed` means an auto-edge proposal exists but no confirmed edge has been written.
- [ ] Add the `proposals.md` schema as a pipe table with these exact columns:

```markdown
| proposal_id | source_candidate_id | proposed_edge_id | fingerprint | type | source | from_project | from_anchor | to_project | to_anchor | contract_summary | verification_status | verification_evidence | proposed_cross_ref_id | proposed_local_entry | proposed_why_pinned | human_status | human_note | created_at | updated_at |
```

- [ ] Define `human_status` values as `pending/accepted/rejected/needs-more-evidence`.
- [ ] Define `verification_status` values as `unverified/source-verified/runtime-verified`. State that `source-verified` requires file/class/method or endpoint evidence from both local and remote sides when a remote project is involved.
- [ ] Update the edge source values to include `auto` and `manual`, where `auto` means promoted from a proposal and `manual` means entered through `project-graph-human-edge` without an auto proposal.
- [ ] Update the candidate promotion rule: `project-graph-auto-edge` may move `pending -> proposed`; only `project-graph-human-edge` may move a candidate to `promoted` and assign `edge_id`.
- [ ] Add the cross-ref maintenance rule: every confirmed edge written by `project-graph-human-edge` must upsert one `cross-refs/index.md` pin row unless the human instruction explicitly says to skip the pin. The skip reason must be written in the log.
- [ ] Add validation rules:
  - `proposals.md` rows must have unique `proposal_id` and unique `fingerprint` among open pending proposals.
  - `source_candidate_id` must resolve to `candidates.md` when present.
  - Accepted proposals must resolve to an `edges.md` row via `proposed_edge_id`.
  - Confirmed edge `fingerprint` values must remain unique in `edges.md`.
  - Confirmed edge `edge_id` values referenced by `cross-refs/index.md` must resolve.
  - Confirmed edges must have a cross-ref pin unless a log entry records an explicit skip.
  - No committed graph row may contain an absolute local path; use repo-relative anchors and project ids.

## Task 2: Create `project-graph-candidates-scan` Skill

Create `project-agent-copilot/project-develop-copilot/project-graph-candidates-scan/SKILL.md`.

- [ ] Add frontmatter:

```yaml
---
name: project-graph-candidates-scan
description: Use when scanning the current project-local .llm-wiki or source tree for potential Project Graph relationship candidates, including Chinese prompts like 扫描 candidates, project-graph candidates scan, 自动扫描候选关系, or 发现缺失跨项目关系.
---
```

- [ ] State the skill purpose in the first paragraph: scan only the current project and write candidate facts, not edges.
- [ ] Include required reads before action:
  - current project `.llm-wiki/project-graph/candidates.md`
  - `.llm-wiki/project-graph/scan-report.md` if present
  - `.llm-wiki/project-graph/scan-state.local.json` if present
  - `references/project-graph.md`
  - `references/cross-project-refs.md` only if candidate signals mention another project
- [ ] Define allowed writes:
  - `.llm-wiki/project-graph/candidates.md`
  - `.llm-wiki/project-graph/scan-report.md`
  - `.llm-wiki/project-graph/scan-state.local.json`
  - `.llm-wiki/log.md`
- [ ] Define forbidden writes:
  - `.llm-wiki/project-graph/edges.md`
  - `.llm-wiki/project-graph/proposals.md`
  - `.llm-wiki/cross-refs/index.md`
  - any remote project wiki or source repo
- [ ] Document the scan algorithm:
  - collect local signals from Feign clients, HTTP URLs, MQ topics, RPC client naming, config keys, package names, and existing wiki mentions
  - normalize `candidate_fingerprint` with stable lowercase project/type/signal tokens and no absolute paths
  - deduplicate against existing candidates by fingerprint
  - create candidates with `status=pending`, `edge_id=` empty, `source=scan`
  - preserve manual candidates and never auto-expire `source=manual`
- [ ] Document output format: report row counts, new candidates, duplicates skipped, and validation result.
- [ ] Add a mini example using `cand-YYYYMMDD-001` and an empty `edge_id`.

## Task 3: Create `project-graph-auto-edge` Skill

Create `project-agent-copilot/project-develop-copilot/project-graph-auto-edge/SKILL.md`.

- [ ] Add frontmatter:

```yaml
---
name: project-graph-auto-edge
description: Use when turning Project Graph candidates into source-backed edge proposals through Base Graph lookup and local/remote read-only verification, including Chinese prompts like 自动生成 edge proposal, 自动登记边候选, auto-edge, or 通过 base-graph 找项目类方法但先给人确认.
---
```

- [ ] State the skill purpose: produce evidence-backed proposals for human review; do not write confirmed edges.
- [ ] Include required reads before action:
  - `.llm-wiki/project-graph/candidates.md`
  - `.llm-wiki/project-graph/proposals.md` if present
  - `references/project-graph.md`
  - `references/cross-project-refs.md`
  - Base Graph locator and catalog when a candidate references a remote project
  - local source anchors needed to verify caller/config evidence
  - remote source anchors read-only when Base Graph resolves a canonical project
- [ ] Define allowed writes:
  - `.llm-wiki/project-graph/proposals.md`
  - `.llm-wiki/project-graph/candidates.md` status updates to `proposed`
  - `.llm-wiki/project-graph/scan-report.md` proposal summary section if the file exists
  - `.llm-wiki/log.md`
- [ ] Define forbidden writes:
  - `.llm-wiki/project-graph/edges.md`
  - `.llm-wiki/cross-refs/index.md`
  - any remote project wiki or source repo
- [ ] Define proposal generation rules:
  - resolve canonical project id via Base Graph when available
  - verify local source anchor and remote source anchor before using `verification_status=source-verified`
  - if only local evidence exists, create proposal with `verification_status=unverified` and human status `needs-more-evidence` only when explicitly requested; otherwise keep `human_status=pending`
  - set `proposed_edge_id` to the next edge id but do not reserve it as confirmed
  - set `proposed_cross_ref_id`, `proposed_local_entry`, and `proposed_why_pinned` so human-edge can upsert `cross-refs/index.md`
  - move candidate `pending -> proposed` and keep `edge_id` empty
- [ ] Document output format: proposal id, candidate id, local/remote evidence, confidence, and next human command.
- [ ] Add a mini example showing a proposal from `cand-YYYYMMDD-009` to `prop-YYYYMMDD-001` without an `edges.md` write.

## Task 4: Create `project-graph-human-edge` Skill

Create `project-agent-copilot/project-develop-copilot/project-graph-human-edge/SKILL.md`.

- [ ] Add frontmatter:

```yaml
---
name: project-graph-human-edge
description: Use when a human confirms, rejects, or manually enters Project Graph edges and cross-ref pins, including Chinese prompts like 人工登记 edge, human-edge, 确认 proposal, 手动登记跨项目关系, or 接受/拒绝 edge proposal.
---
```

- [ ] State the skill purpose: the only Project Graph maintenance skill allowed to write confirmed edges and cross-ref pins.
- [ ] Include required reads before action:
  - `.llm-wiki/project-graph/edges.md`
  - `.llm-wiki/project-graph/candidates.md`
  - `.llm-wiki/project-graph/proposals.md` when confirming/rejecting a proposal
  - `.llm-wiki/cross-refs/index.md`
  - `references/project-graph.md`
  - `references/cross-project-refs.md`
  - source evidence files when manually entering an edge without a proposal
- [ ] Define allowed writes:
  - `.llm-wiki/project-graph/edges.md`
  - `.llm-wiki/project-graph/proposals.md`
  - `.llm-wiki/project-graph/candidates.md`
  - `.llm-wiki/cross-refs/index.md`
  - `.llm-wiki/log.md`
- [ ] Define forbidden writes:
  - remote project wiki or source repo
  - Base Graph catalog files unless the user explicitly invokes the Base Graph skill
- [ ] Define accept flow:
  - validate proposal evidence and fingerprint uniqueness
  - write or upsert the confirmed edge row in `edges.md`
  - set proposal `human_status=accepted`
  - set candidate `status=promoted` and `edge_id=<confirmed edge id>` when a candidate is linked
  - upsert one `cross-refs/index.md` row using proposed cross-ref fields, unless the user explicitly skips it
  - append a log entry with edge id, proposal id, candidate id, verification status, and cross-ref action
- [ ] Define reject flow:
  - set proposal `human_status=rejected`
  - set linked candidate to `rejected` or `blocked` according to human reason
  - do not write `edges.md` or `cross-refs/index.md`
  - append a log entry
- [ ] Define manual entry flow:
  - require human-supplied or source-verified from/to project ids and anchors
  - write edge with `source=manual`
  - create or update cross-ref pin by default
  - create a manual candidate only if the human asks to track the discovery trail
- [ ] Document output format: confirmed edge id, cross-ref id, changed files, and validation result.

## Task 5: Update Top-Level Project Develop Copilot Router

Modify `project-agent-copilot/project-develop-copilot/SKILL.md`.

- [ ] Update trigger bullets so Project Graph candidate scanning, auto proposal generation, and human edge registration are distinct visible routes.
- [ ] Replace routing table rows currently pointing at `project-maintain graph-register` and `project-maintain graph-scan`:
  - known candidate discovery -> `project-graph-candidates-scan`
  - automatic proposal through Base Graph/source verification -> `project-graph-auto-edge`
  - confirming/rejecting/manually entering edges -> `project-graph-human-edge`
  - general Project Graph audit/repair remains `project-maintain`
- [ ] Update deterministic routing notes so `graph-scan`, `candidates scan`, and `自动扫描候选关系` route to candidates scan; `auto-edge`, `自动登记`, and `proposal` route to auto-edge; `human-edge`, `手动登记`, `确认 proposal`, and `接受 proposal` route to human-edge.
- [ ] Keep Base Graph initialization routed to `project-base-init`.

## Task 6: Update `project-maintain` Delegation Boundaries

Modify `project-agent-copilot/project-develop-copilot/project-maintain/SKILL.md`.

- [ ] Keep `project-maintain` responsible for structure linting, stale candidate cleanup policy, schema validation, broken link repair, cross-ref consistency audit, and Base Graph health checks.
- [ ] Replace direct graph-scan instructions with a delegation note to `project-graph-candidates-scan`.
- [ ] Replace direct graph-register/candidate promotion instructions with delegation notes:
  - proposal generation -> `project-graph-auto-edge`
  - confirmed/manual edge writes -> `project-graph-human-edge`
- [ ] Keep read-only audit ability to report missing cross-ref pins for existing edges.
- [ ] Add one warning: `project-maintain` must not write new confirmed edges unless the user is explicitly asking for a maintenance repair to an already confirmed edge and the row identity is unambiguous.

## Task 7: Update Cross-Project Reference Docs

Modify `project-agent-copilot/project-develop-copilot/references/cross-project-refs.md`.

- [ ] Clarify that `cross-refs/index.md` is a pin/navigation layer, not a fact store.
- [ ] State that confirmed facts live in `project-graph/edges.md`; proposed facts live in `project-graph/proposals.md`.
- [ ] Add the automatic pin rule: `project-graph-human-edge` upserts a cross-ref pin when it confirms or manually writes an edge.
- [ ] State that `project-graph-auto-edge` may propose cross-ref fields but must not write `cross-refs/index.md`.
- [ ] State that `project-graph-candidates-scan` must not write cross-refs.

## Task 8: Update README Documentation

Modify both:

- `project-agent-copilot/project-develop-copilot/README.md`
- `project-agent-copilot/project-develop-copilot/README.zh.md`

- [ ] Replace language saying Project Graph is not a separate child skill with language saying the Project Graph evidence lifecycle is now split into three explicit child skills.
- [ ] Add a short skill list:
  - `project-graph-candidates-scan`: scan current project and maintain candidates
  - `project-graph-auto-edge`: resolve candidates into proposals through Base Graph/source evidence
  - `project-graph-human-edge`: accept/reject/manual-register confirmed edges and cross-ref pins
- [ ] Keep `project-maintain` documented as the audit/repair skill for wiki and graph consistency.
- [ ] Add a short Chinese example in `README.zh.md`:

```markdown
- “做一次 project-graph candidates.md 的扫描” -> `project-graph-candidates-scan`
- “通过 base-graph 找到对应项目，生成 edge proposal” -> `project-graph-auto-edge`
- “确认这个 proposal / 手动登记这条边” -> `project-graph-human-edge`
```

## Task 9: Add Acceptance Cases 26-29

Append to `project-agent-copilot/project-develop-copilot/references/acceptance-cases.md` after Case 25.

- [ ] Add `### Case 26: Project Graph Candidate Scan Is Candidate-Only`.
  - Expected route: `project-graph-candidates-scan`.
  - Expected writes: candidates, scan-report, scan-state, log.
  - Forbidden writes: edges, proposals, cross-refs, remote project.
- [ ] Add `### Case 27: Auto Edge Creates Proposal Not Edge`.
  - Expected route: `project-graph-auto-edge`.
  - Expected behavior: Base Graph resolves canonical project, local/remote anchors are read-only verified, proposal row is written, candidate becomes `proposed`, edges and cross-refs remain unchanged.
- [ ] Add `### Case 28: Human Edge Confirmation Writes Edge And Cross-Ref`.
  - Expected route: `project-graph-human-edge`.
  - Expected behavior: accepted proposal writes confirmed edge, updates proposal and candidate, and automatically upserts `cross-refs/index.md`.
- [ ] Add `### Case 29: Human Manual Edge Registration Bypasses Auto Proposal`.
  - Expected route: `project-graph-human-edge`.
  - Expected behavior: manual source-verified edge can be written directly, source is `manual`, cross-ref pin is upserted, remote writes remain forbidden.

## Task 10: Validate Package And Routing Text

Run these commands from `D:\tmp\github\role-copilot-skills`.

- [ ] Check the package sees the new child skills:

```powershell
npx.cmd skills add . --list
```

Expected result: output includes `project-graph-candidates-scan`, `project-graph-auto-edge`, and `project-graph-human-edge`.

- [ ] Check routing mentions exist:

```powershell
Select-String -Path 'project-agent-copilot/project-develop-copilot/SKILL.md' -Pattern 'project-graph-candidates-scan|project-graph-auto-edge|project-graph-human-edge'
```

Expected result: all three skill names appear in top-level routing.

- [ ] Check docs mention the new schemas:

```powershell
Select-String -Path 'project-agent-copilot/project-develop-copilot/references/project-graph.md' -Pattern 'proposals.md|human_status|proposed_cross_ref_id|project-graph-human-edge'
```

Expected result: all schema and ownership terms appear.

- [ ] Check the git diff has no whitespace errors:

```powershell
git diff --check
```

Expected result: no output and exit code 0.

## Task 11: Final Review Checklist

- [ ] Confirm no change touches `project-agent-copilot/project-develop-copilot/internal-trial-guides/`.
- [ ] Confirm no existing user changes are reverted.
- [ ] Confirm all new skill names match exactly:
  - `project-graph-candidates-scan`
  - `project-graph-auto-edge`
  - `project-graph-human-edge`
- [ ] Confirm the workflow boundary is visible in docs:
  - scanner writes candidates only
  - auto-edge writes proposals only
  - human-edge writes confirmed edges and cross-ref pins
- [ ] Confirm the cross-ref empty problem is explicitly solved by the human-edge auto-upsert rule.
- [ ] Confirm the final response names changed files and validation commands.