# Capability Gap Audit

Use this audit after [north-star.md](north-star.md), `full-lifecycle-implementation-plan.zh.md`, and `dry-run-report-2026-06-04.md` when deciding what remains before broad testing.

This file reflects the current Level 3.5 documentation implementation state. It distinguishes implemented documentation contracts from behavior that still needs real or fixture project validation.

## Summary

Project Develop Copilot has moved from a fragmented child-skill collection toward a documented Level 3.5 lifecycle system.

Implemented in documentation:

- top-level `project-develop-copilot` router
- lightweight-answer boundary
- lifecycle router protocol
- lifecycle gate stack
- domain skill contract
- Change Brief and Bug Brief protocols
- Context Handoff / Return Handoff
- progress dashboard evidence protocol
- evaluator / Dolores continuous evolution protocol
- Level 3.5 acceptance cases
- simulated dry-run report

Not yet proven in runtime:

- full Case 10 end-to-end run on a real project; fixture dry run passed on 2026-06-04
- duplicate lifecycle session avoidance during resume
- external bridge behavior with actual `systematic-debugging`, `writing-plans`, and `verification-before-completion`
- dashboard HTML maintainability and evidence links
- review detection from real git diffs

## Level 3.5 Status

| Capability | Status | Notes |
|---|---|---|
| Top-level `project-develop-copilot` router | Implemented | Root `SKILL.md` exists and is discoverable from repository-root install listing. |
| Lightweight Answer Mode | Implemented in router docs | Root router and `lifecycle-router.md` define lightweight-answer; simulated Case 1 passes. |
| Project Query | Implemented | `project-query` handles read-only `.llm-wiki` lookup and discussion context; Acceptance Case 11 added. |
| Lifecycle Session | Strengthened | Change Brief reference exists, Bug Brief reference exists, and routing record persistence is defined. Real project resume still needs testing. |
| Routing Record | Defined | Present in root router, `lifecycle-router.md`, `lifecycle-gates.md`, Change Brief, and Bug Brief protocols. |
| Gate Stack | Implemented in docs | `lifecycle-gates.md` exists and all root/child SKILL files declare owned gates. |
| External Skill Bridge | Strengthened | Context Handoff / Return Handoff are defined in router, gates, and child skills. Real bridge testing remains. |
| Domain Skill Contract | Implemented | `domain-skill-contract.md` exists and root/child SKILL files share the router-friendly section structure. |
| Artifact Registry | Strengthened | Artifact row format exists in `lifecycle-gates.md` and dashboard protocol; real artifact sync still needs dry run. |
| Progress Dashboard | Protocol implemented | `progress-dashboard.md` exists; finish/review include dashboard evidence and drift rules. Real HTML fixture remains. |
| Continuous Skill Evolution | Protocol implemented | `continuous-evolution.md`, `evals/`, `cases/failures/`, and `cases/golden/` exist; review exposes Lifecycle Quality output. |
| Acceptance Pressure Cases | Updated | `acceptance-cases.md` covers numeric Cases 1-36 plus 9A/9B/9C, totaling 39 definitions; simulated dry run recorded. |
| Install Discovery | Passed | `npx.cmd skills add . --list` from repository root finds 13 skills, including root router and seven project child skills. |

## Skill-Level Status

### project-develop-copilot root router

Status: implemented in documentation.

Evidence:

- root `SKILL.md` exists
- `references/lifecycle-router.md` exists
- lightweight vs full lifecycle decision is explicit
- routing record persistence is defined
- primary stage and secondary bridge selection is defined
- resume lookup order is defined

Remaining validation:

- run live prompts for lightweight-answer, bug, feature, finish, review, resume, evaluator, and Dolores routes
- verify agents do not over-create lifecycle state for lightweight discussion

### project-init

Status: contract-aligned.

Evidence:

- Domain Skill Contract structure added
- owned gates declared
- Return Handoff added
- project root, `.llm-wiki`, legacy context, modules, and codegraph marker behavior preserved

Remaining validation:

- run against a real multi-module project
- verify existing `.llm-wiki` content is preserved on refresh

### project-ingest

Status: contract-aligned.

Evidence:

- Domain Skill Contract structure added
- sensitivity modes preserved
- lifecycle attachment to Change Brief, Bug Brief, module, or working-context added
- artifact awareness and Return Handoff added

Remaining validation:

- validate with Markdown, PDF, URL, Word, and log examples
- verify sensitive content is summarized or path-indexed safely

### project-develop

Status: contract-aligned.

Evidence:

- Change Brief creation/resume required
- Context Enrichment, Clarification, Context Lock, and External Skill Bridge gates declared
- lightweight-answer boundary added
- external planning/TDD/execution handoff added

Remaining validation:

- run Case 3 with active/read-only/reference-only scopes
- verify planning artifacts are linked back to Change Brief and artifact registry

### project-fix

Status: contract-aligned.

Evidence:

- Bug Brief creation/resume required
- Bug Evidence Gate and Context Lock Gate declared
- systematic-debugging is explicitly a scoped bridge
- Return Handoff and verification boundaries added

Remaining validation:

- run Case 2 with a realistic failed log or test
- verify candidate scope escalation before editing another service

### project-finish

Status: contract-aligned.

Evidence:

- Verification, Knowledge Sync, Artifact Sync, and Progress Dashboard Sync gates declared
- dashboard evidence rule referenced
- partial verification and residual risk behavior preserved

Remaining validation:

- run Case 5 with partial verification
- verify dashboard facts link to evidence and do not become source of truth

### project-review

Status: contract-aligned.

Evidence:

- Review Gate, Artifact Sync check, Progress Dashboard Sync check, and Evolution Gate declared
- findings-first stance preserved
- scope/wiki/artifact/dashboard/bridge drift checks added
- Lifecycle Quality output added

Remaining validation:

- run Case 6 on a real diff
- run Case 8 or Case 9 to verify evaluator/Dolores remains non-blocking

## Reference-Level Status

| Reference | Status | Notes |
|---|---|---|
| [north-star.md](north-star.md) | Updated | Defines Level 3.5 target and done means. |
| `full-lifecycle-implementation-plan.zh.md` | Added | Main implementation plan. |
| `lifecycle-router.md` | Added | Router decisions, routing records, resume behavior, handoff contract. |
| `lifecycle-gates.md` | Added | Shared Gate Stack. |
| `domain-skill-contract.md` | Added | Required child skill structure. |
| `bug-brief.md` | Added | Bug lifecycle session protocol. |
| `change-brief.md` | Present | Requirement lifecycle session protocol; should be included in commit if this change set is accepted. |
| `progress-dashboard.md` | Added | Static HTML dashboard protocol and evidence rules. |
| `continuous-evolution.md` | Added | evaluator / Dolores protocol. |
| `acceptance-cases.md` | Updated | Level 3.5 pressure cases. |
| `static-lifecycle-review.md` | Added | Static review of case coverage. |
| `dry-run-report-2026-06-04.md` | Added | Simulated dry run for Cases 1, 2, 3, 5, 6, 8, 9. |
| older `*-mvp.md` references | Legacy | Still exist for historical detail; new implementation should prefer the Level 3.5 references above. |

## Remaining Priority

1. Run Case 10 on a real project. Fixture dry run passed on 2026-06-04.
2. Record actual dry-run findings.
3. Patch any over-routing, missing handoff, missing artifact sync, or dashboard evidence issues found during runtime testing.
4. Only then claim broad testing readiness.

## Do Not Do Yet

- Do not build automated Agent lifecycle or Runtime Eval CI integration before Case 10 passes; deterministic repository-integrity CI is allowed.
- Do not add reminder automation as a core dependency.
- Do not require codegraph generation.
- Do not implement a full OpenSpec clone.
- Do not add GitHub issue or PR automation as required behavior.
- Do not expand `.llm-wiki` into a large documentation system.
- Do not make evaluator or Dolores run on every normal task.

## Ready For Broad Testing When

- Natural feature, bug, finish, review, resume, and lightweight discussion prompts route correctly in real testing. Fixture Case 10 has passed.
- Full work creates or resumes a lifecycle session without duplicates.
- External skill calls are scoped and return through handoff.
- Finish sync updates wiki, artifacts, and dashboard state only from evidence.
- Review detects scope, wiki, artifact, dashboard, and bridge drift from real diffs.
- Evaluator or Dolores can be triggered for lifecycle quality issues without blocking ordinary delivery.
