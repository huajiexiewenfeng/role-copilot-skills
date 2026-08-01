# Change Brief: pdc-runtime-first-architecture-v2

## Summary

- title: Project Develop Copilot Runtime-first Architecture V2
- status: done
- flow_id: `pdc-runtime-first-architecture-v2`

## Sources

- `project-agent-copilot/project-develop-copilot/references/2026-07-30-project-develop-copilot-mcp-runtime-assessment.zh.md`
- `project-agent-copilot/project-develop-copilot/scripts/llm_wiki_doctor.py`
- `project-agent-copilot/project-develop-copilot/project-task-dispatch/references/task-control-plane.md`
- `project-agent-copilot/project-develop-copilot/project-task-dispatch/scripts/task_control.py`
- 用户 2026-08-01 对 MCP 前置顺序的修正意见及确认。

## Scope

- active:
  - 保留旧版评估作为历史基线。
  - 新建 Runtime-first V2 架构评估。
  - 将近期默认适配面从 MCP 收窄为版本化 JSON CLI。
  - 明确只读 Runtime、Preview、事务化 Commit 和可选 MCP Adapter 的阶段顺序。
  - 定义 MCP 引入门槛、JSON 协议约束、状态权威和不变量。
- reference-only:
  - 当前 Doctor JSON CLI。
  - Task Control 权威状态 reducer 与测试。
- excluded:
  - 修改 2026-07-30 旧稿。
  - 实现 Project Lifecycle Runtime、CLI 或 MCP。
  - 修改当前 session-digest 与 internal-trial 工作。
  - 承诺某个 Agent Host 或跨 Host 交付日期。

## Acceptance

- 最终结论明确区分“必须建设 Runtime”和“当前不必建设 MCP”。
- 目标架构为 Skill / LLM 控制面、Runtime 状态内核、JSON CLI 默认适配器、MCP 可选适配器。
- 阶段顺序为 invariant -> read-only Runtime/JSON CLI -> preview -> transactional commit -> optional MCP。
- `resolve`、`query`、`diagnose`、`preview`、`commit` 被定义为 Runtime operations，而不是预先绑定的 MCP tools。
- JSON CLI 定义版本化 envelope、稳定错误码、stdout/stderr 边界和 Windows 友好的请求输入方式。
- MCP 只有在跨独立 Host、无 Shell Host、长驻能力或集中权限边界出现真实需求后才进入实施。
- 明确 Base Graph 数据范围大不等于必须 MCP；全局记忆的跨项目、跨会话、跨 Agent 特征更适合服务化适配。
- 文档不把当前工作树原型写成已发布 Runtime，也不宣称尚未实施的事务能力已经存在。

## Plan

- active_plan: inline documentation revision
- status: confirmed
- evidence: 用户回复“可以，继续，我们来写一个新的版本”。

## Verification Plan

- 检查新版是否包含全部 Acceptance。
- 扫描未完成占位符、工作站绝对路径和旧版“必须向 MCP 演进”结论残留。
- 运行项目文档完整性与文本质量检查。
- 使用 `git diff --check` 并确认未修改用户现有工作。

## External Dependencies

- none

## Routing

- intent: 重写 Project Develop Copilot Runtime 架构评估。
- primary_stage: `project-develop`
- secondary_bridges: `brainstorming`, `verification-before-completion`
- confidence: high
- reason: 用户已确认 Runtime-first、JSON CLI-first 的架构方向和文档落地。
- next_gate: none；V2 已被 `pdc-llm-first-deterministic-guardrails-v3` 替代
- routed_at: 2026-08-01

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | 旧版评估、Doctor、Task Control 与用户结论 | 2026-08-01 |
| design | done | Runtime-first / JSON CLI-first 方向已获用户确认 | 2026-08-01 |
| plan | done | inline documentation revision | 2026-08-01 |
| development | done | `references/2026-08-01-project-develop-copilot-runtime-first-architecture-v2.zh.md` | 2026-08-01 |
| testing | done | 文档完整性/文本质量 19/19；编码、占位符、路径、围栏和阶段顺序自检通过 | 2026-08-01 |
| archive | done | 项目 Owner 后续否决 Runtime-first 作为当前路线；V3 保留风险分析并替代实施结论 | 2026-08-01 |

## Open Questions

- none；本 Flow 作为历史设计归档

## Notes

- 本 Flow 只交付了历史设计文档，没有实现 Runtime、CLI 或 MCP。
- 项目 Owner 的最终哲学是 ceiling-preserving / floor-raising；当前权威设计为 `pdc-llm-first-deterministic-guardrails-v3`。
- V2 保留用于解释为何没有继续 Runtime-first 路线，不得作为实施计划恢复执行。
