# Dry Run Report: 2026-06-04

This report simulates the key Level 3.5 acceptance cases against the current Project Develop Copilot skill documents.

It is not a real project execution. It checks whether the router, child skills, and references now give an agent enough instructions to route and continue the lifecycle correctly.

## Summary

Result: simulated pass for Cases 1, 2, 3, 5, 6, 8, and 9.

Case 10 fixture validation passed after this simulated report; see `case10-fixture-run-2026-06-04.md`. A real project run is still not proven.

## Case 1: Lightweight Design Discussion

Prompt:

```text
我们先讨论 Project Develop Copilot 的 dashboard 设计，不开发，也不要更新项目状态。
```

Simulated route:

```text
project-develop-copilot
-> mode: lightweight-answer
-> primary_stage: none
-> lifecycle_session: none
```

Expected behavior from docs:

- Root `SKILL.md` says design discussion without implementation routes to lightweight-answer.
- `lifecycle-router.md` says lightweight answers do not create Change Brief, Bug Brief, working-context, artifact rows, dashboard updates, or code changes.
- `progress-dashboard.md` says ordinary lightweight discussion should not update dashboard.

Result: pass.

Residual risk: live agents may still over-eagerly offer to save decisions. This should be watched in real prompt testing.

## Case 2: Natural Bug Request With External Debugging Bridge

Prompt:

```text
我想改一个 bug，这是 payment callback 的失败日志。先从 payment-service 看，如果需要 order-service，先说明为什么。
```

Simulated route:

```text
project-develop-copilot
-> mode: full-lifecycle
-> primary_stage: project-fix
-> lifecycle_session: Bug Brief
-> next_gate: Context Enrichment Gate + Bug Evidence Gate
-> optional_bridge: systematic-debugging after scoped evidence
```

Expected behavior from docs:

- Root router maps bug/log/error/failed test to `project-fix`.
- `project-fix/SKILL.md` requires Bug Brief creation/resume, Bug Evidence Gate, Context Lock Gate, scoped systematic-debugging bridge, and Return Handoff.
- `bug-brief.md` defines active/read-only/candidate/excluded scope and escalation history.
- `lifecycle-gates.md` requires Context Handoff before external bridges.

Result: pass.

Residual risk: real project testing must verify order-service stays candidate/read-only until escalation is recorded.

## Case 3: Feature Request With Change Brief And Scope Lock

Prompt:

```text
我要开发支付回调补偿功能，只允许先改 payment-service 和 order-service，notification-service 只能参考。
```

Simulated route:

```text
project-develop-copilot
-> mode: full-lifecycle
-> primary_stage: project-develop
-> lifecycle_session: Change Brief
-> next_gate: Context Enrichment Gate -> Clarification Gate -> Context Lock Gate
```

Expected behavior from docs:

- Root router maps feature/requirement/implementation to `project-develop`.
- `project-develop/SKILL.md` requires Change Brief creation/resume and confirms this is not lightweight-answer.
- It records active/read-only/candidate/excluded scope before planning or implementation.
- It runs Clarification Gate and Context Lock Gate before execution.
- It treats external planning/TDD/execution skills as bridges.

Result: pass.

Residual risk: live testing must verify notification-service remains read-only/reference-only and does not become active by implication.

## Case 5: Finish Sync With Dashboard Evidence

Prompt:

```text
Use project finish. Tests could not run locally, but compile passed and manual verification was done. Update the project progress page if needed.
```

Simulated route:

```text
project-develop-copilot
-> mode: full-lifecycle
-> primary_stage: project-finish
-> next_gate: Verification Gate -> Knowledge Sync Gate -> Artifact Sync Gate -> Progress Dashboard Sync Gate
```

Expected behavior from docs:

- Root router maps finish/done/sync/update progress to `project-finish`.
- `project-finish/SKILL.md` requires verification evidence or explicit accepted limitation.
- It owns Knowledge Sync, Artifact Sync, and Progress Dashboard Sync.
- `progress-dashboard.md` requires all dashboard facts to trace back to `.llm-wiki`, artifact registry, verification records, git diff, source proxy, or user decision.

Result: pass.

Residual risk: a real dashboard HTML file is still needed to test maintainability and evidence link conventions.

## Case 6: Review Finds Scope, Wiki, Artifact, And Dashboard Drift

Prompt:

```text
Use project review before commit. 检查这个改动有没有范围漂移、wiki 漂移、artifact 漂移和 dashboard 漂移。
```

Simulated route:

```text
project-develop-copilot
-> mode: full-lifecycle
-> primary_stage: project-review
-> next_gate: Review Gate + Evolution Gate if process risk appears
```

Expected behavior from docs:

- Root router maps review/risk/before commit to `project-review`.
- `project-review/SKILL.md` checks code risk, verification gaps, scope drift, wiki drift, artifact drift, dashboard drift, bridge consistency, and lifecycle quality.
- It reports findings first.
- `progress-dashboard.md` defines dashboard drift conditions.
- `continuous-evolution.md` defines evaluator and Dolores triggers when lifecycle quality issues appear.

Result: pass.

Residual risk: real diff testing is required to prove scope drift is detected from actual changed files.

## Case 8: Conversation Review / Dolores Trigger

Prompt:

```text
复盘一下刚刚这个 project develop 流程是不是跑偏了，用 Dolores 视角看下。
```

Simulated route:

```text
project-develop-copilot
-> mode: lifecycle-quality
-> primary_stage: project-review or conversation-review / Dolores bridge
-> next_gate: Evolution Gate
```

Expected behavior from docs:

- Root router maps Dolores/self-review to lifecycle-quality.
- `project-review/SKILL.md` has `dolores-trigger-review` mode and Lifecycle Quality output.
- `continuous-evolution.md` defines Dolores lifecycle trace checks and privacy boundaries.

Result: pass.

Residual risk: live testing must ensure Dolores remains a lifecycle trace review, not a generic summary or automatic skill rewrite.

## Case 9: Skill Evaluator Trigger From Review Finding

Prompt:

```text
Review 发现 project-fix 跳过了 Bug Evidence Gate。评估一下这个 skill 需要怎么改，但先不要直接改。
```

Simulated route:

```text
project-develop-copilot
-> mode: lifecycle-quality
-> primary_stage: project-review or skill-evaluator bridge
-> next_gate: Evolution Gate
```

Expected behavior from docs:

- Root router maps skill failure/evaluator requests to lifecycle-quality.
- `continuous-evolution.md` requires diagnosis, eval gap, and minimal patch plan.
- It explicitly says not to patch skills immediately unless the user asks to enter modification mode.
- `project-review/SKILL.md` exposes evaluator trigger decision in Lifecycle Quality output.

Result: pass.

Residual risk: live testing should confirm the agent does not over-patch after evaluator analysis.

## Fixture Proven, Real Project Not Yet Proven: Case 10

Case 10 fixture now exists and passed mechanical checks. A real project still needs:

- `.llm-wiki` init/refresh
- source ingest
- Change Brief creation
- working-context creation
- implementation or simulated changed files
- verification evidence
- artifact registry
- dashboard update
- review drift checks

Static docs cover the route, but runtime behavior is not proven.

## Fixes Applied During Dry Run

- README install examples were updated to install the top-level `project-develop-copilot` router by default.
- README local development command was changed to `npx skills add . --list` to show root and child skills.
- Static review now has a separate dry-run report instead of mixing simulated readiness with real execution.

## Next Step

Create a tiny fixture project or use a real repository to run Case 10. The fixture should include:

```text
.git/
.llm-wiki/
docs/prd/payment-callback.md
payment-service/
order-service/
notification-service/
.llm-wiki/dashboard/progress.html
```

Then run the full prompt sequence from `acceptance-cases.md` and record actual behavior.