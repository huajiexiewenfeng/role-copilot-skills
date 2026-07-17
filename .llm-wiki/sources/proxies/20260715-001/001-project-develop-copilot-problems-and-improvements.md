# Source: Project Develop Copilot 问题与改进建议草稿

- Source id: `20260715-001-001`
- Original source: `external/pdc-improvement-draft/project-develop-copilot-problems-and-improvements.zh.md`
- Type: Markdown
- Processing mode: summary
- Status: active
- Related module: `project-agent-copilot/project-develop-copilot`

## Summary

草稿将 Project Develop Copilot 定位为面向 AI Coding Agent 的证据驱动项目生命周期 Harness，并主张下一阶段应从继续扩充提示词协议，转向仓库自一致性、机器化验证、较低使用成本和可复现案例。

草稿提出 13 类问题，覆盖文本编码、Acceptance 状态、Runtime 证据、Router 复杂度、Dashboard 写边界、风险自适应模式、结构化状态、能力协商、持续改进闭环、公开案例、文档漂移、产品定位和版本治理。

## Key Points

### 已由当前仓库证据确认

- 多个中文 Trigger 与示例存在真实 mojibake，且范围超过草稿点名的两个文件。
- Lifecycle Eval 仍以 Markdown 手工 Runbook 和静态记录为主；确定性自动测试主要覆盖 LLM Wiki Doctor。
- 协议成熟度高于 Router、Gate、Bridge 和 Resume 的端到端 Runtime 证据。
- 顶层 Router、状态模型、能力协商和版本治理需要后续分阶段收敛。

### 已按当前仓库事实重述

- `references/acceptance-cases.md` 并未在 Case 9A 中途结束；当前编号覆盖 Case 1–36，另有 9A/9B/9C，共 39 个定义，并包含 Completion Rule。Phase 0 问题改写为历史编号、状态声明和引用一致性缺少机器校验。
- `project-query` 普通模式保持只读；Dashboard 写入只在用户显式请求 `dashboard-refresh` 时发生。后续问题是职责和 Capability 解耦，而非默认查询直接越权。
- `杩`、`绔`、`瀹`、`鍙` 等单字本身是合法 Unicode，不能作为独立失败词表；检查器必须依赖可靠序列、替换字符、严格解码和上下文。
- Normative Authority 与 Observed Status Authority 必须分开描述，不能用一份笼统权威顺序混合目标和运行结果。

### 本轮延期

- Acceptance Manifest 与 Lifecycle Eval Runner。
- Quick / Standard / Strict 风险模式。
- Route Registry、Dashboard Skill 拆分和结构化状态。
- Capability Negotiation、版本迁移、公开真实案例和自动进化闭环。

## Related

- requirement: [`pdc-phase0-repository-integrity`](../../../requirements/pdc-phase0-repository-integrity.md)
- durable design: [`project-develop-copilot-improvement-plan.zh.md`](../../../../project-agent-copilot/project-develop-copilot/references/project-develop-copilot-improvement-plan.zh.md)

## Gaps

- 当前 Agent Runtime 是否能稳定导出完整工具 Trace，将在 Phase 1 设计 Lifecycle Eval Runner 时单独验证。
- 安装版中尚未回到源码的有效规则只作为一次性对账输入，不成为 CI 对本机路径的依赖。

## Next Action

详细实施计划已生成；下一步是用户确认计划并选择执行方式。
