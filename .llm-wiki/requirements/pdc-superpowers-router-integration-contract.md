# Change Brief: pdc-superpowers-router-integration-contract

## Summary

- title: PDC and Superpowers Router Integration Contract
- status: done
- flow_id: `pdc-superpowers-router-integration-contract`

## Sources

- Project Develop Copilot 根 Router、初始化契约测试与 `references/superpowers-bridge.md`。
- 本地 Superpowers frontier Router、当前安装版 Skill 与 2026-07-28 兼容性测试结果。
- 用户确认继续实现三条无需其他 Agent 的确定性集成测试。

## Scope

- active:
  - 未初始化项目必须先转交 `project-init`，不得提前桥接 `brainstorming`。
  - 已初始化项目的 Bug 路由必须先完成 PDC 证据和范围恢复，再桥接 `systematic-debugging`。
  - 仅进行轻量架构讨论时不得强制产生 brainstorming 规格或计划产物。
  - 为上述边界补开发者侧确定性契约测试，并做必要的最小契约文本修正。
- reference-only:
  - Superpowers frontier Router 与已安装 Skill。
  - 已归档的 `pdc-initialization-contract-hardening`。
- excluded:
  - 修改 Superpowers 下游具体 Skill。
  - 绑定某个 Agent Runtime 或运行其他 Agent 产品。
  - 把开发者 Eval 暴露给 PDC 普通用户。

## Acceptance

- 三个跨 Router 场景都有可重复运行的 Python 契约测试。
- 新测试在现状下先因缺少对应契约而产生预期失败，再由最小修改转绿。
- 缺少 `.llm-wiki/` 时，任何 advisory bridge 都位于 `project-init` 和初始化 readiness 之后。
- Bug 路由在桥接 `systematic-debugging` 前保留 PDC 的证据、范围和上下文所有权。
- lightweight-answer 架构讨论不要求 `docs/superpowers/specs/`、执行计划或其他 durable artifact。
- PDC 既有初始化、文本质量和文档完整性测试保持通过。
- Superpowers frontier 的已知 A0 brainstorming over-route 仍如实报告，不在本 Flow 中伪装为已修复。

## Plan

- active_plan: inline RED-GREEN integration contract
- status: confirmed
- evidence: 用户回复“可以 继续”。

## Verification Plan

- 先添加三条最小测试并单独运行，确认失败原因是契约缺口。
- 仅修改 PDC Router/bridge 契约中缺少的边界说明。
- 重新运行新测试、PDC 非 Blackbox 回归和 Superpowers frontier 关键回归。
- 检查 Git diff、编码、路径与工作树状态。

## External Dependencies

- project-id: `superpowers`
- edge_id: none
- dependency_type: local-skill-contract
- required_contract: advisory workflow Skills 不得抢占 PDC 初始化和生命周期所有权
- evidence: 本地 Superpowers 源码、已安装 Skill 与确定性测试输出
- verification_status: source-verified
- derived_staleness: fresh
- impact_on_change: 只验证并记录 PDC 的桥接边界，不修改 Superpowers 下游 Skill
- fallback_or_handoff: 若需改变 frontier 路由策略，另开 Superpowers Flow

## Routing

- intent: 增加 PDC 与 Superpowers 的跨 Router 集成契约测试。
- primary_stage: `project-develop`
- secondary_bridges: `test-driven-development`, `verification-before-completion`
- confidence: high
- reason: 用户已经确认此前提出的三个最小测试场景。
- next_gate: development
- routed_at: 2026-07-28

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | 当前 PDC/Superpowers 源码、安装版与测试结果 | 2026-07-28 |
| design | done | 本 Change Brief 的 Scope 与 Acceptance | 2026-07-28 |
| plan | done | 用户确认的三场景最小计划 | 2026-07-28 |
| development | done | 新增三场景契约测试；补充 `references/superpowers-bridge.md` 的优先级与 lightweight 边界 | 2026-07-28 |
| testing | done | 定向 3/3；PDC 非 Blackbox 81/81；Superpowers 关键路由 30/30；`passed-agent-local` | 2026-07-28 |
| archive | done | `handoff/pdc-superpowers-router-integration-contract-handoff.md` | 2026-07-28 |

## Open Questions

- none

## Notes

- 该测试面向 Skill developer，不增加普通用户操作或认知成本。
- 当前已知 frontier A0 RED 是“复杂但只讨论时可能误触发 brainstorming”；本 Flow 只确保 PDC 自身声明并测试 lightweight-answer 的产物边界。
- Skill Creator 的 `quick_validate.py` 因本地解释器缺少 `PyYAML` 未能启动；这不是 Skill 验证失败。仓库自身的文档完整性、文本质量和契约测试均已通过，但不据此声称外部结构校验器通过。
- 本 Flow 没有运行其他 Agent、完整 Blackbox 行为认证或 CI，因此验证级别保持 `passed-agent-local`。
