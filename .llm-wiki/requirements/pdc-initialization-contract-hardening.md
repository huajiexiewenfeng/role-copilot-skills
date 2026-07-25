# Change Brief: pdc-initialization-contract-hardening

## Summary

- title: Project Develop Copilot Initialization Contract Hardening
- status: ready
- flow_id: `pdc-initialization-contract-hardening`

## Sources

- 当前 Project Develop Copilot Router、`llm-wiki-doctor`、`project-session-extract` 与初始化契约测试。
- 用户确认继续实施 2026-07-25 的最小补强方案。

## Scope

- active:
  - 为 `llm-wiki-doctor` 补齐结构化 Initialization Gate 与 bootstrap handoff。
  - 为 `project-session-extract` 明确“无 Wiki 可预览、写入或 promotion 前必须 init”的条件化门禁。
  - 扩充初始化契约测试、Acceptance 与 Eval，防止新增子 Skill 漏掉初始化策略。
  - 将用户确认的 `project-graph-visualize` mechanical-artifact Skill 从当前安装版纳入源码仓库，并接入根路由。
- reference-only:
  - 已提交的 P0 bootstrap 修复及其 Eval 33。
- excluded:
  - 重写总路由或已经具备 Initialization Gate 的核心子 Skills。
  - 修改 Superpowers 桥接 Skills。
  - 自动运行真实 Agent 或绑定特定 Agent Runtime。

## Acceptance

- 无 `.llm-wiki/` 时，Doctor 保留原始诊断目标并结构化转交 `project-init`，不得运行 Doctor。
- Session Extract 在无 Wiki 时允许只读候选预览，但保存 Session Digest 或 Lifecycle Promotion 必须结构化转交 `project-init`。
- 初始化契约测试覆盖全部 Project Develop Copilot 子 Skill，并拒绝未分类的新子 Skill。
- 既有初始化门禁行为和 Eval 33 保持不变。
- `project-graph-visualize` 在源码中具有完整 Skill、脚本、模板、Eval 与 smoke test，并通过根路由的 `mechanical-artifact` 模式直接调用。
- 可视化生成只允许写目标 HTML，不创建 Change Brief、Flow Record、计划或 finish-sync 状态。

## Plan

- active_plan: inline
- status: confirmed
- evidence: 用户回复“可以，继续”。

## Verification Plan

- 先扩充契约测试并确认新增断言产生预期失败。
- 最小修改两个 Skill 使定向测试转绿。
- 运行完整脚本测试、Skill validation、文本/文档检查和 Git diff 检查。

## External Dependencies

- none

## Routing

- intent: 加固缺少 `.llm-wiki` 时的 Project Develop Copilot 子 Skill 门禁。
- primary_stage: `project-develop`
- secondary_bridges: `skill-creator`, `writing-skills`, `test-driven-development`
- confidence: high
- reason: 用户已确认前一轮提出的最小补强范围。
- next_gate: RED contract tests
- routed_at: 2026-07-25

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | 当前 Skill 与初始化契约测试 | 2026-07-25 |
| design | done | 本 Change Brief 的 Scope 与 Acceptance | 2026-07-25 |
| plan | done | 用户确认的最小补强方案 | 2026-07-25 |
| development | done | 两个初始化 Gate、Eval 34–35、Case 38–39、`project-graph-visualize` 完整包、根路由、README 与契约测试 | 2026-07-25 |
| testing | done | 最终契约 11/11；非 Blackbox 77/77；Blackbox 81/81；Visualizer smoke 18/18；checkers、sync、diff 与 Skill validation | 2026-07-25 |
| archive | pending | 待 finish/review | 2026-07-25 |

## Open Questions

- none

## Notes

- Skill 被模型选择不等于允许执行；本变更约束的是检查项目根目录后的执行与写入边界。
- 验证证据：初始化 Gate 定向测试先产生预期失败，迁移 visualizer 后最终 11/11 通过；非 Blackbox 77/77、Blackbox 81/81、Visualizer smoke 18/18；文本质量与文档完整性均无 findings；`sync-doctor.py --check`、`git diff --check` 以及根 Skill / visualizer 的 `quick_validate.py` 均退出 0。
- 用户已明确批准把 `project-graph-visualize` mechanical-artifact 扩展纳入源码并统一提交 GitHub。
- 安装目录同步后重新运行初始化契约测试为 11/11；源码与安装目录全树 SHA-256 对照差异数为 0。
