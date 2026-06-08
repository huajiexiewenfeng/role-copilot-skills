# Project Develop Copilot 团队试用手册

本文面向团队内部试用，目标是让开发同学用最少的新概念把 `project-develop-copilot` 用起来，同时给项目负责人、技术负责人和流程维护者保留完整生命周期能力。

## 推荐结论

普通开发默认使用“最小使用集”即可：

- 查项目上下文：`project-query`
- 做需求/功能：`project-develop`
- 修 bug：`project-fix`
- 收尾同步：`project-finish`

`project-init` 和 `project-review` 不建议作为普通开发的日常入口：

- `project-init` 通常由项目负责人、试点维护者或仓库首次接入者执行，用于初始化或刷新 `.llm-wiki`。
- `project-review` 通常由负责人、合并前检查人或质量把关人执行，用于检查代码风险、测试缺口、范围漂移、wiki 漂移和 dashboard 漂移。

## 安装

推荐安装顶层 router skill，而不是只安装某一个子 skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot
```

顶层 router 会根据自然语言意图转到 `project-query`、`project-develop`、`project-fix`、`project-finish` 等子流程。

## 版本一：最小使用集

适合对象：

- 日常功能开发同学
- bug 修复同学
- 刚开始试用、不想引入完整流程负担的团队

### 1. 查上下文：`project-query`

用于只读项目问答，不进入实现。

适合问：

```text
基于这个项目的 llm wiki，帮我找一下支付回调相关的需求、开发文档和之前的讨论上下文。先不要开发，我们先讨论。
```

```text
这个项目里面，大疆 API 适配，直播相关的内容有哪些？如何通过 API 调用
```

输出重点：

- 相关 requirement、bug、source proxy、artifact、working-context
- 证据和推断分开
- 缺失或过期的上下文
- 可能的下一步：开发、修复、补充摄入、评审等

使用边界：

- 不修改代码
- 不创建需求或 bug 记录
- 不刷新 dashboard
- 如果只是问“项目里有什么”“API 怎么调用”“之前怎么设计”，优先用它

### 2. 做需求/功能：`project-develop`

用于明确要开发一个功能或需求。

适合说：

```text
Use project develop。我要开发支付回调补偿功能，只允许先改 payment-service 和 order-service，notification-service 只能参考。
```

```text
用 project-develop 做这个需求：让直播能力支持 FPV 和机库摄像头展示。先基于现有 wiki 和源码确认范围，再给计划。
```

输出重点：

- 需求目标和验收标准
- active scope、read-only scope、candidate scope
- 需要读取的项目上下文
- 实施计划和验证方式

使用边界：

- 范围不清时先澄清，不直接写代码
- 需要扩大模块范围时先说明原因
- 不把所有 monorepo 模块都默认拉进来

### 3. 修 bug：`project-fix`

用于诊断并修复具体问题。

适合说：

```text
Use project fix。这里有一段失败日志，先从 payment-service 看，必要时再说明为什么需要看 order-service。
```

```text
用 project-fix 排查这个直播接口返回空数据的问题，先找日志和现有 wiki 里的相关 bug/需求背景。
```

输出重点：

- 症状、影响范围、复现线索
- 证据链
- 根因假设和验证
- 修复方案和测试结果

使用边界：

- 先收集 bug 证据，不直接猜修复
- 不越权修改未进入 active scope 的模块
- 不能验证时要明确剩余风险

### 4. 收尾同步：`project-finish`

用于开发或修复完成后，把实际变更和验证结果同步回 `.llm-wiki`。

适合说：

```text
Use project finish。这个需求代码和测试已经完成，请同步 wiki、记录验证结果，并准备交付说明。
```

输出重点：

- 实际改了什么
- 哪些验证已完成
- 哪些验证受限
- 更新的 wiki、artifact、handoff 或 dashboard 信息

使用边界：

- 没有验证不能声称完成
- dashboard 只能引用已有证据，不作为事实来源
- 不把大段实现叙述塞进 `.llm-wiki`

## 最小使用集流程

```text
先问清楚/查上下文
-> project-query

要开发
-> project-develop
-> project-finish

要修 bug
-> project-fix
-> project-finish
```

普通开发通常不需要主动执行：

```text
project-init
project-review
project-ingest
```

但当资料缺失、项目首次接入、或合并前需要把关时，可以由负责人补充使用。

## 版本二：全量使用

适合对象：

- 项目负责人
- 技术负责人
- 试点维护者
- 需要维护 `.llm-wiki`、dashboard、交付记录和流程质量的人

### 全量 skill 列表

| Skill | 谁常用 | 什么时候用 |
|---|---|---|
| `project-develop-copilot` | 所有人 | 顶层 router，推荐作为自然语言入口 |
| `project-query` | 所有人 | 查项目上下文、API 调用、历史设计、相关文档 |
| `project-init` | 负责人/维护者 | 仓库首次接入、`.llm-wiki` 缺失、项目上下文需要刷新 |
| `project-ingest` | 负责人/维护者/开发 | 新 PRD、PDF、会议纪要、日志、客户反馈需要纳入项目上下文 |
| `project-develop` | 开发 | 做需求或功能 |
| `project-fix` | 开发 | 修 bug 或排查故障 |
| `project-finish` | 开发/负责人 | 完成后同步实际变更、验证和交付记录 |
| `project-review` | 负责人/Reviewer | 合并前、交付前、发现范围/wiki/dashboard 漂移时 |

### 1. 项目首次接入：`project-init`

适合说：

```text
Use project init for this repository. 初始化项目本地 .llm-wiki，发现模块，并给出后续 scoped context 建议。
```

什么时候需要：

- 仓库第一次接入 Project Develop Copilot
- `.llm-wiki` 不存在或明显过期
- 迁移旧版 `docs/ai-coding`
- 需要建立模块索引和基础上下文

什么时候不需要：

- 普通功能开发已经有 `.llm-wiki`
- 只是想查某个功能怎么调用
- 只是修一个明确 bug

### 2. 资料摄入：`project-ingest`

适合说：

```text
Use project ingest。把 docs/prd/payment-callback.md 作为当前支付回调需求的资料摄入 .llm-wiki。
```

适合资料：

- PRD
- 设计文档
- PDF / Word
- 会议纪要
- 客户反馈
- 日志片段
- 临时排查材料

注意：

- 敏感原文不要整段复制进 `.llm-wiki`
- 应保存摘要、来源、关系、缺口和状态
- 命名资料集要尽量保留原始材料路径或 source proxy

### 3. 开发与修复：`project-develop` / `project-fix`

全量使用时，开发或修复仍然应保持和最小使用集一致：

- 明确目标
- 明确 scope
- 先查 `.llm-wiki`
- 再按需查源码
- 验证后再同步

全量流程不会要求普通开发在每次需求前都手动 init 或 review。

### 4. 完成同步：`project-finish`

全量使用中，`project-finish` 是把实际工作变成团队资产的关键步骤。

它负责：

- 更新 requirement 或 bug 状态
- 记录验证证据
- 更新 artifact 索引
- 必要时更新 dashboard
- 准备 handoff

建议在以下场景使用：

- 需求开发完成
- bug 修复完成
- 部署前需要交付说明
- 希望下次会话能恢复当前状态

### 5. 交付前检查：`project-review`

`project-review` 不建议普通开发每次都手动使用，但建议在以下节点使用：

- 合并前
- 交付前
- 改动跨模块
- 改动涉及 `.llm-wiki`、dashboard、artifact
- 怀疑范围漂移、wiki 漂移或验证不足

适合说：

```text
Use project review before commit. 检查这个改动有没有代码风险、测试缺口、范围漂移、wiki 漂移、artifact 漂移和 dashboard 漂移。
```

输出重点：

- findings first
- verification gaps
- context/wiki gaps
- artifact/dashboard gaps
- lifecycle quality
- residual risk

## 全量使用流程

```text
项目首次接入
-> project-init

资料进入项目上下文
-> project-ingest

只读项目问答
-> project-query

需求开发
-> project-develop
-> project-finish
-> project-review

bug 修复
-> project-fix
-> project-finish
-> project-review
```

## 团队试用建议

第一阶段建议只推广最小使用集：

```text
project-query
project-develop
project-fix
project-finish
```

第二阶段再由负责人引入：

```text
project-init
project-ingest
project-review
```

推荐分工：

| 角色 | 推荐使用 |
|---|---|
| 普通开发 | `project-query`, `project-develop`, `project-fix`, `project-finish` |
| 需求/技术负责人 | 加上 `project-ingest`, `project-review` |
| 试点维护者 | 加上 `project-init`, dashboard 和 `.llm-wiki` 维护 |

## 常见误用

- 只是问项目问题，却直接进入 `project-develop`
- 每个需求都重新 `project-init`
- 没有验证就执行 `project-finish` 并声称完成
- 普通开发把 `project-review` 当成每次编码前的必选步骤
- 把 `.llm-wiki` 当作源码替代品，而不是索引和摘要层
- 忽略 active/read-only/candidate/excluded scope，直接跨模块改代码

## 一句话版

普通开发记住四个入口就够了：

```text
查上下文用 project-query
做需求用 project-develop
修 bug 用 project-fix
完成后用 project-finish
```

`project-init`、`project-ingest`、`project-review` 由负责人或流程维护者在需要时补充使用。
