# Project Develop Copilot P0/P1 改进执行计划

## 背景

本计划来自对 `project-agent-copilot/project-develop-copilot` 的结构性评审。

当前主要风险不是功能不足，而是：

- 规则持续增加，但缺少可回归验证。
- 子 skill 依赖 `../references/`，单独安装时容易硬失败。
- Flow Record、artifact registry、dashboard、handoff、log 多份状态容易漂移。
- Gate 数量和 router 规则变重，后续维护成本上升。

本阶段只处理 P0 和 P1。P2 暂不纳入执行范围。

## 不做范围

本阶段不做：

- 私有概念削减。
- 术语表建设。
- golden cases 扩展。
- 大规模 README 美化。
- 新增 Gate。
- 新增新的生命周期概念。

允许顺手修复：

- README 明显损坏代码块。
- `Session Digest` / `Context Digest` 命名漂移。

## 执行顺序

### 1. P0-2：解除 references 硬依赖

目标：

```text
子 skill 单独安装后，不会因为缺少 ../references/ 而直接停止。
```

策略：

```text
子 skill 内置最小可执行规则。
references 变成 deep reference。
缺 references 时降级执行，不直接停止。
```

修改范围：

```text
project-init/SKILL.md
project-ingest/SKILL.md
project-session-extract/SKILL.md
project-query/SKILL.md
project-develop/SKILL.md
project-fix/SKILL.md
project-finish/SKILL.md
project-review/SKILL.md
project-maintain/SKILL.md
```

验收：

```text
任一子 skill 单独安装时：
- 不因缺 references 停止。
- 能完成最小流程判断。
- 需要深度规则时提示 deep references 缺失。
- 不在降级模式下制造不确定项目事实。
```

### 2. P0-1：落地 evals 最小安全网

目标：

```text
有一组可手工回归的 eval，保护后续 Gate 合并和 SKILL.md 瘦身。
```

优先覆盖：

```text
1. lightweight-answer 不应创建 lifecycle state。
2. project-query 只读查询不应进入 develop。
3. 用户要求开发时必须创建或恢复 Change Brief。
4. 不能跳过 Documentation Anchor Gate 直接改码。
5. project-finish 必须同步 Flow Record。
6. dashboard-refresh 不能制造无证据 done 状态。
7. failure case 2026-06-08 的关键失败点。
```

修改范围：

```text
evals/README.md
evals/project-develop-copilot-evals.md
evals/runbook.md
cases/failures/...
```

验收：

```text
每个 eval 至少包含：
- input prompt
- expected route
- required gates
- forbidden behavior
- pass/fail criteria
```

### 3. 修复明显文档损坏和术语漂移

只修 bug，不做 P2 文档重构。

修改：

```text
README.md
README.zh.md
```

内容：

```text
`	ext -> ```text
Context Digest -> Session Digest
```

验收：

```text
README 不再有坏代码块。
同一能力统一叫 Session Digest。
```

### 4. P1-4：Gate 合并与 SKILL.md 瘦身

前提：

```text
P0 evals 已经落地。
```

目标：

```text
Gate 数量 <= 10。
router SKILL.md 只保留 mode 表、边界、handoff。
深度规则移动到 references，并按 mode 触发读取。
```

合并方向：

```text
Verification / Verification Provenance / Test Integrity
-> Verification Gate

Knowledge Sync / Artifact Sync / Dashboard Sync
-> Finish Sync Gate

Context Discovery / Context Enrichment
-> Context Recovery Gate
```

修改范围：

```text
references/lifecycle-gates.md
SKILL.md
project-*/SKILL.md
```

验收：

```text
evals 全部仍然通过。
Owned Gates 和 lifecycle-gates.md 对齐。
router 仍能完成主要路由。
```

### 5. P1-3：状态单向投影

目标：

```text
减少 Flow Record、artifact registry、dashboard、handoff、log 之间互相写导致的 drift。
```

权威源：

```text
Flow Record 是生命周期状态权威源。
artifact registry 是 artifact 权威索引。
dashboard 是纯投影。
log 是审计流水，不作为状态源。
handoff 是归档材料，不反推状态。
```

修改范围：

```text
references/flow-record.md
references/progress-dashboard.md
references/lifecycle-gates.md
project-query/SKILL.md
project-finish/SKILL.md
project-maintain/SKILL.md
project-review/SKILL.md
```

验收：

```text
dashboard-refresh 从 Flow Record + artifact registry 重建。
不允许手工独立维护 dashboard 状态。
review 能识别 dashboard 与 Flow Record drift。
finish 只从实际证据更新 Flow Record，再投影其他状态。
```

### 6. P1-5：路由模糊区修复

目标：

```text
减少 lightweight-answer / project-query / project-maintain / lifecycle-quality 混淆。
```

增加决策树：

```text
是否需要搜索 .llm-wiki 证据？
  否 -> lightweight-answer
  是 -> 是否只读？
    是 -> project-query
    否 -> 是否是 wiki 结构/可见性/一致性问题？
      是 -> project-maintain
      否 -> full lifecycle
```

补充易混淆对照：

```text
问项目里有什么 vs 要开发。
刷新 dashboard vs finish。
流程跑偏评估 vs 普通 review。
```

验收：

```text
evals 新增 3 个路由模糊用例。
router 不依赖 Dolores / skill-evaluator 这类魔法词。
自然语言“评估这次流程是否跑偏”也能进入 lifecycle-quality。
```

## 阶段完成标准

本阶段完成后，应满足：

```text
- 子 skill 单独安装不会因 references 缺失硬失败。
- evals 有最小可跑安全网。
- Gate 数量收敛到 <= 10。
- dashboard 明确是投影，不再是独立状态源。
- router 对模糊请求有决策树。
- README 明显损坏修复。
- Session Digest 命名统一。
- 不新增任何新的 Gate 或生命周期概念。
```

## 当前执行约束

在 P0 evals 落地前：

- 不新增 Gate。
- 不新增 reference 规则体系。
- 不做大规模重构。
- 不引入新的私有概念。

优先做最小、可验证、能降低结构性风险的修改。
