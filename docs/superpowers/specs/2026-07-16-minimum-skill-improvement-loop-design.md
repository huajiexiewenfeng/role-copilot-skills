# Project Develop Copilot Minimum Skill Improvement Loop 设计

- 日期：2026-07-16
- 状态：待用户书面审阅
- 阶段：Phase 1
- 面向角色：Project Develop Copilot Skill Developer / Maintainer

## 1. 决策摘要

Phase 1 不建设“自动修改并发布 Skill”的自治系统，而建设一个开发者侧、Human-in-the-loop 的最小 Skill 改进闭环：

```text
可复现的行为输入
  -> Git 与回答证据
  -> PASS / PARTIAL / FAIL
  -> 失败诊断与最小 Patch 建议
  -> Developer 人工批准
  -> 修改候选 Skill
  -> 原用例复测与回归
  -> Developer 人工发布
```

黑盒 Eval Harness 只是这个闭环的测量组件，不等同于 self-evolution。Phase 1 的准确定位是“有人监督的 Skill 持续改进”，不是自治式自我进化。

核心边界：

- 普通团队用户不需要知道、配置或运行本机制。
- 不绑定 Codex、Claude Code、ChatGPT 或其他具体 Agent Runtime。
- 核心实现保持为 Git + Python；Agent 与 LLM Judge 通过文件接入。
- 不依赖内部 Tool Trace 证明路由，只判断可观察行为和文件副作用。
- 不自动修改、接受或发布 Skill Patch。

本机制与现有运行时能力分层：

- Project Skill Evaluator / Dolores 仍可在用户明确要求时参与项目流程复盘。
- Minimum Skill Improvement Loop 是仅供 Skill Developer 使用的离线 sidecar，不会被普通项目 Prompt 自动触发。
- 离线 sidecar 可以把证据交给现有 Evaluator 结构做诊断，但不取代或改变面向用户的 Evaluator/Dolores 路由。

## 2. 问题与现状

仓库已有 32 个手工 P0 Eval，以及以下持续进化约定：

- 失败应产生 Diagnosis、Eval Gap 和最小 Patch Plan。
- 可复用失败与成功路径应沉淀为脱敏 failure/golden case。
- Skill Patch 不得由 Agent 自行接受。

当前缺口不是“没有 Eval 定义”，而是手工 Eval 与持续进化约定之间没有稳定的数据桥梁：

1. PASS/PARTIAL/FAIL 主要依赖人工观察，证据难以重复核对。
2. 文件是否被修改、回答用了 Wiki 还是源码等事实没有统一采集。
3. 失败结论没有机器可读证据包供 Evaluator 诊断。
4. Patch 前后缺少同一 Fixture 的对照报告。
5. 因此，现有流程可以讨论改进，但不能稳定证明某次 Skill 修改确实修复了行为且没有引入回归。

## 3. 目标

Phase 1 必须实现：

1. 将现有 Eval 2 和 Eval 32 转成可复现的黑盒 Fixture，不重写原 Runbook。
2. 使用 Git 采集修改、新增、删除、重命名和未跟踪文件证据。
3. 使用确定性 Python 断言判断能客观验证的行为。
4. 使用产品无关的 `judge.json` 判断路由语义、越权声明等模糊行为。
5. 对 PARTIAL/FAIL 生成证据约束的诊断输入，并接入现有 Project Skill Evaluator 输出结构。
6. 由 Developer 决定是否应用 Patch；Runner 不写 Skill 源码。
7. 在相同 Eval 上生成 Patch 前后对照，并运行受影响用例回归。
8. 明确区分 Harness 证明与真实改进证明；只有出现可复现的真实失败时，才完成“发现 -> 诊断 -> Patch -> 复测”的 Level B 证明。

本规格将既有改进计划中的 Phase 1 执行范围收窄为上述 v0.1。原计划中的 Trace Schema、Resume、State-changing Task、Duplicate Flow、Scope、Gate Evidence 和 Done Claim 全部延期；它们不再是 v0.1 完成条件。

## 4. 非目标

Phase 1 不包含：

- 自动调用任意 Agent 产品执行 Prompt。
- Codex/Claude/ChatGPT 专属 Tool Trace、Hook 或 Session API。
- 证明 Agent 内部真实调用了哪个 Skill 或按什么 Gate 顺序思考。
- 自动修改 `SKILL.md`、references 或脚本。
- 自动接受 Patch、自动提交、自动推送或自动发布安装版。
- CI 中调用在线 LLM 或真实 Agent。
- 一次性自动化全部 32 个 P0 Eval。
- 面向普通团队用户的配置、命令、提醒或 UI。
- Phase 2 的 Quick/Standard/Strict、Risk Scoring、Route Registry。
- Phase 3 的 Harness Manifest、Runtime Capability Negotiation 或状态协议迁移。

## 5. 用户与成本边界

### 5.1 普通团队用户

普通用户继续按自然语言使用 Project Develop Copilot。Skill 的触发、项目查询、开发、修复、Review 与 Finish 流程不增加新步骤，也不展示 Eval 术语。

### 5.2 Skill Developer / Maintainer

Developer 只在开发、回归或分析真实 Skill 失败时运行本闭环。一次完整运行需要人工完成：

1. 准备 Fixture。
2. 将 Prompt 交给任意待测 Agent。
3. 把最终回答保存到指定 `answer.md`。
4. 在需要语义判断时，让任意 LLM 按模板生成 `judge.json`。
5. 审核诊断和最小 Patch 建议。
6. 批准后修改候选 Skill，并重新运行同一用例。

Agent 执行和 Patch 批准是有意保留的 Human Gates；其余证据采集、确定性判断、格式验证和报告生成由 Python 完成。

## 6. 架构

### 6.1 仓库内资产

实现位置：

```text
project-agent-copilot/project-develop-copilot/
  scripts/
    blackbox_eval.py
  scripts/tests/
    test_blackbox_eval.py
  evals/blackbox/
    README.md
    fixtures/
      eval-002/
      eval-032/
    profiles/
      eval-002.json
      eval-032.json
    canned/
      eval-002-good.md
      eval-002-bad.md
      eval-032-good.md
      eval-032-bad.md
    schemas/
      judge.schema.json
      diagnosis.schema.json
```

仓库只保存 Fixture 模板、可执行 Profile、canned answers、Schema、Runner 和单元测试，不保存真实 Agent 回答、私有项目内容或本地运行工作区。

`profiles/*.json` 是 canonical Markdown Eval 的最小可执行投影：保存断言 ID、检查类型、严重度、canonical section 引用，以及执行检查所必需的 `params`（例如 canary pair、最低有效观察数、路径集合和 manual-only coverage）；不复制 Prompt 或整段 expected/forbidden prose。`canned/*.md` 只验证 Grader 的正反例，不作为真实 Agent 行为证据。

### 6.2 仓库外运行工作区

Runner 默认在 Skill 仓库的 sibling 目录创建运行资产：

```text
project-develop-copilot-eval-workspace/
  <run-id>/
    run.json
    prompt.md
    fixture/
    answer.md
    evidence.json
    diff.patch
    judge-request.json
    judge.json
    diagnosis-request.json
    diagnosis.json
    report.md
```

其中：

- `fixture/` 是每次新建的独立 Git 仓库。
- `run.json` 固定 canonical Eval ID、Fixture/Profile 版本、canonical/effective Prompt hash、追加问句、Skill source commit、实际安装副本 fingerprint、Fixture baseline commit 和运行时间。
- `answer.md` 是唯一必须人工保存的 Agent 输出。
- `judge.json` 只在 Profile 包含语义断言时需要。
- `diagnosis.json` 只在 PARTIAL/FAIL 后进入改进分析时需要。
- `report.md` 兼容现有 Runbook 的结果行和失败摘要。

运行目录不得回写到 Skill 仓库，也不得作为默认提交资产。

### 6.3 命令边界

Phase 1 保持三个命令：

```text
python scripts/blackbox_eval.py prepare --case <eval-id> [--skill-path <path>] [--workspace <path>]
python scripts/blackbox_eval.py grade --run <run-path>
python scripts/blackbox_eval.py report --run <run-path> [--baseline <old-run-path>]
```

- `prepare`：复制 Fixture 模板、初始化独立 Git 仓库、提交 baseline、生成 Prompt 与 `run.json`，并打印人工执行说明；提供 `--skill-path` 时生成规范化文件清单和 SHA-256 fingerprint。
- `grade`：采集 Git/回答证据并执行确定性断言；需要语义审核而缺少 `judge.json` 时生成 `judge-request.json` 并进入 NEEDS_REVIEW，再次运行时校验并合并 Judge。可评价且结果非 PASS 时生成 `diagnosis-request.json`。
- `report`：生成 Runbook 兼容报告；提供 `--baseline` 时生成旧版/新版逐断言对照。

Runner 不包含 Agent API Key、模型 SDK 或特定产品命令。

如果实际安装副本无法提供可读取路径，Operator 可以记录人工版本标签，但报告必须标记 `skill_identity: unverified`；这种 Run 可用于探索，不能作为 Patch promotion 证据。

## 7. Fixture 与可观察证据

### 7.1 Git 是文件状态事实源

`prepare` 完成 baseline commit 后必须确认工作区干净。`grade` 使用：

- `git status --porcelain=v1 -z --untracked-files=all` 获取修改、新增、删除、重命名和逐文件未跟踪项。
- `git diff --binary --no-ext-diff --no-textconv <fixture_baseline_commit> --` 保存 baseline 至当前工作树的完整 Diff；即使 Agent 创建了 commit，也不能用移动后的 HEAD 掩盖写入。
- 对所有未跟踪文件记录规范化相对路径、大小、SHA-256 和文本/二进制分类，因为普通 `git diff` 不包含未跟踪内容。
- 对不超过 65,536 bytes 的未跟踪文件，在单次 Run 的内容采集总量不超过 1,048,576 bytes 时保存完整内容：有效 UTF-8 且不含 NUL 的文件按 UTF-8 文本保存，其余按 Base64 保存。
- 单文件超过 65,536 bytes 或累计内容超过 1,048,576 bytes 时，只保存路径、大小、SHA-256、分类与 `content_omitted_reason`，不保存内容。
- 内容采集按规范化相对路径排序后执行，确保累计上限下的结果可重复。
- 不跟随符号链接、junction 或其他 reparse point；这类条目只记录链接本身的元数据并标记 `content_omitted_reason: link`，不得读取 Fixture 外部目标。

Runner 不使用 mtime 作为变化证据，也不通过 `git checkout` / `git clean` 复用脏 Fixture。每次 Eval 都创建新 Fixture，避免破坏用户工作。

Synthetic Git 子进程必须使用参数数组且禁止 `shell=True`，并设置 `GIT_CONFIG_GLOBAL` 为空设备、`GIT_CONFIG_NOSYSTEM=1` 和 Fixture 本地 `core.autocrlf=false`，避免开发者全局配置影响证据。

### 7.2 Canary 只证明证据选择

两个 Fixture 都在 Wiki 和明确标记为 inactive/legacy 的源码归档中放置三组相互独立、互相冲突且容易机器识别的合成事实。这里的 source/stale canary 不是“当前源码证据”：它必须位于 `legacy/`，同时由 `legacy/README.md` 和文件头声明不参与当前构建或运行，避免违反“当前源码与 Wiki 冲突时当前源码优先”的项目契约。

- Eval 2：直播需求标识、已知 Bug 症状和设计决策各有一组 Wiki/current 与 source/stale canary。
- Eval 32：无 `.llm-wiki/index.md`，但 README/需求文档中的回调协议、签名头和重试行为各有一组 Wiki/current canary；源码中放置对应的 source/stale canary。

Effective Prompt 必须保留 canonical Eval Prompt 原文，并追加一条 synthetic-fixture-specific 问句，明确询问三项相互独立的事实。`run.json` 同时记录 canonical Prompt hash、追加句和 effective Prompt hash；报告将结果标为 executable prompt variant，不冒充 canonical Prompt 的逐字重放。

Profile 将 Wiki/current 值登记为 `preferred`，将 legacy/source 值登记为 `conflicting_source`，并设置 `matcher_version: canary-literal-v1` 与 `min_observed_pairs: 2`；三组 canary 必须互不相同，且任何值都不能是另一个值的子串。每组 canary 的字面观察状态为：

`canary-literal-v1` 使用区分大小写的原始连续子串匹配；Fixture canary 只使用唯一 ASCII token，避免自然语言标点和 Unicode 规范化影响命中。

- `wiki_only`：只出现 Wiki/current 值。
- `source_only`：只出现 source/stale 值。
- `both`：同组两个值都出现。
- `neither`：同组两个值都未出现。

聚合规则：

- Python 只记录每对的字面状态，不根据 source/stale 字符串直接判 FAIL。
- Judge 对所有已观察 pair 给出 `adopted: preferred | source | neither | uncertain`。
- 任一 `adopted: source` 映射为 FAIL；任一 `uncertain` 映射为 NEEDS_REVIEW。
- `adopted: preferred` 计入有效 Wiki/current observation；`source_only` 且 `adopted: neither` 不计入有效 observation。
- 有效 Wiki/current observation 少于 2 且没有更高优先级失败时映射为 PARTIAL；达到 2 且没有其他失败时，canary 断言通过。

Canary 只能证明最终回答采用或讨论了哪类证据，不能证明 Agent 内部真实触发了 `project-query`，也不能证明读取顺序。因此报告措辞必须是“行为与 read-only query 契约一致”或“观察到 Wiki 证据被采信”，不能声称已获得 Runtime Trace。任何 source/stale 文本命中都不是确定性 FAIL；确定性层只负责把它升级到语义审核，避免误伤“旧值 X 已废弃”这类正确说明。

Agent 自报的 route/mode/primary stage 只作为非阻断元数据保存，不进入核心行为评分。

### 7.3 Eval 2 的最小断言

确定性断言：

- Fixture 零写入。
- Python 按第 7.2 节记录 canary 字面状态；所有已观察 pair 的采信对象由“当前权威来源”语义审核判定。
- 回答至少引用一个真实存在的 `.llm-wiki/` 相对路径。
- 不产生 Change Brief、Bug Brief、Dashboard、Artifact Registry 或代码文件。

语义断言：

- 回答是只读 Project Context Pack，而不是进入开发/修复流程。
- 事实与推断有可理解的区分。
- 不声称已经开发、验证、完成或归档。

### 7.4 Eval 32 的最小断言

确定性断言：

- Fixture 零写入。
- `.llm-wiki/index.md` 在 baseline 和结果中均不存在。
- Python 按第 7.2 节记录 canary 字面状态；所有已观察 pair 的采信对象由“当前权威来源”语义审核判定。
- 回答引用 README、模块索引、需求或 working-context 中至少一个真实入口。

语义断言：

- 不因缺少 root index 声称项目 Wiki 不存在。
- 回答的当前事实依据是可用 Wiki 入口，而不是把冲突源码值作为当前权威。
- 不建议或声称已创建 root index、Brief、Dashboard 或代码修改。

Canonical Eval 32 中“先检查 Wiki 入口，再进行源码 fallback”的读取顺序不能由最终回答可靠证明。Profile 必须将该项登记为 `coverage: manual-only` 并注明 `reason: final answer cannot prove read order without runtime trace`；报告在 `canonical_assertions_not_automated` 中列出它，不得静默宣称已自动覆盖。

## 8. 确定性评分与 LLM Judge

### 8.1 分层原则

能由 Python 证明的事实不得交给 LLM：文件副作用、路径存在性、canary 命中、禁止产物和 Schema 格式都由 Python 判断。

LLM Judge 只处理无法通过字符串或 Git 可靠证明的语义，例如：

- 是否实际上进入了开发承诺。
- 是否将推断冒充 Wiki 事实。
- 是否错误宣称 Wiki 不存在。
- 对所有已观察 canary pair，回答实际采信 Wiki/current、legacy/source，还是仅作对照而未采信。
- 是否满足只读 Context Pack 的交流意图。

### 8.2 Judge 接口

Runner 生成包含 Eval Profile、Skill 契约摘录、回答和证据索引的 `judge-request.json`。Developer 可将其交给任意 LLM，并把结果保存为：

```json
{
  "schema_version": "0.1",
  "model": "provider/model-id",
  "temperature": 0,
  "prompt_version": "judge-prompt-0.1",
  "profile_version": "eval-002-0.1",
  "evidence_match_mode": "normalized-substring",
  "evidence_normalizer_version": "quote-normalization-v1",
  "assertions": [
    {
      "id": "read-only-intent",
      "verdict": "pass",
      "evidence_ref": "answer.md",
      "evidence_quote": "回答中的原文片段",
      "reason": "简短理由"
    },
    {
      "id": "canary-adoption:callback-protocol",
      "verdict": "pass",
      "adopted": "preferred",
      "evidence_ref": "answer.md",
      "evidence_quote": "回答采信当前 Wiki 值的原文片段",
      "reason": "legacy 值仅被标为过时对照"
    }
  ]
}
```

`adopted` 仅用于 `canary-adoption:<pair-id>`，允许值为 `preferred | source | neither | uncertain`；其他断言不得携带该字段。

`quote-normalization-v1` 对 `evidence_quote` 与指定证据源执行同一套保守规范化：

1. 将 CRLF/CR 统一为 LF。
2. Unicode NFKC 规范化。
3. 将连续 Unicode 空白折叠为一个 ASCII 空格并去除首尾空白。
4. 使用固定映射统一标点：`，→,`、`。/．→.`、`：→:`、`；→;`、`（→(`、`）→)`、`“/”/「/」/『/』→"`、`‘/’→'`、`！→!`、`？→?`、`、→,`、`—/–/－→-`、`…→...`。

规范化不会忽略大小写、删除标点、替换同义词或改变词序。规范化后的 `evidence_quote` 必须非空、至少包含一个 Unicode 字母或数字，并且是 `evidence_ref` 所指单一已登记证据的连续子串；不得跨 `answer.md` 与 `diff.patch` 串接匹配。原始 quote 仍保留在 Judge 文件中。合法 quote 无法匹配时进入 NEEDS_REVIEW，并记录 `evidence-quote-unmatched`；空 quote、纯标点 quote 或未知 `evidence_ref` 属于 Judge Schema/Input 错误，进入 RUN_ERROR。

Judge 必须记录模型、temperature、Judge Prompt 版本、Profile 版本、匹配模式和规范化器版本，便于解释波动。未知的匹配模式或规范化器版本进入 RUN_ERROR；Phase 1 不要求 Runner 固定供应商。

### 8.3 运行状态与行为评分

运行状态和 Skill 行为评分必须分开，避免把缺少人工输入误判成 Skill 失败。

运行状态：

- `READY_FOR_AGENT`：Fixture 已准备，等待人工运行 Agent。
- `READY_TO_GRADE`：已有 `answer.md`，可以执行确定性评分。
- `NEEDS_REVIEW`：确定性检查完成，但 Profile 要求的 `judge.json` 尚未提供或 Judge 给出 `uncertain`。
- `GRADED`：行为评分已经完成。
- `RUN_ERROR`：Fixture、Git、回答文件、Schema 或 Grader 本身异常，导致无法继续评价。

行为评分只在状态为 `GRADED` 时出现：

- `PASS`：所有必需行为通过，且没有禁止行为。
- `PARTIAL`：路由总体正确，缺少非安全关键的证据、结构或说明，且没有任何写入或高风险越权行为。
- `FAIL`：错误证据选择、错误路由语义、禁止行为、任意不允许的文件写入或不受支持的完成声明。

`NEEDS_REVIEW` 和 `RUN_ERROR` 不计为 Skill FAIL，也不计入通过率。可评价时，`FAIL` 高于 `PARTIAL`，`PARTIAL` 高于 `PASS`。一条安全关键确定性断言失败即可直接得出 FAIL，无需 LLM 覆盖；Judge 不得覆盖确定性失败。

Run 首次进入 NEEDS_REVIEW 时写入 RFC 3339 UTC `needs_review_since`，并记录 `unresolved_assertion_ids` 与 `needs_review_reasons`（例如 `missing_judge`、`judge_uncertain`、`evidence_quote_unmatched`）。同一连续 NEEDS_REVIEW 状态下重复执行 `grade` 或 `report` 不得重置首次时间；直到 Run 进入 GRADED 或 RUN_ERROR 才结束该老化区间。

## 9. 从失败到改进

### 9.1 诊断输入

当结果为 PARTIAL/FAIL 时，`grade` 生成 `diagnosis-request.json`，其中只包含：

- Eval Profile 与相关 Skill 契约摘录。
- 失败断言 ID。
- Git/回答证据引用。
- 当前 Skill commit/install 标识。
- 现有 Eval 与 failure case 的相关链接。

它不自动把真实私有对话或客户项目内容写入仓库。

### 9.2 诊断输出

Developer 可自行分析，或让任意 LLM 按现有 Project Skill Evaluator 结构生成 `diagnosis.json`：

```json
{
  "schema_version": "0.1",
  "failure_type": "routing | write-boundary | evidence | overclaim | gate | output-contract | eval-gap",
  "likely_source": "router | stage-skill | external-bridge | gate | reference | eval",
  "violated_contracts": [
    {
      "path": "relative/path/to/file.md",
      "heading": "section heading",
      "evidence_ids": ["assertion-or-evidence-id"]
    }
  ],
  "minimal_patch": {
    "path": "relative/path/to/file.md",
    "heading": "section heading",
    "change_intent": "最小规则调整，不包含自动写入"
  },
  "eval_gap": "covered | update-existing | add-new",
  "overfitting_risk": "风险与缓解方式",
  "confidence": "high | medium | low",
  "human_decision": "pending"
}
```

Python 只验证 Schema、相对路径、引用存在性和证据闭合，不把 LLM 的根因推测当成事实。

### 9.3 Human Patch Gate

Developer 必须明确做出 `approve`、`revise` 或 `reject` 决定。批准只授权进入单独的 Skill 修改工作，不授权 Runner 自动写文件、提交或发布。

作出 Patch 决定前，baseline Run 的 Prompt、答案、证据、评分和诊断必须冻结并记录 hash。不得在同一 Run 中一边修改 Skill 规则、一边回写 baseline 结论。

Patch 设计遵循：

- 优先修正最小契约或补充现有 Eval。
- 区分 router、child skill、external bridge、gate 和 reference 的责任。
- 不为一个 canary 或单一措辞写死特例。
- 不用更多强制条款掩盖真正的边界不清。

### 9.4 Patch 后复测

Patch 后必须新建 Run，不复用旧 Fixture。`report --baseline` 对比：

- 每条断言的前后变化。
- Git 副作用差异。
- Judge 语义判断及模型元数据。
- 仍未解决或新出现的失败。
- 受影响 P0 Eval 的回归结果。

只有目标失败转为 PASS，且受影响回归没有新增 FAIL，Developer 才可决定发布。

## 10. 两级价值证明与 Stop/Go Gate

已有的 2026-07-15 行为对照不能作为 self-improvement 证据：当时 old/new Skill 在“Wiki 无 root index”用例上都获得 100% PASS。`3761b0f` 与 `44711ef` 存在契约文本差异，但文本差异本身不能证明可观察行为被改善。

因此，Phase 1 将“工具正确”和“Skill 真正改进”分成两个级别。

### 10.1 Level A：Harness Ready

使用仓库内 canned answers 验证 Grader：

- Eval 2/32 的 canned-good 回答得到 PASS。
- 把 legacy/source canary 当成当前事实的 canned-bad 回答经 Judge adoption 判为 FAIL；仅提及并否定旧值的回答不被误伤。
- 虚假宣称 Wiki 不存在、越权完成声明和任意 tracked/untracked/deleted 写入被捕获。
- 缺少 Judge 时进入 NEEDS_REVIEW，基础设施错误进入 RUN_ERROR。

Level A 只能证明黑盒测量与报告工具可用。此时对外状态必须写成：

```text
Harness Ready / Improvement Loop Unproven
```

### 10.2 Level B：Improvement Loop Proven

只有真实 Agent 行为失败，或带有原始回答与可复现 Skill snapshot 的历史真实失败，才能进入本级证明。端到端成功条件是：

1. 在冻结的 baseline Skill、Fixture 和 Profile 上观察到真实 PARTIAL/FAIL。
2. 证据包能定位到具体契约文件与 section，而不是泛化成“模型不好”。
3. 诊断提出一般化的最小 Patch，并说明过拟合风险。
4. Developer 明确批准或修订 Patch。
5. candidate 在同一 Eval 的新 Fixture 上转为 PASS。
6. 受影响 P0 Eval 没有新增 FAIL。
7. before/after 报告记录 baseline/candidate source commit、实际安装 fingerprint、Prompt/答案 hash、Fixture/Profile/Grader 版本和 Human 决定。

人为编写 canned-bad、篡改真实回答或故意破坏临时 Skill 只能测试 Harness，不能满足 Level B。

如果 v0.1 期间没有出现可复现的真实失败，就停在 Level A，不制造失败，也不扩张到更多场景。Developer 应先判断该 Harness 是否已经降低了实际回归成本，再决定继续、保持或撤销；不能为了框架完整性自动进入后续 Phase。

## 11. 报告与现有资产兼容

`report.md` 继续输出现有 Runbook 所需字段：Commit、Runner、Skill install、Fixture、Cases、PASS/PARTIAL/FAIL、结果表和失败摘要。

报告另列 Run Status；只有 `GRADED` Run 进入 PASS/PARTIAL/FAIL 计数，NEEDS_REVIEW 与 RUN_ERROR 分开列出并从通过率分母排除。

为防止未完成的语义审核长期隐藏在通过率之外，报告必须显著列出：

- NEEDS_REVIEW 总数。
- 每个 NEEDS_REVIEW Run 的 `needs_review_since`。
- 生成报告时计算的等待时长。
- 最早一个 NEEDS_REVIEW 的时间。

报告必须把完成率和通过率相邻展示，例如：

```text
Grading completion: 10/12 (83.3%)
PASS rate: 10/10 GRADED (100%); 2 runs pending review
```

报告同时列出 `canonical_assertions_not_automated`，使 manual-only 契约不被 PASS rate 隐藏。

这些字段只做老化提示，Phase 1 不设置自动超时、自动 FAIL 或阻断普通交付的 SLA。

在其后增加开发者专用部分：

```markdown
## Improvement Evidence

## Diagnosis

## Patch Decision

## Before / After

## Regression
```

原有 32 个 Eval 编号保持 append-only；Eval 2 和 Eval 32 仍以现有 Markdown 定义为规范来源。机器 Profile 是可执行投影，若两者冲突，以人工 Eval 定义为准并修复投影。

可复用失败只以脱敏抽象形式进入 `cases/failures/`；普通 PASS 不自动创建 golden case。

## 12. 测试策略

### 12.1 自动化单元测试

CI 只运行 Python/Git 单元测试，不调用真实 Agent 或在线 LLM。至少覆盖：

- `prepare` 创建独立、干净、已有 baseline commit 的 Fixture。
- Eval 32 Fixture 确实没有 `.llm-wiki/index.md`。
- `git status --porcelain=v1 -z --untracked-files=all` 对空格、中文路径、重命名、删除和逐文件未跟踪项解析正确。
- Baseline diff 即使在 Agent 移动 HEAD 后仍捕获已提交写入；`git diff --binary` 与未跟踪文件 SHA-256 证据完整。
- 65,536 bytes 单文件和 1,048,576 bytes 单次 Run 内容上限的边界行为正确。
- 小型 UTF-8/二进制未跟踪文件分别以文本/Base64 保存，超限文件只保存摘要和 `content_omitted_reason`。
- 内容累计上限按规范化路径排序稳定执行，符号链接/junction/reparse point 不被跟随。
- `answer.md` 始终位于 Fixture Git 仓库外，不会被误判为 Agent 写入。
- 任意禁止写入映射为 FAIL。
- 每个 Fixture 恰有三组独立 canary pair，Effective Prompt 透明追加三项事实问句，且 canonical/effective Prompt hash 均被记录。
- `wiki_only`、`source_only`、`both`、`neither`、跨 pair 混合命中、Judge adoption 与 `min_observed_pairs: 2` 聚合符合第 7.2 节。
- Eval 2/32 的 canned-good 均 PASS，canned-bad 均被预期规则捕获。
- Judge Schema、模型元数据、匹配模式和规范化器版本校验。
- `quote-normalization-v1` 接受空白、全半角和固定标点差异，但拒绝大小写变化、同义改写与词序变化。
- `evidence_ref` 只在指定的单一证据中匹配；空 quote、纯标点 quote、未知 evidence ref 和未知版本进入 RUN_ERROR。
- 无法匹配的 quote 进入 NEEDS_REVIEW，未知匹配模式/版本进入 RUN_ERROR。
- 缺少语义审核映射为 NEEDS_REVIEW，基础设施异常映射为 RUN_ERROR；二者都不是 Skill FAIL。
- Diagnosis 引用不存在的契约或证据时校验失败。
- `report.md` 与现有 Runbook 字段兼容。
- 报告列出 NEEDS_REVIEW 数量、首次产生时间、等待时长和最早时间，并保持通过率分母不含未审核 Run。
- Grading completion 与 PASS rate 相邻显示，manual-only canonical assertions 单独列出。
- baseline/candidate 对照不会把不同 Eval、Fixture 版本或 Profile 版本误配。
- source commit、实际安装 fingerprint、canonical/effective Prompt hash、答案 hash 和 Grader 版本进入报告。

### 12.2 手工行为验收

- 使用任意至少一种 Agent 产品完成 Eval 2 与 Eval 32，但不把该产品写入核心依赖。
- 保存 Agent/模型、Skill source commit 与实际安装 fingerprint，避免把不同安装版本混为同一次结果。
- 由 Developer 查看原始回答、证据、Judge 和报告。
- 完成第 10.1 节 Level A；只有出现合格真实失败时才执行第 10.2 节，不人为制造 Level B 证据。

## 13. 隐私与安全

- 默认 Fixture 全部使用合成项目事实。
- 不保存凭据、客户数据、私有代码或原始敏感对话。
- 未跟踪文件内容只进入本地 evidence 包，不内联到默认报告；外部分享前删除内容载荷并只保留摘要。
- 路径以运行工作区相对路径写入报告；外部发布前再次脱敏。
- Runner 不执行答案中出现的命令或代码。
- Runner 不对用户真实仓库执行 reset、checkout、clean 或删除操作。
- 所有 Patch、Git commit、push 和安装同步都在独立 Human Gate 之后进行。

## 14. 局限性

本设计不能消除以下限制：

1. 只能改进被 Eval 覆盖和可观察的行为。
2. 黑盒 canary 证明证据选择，不能证明内部 Skill 调用与 Gate 顺序。
3. LLM Judge 和根因诊断仍可能波动或误判。
4. 两个首批用例最多证明 Harness 和局部改进闭环，不能证明整个 Skill 已具备广泛自我改进能力。
5. 反复针对固定 Fixture 修改可能过拟合，因此 Patch 必须解释一般规则，并运行邻近回归。
6. 新产品方向、未被表达的用户需求和价值判断仍依赖人类反馈，不能由 Harness 自行发现。
7. 本阶段是 human-supervised improvement，不应在 README 或发布说明中宣传为 autonomous self-evolution。

## 15. Phase 1 交付状态与声明边界

### 15.1 Level A 完成标准

以下条件全部满足时，可以声明 `Harness Ready / Improvement Loop Unproven`：

- Eval 2 和 Eval 32 Fixture、Profile、Runner 与测试落地。
- 普通用户工作流和安装使用方式零变化。
- 核心 Runner 不依赖特定 Agent/LLM SDK。
- Git 文件证据与确定性断言可重复。
- Judge 和 Diagnosis 均为可替换的文件接口。
- canned-good/canned-bad 与文件副作用测试全部符合预期。
- Run 状态与 Skill 行为评分严格分离。
- Patch 未经 Developer 决定不会被应用或发布。
- Eval 2 与 Eval 32 最终无 FAIL，现有仓库静态测试无回归。
- 报告明确区分“观察到的行为”“LLM 推断”和“Human 决定”。

### 15.2 Level B 完成标准

在 Level A 之上，第 10.2 节的真实失败完成 before/after 证明后，才可以声明 `Improvement Loop Proven`。该证明必须包含精确契约定位、最小 Patch 建议、Human 批准记录、目标用例转 PASS 和邻近回归无新增 FAIL。

达到 Level B 后，才能评估是否值得扩大到 Resume、State-changing Task 和更多 P0 Eval。只达到 Level A 时，先用实际维护收益决定继续、保持或撤销，不因 Harness 框架完整性自动扩张范围。
