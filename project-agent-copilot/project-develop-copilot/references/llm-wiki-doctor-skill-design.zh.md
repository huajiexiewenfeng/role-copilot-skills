# LLM Wiki Doctor Skill 设计

## 背景

`project-develop-copilot` 已经具备项目 `.llm-wiki` 初始化、维护、Project Graph、finish/review 同步等能力，但当前存在两个明显缺口：

- `project-init` 可以把目录结构建完整，但很多页面可能仍是空壳 README，无法支撑真实查询、开发决策或跨项目排查。
- `llm_wiki_doctor.py` 已经能做局部 validator，但缺少自然语言 skill 入口、中文综合报告、成熟度评分和下一步引导。

本设计新增一个可触发的 `llm-wiki-doctor` child skill，并增强 doctor 脚本，让它承担两类职责，但在代码路径上保持隔离：

- 确定性 validator：服务 pre-commit、CI、project-finish 等强约束场景，必须可复现。
- 成熟度评分与中文报告：服务用户和 skill 触发的诊断场景，必须说明依据、避免灌水、默认不阻断。

核心原则：确定性的归脚本，判断性的归 skill；评分锚定可验证信号，不奖励灌水；简单项目不因没有跨项目关系被误扣分；Doctor 自动修复只补结构，不编造语义内容。

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
关键结论：目录存在，但模块、来源、需求和 Project Graph 事实不足。
建议行动计划：1-N 步，逐项关闭下方列出的成熟度 gap；完成后重跑 Doctor 复核。
分数：32/100
等级：空壳 wiki
Validator 发现：missing-graph-evidence、orphan-design-doc ...
```

分数是方向性指南，不是 KPI。不要为提分而向页面填充内容；填充无验证依据的内容不会增加成熟度，必要时还会被占位、缺少锚点或 Project Graph evidence 检查反向扣分。

## 不做范围

本阶段不做：

- 不替代 `project-maintain` 的全部维护职责。
- 不自动编造模块职责、接口说明、需求背景或跨项目关系。
- 不默认写入 `.llm-wiki`。
- 不把判断性 `missing-graph-evidence` 升级为默认 FAIL。
- 不移除 pre-commit / CI / project-finish 的脚本入口。
- 不引入未定义的 `proposals.md` 检查；除非先在 `references/project-graph.md` 定义 proposal schema、职责和晋升流程。

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
- 默认运行 `report`，在 CI/pre-commit/project-finish 问题定位时运行 `validate`。
- 解释 text/json 输出，把脚本 signals 翻译成中文结论、成熟度缺口和行动计划。
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

第一版采用 Python 脚本子命令形态：

```text
python scripts/llm_wiki_doctor.py validate --root . --changed --format text --fail-on error
python scripts/llm_wiki_doctor.py score --root . --format json
python scripts/llm_wiki_doctor.py report --root . --format text
```

后续如果需要独立 CLI，可以再包装成：

```text
llm-wiki doctor validate
llm-wiki doctor score
llm-wiki doctor report
```

### 子命令隔离

必须拆成三个执行路径：

| 子命令 | 职责 | 阻断策略 |
|---|---|---|
| `validate` | 只运行确定性 validator | `--fail-on error` 只对 validate 的 ERROR 生效 |
| `score` | 只输出成熟度 signals、维度分和建议线索 | 永不影响退出码 |
| `report` | 合并 validate + score，输出中文综合报告 | 默认人触发使用；score 不影响退出码 |

约束：

- `validate` 的代码不得 import 或调用评分启发式。
- pre-commit、CI、project-finish 只跑 `validate`。
- `score` 永远不进入阻断路径。
- json 可以合并字段，但 `score` 字段缺失不得让 `validate` 失败。
- `score_version` 必须出现在 score/report json 中；跨版本对比分数前先确认版本一致。

### Canonical 检查名

全文档和实现统一使用以下检查名：

| 检查名 | 含义 | severity | 进 validate |
|---|---|---|---|
| `leaked-local-path` | 入库文件出现本机绝对路径、`registry.local.json` 或 local-only registry 内容 | ERROR | 是 |
| `invalid-edge-id` | Evidence 或普通 wiki 文档引用的 edge_id 在 `edges.md` 中不存在 | ERROR | 是 |
| `dangling-cross-ref` | `cross-refs/index.md` 的 pin 指向不存在的 edge | ERROR | 是 |
| `duplicate-edge-fingerprint` | confirmed edge fingerprint 重复 | ERROR | 是 |
| `orphan-design-doc` | 外部 design/requirement/bug/plan 文档未登记到 `.llm-wiki` source/original_path | WARN | 是 |
| `missing-graph-evidence` | 涉及跨项目推理的 wiki 文档缺少 Project Graph Evidence / Gaps | WARN | 是 |
| `unresolved-project-id` | 文档引用了 registry 不可解析的 project-id 或 alias | WARN | 是 |

规则：

- ERROR 类检查必须确定、可机械判定、无歧义；CI / pre-commit / project-finish 的 `--fail-on error` 阻断这些。
- WARN 类检查依赖散文语义识别或项目登记时序，存在 alias、指代或误报；永不默认升 ERROR。
- severity 是检查的固有属性，写在检查定义里，不由调用方临时指定。
- 这些规则仍服务于 pre-commit、CI 和 project-finish，不因新增 maturity score 而弱化。

### Project Graph 结构检查

第一版检查三层模型：

```text
project-graph/candidates.md
project-graph/edges.md
project-graph/scan-report.md
cross-refs/index.md
```

不检查 `proposals.md`，除非先在 `references/project-graph.md` 定义其 schema、职责、与 candidates/edges 的关系和晋升流程。

第一版至少覆盖：

- 基础 graph 文件是否存在。
- `cross-refs/index.md` 是否存在 dangling `edge_id`。
- confirmed edge 是否存在重复 fingerprint。
- committed 文件是否泄露 `registry.local.json` 或本机绝对路径。
- edge `from_project` / `to_project` 是否为已知 logical project id。

这些检查中，确定性错误进入 `validate`；结构缺口可以同时作为 `score` 的 signals。

### 词表来源

`unresolved-project-id` 和 project-id / alias 解析必须只使用入库、CI 可读的词表来源。

词表来源按优先级合并：

1. `<repo>/.llm-wiki/project-ids.json`：committed，CI 可读，第一版权威源。
2. Base Graph `project-catalog.md`：仅当当前环境可解析 Base Graph 时作为补充。

禁止从 `registry.local.json` 取词表用于 `validate`。`registry.local.json` 是 gitignored 的本机路径配置，CI 上可能不存在，会导致本地和 CI 判定不一致。

`edges.md` 的 `from_project` / `to_project` 只用于 edge 是否解析和 Project Graph 结构校验，不作为 `unresolved-project-id` 的词表来源。否则刚引入一个新服务但还没登记词表时，所有新关系都会被误当成权威词表。

`unresolved-project-id` 必须保持 WARN：它提醒补登记，不阻断提交。

## 成熟度评分

### 分工

脚本层只产出客观可测 signals，skill 层负责语义解释和行动计划。

脚本层 signals：

- 文件/目录是否存在。
- 有效正文字符数，去除标题、空表格和占位词后统计。
- 占位信号命中数，例如 `TODO`、`TBD`、`待补充`、`placeholder`、`coming soon`。
- 覆盖率比值，例如 `modules/index.md` 列出的模块中，有非空 README/source-map 的比例。
- 可验证锚点命中，例如 source-map 指向的文件是否真实存在、edge_id 是否可解析。
- validator findings 计数。

Skill 层判断：

- 读取脚本 signals，对入口可读性、模块职责充分度、生命周期可用性等语义维度给判断分。
- 生成中文报告、关键结论、成熟度缺口和行动计划。
- 每个维度都要标注来源：`脚本测量` 或 `LLM 判断`。
- LLM 判断必须引用 signals，不得凭空打分。

### 评分原则

1. 优先用可验证信号，而不是散文长度。
2. 字符数只作辅助、低权重，只用于疑似空壳提示，不直接加分。
3. 正文增长但可验证锚点未增加时，成熟度不升。
4. 缺少证据的跨项目内容不加分，必要时通过 validator 或占位识别扣分。
5. 分数在报告中服务于 gap 和行动计划，不作为主标题或唯一目标。`行动计划` 以关闭具体 gap 为成功判据，不以达到某个分数为目标。

### 计分去重

同一个底层事实在成熟度总分中只能被计一次。

- 每个 signal 应带 `fact_id` 或等价标识，表示它对应的底层事实。
- 结构缺口如果已经在某个维度中扣分，不再在 `Validator 健康度` 中二次扣分。
- `Validator 健康度` 只反映 validate findings 的整体风险数量级，不重复惩罚已经被基础结构、Project Graph 或来源登记维度吸收的同一事实。
- 实现上先按 `fact_id` 聚合，再决定它影响哪个维度。

### 维度与权重

每个维度支持 `applicable` / `not-applicable`。总分按适用维度重归一：

```text
总分 = 已得分 / 适用维度满分 * 100
```

Project Graph / cross-refs 在以下条件下可标记为 not-applicable：

- registry 中除当前项目外没有其它项目；并且
- 代码和 wiki 中没有跨服务、跨项目、Feign、MQTT、HTTP/RPC、shared config、event bus 等信号。

等级反映“对该项目的适配度”，不是绝对体量。一个完整的单模块 wiki 可以拿到“生命周期可用”，即使它没有任何 Project Graph edge。

建议权重：

| 维度 | 分值 | 来源 | 判断 |
|---|---:|---|---|
| 基础结构 | 15 | 脚本测量 | `.llm-wiki`、README、log、modules、sources、requirements、bugs、working-context、artifacts 是否存在 |
| 入口可读性 | 10 | LLM 判断 | README/index 是否基于 signals 展示真实项目入口和导航，不奖励长篇散文 |
| 模块上下文 | 20 | 脚本测量 + LLM 判断 | modules/index 覆盖、source-map 锚点存在、模块页能否说明职责和验证入口 |
| 来源登记 | 10 | 脚本测量 + LLM 判断 | `sources/`、`ingest/index.md`、`original_path` 是否登记真实资料且路径可解析；登记内容是否为真实资料而非占位 stub |
| 生命周期内容 | 15 | 脚本测量 + LLM 判断 | requirements、bugs、working-context、handoff、log 是否有真实条目和可追溯关系 |
| artifacts/dashboard 可见链路 | 10 | 脚本测量 | `artifacts/index.md`、dashboard、log、模块 README 是否能形成发现链 |
| Project Graph / cross-refs | 15 | 脚本测量 + LLM 判断 | graph 文件、edges/candidates、Project Graph Evidence / Gaps、cross-ref pins 是否适用且可用 |
| Validator 健康度 | 5 | 脚本测量 | 根据去重后的 validate ERROR/WARN 风险数量级扣分 |

等级建议：

| 分数 | 等级 | 含义 |
|---:|---|---|
| 0-30 | 空壳 wiki | 目录存在或部分存在，但缺少事实内容 |
| 31-60 | 初始可读 | 有一些入口和模块信息，但难以支撑稳定开发 |
| 61-80 | 可辅助查询 | 能帮助回答项目问题，仍有明显补齐项 |
| 81-100 | 生命周期可用 | 可支撑需求、bug、Project Graph、finish/review 流程 |

### 空模板识别

Doctor 需要识别“文件存在但几乎没用”的情况。第一版使用轻量启发式：

主信号满足任一即可视为 gap：

- 模块页的 source-map、关键类或 API 锚点无法解析到真实源码。
- 页面只有标题、目录、空表格或占位词。
- 出现 `TODO`、`TBD`、`待补充`、`placeholder`、`coming soon` 等占位信号，且缺少可验证锚点。

辅信号只提示、不单独定性：

- 正文有效字符数过少，但阈值按文件类型区分。

原则：短但 source-map 锚点全部解析的页面，不算空壳；长但没有任何可解析锚点的页面，仍算空壳。

## 中文报告模板

默认 text 输出中文为主，技术字段保持英文。

```markdown
# LLM Wiki Doctor 报告

## 关键结论

1. `.llm-wiki` 基础目录存在，但多个入口页仍接近空模板。
2. `modules` 有目录，但模块职责、源码入口、验证方式不足。
3. `sources/ingest` 缺少真实资料登记。
4. Project Graph 对当前项目适用，但 evidence / edge / candidate 不足。

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
10. 关闭上面列出的成熟度 gap 后再次运行 Doctor，确认 gap 收敛、无新增 ERROR。分数会随之上升，但目标是关闭具体 gap，不是凑到某个分数。

## 总体评分

- 分数：32/100
- 等级：空壳 wiki
- score_version：1
- 判断：目录结构已经建立，但缺少可支撑查询和开发决策的事实内容。
- 说明：分数是方向性指南，不是 KPI；不要为提分而填充无验证依据的内容。

## 成熟度维度

| 维度 | 适用性 | 得分 | 来源 | 问题 |
|---|---|---:|---|---|
| 基础结构 | applicable | 12/15 | 脚本测量 | 目录基本完整 |
| 模块上下文 | applicable | 4/20 | 脚本测量 + LLM 判断 | README 多为空壳，source-map 锚点不足 |
| 来源登记 | applicable | 0/10 | 脚本测量 + LLM 判断 | 没有登记真实资料，或登记内容像占位 stub |
| Project Graph | not-applicable | - | 脚本测量 | 单模块且未发现跨服务信号 |

## Validator 发现

### Errors

- 暂无

### Warnings

- `missing-graph-evidence`: ...
- `orphan-design-doc`: ...
```

## 修复边界

默认只读。

用户明确要求“修复 / 补齐 / 继续完善”后，允许进入受控修复。进入修复模式后：

- 结构性补齐可以批量执行：创建缺失目录、空 graph 文件、`cross-refs/index.md` 骨架、标题、导航占位、log 维护记录、索引入口链接结构。
- 语义内容必须来自源码证据、已有文档或用户确认：模块职责、源码入口、关键类/API、验证方式、需求背景、验收标准、bug 结论、跨项目关系。
- Doctor 自动补的是空壳的结构，不是结构里的业务内容。

不得自动编造：

- 模块职责。
- API 契约。
- Project Graph confirmed edge。
- 需求范围和验收标准。
- bug 结论。
- `source-verified`、`runtime-verified` 等验证状态。

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
3. `validate` 保持确定性，只输出 validator findings，现有 validator 测试继续通过。
4. `score` 输出 `score_version`、signals、applicable/not-applicable 维度、分数线索和 next step signals，且永不影响退出码。
5. `report` 输出中文 text 报告，包含关键结论、行动计划、分数、等级、validator 发现、成熟度缺口和 N/A 维度说明。
6. json 输出包含 validate findings、score signals、dimensions、score_version、level、next_steps，便于 CI 或 dashboard 复用。
7. 新增测试覆盖空壳 wiki、模块空 README、缺少 sources、Project Graph 只有空结构、单模块 Project Graph N/A、灌水但缺少锚点不提分等场景。
8. README 中英文版说明安装后自带 skill 触发和 doctor 脚本能力。
9. pre-commit、CI、project-finish 文档全部改为 `validate` 子命令。
10. 不触碰无关未跟踪目录，例如 `internal-trial-guides/`。

## 自检

- 无未完成占位。
- 设计同时保留旧 validator 和新增 maturity score，但两者执行路径隔离。
- 中文报告模板是默认 text 输出，不影响 json 结构化消费。
- 默认只读，修复行为必须经过用户确认。
- Project Graph 功能仍是 Doctor 的核心组成部分，但简单项目支持 N/A。
- Canonical 检查名已统一。
- `proposals.md` 已从第一版基础检查中移除，除非未来先定义 schema。
