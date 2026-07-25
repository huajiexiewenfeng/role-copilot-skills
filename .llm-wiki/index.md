# Role Copilot Skills LLM Wiki

本目录记录 `role-copilot-skills` 的项目生命周期状态。项目事实仍以当前用户决定、源码、测试和原始需求材料为准。

## Active Flow

- [`pdc-phase0-repository-integrity`](requirements/pdc-phase0-repository-integrity.md)：Project Develop Copilot Phase 0 仓库自一致性已完成代理本地实现、验证与独立全分支复审；`archive` 已完成，当前等待用户决定未提交分支的集成方式。

## Sources

- [`20260715-001-001`](sources/proxies/20260715-001/001-project-develop-copilot-problems-and-improvements.md)：外部改进建议稿的校准摘要。

## Durable Design

- [`project-develop-copilot-improvement-plan.zh.md`](../project-agent-copilot/project-develop-copilot/references/project-develop-copilot-improvement-plan.zh.md)

## Implemented Plan

- [`pdc-phase0-repository-integrity`](working-context/pdc-phase0-repository-integrity.md)：8 个 TDD/验证任务已执行；修复后 whole-branch re-review 为 Critical 0、Important 0、`Ready to merge: Yes`，Wiki Integrity Gate 已归档。GitHub 托管 CI 仍待运行。
- [`pdc-initialization-contract-hardening`](requirements/pdc-initialization-contract-hardening.md)：补齐初始化 Gate、子 Skill 初始化策略覆盖和 `project-graph-visualize` mechanical-artifact 路由；本地回归完成并已提交 GitHub，详见 [`handoff`](handoff/pdc-initialization-contract-hardening-handoff.md) 与 [`升级复盘`](../project-agent-copilot/project-develop-copilot/references/upgrades/2026-07-25-project-develop-copilot-upgrade-retrospective.zh.md)。
