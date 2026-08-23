# Change Brief: pdc-lifecycle-state-guard-v1

> **PAUSED — DO NOT EXECUTE:** 当前 PDC 核心 develop、fix、Base Graph 和 LLM Wiki
> 体验正常，State Guard 的净收益尚未被真实使用证据证明。保留本设计作为候选研究，
> 不生成执行计划、不修改产品行为；只有新的重复或高影响故障证据才能重新开启。

## Summary

- title: Project Develop Copilot Lifecycle State Guard V1
- status: paused
- flow_id: `pdc-lifecycle-state-guard-v1`
- replaces_flow_id: `pdc-llm-first-guardrails-contract-integration`
- related_flow_id: `pdc-llm-first-deterministic-guardrails-v3`

## Why

上一版把“不限制模型上限、提高模型下限”当成需要显式接入根 Skill 的交付功能，
偏离了本轮真正要解决的问题。该原则应当约束架构取舍，不应成为用户或模型每次
运行都要阅读和执行的新规则。

本轮需要处理的是已经观察到的机械状态问题：

- 项目没有 `.llm-wiki/` 时，状态型子 Skill 仍可能开始执行；
- `.llm-wiki/` 目录存在不等于初始化完整或当前阶段可用；
- Flow Record、Artifact Registry、Dashboard、Handoff 和 Log 由 LLM 分散更新，
  容易产生状态漂移；
- 某些文件写入成功、另一些失败时，最终回答仍可能被表述为整体成功；
- 当前静态契约测试能证明规则写在 Skill 中，但不能证明一次真实运行获得了可靠的
  前置状态或完成后状态。

Project Lifecycle Runtime V2 对这些问题的识别是正确的，但一次性建设 Context
Engine、Projection Engine、Preview/Commit、事务恢复、JSON 平台和 MCP 过重。
本设计选择其中最小且有直接收益的垂直切片：只读的 Lifecycle State Guard。

## Sources

- 当前项目 Owner 的设计纠正：目标是提高状态可靠性、修复初始化问题、减少状态漂移、
  防止部分成功误报；模型上限/下限原则只作为设计语言。
- [`Runtime-first Architecture V2`](../../project-agent-copilot/project-develop-copilot/references/2026-08-01-project-develop-copilot-runtime-first-architecture-v2.zh.md)。
- [`MCP / Runtime 架构评估`](../../project-agent-copilot/project-develop-copilot/references/2026-07-30-project-develop-copilot-mcp-runtime-assessment.zh.md)。
- [`Flow Record`](../../project-agent-copilot/project-develop-copilot/references/flow-record.md)。
- [`Lifecycle Gates`](../../project-agent-copilot/project-develop-copilot/references/lifecycle-gates.md)。
- [`Progress Dashboard`](../../project-agent-copilot/project-develop-copilot/references/progress-dashboard.md)。
- 已完成的 [`Initialization Contract Hardening`](pdc-initialization-contract-hardening.md)。
- 已完成的 [`Current Codex Initialization Certification`](pdc-current-codex-initialization-certification.md)。
- 当前 `scripts/llm_wiki_doctor.py` 和 `scripts/tests/test_skill_initialization_contract.py`。

## Observed Gap

当前能力已经覆盖“自然语言契约”和“Wiki 内容质量”，但中间缺少可执行的状态边界：

```text
Skill says: run Initialization Gate
  -> LLM manually checks files
  -> LLM manually writes several lifecycle files
  -> Doctor validates selected wiki-quality rules
  -> LLM summarizes success or failure
```

缺失的是：

```text
selected stage
  -> deterministic preflight result
  -> existing LLM-led work
  -> deterministic state audit / claim receipt
```

Doctor 当前不负责：

- 判定所选 stage 是否具备 Wiki 前置条件；
- 判定初始化是否只是“目录存在”但结构不完整；
- 解析 Flow Record 并校验状态、证据与唯一性；
- 比较 Dashboard/Handoff 与 Flow Record 的状态强度；
- 为一次“初始化完成”或“生命周期状态已同步”声明出具机器可读结论。

## Alternatives Considered

### A. 继续只加强 Skill 文本和 Eval

优点：改动小，不增加 Python 代码。

局限：已有初始化契约和 11/11 静态测试仍未消除真实运行偏差；同类规则继续复制到
多个子 Skill，只能证明“写了规则”，不能为一次运行提供确定性状态证据。

结论：不采用为主方案。Skill 契约仍保留，但不再把它当作唯一保证。

### B. 实现完整 Project Lifecycle Runtime

优点：可以统一状态读取、转换、投影、事务和恢复，最终一致性能力最强。

局限：需要一次性固化大量尚在演进的语义和操作面；开发、迁移、跨平台和维护成本高；
容易把 Runtime 扩张为流程引擎。

结论：当前不采用。保留为未来证据驱动的演进方向。

### C. 只读 Lifecycle State Guard

实现三个小型 Python operation：`preflight`、`audit`、`verify-claim`。它只读取
项目和 `.llm-wiki`，返回结构化事实、不变量 findings、exit code 和状态声明回执。
LLM 继续负责路由、初始化内容、语义判断、修复和项目开发。

优点：直接覆盖四类真实问题；没有服务、MCP、数据库或通用事务；失败可降级；
可以用 Python fixture 在 Windows/Linux 上完整测试。

局限：它能检测和阻止误报，但第一版不自动修复漂移，也不能在 Agent Host 层强制
模型一定调用；状态写入仍由现有 Skills/LLM 完成。

结论：采用。

## Architecture Decision

### 1. 定位

Lifecycle State Guard 是 Project Lifecycle Runtime 的最小只读切片，不是新的
Router，也不是完整状态机。

```text
Skill / LLM
  - 理解用户意图
  - 选择 stage
  - 决定范围与方案
  - 执行初始化、开发和修复
  - 根据 findings 修复状态

Lifecycle State Guard
  - 读取确定性文件事实
  - 校验 stage 前置条件
  - 校验生命周期不变量
  - 判断某个机械状态声明是否有证据支持

Markdown / Git
  - 继续作为团队可读、可审计的事实载体
```

Guard 不选择 `project-develop`、`project-fix` 或 `project-query`，只校验 LLM 已经
选择的 stage。它也不决定需求是否完成、设计是否优秀或测试是否充分。

### 2. 设计原则的放置

“不限制模型上限、提高模型下限”只出现在架构说明、设计取舍和维护决策中。

产品 Skill 中只写可执行的操作契约，例如：

- 哪些 stage 之前运行 `preflight`；
- 哪些状态修改之后运行 `audit`；
- 哪些完成声明之前运行 `verify-claim`；
- blocked/partial/inconclusive 结果不得改写为成功。

不在根 Skill 中增加哲学口号、模型能力分级、Guardrail 治理章节或 Runtime 推广说明。

### 3. 第一版操作面

#### `preflight`

用途：在进入 wiki-backed/stateful stage 前获得确定性的项目状态。

输入：

- explicit project root；
- LLM 已选择的 stage；
- optional flow id；
- optional allowed root。

输出事实：

- canonical project root 和 root evidence；
- Wiki 状态：`missing`、`incomplete`、`legacy-compatible`、`ready`、`invalid`；
- 所选 stage 的初始化策略；
- 可用 lifecycle targets；
- blocking findings、warnings 和 required action；
- 是否允许进入所选 stage。

行为：

- `.llm-wiki/` 缺失且 stage 需要 Wiki：assessment 为 `blocked`，required action 为
  `project-init`；
- `.llm-wiki` 是普通文件、路径越界或关键 lifecycle target 不存在：拒绝进入写入型
  stage；
- 旧版 Wiki 具备当前 stage 所需的最小目标：返回 `legacy-compatible` 和可见 warning，
  不因可选新目录缺失而全面阻断；
- lightweight-answer 和明确无需业务 Wiki 的 mechanical-artifact 不调用 Guard。

#### `audit`

用途：读取一个 flow 或整个 Wiki，找出确定性状态漂移。

第一版检查：

- Flow Record 的 `flow_id` 唯一性；
- Flow Record table 的 step/status 合法性和重复行；
- `development`、`testing`、`archive` 为 `done` 时 Evidence 不得为空；
- 明确写成仓库内路径的 evidence 必须存在；
- Artifact Registry 中的仓库内 artifact path 必须存在；
- Dashboard 可解析时，其状态不得强于对应 Flow Record；
- `archive=done` 时必须存在 handoff/closure evidence；
- 同一 flow 的 handoff 不得声明比 Flow Record 更强的 testing/archive 状态；
- 初始化结构必须满足所选 profile 的 minimum targets；
- Doctor 已有 deterministic findings 通过同一结果聚合，而不是复制实现。

第一版不检查：

- 设计内容是否正确；
- 某条测试是否真正覆盖业务行为；
- 用户是否应该接受风险；
- 生命周期步骤必须严格串行；
- Dashboard 的视觉质量；
- 自然语言 evidence 的真实性。

无法确定解析的自定义 Markdown 返回 `inconclusive` 或 warning，不伪造 FAIL。

#### `verify-claim`

用途：在 Agent 准备声明某个机械生命周期结果前出具回执。

第一版 claim：

- `initialization-ready`：当前项目具备所选 stage 的 Wiki 前置条件；
- `lifecycle-state-synced`：指定 flow 没有阻断级状态漂移；
- `finish-state-ready`：Flow Record、verification evidence、handoff、artifact 和可选
  Dashboard 的机械状态支持 finish sync。

回执必须明确：

- `state_claim_allowed: true | false`；
- `assessment: pass | blocked | partial | inconclusive`；
- `claim_scope: lifecycle-state-only`；
- `business_completion_proven: false`；
- findings 和 required actions。

`business_completion_proven` 永远不会由 V1 设为 true。代码或业务功能是否完成仍由
实际源码、测试、CI、Review 和用户决策证明。

### 4. Stage policy

Guard 内部维护一个小型 stage policy registry，并由测试与实际子 Skill 目录闭合：

- `wiki-required`：develop、fix、ingest、finish、maintain 和三个 Project Graph 状态写入
  stage；
- `conditional`：query、review、doctor、session-extract；
- `bootstrap`：project-init、project-base-init；
- `excluded`：lightweight-answer、project-graph-visualize 等不依赖业务 Wiki 生命周期的
  mechanical-artifact。

该 registry 只回答“已选 stage 的机械前置条件”，不参与自然语言意图路由。

新增子 Skill 如果没有 policy，契约测试失败；运行时未知 stage 返回 invalid request，
不得静默假设可写。

### 5. Wiki readiness

V1 不再把“发现 `.llm-wiki/` 目录”直接等同于“任何 stateful stage 都 ready”。

Readiness 由 stage capability 决定：

```text
missing
  -> no .llm-wiki directory

invalid
  -> .llm-wiki is not a directory, root escapes boundary, or unreadable

incomplete
  -> directory exists but selected stage has no required lifecycle target

legacy-compatible
  -> old/custom layout has the minimum targets needed by selected stage
     but lacks optional current-standard entries

ready
  -> current minimum targets for the selected stage are present
```

这不会引入新的单一 sentinel。`.llm-wiki/index.md` 仍不是存在性判据；Guard 直接检查
目录和当前 stage 的最小目标。

### 6. Response envelope

stdout 只输出一个 UTF-8 JSON 对象；stderr 用于诊断。

```json
{
  "schema_version": 1,
  "guard_version": "0.1.0",
  "operation": "verify-claim",
  "execution": "completed",
  "assessment": "partial",
  "state_claim": "finish-state-ready",
  "state_claim_allowed": false,
  "claim_scope": "lifecycle-state-only",
  "business_completion_proven": false,
  "facts": {},
  "findings": [],
  "required_actions": []
}
```

`execution=completed` 只表示 Guard 正常完成检查，不代表被检查状态成功。
Agent 必须读取 `assessment` 和 `state_claim_allowed`，不能只看进程是否输出 JSON。

建议 exit code：

| Exit | Meaning |
|---:|---|
| 0 | assessment pass，或不阻断的 audit warnings |
| 2 | invalid request/schema/stage |
| 3 | precondition blocked，例如 Wiki missing/incomplete |
| 4 | deterministic invariant/drift violation |
| 5 | partial 或 inconclusive，禁止完整状态声明 |
| 6 | Guard internal error |

### 7. State authority

Guard 不创建新的项目状态数据库。权威顺序保持：

```text
current user decision
  -> current source/tests/raw verification
  -> Flow Record
  -> Artifact Registry
  -> Log
  -> Dashboard / Handoff
```

Guard 的 JSON 是一次检查回执，不反向成为项目事实源。需要持久化时，由现有
`project-finish` 将命令、exit code 和摘要记录到 verification/handoff；V1 不自动写入
receipt 文件或 Registry，避免又制造一套需要同步的状态。

### 8. Integration points

#### Root Router

- 先由 LLM 完成现有 mode/stage 选择；
- full-lifecycle 或 wiki-backed stage 在创建/恢复 lifecycle state 前调用 `preflight`；
- blocked 时保留 `pending_intent` 和 `pending_primary_stage`，进入现有 `project-init`；
- init 返回后重新调用 `preflight`，通过后才恢复原 stage。

#### Direct child invocation

- wiki-required/conditional 子 Skill 的 Initialization Gate 调用同一 `preflight`；
- 不再仅靠检查 `.llm-wiki` 是否存在；
- existing source-only/read-only exceptions 保持不变。

#### `project-init`

- V1 仍由现有 Skill/LLM 创建和补全 Wiki；
- 返回 initialization handoff 前调用 `verify-claim initialization-ready`；
- partial/inconclusive 时继续修复或如实返回，不得声称 init 已完成；
- V1 不实现 deterministic bootstrap、migration 或 project-root integrations。

#### State-changing stages

- 在一次生命周期状态写入后调用 `audit --flow-id ...`；
- findings 只要求修复确定性不一致，不限制语义内容或开发方法；
- 非阻断 warning 可带着残余风险继续。

#### `project-finish`

- 完成状态声明前调用 `verify-claim finish-state-ready`；
- 只有 `state_claim_allowed=true` 才能声明生命周期状态同步完成；
- `partial`、`blocked`、`inconclusive` 必须按原状态报告，并列出未完成项；
- 该回执不能替代 verification-before-completion、测试、CI 或 Review。

### 9. Control flow

```text
User request
  -> LLM selects mode and stage
  -> lightweight/mechanical? yes -> existing path, no Guard
  -> wiki-backed/stateful? yes
       -> preflight
          -> pass -> existing LLM-led stage
          -> missing/incomplete -> existing project-init/repair
                                  -> verify initialization-ready
                                  -> preflight again
       -> state changed?
          -> audit
          -> repair deterministic findings and rerun, or report partial
       -> completion/state-sync claim?
          -> verify-claim
          -> pass: state-scoped claim allowed
          -> blocked/partial/inconclusive: no full claim
```

Guard 不是所有推理步骤的中央调度器，只出现在机械状态边界。

## Failure Mapping

| Real problem | V1 mechanism | Observable result |
|---|---|---|
| 无 Wiki 仍进入开发 Skill | `preflight` + stage policy | exit 3，`required_action=project-init`，原 stage 不执行 |
| 只有空/残缺 `.llm-wiki` | stage-specific readiness | `incomplete`，不能只靠目录存在通过 |
| 初始化部分成功却报告完成 | post-init `verify-claim` | `state_claim_allowed=false`，列出缺失 targets |
| Flow Record 与 Dashboard/Handoff 漂移 | `audit` invariants | 明确 drift findings，finish claim 被阻断 |
| Registry 指向不存在产物 | artifact existence check | deterministic error，要求修复/降级 |
| 部分 finish sync 被写成整体完成 | compact envelope + finish receipt | assessment partial/blocked，不能改写为 pass |
| 顶级模型需要灵活压缩流程 | Guard 不路由、不计划、不规定步骤顺序 | 语义与执行方式仍由模型决定 |

## Honest Limitation

在“纯 Skill + LLM + Python、无 Host 插件”的边界下，无法从技术上强迫一个 Agent
一定调用 Python。V1 提供的是：

- 被调用时确定性的状态结果；
- 根 Router 和所有相关子 Skill 的统一调用契约；
- 静态契约测试，防止新 Skill 漏接；
- Python fixture 和 black-box 行为用例；
- 失败结果不可被产品契约合法改写为成功。

真正的 Host-level 强制执行需要 Agent Runtime hook/MCP/受控工具代理，这不在 V1。
设计和发布说明不得声称 V1 让初始化违规“物理上不可能发生”。

## User Cost

- 普通团队用户不安装服务、不配置 MCP、不学习命令、不填写状态表；
- CLI 由 PDC 内部调用，默认不展示完整 JSON；
- 用户只在 root 不确定、明确 no-write、状态确实 partial/blocked 或需要业务决策时被询问；
- lightweight-answer 和 mechanical-artifact 没有新增调用；
- 运行成本是 wiki-backed/stateful 请求边界上的短 Python 进程，目标为亚秒级；
- Python/Guard 不可用时回退现有 Skill-only 检查，并明确标记
  `lifecycle_guard: unavailable`，不得伪称 runtime-verified。

## Compatibility And Rollout

- Python 仅使用标准库；
- Windows、Linux、macOS 使用同一 fixture；
- 不依赖 Codex、Claude Code、Cursor 或其他具体 Agent API；
- 不启动常驻进程；
- 不改变 `.llm-wiki` Markdown 权威；
- 对旧版 Wiki 使用 `legacy-compatible`，只在当前 stage 缺少必要目标时阻断；
- 先以 opt-in/internal trial 运行，记录误报、漏报、运行耗时和 Guard unavailable 次数；
- 指标达到门槛后再升级为 PDC 默认契约；开发阶段不能直接把实验结果写成全面可靠性结论。

## Acceptance

- 存在一个可导入、可通过 CLI 调用、仅使用 Python 标准库的只读 State Guard。
- `preflight` 能稳定区分 missing、invalid、incomplete、legacy-compatible 和 ready。
- 已选择 wiki-required stage 且 Wiki missing/incomplete 时，Guard 返回阻断结果和稳定
  exit code；不会创建 Flow 或修改项目文件。
- init 返回后必须通过 `initialization-ready` 回执，才允许恢复 pending stage。
- `audit` 覆盖 V1 声明的 Flow/Artifact/Dashboard/Handoff deterministic invariants。
- `verify-claim` 明确区分 Guard 执行成功与被检查状态通过。
- `business_completion_proven` 始终为 false，避免把状态一致性误写成业务完成。
- partial/blocked/inconclusive 不能被 Root、project-init 或 project-finish 表述为整体成功。
- 所有 stateful/conditional 子 Skill 有闭合的 stage policy 和 preflight contract。
- 现有 source-only、explicit no-write、quick-diff-review、session preview 和
  mechanical-artifact 例外保持不变。
- fixture 覆盖 Windows/Linux 路径、缺 Wiki、残缺 Wiki、legacy Wiki、重复 flow、
  空 evidence、missing artifact、Dashboard/Handoff 漂移和 partial claim。
- 现有 PDC tests、Doctor tests、Initialization tests、Black-box sidecar、文本质量和
  文档完整性保持通过。
- 普通用户无需感知 CLI；内部试点能单独统计延迟、误报、漏报和 unavailable。

## Non-Goals

- 不实现 MCP Server 或任何 Agent 产品适配器。
- 不实现通用 Context Engine、Project Graph 查询层或 bounded context pack。
- 不实现 preview token、事务化 multi-file commit、lock、journal、rollback 或 recovery
  engine。
- 不实现 deterministic project-init/bootstrap 或迁移引擎。
- 不自动修复 Flow Record、Dashboard、Handoff 或 Artifact Registry。
- 不把 Router、需求讨论、方案选择、验证充分性或生命周期顺序写成状态机。
- 不把 Guard JSON 作为新的持久化事实源。
- 不承诺检测自然语言中的所有虚假完成声明。
- 不为假设中的弱模型增加分支流程。
- 不修改 session-digest 和 internal-trial 的现有未提交工作。

## Future Promotion Gates

只有 V1 试点证据证明相应问题仍然存在，才考虑后续能力：

| Candidate | Required evidence |
|---|---|
| deterministic bootstrap | 多次出现 init 结构 partial/错误恢复问题，且 post-init verify 只能反复人工修复 |
| state transition reducer | Flow Record 非法转换/并发覆盖持续发生，单纯 audit 无法降低漂移 |
| projection generator | Dashboard/Handoff 漂移频率高且修复成本显著 |
| preview/commit transaction | 多文件生命周期写入 partial 仍是高频高风险问题 |
| MCP adapter | 跨独立 Host 复用或无可靠 Shell 的真实需求成立 |

后续能力分别建立独立 Change Brief，不把它们预埋进 V1。

## Planned Product File Map

以下只用于设计评审；设计通过后才生成逐步执行计划：

| Responsibility | Planned action |
|---|---|
| Guard CLI/API | Create `project-agent-copilot/project-develop-copilot/scripts/project_lifecycle_guard.py` and minimal importable helpers if needed |
| Guard unit/fixture tests | Create `project-agent-copilot/project-develop-copilot/scripts/tests/test_project_lifecycle_guard.py` |
| Root integration | Modify `project-agent-copilot/project-develop-copilot/SKILL.md` |
| Shared behavior contract | Create `project-agent-copilot/project-develop-copilot/references/lifecycle-state-guard.md` |
| Router/readiness detail | Modify `project-agent-copilot/project-develop-copilot/references/lifecycle-router.md` and `references/lifecycle-gates.md` |
| Initialization postcondition | Modify `project-agent-copilot/project-develop-copilot/project-init/SKILL.md` |
| Finish claim receipt | Modify `project-agent-copilot/project-develop-copilot/project-finish/SKILL.md` |
| Audit integration | Modify `project-agent-copilot/project-develop-copilot/project-maintain/SKILL.md` and `project-review/SKILL.md` |
| Direct child preflight | Modify only wiki-required/conditional child `SKILL.md` Initialization Gate sections |
| Contract closure tests | Modify `scripts/tests/test_skill_initialization_contract.py`; create a focused Guard integration contract test only if separation improves diagnostics |
| Observable behavior | Extend the existing uninitialized Eval/Acceptance case and add partial-Wiki/state-drift cases |
| Developer docs | Add a developer-only Guard section; do not add ordinary user steps |
| Lifecycle state | Update this Change Brief, future execution plan, index/log and final handoff |

## Verification Strategy

### Deterministic tests

- RED/GREEN unit tests for every state classification, invariant, response field and exit code；
- temp Git fixtures for path/evidence/artifact behavior；
- existing Doctor functions reused through an adapter test，避免两套 findings 语义；
- malformed/custom Markdown produces inconclusive，not false FAIL；
- test discovery proves every child Skill has exactly one supported policy；
- source and installed Skill trees pass the same integration contract after sync。

### Behavior tests

- Existing uninitialized development scenario must still initialize before business writes；
- Partial `.llm-wiki` fixture must not be treated as ready solely because the directory exists；
- Drift fixture must not allow finish-state-ready；
- Partial finish answer must name incomplete state and avoid “已完成/已同步完成” claims；
- No black-box assertion claims an internal CLI call unless the trace is actually captured；
  behavior is judged from observable state and answer。

### Release evidence

- Windows and Linux Python test suites；
- all existing PDC non-blackbox and blackbox tests；
- Skill validation/package；
- text quality/document integrity/sync-doctor/diff check；
- internal trial report with latency, false-positive, false-negative and unavailable counts；
- no claim of Host-level enforcement or cross-Agent certification without corresponding evidence。

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| Guard 变成 Runtime-first V2 的入口 | V1 operation/file/non-goal freeze；新增 operation 必须另开 Change Brief |
| 只读检查只能发现、不能修复 | 同一轮由 LLM 按精确 findings 修复并重跑；用试点数据决定是否需要 reducer/commit |
| 旧 Wiki 被误判不兼容 | stage-specific minimum + `legacy-compatible`；可选目录只 warning |
| Markdown parser 误报 | 只解析已定义表格/数据区；不确定即 inconclusive，不猜测语义 |
| Agent 忽略 Guard | 根与 direct-child 双入口契约、闭合测试和 black-box；明确非 Host-level 保证 |
| CLI 输出成功被误读为状态成功 | 分离 `execution`、`assessment`、`state_claim_allowed` 并测试错误分支 |
| Guard 验证被误当业务完成 | 固定 `claim_scope=lifecycle-state-only`、`business_completion_proven=false` |
| 普通用户感知复杂度 | 内部调用、无服务/配置/表单；仅真实 blocked/partial 时呈现结果 |
| Doctor 规则重复 | 复用 Doctor Python API/finding adapter，不复制 checker |
| 性能影响 | 只在状态边界调用；限定扫描目录和 flow；内部试点记录 P50/P95 |

## Plan

- active_plan: none
- status: skipped while paused
- reason: 当前 PDC 的核心路径已被真实使用证明好用，但 State Guard 的收益尚未量化，
  默认接入会增加新的检查、兼容和失败路径。项目 Owner 决定保留设计并暂停升级。

## Design Verification Plan

- 核对 V1 是否实际映射四类用户问题，而不是只增加原则文本。
- 核对所有 operation 均为只读，产品文件地图不包含 Runtime 写入/事务能力。
- 核对 Skill 集成只有具体调用契约，没有哲学口号。
- 核对 existing source-only/no-write/mechanical exceptions 未被误删。
- 核对 V1 与 V2、V3、旧 P0 计划的替代关系清楚，不会误执行旧计划。
- 运行文本质量、文档完整性、UTF-8/BOM/尾随空白和 `git diff --check`。
- 确认本轮没有修改任何产品 Skill、Python、Eval、测试或 CI。

## External Dependencies

- Python 3 standard library
- Git 只用于测试 fixture 和既有证据读取；Guard V1 本身不要求修改 Git 状态
- no MCP, no daemon, no Agent-specific API

## Routing

- intent: 以最小只读 Runtime 切片解决 PDC 真实生命周期状态可靠性问题。
- primary_stage: design only
- confidence: high
- reason: 用户否决纯哲学契约集成，并明确了四个需要实际解决的状态问题。
- next_gate: none；只有重复或高影响真实故障满足 Future Promotion Gates 时重新开启
- routed_at: 2026-08-01

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | 用户纠正、V2/V3、现有 Initialization Gate/Doctor/Flow Record/Finish 契约 | 2026-08-01 |
| design | done | 本 Change Brief 作为候选研究设计保留，不代表实施批准 | 2026-08-01 |
| plan | skipped | 项目 Owner 决定暂停升级，不生成 execution plan | 2026-08-01 |
| development | skipped | 未修改 PDC 产品 Skill、Python、Eval 或 CI | 2026-08-01 |
| testing | skipped | 没有产品实现需要测试；仅验证设计文档完整性 | 2026-08-01 |
| archive | done | 项目 Owner 决定同步候选设计到 GitHub 并暂停升级；见 index/log | 2026-08-01 |

## Open Questions

- none while paused；未来只有真实故障证据重新开启本 Flow 时，才重新评估只读 Guard
  与 deterministic bootstrap 的边界。

## Notes

- 2026-08-01，项目 Owner 判断当前无法证明本优化为正向收益；PDC 核心功能保持正常，
  因此决定同步设计记录但暂停升级。
- 上一版 active-contract integration 已被项目 Owner 明确否决，不得进入执行计划。
- 本设计没有修改已发布 V3 文档；如果本设计获批，实施计划中需要把 V3 的“当前不建设
  Runtime”修订为“只建设只读 State Guard，不建设完整 Runtime”。
- 当前 main checkout 中 session-digest 和 internal-trial 的未提交工作保持不变。
