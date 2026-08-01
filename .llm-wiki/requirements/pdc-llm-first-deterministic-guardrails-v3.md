# Change Brief: pdc-llm-first-deterministic-guardrails-v3

## Summary

- title: Project Develop Copilot LLM-first Deterministic Guardrails V3
- status: done
- flow_id: `pdc-llm-first-deterministic-guardrails-v3`
- replaces_flow_id: `pdc-runtime-first-architecture-v2`

## Why

PDC 当前主要由顶级模型使用，实际体验表明模型能够处理大部分语义判断，
并在用户提醒后纠正偶发偏差。强制建设统一 Project Lifecycle Runtime
可能把可演进的 Skill 协议固化为工作流引擎，限制未来模型的能力上限，
同时为尚未证实的弱模型兼容需求增加复杂度。

项目 Owner 确立新的北极星：

> 不限制模型的上限，通过必要、最小、基于真实故障的确定性保护提高下限。

## Sources

- [`Runtime-first Architecture V2`](../../project-agent-copilot/project-develop-copilot/references/2026-08-01-project-develop-copilot-runtime-first-architecture-v2.zh.md)，作为被替代的历史方案。
- [`LLM-first Deterministic Guardrails V3`](../../project-agent-copilot/project-develop-copilot/references/2026-08-01-project-develop-copilot-llm-first-deterministic-guardrails-v3.zh.md)。
- 已发布的 `project-develop-copilot-v0.1.0` 及当前顶级模型使用体验。
- 现有 Initialization Gate、Doctor、repository integrity checks、Black-box Eval 和 Task Control 的边界证据。
- 项目 Owner 2026-08-01 关于“不能限制模型上限，提高模型下限”的明确决策。

## Scope

- active:
  - 将 PDC 的架构北极星改为 LLM-first、ceiling-preserving、floor-raising。
  - 明确模型自主区、软诊断区和硬安全区三类边界。
  - 定义 Guardrail 从真实失败晋升的严格门槛。
  - 明确当前不建设统一 Project Lifecycle Runtime、JSON CLI operation 平台或 MCP Adapter。
  - 保留现有小型 Python 工具和 Domain-specific reducer，不把它们强行统一。
  - 将 Runtime-first V2 和 P0 Runtime 计划标记为历史、不可执行。
- reference-only:
  - V2 中关于路径安全、证据、状态漂移、跨平台和部分成功的风险分析。
  - 当前面向 Codex/顶级模型的 Eval 证据；不外推到未认证模型。
- excluded:
  - 新增 Guardrail、Runtime、CLI、MCP、Schema Registry 或状态机代码。
  - 修改根 Router、子 Skill、现有 Python 工具或普通用户工作流。
  - 为未实际使用、未评测的模型建设兼容层。
  - 自动识别模型等级或针对具体 Agent 产品分流。
  - 修改 session-digest 和 internal-trial 的既有未提交工作。

## Acceptance

- V3 明确 Skill/LLM 拥有意图、路由、流程压缩、需求判断、验证充分性和自我纠正权。
- Guardrail 不得决定业务语义、固定生命周期顺序或要求所有任务经过统一 operation。
- 软诊断默认只返回证据和 warning，由 LLM 决定如何处理。
- 硬拒绝只适用于可确定判断且后果涉及越权、破坏、不可逆副作用或虚假机械成功的边界。
- 新 Guardrail 必须有重复真实失败、无法稳定自纠正、高风险后果、确定性判定、最小实现和前后证据。
- 当前不因假设中的弱模型需求建设 Runtime；模型支持范围以真实 Eval 为准。
- 普通用户不增加安装、配置、prompt、表单、Runtime 或 Eval 操作。
- V2/P0 文档被保留为历史决策证据，但明确不得执行。
- 本 Flow 只交付设计修订，不修改产品行为或代码。

## Plan

- active_plan: inline documentation revision
- status: confirmed
- evidence: 项目 Owner 明确提出 ceiling-preserving / floor-raising 哲学，并在方案说明后回复“可以继续”。

## Verification Plan

- 检查 V3 是否清楚区分模型自主、软诊断和硬安全。
- 检查是否仍残留“必须建设 Runtime”“P0 是强制前置”等当前结论。
- 检查 V2/P0 历史文档是否有醒目的 superseded / do-not-execute 标记。
- 运行项目文本质量、文档完整性和 `git diff --check`。
- 确认没有 Runtime/Guardrail 代码、CI 或 Skill 行为修改进入本 Flow。

## External Dependencies

- none

## Routing

- intent: 修订 PDC 架构哲学，避免 Runtime 过度设计和模型能力上限受限。
- primary_stage: `project-develop`
- secondary_bridges: `brainstorming`, `verification-before-completion`
- confidence: high
- reason: 项目 Owner 已明确当前顶级模型体验和架构取舍。
- next_gate: repository integration decision；未发现真实 Guardrail 候选前不进入实现计划。
- routed_at: 2026-08-01

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | 当前 PDC 使用体验、V2/P0 历史方案、现有工具边界 | 2026-08-01 |
| design | done | `references/2026-08-01-project-develop-copilot-llm-first-deterministic-guardrails-v3.zh.md` | 2026-08-01 |
| plan | skipped | 当前没有满足晋升门槛的 Guardrail，不创建代码实施计划 | 2026-08-01 |
| development | skipped | 本 Flow 不修改产品行为或代码 | 2026-08-01 |
| testing | done | text quality、document integrity、scoped encoding/whitespace 与 `git diff --check` 均无 findings；产品代码 diff 为空 | 2026-08-01 |
| archive | done | 项目 Owner 回复“确认，继续”；`../handoff/pdc-llm-first-deterministic-guardrails-v3-handoff.md` | 2026-08-01 |

## Open Questions

- none for the architecture revision；未来 Guardrail 只能由新的真实失败证据打开独立 Change Brief。

## Notes

- V3 不承诺让较弱模型达到顶级模型的表现。
- Domain-specific Python 工具可以继续存在，但不能仅因数量增加就自动合并成 Runtime。
- “不限制模型上限”不等于取消副作用安全边界；安全边界必须与业务推理正交。
- 本 Flow 没有具体 Guardrail 实现目标，因此不创建或执行 implementation plan。
