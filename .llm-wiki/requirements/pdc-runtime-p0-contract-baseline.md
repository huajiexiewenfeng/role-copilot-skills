# Change Brief: pdc-runtime-p0-contract-baseline

## Summary

- title: Project Lifecycle Runtime P0 Contract And Skill-only Baseline
- status: done
- flow_id: `pdc-runtime-p0-contract-baseline`
- parent_flow_id: `pdc-runtime-first-architecture-v2`

## Why

Project Develop Copilot 已确认需要一个确定性的 Project Lifecycle Runtime，
但近期不应先实现 MCP，也不应在状态权威和错误边界尚未冻结时直接进入
只读 CLI。P0 先把现有 Skill 合同中分散的权威顺序、写入前置条件、
不变量、operation、错误码和兼容策略固化为版本化、可测试的开发者契约，
为 P1 只读 Runtime 提供唯一输入。

## Sources

- [`Runtime-first Architecture V2`](../../project-agent-copilot/project-develop-copilot/references/2026-08-01-project-develop-copilot-runtime-first-architecture-v2.zh.md)
- [`Flow Record`](../../project-agent-copilot/project-develop-copilot/references/flow-record.md)
- [`Change Brief`](../../project-agent-copilot/project-develop-copilot/references/change-brief.md)
- [`Progress Dashboard`](../../project-agent-copilot/project-develop-copilot/references/progress-dashboard.md)
- [`Project Graph`](../../project-agent-copilot/project-develop-copilot/references/project-graph.md)
- [`Session Digest`](../../project-agent-copilot/project-develop-copilot/references/session-digest.md)
- 当前 Doctor JSON CLI、Task Control reducer、Black-box Eval sidecar、发布标签
  `project-develop-copilot-v0.1.0` 及其 GitHub Actions 证据。

## Scope

- active:
  - 新建不带 `SKILL.md` 的内部 `project-lifecycle-runtime/` 开发者组件。
  - 定义版本化 authority model 和 `.llm-wiki` 写入点清单。
  - 将 Runtime-first V2 的 15 条核心不变量登记为可机读 registry。
  - 定义五个协议无关 Runtime operations、统一 response envelope、稳定错误分类和 exit code 映射。
  - 定义可移植 `context_ref` 和 schema/storage 兼容策略。
  - 提供可供 P1-P3 重放的代表性 fixture manifest。
  - 冻结 `project-develop-copilot-v0.1.0` 的 Skill-only 基线，无法测量的 token、工具调用和 drift 指标显式记为 `not_measured`。
  - 在 Linux/Windows CI 中运行 P0 合同测试。
- reference-only:
  - 现有 `scripts/llm_wiki_doctor.py` 的 JSON/exit-code 模式。
  - 现有 `project-task-dispatch/scripts/task_control.py` 的严格 schema、有限状态和权威 reducer 模式。
  - 现有 Black-box Eval sidecar；P0 只引用其边界，不扩展 Agent 自动执行。
- excluded:
  - `project_context.resolve`、`query`、`diagnose` 的真实文件读取实现。
  - JSON CLI 命令入口、请求文件解析和 stdout/stderr 运行时行为。
  - Preview token、持久写入、事务、lock、journal、幂等和 recovery。
  - MCP Server、MCP tool schema 或任何具体 Agent Host 适配器。
  - 自动运行 Agent/LLM、跨 Agent 产品认证和新增人工评测负担。
  - 改写当前 Doctor、Task Control、Router 或普通团队用户工作流。
  - 修改 `references/session-digest-implementation-plan.zh.md` 和 `internal-trial-guides/` 的既有未提交工作。

## Acceptance

- `project-lifecycle-runtime/` 是内部 Python/JSON 开发者组件，不含 `SKILL.md`、MCP Server 或面向普通用户的安装步骤。
- authority registry 覆盖 PDC 当前声明的持久写入家族；每个写入点都有权威来源、前置条件、允许写入者、投影关系和引入阶段。
- invariant registry 完整登记 Runtime-first V2 第 9 节的 15 条不变量，且每条包含稳定 ID、适用 operation、enforcement phase 和可测试证据要求。
- operation registry 只使用 `project_context.resolve/query/diagnose` 与 `project_lifecycle.preview/commit`，不绑定 MCP 命名或服务生命周期。
- response envelope 固定 `schema_version`、`operation`、`status`、`request_id`、`runtime_version`、`data`、`context_refs`、`diagnostics` 和 `error` 边界。
- error registry 中的 code 唯一、映射到已允许的 exit code，并声明 retryable、适用 operation 和最早生效阶段；测试可阻止删除或悄然改义。
- `context_ref` 只保存 repo/wiki 相对引用及明确 revision/digest/trust，不接受工作站绝对路径。
- schema/storage policy 定义 additive、breaking、reader/writer compatibility、Markdown 权威和派生缓存可重建规则。
- representative fixture manifest 至少覆盖未初始化只读解析、testing 无证据、Dashboard 超前、candidate 越级、remote write 和路径逃逸。
- Skill-only baseline 绑定发布 tag/commit/CI 证据，并把无法证明的指标保留为 `not_measured`，不生成虚假收益结论。
- P0 合同测试在 Python 3.11 的 Linux/Windows CI 中执行；实现只使用 Python 标准库且不联网。
- P0 不改变 Router、子 Skill 触发、普通用户提示、项目初始化或 Agent 调用流程，因此普通团队用户新增成本为零。

## Plan

- active_plan: [`../working-context/pdc-runtime-p0-contract-baseline.md`](../working-context/pdc-runtime-p0-contract-baseline.md)
- status: stale
- evidence: 候选计划完成后，项目 Owner 判断统一 Lifecycle Runtime 的固化风险高于当前收益，并确认由 LLM-first Guardrails V3 替代；计划未执行。

## Verification Plan

- 每个任务先增加聚焦失败测试，再实现最小契约或数据使其通过。
- 运行 P0 Runtime 合同测试、父 `scripts/tests`、Task Dispatch 测试、文本质量、文档完整性和 scaffold drift。
- 静态检查 P0 组件不含 `SKILL.md`、MCP 依赖、网络调用、工作站绝对路径或第三方 Python 依赖。
- 在 GitHub Actions 的 Ubuntu 和 Windows job 中使用同一测试命令。
- 对最终 Git union 运行 UTF-8、BOM、尾随空白和 `git diff --check` 检查，并排除既有不相关未提交文件。

## External Dependencies

- none

## Routing

- intent: 进入 Runtime-first V2 的 P0 状态权威与契约建设。
- primary_stage: `project-develop`
- secondary_bridges: `writing-plans`, `test-driven-development`, `verification-before-completion`
- confidence: high
- reason: Runtime-first P0 曾作为候选路线，但已被项目 Owner 明确否决为当前实施方向。
- next_gate: none；只有新的真实失败满足 V3 Guardrail 晋升门槛时才创建独立 Flow。
- routed_at: 2026-08-01

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | Runtime-first V2、现有 lifecycle contracts、Doctor、Task Control、v0.1.0 release | 2026-08-01 |
| design | done | 本 Change Brief 的 Scope、Acceptance 和明确非目标 | 2026-08-01 |
| plan | done | `../working-context/pdc-runtime-p0-contract-baseline.md`（candidate） | 2026-08-01 |
| development | skipped | 项目 Owner 决定不建设统一 Runtime P0；没有代码或 CI 修改 | 2026-08-01 |
| testing | skipped | 无实现内容；仅由 V3 文档修订验证覆盖历史标记 | 2026-08-01 |
| archive | done | 被 `pdc-llm-first-deterministic-guardrails-v3` 替代，候选计划不得执行 | 2026-08-01 |

## Open Questions

- none；P0 已取消，不再进入 Python 包或 CLI 设计。

## Notes

- 本文保留为被否决方案的 Change Brief，不是有效实施入口。
- 没有创建 `project-lifecycle-runtime/`、JSON catalog、CLI、MCP、测试或 CI 变更。
- 当前权威路线见 `pdc-llm-first-deterministic-guardrails-v3`。
