# P1 State Projection Static Dry Run - 2026-06-11

## Scope

This dry run checks whether lifecycle state now has a one-way authority model:

```text
Flow Record + artifact registry + verification evidence
-> dashboard projection / handoff summary / log audit trail
```

It is a static rule audit, not a fresh live-session evaluation.

## Result

| Check | Result | Evidence |
|---|---|---|
| Flow Record is lifecycle status authority | PASS | `references/flow-record.md` defines the State Authority Model. |
| Artifact registry authority is bounded | PASS | Artifact registry is limited to artifact existence, path, owner, status, and discoverability. |
| Dashboard is projection-only | PASS | `references/progress-dashboard.md` defines Projection Rules and forbids dashboard-only lifecycle truth. |
| Finish writes authority before projection | PASS | `project-finish/SKILL.md` updates Flow Record before dashboard, handoff, and log. |
| Dashboard refresh cannot mutate lifecycle state | PASS | `project-query/SKILL.md` forbids editing Flow Records or verification status during dashboard-only refresh. |
| Maintenance repairs projections from evidence | PASS | `project-maintain/SKILL.md` uses authority order and forbids changing Flow Record to match dashboard/handoff/log. |
| Review detects projection drift | PASS | `project-review/SKILL.md` checks dashboard/handoff/log claims against Flow Record and current evidence. |
| Finish Sync Gate encodes one-way projection | PASS | `references/lifecycle-gates.md` states dashboard refresh must rebuild visible cards from Flow Records and artifact evidence. |

## Drift Cases Covered

| Scenario | Expected behavior |
|---|---|
| Dashboard says testing done, Flow Record has no verification evidence | Review flags dashboard drift; dashboard refresh downgrades/removes the claim. |
| Handoff says archived, Flow Record archive step is pending | Finish/review must update Flow Record from actual handoff evidence or flag drift; dashboard must not copy handoff status blindly. |
| Flow Record says done, current verification failed | Route through finish/review before changing done/verified status. |
| Artifact registry points to a missing dashboard file | Maintenance repairs registry or recreates dashboard conservatively from evidence. |
| Log says work completed, Flow Record is active | Treat log as audit note only; do not promote lifecycle status from log text. |

## Residual Risk

- Historical design documents may still describe the older multi-source sync model.
- No automated runner enforces the authority model yet; this is a static instruction audit.
- Real project testing should include a dashboard refresh on a `.llm-wiki` with intentionally stale dashboard cards.

## Follow-up

- Add an executable eval prompt for dashboard-vs-Flow-Record conflict before the next large refactor.
- Continue with P1-5 routing ambiguity after this projection model is stable.
