# Handoff: pdc-llm-first-deterministic-guardrails-v3

## Summary

Project Develop Copilot 的当前架构方向已经从 Runtime-first 修订为
LLM-first Deterministic Guardrails。项目 Owner 批准以下北极星：

> 不限制模型的上限，通过必要、最小、基于真实故障的确定性保护提高下限。

本 Flow 只交付架构决策和生命周期同步，没有修改 PDC 产品代码、Skill、
CI、Python 工具或普通用户工作流。

## Final Decision

- Skill / LLM 保留意图、路由、流程压缩、方案、验证判断和自我纠正权。
- 当前不建设统一 Project Lifecycle Runtime、JSON CLI operation 平台、Preview/Commit 协议或 MCP Adapter。
- 现有 Doctor、repository checks、Black-box Eval、Task Control 和 visualizer 保持独立，不因“架构完整性”被强制统一。
- 新 Python Guardrail 只能由真实、高风险、重复、不可稳定自纠正且可确定判断的机械故障触发。
- 未实际使用或认证的弱模型不构成当前架构建设理由。

## Artifacts

- Current design: `project-agent-copilot/project-develop-copilot/references/2026-08-01-project-develop-copilot-llm-first-deterministic-guardrails-v3.zh.md`
- Lifecycle anchor: `.llm-wiki/requirements/pdc-llm-first-deterministic-guardrails-v3.md`
- Historical V2: `project-agent-copilot/project-develop-copilot/references/2026-08-01-project-develop-copilot-runtime-first-architecture-v2.zh.md`
- Cancelled P0 plan: `.llm-wiki/working-context/pdc-runtime-p0-contract-baseline.md`

The repository does not currently contain `.llm-wiki/artifacts/index.md` or an
enabled progress dashboard. This design-only Flow did not create either one.

## Verification

- executor: agent-local
- scope: V3/V2/P0 design and lifecycle Markdown only
- text quality:
  - command: `python project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py --root project-agent-copilot/project-develop-copilot`
  - result: `text quality: no findings`
  - exit code: 0
- document integrity:
  - command: `python project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py --root project-agent-copilot/project-develop-copilot`
  - result: `document integrity: no findings`
  - exit code: 0
- Git whitespace:
  - command: `git diff --check`
  - result: no findings
  - exit code: 0
- scoped encoding audit: strict UTF-8, no BOM, no U+FFFD, no trailing whitespace
- scope audit: no `.github/**`, Python or `SKILL.md` product diff
- user authority: project Owner replied “确认，继续” after reviewing the written V3 design
- trust level: user-approved design plus passed-agent-local static verification; not CI-backed

## Superseded Work

- `pdc-runtime-first-architecture-v2` is archived as a historical assessment.
- `pdc-runtime-p0-contract-baseline` was never implemented and is marked
  `SUPERSEDED — DO NOT EXECUTE`.
- No Runtime package, contract catalog, CLI, MCP tool, test or CI change was
  created from the cancelled plan.

## Residual Risk

- The architecture documents and lifecycle updates are still local working-tree changes; they have not been committed or pushed.
- PDC runtime behavior remains exactly the published v0.1.0 behavior plus other pre-existing local work; V3 is a governance decision, not a new runtime feature.
- No other Agent product or weaker model was tested, and V3 intentionally makes no compatibility claim for them.
- Future Guardrail candidates require a new failure-backed Change Brief and must pass all V3 promotion gates.

## Unrelated Working Tree

The following pre-existing user work remains outside this Flow and was not
modified or included in its verification claim:

- `project-agent-copilot/project-develop-copilot/references/session-digest-implementation-plan.zh.md`
- `project-agent-copilot/project-develop-copilot/internal-trial-guides/`

## Next Action

Decide whether to commit and push this architecture-only documentation set.
After integration, keep using the current PDC normally. Open a new Flow only
when a concrete failure satisfies the V3 Guardrail promotion criteria.

## Return Handoff

- stage_or_bridge_used: `project-finish`
- result_summary: V3 design approved and archived; V2/P0 preserved as superseded history
- changed_assumptions: unified Lifecycle Runtime is no longer the default or planned direction
- recommended_scope_changes: none
- artifacts: V3 design, Change Brief, historical V2/P0 markers, this handoff
- verification_notes: user-approved design; agent-local document and scope checks passed; no product tests needed because no product code changed
- lifecycle_updates_needed: none before commit/push decision
- next_gate: repository integration decision
