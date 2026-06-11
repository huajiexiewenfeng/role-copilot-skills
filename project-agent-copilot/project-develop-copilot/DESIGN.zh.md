# Project Develop Copilot 设计

## 愿景

Project Develop Copilot 不是又一套复杂的 skills 体系。

它站在 Superpowers、OpenSpec、LLM Wiki、CodeGraph 和既有 project coding context 等实践的肩膀上，把这些分散能力收拢到同一个项目开发生命周期里。

它的目标不是让团队学习更多入口，而是让团队少记入口：从需求、临时资料、bug、跨服务变更，到计划、实现、验证、交付和知识回写，都通过一个 Project Develop Copilot 协调完成。

Superpowers 提供通用工程纪律，OpenSpec 提供规格变更思想，LLM Wiki 提供项目知识索引，CodeGraph 提供代码结构加速，历史 project coding context 提供已有项目经验。Project Develop Copilot 负责把它们组织起来，让人、Agent、文档、代码和知识库围绕同一个需求一起工作。

它追求的不是一次性完美自动化，而是先把项目开发中最割裂、最容易丢上下文的环节连起来，然后在真实项目中逐步演进。

## 定位

Project Develop Copilot 是 Project Agent Copilot 角色组下的项目开发生命周期 skill，适合放在 `role-copilot-skills/project-agent-copilot/project-develop-copilot/` 中。

它是 Project Agent Copilot 角色组下的第一个 domain skill，而不是整个角色组本身。Project Agent Copilot 可以继续承载更多项目研发 domain skills，例如 `project-prd-copilot`、`project-ui-copilot`、`project-review-copilot`、`project-release-copilot`、`project-test-copilot` 等。

它不是单纯的 coding skill，也不是 Obsidian LLM Wiki 的替代品。它负责把项目开发中的需求进入、上下文补全、规格建模、计划执行、验证、知识回写、review 和后续跟进编排成一套统一流程。

核心原则：

- 用户只面对 Project Develop Copilot，不直接面对底层零散 skills。
- Project Develop Copilot 不复制 superpower skills，只编排它们。
- LLM Wiki 内化为项目上下文机制，由 Copilot 自动维护。
- OpenSpec 是可选工具；必须内置的是 spec/change protocol。
- CodeGraph 是可选代码理解增强器；存在 `.codegraph/` 时使用，不存在不阻塞。

## 对外入口

建议只暴露这些主入口：

```text
project init
project ingest
project develop
project fix
project finish
project review
```

### project init

初始化项目开发协议。

职责：

- 初始化或检查项目规则。
- 初始化项目级 `.llm-wiki/`。
- 检测项目是否已有 `docs/ai-coding/`，并把它作为项目编码上下文来源接入。
- 识别单仓库多模块 / 多微服务结构，建立 context scope registry。
- 检测 superpower skills 是否可用。
- 检测 `.codegraph/` 是否存在。
- 写入本项目 Agent 工作约定。

### project ingest

接收临时资料、需求、链接、PDF、Word、Markdown、会议纪要、客户反馈、线上问题线索等。

职责：

- 引导用户确认资料来源和用途。
- 扫描配置的 source directories，发现用户手动拷贝但尚未索引的资料。
- 识别资料类型：需求、bug、设计补充、背景资料、决策依据、待确认线索。
- 创建 source proxy。
- 更新 `.llm-wiki/ingest/index.md`。
- 需要时创建 requirement draft、bug draft 或 follow-up。
- 不默认复制大段原文，不默认深读敏感材料。

### project develop

正式需求开发流程。

职责：

- 执行 Context Enrichment Gate。
- 基于 wiki 和原始资料恢复上下文。
- 进入需求讨论和 spec/change protocol。
- 生成 implementation plan。
- 执行计划。
- 验证实现。

### project fix

bug 修复流程。

职责：

- 接收 bug 描述、日志、链接或外部资料。
- 必要时先执行 project ingest。
- 查询相关模块、历史问题、最近变更。
- 复现、诊断、制定轻量修复计划。
- 执行修复并验证。
- 验证通过后更新 bug 摘要和相关模块知识。

### project finish

开发完成后的知识同步和交付准备。

职责：

- 确认测试、构建、lint 或人工验证已经完成。
- 执行 Knowledge Sync Gate。
- 更新 `.llm-wiki/` 的索引、摘要、关系、状态和缺口。
- 执行 wiki lint/maintain。
- 准备 commit、PR 或交付说明。

### project review

review 和合并前检查。

职责：

- 检查 diff、测试、spec、wiki 是否一致。
- 检查是否遗漏需求、bug、模块或决策更新。
- 输出风险、阻塞项和建议。

## Lifecycle Router

Project Develop Copilot 必须提供一个总入口，而不是要求用户准确选择 `project-query`、`project-init`、`project-ingest`、`project-develop`、`project-fix`、`project-finish` 或 `project-review`。

用户可以用自然语言进入项目生命周期，例如：

```text
帮我基于这个 PRD 开发
我想改一个 bug
看一下这段日志
继续上次那个需求
这次改动完成了吗
帮我 review 一下
```

Router 的职责不是简单分发子 skill，而是先创建或恢复一个生命周期会话，再决定当前应该进入哪个阶段。用户面对的是 Project Develop Copilot；七个 project skills 是内部阶段能力。

Router 输入：

- 用户当前请求
- 当前项目路径和 git 状态
- `.llm-wiki` 是否存在
- `.llm-wiki/requirements/`、`.llm-wiki/bugs/`、`.llm-wiki/working-context/` 中是否存在 active / draft / executing / blocked 状态
- 用户提供的 PRD、设计文档、日志、链接、截图、diff 或错误信息
- 最近一次生命周期日志和 Artifact Registry

Router 输出：

```text
intent: init | ingest | discuss | develop | fix | finish | review | resume | unknown
project_root:
lifecycle_session:
active_change_or_bug:
next_stage:
required_gates:
external_bridges:
open_questions:
```

路由规则：

- 如果项目没有 `.llm-wiki`，先建议或执行 `project-init`，但不要阻塞用户表达的真实目标。
- 如果用户输入的是 PRD、设计文档、会议纪要、链接、PDF、Word、日志或截图，先进入 `project-ingest`，再判断是否转入 requirement、bug 或 evidence。
- 如果用户表达“基于项目 wiki 回答、找一下相关需求/开发文档、把上下文找出来、先不要开发、我们先讨论”，进入 `project-query`。
- 如果用户询问“这个接口对面是谁”“这个 topic 谁发谁消费”“这个 Feign 调哪个服务”或其他跨服务契约线索，且当前 wiki 证据不足，进入 `project-query` 的 cross-project lookup；如果用户要求开发或修 bug，则在当前 `project-develop` / `project-fix` 阶段内进入 Cross-Project Boundary Gate。
- 如果用户表达“开发、实现、改需求、做功能”，进入 `project-develop`，但必须先创建或恢复 Change Brief。
- 如果用户表达“bug、报错、失败、异常、日志、线上问题”，进入 `project-fix`，但必须先创建或恢复 Bug Brief / Change Brief。
- 如果用户表达“继续、上次、按计划执行”，优先恢复最近 active / ready / executing 的 Change Brief；若存在多个候选，询问用户选择。
- 如果用户表达“完成了吗、收尾、同步文档、准备交付”，进入 `project-finish`。
- 如果用户表达“review、检查、合并前看一下、有没有风险”，进入 `project-review`。
- 如果用户意图不清楚，Router 只问一个最小澄清问题，不把用户拖进长表单。


### Thinking Router 借鉴

Lifecycle Router 可以参考 `huajiexiewenfeng/thinking-skills` 中 `thinking-router` 的路由纪律，但不能照搬为普通 domain skill router。

可借鉴的原则：

- Router 不解决实体问题，只判断意图、恢复状态和选择下一阶段。
- Router 先判断是否需要进入完整生命周期；轻量问答可以走 lightweight-answer，不强行创建 Change Brief。
- Router 选择一个 primary stage，例如 `project-develop` 或 `project-fix`。
- Router 可以携带 optional secondary bridge，例如 brainstorming、systematic-debugging、writing-plans 或 verification-before-completion。
- 低置信度时只问一个最小路由问题，不启动长表单。
- Router 输出简短 routing record，供后续 Agent 恢复判断依据。

与 thinking-router 的关键差异：

- thinking-router 路由后可以把控制权交给 domain skill；Lifecycle Router 不能完全放手。
- Project Develop Copilot 必须持续拥有 lifecycle session、scope、Change Brief / Bug Brief、Artifact Registry、progress dashboard、finish 和 review。
- 外部 skills 只作为 bridge，不能成为生命周期主线。

推荐 routing record：

```text
Intent:
Primary stage:
Secondary bridges:
Lifecycle session:
Active sources:
Active scopes:
Confidence:
Reason:
Next gate:
```
核心原则：

```text
Every entry is resumable.
Every entry is scoped.
Every entry returns to lifecycle.
```

也就是说，不管从哪个入口进入，都必须能恢复上下文、限定 scope，并最终回到 finish / review / wiki sync / artifact sync 的生命周期闭环。

## Lightweight Answer Mode

Lifecycle Router 不应该把所有项目相关问题都强行升级为完整生命周期。Project Develop Copilot 需要保留轻量回答模式，用于用户只想快速理解、定位或确认某个信息的场景。

适合 lightweight-answer 的场景：

- 用户只询问某个 README、设计文档、skill 文件或目录的含义。
- 用户询问当前设计里的某个概念，例如 Gate、Artifact Registry、Change Brief。
- 用户只要求解释、对比、定位文件或给出建议，不要求执行开发、修复、同步、review 或交付。
- 用户明确说“先讨论一下”“不开发”“不用进入流程”。

lightweight-answer 的边界：

- 不创建 Change Brief 或 Bug Brief，除非用户要求保存讨论结果。
- 不修改代码、skill、wiki、artifact 或 dashboard。
- 不宣称需求完成、bug 修复完成或项目状态已更新。
- 不调用外部 implementation skills。
- 可以引用 `.llm-wiki`、DESIGN、README、references 或源码作为只读证据。

必须升级到完整 lifecycle 的场景：

- 用户要求开发、修 bug、执行计划、finish、review、提交、发布或更新项目状态。
- 用户提供 PRD、日志、错误信息、diff 或测试失败，并希望继续处理。
- 讨论已经产生明确需求、bug、验收标准、计划或待执行项。
- 回答会影响 scope、验证、artifact、dashboard 或 `.llm-wiki` 状态。

升级时 Router 应说明升级原因，并创建或恢复 Lifecycle Session。
## Project Query Mode

`project-query` 是 Project Develop Copilot 的只读项目知识查询入口，设计目标接近 Obsidian LLM Wiki 的 `obsidian-wiki-query`，但作用域限定在当前项目的 `.llm-wiki`。

它解决的不是“是否开发”，而是“先把和这个问题有关的项目证据找出来，方便继续讨论”。用户可能只是想理解历史需求、设计文档、bug 背景、模块边界、风险或之前的决策，不应该因此被强行带入 Change Brief、Bug Brief 或执行计划。

适合 `project-query` 的触发语言：

```text
基于这个项目的 llm wiki 回答一下...
帮我找一下某个功能相关的需求和开发文档。
先把上下文找出来，我们讨论一下。
这个模块之前有哪些设计、bug、风险和决策？
不要开发，先看项目 wiki 里的证据。
```

`project-query` 的读取顺序：

1. 解析项目根目录和 `.llm-wiki/index.md`。
2. 查看 `.llm-wiki/modules/`、`.llm-wiki/ingest/index.md`、`.llm-wiki/requirements/`、`.llm-wiki/bugs/`、`.llm-wiki/sources/`、`.llm-wiki/working-context/` 和 artifact 记录。
3. 根据用户主题搜索相关页面，必要时回到 source proxy 或原始文档进行只读核验。
4. 输出 Project Context Pack，而不是实现计划。

Project Context Pack 至少包含：

- Answer：基于证据的直接回答。
- Relevant Context：相关需求、bug、source proxy、artifact、working-context 或模块页面。
- Evidence：引用哪些项目 wiki 页面或原始资料。
- Inference：哪些判断是 Agent 推断，不是文档明说。
- Confidence：上下文是否完整、是否可能过期。
- Possible Next Routes：继续讨论、补充 ingest、创建 Change Brief、创建 Bug Brief、进入 review、触发 skill-evaluator 或 Dolores。

边界：

- 默认不创建 Change Brief / Bug Brief。
- 默认不创建或更新 working-context。
- 默认不改代码、不改 dashboard、不同步 artifact。
- 如果发现 wiki 缺失或明显过期，可以建议 `project-ingest` 或 `project-init`，但不自动改写状态，除非用户同意。
- 如果用户在讨论中明确说“那就开始做”“按这个修”“进入 review”“记录成需求”，Router 再升级到对应 lifecycle stage。

`project-query` 和 `lightweight-answer` 的区别：lightweight-answer 适合不需要项目 wiki 搜索的快速解释；`project-query` 需要主动检索 `.llm-wiki` 并组装证据。`project-query` 和完整 lifecycle 的区别：它输出讨论上下文，不输出执行闭环。
## Lifecycle Session

生命周期会话是 Project Develop Copilot 的状态主线。它不是用户手写表单，而是 Agent 在自然对话和项目操作中维护的轻量状态对象。

需求类会话优先使用：

```text
.llm-wiki/requirements/<change-id>.md
```

Bug 类会话优先使用：

```text
.llm-wiki/bugs/<bug-id>.md
```

复杂或跨模块工作额外使用：

```text
.llm-wiki/working-context/<change-id>.md
```

Lifecycle Session 至少要能回答：

- 当前处理的是哪个需求、bug 或任务？
- 哪些 source、artifact、计划和验证记录属于它？
- 当前状态是 draft、clarified、planned、ready、executing、done 还是 blocked？
- active scope、read-only scope、candidate scope、excluded scope 分别是什么？
- 是否已经确认验收标准？
- 是否已经确认计划？
- 是否进入执行？
- 是否完成验证和知识回写？

Change Brief 是需求类 Lifecycle Session 的默认实现。Bug Brief 可以复用相同状态思想，但字段更偏向 symptom、evidence、diagnosis、fix 和 verification。
### Routing Record Persistence

Router 每次进入完整生命周期时，都应保存简短 routing record，避免后续 Agent 不知道为什么进入某个阶段。

保存位置：

- requirement / feature：写入 `.llm-wiki/requirements/<change-id>.md` 的 `## Routing` 区。
- bug / incident：写入 `.llm-wiki/bugs/<bug-id>.md` 的 `## Routing` 区。
- cross-module work：同步摘要到 `.llm-wiki/working-context/<change-id>.md`。
- review-only 且无法绑定现有 session：创建临时 review context，或在 `.llm-wiki/log.md` 记录 routing decision。
- lightweight-answer：默认不保存 routing record，除非用户要求留痕。

最小字段：

```markdown
## Routing

- intent:
- primary_stage:
- secondary_bridges:
- confidence:
- reason:
- next_gate:
- routed_at:
```

Routing record 是决策痕迹，不是长篇推理。它只记录足够让后续 Agent 恢复上下文的结论。

### Bug Brief Minimum

Bug Brief 是 bug 类 Lifecycle Session 的默认状态对象。它不需要完整 PRD，但必须记录足够的证据、scope、诊断和验证状态。

建议路径：

```text
.llm-wiki/bugs/<bug-id>.md
```

最小结构：

```markdown
# Bug Brief: <bug-id>

## Summary

- title:
- status: draft | triaged | reproduced | diagnosed | planned | ready | executing | verified | done | blocked
- severity:

## Routing

- intent:
- primary_stage:
- secondary_bridges:
- confidence:
- reason:
- next_gate:
- routed_at:

## Source

- path/url/log/user report:
- source_proxy:

## Symptom

## Expected

## Evidence

## Reproduction

- status: reproduced | not-reproduced | blocked
- command_or_steps:
- observed:
- expected:

## Scope

- active:
- read-only:
- candidate:
- excluded:

## Diagnosis

## Fix Plan

## Verification

## Artifacts

## Open Questions

## Residual Risk
```

规则：

- 未复现或证据不足时，不得大范围修改代码，除非用户明确接受风险。
- 修复计划必须绑定 active scope。
- 修改 read-only、candidate 或 excluded scope 必须走 scope escalation。
- 验证通过或限制被明确接受后，才能进入 Knowledge Sync Gate。

## Lifecycle Gate Stack

Project Develop Copilot 的七个 project skills 不应该各自发明流程，而应该共享同一套生命周期门。不同入口可以跳过不相关的门，但不能绕过会影响安全、scope、状态或证据链的门。

推荐 Gate Stack：

```text
Natural User Request
-> Router Gate
-> Project Root Gate
-> Context Discovery Gate
-> Lifecycle Session Gate
-> Context Enrichment Gate
-> Clarification Gate / Bug Evidence Gate
-> Change Brief Gate / Bug Brief Gate
-> Context Lock Gate
-> External Skill Bridge Gate
-> Execution Gate
-> Verification Gate
-> Knowledge Sync Gate
-> Artifact Sync Gate
-> Progress Dashboard Sync Gate
-> Review Gate
```

### Router Gate

识别用户意图，决定当前是 init、ingest、develop、fix、finish、review、resume 还是 unknown。Router Gate 必须保留用户真实目标，不因为项目还没初始化就忘掉用户最初想解决的问题。

### Project Root Gate

确定项目根目录。项目根目录必须足够覆盖源码、构建文件、Git 历史、共享文档和 `.llm-wiki`。如果存在多个候选根目录，询问用户。

### Context Discovery Gate

扫描配置的 source directories、docs、PRD、设计文档、日志、会议纪要和用户刚提供的材料，发现未索引或已修改的资料。Discovery 只负责发现和登记候选，不默认深读所有资料。

## Lifecycle Session Gate

创建或恢复 Change Brief、Bug Brief 或 Working Context。任何 develop、fix、finish、review 都应该绑定到一个会话；如果无法绑定，必须说明原因并创建临时 review context 或询问用户。

### Context Enrichment Gate

恢复 `.llm-wiki`、source proxy、module index、working context、git 状态和相关原始资料，选择 active / candidate / excluded sources，以及 active / read-only / candidate / excluded code scopes。

### Clarification Gate

用于需求和功能开发。在写计划或改代码前，确认目标、scope、out of scope、non-goals、验收标准、约束和关键缺口。Clarification Gate 可以桥接 brainstorming，但 brainstorming 不能替代 Lifecycle Session。

### Bug Evidence Gate

用于 bug 修复。在改代码前，记录 symptom、expected behavior、evidence、reproduction status、affected scope 和最近变更。未复现或证据不足时，不做大范围修复，除非用户明确接受风险。

### Change Brief Gate / Bug Brief Gate

把需求或 bug 的状态写入 `.llm-wiki/requirements/` 或 `.llm-wiki/bugs/`。计划、验收、scope、状态、风险和 open questions 必须能被后续 Agent 恢复。

### Context Lock Gate

进入 implementation plan 或执行阶段后锁定当前 Working Context。新增 source、扩大 scope、修改 read-only scope、替换计划或改变验收标准，都必须记录 scope change / plan deviation，并在需要时请求用户确认。

### External Skill Bridge Gate

调用外部 skills 或工具前，必须输出 Context Handoff。外部 skill 只能在 scoped context 内工作，不能绕过 Project Develop Copilot 的 scope、状态、验证和知识回写规则。

### Execution Gate

执行代码修改前确认：scope 已锁定、计划已确认、验收标准明确、必要的外部 skill 已完成前置工作。用户明确只讨论设计或方案时，不进入 Execution Gate。

### Verification Gate

完成实现后必须验证。验证可以是 test、compile、lint、manual verification，或者明确记录无法验证的原因和用户接受的残余风险。没有验证或明确限制，不得宣称完成。

### Knowledge Sync Gate

验证通过或限制被明确接受后，把真实变更同步回 `.llm-wiki`：requirement、bug、module、source proxy、working context、log。同步内容必须轻量，不写长篇实现叙事。

### Artifact Sync Gate

把设计文档、PRD、Change Brief、implementation plan、review 报告、测试报告、Superpowers spec/plan、OpenSpec change 等过程产物登记到 `.llm-wiki/artifacts/index.md`。Artifact Registry 是证据链索引，不是原文仓库。

### Progress Dashboard Sync Gate

如果项目启用了静态项目进度驾驶舱，finish 和 review 阶段必须检查页面是否反映当前状态、风险、任务卡片、证据链接和更新日志。页面不一致时，以源码、测试、`.llm-wiki`、artifact 和验证记录为准修正页面。

### Review Gate

交付、commit、PR 或合并前执行。检查代码风险、测试缺口、scope drift、wiki drift、artifact drift、dashboard drift、tool bridge consistency 和残余风险。Review Gate 输出 findings-first 结果。

## External Skill Bridge Contract

Project Develop Copilot 不应该重写所有能力。系统调试、TDD、计划执行、代码审查、浏览器验证、GitHub 检查、Java 编码安全等都可以由外部 skills 或工具承担。

但外部 skills 只能作为生命周期内的能力桥接，不能抢走项目生命周期主线。

职责边界：

```text
Project Develop Copilot owns lifecycle.
External skills own expertise.
```

Project Develop Copilot 负责：

- Router 和生命周期会话
- project root
- `.llm-wiki`
- Change Brief / Bug Brief
- active scope / read-only scope / excluded scope
- Context Lock 和 Scope Escalation
- Artifact Registry
- progress dashboard
- finish / review / sync

外部 skills 负责：

- brainstorming：需求澄清、方案讨论、权衡
- writing-plans：实现计划
- test-driven-development：测试先行纪律
- systematic-debugging：问题诊断纪律
- executing-plans：按计划执行
- verification-before-completion：完成前验证纪律
- requesting-code-review：额外审查视角
- browser / github / language-specific skills：具体工具或技术能力

桥接规则：

- 调用外部 skill 前必须先通过 Context Enrichment Gate。
- 外部 skill 必须收到 Context Handoff。
- 外部 skill 不得从零选择项目 scope。
- 外部 skill 不得把 candidate / excluded scope 升级为 write scope；升级必须回到 Project Develop Copilot。
- 外部 skill 不得覆盖用户决策、源码、测试、构建文件、原始需求或运行证据。
- 外部 skill 的产物必须通过 Return Handoff 回到 Lifecycle Session。
- 外部 skill 的重要产物必须登记为 artifact。
- 外部 skill 不得直接宣称项目完成；完成必须经过 Verification Gate、Knowledge Sync Gate 和 Review Gate。

如果用户直接触发了外部 skill，例如“用 systematic debugging 看这个 bug”，Project Develop Copilot 仍应先建立 lifecycle session，再把该 skill 作为 bridge 调用，最后把诊断、修复、验证和知识回写收回生命周期。

## Project Domain Skill Contract

Project Develop Copilot 的 domain skills 应参考 Superpowers / Thinking Skills 的 skill 写法，让 Router 能稳定判断何时使用、何时不使用、需要先读什么、拥有哪些 Gate、输出什么 handoff。

每个 project domain skill 不应只依赖 `description` 和文件名。它必须暴露足够的路由信号和边界说明。

建议结构：

```markdown
---
name:
description:
---

# Skill Name

## Purpose

## When to Use

## When Not to Use

## Owned Gates

## Required First Check

## Core Process

## Mode / Entry Selection

## Inputs

## Outputs

## Context Handoff

## Return Handoff

## Boundaries

## Common Mistakes
```

### Purpose

说明这个 skill 在 Project Develop Copilot 生命周期里负责什么，不负责什么。

### When to Use

列出 Router 可以识别的自然语言信号、项目状态信号和文件/证据类型。例如 bug、PRD、diff、finish、review、resume。

### When Not to Use

列出容易误触发的反例。例如用户只是轻量讨论设计时，不进入 `project-develop`；用户只是问某个文件位置时，不创建 Change Brief。

### Owned Gates

声明这个 skill 负责执行或检查哪些 Gates，例如 Context Enrichment Gate、Bug Evidence Gate、Knowledge Sync Gate、Review Gate。

### Required First Check

进入 skill 后第一件必须确认的事。例如：

- project root 是否明确。
- 是否已有 `.llm-wiki`。
- 是否已有 Lifecycle Session。
- 是否存在 active scope。
- 是否只是 lightweight-answer。

### Mode / Entry Selection

一个 skill 内部可以有轻量模式和完整模式。例如 `project-develop` 可以区分 requirement discussion、plan confirmation、execution；`project-review` 可以区分 quick diff review、full lifecycle review、Dolores-triggered review。

### Handoff 规则

所有会调用外部 skills 或被 Router 调用的 project skills，都必须支持 Context Handoff 和 Return Handoff。Handoff 必须保持短而结构化，不暴露长推理。

### Common Mistakes

每个 skill 都应该列出最容易导致生命周期割裂的错误。例如：

- 过早实现。
- 跳过 Context Enrichment Gate。
- 未创建 Change Brief / Bug Brief。
- 外部 skill 绕过 scope。
- finish 未同步 artifact。
- review 未检查 drift。

这个 contract 的目的不是让每个 SKILL.md 变重，而是让 Router 能读懂 domain skill 的触发边界，并让实现者知道每个 skill 在生命周期里的职责。

## Continuous Skill Evolution

Project Develop Copilot 不只是一组执行 skills，还需要持续进化机制。真实项目使用会暴露 routing mistake、gate skip、scope drift、artifact drift、dashboard drift、输出过重、过早实现、缺少验证等问题；这些问题应该进入可复盘、可评估、可最小修补的改进闭环。

持续进化层可以借鉴 `thinking-skills` 中的 `skill-evaluator` 和 `conversation-review` / Dolores，但对象从 Thinking Skills 的回答质量，转为 Project Develop Copilot 的生命周期质量。

Continuous Skill Evolution 默认不阻塞正常交付；只有用户明确要求复盘、出现高风险流程失败、或 Review Gate 发现流程级问题时，才进入 evaluator 或 Dolores。

### Project Skill Evaluator

Project Skill Evaluator 用于评估一次具体的 project skill failure、golden case candidate 或用户反馈。

触发场景：

- Lifecycle Router 选错 primary stage。
- Router 没有创建或恢复 Lifecycle Session。
- `project-develop` 过早进入实现，没有完成 Clarification Gate。
- `project-fix` 没有复现或诊断就修改代码。
- 外部 skill 绕过 Project Develop Copilot 的 scope 或状态主线。
- `project-finish` 没有同步 Change Brief、Bug Brief、Artifact Registry 或 progress dashboard。
- `project-review` 没有发现 scope drift、wiki drift、artifact drift 或 dashboard drift。
- 某次响应太长、太重、太像流程表单，破坏自然入口体验。
- 某次流程特别顺畅，值得保存为 golden case 或 eval。

Evaluator 输出：

```markdown
## Diagnosis

Case summary:
Failure or golden type:
Likely source: router / stage skill / external bridge / gate / reference doc / eval gap

## Eval Gap

Existing coverage:
New or updated eval:

## Patch Plan

Smallest useful change:
Files likely affected:
Overfitting risk:
Recommendation:
```

Evaluator 规则：

- 默认不直接重写 skill；先诊断、归因、提出最小 patch。
- 优先补一个 eval 或明确一个 gate 规则，而不是为单个 case 重写整个 skill。
- 区分 router 问题、stage skill 问题、external bridge 问题和 reference doc 问题。
- 不保存原始私人对话、客户资料、真实日志、凭据或敏感上下文；必要时只保存抽象案例。
- golden case 必须记录可复用行为，不记录普通表扬。

### Project Conversation Review / Dolores

Project Conversation Review 用于复盘完整项目对话轨迹。模式名可以沿用 Dolores，但它在这里关注的是 lifecycle trace，而不是普通回答流。

核心世界观：

```text
A project conversation is not only an answer stream. It is an observable lifecycle trace.
```

Dolores 检查：

- 用户从哪个自然入口进入。
- Router 是否正确识别 intent、primary stage 和 secondary bridge。
- 是否创建或恢复 Change Brief、Bug Brief 或 Working Context。
- 哪些 Gates 被执行、跳过或顺序错误。
- 外部 skills 是否在 scoped context 内工作。
- scope escalation 是否有证据和确认。
- implementation 是否过早开始。
- verification、Knowledge Sync、Artifact Sync、Dashboard Sync 和 Review 是否形成闭环。
- 哪些失败应该成为 failure case 或 eval。
- 哪些成功路径值得成为 golden case。

Dolores 输出：

```markdown
## Lifecycle Trace

## Routing And Gate Trace

## External Bridge Trace

## What Worked

## Failure Signals

## Eval Gaps

## Golden Signals

## Patch Strategy

## Dolores Note
```

Dolores 规则：

- 轻量复盘只给一两个关键改进点。
- 深度 Dolores 才展开完整 lifecycle trace。
- 不把普通总结伪装成 Dolores。
- 不直接 patch skills，除非用户明确要求进入修改阶段。
- 不记录原始敏感对话；只抽象为 eval candidate 或 failure pattern。

### Evolution Artifacts

持续进化需要轻量产物，但不应变成大型流程系统。

推荐目录：

```text
project-agent-copilot/project-develop-copilot/evals/
project-agent-copilot/project-develop-copilot/cases/failures/
project-agent-copilot/project-develop-copilot/cases/golden/
project-agent-copilot/project-develop-copilot/docs/improvement-loop.md
```

完整开发版本应先落地 reference 级持续进化约定，并预留 eval runner 扩展点。实现时优先覆盖这些 eval：

- 自然语言 bug 请求应进入 Router -> Lifecycle Session -> project-fix，而不是直接 systematic-debugging。
- 需求讨论请求不应直接进入实现。
- finish 缺少验证时不得宣称完成。
- review 应检查 Change Brief、Artifact Registry 和 dashboard drift。
- 外部 skill 输出必须通过 Return Handoff 回到 Lifecycle Session。
## LLM Wiki 合约

项目级 LLM Wiki 是 LLM 自己维护的索引层和归纳层，不是让用户手写的新文档系统。

规则：

- LLM Wiki 不替代 PRD、issue、design、代码和测试。
- LLM Wiki 不保存大段原始内容。
- LLM Wiki 只保存索引、摘要、关系、状态和缺口。
- 用户不需要手动维护 LLM Wiki。
- 当 wiki 与原始资料冲突时，以原始资料为准。

推荐目录：

```text
.llm-wiki/
  index.md
  log.md
  AGENTS.md

  ingest/
    index.md

  sources/
    xxx.md

  requirements/
    xxx.md

  bugs/
    xxx.md

  modules/
    xxx.md

  decisions/
    adr-xxxx.md

  code/
    entrypoints.md
    api-map.md
    data-model-map.md

  followups/
    index.md

  artifacts/
    index.md
```

## docs/ai-coding 迁移策略

很多项目已经存在旧版 `docs/ai-coding/`，它通常保存项目级或模块级的 AI coding context，例如：

```text
docs/ai-coding/
  contexts.md
  <context-scope>/
    project-profile.md
    architecture-summary.md
    coding-rules.md
    ai-context-sources.md
    feature-prompt-context.md
    open-questions.md
```

Project Develop Copilot 的目标不是长期并存两套上下文目录，而是在 `project init` 或 `project refresh` 阶段把旧上下文迁移到新的规范中。迁移后，`docs/ai-coding/` 应作为 legacy source 保留只读，后续逐步弃用。

职责边界：

```text
docs/ai-coding = 旧版项目/模块编码上下文
.llm-wiki = 新版项目知识索引、需求/bug 摘要、关系、状态和缺口
project-develop-copilot rules = 新版开发生命周期和编码上下文规则
```

迁移目标：

```text
docs/ai-coding/contexts.md
  -> .llm-wiki/modules/index.md

docs/ai-coding/<scope>/project-profile.md
  -> .llm-wiki/modules/<scope>/index.md 的项目画像 / scope 边界

docs/ai-coding/<scope>/architecture-summary.md
  -> .llm-wiki/modules/<scope>/architecture.md 的架构摘要

docs/ai-coding/<scope>/coding-rules.md
  -> .llm-wiki/modules/<scope>/rules.md 的本地编码规则摘要
  -> 或 project-develop-copilot 的 scope rules reference

docs/ai-coding/<scope>/ai-context-sources.md
  -> .llm-wiki/ingest/index.md
  -> .llm-wiki/sources/<source-proxy>.md

docs/ai-coding/<scope>/feature-prompt-context.md
  -> .llm-wiki/modules/<scope>/development.md 的开发起手检查
  -> project develop 的 Context Enrichment Gate 输入

docs/ai-coding/<scope>/open-questions.md
  -> .llm-wiki/modules/<scope>/open-questions.md 的 open questions
  -> .llm-wiki/log.md
```

迁移规则：

- 不直接删除、移动或重写旧 `docs/ai-coding/`。
- 迁移时保留来源路径，生成 source proxy 和迁移日志。
- 不复制大段正文，只抽取稳定规则、scope 边界、事实依据、open questions 和验证命令。
- 对旧文档中的历史状态、过时事实、乱码、prompt 占位符，迁移为 caution 或 open question，不提升为新规范。
- 当 `docs/ai-coding` 与源码冲突时，以源码、配置、构建文件和测试为准。
- 迁移完成后，在 `.llm-wiki/log.md` 记录 legacy migration。
- 可选：在 `docs/ai-coding/contexts.md` 顶部追加 deprecation note，但第一版不强制修改旧目录。

真实项目样式参考：

```text
docs/ai-coding/contexts.md
  -> dji-dock3-adapter

docs/ai-coding/dji-dock3-adapter/
  -> Core Workspace: dji-dock3-adapter
  -> Reference Area: dock-api
  -> Review status: draft
```

这种结构已经天然支持目录级 scoped context。迁移后，新体系继续保留 scope 隔离思想，但以 `.llm-wiki/modules/index.md` 和 `.llm-wiki/modules/<scope>/` 作为主要入口。

弃用原则：

- 新项目不再创建 `docs/ai-coding/`。
- 已有项目首次 `project init` 时执行 legacy discovery。
- 已有项目完成迁移后，新上下文写入 `.llm-wiki/`。
- 后续开发不再更新 `docs/ai-coding/`，除非用户明确要求兼容旧流程。

## Init Scope 隔离策略

一个仓库可能包含十几个微服务或模块。project init 不应该默认为每个微服务生成完整上下文，否则会很重，也容易产生噪声。

推荐策略：

```text
root registry first
selected scope bootstrap
other modules discovered only
```

project init 第一版必须创建或维护：

```text
.llm-wiki/index.md
.llm-wiki/log.md
.llm-wiki/AGENTS.md
.llm-wiki/ingest/index.md
.llm-wiki/sources/
.llm-wiki/cross-refs/index.md
.llm-wiki/modules/index.md
```

`.llm-wiki/cross-refs/index.md` 是跨项目引用层，只存本项目与外部项目的集成点索引、逻辑 project-id、远端 wiki anchor、契约摘要和验证状态。本机路径只允许放在 gitignore 的 `.llm-wiki/cross-refs/registry.local.json`，不进入团队共享 wiki。

对于多微服务仓库，`.llm-wiki/modules/index.md` 只登记模块清单和状态：

```markdown
# Modules Index

| Module | Path | Type | Context Scope | Status |
|---|---|---|---|---|
| dji-dock3-adapter | dji-dock3-adapter | adapter-service | docs/ai-coding/dji-dock3-adapter | active |
| dock-api | dock-api | reference-service | - | reference-only |
| user-center | user-center | service | - | discovered |
```

目录级隔离规则：

- `active` scope：本次 init/develop 明确选择的模块，可以生成详细 wiki/module 页面。
- `reference-only` scope：只作为参考区，不进入默认写入范围。
- `discovered` scope：只登记存在，不深读、不生成详细上下文。
- `excluded` scope：明确不参与当前项目开发上下文。

当用户开发某个模块时，再按需升级：

```text
discovered -> candidate -> active
```

升级到 active 后才创建或刷新：

```text
.llm-wiki/modules/<scope>/
.llm-wiki/working-context/<change-id>.md
```

这和 `docs/ai-coding/<context-scope>/` 的思想一致：上下文必须按作用域隔离，不能把一个 scoped context 自动套用到其他微服务。

## Cross-Project Refs

Cross-Project Refs 是 `.llm-wiki` 内的横切 evidence layer，不是新的子 skill，也不是中央同步服务。它解决的是：当前项目的需求或 bug 需要理解外部服务契约时，agent 如何从当前项目索引安全跳转到另一个本地项目的 `.llm-wiki` 继续取证。

核心约束：

- 当前项目只登记 integration point，不复制外部项目内容。
- `remote_project` 只写逻辑 project-id，不写本机路径。
- `remote_anchor` 相对外部项目 wiki 根目录，不写 `.llm-wiki/` 前缀。
- 本机路径只写入 gitignore 的 `registry.local.json`。
- 外部项目 wiki 和源码默认 read-only。
- `verification_status` 只记录 `draft`、`wiki-checked`、`source-verified`、`blocked`，不落盘 `stale`。
- 过期状态由 `last_verified` 和统一阈值实时派生。

进入外部项目之前必须经过 Cross-Project Boundary Gate：

```markdown
- remote_project:
- resolved_path:
- reason:
- scope: read-only
- anchors_to_read:
- verification_required:
```

`project-query` 可以用 wiki-only 证据回答“对面是谁”这类线索问题，但必须说明未做源码验证。`project-develop` 和 `project-fix` 如果要基于外部契约做实现或修复决策，必须对照外部源码完成 `source-verified`。

## Multi-Scope Change Protocol

Scoped context 用来隔离噪声，但不能变成上下文孤岛。复杂需求可能涉及多个微服务、模块或共享库，此时需要在 scoped context 之上创建 change-level 工作上下文。

分层模型：

```text
Project Root Context
  -> 全局仓库规则、模块索引、共享标准

Scoped Context
  -> 单个微服务/模块的编码上下文

Change Working Context
  -> 本次需求横跨哪些 scope，以及它们如何协作
```

核心规则：

```text
Scoped context owns local implementation rules.
Change working context owns cross-scope coordination.
```

触发条件：

- 需求明确涉及多个微服务或模块。
- API、消息、数据库、事件或配置契约跨服务变化。
- 调用链超过一个 active scope。
- 测试、构建或部署影响多个模块。
- CodeGraph 或源码分析显示存在直接跨 scope 依赖。

流程：

```text
candidate scopes
  -> read each scoped context only as needed
  -> create change working context
  -> assign scope roles and read/write permissions
  -> define cross-service contracts
  -> lock active scopes
  -> create per-scope implementation plan
  -> execute and verify per scope
  -> sync scope-level wiki and change-level wiki
```

建议记录到：

```text
.llm-wiki/working-context/<change-id>.md
```

示例：

```markdown
# Working Context: req-cross-service-xxx

## Active Scopes
- order-service
- payment-service
- notification-service

## Scope Roles
| Scope | Role | Write Permission |
|---|---|---|
| order-service | 需求入口和状态机 | write |
| payment-service | 支付确认与回调 | write |
| notification-service | 发送通知 | write |
| user-center | 查询用户信息 | read-only |

## Cross-Service Contracts
- order-service -> payment-service: payment request API
- payment-service -> order-service: payment callback/event
- order-service -> notification-service: notification command/event

## Read Policy
- Active scopes: 读取各自 scoped context + 相关代码
- Read-only scopes: 只读 API contract、DTO、README、接口定义
- Excluded scopes: 不读

## Write Policy
- 只允许修改 write scopes
- read-only scopes 需要升级确认后才能修改
```

计划拆分建议：

```text
Phase 1: Contract
Phase 2: scope A implementation
Phase 3: scope B implementation
Phase 4: scope C implementation
Phase 5: integration verification
```

冲突处理：

- 局部实现规则以各自 `docs/ai-coding/<scope>/coding-rules.md` 为准。
- 跨服务契约以 change working context 中确认的 contract 为准。
- 当 AI 文档、wiki、contract 与源码/测试冲突时，源码、接口定义、测试和运行结果优先。
- 新增 scope 进入 write 范围必须走 escalation，并记录原因。

finish 阶段需要同步两层 wiki：

```text
scope-level:
  .llm-wiki/modules/<scope>/

change-level:
  .llm-wiki/requirements/<change-id>.md
  .llm-wiki/code/cross-service-contracts.md
```

## Context Discovery 协议

project init 之后，用户可能手动把 PRD、设计文档、会议纪要、PDF、Word 或 Markdown 拷贝到项目目录。Copilot 不需要实时监听文件系统，但必须在关键入口执行 context discovery，避免新增资料对开发流程不可见。

触发入口：

```text
project ingest
project develop
project fix
project finish
project review
```

project init 应配置 source directories：

```text
docs/inbox
docs/prd
docs/design
docs/meeting
docs/feedback
```

也可以由项目自定义，例如：

```text
requirements/
product/
docs/
```

扫描流程：

```text
source directories
  -> compare with .llm-wiki/ingest/index.md
  -> detect new / changed / moved / deleted sources
  -> classify by type and likely topic
  -> present discovery summary
  -> ask confirmation before deep ingest
```

`.llm-wiki/ingest/index.md` 至少记录：

```text
path or url
type
size
modified_time
hash, optional
wiki_entry
status
last_ingested_at
```

默认策略：

- 新 Markdown：建议 summary ingest。
- 新 PDF/Word：建议 path index，深读前确认。
- 大文件或敏感文件：只做 path index。
- 已索引但修改过：提示需要 refresh source proxy。
- 已删除或移动：标记为 missing/moved，不直接删除 wiki 记录。

## Artifact Registry

Project Develop Copilot 不改变底层 skills 和工具的默认产物路径。Superpower、OpenSpec、PRD、设计文档、implementation plan、review 报告、测试报告等都可以保留在原位置。

`.llm-wiki/artifacts/index.md` 负责统一登记这些过程产物，避免文档散落后不可发现。

artifact 类型：

```text
prd
source
spec
design
plan
review
test-report
release-note
incident-report
```

最小字段：

```text
path or url
type
created_at
updated_at
related requirement / bug / module
status
last_checked
notes
```

规则：

- 不复制、不搬迁底层 artifact。
- 只登记路径、摘要、关系和状态。
- Superpower 生成的 `docs/superpowers/specs/` 和 `docs/superpowers/plans/` 文件必须登记为 artifact。
- 如果项目使用 OpenSpec，其 `openspec/changes/` 产物也登记为 artifact。
- Artifact Registry 与 `.llm-wiki/ingest/index.md` 互补：ingest 偏原始输入来源，artifacts 偏开发过程产物。

## project ingest 协议

project ingest 是临时资料进入项目开发体系的 intake 入口。

流程：

```text
source
  -> 引导确认
  -> 元信息提取
  -> 类型判断
  -> source proxy
  -> ingest/index.md
  -> 关联 requirement / bug / module / decision
  -> 可选 follow-up
```

支持来源：

- URL
- Markdown
- PDF
- Word
- 文本片段
- 会议纪要
- 客户反馈
- 日志或报错

处理优先级：

```text
Markdown > URL 摘要 > Word/PDF 摘要 > 路径索引
```

source proxy 最小字段：

```markdown
# Source: xxx

## Source
- type:
- path/url:
- captured_at:
- processing_mode:

## Summary

## Key Points

## Related
- requirements:
- bugs:
- modules:
- decisions:

## Gaps

## Next Action
```

## Follow-up 协议

project ingest 可以创建轻量 follow-up，但不把 wiki 变成项目管理系统。

`.llm-wiki/followups/` 只记录为什么要跟进、跟进什么、关联哪个 source。真正到点提醒可以交给 Codex automation、日历、GitHub issue 或团队工具。

follow-up 类型：

```text
triage
summarize
confirm
review
schedule
close
```

follow-up 最小字段：

```markdown
# Follow-up: xxx

## Source
- [[sources/xxx]]

## Reason

## Reminder
- due:
- action:
- status: pending

## Next Step
```

## 静态项目进度驾驶舱

Project Develop Copilot 后续可以维护一个单文件静态 HTML 页面，用于展示当前项目的开发进度。这个页面不是人工手写汇报页，而是由 LLM / skills 在项目生命周期中持续更新的可视化状态入口。

页面定位是“项目状态可视化索引”，不是新的事实源。源码、测试、设计文档、`.llm-wiki`、验收记录和 Artifact Registry 仍然是事实来源；HTML 只负责汇总、展示和帮助团队快速判断当前进度、风险、证据和下一步。

Dashboard 上任何关键状态都必须能回溯到 artifact、`.llm-wiki` 页面、验证记录或 git diff。不能只写自然语言状态，也不能让 dashboard 成为独立事实源。

建议页面分为四个区域：

1. 上半屏：项目驾驶舱

   展示项目目标、当前阶段、总体进度、关键风险、最近更新和下一步重点。它回答“这个项目现在走到哪里、最重要的问题是什么、下一步应该看哪里”。

2. 下半屏：开发流程看板

   按 `project-init`、`project-ingest`、`project-develop`、`project-fix`、`project-finish`、`project-review` 展示任务卡片、状态、维护方、阻塞项和验证结果。它回答“每个生命周期阶段还有哪些任务、哪些已经完成、哪些需要补证据”。

3. 文档证据区

   链接 README、DESIGN、references、acceptance cases、capability gap audit、相关 `.llm-wiki` 页面和验证记录。看板上的状态、风险和完成度必须能回溯到这些证据，避免页面变成过期装饰。

4. Skills 维护约定区

   说明哪些 skills 可以更新页面，更新哪些字段，更新后需要同步哪些日志、artifact 或 wiki 证据。建议约定 skills 只改页面顶部的数据区、任务卡片、风险列表和更新日志，不随意重写布局结构。

后续如果实现为 `progress.html`，建议优先采用单文件静态页：HTML、CSS、少量 JS 和页面数据放在同一个文件里，便于 GitHub 直接查看，也便于 LLM 单点维护。页面内部应把可维护数据集中在一个清晰的数据区，例如 `dashboardData`，让 skills 更新进度时尽量只改结构化数据，不碰展示逻辑。

维护规则：

- `project-init` 可以初始化页面、写入项目目标、阶段和初始证据链接。
- `project-ingest` 可以补充文档证据区和未处理资料状态。
- `project-develop` / `project-fix` 可以更新任务卡片、风险、阻塞项和验证计划。
- `project-finish` 可以在验证后更新完成度、结果摘要和更新日志。
- `project-review` 可以检查看板状态是否与 diff、`.llm-wiki`、Artifact Registry 和验证记录一致。
- 页面不得保存敏感信息、长原文、真实凭据、客户环境地址或生产日志正文。
- 页面状态不一致时，以源码、测试、`.llm-wiki`、artifact 和验证记录为准，页面必须被修正。

## Context Enrichment Gate

需求阶段必须触发。

目标不是写文档，而是让 Agent 在讨论和设计前先恢复项目上下文。

Quick context：

- `.llm-wiki/index.md`
- `.llm-wiki/project.md`，如果存在
- `.llm-wiki/ingest/index.md`
- 相关 requirement、source、module、decision 页面
- 当前 git 状态和最近提交
- 如果 `.codegraph/` 存在，使用它辅助定位相关模块和影响面

Deep context 触发条件：

- 跨模块需求
- 架构变化
- 数据模型/API/配置变化
- 业务规则不清
- 新 Agent 或新人接手
- wiki 信息不足或互相冲突

通过条件：

- 已总结当前上下文。
- 已列出已知事实、假设和缺口。
- 已提出需要用户确认的问题。
- 已判断是否进入 spec/change protocol。

## Scoped Working Context

全量资料和全量代码可以被索引，但当前任务只能激活局部上下文。Context Enrichment Gate 的关键产物不是“读了很多资料”，而是一个受控的 Working Context Set。

核心原则：

```text
ingested != activated
indexed != deep read
available != included in prompt
repository exists != all services are in scope
```

建议记录到：

```text
.llm-wiki/working-context/<change-id>.md
```

或简单场景：

```text
.llm-wiki/working-context/current.md
```

### Document Working Context

用于控制需求、PRD、设计、会议纪要和临时资料的上下文范围。

状态：

```text
discovered
indexed
summarized
candidate
active
excluded
archived
```

示例：

```markdown
# Working Context: req-a

## Active Sources
- [[sources/prd-a]]
- [[sources/design-d-auth-section]]

## Candidate Sources
- [[sources/prd-b]] - 同模块但目标不同，暂不深读

## Excluded Sources
- [[sources/prd-c]] - 主题不同，不进入当前任务

## Scope
本次只处理需求 A。

## Out of Scope
- 需求 B
- 需求 C
- 设计 D 中与 A 无关的部分
```

默认策略：

- Active sources 可以深读并进入当前任务上下文。
- Candidate sources 只读索引和摘要，不读正文。
- Excluded sources 不进入当前任务上下文。

### Code Working Context

用于控制代码、模块、微服务和共享库的阅读与修改范围。

示例：

```markdown
## Code Scope

### Active
- services/order
- services/payment

### Candidate
- libs/common-api
- services/auth

### Excluded
- services/inventory
- services/notification
- services/reporting

## Read Policy
- Active: 可以深读源码、测试、配置
- Candidate: 只读接口、README、API contract、调用边界
- Excluded: 不读，除非用户确认升级

## Write Policy
- Active: 可以修改
- Candidate: 默认不可修改
- Excluded: 禁止修改
```

### Escalation Rule

只有出现明确证据时，Candidate 才能升级为 Active。

升级条件示例：

- 编译失败指向 candidate 模块。
- 测试失败来自 candidate 服务契约。
- 需求明确要求跨服务链路。
- API 或数据结构变更必须同步共享库。
- CodeGraph 或源码分析显示存在直接影响面，并且当前任务无法绕开。

升级时 Copilot 必须说明原因并请求确认，或在用户已授权的自动执行模式下记录 escalation log。

```markdown
## Escalation Log
- 2026-05-28: libs/common-api 升级为 Active，因为新增字段需要更新共享 DTO。
```

## Spec/Change Protocol

不强制依赖 OpenSpec CLI，但必须有类似 OpenSpec 的变更建模。

Spec 回答：

- 为什么做
- 做什么
- 不做什么
- 验收标准是什么

Implementation plan 回答：

- 怎么改
- 改哪些文件
- 怎么验证

建议结构：

```text
.llm-wiki/requirements/<change-id>.md
```

或在项目需要时扩展为：

```text
.project/specs/changes/<change-id>/
  proposal.md
  design.md
  tasks.md
  acceptance.md
  result.md
```

## Context Lock

进入 implementation plan 之后，Working Context 默认锁定，防止开发过程中需求范围漂移。

锁定内容：

```text
active sources
active requirements / bugs
active services / modules
write scope
acceptance criteria
```

锁定后规则：

- 新发现资料默认进入 candidate，不自动进入 active。
- Candidate 模块默认只读，不自动进入可修改范围。
- 不得因为发现需求 B/C 就顺手实现。
- 扩大 scope 必须说明原因、影响和验证成本。
- 用户确认后才能更新 working context，并记录 change log。

示例记录：

```markdown
## Context Lock
- locked_at: 2026-05-28 15:30
- locked_by: project develop
- active requirement: req-a
- active services: service-a, service-b

## Scope Change Log
- 2026-05-28 16:10: service-common 升级为 active，因为 req-a 新增字段影响共享 DTO。
```

例外：

- emergency-fix 可以先修复，但 finish 阶段必须补齐 scope 记录和知识回写。
- investigation-only 不锁定 write scope，因为它不允许修改代码。

## Context Freshness Check

LLM Wiki 是索引和摘要层，可能落后于原始资料和代码。project develop、project finish、project review 必须检查上下文新鲜度。

检查项：

```text
source modified after source proxy
artifact modified after artifact registry entry
requirement summary older than PRD/spec
plan older than latest code changes
module summary mentions missing or moved code
bug status inconsistent with verification result
wiki links broken or pointing to moved files
```

处理策略：

- 发现过期 source：提示 refresh source proxy。
- 发现 plan 过期：要求重新确认 plan 或记录 deviation。
- 发现 module summary 过期：finish 阶段更新。
- 发现冲突：以原始资料、源码、测试和运行结果为准。

Context Freshness Check 不应该读取所有文件正文。优先使用路径、修改时间、大小、hash、git diff 和已有索引判断，必要时再深读。

## Bug Fix Protocol

Bug fix 不需要完整 PRD，但需要轻量闭环。

流程：

```text
bug source
  -> ingest if needed
  -> 查 wiki/context
  -> reproduce
  -> diagnose
  -> fix plan
  -> execute
  -> verify
  -> update bug/module wiki
```

bug 页面最小字段：

```markdown
# Bug: xxx

## Source

## Symptom

## Expected

## Scope

## Diagnosis

## Fix

## Verification

## Related
```

规则：

- 未复现或未形成诊断前，不直接大范围改代码。
- 修复后必须验证。
- 验证通过后才更新根因和修复摘要。

## Knowledge Sync Gate

开发完成且验证通过后必须触发。

目标是把实际变更登记回 LLM Wiki，使后续 Agent 能找到项目知识。

更新分级：

```text
none       纯内部实现，小修，不改变上下文
light      更新日志、需求状态、bug 状态或模块摘要
structural 更新模块边界、API、配置、数据模型、架构决策
```

必须更新：

- `.llm-wiki/log.md`
- 相关 requirement 或 bug 状态
- 相关 source proxy 的处理状态

按需更新：

- `modules/`
- `code/`
- `decisions/`
- `followups/`
- `index.md`

## 依赖策略

### Superpower skills

推荐依赖，不复制。

优先使用：

- brainstorming
- writing-plans
- executing-plans
- systematic-debugging
- test-driven-development
- verification-before-completion
- requesting-code-review

如果不存在，Project Develop Copilot 执行内置最小流程，并提示推荐安装。

### CodeGraph

可选增强。

规则：

- 存在 `.codegraph/` 时，用于代码理解、模块定位、影响面分析。
- 不存在时不阻塞，使用 `rg`、源码阅读和测试验证。
- CodeGraph 不能替代源码、测试和运行结果作为最终事实来源。

### OpenSpec CLI

可选增强。

规则：

- 项目已使用 OpenSpec 时，遵循其目录和命令。
- 项目未使用 OpenSpec 时，执行内置 spec/change protocol。
- 不因缺少 OpenSpec 阻塞项目开发流程。

## Skill 包建议结构

```text
role-copilot-skills/
  project-agent-copilot/
    README.md
    README.zh.md
    project-develop-copilot/
      SKILL.md
      references/
        lifecycle.md
        commands.md
        gates.md
        llm-wiki-contract.md
        spec-change-protocol.md
        ingest-protocol.md
        bugfix-protocol.md
        finish-protocol.md
        optional-tools.md
        templates/
          wiki-index.md
          source-proxy.md
          requirement-summary.md
          bug-summary.md
          followup.md
          finish-report.md
```

仓库结构遵循 `role-copilot-skills` 的两层模型：

```text
Agent Copilot role group
  -> installable role-specific skill
```

其中：

```text
project-agent-copilot = 项目研发角色组
project-develop-copilot = 项目开发生命周期 domain skill
```

未来可扩展：

```text
project-prd-copilot = PRD / 需求产品域 skill
project-ui-copilot = UI / 设计实现域 skill
project-review-copilot = 评审域 skill
project-release-copilot = 发布交付域 skill
project-test-copilot = 测试质量域 skill
```

`SKILL.md` 保持短小，只写：

- 角色定位
- 入口选择
- 必须遵守的 gate
- 依赖策略
- 何时读取 reference 文件

详细协议放入 references，避免主 skill 变成不可维护的超大提示词。

## 完整开发版本范围

这一版不再以割裂 MVP 为目标，而是直接实现完整 Project Develop Copilot 生命周期，再进行集中测试。原因是旧的 MVP 版本已经证明：只实现分散 child skills 会让用户重新面对入口选择问题，无法形成自然、连续、可恢复的项目开发体验。

完整开发版本必须包含：

- 顶层 Lifecycle Router / 总入口。
- 七个内部能力 skills：`project-query`、`project-init`、`project-ingest`、`project-develop`、`project-fix`、`project-finish`、`project-review`。
- Lightweight Answer Mode。
- Lifecycle Session：Change Brief、Bug Brief、Working Context。
- Context Discovery Gate。
- Context Enrichment Gate。
- Clarification Gate / Bug Evidence Gate。
- Context Lock Gate。
- External Skill Bridge Gate。
- Verification Gate。
- Knowledge Sync Gate。
- Artifact Sync Gate。
- Progress Dashboard Sync Gate。
- Review Gate。
- Project Domain Skill Contract。
- Continuous Skill Evolution：Project Skill Evaluator、Project Conversation Review / Dolores、eval / failure / golden case 约定。

完整开发版本需要创建或维护的项目 `.llm-wiki` 能力：

```text
.llm-wiki/index.md
.llm-wiki/log.md
.llm-wiki/AGENTS.md
.llm-wiki/ingest/index.md
.llm-wiki/sources/
.llm-wiki/requirements/
.llm-wiki/bugs/
.llm-wiki/working-context/
.llm-wiki/modules/index.md
.llm-wiki/artifacts/index.md
```

完整开发版本需要覆盖的用户入口：

- 从 PRD / 设计文档进入。
- 从 bug / 日志 / 错误信息进入。
- 从“继续上次”进入。
- 从“按计划执行”进入。
- 从 finish / 交付 / 是否完成进入。
- 从 review / 合并前检查进入。
- 从轻量设计讨论或文件定位进入，并正确保持 lightweight-answer。

完整开发版本暂缓但必须保留扩展点：

- 自动 CI 集成。
- 自动 CodeGraph 生成。
- 完整 OpenSpec CLI 兼容。
- 完整 eval runner。
- 自动创建 GitHub issue / PR automation。

开发顺序可以分阶段，但测试验收应以完整生命周期为对象，而不是只验证单个分散 skill。

## 流程例外模式

为了避免流程过重，Project Develop Copilot 应支持几个明确的轻量模式。

### trivial-change

适合拼写、注释、局部配置、小范围样式等低风险修改。

规则：

- 可以跳过完整 spec/change。
- 仍需检查 git diff 和验证方式。
- finish 阶段只做 light wiki sync 或记录不需要更新。

### investigation-only

适合只排查问题、阅读代码、分析方案，不修改代码。

规则：

- 可以读取 wiki 和代码。
- 不允许修改代码。
- 产出调查结论或候选方案。
- 可选登记到 `.llm-wiki/artifacts/index.md`。

### emergency-fix

适合线上故障或紧急阻断。

规则：

- 可以先走最短修复路径。
- 必须记录最小 bug 页面。
- 验证通过后必须补 Knowledge Sync Gate。
- 后续必须补根因、影响范围和回归测试建议。

## 团队采用等级

为了降低团队推广阻力，可以分阶段启用。

```text
Level 1: project init + project ingest + project finish wiki sync
Level 2: project develop/fix + scoped working context
Level 3: artifact registry + context freshness + review checks
Level 3.5: continuous evolution hooks + evaluator/Dolores artifacts
Level 4: CI/wiki lint/reminder automation + automated eval runner
```

完整开发版本建议达到 Level 3.5：总入口、生命周期会话、完整 Gate Stack、Artifact Registry、progress dashboard、review drift 检查，以及 evaluator / Dolores 的触发与记录机制形成闭环。团队稳定后再进入 Level 4，把 CI、wiki lint、提醒和自动 eval runner 接入自动化。

## 成功标准

- 用户只需要记住 project 入口。
- 临时资料不会丢失，都会进入 source proxy 和 ingest index。
- 需求阶段会先恢复上下文，而不是直接写代码。
- bug fix 有复现、诊断、验证和知识回写。
- Superpower、OpenSpec、plan、review 等过程产物都能从 Artifact Registry 找到。
- Working Context 被锁定后不会无意扩大需求范围。
- 过期 wiki 摘要能被 Context Freshness Check 发现。
- finish 后 wiki 能反映真实实现结果。
- wiki 内容轻量，不成为人工文档负担。
- Project skill 失败可以由 evaluator 复盘，并遵守最小 patch 与 eval-gap 纪律。
- 完整生命周期对话可以用 Dolores 模式复盘为可观察的 lifecycle trace。
- 可复用失败和黄金路径可以沉淀为抽象 eval 或 golden case，但不保存原始私人对话。
- 没有 superpower、CodeGraph 或 OpenSpec 时，流程仍可运行。
