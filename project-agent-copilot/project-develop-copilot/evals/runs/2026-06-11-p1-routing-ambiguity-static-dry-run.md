# P1 Routing Ambiguity Static Dry Run - 2026-06-11

> Numbering note: eval numbers in this report follow the eval file as of commit `b2a0b31`.
> After cross-project evals 8-15 were inserted, the referenced evals were renumbered:
> Eval 11 -> Eval 19, Eval 12 -> Eval 20, Eval 13 -> Eval 21.

## Scope

This dry run checks whether ambiguous natural-language project requests now route by write intent and evidence need rather than by loose keyword matching.

It is a static instruction audit, not a fresh live-session evaluation.

## Result

| Check | Result | Evidence |
|---|---|---|
| Router has an explicit decision order | PASS | `references/lifecycle-router.md` now includes Routing Decision Tree. |
| Root skill has short tie-breakers | PASS | `SKILL.md` includes Routing Tie-breakers for agents that only load the entry skill. |
| Least-state-changing route is preferred | PASS | Both router docs use `lightweight-answer < read-only-query < dashboard-refresh < wiki-maintenance < full-lifecycle`. |
| Dashboard refresh is separated from finish | PASS | Decision tree and Eval 12 require dashboard projection only through `project-query`. |
| Wiki visibility problems are separated from read-only query | PASS | Decision tree and Eval 11 route missing dashboard/cards/links/indexes to `project-maintain`. |
| Natural lifecycle-quality intent does not require magic words | PASS | Router accepts process-evaluation intent without requiring `Dolores` or `skill-evaluator`. |
| Ordinary code review is not lifecycle-quality | PASS | Eval 13 keeps normal commit/code review on `project-review`. |

## Added Eval Coverage

| Eval | Route protected |
|---|---|
| Eval 11: Missing Dashboard Card Routes To Maintain | `project-maintain` instead of query/develop |
| Eval 12: Dashboard Refresh Is Not Finish | `project-query dashboard-refresh` instead of `project-finish` |
| Eval 13: Code Review Is Not Lifecycle Quality | normal `project-review` instead of evaluator/Dolores |

## Residual Risk

- The decision tree is still manual instruction, not an automated router.
- Older historical design documents may contain older routing examples.
- A fresh agent-session eval is still needed to confirm the decision order is followed without prompting.

## Follow-up

- Run Eval 11-13 in a fresh session before further router slimming.
- If any ambiguity remains, patch the smallest matching table row instead of adding a new mode.
