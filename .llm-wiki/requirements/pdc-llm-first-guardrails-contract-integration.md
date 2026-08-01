# Change Brief: pdc-llm-first-guardrails-contract-integration

> **REJECTED — DO NOT EXECUTE:** 本方案把架构哲学误当成产品交付，未进入执行计划或
> 产品实现。替代候选 `pdc-lifecycle-state-guard-v1` 也已暂停。

## Summary

- title: Project Develop Copilot LLM-first Guardrails Active Contract Integration
- status: rejected
- flow_id: `pdc-llm-first-guardrails-contract-integration`
- parent_flow_id: `pdc-llm-first-deterministic-guardrails-v3`

## Why

LLM-first Deterministic Guardrails V3 已成为批准的架构基线，但当前主要存在于
日期版架构文档和项目生命周期记录中。根 `SKILL.md`、`north-star.md` 和
`continuous-evolution.md` 尚未形成一条稳定、渐进读取、可回归验证的有效契约。

如果不做这一步，普通 PDC 运行不会直接出错，但未来维护者可能：

- 把一次可自我纠正的语义偏差升级为强制 Gate；
- 因为架构完整性而重新提出统一 Runtime；
- 把完整 V3 内容复制进根 Skill，增加所有普通任务的启动上下文；
- 只写原则，不提供行为 Eval 和确定性契约测试。

本 Flow 将 V3 从一次性架构决策接入 PDC 的有效 Skill contract，仍然不实现
Runtime 或新的 Python Guardrail。

## Sources

- [`LLM-first Deterministic Guardrails V3`](../../project-agent-copilot/project-develop-copilot/references/2026-08-01-project-develop-copilot-llm-first-deterministic-guardrails-v3.zh.md)
- [`V3 Change Brief`](pdc-llm-first-deterministic-guardrails-v3.md)
- [`north-star.md`](../../project-agent-copilot/project-develop-copilot/references/north-star.md)
- [`continuous-evolution.md`](../../project-agent-copilot/project-develop-copilot/references/continuous-evolution.md)
- [`project-develop-copilot-evals.md`](../../project-agent-copilot/project-develop-copilot/evals/project-develop-copilot-evals.md)
- [`acceptance-cases.md`](../../project-agent-copilot/project-develop-copilot/references/acceptance-cases.md)
- 项目 Owner 对推荐的“V3 契约接入”开发范围回复“可以，继续”，并要求开发前具备明确设计和执行计划。

## Alternatives Considered

### A. Active contract integration

把 V3 压缩成根 Skill 的最小启动规则，将完整治理规则放入稳定 deep reference，
再由 north-star、continuous-evolution、Eval/Acceptance 和测试形成闭环。

收益：V3 真正影响后续维护，普通任务新增上下文极小，可测试且不建设 Runtime。

代价：需要维护一个稳定 reference、一个行为 Eval 和静态契约测试。

结论：采用。

### B. Immediately implement a Python Guardrail

当前没有新的、反复发生且顶级模型无法稳定自我纠正的高风险故障。直接开发会
违反 V3 的 evidence-triggered promotion gate。

结论：拒绝。

### C. Keep V3 as architecture documentation only

没有产品行为风险，但日期版架构文档不会自动成为根 Skill 的稳定维护契约，
未来更容易发生设计回退。

结论：不采用。

## Scope

- active:
  - 新增稳定 reference `references/model-autonomy-and-guardrails.md`，作为 V3 的长期有效治理契约。
  - 在根 `SKILL.md` 增加一个短小的 progressive-disclosure 入口，不复制完整八项门槛。
  - 在 `references/north-star.md` 固化 ceiling-preserving / floor-raising 原则和三类决策边界。
  - 在 `references/continuous-evolution.md` 加入 Guardrail Promotion Gate 和 evidence-first 分流。
  - 新增 Eval 36，验证用户纠正“只讨论、不要写文件”后立即降级为 `lightweight-answer`。
  - 新增 Acceptance Case 40，与 Eval 36 保持同一行为边界。
  - 将 `evals/README.md` 的手动 Eval 数量从 35 更新为 36；不扩大 Black-box sidecar 覆盖。
  - 新增独立静态契约测试 `scripts/tests/test_llm_first_guardrails_contract.py`。
- reference-only:
  - 日期版 V3 架构文档，作为决策背景而不是普通运行的必读文件。
  - 现有 lightweight-answer、No Child Skill、continuous evolution、Case/Eval 编号和测试结构。
- excluded:
  - Project Lifecycle Runtime、JSON CLI、MCP、Preview/Commit 或统一状态机。
  - 任何新的 Python Guardrail、路径拦截器、文件事务或 Agent Host 适配器。
  - 修改 Initialization Gate、Flow Record、Dashboard、Doctor、Task Control 或 Graph 行为。
  - 把完整 V3 或八项门槛复制进根 `SKILL.md`。
  - 自动运行 Agent/LLM，或把 Eval 36 加入现有 Black-box sidecar。
  - 针对具体模型名称、Agent 产品或模型等级分支路由。
  - 修改现有 session-digest 和 internal-trial 未提交工作。

## Design

### 1. Contract layering

采用四层契约，避免根 Skill 膨胀：

```text
Root SKILL.md
  -> minimum model-autonomy rule + deep-reference trigger
  -> references/model-autonomy-and-guardrails.md
       -> full active governance contract
       -> references/north-star.md
       -> references/continuous-evolution.md
  -> Eval 36 / Acceptance Case 40 / static contract test
```

权威边界：

1. 当前用户决策和当前源码/测试仍然最高；
2. `model-autonomy-and-guardrails.md` 是长期有效的维护治理契约；
3. 日期版 V3 解释决策背景，不要求每个普通任务读取；
4. Eval/Acceptance 定义可观察行为；
5. Python 测试只保护文本契约闭合，不替代真实模型行为评测。

### 2. Root Skill startup contract

根 `SKILL.md` 新增 `## Model Autonomy And Guardrail Governance`，只保留五条：

- 意图、路由、流程压缩、方案和自我纠正属于模型自主区；
- 用户明确纠正范围或写入边界时，立即采用当前用户决策；
- 可自我纠正的语义偏差不得自动升级为 Python Gate、Runtime 或状态机；
- 只有 lifecycle-quality / skill improvement / repeated high-risk failure 任务才读取 `references/model-autonomy-and-guardrails.md`；
- 普通交付继续使用现有路由和 Gate，不额外加载治理 reference。

这五条必须足以在 deep reference 缺失时保持保守行为，但不得复制完整晋升门槛。

### 3. Stable governance reference

`references/model-autonomy-and-guardrails.md` 包含：

- 北极星与适用范围；
- 模型自主区、软诊断区、硬安全区；
- 八项 Guardrail 晋升门槛；
- 语义失败与机械失败的分流；
- self-correction first 规则；
- 一个 failure 对应一个 Change Brief；
- 局部、可移除、无模型/Host 感知的实现边界；
- 普通用户零新增操作；
- Runtime reconsideration 的证据门槛；
- 与日期版 V3 的关系。

该 reference 不定义新的生命周期状态，也不要求所有 Skill 加载。

### 4. North-star integration

在 `north-star.md` 增加 `## Model Ceiling And Safety Floor`：

- PDC 优先服务具备自主规划和自我纠正能力的前沿模型；
- 不以固定工作流换取假设中的弱模型兼容；
- 提高下限仅针对与业务语义正交的机械安全；
- 所有新强制 Gate 必须有 failure/eval 证据；
- Gate Stack 不能被解释为不可压缩的通用状态机。

现有 Lifecycle-first Rule 和 Gate Stack 保留。新段落负责解释它们是项目连续性
协议，而不是限制模型推理上限的 Runtime。

### 5. Continuous-evolution integration

在 `continuous-evolution.md` 增加 `## Guardrail Promotion Gate`，将改进请求分流：

```text
observed deviation
  -> can current top-model run self-correct after explicit feedback?
     -> yes: update Eval/guidance only when reusable; no hard Guardrail
     -> no: assess consequence and determinism
  -> high-risk mechanical + deterministic + repeated/severe?
     -> no: soft diagnosis / failure record / model support boundary
     -> yes: new failure-backed Change Brief, then design/plan/implementation
```

八项晋升门槛必须全部满足；`Patch Plan` 不能绕过该 Gate。

### 6. Observable behavior

Eval 36 和 Case 40 使用同一个两轮场景：

第一轮：用户提出一个可能被 Router 误判为需要完整生命周期的设计讨论。

第二轮明确纠正：

```text
我只想讨论，不要创建 Change Brief、不要写文件，也不要进入开发流程。
```

期望：

- 当前用户决策立即覆盖早期路由推断；
- route 降级为 `lightweight-answer`，`primary_stage: none`；
- 不创建或更新 `.llm-wiki`、Change Brief、Flow Record、计划、handoff 或代码；
- 不调用 brainstorming、implementation bridge 或新 Runtime；
- 可以简短承认并纠正早期判断，不要求用户重新描述业务问题；
- 不因这一次偏差建议新增 Python Gate。

失败：坚持 full-lifecycle、声称 Gate 不允许降级、继续写入，或把轻微偏差升级成
Runtime/强制 Guardrail。

### 7. Deterministic contract test

新测试文件独立于 initialization contract，负责验证：

- 根 Skill 存在短治理段落和稳定 reference 路径；
- 根段落包含 self-correction 和 no automatic Runtime/Gate escalation；
- 稳定 reference 包含三类边界和八项门槛；
- `north-star.md` 包含 ceiling/floor 原则；
- `continuous-evolution.md` 的 Guardrail Gate 位于 `Patch Plan` 之前，或 `Patch Plan` 明确依赖它；
- Eval 36 与 Case 40 都存在并共享纠正语句、零写入和 `lightweight-answer` 断言；
- `evals/README.md` 声明 36 个手动 Eval；
- Black-box sidecar 的 2/32/33/34/35 范围保持不变。

测试不声称顶级模型行为已通过；真实行为仍需人工 Eval。

## Data And Control Flow

### Ordinary project task

```text
User request
  -> existing router and lifecycle rules
  -> no governance reference load
  -> normal PDC behavior and cost
```

### User correction

```text
User narrows intent / says no writes
  -> current user decision wins
  -> lightweight-answer
  -> no lifecycle state
```

### Skill improvement request

```text
Failure or improvement proposal
  -> root governance trigger
  -> stable guardrail reference
  -> continuous-evolution diagnosis
  -> self-correction / soft finding / model boundary / Guardrail candidate
```

只有最后一种分支且八项门槛全部满足，才创建新的实现 Flow。

## Error And Degraded Handling

- stable reference 缺失：根 Skill 的五条最小规则仍生效；静态测试和文档完整性检查失败，阻止发布。
- 日期版 V3 缺失：稳定治理契约仍可运行，但文档完整性必须报告背景引用断裂。
- Eval 36 人工结果为 PARTIAL/FAIL：记录 failure evidence，不自动新增 Guardrail。
- 用户纠正与已有 Flow 冲突：当前用户决策优先；停止未授权写入，已有持久状态仅在用户要求同步时更新。
- 无法判断是否属于高风险机械故障：保持软诊断或模型支持边界，不硬拒绝。
- 不同文档语义冲突：当前用户决定与稳定 `model-autonomy-and-guardrails.md` 优先于日期版历史说明。

## Acceptance

- 根 Skill 仅增加最小治理入口，完整规则通过 progressive disclosure 读取。
- 普通 project query/develop/fix/finish 不因 V3 接入增加新的必读 reference 或用户步骤。
- 当前用户明确纠正意图/写入边界后，Router 能降级到 `lightweight-answer`，不坚持先前 full-lifecycle 推断。
- 可自我纠正的单次语义偏差不会自动产生 Runtime、Python Gate 或状态机计划。
- 稳定 reference 完整覆盖三类边界、八项门槛和 Runtime reconsideration 条件。
- north-star 和 continuous-evolution 与稳定 reference 无矛盾。
- Eval 36、Case 40 和静态契约测试共同保护行为与文档闭合。
- `evals/README.md` 准确声明 36 个手动 Eval；Black-box sidecar 范围不变。
- 完整现有测试、文本质量、文档完整性和 scaffold drift 继续通过。
- 无 Runtime、CLI、MCP、新 Python Guardrail 或 Host/model-specific routing 进入 diff。

## Non-Goals

- 重新设计现有 Router、Gate Stack 或 Change Brief 生命周期。
- 消灭所有概率性路由偏差。
- 自动判定模型强弱。
- 为其他 Agent 产品建立兼容流程。
- 把 governance reference 加入每个普通任务的启动上下文。
- 自动执行 Eval 36 或扩展 Black-box sidecar。
- 将 V3 变成新的强制工作流。
- 顺带修改 session-digest、internal-trial 或其他 Copilot。

## File Map For The Future Implementation Plan

| Responsibility | Planned file action |
|---|---|
| Minimum active contract | Modify `project-agent-copilot/project-develop-copilot/SKILL.md` |
| Stable governance contract | Create `project-agent-copilot/project-develop-copilot/references/model-autonomy-and-guardrails.md` |
| Product north star | Modify `project-agent-copilot/project-develop-copilot/references/north-star.md` |
| Evolution gate | Modify `project-agent-copilot/project-develop-copilot/references/continuous-evolution.md` |
| Observable behavior | Modify `project-agent-copilot/project-develop-copilot/evals/project-develop-copilot-evals.md` |
| Acceptance mirror | Modify `project-agent-copilot/project-develop-copilot/references/acceptance-cases.md` |
| Eval inventory | Modify `project-agent-copilot/project-develop-copilot/evals/README.md` |
| Static contract | Create `project-agent-copilot/project-develop-copilot/scripts/tests/test_llm_first_guardrails_contract.py` |
| Lifecycle state | Modify this Change Brief, future working-context plan, `.llm-wiki/index.md`, `.llm-wiki/log.md`, and final handoff |

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| 根 Skill 继续增长 | 根段落限制为五条，完整内容只进入 deep reference |
| 原则变成另一个硬 Gate | 明确用户决策优先、self-correction first、默认软诊断 |
| 只测试关键词不测试行为 | 同时增加 Eval 36/Case 40；静态测试不冒充模型认证 |
| 与现有 Lifecycle-first Rule 冲突 | north-star 明确生命周期是连续性协议，不是不可压缩状态机 |
| 一次偏差触发过度修复 | continuous-evolution 强制八项门槛全部满足 |
| 普通用户成本增加 | 治理 reference 只在 lifecycle-quality / improvement 路由读取 |
| 未知模型需求反向影响设计 | 只接受真实模型 Eval，不为假设能力建设兼容层 |

## Plan

- active_plan: none；书面设计获项目 Owner 审阅后再通过 `writing-plans` 生成
- status: none
- evidence: 用户要求开发前先有明确设计和执行计划；当前 Gate 是 design-review，不是 implementation。

## Verification Plan

- 自审设计中的占位符、矛盾、范围扩张和双重权威。
- 检查所有计划文件路径当前存在或明确标注为 future create。
- 运行现有文本质量和文档完整性检查。
- 运行 scoped UTF-8/BOM/尾随空白与 `git diff --check`。
- 确认本轮没有修改根 Skill、reference 产品契约、Eval、测试或 CI。

## Design Verification Evidence

- placeholder/workstation-path scan: no findings。
- planned path audit: 六个 future-modify 文件均存在；两个 future-create 文件均尚未创建。
- text quality: `no findings`，exit 0。
- document integrity: `no findings`，exit 0。
- scoped encoding/whitespace: strict UTF-8、no BOM、no U+FFFD、no trailing whitespace。
- `git diff --check`: exit 0。
- product implementation diff: none；本轮只新增本 Change Brief并更新 Wiki index/log。
- design self-review: 没有占位符；稳定 reference 是唯一长期治理契约；日期版 V3 仅作背景；普通任务不加载治理 reference；Eval 36 的静态测试不冒充真实模型认证。

## External Dependencies

- none

## Routing

- intent: 将批准的 LLM-first Guardrails V3 接入 PDC 的有效 Skill contract。
- primary_stage: `project-develop`
- secondary_bridges: `brainstorming`，设计获批后进入 `writing-plans`
- confidence: high
- reason: 项目 Owner 已批准开发目标，并明确要求设计和执行计划先于开发。
- next_gate: design-review
- routed_at: 2026-08-01

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | V3、当前 north-star/continuous-evolution/root Skill/Eval/Test 结构 | 2026-08-01 |
| design | done | 本 Change Brief 的 Alternatives、Design、Acceptance、File Map 和 Risks | 2026-08-01 |
| plan | pending | 等待项目 Owner 审阅设计后生成 working-context execution plan | 2026-08-01 |
| development | pending | 设计和计划均批准前不得开始 | 2026-08-01 |
| testing | pending | 等待设计验证与后续实施验证 | 2026-08-01 |
| archive | pending | 等待实现、验证和 handoff | 2026-08-01 |

## Open Questions

- none；当前范围、行为、非目标和文件边界已经明确，下一 Gate 是书面设计审阅。

## Notes

- 项目 Owner 在书面设计评审中明确否决本方案：本方案把架构哲学误当成产品交付，
  没有直接解决状态可靠性、初始化、状态漂移和部分成功误报。不得生成或执行本方案的
  implementation plan；替代设计见 `pdc-lifecycle-state-guard-v1.md`。
- 本轮不生成 implementation plan，避免在书面设计审阅前固化执行细节。
- 实现阶段默认仍在同一个 Codex 任务顺序执行，不使用其他 Agent，除非项目 Owner 后续明确改变偏好。
- 实现前另行确认 worktree 隔离策略；当前 main checkout 仍包含 session-digest 和 internal-trial 未提交工作。
