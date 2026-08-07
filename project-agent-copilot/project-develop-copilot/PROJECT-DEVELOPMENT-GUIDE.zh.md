# PDC 单项目开发流程

本文介绍 Project Develop Copilot（PDC）在一个业务项目中的常规使用流程：

```text
project-init
  -> project-ingest
  -> project-query
  -> project-develop
  -> project-finish
```

前四步是主流程，`project-finish` 负责在实现和验证完成后收尾。

## 1. 这套流程解决什么问题

AI 会写代码，但在真实项目里，它通常缺少三类信息：

1. 当前项目有哪些模块，代码入口在哪里；
2. 需求、设计、历史决策和已知风险在哪里；
3. 这次修改的范围、验收标准和验证结果是什么。

PDC 用项目内的 `.llm-wiki` 保存这些上下文，让 AI 在开发前先找到资料、确认范围，开发后再把结果同步回来。

可以把这条流程理解为：

```text
project-init     = 建立项目目录和上下文入口
project-ingest   = 把外部资料变成可追溯的项目来源
project-query    = 开发前查询证据和相关上下文
project-develop  = 明确范围后进入需求开发
project-finish   = 用验证结果更新项目状态并生成交接
```

## 2. 开始前准备什么

准备一个业务代码仓库，例如：

```text
D:/code/order-service
```

建议同时准备：

- 项目源码和构建文件；
- 当前需求或问题描述；
- PRD、设计文档、接口说明或会议纪要；
- 可以运行的测试、编译或人工验证方式。

进入正确的项目根目录后再开始：

```powershell
cd D:/code/order-service
```

项目根目录很重要。PDC 会把 `.llm-wiki` 建在当前业务项目中；如果根目录选错，后续模块、资料和开发范围都会跟着错。

## 3. 第一步：用 `project-init` 初始化业务项目

对 Codex 说：

```text
使用 project-init 初始化当前业务项目。
```

也可以把项目范围说得更明确：

```text
这是 order-service 的业务项目根目录。
请使用 project-init 初始化项目上下文，识别主要模块，但不要修改生产代码。
```

`project-init` 会先确认项目根目录，然后创建或补全标准 `.llm-wiki`，识别项目模块、已有文档和可用工具。

初始化后常见目录如下：

```text
.llm-wiki/
  README.md
  log.md
  project/
  requirements/
  ingest/
  modules/
  sources/
  artifacts/
  cross-refs/
  project-graph/
  tools/
  dashboard/
  session-digests/
  migration/
  working-context/
  decisions/
  verification/
  handoff/
```

几个最常用的入口：

```text
.llm-wiki/project/overview.md          项目总览
.llm-wiki/modules/index.md             模块清单
.llm-wiki/sources/registry.md          来源登记
.llm-wiki/context-completion-plan.md   还缺哪些上下文
.llm-wiki/dashboard/progress.html      项目进度看板
.llm-wiki/tools/llm_wiki_doctor.py     知识库校验工具
```

### 初始化不是完整项目分析

全仓初始化通常只达到以下两个阶段：

| Level | 名称 | 含义 |
|---|---|---|
| 1 | `project-navigation-ready` | 已有项目总览、模块索引和来源入口 |
| 2 | `context-completion-plan-ready` | 已列出建议补全的模块和缺失事实 |

这表示 AI 已经知道“去哪里找”，不表示它已经理解每个模块，更不表示可以直接修改任意代码。

当一个具体模块已经有源码支撑的架构、入口和约束时，才会达到 `scoped-context-ready`。当具体需求同时具备范围、来源、验收标准、验证计划和 working context 时，才是 `feature-ready`。

### Base Graph 不用 `project-init`

普通业务项目使用：

```text
project-init
```

独立 Base Graph 仓库使用：

```text
project-base-init
```

不要混用。Base Graph 的完整操作见《Base Graph 使用教程》。

## 4. 初始化后检查什么

先检查 PDC 返回的结果：

```text
Project root:
Mode:
Created:
Updated:
Preserved:
Modules:
Context completion level:
Recommended scoped contexts:
Open questions:
Next action:
```

重点确认：

- `Project root` 是正确的业务仓库；
- `.llm-wiki` 已创建，且没有修改生产代码；
- `modules/index.md` 没有把所有目录都标成 active；
- 已有 Wiki 内容和旧文档没有被覆盖；
- `context-completion-plan.md` 明确指出仍缺哪些事实；
- 初始化等级没有被夸大成 `feature-ready`。

如果根目录不对，立即停止并让 PDC 在正确目录重新初始化。不要继续使用错误项目中生成的事实，也不要直接删除错误目录，先单独确认清理范围。

## 5. 第二步：用 `project-ingest` 加入项目资料

初始化解决“项目结构在哪里”，`project-ingest` 解决“需求和背景资料在哪里”。

例如摄入一份需求文档：

```text
使用 project-ingest 将 docs/requirements/payment-callback.md
加入当前项目知识库，并关联到 order 模块。
```

摄入外部 Markdown：

```text
使用 project-ingest 将这份支付回调设计文档加入当前项目。
保留可追溯来源，并在安全的情况下保存 wiki 内完整副本。
```

摄入 URL、PDF、Word、日志或敏感资料时，PDC 会先确认读取方式。例如：

```text
这个 PDF 只登记路径，还是现在读取并总结？
这个 URL 只记录链接，还是抓取并总结？
这份日志是否只总结现象，不复制原始敏感内容？
```

### 常见处理方式

| 方式 | 适用情况 |
|---|---|
| `path-only` | 只登记来源，不读取正文 |
| `summary` | 保存摘要和关键点 |
| `summary + full-source-copy` | 安全的 Markdown，保存摘要和 Wiki 内完整副本 |
| `cautious-summary` | 日志或可能敏感的资料，只总结必要信息 |
| `needs-confirmation` | 大文件、二进制、远程或敏感来源，需要确认后读取 |

对于安全的 Markdown，常见产物如下：

```text
.llm-wiki/
  ingest/
    index.md
  sources/
    proxies/
      20260807-001/
        001-payment-callback.md
    originals/
      20260807-001/
        manifest.md
        001-payment-callback.md
```

其中：

- `ingest/index.md` 是摄入索引；
- `sources/proxies/` 保存便于 AI 检索的来源摘要；
- `sources/originals/` 保存允许团队共享的 Wiki 内原文副本；
- `manifest.md` 记录同一批资料的来源和归属。

长期保存的 `.llm-wiki` 页面应使用仓库相对路径或稳定来源标签，不能把 `C:/Users/...`、`D:/workspace/...` 这类个人绝对路径写入团队知识库。

### 摄入不等于确认事实

新摄入资料默认是 `candidate`。它进入了项目知识库，但不自动成为当前需求的活动来源，也不自动覆盖当前源码、测试和用户决策。

如果资料提到跨项目关系，但没有已确认的 Project Graph edge，应记录为 `Project Graph Gaps`，不能根据文档描述直接虚构 edge。

历史聊天、AI 会话或旧交接记录应优先使用 `project-session-extract`，而不是当作普通 PRD 直接摄入。

## 6. 摄入后检查什么

PDC 应返回类似信息：

```text
Source:
Normalized source:
Type:
Processing mode:
Ingest status:
Source proxy:
Full source copy:
Batch manifest:
Related requirement/bug/module:
Sensitivity notes:
Gaps:
Next action:
```

重点确认：

- 来源可以追溯到原文或稳定 URL；
- Wiki 元数据没有个人绝对路径；
- proxy 和 original 的批次、序号一致；
- 二进制、远程或敏感资料没有在未确认时被深读；
- 资料状态仍是 candidate，除非当前任务明确激活；
- 跨项目事实没有从文档描述中被直接推断出来。

## 7. 第三步：用 `project-query` 查询项目上下文

进入开发之前，先通过 `project-query` 查清楚当前项目已经知道什么。

例如：

```text
使用 project-query 查询支付回调需求涉及的模块、历史决策、
已摄入资料、相关接口和已知风险。先不要修改代码。
```

也可以问得更具体：

```text
从当前项目 .llm-wiki 查询：
1. 支付回调入口在哪个模块；
2. 是否已有幂等设计；
3. 相关需求和来源文档有哪些；
4. 还有哪些事实需要回到源码确认。
```

`project-query` 默认只读。它会先查 `.llm-wiki` 的索引和相关页面，只读取回答问题所需的最小上下文；当 Wiki 摘要不足或过期时，再核对当前源码、测试和配置。

查询不应该：

- 修改生产代码；
- 自动创建 Change Brief；
- 把讨论结果直接写回 Wiki；
- 在查询模式下创建或修改 candidate、edge、proposal 或 pin；
- 把历史 Session Digest 当作当前项目事实。

## 8. 查询结果应该包含什么

推荐输出结构：

```markdown
## Answer

## Project Context Pack

- wiki_pages_used:
- source_proxies_used:
- related_requirements:
- related_modules:
- project_graph_edges:
- project_graph_candidates:
- open_questions:
- confidence:

## Evidence

## Inference

## Possible Next Routes
```

重点看三件事：

1. **用了哪些页面和来源**：答案必须能回到 `.llm-wiki` 或源码；
2. **证据和推断是否分开**：没有证据的判断不能写成事实；
3. **是否足以进入开发**：范围、验收标准或关键接口仍不清楚时，应先补资料或核对源码。

如果问题涉及其他项目，查询顺序应是：

```text
cross-ref pin -> confirmed edge -> candidate
```

只有 candidate 时，结果必须明确标注“candidate only”。读取外部项目之前，应先说明：

```text
scope: read-only
```

Base Graph 负责找到相关项目及其目录，Project Graph 负责记录关系证据。具体见《Base Graph 使用教程》和《Project Graph 使用教程》。

## 9. 第四步：用 `project-develop` 进入开发

当需求已明确需要实现时，对 Codex 说：

```text
使用 project-develop 实现支付回调幂等需求。
先恢复相关项目上下文，确认 active scope、验收标准和验证方式，再开始修改代码。
```

`project-develop` 进入代码修改前，必须创建或恢复 Change Brief：

```text
.llm-wiki/requirements/<change-id>.md
```

Change Brief 至少说明：

- 为什么需要修改；
- 修改什么；
- 明确不修改什么；
- 验收标准；
- active scope；
- 验证计划；
- Flow Record。

然后再完成以下步骤：

1. 恢复相关 Wiki、来源、模块和 working context；
2. 区分 active、read-only、candidate 和 excluded scope；
3. 核对当前源码、测试、配置和关键外部契约；
4. 明确需求摘要、验收标准、非目标和风险；
5. 形成实现计划；
6. 锁定范围后实施；
7. 记录验证结果和剩余风险。

### 为什么开发前要有 Change Brief

Change Brief 不是为了增加文档，而是为了避免 AI 在需求还没说清楚时直接改代码。即使改动很小，只要会改变 API、协议、Topic、DTO、字段或可观察行为，也需要明确修改边界和验收标准。

### 开发时的事实优先级

```text
1. 用户当前明确决定
2. 当前源码、测试、配置、构建和运行证据
3. 原始 PRD、Issue、设计文档和会议结论
4. .llm-wiki 索引与摘要
5. 旧 AI 文档或生成材料
```

Wiki 帮助定位上下文，但不能覆盖当前源码事实。过期、未验证或在脏工作区中捕获的内容只能作为线索，使用前必须重新核对。

### 跨项目需求的额外要求

如果需求涉及 Feign、HTTP、MQTT、RPC、共享数据库或共享配置，应先检查：

```text
cross-ref pin -> confirmed edge -> candidate
```

只有新鲜且 `source-verified` 或 `runtime-verified` 的 edge 可以直接支撑实现决策。以下内容只能作为线索或风险：

- candidate；
- proposal；
- `unverified` edge；
- 已过期 edge；
- 只有 Wiki、没有当前源码证据的关系。

外部项目默认只读。需要修改外部项目时，应生成 context handoff，在对方项目中单独开展工作。

## 10. 一个连续示例

假设收到需求：

```text
order-service 的支付回调需要增加幂等处理，避免第三方重复通知导致订单重复更新。
```

### 10.1 初始化项目

```text
使用 project-init 初始化 order-service。
识别订单相关模块，但不要修改生产代码。
```

检查结果：

- 项目根目录正确；
- `.llm-wiki` 已创建；
- `modules/index.md` 中识别出订单模块；
- 初始化等级为 Level 1 或 Level 2；
- `context-completion-plan.md` 提示需要补充支付回调入口和数据更新链路。

### 10.2 摄入需求资料

```text
使用 project-ingest 摄入 docs/requirements/payment-callback-idempotency.md，
关联到订单模块，并保留可追溯的 Wiki 内来源。
```

检查结果：

- `ingest/index.md` 有来源记录；
- `sources/proxies/<batch-id>/` 有摘要；
- 安全的 Markdown 已归档到 `sources/originals/<batch-id>/`；
- 来源状态为 candidate，没有自动变成已确认代码事实。

### 10.3 查询开发上下文

```text
使用 project-query 查询支付回调幂等需求：
回调入口、订单更新方法、已有唯一约束、历史设计和待确认问题分别是什么？
```

预期结果：

- 指出相关 Wiki 页面和来源 proxy；
- 找到订单模块和可能的回调 Controller；
- 把“文档提到幂等键”列为 Evidence 或 Inference；
- 指出需要核对数据库唯一键、事务范围和重复回调测试。

### 10.4 进入开发

```text
使用 project-develop 实现支付回调幂等处理。
先创建或更新 Change Brief，确认不改变外部回调协议，
并将重复回调测试作为验收条件。
```

预期过程：

- 创建 `.llm-wiki/requirements/payment-callback-idempotency.md`；
- active scope 只包含回调入口、订单更新逻辑和相关测试；
- 非目标明确为“不改变第三方回调字段和响应协议”；
- 验收标准包含“同一业务回调重复提交只产生一次状态变更”；
- 实施前确认数据库和事务事实；
- 修改代码并运行约定的测试或人工验证。

## 11. 完成后用 `project-finish` 收尾

实现和验证完成后说：

```text
使用 project-finish 完成验证并将结果同步回 .llm-wiki。
记录测试命令、结果、剩余风险和交接信息。
```

`project-finish` 会：

1. 核对测试、编译、lint、人工验证或明确接受的限制；
2. 先更新 Change Brief 或 working context 中的 Flow Record；
3. 更新相关 artifact 和 Dashboard 投影；
4. 生成 `.llm-wiki/handoff/<flow-id>-handoff.md`；
5. 写入必要的 `.llm-wiki/log.md` 记录；
6. 在 Doctor 可用时运行 finish 阶段校验。

如果验证没有完成，必须如实记录 blocked、partial 或 residual risk，不能仅凭代码已经写完就标记完成。

## 12. 推荐验收清单

### project-init

- [ ] 项目根目录正确；
- [ ] `.llm-wiki` 标准目录已创建；
- [ ] 模块被保守识别，没有全部标成 active；
- [ ] 已有 Wiki 和旧文档被保留；
- [ ] 初始化等级真实，没有把 Level 1/2 写成 feature-ready；
- [ ] 没有修改生产代码。

### project-ingest

- [ ] 来源身份稳定且可追溯；
- [ ] 没有把个人绝对路径写入团队 Wiki；
- [ ] proxy、original 和 manifest 能互相对应；
- [ ] 敏感或二进制来源经过确认；
- [ ] 新资料默认是 candidate；
- [ ] 没有根据资料直接虚构跨项目 edge。

### project-query

- [ ] 明确列出使用的 Wiki 页面和来源；
- [ ] Evidence 与 Inference 分开；
- [ ] 只读取回答问题需要的最小范围；
- [ ] Wiki 过期时回到当前源码验证；
- [ ] 查询过程没有改代码和生命周期状态。

### project-develop

- [ ] Change Brief 在执行计划和代码修改之前创建；
- [ ] 需求摘要、验收标准和非目标明确；
- [ ] active/read-only/candidate/excluded scope 已区分；
- [ ] 外部契约有当前源码证据；
- [ ] 实施没有超出锁定范围；
- [ ] 测试或人工验证方式明确。

### project-finish

- [ ] 完成状态有验证证据；
- [ ] Flow Record 先于 Dashboard 更新；
- [ ] handoff 位于 `.llm-wiki/handoff/`；
- [ ] 剩余风险没有被隐藏；
- [ ] Doctor 可用时已执行 finish 校验。

## 13. 常见错误

### 错误 1：初始化后就认为 AI 已理解整个项目

初始化通常只做到可导航。正确做法是根据 `context-completion-plan.md` 补充当前模块，再进入具体需求。

### 错误 2：把 PRD 摄入后直接当成当前代码事实

摄入资料默认是 candidate。实现前仍需通过 `project-query` 和当前源码确认。

### 错误 3：跳过查询，直接让 AI 全仓搜索并改代码

先用 Wiki 缩小范围，再核对源码，可以减少上下文噪声和误改。

### 错误 4：先写执行计划，后补 Change Brief

Change Brief 必须先明确为什么改、改什么、不改什么和如何验收。执行计划不能成为需求的第一个长期文档。

### 错误 5：把 candidate 或未验证的外部关系用于实现

跨项目实现必须回到源码核对。candidate、proposal 和 `unverified` edge 只能作为线索。

### 错误 6：代码写完就标记完成

完成需要验证证据。测试受阻时，应记录限制、接受人和残余风险，而不是把状态写成 verified。

### 错误 7：用 `project-init` 初始化 Base Graph

业务项目使用 `project-init`，Base Graph 仓库使用 `project-base-init`。

## 14. 一句话使用流程

```text
1. 在业务项目根目录运行 project-init，建立可导航的 .llm-wiki。
2. 用 project-ingest 摄入需求和项目资料，保留可追溯来源。
3. 用 project-query 查询相关模块、历史决策、证据和风险。
4. 用 project-develop 创建 Change Brief、锁定范围并实施。
5. 用 project-finish 根据验证结果同步 Wiki、状态和 handoff。
```

最重要的是：

**先建立项目上下文，再查证据；先确认范围，再改代码；先完成验证，再同步完成状态。**
