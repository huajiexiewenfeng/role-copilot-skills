# Eval Run Report: 2026-06-11 P0 Static Dry Run

> Numbering note: eval numbers in this report follow the eval file as of commit `373327c`.
> After cross-project evals 8-15 were inserted, the referenced evals were renumbered:
> Eval 8 -> Eval 16, Eval 9 -> Eval 17, Eval 10 -> Eval 18.

- Commit before run: `373327c`
- Runner: Codex
- Skill install checked: repository files plus local `.codex/skills` sync from previous step
- Project fixture: static rule review only; no real project fixture executed
- Eval set: `evals/project-develop-copilot-evals.md`
- Cases run: 10
- PASS: 10
- PARTIAL: 0
- FAIL: 0

## Scope

This was a static dry-run against the current Project Develop Copilot skill rules.

It checked whether router rules, child skill rules, degraded-reference behavior, Session Digest behavior, finish/dashboard constraints, and lifecycle-quality routing are explicitly represented in the skill documents.

It did not execute a fresh live agent conversation against a real `.llm-wiki` fixture. A live run is still recommended before P1 Gate consolidation.

## Results

| Case | Score | Evidence | Notes |
|---|---|---|---|
| Eval 1: Lightweight Discussion Must Stay Lightweight | PASS | `SKILL.md` has `lightweight-answer`, `No Child Skill Mode`, and explicit no-write boundaries. | Static rule coverage is sufficient. |
| Eval 2: Project Wiki Question Routes To Read-Only Query | PASS | `SKILL.md` routes `.llm-wiki` query to `project-query`; `project-query/SKILL.md` is read-only by default. | Static rule coverage is sufficient. |
| Eval 3: Development Must Use Documentation Anchor | PASS | `project-develop/SKILL.md` requires Documentation Anchor Gate, Change Brief, Flow Record, acceptance, scope, and verification plan before code edits. | Static rule coverage is sufficient. |
| Eval 4: Missing References Must Degrade, Not Hard Fail | PASS | All child skills now treat shared references as deep references and state `Do not stop solely because ../references/ is missing`. | This directly covers the 2026-06-08 failure point. |
| Eval 5: Finish Sync Must Update Flow Record Before Projection | PASS | `project-finish/SKILL.md` requires verification evidence, Flow Record step updates, artifact/dashboard evidence, and residual risk. | P1 single-projection hardening is still future work, but P0 rule coverage exists. |
| Eval 6: Dashboard Refresh Must Project Child Flow Records | PASS | `project-query/SKILL.md` requires every distinct `flow_id` and child Flow Record to appear in visible board cards and `dashboardData.flowRecords`. | Covers the 2026-06-08 child-flow dashboard failure. |
| Eval 7: Handoff Must Live Under `.llm-wiki/handoff` | PASS | `project-finish/SKILL.md` has a Handoff Path Rule requiring `.llm-wiki/handoff/<flow-id>-handoff.md`. | Covers the 2026-06-08 handoff placement failure. |
| Eval 8: Scope Expansion Requires Child Change Brief | PASS | `project-develop/SKILL.md` requires child Change Brief with `parent_flow_id` before child execution plan. | Covers the 2026-06-08 child plan without child requirement failure. |
| Eval 9: Historical Session Import Is Candidate First | PASS | `SKILL.md` routes `session-context-import` to `project-session-extract`; `project-session-extract/SKILL.md` requires candidate Session Digest and confirmation before writes. | During this run, remaining `Context Digest` terminology drift was found and fixed to `Session Digest`. |
| Eval 10: Lifecycle Quality Uses Natural Intent | PASS | `SKILL.md` includes project-flow failure review intent and lifecycle-quality mode; no-edit boundaries are present for review/evaluator-style requests. | P1 router decision tree should make this more discoverable, but P0 coverage exists. |

## Findings

No P0 blocking failures found in static rule coverage after fixes.

## Fixes Applied During Run

- Replaced remaining `Context Digest` / `Context Digests` wording with `Session Digest` / `Session Digests` in router and child skills.
- Confirmed no hard-stop references behavior remains in child skill documents.

## Residual Risk

- This run did not execute live prompts in a fresh Codex session.
- P1 Gate consolidation should not start until at least one live run confirms the same 10 cases against a real or fixture `.llm-wiki`.
- Some Chinese prompts display as mojibake in PowerShell output, but the Markdown files remain usable in UTF-8-aware editors.

## Next Action

Run one live manual eval pass using `evals/runbook.md`, then proceed to P1-4 Gate consolidation if there are no FAIL results.
