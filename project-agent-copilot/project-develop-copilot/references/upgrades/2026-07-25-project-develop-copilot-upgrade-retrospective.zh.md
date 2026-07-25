# Project Develop Copilot 改造升级技术复盘

> 日期：2026-07-25
>
> 对应提交：[`3719ef2`](https://github.com/huajiexiewenfeng/role-copilot-skills/commit/3719ef2620fc231e19be95e5586c4069f7de37d5)
>
> 结论：已完成面向顶级模型的架构级适配；真实多模型行为认证仍需继续。

## 1. 改造目标

本次升级不是简单增加几个子 Skill，而是重新划分模型、Router、子 Skill、确定性脚本和 Eval 之间的职责。

目标是把 Project Develop Copilot 从“依赖模型理解一大段提示词的项目路由 Skill”，升级为一个：

- 不绑定具体 Agent 产品；
- 不和顶级模型自身的规划、推理及工具选择能力冲突；
- 具有明确执行前置条件和写入边界；
- 可以通过黑盒证据验证行为；
- 普通团队成员低感知、Skill Developer 可持续维护；
- 能够在出现失败后形成最小修复和回归用例；

的项目生命周期框架。

核心技术形态保持为：

```text
Skill 契约 + 顶级 LLM + Python/PowerShell 确定性脚本
```

## 2. 改造前的主要问题

### 2.1 Router 与顶级模型职责重叠

旧设计让 Router 承担了较多判断、规划和流程控制职责，容易与顶级模型自身的能力重复：

- 简单讨论也可能被升级成完整生命周期；
- 通用规划 Skill 可能在项目范围尚未确定前介入；
- Router、Superpowers 和具体子 Skill 之间可能重复路由；
- 模型已经能够完成的推理，仍被大量流程性提示词再次约束。

问题本质不是模型能力不足，而是 Skill 的控制粒度过重。

### 2.2 缺少强制初始化前置条件

最严重的问题是：当前项目没有 `.llm-wiki/` 时，某些依赖项目 Wiki 的 Skill 仍可能开始执行。

可能出现的错误行为包括：

- 直接创建 Change Brief、Bug Brief 或 Flow Record；
- 运行依赖 Wiki 的 Doctor、维护或开发流程；
- 在错误目录创建部分 `.llm-wiki`；
- 修改代码后才发现项目没有初始化；
- 把“Skill 已被模型选择”误认为“Skill 已具备执行条件”。

这是一个 P0 级生命周期前置条件漏洞。

### 2.3 评测依赖人工观察

仓库虽然已经有 32 个手动 P0 用例，但缺少可复用的行为证据采集和评分机制。

主要问题包括：

- 文件是否被越权修改依赖人工查看；
- 无法稳定区分 Router 失败、Skill 失败和 Agent Runtime 失败；
- “模型是否优先使用 Wiki”缺少可观察证据；
- 不同模型、不同 Agent 产品之间难以复用同一评测；
- 改动后容易只验证文档存在，而没有验证真实行为边界。

### 2.4 确定性任务被过度生命周期化

像 Project Graph HTML Viewer 这类任务，本质是：

```text
读取结构化输入 → 运行确定性脚本 → 生成单一产物 → 校验产物
```

如果仍然创建 Change Brief、计划、Flow Record、Finish Sync，会明显增加使用成本，并与任务复杂度不匹配。

## 3. 核心设计原则

### 3.1 Router 只负责路由与生命周期连续性

Project Develop Copilot Router 不替代具体子 Skill，也不替代模型完成实现。

Router 的核心职责收敛为：

1. 判断请求属于哪种模式；
2. 解析项目根目录；
3. 选择预期 primary stage；
4. 执行必要的前置 Gate；
5. 保存最小上下文；
6. 确保当前阶段结束后仍有明确的 next gate。

具体的开发、修复、查询、评审、维护和产物生成由对应子 Skill 负责。

### 3.2 使用最小状态变化原则

当前路由优先级被明确为：

```text
lightweight-answer
< read-only-query
< mechanical-artifact
< wiki-doctor
< dashboard-refresh
< wiki-maintenance
< full-lifecycle
```

含义是：

- 能直接回答就不创建项目状态；
- 能只读就不写入；
- 能用确定性脚本生成单一产物就不进入完整生命周期；
- 只有需求开发、Bug 修复、初始化、摄入、完成同步等任务进入 full lifecycle。

### 3.3 Skill 被触发不等于允许执行

不同 Agent Runtime 可能根据 Skill 名称或描述先完成 Skill 选择，Project Develop Copilot 无法完全控制这个外部选择过程。

本次改造把安全边界放在 Skill 执行入口：

> 即使某个 Skill 已经被模型触发，也必须先满足自己的 Initialization Gate、只读边界和写入边界。

这样可以把“选择是否准确”和“执行是否安全”拆成两个独立问题。

### 3.4 Agent 产品无关

我们没有依赖 Agent Runtime 的内部调用链、Hook 或白盒路由信息。

所有关键能力都通过以下可移植对象表达：

- Markdown Skill 契约；
- Git 工作区状态；
- Python 确定性断言；
- PowerShell 产物生成与验证；
- LLM-as-Judge 语义评分；
- JSON/Markdown 证据与报告。

## 4. 第一阶段：建立 Blackbox Eval

### 4.1 为什么采用黑盒评测

如果要检查 Agent 内部是否先走了某个 Router、是否按固定顺序执行 Gate，就必须绑定具体 Agent Runtime。

这与产品无关目标冲突。

因此评测改为观察最终可验证行为：

```text
准备 Git Fixture
    ↓
人工把问题交给任意 Agent
    ↓
保存 Agent 回答
    ↓
Python 收集 Git diff 和确定性证据
    ↓
LLM Judge 评估语义行为
    ↓
生成 PASS / PARTIAL / FAIL / NEEDS_REVIEW
```

### 4.2 Git 作为文件证据来源

没有自制 mtime/hash 快照系统，而是直接使用 Git：

- 运行前通过 `git status --porcelain` 确认 Fixture 干净；
- 运行后收集新增、修改、删除和 diff；
- 用例之间通过 Git 复位；
- 把 diff 作为确定性断言和 Judge 证据。

这减少了自定义状态管理代码，也提高了诊断能力。

### 4.3 两层判定模型

能够通过 Python 判断的行为不交给 LLM：

- 文件是否发生变化；
- 是否创建未跟踪文件；
- 回答是否引用指定 Wiki 路径；
- 是否出现禁止性的完成声明；
- Judge 输出结构是否有效；
- 证据引用是否闭合。

需要语义判断的行为才交给 LLM Judge：

- 路由选择是否符合用户意图；
- 模型究竟采信 Wiki 事实还是 Source 旧事实；
- 回答是否越权承诺实现；
- 两个 canary 同时出现时，模型把哪一个作为结论。

确定性硬失败不能被 Judge 覆盖。

### 4.4 Canary 陷阱设计

为了解决“无法证明 Agent 是否真的查看 Wiki”的黑盒局限，在 Fixture 中放置冲突事实：

- Source 中保留一个过时事实；
- `.llm-wiki` 中放置对应的正确事实；
- Prompt 确保至少有一组事实会被触及。

判定策略为：

- 只采信 Source canary：确定性失败；
- 只采信 Wiki canary：可作为正确行为证据；
- 两者都出现：交给语义 Judge 判断模型实际采信对象；
- 两者都未出现：不能据此证明查询路径，需要其他证据或 `NEEDS_REVIEW`。

每个 Fixture 使用多组 canary，降低单一信号失效风险。

### 4.5 Judge 可靠性补强

评审反馈推动了以下修正：

- `evidence_quote` 从严格原始子串调整为有限规范化匹配；
- 只折叠空白和统一受控标点，不允许任意语义改写；
- Judge 必须返回结构化 JSON；
- Judge 必须引用指定证据源；
- 缺失或不确定 Judge 结果进入 `NEEDS_REVIEW`；
- `NEEDS_REVIEW` 不进入通过率，并记录产生时间；
- 小型未跟踪文件保存内容，较大文件只保存摘要；
- Level A 与 Level B 声明边界明确；
- 先使用 canned answers 验证 Grader，再评估真实 Agent。

### 4.6 Eval 的用户边界

Eval 主要服务 Skill Developer，不进入普通团队用户的日常工作流。

普通用户仍然只需要自然语言描述项目任务。人工参与主要集中在：

1. 把测试 Prompt 交给目标 Agent；
2. 保存 Agent 回答；
3. 对少量 `NEEDS_REVIEW` 做最终确认。

## 5. 第二阶段：修复 Initialization Gate

### 5.1 根 Router 执行顺序

新的核心路径为：

```text
识别用户意图
    ↓
选择预期 primary stage
    ↓
解析项目根目录
    ↓
检查 <project_root>/.llm-wiki/
    ↓
不存在：保存 pending_intent 和 pending_primary_stage
    ↓
转交 project-init
    ↓
根据 project-init return handoff 恢复原任务
```

初始化之前明确禁止：

- 创建部分 `.llm-wiki`；
- 创建 Change Brief 或 Bug Brief；
- 创建 Flow Record；
- 写计划或工作上下文；
- 修改代码；
- 运行依赖 Wiki 的 Doctor 或维护流程；
- 把 Level 1/2 初始化误报为 feature-ready。

### 5.2 只读例外

如果用户明确要求只读或禁止写入：

- 报告项目还没有 `.llm-wiki`；
- 在运行 `project-init` 前征求确认；
- 可以提供 source-only `lightweight-answer`；
- 保留原始 `pending_intent`，避免用户后续初始化时重复描述任务；
- 不得宣称完成了生命周期或 Wiki 完整性检查。

### 5.3 `.llm-wiki` 存在性判定

发现 `.llm-wiki/` 目录本身，就表示项目已经存在 LLM Wiki。

不再把 `.llm-wiki/index.md` 作为唯一 sentinel。即使根 index 缺失，也应继续检查现有的：

- `README.md`
- `log.md`
- `modules/`
- `requirements/`
- `bugs/`
- `sources/`
- `working-context/`
- `artifacts/`
- `project-graph/`

## 6. 第三阶段：补齐子 Skill 门禁

### 6.1 `llm-wiki-doctor`

无 `.llm-wiki` 时：

- 不运行 Doctor；
- 不输出伪造或无意义的 Wiki 健康结果；
- 不创建部分目录；
- 保存原始诊断请求；
- 结构化转交 `project-init`；
- 初始化返回后继续原诊断目标。

### 6.2 `project-session-extract`

采用条件化初始化策略：

| 模式 | 无 Wiki 时的行为 |
|---|---|
| `brief-candidates` | 允许临时候选预览，不写文件 |
| `draft-context-digest` | 允许临时草稿，不写文件 |
| `save-context-digest` | 必须先执行 `project-init` |
| `promote-to-lifecycle` | 必须先执行 `project-init` |

预览模式不得：

- 声称 Session Digest 已导入；
- 创建 `session-digests/`；
- 对不存在的 Wiki 做重复检测；
- 创建 requirement、bug、Flow Record 或 dashboard 状态。

### 6.3 全子 Skill 初始化策略分类

新增契约测试，要求所有子 Skill 必须属于一种明确策略：

- `bootstrap`
- `stateful`
- `specialized`
- `mechanical`

新增子 Skill 如果没有被分类，测试会直接失败，从而避免未来再次出现隐式初始化漏洞。

## 7. 第四阶段：引入 Mechanical Artifact

### 7.1 为什么需要独立模式

`project-graph-visualize` 是确定性产物生成任务，不需要完整项目开发生命周期。

根 Router 新增：

```text
mechanical-artifact → project-graph-visualize
```

该模式不会创建：

- Change Brief；
- Flow Record；
- working-context；
- 计划；
- handoff；
- artifact registry；
- finish-sync 状态。

### 7.2 `project-graph-visualize` 边界

输入必须是已初始化 Base Graph，并满足：

```json
{
  "graph_role": "base"
}
```

默认输出：

```text
<base-root>/.llm-wiki/base-graph/graph.html
```

允许写入的只有目标 HTML。

只读输入包括：

- Base Graph `manifest.json`；
- `project-catalog.md`；
- `overview.md`；
- `registry.local.json`；
- 已登记业务项目的 `.llm-wiki/project-graph/*.md`。

实现包含：

- `SKILL.md`
- HTML 模板
- PowerShell Builder
- Graph Snapshot 模块
- Validator
- Eval
- Smoke Test

生成结果不得序列化本机 registry 绝对路径，也不得修改业务项目。

## 8. Superpowers 边界调整

Project Develop Copilot 不再依赖 Superpowers 的通用意图 Router 来维护项目生命周期。

当前关系为：

```text
Project Develop Copilot
    ├── 自己负责项目意图和生命周期
    ├── 调用明确的项目子 Skill
    └── 必要时把 Superpowers Skill 当作外部桥接能力
```

因此，针对 Superpowers 通用 Router 的优化通常不会直接破坏 Project Develop Copilot。

仍可能产生影响的情况包括：

- 修改了被 Project Develop Copilot 直接调用的具体 Skill；
- 修改了 Agent 全局强制规则；
- Superpowers 在 Runtime 层提前拦截项目请求；
- Context Handoff / Return Handoff 契约发生不兼容变化。

这不是完全解除依赖，而是把依赖收敛到明确、可检查的桥接边界。

## 9. 验证结果

本次采用先失败、再修复、最后完整回归的验证过程。

最终结果：

| 验证项 | 结果 |
|---|---:|
| Initialization Contract | 11/11 |
| 非 Blackbox 单元测试 | 77/77 |
| Blackbox Grader 测试 | 81/81 |
| Graph Visualizer Smoke | 18/18 |
| Skill 结构校验 | 通过 |
| 文本质量扫描 | 无 findings |
| 文档完整性扫描 | 无 findings |
| Doctor 同步检查 | 通过 |
| Git diff 检查 | 通过 |
| 源码版与本地安装版全树 SHA-256 对照 | 差异数 0 |

最终变更已经合入 GitHub `main`：

- Commit：[`3719ef2`](https://github.com/huajiexiewenfeng/role-copilot-skills/commit/3719ef2620fc231e19be95e5586c4069f7de37d5)

## 10. 架构收益

### 10.1 对顶级模型更友好

- 不再用过度细化的流程提示词替代模型推理；
- 模型负责理解意图，Router 负责执行边界；
- 确定性任务交给脚本；
- 子 Skill 各自拥有清晰的输入、输出和 Gate；
- 外部 Skill 作为桥接能力，而不是生命周期所有者。

### 10.2 普通用户使用成本可控

- 用户仍然通过自然语言进入；
- 不要求用户选择子 Skill；
- Eval 不进入普通工作流；
- 简单请求不会被强制创建生命周期状态；
- 初始化只在实际需要项目 Wiki 写入或完整生命周期时发生。

### 10.3 Skill Developer 获得可演进基础

- 失败能够被分类为 Router、Skill、Grader、Agent 或 Runtime 问题；
- 改动可以通过 Git 证据和语义证据回归；
- 新子 Skill 必须声明初始化策略；
- 新的行为漏洞可以形成 acceptance case 和 Eval；
- 不需要为不同 Agent 产品分别重写评测框架。

## 11. 剩余局限

### 11.1 尚未完成真实多模型认证

现有 81 项 Blackbox 测试主要验证 Grader、证据链和契约逻辑。

它们不能替代 GPT、Claude、Gemini 等模型在真实 Agent 环境中的行为运行。

当前准确状态是：

> 架构级顶级模型适配已经完成，真实跨模型行为认证仍待完成。

### 11.2 无法完全控制首次 Skill 选择

Agent Runtime 可能先触发某个 Skill。当前能够保证的是：

- Skill 执行前仍需通过 Gate；
- 不满足条件时必须停止或转交；
- 错误触发不应继续演变成越权写入。

### 11.3 外部全局规则仍可能干扰

更高优先级的 Agent 产品规则、系统提示或 Superpowers 全局约束仍可能影响最终行为。

### 11.4 Eval 保留 Human-in-the-loop

Agent 回答采集仍由人工完成。这是保持 Agent 产品无关的设计选择，不是遗漏。

### 11.5 Visualizer 当前只面向 Base Graph

它不是任意业务项目 `.llm-wiki` 的通用可视化工具。该限制用于保持输入结构和写入边界确定。

## 12. 后续建议

下一阶段不建议继续扩大框架复杂度，而应进行真实模型认证。

建议：

1. 选择团队实际使用的 2–3 个顶级模型；
2. 固定 Agent 产品、模型版本和运行参数；
3. 优先运行初始化、只读边界、路由和越权写入相关 P0 用例；
4. 使用现有 Blackbox Grader 收集统一证据；
5. 记录模型间的路由差异，而不是立即为单次失败增加规则；
6. 只有可重复失败才进入最小 Skill Patch；
7. 将修复后的失败样本加入 acceptance case 和回归 Eval。

重点观察：

- 是否把轻量讨论错误升级为完整生命周期；
- 没有 `.llm-wiki` 时是否先初始化；
- 是否正确选择主要子 Skill；
- 是否提前调用外部规划或实现 Skill；
- 是否越权写入文件；
- 是否提前声明完成、验证或归档；
- 是否优先使用 Wiki，并在 Wiki 不足或过期时回到源码验证。

## 13. 总结

这次升级完成了一个关键架构转向：

> 从“通过更多提示词控制模型”，转向“让模型负责理解，让契约负责边界，让脚本负责确定性，让 Eval 负责证明改进”。

当前 Project Develop Copilot 已具备：

- 面向顶级模型的职责划分；
- 强制初始化执行边界；
- 低成本自然语言入口；
- 项目生命周期连续性；
- 确定性机械产物通道；
- Agent 产品无关的黑盒评测基础；
- 可通过回归用例持续进化的工程结构。

后续工作的重点应从“继续设计框架”转向“用真实模型运行证据完成认证”。
