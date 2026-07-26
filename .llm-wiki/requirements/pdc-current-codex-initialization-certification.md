# Change Brief: pdc-current-codex-initialization-certification

## Summary

- title: Current Codex Initialization Gate Black-box Certification
- status: active
- flow_id: `pdc-current-codex-initialization-certification`

## Sources

- 用户批准继续验证 Initialization Gate。
- 用户明确当前只使用 Codex，不使用其他 Agent 产品或模型做测试。
- 现有 Eval 33、34、35 与 Developer-only Black-box Sidecar。

## Scope

- active:
  - 将 Black-box Sidecar 从只读 Wiki 用例扩展到 Eval 33、34、35。
  - 保持 Eval 2、32 的 v0.1 行为和历史声明边界兼容。
  - 为有写入的初始化场景增加显式写入策略，不再把所有 Git 变更一律判为失败。
  - 为 Eval 35 的第一轮预览记录独立 Git 检查点，证明保存请求前没有写入。
  - 生成仅适用于当前 Codex Run 的证据和报告。
  - 根据首轮真实 Eval 33–35 的失败证据，新增只写 `.llm-wiki/**` 的 `automatic-minimal` 初始化桥接模式。
  - 将“子 Skill 默认只读”与“用户明确禁止写入”分离，避免普通 Doctor 健康检查停在确认前。
  - 直达子 Skill 时将 `bootstrap_handoff` 定义为内部路由消息，同一轮继续执行 `project-init`，不得把 handoff 当最终答复。
- reference-only:
  - 已完成的 Initialization Gate Skill 改造。
  - 既有 Eval 2、32 真实 Agent Run。
- excluded:
  - 调用、安装或测试其他 Agent 产品。
  - 自动运行 Agent 或 Judge。
  - 跨 Agent、跨模型或“所有顶级模型已通过”的认证结论。
  - 将 Eval Sidecar 暴露给普通团队用户。

## Acceptance

- Eval 2、32 的 profile、prepare、grade 与既有测试保持通过。
- Eval 33、34、35 profile 可加载，且 Fixture 基线明确没有 `.llm-wiki/`。
- Eval 33 只允许标准 Wiki、`src/config.py` 与 `tests/test_config.py` 范围内的变更；越界写入确定性失败。
- Eval 34 只允许标准 Wiki 范围内的变更；业务源码写入确定性失败。
- Eval 35 在第二轮之前必须存在已锁定的第一轮检查点；第一轮任何 Git 写入都确定性失败。
- 缺 Wiki 的自动桥接必须携带 `bootstrap_mode: automatic-minimal`，且只能写 `.llm-wiki/**`。
- `.gitignore`、`.pre-commit-config.yaml` 与 `.github/workflows/llm-wiki-doctor.yml` 只属于用户显式 `explicit-full` init/refresh；自动桥接不得写入。
- Doctor 的默认只读诊断不等于用户禁止 bootstrap 写入；仅用户明确 no-write 时暂停确认。
- 直达任一 wiki-backed 子 Skill 且缺 Wiki 时，除明确 no-write 或根目录置信度需确认外，必须在同一轮 dispatch `project-init`；不得终止于 `bootstrap_handoff`。
- 无 canary 的初始化用例不会伪造 Wiki canary 或 Wiki 路径引用评分。
- Judge 能分别引用 Eval 35 第一轮与第二轮回答。
- 文档明确这是 Skill Developer 使用的人工 Sidecar，普通用户零感知。
- 认证结论只绑定记录在 Run 中的当前 Codex 产品、模型标签、Skill 指纹和提交。

## Plan

- active_plan: inline
- status: confirmed
- evidence: 用户回复“可以继续，目前不准备用其他 agent 来测试”。

## Verification Plan

- 先为新 profile、写入策略、Eval 35 检查点和多轮证据编写失败测试。
- 运行聚焦测试确认 RED 原因来自缺失的新契约。
- 实现最小兼容扩展与 Fixture。
- 运行完整 Black-box 测试、非 Black-box 测试、文档完整性和文本质量检查。
- 准备当前 Codex 的人工 Run；不把本开发会话冒充为干净的独立认证 Run。

## External Dependencies

- none

## Routing

- intent: 为 Initialization Gate 增加当前 Codex 的真实黑盒认证能力。
- primary_stage: `project-develop`
- secondary_bridges: `test-driven-development`
- confidence: high
- reason: 已有 Eval 定义和 Sidecar，目标是最小、可验证的兼容扩展。
- next_gate: remediation-verification
- routed_at: 2026-07-25

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | Eval 33–35、现有 Black-box v0.1 与用户边界 | 2026-07-25 |
| design | done | 本 Change Brief 的 Scope 与 Acceptance | 2026-07-25 |
| plan | done | 用户批准仅以当前 Codex 继续 | 2026-07-25 |
| development | done | Blackbox v0.2 profile、allowlist 写入策略、Eval 35 多轮检查点与 Eval 33–35 Fixture | 2026-07-25 |
| testing | done | TDD RED；Blackbox 92/92；仓库级 77/77；文本、文档、sync、Skill validation 与 diff check | 2026-07-25 |
| current-codex-run-1 | done | Eval 33–35 均完成真实 Codex/gpt-5.6-sol Run；确定性失败分别暴露根目录集成越界写入与 Doctor 误停确认 | 2026-07-26 |
| remediation | in-progress | 新增 `automatic-minimal` / `explicit-full` 边界；首轮重跑又发现直达 `project-session-extract` 停在 handoff，已进入第二轮 TDD 修复 | 2026-07-26 |
| archive | pending |  | 2026-07-25 |

## Open Questions

- none

## Notes

- Eval 33 的顺序语义仍需要回答、工具记录与 Judge 共同判断；最终 Git 状态只能证明写入范围，不能单独证明调用顺序。
- Eval 35 的第一轮零写入是可确定性验证的中间状态，因此必须在第二轮之前冻结检查点。
- Sidecar 实现已完成但本 Flow 尚未归档；下一门禁是使用当前 Codex、当前安装 Skill 和明确模型标签运行 Eval 33–35。
- 首轮真实 Run 使用 Codex Desktop / `gpt-5.6-sol`：Eval 33、35 因 `.gitignore`、`.pre-commit-config.yaml`、`.github/workflows/llm-wiki-doctor.yml` 越过 profile allowlist 失败；Eval 34 因普通健康检查被误判为禁止写入而未初始化失败。
- 修复后的第二轮真实 Run 中，Eval 35 第一轮零写入检查点通过，但第二轮直达 `project-session-extract` 后把 `bootstrap_handoff` 当成最终答复；该 Run 不作为通过证据，触发 direct-invocation dispatch 契约补强。
