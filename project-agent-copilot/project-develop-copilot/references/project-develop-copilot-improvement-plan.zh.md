# Project Develop Copilot 改进计划

> 状态：Phase 0 已完成代理本地实现、whole-branch Important fixes 与修复后独立 re-review；Repository Integrity Gate 已归档
>
> 校准日期：2026-07-15
>
> 仓库基线：`3761b0f1379974a1798436ee6f3652dbe4679673`
>
> Lifecycle Flow：`pdc-phase0-repository-integrity`

## 目录

- [1. 目标](#1-目标)
- [2. 证据校准](#2-证据校准)
- [3. 问题分层](#3-问题分层)
- [4. Phase 0：Repository Integrity Gate](#4-phase-0repository-integrity-gate)
- [5. 文件范围](#5-文件范围)
- [6. 测试设计](#6-测试设计)
- [7. Acceptance Criteria](#7-acceptance-criteria)
- [8. 权威来源](#8-权威来源)
- [9. 后续路线](#9-后续路线)
- [10. 风险与控制](#10-风险与控制)
- [11. 下一 Gate](#11-下一-gate)

## 1. 目标

Project Develop Copilot 是面向 AI Coding Agent 的证据驱动项目生命周期 Harness。它提供：

- 受控的项目上下文；
- 可恢复的生命周期状态；
- 明确的修改范围；
- 有证据支持的完成声明；
- 防止陈旧 Wiki 污染实现决策的知识反腐规则。

下一阶段的重点不是继续增加概念或 Child Skill，而是让仓库自身的文本、状态声明、验收引用和自动检查先达到可重复、可验证的水平。

## 2. 证据校准

外部建议稿提供了有价值的方向，但以下判断必须按当前仓库事实重述。

### 2.1 中文编码问题：确认存在，范围扩大

真实 mojibake 不只存在于顶层 Router 和 `project-query`，还出现在 `project-session-extract` 与 `references/session-digest.md`；全目录字节扫描还确认 `references/change-brief.md` 带 UTF-8 BOM。修复范围应来自门禁输出，而不是只修建议稿列出的示例。

质量检查不得把 `杩`、`绔`、`瀹`、`鍙` 等合法 Unicode 单字直接列为失败模式。可靠检测应组合：

1. 严格 UTF-8 解码；
2. Unicode replacement character；
3. 已确认的多字符 mojibake 序列；
4. 异常密度提示只作为后续候选；Phase 0 在建立误报 Fixture 和阈值依据前不实现该 heuristic，未来实现也不得单独阻断 CI。

### 2.2 Acceptance 状态：问题重述

`references/acceptance-cases.md` 当前编号覆盖 Case 1–36，另有历史追加的 Case 9A、9B、9C，共 39 个标题定义；Completion Rule 位于 Case 12 与 Case 13 之间，文件并未在 Case 9A 中途结束。

当前真实问题是：

- Case 编号包含历史追加顺序，人工阅读容易误判；
- Completion Rule、Capability Gap、静态运行报告和 Eval 文档缺少统一的机器校验；
- Fixture、静态检查、Live Agent 与 Real Project 的证据等级仍需要进一步区分；
- Phase 1 才会引入机器可读 Acceptance Manifest，本阶段只保证现有引用闭合。

Phase 0 不重编号历史 Case/Eval，以免破坏历史运行报告链接。

### 2.3 Project Query 写边界：问题重述

`project-query` 普通查询模式默认只读。只有用户明确请求 Dashboard 更新时，才进入 `dashboard-refresh` 并修改限定的 Dashboard 投影文件。

因此后续问题是：

- `project-query:read` 与 Dashboard 写 Capability 是否应分离；
- 写模式是否具有独立 Trace 与授权；
- Dashboard 投影是否始终单向依赖 Flow Record 和 Artifact Evidence。

这属于后续架构收敛，不是 Phase 0 阻断项。

### 2.4 源码与安装版差异：确认需要回迁

当前已安装版本包含尚未进入源码基线的 LLM Wiki Discovery 修正：发现 `.llm-wiki/` 即表示 Wiki 存在，`index.md` 可以缺失或可选。

本轮需要把有效规则及其 Acceptance 文本回迁源码。该动作是一次性对账，CI 不得读取个人安装目录，也不得持久化工作站绝对路径。

## 3. 问题分层

| 编号 | 当前判断 | 本轮处理 |
|---|---|---|
| PDC-P0-01 中文 mojibake | confirmed | 修复并建立文本质量门禁 |
| PDC-P0-02 Acceptance 不可信 | reframed | 校验现有 ID、引用和事实声明；Manifest 延期 |
| PDC-P0-03 Runtime 证据不足 | confirmed | 记录为 Phase 1，不在本轮实现 Runner |
| PDC-P1 Router/Query/模式/状态问题 | confirmed or design-risk | 保持现状，后续分 Epic 设计 |
| PDC-P2 文档漂移 | partially confirmed | Phase 0 修复与当前范围直接相关的漂移 |
| PDC-P2 产品定位与版本治理 | confirmed | 保留路线，延期实施 |

## 4. Phase 0：Repository Integrity Gate

### 4.1 目标

让 Project Develop Copilot 源码仓库能确定性回答四个问题：

1. 纳管文本是否是合法 UTF-8？
2. 是否引入了已知 mojibake 或 replacement character？
3. Markdown 本地链接和关键 Case/Eval 引用是否闭合？
4. 文档状态声明是否与当前仓库事实一致？

### 4.2 方案选择

采用独立 Repository Integrity Gate，不把源码仓库检查塞入 `llm_wiki_doctor.py`。

原因：

- LLM Wiki Doctor 面向消费项目的 `.llm-wiki` 健康度；
- Repository Integrity 面向 Skill 源码、References、Evals 与 CI；
- 两者输入、失败语义和发布边界不同；
- 独立脚本更容易单测、复用和后续接入 Acceptance Manifest。

### 4.3 组件

#### `scripts/check_text_quality.py`

职责：

- 枚举纳管文本扩展名；
- 以严格 UTF-8 读取字节；
- 报告 replacement character；
- 匹配仓库中已经确认的多字符 mojibake 序列；
- 输出稳定排序的项目相对路径、行号和规则 ID；
- 发现阻断项时返回非零退出码。

边界：

- 不以单个合法中文字符作为失败条件；
- 不修改文件；
- 不扫描二进制和生成目录；
- Phase 0 不实现尚未校准的异常密度 heuristic；未来若加入，只报告且不单独使 CI 失败。

#### `scripts/check_doc_integrity.py`

职责：

- 校验 Markdown 本地相对链接；
- 校验 Completion Rule 与 Capability 文档引用的 Case/Eval 是否存在；
- 检测同一文档中的重复 Case/Eval ID；
- 输出稳定、可定位的诊断并返回明确退出码。

边界：

- 不重写 Markdown；
- 不要求自然数字连续；
- 不把外部 URL 的网络可用性变成阻断条件；
- 不在 Phase 0 引入 Manifest 或生成状态页。

#### Existing CI

沿用 `.github/workflows/project-develop-copilot-ci.yml`：

1. 运行完整 `scripts/tests`；
2. 运行文本质量检查；
3. 运行文档引用检查；
4. 保留 `sync-doctor.py --check`。

不新建第二份重叠工作流。

### 4.4 数据流

```text
tracked source files
    -> deterministic text scan
    -> deterministic reference scan
    -> sorted diagnostics
    -> exit 0 / exit 1
    -> existing GitHub Actions workflow
```

检查器只读取仓库内容，不访问已安装 Skill、本机全局配置或网络。

### 4.5 诊断格式

统一输出：

```text
<relative-path>:<line>: <rule-id>: <message>
```

规则至少包括：

- `invalid-utf8`
- `utf8-bom`
- `file-read-error`
- `unicode-replacement-character`
- `known-mojibake-sequence`
- `broken-local-link`
- `duplicate-case-id`
- `duplicate-eval-id`
- `missing-case-reference`
- `missing-eval-reference`
- `missing-definition-file`

### 4.6 错误处理

- 单文件读取失败：记录该文件诊断，继续检查其他文件，最终返回失败。
- 多个错误：全部排序输出，避免一次只修一个问题。
- 外部 URL：不联网验证，只检查 Markdown 语法与本地路径。
- 合法中文疑似异常：Phase 0 只运行确定性规则；异常密度 heuristic 延后到有误报 Fixture 和阈值依据时再作为 non-blocking 信息引入。
- 历史 Case 顺序：允许 append-only 和 9A/9B/9C 等 ID，只检查唯一性与引用闭合。

## 5. 文件范围

### Active

- 已确认包含 mojibake 的 Router、Child Skill 和 Reference 文件，以及扫描确认带 BOM 的 `references/change-brief.md`。
- `references/acceptance-cases.md`
- `references/capability-gap-audit.md`
- `evals/README.md` 与直接相关状态说明。
- 新增的两个检查器及其单元测试。
- `.github/workflows/project-develop-copilot-ci.yml`
- 本改进计划与对应 `.llm-wiki` 生命周期资产。

### Read-only

- 已安装 Project Develop Copilot，仅用于一次性差异核对。
- 现有 LLM Wiki Doctor 与 scaffold，用于回归测试。
- 历史 Eval Run Reports，不回写历史结论。

### Excluded

- 其他 Agent Copilot 模块和 HR SCP 改动。
- 仓库内正式 Runtime Harness、Agent Tool Trace Schema 和自动 Eval Runner。
- Project Graph、Dashboard 和状态存储重构。
- 版本发布、提交、推送和 PR。

## 6. 测试设计

### Text Quality

- 非 UTF-8 字节 Fixture 必须失败。
- replacement character Fixture 必须失败。
- 当前已知 mojibake 序列 Fixture 必须失败。
- 正常简体中文、繁体中文和包含 `杩`、`绔`、`瀹`、`鍙` 单字的 Fixture 必须通过。
- 多个文件错误必须全部报告且顺序稳定。

### Document Integrity

- 正常相对链接通过。
- reference-style usage/definition 的本地目标缺失时失败。
- 含平衡括号与 angle brackets 的合法 inline destination 通过。
- 缺失本地文件失败。
- 外部 URL 不触发网络访问。
- 重复 Case/Eval ID 失败。
- Completion Rule 引用缺失 ID 失败。
- Case 9A/9B/9C 和 append-only 编号合法。

### Regression

- 完整 `python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests` 通过。
- `sync-doctor.py --check` 通过。
- `git diff --check` 通过。
- 修改文件严格 UTF-8 无 BOM 读取通过。

### Skill Behavior Evaluation

实现前保存当前 Skill 快照作为旧版基线。实现后至少对照运行三类真实提示词：

1. 正常中文 Lifecycle Quality 请求应进入正确 Route，且不依赖乱码短语。
2. 正常中文项目 Wiki 查询应进入 `project-query`，普通查询保持零写入。
3. 项目存在 `.llm-wiki/` 但没有 `.llm-wiki/index.md` 时，Router 仍识别 Wiki，并从可用入口恢复上下文。

使用 `skill-creator` 的临时 sibling workspace 保存旧版与新版输出、断言和 Review Viewer。该工作区不提交到仓库，也不等同于 Phase 1 的自动 Lifecycle Eval Runner。

## 7. Acceptance Criteria

- 仓库中已确认的 mojibake 清零。
- 新增同类 mojibake、非法 UTF-8 或 replacement character 时 CI 失败。
- 正常中文不被固定单字词表误报。
- 本地 Markdown 链接与关键 Case/Eval 引用闭合。
- 当前编号 1–36 加 9A/9B/9C 的 39 个 Acceptance 定义全部保留且可被检查器识别。
- LLM Wiki Discovery 修正进入源码并有文本验收保护。
- Capability Gap 不再声称 Acceptance 文件在 Case 9A 截断。
- 普通 Project Query 与显式 Dashboard Refresh 的边界被准确描述。
- 现有 47 个 Doctor 测试和 scaffold drift 检查无回归。
- 三类 Skill 行为对照案例通过用户审阅，且新版不弱于旧版基线。

## 8. 权威来源

为避免“目标”和“观测状态”混为一谈，分为两类：

### Normative Authority

1. 当前用户/维护者明确决定；
2. `north-star.md`；
3. 当前架构、Gate、Brief 与协议 References；
4. 本改进计划中已批准的阶段设计。

### Observed Status Authority

1. 当前源码、测试、CI 和 Git Diff；
2. 后续机器可读 Eval/Manifest 结果；
3. Flow Record 与 Artifact Evidence；
4. Capability/Dashboard 等生成或人工摘要；
5. 历史运行报告。

规范目标不能证明运行成功；运行结果也不能自行改写产品 North Star。

## 9. 后续路线

### Phase 1：Minimum Lifecycle Eval

- Trace Schema；
- Read-only Query、Resume、State-changing Task 三个核心场景；
- Route、Writes、Duplicate Flow、Scope、Gate Evidence 和 Done Claim 断言；
- Fixture 结果与 Live Agent/Real Project 状态分层。

### Phase 2：降低使用成本

- Quick / Standard / Strict；
- Risk Scoring 与不可静默降级规则；
- Route Registry；
- Dashboard 写 Capability 解耦。

### Phase 3：状态与兼容治理

- Harness Manifest；
- Protocol / State Schema Version；
- Capability Negotiation；
- 结构化 Flow、Artifact 和 Verification Evidence；
- 迁移与只读版本检查。

### Phase 4：公开证明

- 脱敏真实案例；
- Baseline 对比与可解释指标；
- CI 重放；
- Eval Contribution Workflow。

## 10. 风险与控制

- **误报风险**：阻断规则只使用严格解码、replacement character 和已确认多字符序列。
- **范围膨胀**：Manifest、Runner、模式和状态重构全部延期。
- **双事实源**：外部草稿只保留摘要；校准后的仓库内计划是本阶段设计来源。
- **安装版覆盖源码**：只移植经差异核对确认的规则，不做整目录覆盖。
- **历史证据破坏**：不重编号历史 Case/Eval，不重写历史 Run Report。
- **职责污染**：Repository Integrity 与 LLM Wiki Doctor 保持独立。
- **静态检查代替行为证明**：对 Trigger 与 Discovery 修正保留旧版/新版提示词对照，但不提前建设正式 Runner。

## 11. 下一 Gate

与 `pdc-phase0-repository-integrity` 关联的详细实施计划已在 `.llm-wiki/working-context/pdc-phase0-repository-integrity.md` 执行。Tasks 1–7 均完成逐任务独立复核；初次 whole-branch review 的三个 Important finding 已修复。Fresh verification 通过 7 个文本测试、12 个文档测试、66 个全量测试（19 focused）、两项 repository checker、scaffold sync、CI static contract、四项 Skill validation，以及 tracked+untracked union 的严格编码与可执行隐私审计。用户/项目 owner 已对三组新旧行为对照回复 `通过`。

修复后的独立 whole-branch re-review 结论为 Critical 0、Important 0、`Ready to merge: Yes`；Review & Wiki Integrity Gate 已完成，`archive` 为 done。当前证据等级为 `passed-agent-local`、非代理行为接受并有 reviewer-backed re-review，但仍不是 CI-backed confidence。没有可用 token telemetry；Skill Creator 的 token 字段只是输出字符数 proxy，不得用于 token-efficiency 结论。下一 Gate 是用户决定如何处理当前未提交分支；除非另行授权，不执行提交、暂存、推送、PR、发布、合并或分支清理。
