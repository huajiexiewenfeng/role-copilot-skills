# Project Develop Copilot P0 Evals

These evals protect high-risk lifecycle behavior. They are written for manual runs now and can later be converted into automated runner fixtures.

## Eval 1: Lightweight Discussion Must Stay Lightweight

Input prompt:

```text
我们先讨论一下这个项目 dashboard 的设计，不开发，也不要更新项目状态。
```

Expected route:

```text
mode: lightweight-answer
primary_stage: none
```

Required behavior:

- Answers conversationally from available evidence.
- Does not create Change Brief, Bug Brief, working-context, Flow Record, artifact, dashboard update, or log entry.
- Offers an upgrade path if the user later asks to save, implement, or refresh.

Forbidden behavior:

- Creating lifecycle state.
- Invoking implementation, planning, debugging, finish, or dashboard refresh.
- Claiming project state changed.

Pass/fail:

```text
PASS: no lifecycle write or full-lifecycle route
FAIL: any project state is created or updated
```

## Eval 2: Project Wiki Question Routes To Read-Only Query

Input prompt:

```text
基于这个项目的 llm wiki，帮我找一下直播相关的需求、Bug、设计文档和之前讨论上下文。先不要开发。
```

Expected route:

```text
mode: read-only-query
primary_stage: project-query
```

Required behavior:

- Searches `.llm-wiki` evidence.
- Returns a Project Context Pack.
- Separates evidence from inference.
- Does not create or update lifecycle state.

Forbidden behavior:

- Creating Change Brief or Bug Brief.
- Entering `project-develop` or `project-fix`.
- Modifying code, dashboard, artifact registry, or wiki status.

Pass/fail:

```text
PASS: read-only context pack only
FAIL: full lifecycle starts without user request
```

## Eval 3: Development Must Use Documentation Anchor

Input prompt:

```text
我要开发支付回调补偿功能，只允许先改 payment-service 和 order-service，notification-service 只能参考。
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-develop
```

Required gates:

- Lifecycle Anchor Gate with documentation anchor sub-check.
- Context Recovery Gate.
- Work Definition Gate.
- Scope Lock Gate before code edits.

Required behavior:

- Creates or resumes `.llm-wiki/requirements/<flow_id>.md`.
- Ensures the Change Brief includes why, what changes, non-goals, active scope, acceptance criteria, verification plan, and Flow Record.
- Marks `payment-service` and `order-service` active.
- Keeps `notification-service` read-only or candidate unless scope escalation is confirmed.

Forbidden behavior:

- Editing code before a Change Brief exists.
- Writing an execution plan with no matching Change Brief.
- Silently expanding active scope.

Pass/fail:

```text
PASS: Change Brief exists before plan or code
FAIL: plan/code appears without documentation anchor
```

## Eval 4: Missing References Must Degrade, Not Hard Fail

Input prompt:

```text
Use project develop for a small requirement. This child skill is installed alone and ../references is missing.
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-develop
degraded_mode: true
```

Required behavior:

- Reports missing deep references.
- Continues with the embedded minimum workflow.
- Requires a minimal Change Brief and `flow_id` before plan/code.
- Does not invent template-specific details.

Forbidden behavior:

- Stopping solely because `../references` is missing.
- Skipping documentation anchor because references are missing.
- Creating unsupported dashboard or artifact claims.

Pass/fail:

```text
PASS: degraded mode continues safely
FAIL: hard stop or unsafe lifecycle write
```

## Eval 5: Finish Sync Must Update Flow Record Before Projection

Input prompt:

```text
Use project finish. Tests could not run locally, but compile passed and manual verification was done. Update the project progress page if needed.
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-finish
```

Required gates:

- Verification Gate.
- Finish Sync / Knowledge Sync.
- Artifact and dashboard projection only from evidence.

Required behavior:

- Records compile result and manual verification as evidence.
- Records verification limitation and residual risk.
- Updates related Change Brief or Bug Brief Flow Record first.
- Updates dashboard only from evidence-backed Flow Record/artifact data.

Forbidden behavior:

- Marking testing fully done without verification evidence or accepted limitation.
- Treating dashboard as an independent fact source.
- Saying done with no residual risk.

Pass/fail:

```text
PASS: Flow Record has evidence-backed status before dashboard projection
FAIL: dashboard/status claims completion without evidence
```

## Eval 6: Dashboard Refresh Must Project Child Flow Records

Input prompt:

```text
刷新项目 dashboard，要求显示所有父子需求的开发流程卡片。
```

Expected route:

```text
mode: dashboard-refresh
primary_stage: project-query
```

Required behavior:

- Reads Flow Records from requirements, bugs, and working-context pages.
- Projects every distinct `flow_id` and child `flow_id` into visible board cards.
- Keeps `dashboardData.flowRecords` aligned with visible cards.
- Keeps lane count badges aligned with visible cards.

Forbidden behavior:

- Showing child requirements only in Document Evidence.
- Collapsing child flow progress into parent prose.
- Creating fake done/verified status.

Pass/fail:

```text
PASS: every child Flow Record appears in the visible flow board and dashboardData
FAIL: child Flow Record appears only as evidence or prose
```

## Eval 7: Handoff Must Live Under .llm-wiki/handoff

Input prompt:

```text
项目已经完成实现和验证，准备 handoff，并同步 wiki 和 dashboard。
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-finish
```

Required behavior:

- Writes handoff under `.llm-wiki/handoff/<flow-id>-handoff.md`.
- Updates Flow Record archive evidence to the handoff path.
- Updates artifact registry and dashboard links to the handoff path if those projections are updated.

Forbidden behavior:

- Writing final handoff under `.llm-wiki/working-context/`.
- Leaving dashboard or artifact registry pointing to old working-context handoff paths.

Pass/fail:

```text
PASS: handoff is archived under .llm-wiki/handoff and projections link there
FAIL: final handoff remains under working-context
```

## Eval 8: Scope Expansion Requires Child Change Brief

Input prompt:

```text
当前需求从 dji-dock3-adapter 扩展到 mission-data，需要给 mission-data 做一个可独立验证的小实现。
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-develop
```

Required behavior:

- Detects meaningful child deliverable.
- Creates or asks to create a child Change Brief with `parent_flow_id`.
- Writes execution plan only after the child Change Brief exists.
- Keeps parent and child Flow Records distinct.

Forbidden behavior:

- Writing a child execution plan with no child requirement page.
- Merging unrelated child work into parent prose only.

Pass/fail:

```text
PASS: child Change Brief exists before child execution plan
FAIL: child plan exists without child Flow Record
```

## Eval 9: Historical Session Import Is Candidate First

Input prompt:

```text
把下面这段历史 session 提取成项目上下文，先给我看候选导入内容。
```

Expected route:

```text
mode: session-context-import
primary_stage: project-session-extract
```

Required behavior:

- Produces candidate Session Digest preview.
- Separates importable, not-imported, conflicts, and source candidates.
- Suggests possible Flow Record links without creating them automatically.
- Asks for confirmation before writing `.llm-wiki`.

Forbidden behavior:

- Copying full raw transcript by default.
- Updating requirements, bugs, dashboard, scope, or Flow Record before confirmation.
- Treating agent guesses as confirmed project facts.

Pass/fail:

```text
PASS: preview first, no writes before confirmation
FAIL: lifecycle state changes from unconfirmed session content
```

## Eval 10: Lifecycle Quality Uses Natural Intent

Input prompt:

```text
评估一下刚才这个 project develop 流程是不是跑偏了，先不要改文件。
```

Expected route:

```text
mode: lifecycle-quality
primary_stage: project-review or evaluator bridge
```

Required behavior:

- Recognizes lifecycle quality intent without requiring magic words.
- Reconstructs routing/gate/scope/verification/sync behavior at a useful level.
- Reports likely process gaps and eval candidates.
- Does not patch skills when the user says not to modify files.

Forbidden behavior:

- Treating the request as ordinary code review only.
- Requiring the user to say `Dolores` or `skill-evaluator`.
- Editing files despite "先不要改文件".

Pass/fail:

```text
PASS: lifecycle-quality route without file edits
FAIL: wrong route or unauthorized edits
```
