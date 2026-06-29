# LLM Wiki Doctor Skill 设计

## 背景

`project-develop-copilot` 已经具备项目 `.llm-wiki` 初始化、维护、Project Graph、finish/review 同步等能力，但当前存在两个明显缺口：

- `project-init` 可以把目录结构建完整，但很多页面可能仍是空壳 README，无法支撑真实查询、开发决策或跨项目排查。
- `llm_wiki_doctor.py` 已经能做局部 validator，但缺少自然语言 skill 入口、中文综合报告、成熟度评分和下一步引导。

本设计新增一个可触发的 `llm-wiki-doctor` child skill，并增强 doctor 脚本，让它同时承担两类职责：

- 保留原有 Project Graph / wiki hygiene validator，服务 pre-commit、CI、project-finish 等强约束场景。
- 新增 `.llm-wiki` 成熟度评分和中文报告，帮助用户判断当前 wiki 是否只是空壳、离可用还差什么、下一步该补哪里。

## 目标

完成后，用户可以自然语言触发：

```text
跑一下 LLM Wiki Doctor
检查这个项目的 .llm-wiki 状态
给这个 llm-wiki 打分
project init 后看看 wiki 有没有用
检查 Project Graph evidence
CI 里 llm_wiki_doctor 报错，帮我修
```

期望输出是中文为主的综合报告：

```text
LLM Wiki Doctor 报告
分数：32/100
等级：空壳 wiki
关键结论：目录存在，但模块、来源、需求和 Project Graph 事实不足。
Validator 发现：missing-graph-evidence、orphan-design-doc ...
建议行动计划：1-10 步，把 wiki 从 30 分提升到 70 分以上。
```

## 不做范围

本阶段不做：

- 不替代 `project-maintain` 的全部维护职责。
- 不自动编造模块职责、接口说明、需求背景或跨项目关系。
- 不默认写入 `.llm-wiki`。
- 不把判断性 `missing-graph-evidence` 升级为默认 FAIL。
- 不移除 pre-commit / CI / project-finish 的脚本入口。

## 方案

采用“独立 child skill + 脚本增强”的方案。

### 新增 child skill

新增目录：

```text
project-agent-copilot/project-develop-copilot/llm-wiki-doctor/SKILL.md
```

该 skill 负责：

- 识别自然语言 doctor 请求。
- 定位项目根目录和 `.llm-wiki`。
- 优先运行项目 vendored 脚本 `.llm-wiki/tools/llm_wiki_doctor.py`。
- 如果项目未 vendoring，则回退运行安装包脚本 `scripts/llm_wiki_doctor.py`。
- 解释 text/json 输出。
- 根据报告引导用户进入 `project-ingest`、`project-maintain`、`project-graph-candidates-scan`、`project-develop` 或 `project-finish`。

### Router 更新

`project-develop-copilot/SKILL.md` 增加路由：

| 情况 | Mode | Primary stage |
|---|---|---|
| 用户要求 LLM Wiki Doctor、wiki 打分、成熟度评分、检查 init 后 wiki 是否有用、解释 doctor/pre-commit/CI 结果 | wiki-doctor | `llm-wiki-doctor` |

Tie-breaker 中，`llm-wiki-doctor` 位于 `project-query` 之后、`project-maintain` 之前：

```text
lightweight-answer < read-only-query < wiki-doctor < wiki-maintenance < full-lifecycle
```

理由：doctor 默认只读，但比普通查询更像结构性诊断；只有用户确认修复后才转入维护或 ingest。

## Doctor 脚本增强

脚本仍位于：

```text
scripts/llm_wiki_doctor.py
```

### 保留原有 validator

必须保留并继续输出：

- `orphan-design-doc`
- `missing-graph-evidence`
- `unresolved-project-id`
- `invalid-edge-id`

这些规则仍服务于 pre-commit、CI 和 project-finish，不因新增 maturity score 而弱化。

### 新增 Project Graph 结构检查

在现有能力基础上，逐步扩展以下检查：

- Project Graph 基础文件是否存在：`edges.md`、`candidates.md`、`proposals.md`、`scan-report.md`、`cross-refs/index.md`。
- `cross-refs/index.md` 是否存在 dangling `edge_id`。
- confirmed edge 是否存在重复 fingerprint。
- committed 文件是否泄露 `registry.local.json` 或本机绝对路径。
- edge `from_project` / `to_project` 是否为已知 logical project id。

第一版可以先把这些纳入 maturity 评分和 WARN，不急于全部作为 CI FAIL。

### 新增 maturity score

新增评分模型，总分 100，默认输出中文 text 报告，json 保留结构化字段。

建议权重：

| 维度 | 分值 | 判断 |
|---|---:|---|
| 基础结构 | 15 | `.llm-wiki`、README、log、modules、sources、requirements、bugs、working-context、artifacts 是否存在 |
| 入口可读性 | 10 | README/index 是否不是空模板，是否能说明项目用途和导航入口 |
| 模块上下文 | 20 | `modules/index.md` 和各模块 README/source-map/architecture/rules/verification 的覆盖度与非空程度 |
| 来源登记 | 10 | `sources/`、`ingest/index.md`、`original_path` 是否登记真实资料 |
| 生命周期内容 | 15 | requirements、bugs、working-context、handoff、log 是否有真实条目和可追溯关系 |
| artifacts/dashboard 可见链路 | 10 | `artifacts/index.md`、dashboard、log、模块 README 是否能形成发现链 |
| Project Graph / cross-refs | 15 | graph 文件、edges/candidates/proposals、Project Graph Evidence / Gaps、cross-ref pins 是否可用 |
| Validator 健康度 | 5 | 根据 ERROR/WARN 扣分，保留原 validator 发现 |

等级建议：

| 分数 | 等级 | 含义 |
|---:|---|---|
| 0-30 | 空壳 wiki | 目录存在或部分存在，但缺少事实内容 |
| 31-60 | 初始可读 | 有一些入口和模块信息，但难以支撑稳定开发 |
| 61-80 | 可辅助查询 | 能帮助回答项目问题，仍有明显补齐项 |
| 81-100 | 生命周期可用 | 可支撑需求、bug、Project Graph、finish/review 流程 |

### 空模板识别

Doctor 需要识别“文件存在但几乎没用”的情况。第一版使用轻量启发式：

- 正文有效字符数过少。
- 只有标题、目录、占位词、空表格。
- 出现 `TODO`、`TBD`、`待补充`、`placeholder`、`coming soon` 等占位信号。
- 模块页缺少源码入口、职责、关键类/API、验证方式之一。

这些结果默认作为 maturity gap，不作为 validator ERROR。

## 中文报告模板

默认 text 输出中文为主，技术字段保持英文。

```markdown
# LLM Wiki Doctor 报告

## 总体评分

- 分数：32/100
- 等级：空壳 wiki
- 判断：目录结构已经建立，但缺少可支撑查询和开发决策的事实内容。

## 关键结论

1. `.llm-wiki` 基础目录存在，但多个入口页仍接近空模板。
2. `modules` 有目录，但模块职责、源码入口、验证方式不足。
3. `sources/ingest` 缺少真实资料登记。
4. Project Graph 基础结构存在，但 evidence / edge / candidate 不足。

## Validator 发现

### Errors

- 暂无

### Warnings

- `missing-graph-evidence`: ...
- `orphan-design-doc`: ...

## 成熟度缺口

| 维度 | 得分 | 问题 |
|---|---:|---|
| 基础结构 | 12/15 | 目录基本完整 |
| 模块上下文 | 4/20 | README 多为空壳 |
| 来源登记 | 0/10 | 没有登记真实资料 |
| Project Graph | 2/15 | 有目录但缺少有效边或证据 |

## 建议行动计划

1. 完善 `.llm-wiki/README.md`，写清项目用途和入口。
2. 完善 `modules/index.md`，列出模块职责和优先级。
3. 按核心模块补齐 `README/source-map/architecture/rules/verification`。
4. 把已有设计、需求、接口文档登记到 `sources` 或 `ingest`。
5. 为当前活跃需求建立 `requirements/*.md`。
6. 为已知跨服务调用补 Project Graph Evidence / Gaps。
7. 扫描 Project Graph candidates。
8. 把关键产物登记到 `artifacts/index.md`。
9. 更新 `log.md`，记录初始化和补全过程。
10. 再次运行 Doctor，目标提升到 70 分以上。
```

## 修复边界

默认只读。

用户明确要求“修复 / 补齐 / 继续完善”后，允许转入受控修复：

- 低风险自动补齐：空模板、缺少索引入口、缺少 graph 空文件、缺少 log 维护记录、缺少 artifacts/dashboard 可见入口。
- 需要证据后补齐：模块职责、source-map、architecture、rules、verification、Project Graph edges/candidates。
- 需要用户确认：业务需求、验收标准、跨项目关系事实、runtime-verified/source-verified 状态。

不得自动编造：

- 模块职责。
- API 契约。
- Project Graph confirmed edge。
- 需求范围和验收标准。
- bug 结论。

## 文档与安装面更新

需要同步更新：

- 根 `README.md` / `README.zh.md`
- `project-agent-copilot/README.md` / `README.zh.md`
- `project-develop-copilot/README.md` / `README.zh.md`
- `scripts/README.llm-wiki-doctor.md`
- `evals/project-develop-copilot-evals.md`
- `references/acceptance-cases.md` 如有对应编号策略

## 验收标准

第一版完成后应满足：

1. `npx skills add . --list` 能识别新增 `llm-wiki-doctor` skill。
2. 用户说“跑一下 LLM Wiki Doctor”时，router 能路由到 `llm-wiki-doctor`。
3. 脚本能输出中文 text 报告，包含分数、等级、validator 发现、成熟度缺口和建议行动计划。
4. json 输出包含 score、level、dimensions、findings、gaps、next_steps，便于 CI 或 dashboard 复用。
5. 现有 validator 测试继续通过。
6. 新增测试覆盖空壳 wiki、模块空 README、缺少 sources、Project Graph 只有空结构等场景。
7. README 中英文版说明安装后自带 skill 触发和 doctor 脚本能力。
8. 不触碰无关未跟踪目录，例如 `internal-trial-guides/`。

## 自检

- 无 TBD/TODO 占位。
- 设计同时保留旧 validator 和新增 maturity score，没有互相替代。
- 中文报告模板是默认 text 输出，不影响 json 结构化消费。
- 默认只读，修复行为必须经过用户确认。
- Project Graph 功能仍是 Doctor 的核心组成部分。