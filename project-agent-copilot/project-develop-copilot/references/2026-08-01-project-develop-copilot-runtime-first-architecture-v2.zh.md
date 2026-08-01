# Project Develop Copilot Runtime-first 架构评估 V2

日期：2026-08-01

状态：历史评估；已被 LLM-first Deterministic Guardrails V3 替代，Runtime 未实现

替代关系：本文件曾替代 2026-07-30 MCP / Runtime 评估，现由 `2026-08-01-project-develop-copilot-llm-first-deterministic-guardrails-v3.zh.md` 替代。保留本文件仅用于记录决策演进，不得执行其 P0-P4 路线。

评估基线：role-copilot-skills@f388458

范围：重新判断 Project Develop Copilot 的 Runtime、JSON CLI、MCP 与 Host 工具边界，并给出按收益和风险排序的演进路径。

## 1. 执行结论

> 历史说明：以下内容是 V2 当时的判断，不再代表当前实施方向。当前结论以 LLM-first Deterministic Guardrails V3 为准。

Project Develop Copilot 需要建设 Project Lifecycle Runtime，但当前不需要把 MCP 作为 P1 的默认交付。

更准确的架构结论是：

> Skill / LLM 继续负责语义判断、生命周期路由和项目领导；Project Lifecycle Runtime 接管确定性的状态访问、不变量和状态转换；版本化 JSON CLI 是近期默认适配面；MCP 只在跨独立宿主复用、无 Shell Host、长驻能力或集中权限边界被真实需求证明后，作为很薄的可选适配器加入。

正确顺序是：

~~~text
状态权威与不变量
  -> 可导入、可单测的 Runtime Core
  -> 只读 JSON CLI
  -> 写入 Preview
  -> 事务化 Commit
  -> 按条件增加 MCP Adapter
~~~

不推荐的顺序是：

~~~text
先设计 MCP tools
  -> 再倒推 Runtime
  -> 最后补状态一致性
~~~

Runtime 是当前确定方向。

JSON CLI 是近期正确入口。

MCP 是条件性适配器，不是演进目标，也不是 Runtime 成立的前提。

## 2. V2 相对旧稿的关键修正

旧稿已经正确识别了三件事：

1. Skill 应保留项目语义和路由权；
2. Runtime 应接管确定性状态操作；
3. CLI 应继续服务 CI、测试、人类操作和 fallback。

V2 修正的是优先级，而不是推翻上述边界。

| 主题 | 旧稿倾向 | V2 决策 |
| --- | --- | --- |
| 近期演进目标 | Runtime 与 MCP 同步进入 P1 | 只建设 Runtime 和 JSON CLI |
| Agent 默认适配面 | MCP | JSON CLI |
| MCP 定位 | Agent 原生适配层，较早交付 | 可选薄适配器，满足门槛后交付 |
| 操作命名 | MCP capabilities | Runtime operations |
| Preview / Commit | 后续 MCP 能力 | Runtime 能力，先由 CLI 暴露 |
| Base Graph | 可能增强 MCP 必要性 | 数据范围大，不等于协议必须服务化 |
| 跨 Host | 作为提前建设理由 | 作为未来引入 MCP 的验证门槛 |

V2 的核心变化可以概括为：

> 先把正确性建在 Runtime 内核里，再决定需要多少适配层。

## 3. 决策问题

本版评估回答六个问题：

1. PDC 当前真正缺少的是协议，还是状态内核？
2. 哪些规则必须成为 Runtime invariant？
3. JSON CLI 能否先满足 Agent、CI、测试和人工诊断？
4. Preview 和 Commit 应属于 Runtime 还是 MCP？
5. 什么证据出现后，MCP 才有净收益？
6. 如何避免把 Runtime 变成僵硬的工作流平台？

判断标准按以下顺序排列：

1. 状态正确性；
2. 权限与路径安全；
3. 可测试性和可恢复性；
4. Git / Markdown 可审计性；
5. Host 兼容性；
6. Token 与调用成本；
7. 实现和维护复杂度。

## 4. 当前证据

### 4.1 PDC 已经有明确的状态权威

当前设计已经规定：

~~~text
当前用户决策
  -> 当前源码、测试和验证输出
  -> Flow Record
  -> Artifact Registry
  -> Log
  -> Dashboard / Handoff
  -> 未晋升的 Session Digest
~~~

这套顺序应成为 Runtime 的核心约束。

其中：

- Flow Record 是生命周期状态权威；
- Artifact Registry 是产物存在性和可发现性权威；
- Dashboard 和 Handoff 是投影；
- Log 是审计记录；
- Session Digest 默认只是召回上下文；
- candidate、wiki-checked 与 stale evidence 不能被静默提升为 verified fact。

### 4.2 Doctor 已证明 JSON CLI 路线可行

scripts/llm_wiki_doctor.py 已经支持：

- validate；
- score；
- report；
- text / json 输出；
- 稳定 exit code；
- CI、测试、pre-commit 和 Agent 调用。

它还不是统一的 Project Lifecycle Runtime，也没有统一 response envelope，但已经证明：

> 确定性能力不需要先包装成 MCP，才能被 Agent 和自动化系统可靠调用。

### 4.3 Task Control 已证明应先建权威 reducer

project-task-dispatch/scripts/task_control.py 已经采用：

- 单一父级状态权威；
- 子任务只提交 requested state；
- 固定状态集合；
- 合法转换表；
- 严格字段校验；
- unknown field 拒绝；
- blocker 一致性；
- terminal state；
- 确定性 projection。

这类 reducer 没有依赖 MCP，也没有依赖特定 Agent Host。

它验证了一个重要方向：

> 先把状态权威、不变量和 reducer 做正确，后续 CLI、MCP、WALK 或 UI 都只是适配问题。

### 4.4 当前没有 MCP 实现负担

当前仓库中的 MCP 内容仍是架构评估，没有已经交付且必须兼容的 Project MCP Server。

因此现在收窄 P1 的成本很低，不存在需要保护的 MCP 既有投资。

## 5. 架构决策

### AD-1：Skill 是语义控制面

Skill / LLM 保留：

- 判断 lightweight-answer 或 full-lifecycle；
- 选择 query、develop、fix、review、finish 等阶段；
- 理解用户目标和项目范围；
- 区分事实、推断、风险和候选；
- 决定创建、复用或拆分 Change Brief；
- 判断哪些知识值得沉淀；
- 进行需求讨论、架构权衡、开发和 Review；
- 选择外部专业 Skill；
- 处理模糊信息和用户确认。

Runtime 不得自行推断这些语义。

### AD-2：Runtime 是确定性状态数据面

Runtime 接管：

- Project Root / Wiki Root 解析；
- 路径 containment；
- Wiki 初始化与版本迁移；
- 有界 Context Pack；
- Flow Record 状态转换；
- Artifact Registry；
- Dashboard / Handoff 投影；
- append-only Log；
- Doctor / deterministic validation；
- Project Graph 确定性查询；
- lock、幂等、preview、commit 和 recovery。

### AD-3：Operation 独立于适配协议

以下名称首先是 Runtime operations：

- project_context.resolve；
- project_context.query；
- project_context.diagnose；
- project_lifecycle.preview；
- project_lifecycle.commit。

它们不应在设计阶段被定义为 MCP 专属 tools。

同一 operation 可以由：

- Python API；
- JSON CLI；
- MCP Adapter；
- 测试 Fixture；
- CI；
- 未来 UI

调用。

### AD-4：JSON CLI 是近期默认适配器

JSON CLI 具备当前阶段需要的特性：

- Agent 可通过 Shell 调用；
- CI 和测试可直接调用；
- 无长驻服务生命周期；
- 调试链路短；
- Windows、Linux 和 macOS 都可验证；
- 可以保留 repo-vendored fallback；
- 与 Python Runtime 使用同一实现；
- 不提前引入 Host-specific MCP 配置。

### AD-5：Preview 和 Commit 属于 Runtime

Preview 不是 MCP 特性。

事务化 Commit 也不是 MCP 特性。

它们必须先在 Runtime Core 中成立，再由 CLI 或 MCP 暴露。

### AD-6：Markdown / Git 仍是可审计事实载体

Runtime 不引入一个隐藏数据库替代项目 Markdown。

允许使用本地派生索引、cache、lock、journal 或 hash，但它们：

- 不是团队共享事实源；
- 可以重建；
- 默认不进入 Git；
- 不得让 Dashboard 或索引反向覆盖 Flow Record；
- 不得降低 Markdown diff 可读性。

### AD-7：MCP 采用需求触发，而不是路线预设

MCP 只有满足第 14 节的引入门槛后才进入交付。

如果 JSON CLI 已满足当前 Host、CI、测试和用户流程，就不因 MCP 可用而增加一层服务。

## 6. 责任边界

| 层 | 负责 | 不负责 |
| --- | --- | --- |
| Skill / LLM | 意图、路由、范围、证据语义、业务判断、用户确认 | 文件事务、锁、幂等、机械投影 |
| Runtime Core | 状态权威、不变量、路径安全、operation、事务、恢复 | 判断用户想开发还是讨论 |
| JSON CLI | 请求解析、调用 Runtime、稳定 JSON / exit code | 生命周期业务逻辑 |
| MCP Adapter | tool schema、Host 协议、超时取消、会话观测 | 复制 Runtime 规则、成为状态权威 |
| Host Tools | 源码编辑、Shell、Git、测试、Codegraph | PDC 生命周期状态权威 |
| Markdown / Git | 团队共享事实、审计、diff、历史 | 动态路由和 LLM 推理 |

## 7. 目标架构

~~~mermaid
flowchart TD
    U["用户"] --> S["Project Develop Copilot Skills"]

    S --> H["Host Tools"]
    H --> HC["源码编辑 / Shell / Git / Tests / Codegraph"]

    S --> A["Adapter Layer"]
    A --> C["JSON CLI：近期默认"]
    A -. "满足引入门槛后" .-> M["MCP Adapter：可选"]

    C --> R["Project Lifecycle Runtime Core"]
    M --> R

    R --> X["Context Engine"]
    R --> L["Lifecycle State Engine"]
    R --> G["Project Graph Engine"]
    R --> D["Doctor / Validation Engine"]
    R --> T["Transaction / Recovery Engine"]

    X --> W["项目 .llm-wiki"]
    L --> W
    G --> W
    D --> W
    T --> W
~~~

关键点：

1. Adapter 可以替换，Runtime 语义不能分叉；
2. CLI 和 MCP 不得各自实现一套状态规则；
3. Skill 不直接编排底层多文件写入；
4. Host Tools 继续负责真实项目开发；
5. Runtime 不接管需求讨论和项目领导。

## 8. Runtime Core 组成

### 8.1 Root And Scope Resolver

职责：

- 解析 project root 和 wiki root；
- 返回 root evidence 和 confidence；
- 绑定 allowed roots；
- 拒绝路径逃逸；
- 区分 business project、Base Graph 和 read-only remote project；
- 返回 initialization level 和能力降级原因。

### 8.2 Context Engine

职责：

- 按预算读取最小 entrypoints；
- 执行 pin -> edge -> candidate -> source fallback；
- 区分 evidence、inference、candidate-only 和 stale clue；
- 生成 context refs；
- 保证远端默认只读；
- 对结果排序、裁剪和去重。

### 8.3 Lifecycle State Engine

职责：

- Change Brief / Bug Brief / Flow Record lookup；
- flow_id 唯一性；
- 状态转换；
- verification evidence 前置条件；
- source、design、plan、development、testing、archive 步骤约束；
- 并发与 stale state 检查。

### 8.4 Projection Engine

职责：

- 从 Flow Record 和 Artifact Registry 生成 Dashboard；
- 从权威状态生成 Handoff；
- append-only Log；
- 拒绝投影反向覆盖状态；
- 生成确定性 diff 和 refs。

### 8.5 Doctor And Graph Engine

职责：

- 复用 Doctor findings 和 score；
- 校验路径、backlink、fingerprint、edge 和 candidate；
- 生成 repair preview；
- 默认不执行 repair；
- 保持 Base tracked files 的独立授权边界。

### 8.6 Transaction And Recovery Engine

职责：

- preview token；
- lock；
- idempotency key；
- 原子写入或 journal；
- stale preview 拒绝；
- partial failure 记录；
- resume / rollback / manual recovery 指引。

## 9. 核心不变量

Runtime 第一版至少应固化以下不变量：

1. Flow Record 先于 Dashboard 和 Handoff；
2. testing=done 必须有满足策略的 verification evidence；
3. Artifact Registry 不登记不存在的产物；
4. Dashboard 不得比 Flow Record 声明更强状态；
5. Handoff 不得成为生命周期状态权威；
6. Log 只能追加事件，不能替代状态；
7. confirmed edge 必须来自 proposal / explicit confirmation；
8. candidate 不得静默提升为 verified fact；
9. remote project 默认只读；
10. business project session 不得写 Base tracked files；
11. 所有写路径必须位于绑定 root 内；
12. 相同 idempotency key 不得产生重复写入；
13. stale preview 不得提交；
14. Runtime 不得自行决定用户业务意图；
15. Runtime 的错误结果不得被 Skill 表述为整体成功。

## 10. Runtime Operation Surface

### 10.1 project_context.resolve

输入：

- project root candidate；
- allowed roots；
- requested capability；
- optional scope hints。

输出：

- resolved project root；
- wiki status；
- initialization level；
- root evidence；
- active / candidate flows；
- available domains；
- degraded capabilities；
- context refs。

性质：只读。

### 10.2 project_context.query

输入：

- query；
- scope；
- token / item budget；
- evidence requirements；
- remote access policy。

输出：

- bounded context pack；
- evidence / inference / candidate-only / stale clue 分类；
- context refs；
- gaps；
- fallback reason。

性质：只读。

Runtime 不负责回答最终业务问题，只负责提供有边界的证据包。

### 10.3 project_context.diagnose

输入：

- scan scope；
- phase；
- policy；
- optional changed / base selector。

输出：

- deterministic findings；
- score；
- affected refs；
- repair preview candidates；
- exit classification。

性质：只读。

### 10.4 project_lifecycle.preview

输入：

- intended operation；
- flow_id；
- proposed state or patch；
- evidence refs；
- expected Git / workspace state。

输出：

- proposed changes；
- affected files；
- precondition results；
- conflicts；
- required confirmations；
- preview token；
- preview digest；
- expiry。

性质：只读。

### 10.5 project_lifecycle.commit

输入：

- preview token；
- preview digest；
- idempotency key；
- confirmation evidence；
- expected workspace state。

输出：

- final status；
- step results；
- changed refs；
- transaction / journal id；
- recovery state；
- final context refs。

性质：写入；只能在 P3 引入。

## 11. JSON CLI 协议

### 11.1 CLI 只是适配器

建议形成一个薄入口，例如：

~~~text
python -m project_lifecycle_runtime resolve --request-file request.json
python -m project_lifecycle_runtime query --stdin
python -m project_lifecycle_runtime diagnose --request-file request.json
python -m project_lifecycle_runtime preview --request-file request.json
python -m project_lifecycle_runtime commit --request-file request.json
~~~

operation 的实现必须位于可导入 Python 模块中。

CLI 不得包含独立状态规则。

### 11.2 输入方式

优先支持：

1. --request-file；
2. stdin；
3. 少量简单 flags。

不要要求 Agent 在 Windows Shell 中拼接大型 inline JSON。

请求文件或 stdin 可以降低：

- 引号和转义错误；
- 命令长度问题；
- 非 ASCII 编码问题；
- secret 或敏感字段出现在进程列表中的风险。

### 11.3 输出边界

规则：

- stdout 只输出一个完整 JSON response；
- stderr 输出人类诊断、trace 和 debug log；
- 默认不输出 Markdown；
- 不把 prompt、源码正文或 secret 写入 trace；
- JSON 编码固定为 UTF-8；
- field order 不作为语义契约；
- response 必须包含 schema_version 和 operation。

### 11.4 Response Envelope

~~~json
{
  "schema_version": 1,
  "operation": "project_context.resolve",
  "status": "ok",
  "request_id": "req-...",
  "runtime_version": "0.1.0",
  "data": {},
  "context_refs": [],
  "diagnostics": [],
  "error": null
}
~~~

失败示例：

~~~json
{
  "schema_version": 1,
  "operation": "project_lifecycle.commit",
  "status": "rejected",
  "request_id": "req-...",
  "runtime_version": "0.1.0",
  "data": null,
  "context_refs": [],
  "diagnostics": [],
  "error": {
    "code": "stale_preview",
    "message": "Workspace state changed after preview.",
    "retryable": true,
    "recovery": "Run preview again."
  }
}
~~~

### 11.5 Exit Code

建议：

| Exit | 含义 |
| ---: | --- |
| 0 | operation 成功，包括有 WARN 的只读诊断 |
| 2 | 请求格式或 schema 无效 |
| 3 | precondition / conflict / stale preview |
| 4 | permission / root containment 拒绝 |
| 5 | partial commit 或 recovery_required |
| 6 | Runtime 内部错误 |

JSON error code 是稳定机器契约。

进程 exit code 只提供粗粒度自动化分类。

## 12. Preview 与事务化 Commit

### 12.1 Preview Token 绑定内容

preview token 至少绑定：

- operation；
- project id；
- resolved root identity；
- Git HEAD；
- relevant dirty-state digest；
- read-set hashes；
- proposed write-set hashes；
- policy / schema version；
- confirmation requirements；
- expiry；
- nonce。

token 可以是 opaque value，但服务端或 Runtime 必须能验证其完整性。

### 12.2 Commit 顺序

逻辑顺序：

~~~text
validate preview
  -> acquire lock
  -> recheck read set
  -> update authoritative record
  -> update artifact state
  -> generate projections
  -> append log
  -> run deterministic validation
  -> finalize journal
~~~

### 12.3 部分失败

Runtime 必须返回明确状态：

- committed；
- rejected_precondition；
- conflict；
- stale_preview；
- permission_denied；
- partially_committed；
- recovery_required。

partially_committed 不得被 Skill 改写为“已完成”。

### 12.4 原子性策略

优先顺序：

1. 同目录临时文件 + atomic replace；
2. write-ahead journal；
3. 幂等 step key；
4. 明确 recovery command；
5. 无法补偿时保留可诊断 partial state。

不要承诺跨文件系统或跨仓库的虚假全局事务。

## 13. 演进阶段

### P0：状态权威与契约

目标：不实现 MCP，不急于实现完整 CLI。

交付：

- authority model；
- invariant registry；
- operation contracts；
- response envelope；
- error taxonomy；
- context ref 规范；
- schema / storage compatibility policy；
- representative fixtures；
- Skill-only baseline；
- Doctor 和 Task Control 能力盘点。

退出条件：

- 每个写入点都有权威来源和前置条件；
- 每个投影都能追溯到权威状态；
- error code 有测试；
- operation 不依赖 MCP 命名和生命周期。

### P1：只读 Runtime + JSON CLI

实现：

- project_context.resolve；
- project_context.query；
- project_context.diagnose。

约束：

- 不写 Wiki；
- 不创建 Flow；
- 不修改 Registry；
- 不生成持久 Dashboard；
- 不替代 Router；
- CLI / Skill fallback 保持可用；
- 不启动 MCP Server。

退出条件：

- Python API 与 JSON CLI 使用同一契约测试；
- Windows / Linux 行为一致；
- root containment 有负向测试；
- bounded context pack 有预算测试；
- Doctor 结果可通过统一 envelope 返回；
- 相比 Skill-only 有可测的正确性或成本收益。

### P2：Preview

实现：

- flow lookup / match；
- proposed state transition；
- Change Brief / Bug Brief patch preview；
- Artifact、Dashboard、Handoff、Log 影响预览；
- conflict / confirmation requirements；
- preview token 和 digest。

约束：

- 不执行持久写入；
- 不允许 Preview 暗中修复；
- 不把 Preview 结果当作已提交事实。

### P3：事务化 Commit

实现：

- authoritative record update；
- Artifact Registry；
- projection generation；
- append-only Log；
- lock；
- idempotency；
- journal；
- stale preview；
- partial failure；
- recovery。

灰度策略：

- 先选择单项目、低风险、文件数有限的一个 Domain；
- 不先做跨仓库事务；
- 不先做 Base Graph 写入；
- 保留人工 diff 和 Git 回滚。

### P4：可选 MCP Adapter

只有满足 MCP 引入门槛后才实施。

实现原则：

- tool schema 是 Runtime operation 的薄映射；
- 不复制状态规则；
- 不引入新事实源；
- MCP unavailable 时 JSON CLI 仍可运行；
- 同一 fixture 同时认证 Python API、CLI 和 MCP；
- MCP 版本不能领先 Runtime schema。

## 14. MCP 引入门槛

满足以下至少一类真实需求，才进入 MCP 实现评审：

### 14.1 跨独立 Host 复用

- 至少两个独立 Agent Host 需要同一 Runtime；
- 各 Host 的 Shell / CLI glue 已出现明显重复；
- MCP 可以减少而不是增加总体适配代码。

### 14.2 Host 缺少可靠 Shell

- 目标 Host 不能可靠启动 Python CLI；
- 但支持受控 MCP tools；
- MCP 能形成真实权限边界。

### 14.3 长驻能力

- 查询需要共享 cache；
- 需要 filesystem watch；
- 需要 streaming、cancellation 或 progress；
- 重复进程启动成本已被测量为瓶颈。

### 14.4 集中权限与并发

- 多进程或多 Agent 同时访问相同项目状态；
- 需要统一 root allowlist、锁、审计和并发控制；
- 单进程 CLI 无法合理满足。

### 14.5 数据证明净收益

至少证明：

- 总 token 没有因 tool schema 和返回体上升；
- 调用轮次下降；
- Host glue 减少；
- 启动和重连失败率可接受；
- CLI fallback 仍通过；
- 权限边界更清晰。

以下情况本身不构成 MCP 理由：

- Base Graph 数据量大；
- 项目数量多；
- 想让架构看起来更 Agent-native；
- Skill 文档较长；
- 某个 Host 支持 MCP；
- 未来可能跨 Host；
- Python CLI 不够时髦。

## 15. JSON CLI 与 MCP 对比

| 维度 | JSON CLI | MCP |
| --- | --- | --- |
| 当前实现复杂度 | 低 | 中高 |
| CI / 测试复用 | 直接 | 通常仍需额外 CLI |
| 服务生命周期 | 无 | 有 |
| Host 工具发现 | 依赖 Skill / 文档 | 原生 tool schema |
| Shell 转义 | 需通过 request-file / stdin 规避 | 较少 |
| 长驻 cache / watch | 不适合 | 适合 |
| 集中权限 | 有限 | 更适合 |
| 调试链路 | 短 | 更长 |
| 跨独立 Host | 可用但需 glue | 更统一 |
| 当前 PDC 必要性 | 高 | 未证明 |

结论：

> JSON CLI 不是临时废弃物，而是 Runtime 的第一等适配器和长期 fallback。

## 16. 全局记忆与 Base Graph 的差异

全局记忆通常具备：

- 跨项目；
- 跨会话；
- 跨 Agent；
- 长期存在；
- 多个独立消费者；
- 统一访问控制和召回入口。

因此它天然更接近长驻服务或 MCP Adapter 的适用场景。

Base Graph 具备：

- 多项目范围；
- 共享目录或仓库；
- 跨会话读取；
- 大范围导航。

但这些特征只说明数据范围更大。

只要它仍然：

- 以本地仓库和 Markdown 为事实载体；
- 由同一 Host 通过允许 root 访问；
- 不需要长驻 cache / watch；
- 不需要多个独立消费者并发写；

就可以由 Runtime + JSON CLI 可靠访问。

因此：

> 跨项目是数据范围问题；MCP 是适配和服务生命周期选择。两者不能直接画等号。

## 17. 兼容与降级

### 17.1 Skill Compatibility

- Router 和子 Skill 继续存在；
- Skill 逐步删除机械执行细节，而不是一次重写；
- Runtime unavailable 时可以回到明确标注的 Skill / CLI fallback；
- fallback 不得绕过高风险 Gate。

### 17.2 Storage Compatibility

- 现有 Markdown 保持可读；
- schema 变更需要版本与 migration preview；
- Runtime 不要求一次性迁移全部项目；
- 新字段必须有旧版本降级策略；
- 派生索引可以删除并重建。

### 17.3 CLI Compatibility

- schema_version 独立于 Runtime package version；
- breaking change 必须提升 schema major；
- 旧 Doctor CLI 在统一 Runtime 成熟前继续保留；
- CLI 和 MCP 共享 fixtures，避免双接口漂移。

## 18. 验证指标

### 18.1 正确性

- wrong-root 访问次数；
- Flow / Dashboard drift；
- Artifact 漏登记；
- stale evidence 误提升；
- remote write boundary 违规；
- illegal state transition；
- 部分成功误报；
- recovery failure。

### 18.2 效率

- 单任务输入 token；
- Runtime 调用次数；
- Shell / tool round trips；
- context pack 大小；
- 平均完成时间；
- 新 Domain 接入成本。

### 18.3 可维护性

- Skill 中机械规则行数；
- operation contract 重复数；
- CLI / MCP fixture 复用率；
- schema breaking frequency；
- Host-specific glue 行数；
- 平台差异缺陷数。

### 18.4 MCP 净收益

~~~text
减少的 Host glue
  + 减少的调用轮次
  + 新增的权限与长驻能力收益
  - MCP schema tokens
  - 服务生命周期成本
  - 重连与版本握手成本
  - 双适配器维护成本
~~~

只有净收益为正，才扩大 MCP。

## 19. 主要风险与缓解

### 19.1 CLI 逻辑膨胀

风险：状态逻辑被写进 argparse handler。

缓解：CLI 只能调用可导入 Runtime API；所有 operation 用同一 fixtures 测试。

### 19.2 JSON 协议过早冻结

风险：PDC 仍在快速演进。

缓解：先冻结 envelope、error taxonomy 和 invariants；业务 payload 版本化演进。

### 19.3 Preview 被误当作 Commit

风险：Agent 根据预览宣称状态已更新。

缓解：Preview response 明确 status=preview_only，并且不返回 committed refs。

### 19.4 虚假事务

风险：跨文件或跨仓库失败后仍宣称原子成功。

缓解：journal、step result、partial state 和 recovery_required 必须显式。

### 19.5 Runtime 越权进入业务语义

风险：Runtime 开始决定创建哪个需求、是否开发或保存什么知识。

缓解：Runtime 只验证 Skill 提交的意图和状态操作，不生成业务决策。

### 19.6 MCP 永久延期

风险：CLI glue 在多个 Host 中重复，但团队仍不愿抽适配层。

缓解：使用第 14 节门槛定期评审；一旦证据满足，就实现薄 MCP Adapter。

## 20. 非目标

本路线不包括：

- 用 Runtime 替代 Skills；
- 用 CLI 替代项目语义判断；
- 用 MCP 替代 Codex 文件、Shell、Git、测试和代码工具；
- 把 Router 改成固定工作流状态机；
- 建设通用任务管理平台；
- 自动注入全部 Wiki；
- 删除 Markdown / Git 事实载体；
- 立即统一所有 Base Graph 写入；
- 立即迁移所有项目；
- 在 P1 引入持久写入；
- 在没有真实需求时启动 MCP Server。

## 21. 有意延后的决策

以下决策不在 V2 文档阶段提前冻结，而是绑定阶段 Gate：

| 决策 | 最早阶段 | 决策证据 |
| --- | --- | --- |
| Runtime 包放在当前仓库还是独立仓库 | P0 | Domain 边界和复用评估 |
| 是否复用 llm-wiki-runtime Core | P0 | record、scope、lock 和 envelope 兼容测试 |
| 是否使用本地派生索引 | P1 | 查询性能和 context budget 数据 |
| journal 还是补偿式恢复 | P2/P3 | write-set 和失败注入测试 |
| Base Graph 是否独立进程 | P3/P4 | 权限和并发需求 |
| 是否建设 MCP | P4 | 第 14 节门槛 |

延后不等于遗漏。

每项决策都有进入条件和证据要求。

## 22. 最终判断

Project Develop Copilot 最有价值的能力仍然是：

- 自然语言路由；
- 生命周期连续性；
- 项目上下文恢复；
- 证据权威顺序；
- develop、fix、finish 和 review 闭环；
- 与外部专业 Skills 的桥接。

这些能力继续留在 Skill / LLM。

当前最需要工程化的是：

- Project Root 和 Wiki Root 解析；
- 有界 Context Pack；
- Flow Record 状态转换；
- Artifact / Dashboard / Handoff / Log 投影；
- Doctor / Graph 确定性执行；
- 路径和权限边界；
- preview、lock、幂等、事务和恢复。

这些能力进入 Project Lifecycle Runtime。

本版最终结论是：

> Project Develop Copilot 有必要向 Project Lifecycle Runtime 演进；近期默认适配面应是版本化 JSON CLI。MCP 不是演进目标，而是在跨独立宿主复用、无 Shell Host、长驻能力或集中权限收益被真实证据验证后增加的薄适配器。

近期实施方向是：

> 先定义状态权威与不变量，再交付只读 Runtime / JSON CLI；随后实现 Preview；最后在单项目低风险范围内灰度事务化 Commit。MCP 保留在条件性 P4，不进入 P1。

这条路线保持：

- Skill + LLM 的语义弹性；
- Python Runtime 的确定性；
- JSON CLI 的低耦合和可测试性；
- Markdown / Git 的可审计性；
- MCP 的未来兼容空间；
- 对普通 PDC 用户透明。
