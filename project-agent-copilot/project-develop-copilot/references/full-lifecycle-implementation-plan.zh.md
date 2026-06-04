# Project Develop Copilot 完整生命周期实现计划

> **For agentic workers:** 按本计划实施时，先读 `references/north-star.md` 和 `DESIGN.zh.md`。实现阶段必须使用生命周期视角，不要把七个 child skills 当成互不相关的 MVP 小工具逐个修补。

**Goal:** 把 Project Develop Copilot 从分散的 child skills 升级为一个可自然进入、可恢复、可桥接外部 skills、可同步证据和 dashboard、可持续进化的完整 Level 3.5 项目开发生命周期。

**Architecture:** 新增顶层 router skill 作为唯一自然入口；七个 child skills 改造成 domain stage skills；`references/` 承载短协议；`.llm-wiki` 承载项目状态；external skills 通过 Context Handoff / Return Handoff 接入；evaluator 和 Dolores 作为非阻塞的持续进化层。

**Tech Stack:** Codex / agents skills Markdown, `.llm-wiki` Markdown protocol, static HTML progress dashboard, optional Superpowers / Thinking Skills / OpenSpec-style bridge.

---

## 文件结构

### 新增

- `project-agent-copilot/project-develop-copilot/SKILL.md`：顶层 Lifecycle Router / 总入口。
- `project-agent-copilot/project-develop-copilot/references/full-lifecycle-implementation-plan.zh.md`：本计划。
- `project-agent-copilot/project-develop-copilot/references/lifecycle-router.md`：router 决策协议和 routing record。
- `project-agent-copilot/project-develop-copilot/references/lifecycle-gates.md`：Gate Stack 的最小可执行规则。
- `project-agent-copilot/project-develop-copilot/references/bug-brief.md`：Bug Brief 协议。
- `project-agent-copilot/project-develop-copilot/references/progress-dashboard.md`：静态 HTML dashboard 协议。
- `project-agent-copilot/project-develop-copilot/references/domain-skill-contract.md`：所有 project domain skills 的结构规范。
- `project-agent-copilot/project-develop-copilot/references/continuous-evolution.md`：evaluator / Dolores / eval case 约定。
- `project-agent-copilot/project-develop-copilot/evals/README.md`：后续 eval runner 的占位说明。
- `project-agent-copilot/project-develop-copilot/cases/failures/README.md`：抽象失败案例约定。
- `project-agent-copilot/project-develop-copilot/cases/golden/README.md`：黄金路径案例约定。

### 修改

- `project-agent-copilot/project-develop-copilot/README.md`：从 MVP 说明改为完整生命周期说明。
- `project-agent-copilot/project-develop-copilot/README.zh.md`：同步中文说明。
- `project-agent-copilot/project-develop-copilot/references/north-star.md`：方向锚点已经切换到 Level 3.5。
- `project-agent-copilot/project-develop-copilot/references/capability-gap-audit.md`：改成完整生命周期差距审计。
- `project-agent-copilot/project-develop-copilot/references/acceptance-cases.md`：改成完整生命周期验收场景。
- `project-agent-copilot/project-develop-copilot/project-init/SKILL.md`：补 Domain Skill Contract 结构和 router handoff。
- `project-agent-copilot/project-develop-copilot/project-ingest/SKILL.md`：补 source ingest 与 lifecycle session 连接。
- `project-agent-copilot/project-develop-copilot/project-develop/SKILL.md`：补 Change Brief、Context Lock、External Bridge、dashboard sync。
- `project-agent-copilot/project-develop-copilot/project-fix/SKILL.md`：补 Bug Brief、Bug Evidence Gate、scope escalation、Return Handoff。
- `project-agent-copilot/project-develop-copilot/project-finish/SKILL.md`：补 Knowledge Sync、Artifact Sync、Progress Dashboard Sync。
- `project-agent-copilot/project-develop-copilot/project-review/SKILL.md`：补 Review Gate、drift checks、evaluator / Dolores 触发。

---

## Task 1: 新增顶层 Lifecycle Router

**Files:**

- Create: `project-agent-copilot/project-develop-copilot/SKILL.md`
- Create: `project-agent-copilot/project-develop-copilot/references/lifecycle-router.md`
- Modify: `project-agent-copilot/project-develop-copilot/README.md`
- Modify: `project-agent-copilot/project-develop-copilot/README.zh.md`

**Purpose:** 让用户只需要记住 Project Develop Copilot 一个入口。任何自然请求先进入 router，由 router 判断 lightweight-answer 或完整 lifecycle。

- [ ] Step 1: 编写 router skill frontmatter。

```yaml
---
name: project-develop-copilot
description: Use when the user wants project development help from natural intent, including requirements, bugs, logs, design discussion, file lookup, progress, finish, review, resume, or routing into project lifecycle skills.
---
```

- [ ] Step 2: 在 router skill 中加入 Required First Check。

```markdown
## Required First Check

1. Decide whether the request is lightweight-answer or full lifecycle.
2. If lightweight-answer applies, answer from available evidence without creating lifecycle state.
3. If full lifecycle applies, resolve project root and create or resume a Lifecycle Session.
4. Select one primary stage skill.
5. Select optional secondary bridges only after project scope is known.
```

- [ ] Step 3: 在 `lifecycle-router.md` 写入 routing decision table。

```markdown
| User signal | Router result |
|---|---|
| asks where a file/doc is | lightweight-answer |
| asks to discuss design without implementation | lightweight-answer |
| asks to implement a feature | project-develop |
| provides PRD and wants progress | project-develop or project-ingest then project-develop |
| reports bug/log/error/test failure | project-fix |
| says finish/done/sync/update status | project-finish |
| asks review/before commit/risk check | project-review |
| says continue previous work | resume latest lifecycle session, then choose stage |
```

- [ ] Step 4: 定义 routing record 最小字段。

```markdown
## Routing Record

- intent:
- primary_stage:
- secondary_bridges:
- confidence:
- reason:
- next_gate:
- routed_at:
```

- [ ] Step 5: 验收 router 不得直接替代 child skill。

Expected behavior:

```text
Router chooses stage and passes scoped context. Router does not perform full bug diagnosis, full implementation, or final review by itself.
```

---

## Task 2: 抽出 Gate Stack 协议

**Files:**

- Create: `project-agent-copilot/project-develop-copilot/references/lifecycle-gates.md`
- Modify: all seven `project-*/SKILL.md`

**Purpose:** 把 Gate 从设计概念变成每个 skill 可执行、可检查的规则。

- [ ] Step 1: 在 `lifecycle-gates.md` 定义 Gate 表。

```markdown
| Gate | Required before | Minimum output |
|---|---|---|
| Context Discovery Gate | any full lifecycle work | project root, stale/new context signals |
| Context Enrichment Gate | planning/debugging/implementation | active sources, relevant wiki pages, scope split |
| Clarification Gate | requirement planning | goal, acceptance, active scope, non-goals |
| Bug Evidence Gate | bug fixing | symptom, evidence, reproduction status |
| Context Lock Gate | plan execution or code edits | locked active/read-only/candidate/excluded scopes |
| External Skill Bridge Gate | external skill call | Context Handoff |
| Verification Gate | finish or done claim | command/result/limitation |
| Knowledge Sync Gate | finish | updated requirement/bug/module/source summaries |
| Artifact Sync Gate | finish/review/dashboard | artifact registry row |
| Progress Dashboard Sync Gate | finish/review/status update | dashboard facts linked to evidence |
| Review Gate | before handoff/commit/PR | findings-first review or no-finding statement |
```

- [ ] Step 2: 每个 child skill 增加 `## Owned Gates`。

Expected mapping:

```text
project-init: Context Discovery, Knowledge Sync
project-ingest: Context Discovery, Knowledge Sync, Artifact Sync
project-develop: Context Enrichment, Clarification, Context Lock, External Skill Bridge
project-fix: Context Enrichment, Bug Evidence, Context Lock, External Skill Bridge
project-finish: Verification, Knowledge Sync, Artifact Sync, Progress Dashboard Sync
project-review: Review, Artifact Drift, Dashboard Drift, evaluator/Dolores trigger
```

- [ ] Step 3: 每个 child skill 增加 gate skip 边界。

Required rule:

```markdown
Do not skip an owned gate silently. If a gate cannot be completed, record the limitation and the next safest action.
```

---

## Task 3: 完成 Lifecycle Session 协议

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/references/change-brief.md`
- Create: `project-agent-copilot/project-develop-copilot/references/bug-brief.md`
- Modify: `project-agent-copilot/project-develop-copilot/references/scoped-working-context.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-develop/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-fix/SKILL.md`

**Purpose:** 让需求、bug、跨模块上下文成为可恢复状态，而不是一次性回答。

- [ ] Step 1: `change-brief.md` 移除 MVP 语言，加入 Routing 区。

```markdown
## Routing

- intent:
- primary_stage:
- secondary_bridges:
- confidence:
- reason:
- next_gate:
- routed_at:
```

- [ ] Step 2: 新建 `bug-brief.md`，包含 DESIGN 中的 Bug Brief Minimum。

Required sections:

```markdown
# Bug Brief: <bug-id>

## Summary
## Routing
## Source
## Symptom
## Expected
## Evidence
## Reproduction
## Scope
## Diagnosis
## Fix Plan
## Verification
## Artifacts
## Open Questions
## Residual Risk
```

- [ ] Step 3: `project-develop` 创建或恢复 Change Brief。

Expected behavior:

```text
A requirement discussion can stop after clarification. It still leaves a recoverable Change Brief if the user asks to save the decision or if full lifecycle has started.
```

- [ ] Step 4: `project-fix` 创建或恢复 Bug Brief。

Expected behavior:

```text
A bug request records evidence and reproduction status before broad edits. If reproduction is blocked, the limitation is explicit.
```

---

## Task 4: 改造七个 Domain Skills

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/project-init/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-ingest/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-develop/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-fix/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-finish/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-review/SKILL.md`
- Create: `project-agent-copilot/project-develop-copilot/references/domain-skill-contract.md`

**Purpose:** 让每个 child skill 都像 Thinking Skills 的 domain skill 一样 router-friendly。

- [ ] Step 1: 在 `domain-skill-contract.md` 固化结构。

```markdown
## Purpose
## When to Use
## When Not to Use
## Owned Gates
## Required First Check
## Core Process
## Mode / Entry Selection
## Inputs
## Outputs
## Context Handoff
## Return Handoff
## Boundaries
## Common Mistakes
```

- [ ] Step 2: 七个 SKILL.md 都补齐上述结构。

Validation command:

```bash
rg -n "^## (Purpose|When to Use|When Not to Use|Owned Gates|Required First Check|Core Process|Mode / Entry Selection|Inputs|Outputs|Context Handoff|Return Handoff|Boundaries|Common Mistakes)" project-agent-copilot/project-develop-copilot/project-*/SKILL.md
```

Expected:

```text
Each child skill has all required section headings.
```

- [ ] Step 3: description 只写触发条件，不总结流程。

Bad:

```yaml
description: Use when fixing bugs - gathers evidence, runs debugging, updates wiki, verifies, and syncs dashboard.
```

Good:

```yaml
description: Use when diagnosing or fixing a project bug, error, failed test, regression, incident, log symptom, or unexpected behavior with scoped project context and LLM Wiki bug summaries.
```

---

## Task 5: 实现 External Skill Bridge Contract

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/references/superpowers-bridge.md`
- Modify: `project-agent-copilot/project-develop-copilot/references/tool-bridge.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-develop/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-fix/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-review/SKILL.md`

**Purpose:** 解决“用户说改 bug 触发了 systematic-debugging 等外部 skills，怎么仍然进入生命周期”的问题。

- [ ] Step 1: 定义 Context Handoff。

```markdown
## Context Handoff

- lifecycle_session:
- user_intent:
- active_sources:
- active_scope:
- read_only_scope:
- candidate_scope:
- excluded_scope:
- current_gate:
- requested_bridge:
- constraints:
```

- [ ] Step 2: 定义 Return Handoff。

```markdown
## Return Handoff

- bridge_used:
- result_summary:
- changed_assumptions:
- recommended_scope_changes:
- artifacts:
- verification_notes:
- lifecycle_updates_needed:
```

- [ ] Step 3: 写入强规则。

```text
External skills are bridges, not lifecycle owners. They must not choose project scope from scratch, bypass verification, or declare project completion.
```

---

## Task 6: 完成 Artifact Registry 和 Progress Dashboard 协议

**Files:**

- Create: `project-agent-copilot/project-develop-copilot/references/progress-dashboard.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-finish/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-review/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/references/llm-wiki-mvp.md` or create successor reference if renaming is deferred

**Purpose:** 让 dashboard 成为证据索引，不成为新的事实源。

- [ ] Step 1: 定义 artifact registry row。

```markdown
| id | type | path | owner | related_session | status | last_checked | notes |
|---|---|---|---|---|---|---|---|
```

- [ ] Step 2: 定义 dashboard evidence rule。

```text
Every dashboard status must link back to .llm-wiki, artifact registry, verification record, or git diff evidence.
```

- [ ] Step 3: 定义静态 HTML 区块。

```text
Top half: Project Cockpit
Bottom half: Development Flow Board
Reserved: Document Evidence
Reserved: Skills Maintenance Convention
```

- [ ] Step 4: 在 finish/review 中加入 dashboard drift 检查。

Expected:

```text
If dashboard says done but verification or Change Brief is not done, review reports dashboard drift.
```

---

## Task 7: 接入 Continuous Skill Evolution

**Files:**

- Create: `project-agent-copilot/project-develop-copilot/references/continuous-evolution.md`
- Create: `project-agent-copilot/project-develop-copilot/evals/README.md`
- Create: `project-agent-copilot/project-develop-copilot/cases/failures/README.md`
- Create: `project-agent-copilot/project-develop-copilot/cases/golden/README.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-review/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/SKILL.md`

**Purpose:** 用 `skill-evaluator` 和 `conversation-review / Dolores` 做持续进化，但默认不阻塞交付。

- [ ] Step 1: 定义 evaluator 触发条件。

```text
routing mistake, gate skip, scope drift, artifact drift, dashboard drift, external bridge bypass, over-heavy response, premature implementation, missing verification
```

- [ ] Step 2: 定义 Dolores 触发条件。

```text
user explicitly asks for conversation self-review, review finds process-level risk, or a lifecycle run should become a golden/failure case
```

- [ ] Step 3: 定义隐私边界。

```text
Do not store raw private conversations, customer data, logs, credentials, or sensitive project context. Save abstract failure patterns or golden behavior only.
```

- [ ] Step 4: 在 `project-review` 增加非阻塞输出。

```markdown
## Lifecycle Quality

- evaluator_needed: yes/no
- dolores_review_needed: yes/no
- reason:
- suggested_artifact:
```

---

## Task 8: 更新差距审计和验收用例

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/references/capability-gap-audit.md`
- Modify: `project-agent-copilot/project-develop-copilot/references/acceptance-cases.md`

**Purpose:** 把旧 MVP 审计变成完整生命周期验收。

- [ ] Step 1: capability audit 改为 Level 3.5 表。

Required rows:

```text
Top-level router
Lightweight Answer Mode
Lifecycle Session
Routing Record
Gate Stack
External Skill Bridge
Domain Skill Contract
Artifact Registry
Progress Dashboard
Evaluator / Dolores
Acceptance pressure cases
```

- [ ] Step 2: acceptance cases 增加至少这些场景。

```text
1. Lightweight design discussion does not create lifecycle state.
2. Natural bug request routes to project-fix even when systematic-debugging is useful.
3. Feature request creates Change Brief and locks scope before implementation.
4. External skill output returns through Return Handoff.
5. Finish sync updates wiki, artifacts, dashboard evidence.
6. Review detects scope/wiki/artifact/dashboard drift.
7. Dolores review turns a lifecycle failure into abstract eval candidate.
```

---

## Task 9: 集中验证

**Files:**

- All changed files.

**Purpose:** 完整开发完再测试，但测试对象必须是完整生命周期，不是单个 skill 的孤立段落。

- [ ] Step 1: 结构验证。

```bash
rg -n "MVP|最小可行|默认 MVP" project-agent-copilot/project-develop-copilot
rg -n "^## When to Use|^## When Not to Use|^## Owned Gates|^## Required First Check|^## Return Handoff|^## Common Mistakes" project-agent-copilot/project-develop-copilot/project-*/SKILL.md
```

Expected:

```text
No stale MVP language in user-facing goal docs. All child skills expose router-friendly sections.
```

- [ ] Step 2: install discovery 验证。

```bash
npx skills add . --list
```

Expected:

```text
project-develop-copilot and all seven child project skills are discoverable.
```

- [ ] Step 3: pressure scenario dry run。

Use `references/acceptance-cases.md` after it is updated. Do not claim complete until natural entry, external bridge, finish sync, review drift, and evaluator/Dolores trigger all pass at least one scenario.

---

## 已发现的当前偏差

- 顶层 `project-develop-copilot/SKILL.md` 已建立，用户可以从自然语言进入 router。
- README、north-star、DESIGN 和核心 references 已从 MVP 语言更新为完整生命周期目标。
- 七个 child skills 已统一 Domain Skill Contract 结构，包括 `project-query` 只读讨论入口。
- Change Brief、Bug Brief、Lifecycle Gates、External Bridge、Dashboard 和 Continuous Evolution 已有独立 reference。
- 剩余风险转向真实项目回归验证：外部 skills bridge、dashboard 写回、Artifact Registry、Evaluator / Dolores 触发是否稳定。
- Progress Dashboard 已在设计中出现，但还缺可执行 reference。
- evaluator / Dolores 已在设计中出现，但还缺 reference、case 目录和 review 触发输出。

## 完成判定

这一版完成后，用户应该可以说：

```text
我想改一个 bug，这是日志。
```

系统自然进入：

```text
project-develop-copilot router
-> full lifecycle
-> Bug Brief
-> Context Enrichment / Bug Evidence Gate
-> project-fix
-> optional systematic-debugging bridge
-> Return Handoff
-> Verification
-> project-finish
-> Artifact / Dashboard Sync
-> project-review
-> evaluator or Dolores only if needed
```

用户也可以说：

```text
我们先讨论这个设计，不开发。
```

系统自然停在 lightweight-answer，不创建多余状态。这两个入口都顺，才说明这次没有再变成割裂的 skill 集合。