# Flow Record 执行计划

## 目标

把 Flow Record 从设计文档落到真实可用的 project skills 行为中。

最终效果：

```text
需求/设计文档
-> flow_id
-> Change Brief / Bug Brief
-> 执行计划
-> 开发实现
-> 测试验证
-> 归档交付
-> dashboard 看板卡片
```

用户不需要手动维护表格。LLM / skills 根据证据维护 Flow Record，只在影响范围、执行计划、验证或风险时询问用户。

## 当前状态

已完成：

- `references/flow-record.md` 定义主设计。
- `references/change-brief.md` 增加 Flow Record 表结构。
- `references/progress-dashboard.md` 定义看板卡片来自 Flow Record。
- `project-develop` 已要求创建/更新 Flow Record。
- `project-query dashboard-refresh` 已要求从 Flow Record 刷新看板。
- `project-finish` 已要求更新 development/testing/archive。
- `project-review` 已要求检查 dashboard 和 Flow Record drift。

仍需落地：

- init/ingest/develop/fix/finish/query/review 的执行细节还需要更具体。
- dashboard 模板还只是静态骨架，没有明确的卡片生成契约。
- 需要真实测试用例验证一个需求能从文档串到看板。

## P0：最小可用闭环

Status: implemented in skill docs on 2026-06-05; pending real project dry-run.

### 1. 完善 Change Brief 模板

Status: done.

改动：

- `references/templates.md`
- `references/change-brief.md`

要求：

- Requirement Summary 模板内加入 `## Flow Record`。
- 明确 `source/design/plan/development/testing/archive` 默认状态。
- 示例要足够短，避免变成复杂表单。

验收：

- 新建 Change Brief 时默认包含 Flow Record。
- 用户不需要手动填写。

### 2. project-develop 创建或恢复 Flow Record

Status: done.

改动：

- `project-develop/SKILL.md`
- 必要时补 `references/change-brief.md`

要求：

- 创建 Change Brief 时生成 `flow_id`。
- 将 active source/design 文档写入 `source` 或 `design` step evidence。
- 生成或确认执行计划时更新 `plan` step。
- 如果匹配到已有 Change Brief，复用原 `flow_id`。
- 如果只有候选匹配，先问一个确认问题。

验收：

- `project-develop 一个需求` 后，`.llm-wiki/requirements/<flow_id>.md` 存在。
- Flow Record 至少能看到 source/design/plan 的状态和证据。

### 3. dashboard-refresh 从 Flow Record 生成看板

Status: done.

改动：

- `project-query/SKILL.md`
- `references/progress-dashboard.md`
- `references/progress-dashboard-template.html`

要求：

- 读取 requirements/bugs/working-context 中的 Flow Record。
- 按 step 投影到看板 lanes：
  - 需求/来源
  - 设计
  - 执行计划
  - 开发
  - 测试
  - 归档
- 每张卡保留：
  - `flow_id`
  - title
  - step
  - status
  - source/evidence
  - updated
- 没有 Flow Record 的新文档只显示为 candidate/pending，不自动假设执行计划。

验收：

- 用户说“更新项目看板”时，不需要 `project-finish`。
- dashboard 能显示同一个 `flow_id` 的多个阶段卡片。
- dashboard 不声称未验证工作完成。

### 4. project-finish 更新开发、测试、归档状态

Status: done.

改动：

- `project-finish/SKILL.md`

要求：

- 根据实际 changed files 更新 `development` step。
- 根据验证命令或人工验证更新 `testing` step。
- 根据 handoff / archive notes 更新 `archive` step。
- 没有验证证据时，不能把 `testing` 标为 done。

验收：

- 完成一次验证后，Flow Record testing 有证据。
- finish 后 dashboard 可以展示测试/归档进度。

### 5. project-review 检查 Flow Record drift

Status: done.

改动：

- `project-review/SKILL.md`

要求：

- 检查 dashboard card 是否有对应 Flow Record。
- 检查 card status 是否和 Flow Record step status 一致。
- 检查 `done` 是否有 evidence。
- 检查代码变更是否超出 Flow Record 对应 scope。

验收：

- 手动制造 dashboard done 但无测试证据时，review 能报出 drift。

## P1：真实项目测试

Status: next.

### 测试场景 A：单需求完整链路

Status: dry-run applied on 2026-06-05; see `flow-record-dry-run-2026-06-05.md`.

项目：

```text
D:\workspace\drone\develop\smartghub\drone-cloud-api
```

流程：

1. ingest 一个 Markdown 需求。
2. project-develop 讨论并确认需求。
3. 生成执行计划。
4. 更新 dashboard。
5. 模拟或完成开发。
6. project-finish 写回验证。
7. 再次更新 dashboard。
8. project-review 检查 drift。

验收：

- 同一个 `flow_id` 串联需求、设计、计划、开发、测试、归档。
- dashboard 点击 evidence 能查看 Markdown 且不乱码。

### 测试场景 B：一个文档拆多个 Flow Record

触发条件：

- 一个源文档包含两个可独立交付的需求。

验收：

- skill 不盲目拆分。
- 只有实现/验证路径明显不同，才拆成多个 Flow Record。
- 拆分前要给用户一个确认问题。

### 测试场景 C：旧文档没有 Flow Record

触发条件：

- 用户手动拷贝很多 PRD/design 文档。

验收：

- dashboard-refresh 将它们显示为 candidate/pending。
- 不生成虚假的 ready/executing/done。
- 推荐下一步创建或确认 Change Brief。

## P2：体验优化

- dashboard 卡片增加 `flow_id` 可见或 hover 信息。
- dashboard 支持按 active/blocked/done 过滤。
- `.llm-wiki/log.md` 记录 dashboard-refresh 变更摘要。
- artifact registry 记录关键计划、验证、归档文档。

## 非目标

- 不做完整工单系统。
- 不做复杂状态机。
- 不要求用户填写表单。
- 不要求 OpenSpec CLI。
- 不自动把所有文档变成 active 工作。
- 不在 dashboard 中创建事实。

## 完成标准

P0 完成后，项目内应能稳定执行：

```text
project-ingest
-> project-develop
-> 更新项目看板
-> project-finish
-> project-review
```

并且任意一个可交付需求都能通过 `flow_id` 回溯：

```text
source/design -> plan -> development -> testing -> archive -> dashboard
```
