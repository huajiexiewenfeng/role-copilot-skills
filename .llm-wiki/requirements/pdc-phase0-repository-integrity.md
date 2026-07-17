# Change Brief: pdc-phase0-repository-integrity

## Summary

- title: Project Develop Copilot Phase 0 Repository Integrity Gate
- status: ready
- flow_id: `pdc-phase0-repository-integrity`
- original_path: `project-agent-copilot/project-develop-copilot/references/project-develop-copilot-improvement-plan.zh.md`

## Sources

- [`20260715-001-001`](../sources/proxies/20260715-001/001-project-develop-copilot-problems-and-improvements.md)
- [`project-develop-copilot-improvement-plan.zh.md`](../../project-agent-copilot/project-develop-copilot/references/project-develop-copilot-improvement-plan.zh.md)
- 当前源码、测试和 `3761b0f` 基线证据。

## Scope

- active:
  - 修复 `project-agent-copilot/project-develop-copilot` 内已确认的中文 mojibake，并移除扫描确认的 UTF-8 BOM。
  - 将已安装版本中有效的 LLM Wiki Discovery 修正回迁源码，并补齐对应 Acceptance 证据。
  - 新增独立的文本质量与文档引用检查器、单元测试和现有 CI 步骤。
  - 校准 Acceptance、Capability Gap 与改进计划中的事实声明。
- reference-only:
  - 当前本机已安装版本，仅用于一次性差异核对；不得把本机路径写入项目文档或 CI。
  - 外部改进建议稿，只通过 wiki-local source proxy 使用。
  - 现有 LLM Wiki Doctor 实现，用于保持职责边界和回归验证。
- excluded:
  - HR SCP 与其他 Agent Copilot 模块。
  - 仓库内 Acceptance Manifest、正式 Lifecycle Eval Runner，以及公开或真实项目 Benchmark；本阶段只保留仓库外的三用例临时对照证据。
  - Quick / Standard / Strict、Route Registry、Dashboard Skill 拆分。
  - 结构化状态、协议版本、Schema Migration 和公开真实项目案例。
  - 未经误报 Fixture 校准的异常字符密度 heuristic；若后续加入，只能作为 non-blocking 提示。

## Acceptance

- 纳管文本均可按严格 UTF-8 无 BOM 读取，且不含已确认的 mojibake 序列或 Unicode replacement character。
- 合法中文单字 Fixture 不误报，损坏编码与真实 mojibake Fixture 必须失败。
- 单文件读取失败产生稳定诊断，检查继续处理其余文件并最终失败。
- Markdown 本地链接、Case/Eval 引用和被 Completion Rule 引用的 ID 可解析且无重复；Acceptance 编号 1–36 加 9A/9B/9C 共 39 个定义均保留。
- 安装版中有效的 LLM Wiki Discovery 修正进入源码，并由 Acceptance/Eval 文本保护。
- `project-develop-copilot-ci.yml` 执行新增检查和测试。
- 现有 47 个 Doctor 单元测试和 scaffold drift 检查继续通过。
- 中文 Lifecycle Quality、中文 Project Query 和无 `index.md` Wiki Discovery 三类新版/旧版行为对照完成用户审阅。
- Phase 0 文档不再声称 Acceptance 文件在 Case 9A 截断，也不再把显式 Dashboard Refresh 描述成普通 Query 默认写入。

## Plan

- active_plan: [`../working-context/pdc-phase0-repository-integrity.md`](../working-context/pdc-phase0-repository-integrity.md)
- status: confirmed
- evidence: 用户批准 Phase 0 设计与实施；Tasks 1–7 已完成逐任务独立复核，Task 8 及 whole-branch Important fixes 已完成代理本地 Verification Gate；修复后的独立全分支 re-review 为 Critical 0、Important 0、`Ready to merge: Yes`。

## Verification Plan

- 对检查器先写失败 Fixture，再实现最小通过逻辑。
- 运行新增单元测试、完整 `scripts/tests` 测试发现和 `sync-doctor.py --check`。
- 对修复后的仓库运行文本质量与文档引用检查器。
- 检查 `git diff --check HEAD --`，并将 tracked diff 与 `git ls-files --others --exclude-standard` 合并后独立验证严格 UTF-8、无 BOM、无 U+FFFD 和尾随空白。

## External Dependencies

- none

## Routing

- intent: 改进现有 Project Develop Copilot，第一批锁定 Phase 0 仓库自一致性。
- primary_stage: `project-develop`
- secondary_bridges: `brainstorming`, `skill-creator`, `project-ingest`, `writing-plans`
- confidence: high
- reason: 用户明确选择并批准 Repository Integrity Gate 设计。
- next_gate: 用户决定如何处理当前未提交分支；除非另行授权，不提交、暂存、推送、创建 PR、发布、合并或清理分支。
- routed_at: 2026-07-15

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | `../sources/proxies/20260715-001/001-project-develop-copilot-problems-and-improvements.md` | 2026-07-15 |
| design | done | `../../project-agent-copilot/project-develop-copilot/references/project-develop-copilot-improvement-plan.zh.md` | 2026-07-15 |
| plan | done | `../working-context/pdc-phase0-repository-integrity.md`（confirmed） | 2026-07-15 |
| development | done | Tasks 1–7 实施报告、下方 24 文件最终 Git union 与 `../handoff/pdc-phase0-repository-integrity-handoff.md` | 2026-07-15 |
| testing | done | agent-local：7/12/66 tests（19 focused）、两项 checker、sync-doctor、diff check、CI static contract、四项 Skill validation、修订后的编码/隐私审计；用户接受 Task 7 行为复核 | 2026-07-15 |
| archive | done | 修复后 whole-branch re-review：Critical 0、Important 0、`Ready to merge: Yes`；最终 Wiki Integrity Gate 通过 | 2026-07-15 |

## Implementation Evidence

Task 8 生命周期同步后的 tracked diff 与 untracked 文件精确 union 共 24 个：

- `.github/workflows/project-develop-copilot-ci.yml`
- `.llm-wiki/handoff/pdc-phase0-repository-integrity-handoff.md`
- `.llm-wiki/index.md`
- `.llm-wiki/ingest/index.md`
- `.llm-wiki/log.md`
- `.llm-wiki/requirements/pdc-phase0-repository-integrity.md`
- `.llm-wiki/sources/proxies/20260715-001/001-project-develop-copilot-problems-and-improvements.md`
- `.llm-wiki/working-context/pdc-phase0-repository-integrity.md`
- `project-agent-copilot/project-develop-copilot/SKILL.md`
- `project-agent-copilot/project-develop-copilot/evals/README.md`
- `project-agent-copilot/project-develop-copilot/evals/project-develop-copilot-evals.md`
- `project-agent-copilot/project-develop-copilot/project-develop/SKILL.md`
- `project-agent-copilot/project-develop-copilot/project-query/SKILL.md`
- `project-agent-copilot/project-develop-copilot/project-session-extract/SKILL.md`
- `project-agent-copilot/project-develop-copilot/references/acceptance-cases.md`
- `project-agent-copilot/project-develop-copilot/references/capability-gap-audit.md`
- `project-agent-copilot/project-develop-copilot/references/case11-project-query-run-2026-06-04.md`
- `project-agent-copilot/project-develop-copilot/references/change-brief.md`
- `project-agent-copilot/project-develop-copilot/references/project-develop-copilot-improvement-plan.zh.md`
- `project-agent-copilot/project-develop-copilot/references/session-digest.md`
- `project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py`
- `project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py`
- `project-agent-copilot/project-develop-copilot/scripts/tests/test_check_doc_integrity.py`
- `project-agent-copilot/project-develop-copilot/scripts/tests/test_check_text_quality.py`

Task 8 首次 whole-file audit 发现 `references/change-brief.md` 的 4 个 baseline 空列表占位带尾随空格；已用窄补丁将 `- ` 改为 `-`，语义不变，最终审计无 findings。

初次 Task 8 scope 结论来自编码检查加人工文件列表复核，并未机器化拒绝 durable Wiki 中的任意工作站绝对路径。Whole-branch review 暴露该缺口后，Step 4 audit 增加 drive-letter 与 POSIX user-home path 规则；临时 durable-wiki fixture 与旧 handoff 路径先产生预期 RED，portable handoff 修复后 exact 24-file union 转为 GREEN。

## Verification Evidence

- executor: agent-local
- focused tests: text 7/7，document 12/12，共 19 focused tests，退出码均为 0；两个新增 Markdown parser 测试均保留 RED/GREEN 证据。
- full tests: 66/66，退出码 0；包含既有 47 个 Doctor 测试。
- repository gates: `text quality: no findings`；`document integrity: no findings`；`sync-doctor.py --check` 退出码 0；`git diff --check HEAD --` 退出码 0。
- Skill validation: 使用已安装 Skill Creator 的同一个 `quick_validate.py` 校验 Router、`project-query`、`project-develop`、`project-session-extract`，四项均返回 `Skill is valid!`、退出码 0。
- changed-file audit: 最终 24 文件 union 严格 UTF-8、无 BOM、无 U+FFFD、无尾随空白，退出码 0。
- privacy/scope audit: durable `.llm-wiki` 文本无 drive-letter 或 POSIX user-home path；没有安装版路径、用户名、secret、临时 Eval Workspace 文件、Manifest、永久 Runner、mode、Registry、Dashboard、state/schema/version-governance 文件进入 Git union，退出码 0。
- behavior review: Tasks 1–7 有逐任务独立代理复核；Task 7 三组新旧对照均为 3/3，用户/项目 owner 回复 `通过`，构成非代理行为复核接受。
- accepted limitation: 没有 token telemetry；Skill Creator token 字段只是输出字符数 proxy，不得据此声称 token efficiency。用户同时接受 Eval 2 的响应长度取舍。
- trust level: `passed-agent-local` 加用户行为接受，并有独立 whole-branch reviewer 结论；不是 CI-backed confidence。
- residual risk: GitHub 托管 CI 尚未在本分支运行；collapsed 与 shortcut reference 当前实现经 reviewer 纯解析检查通过，但没有各自独立单元测试。两项均不阻断本 Flow 归档。

## Non-Goals

- 本阶段不实现 Runtime Harness 或自动 Agent 执行器。
- 本阶段不把临时 Skill 行为评测工作区或 Review Viewer 提交进仓库。
- 本阶段不重编号历史 Acceptance Case/Eval。
- 本阶段不让源码质量检查依赖某台工作站的已安装 Skill 目录。
- 本阶段不把仓库质量检查并入面向消费项目的 LLM Wiki Doctor。

## Open Questions

- none

## Notes

- 工作基线：`3761b0f1379974a1798436ee6f3652dbe4679673`。
- 设计资产在独立分支 `feat/pdc-phase0-repository-integrity` 中编写。
- Phase 0 Skill、检查器、测试与 CI 修改已在工作树实现并通过代理本地验证；没有创建提交或推送。
- 详细实施计划位于 `.llm-wiki/working-context/pdc-phase0-repository-integrity.md`；验证与续接摘要位于 `.llm-wiki/handoff/pdc-phase0-repository-integrity-handoff.md`。
- 独立计划审阅的阻断项和 Tasks 1–7 的逐任务复核结论已回写；初次全分支 review 的三个 Important finding 已修复，修复后 re-review 为 Critical 0、Important 0、`Ready to merge: Yes`。当前工作树仍未提交，下一步由用户决定集成方式。
