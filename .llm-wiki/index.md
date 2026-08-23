# Role Copilot Skills LLM Wiki

本目录记录 `role-copilot-skills` 的项目生命周期状态。项目事实仍以当前用户决定、源码、测试和原始需求材料为准。

## Active Flow

- none

## Sources

- [`20260715-001-001`](sources/proxies/20260715-001/001-project-develop-copilot-problems-and-improvements.md)：外部改进建议稿的校准摘要。

## Durable Design

- [`project-develop-copilot-improvement-plan.zh.md`](../project-agent-copilot/project-develop-copilot/references/project-develop-copilot-improvement-plan.zh.md)
- [`LLM-first Deterministic Guardrails V3`](../project-agent-copilot/project-develop-copilot/references/2026-08-01-project-develop-copilot-llm-first-deterministic-guardrails-v3.zh.md)：Skill/LLM 保留语义与流程自主权；Python Guardrail 只能由真实、高风险、重复且不可稳定自纠正的机械故障触发。

## Historical Design

- [`Runtime-first Architecture V2`](../project-agent-copilot/project-develop-copilot/references/2026-08-01-project-develop-copilot-runtime-first-architecture-v2.zh.md)：被 V3 替代，未实现 Runtime。
- [`pdc-runtime-p0-contract-baseline`](working-context/pdc-runtime-p0-contract-baseline.md)：未执行的 P0 候选计划，已标记 `SUPERSEDED — DO NOT EXECUTE`。

## Implemented Plan

- [`pdc-llm-first-deterministic-guardrails-v3`](requirements/pdc-llm-first-deterministic-guardrails-v3.md)：项目 Owner 已批准当前架构基线；V2/P0 作为历史保留，未实现 Runtime，详见 [`handoff`](handoff/pdc-llm-first-deterministic-guardrails-v3-handoff.md)。
- [`pdc-project-task-dispatch-control-plane`](requirements/pdc-project-task-dispatch-control-plane.md)：为 `project-task-dispatch` 增加有限状态、严格子任务回执、主线程权威归约和确定性任务投影；本地 25/25 子测试、3/3 定向父集成与 177/177 父集合回归通过，详见 [`handoff`](handoff/pdc-project-task-dispatch-control-plane-handoff.md)。
- [`pdc-phase0-repository-integrity`](working-context/pdc-phase0-repository-integrity.md)：8 个 TDD/验证任务已执行；修复后 whole-branch re-review 为 Critical 0、Important 0、`Ready to merge: Yes`，Wiki Integrity Gate 已归档。GitHub 托管 CI 仍待运行。
- [`pdc-initialization-contract-hardening`](requirements/pdc-initialization-contract-hardening.md)：补齐初始化 Gate、子 Skill 初始化策略覆盖和 `project-graph-visualize` mechanical-artifact 路由；本地回归完成并已提交 GitHub，详见 [`handoff`](handoff/pdc-initialization-contract-hardening-handoff.md) 与 [`升级复盘`](../project-agent-copilot/project-develop-copilot/references/upgrades/2026-07-25-project-develop-copilot-upgrade-retrospective.zh.md)。
- [`pdc-current-codex-initialization-certification`](requirements/pdc-current-codex-initialization-certification.md)：完成 Eval 33–35 当前 Codex 认证、初始化边界修复与 file-only 可观测性收口；顺序/内部 gate 断言以 `MANUAL_CHECK_REQUIRED` 保留，详见 [`handoff`](handoff/pdc-current-codex-initialization-certification-handoff.md)。
