# Project Develop Copilot LLM-first Deterministic Guardrails 架构 V3

日期：2026-08-01

状态：项目 Owner 已批准，当前架构基线

替代关系：本文件替代 2026-08-01 Runtime-first V2 作为当前架构判断。V2 和其 P0 实施计划保留为历史决策证据，但不得继续执行。

适用基线：`project-develop-copilot-v0.1.0` 及以后版本。

## 1. 执行结论

Project Develop Copilot 当前不建设统一 Project Lifecycle Runtime。

PDC 继续采用 Skill / LLM-first 架构。模型拥有语义判断、生命周期路由、流程压缩、工具选择、需求权衡和自我纠正权。Python 只保留现有已证明价值的小型工具，并在新的真实故障满足严格门槛时增加一个最小、局部、可移除的 Deterministic Guardrail。

架构北极星是：

> 不限制模型的上限，通过必要、最小、基于真实故障的确定性保护提高下限。

当前不实施：

- 统一 Runtime Core；
- 五个统一 lifecycle operations；
- JSON CLI 平台；
- Preview / transactional Commit 协议；
- MCP Adapter；
- 面向未知弱模型的兼容状态机。

## 2. 为什么修正 V2

V2 正确识别了路径安全、状态漂移、部分成功、跨平台和可测试性风险，也正确地把 MCP 从近期目标降为条件性适配器。

V2 的问题是把“存在一些确定性风险”推导成了“必须建设统一生命周期 Runtime”。这个推导缺少当前使用证据：

1. PDC 的主要使用对象是顶级模型；
2. 当前整体体验良好；
3. 偶发语义偏差通常能通过用户提醒和模型自我纠正解决；
4. 没有证据证明完整 Runtime 能带来净收益；
5. 没有对其他模型的真实使用和认证证据；
6. 固定状态机可能把模型可适应的协议变成必须绕行的旧约束。

因此，V3 不否认 V2 列出的风险，而是改变处理原则：

> 不围绕理论风险建设平台；只围绕已经发生、重复、高风险且可确定判断的故障增加局部保护。

## 3. 产品哲学

### 3.1 Ceiling-preserving

PDC 不得通过 Runtime 或状态机限制模型：

- 如何理解用户目标；
- 选择 query、develop、fix、review 或 lightweight-answer；
- 是否压缩、跳过或合并生命周期步骤；
- 是否创建或复用 Change Brief；
- 如何设计和实现功能；
- 哪类验证足以支持业务结论；
- 如何根据新证据推翻早期判断；
- 如何利用未来模型的新能力。

### 3.2 Floor-raising

PDC 可以保护与模型智力无关的机械边界：

- 明确的路径逃逸；
- 未授权跨项目写入；
- 格式和编码损坏；
- 确定性的 schema 错误；
- 已执行命令的 exit code 被错误解析；
- 可证明的重复副作用；
- 不可逆操作缺少明确授权。

这些保护类似类型检查、权限检查或 Git safety，不替代业务推理。

### 3.3 Evidence-triggered evolution

新的 Python 能力必须从失败证据生长，不能从架构想象生长。

PDC 不以“以后可能需要”“其他模型也许需要”“框架更完整”为实施理由。

## 4. 三类决策边界

| 区域 | 责任 | 默认行为 |
| --- | --- | --- |
| 模型自主区 | 意图、路由、语义、范围、方案、流程、验证判断、自我纠正 | LLM 自主，不增加 Python Gate |
| 软诊断区 | 状态可能漂移、证据可能不足、Wiki 可能陈旧、Artifact 可能缺失 | 返回 warning 和 evidence，由 LLM 判断 |
| 硬安全区 | 可确定的越权、破坏、路径逃逸、不可逆副作用或虚假机械成功 | 在副作用边界拒绝，并返回具体原因 |

规则默认进入模型自主区。

只有能证明规则完全不依赖业务语义时，才可以进入软诊断区；只有同时存在高风险副作用时，才可以进入硬安全区。

## 5. 模型自主区

以下能力必须继续留在 Skill / LLM：

- lightweight-answer 与 full-lifecycle 判断；
- project-query、develop、fix、review、finish 路由；
- 初始化后的 pending intent 恢复；
- Change Brief 创建、复用、拆分判断；
- candidate、inference、evidence 的业务解释；
- Scope、Acceptance 和架构权衡；
- 外部 Skill 选择；
- 测试与验证是否满足业务目标；
- 是否需要沉淀项目知识；
- 是否需要用户确认；
- 对用户反馈的即时自我纠正。

Python 不得把这些判断转成固定状态转换表。

## 6. 软诊断区

软诊断只观察，不自动改写生命周期状态。

适合的输出形式是：

~~~text
finding
severity
evidence
affected_paths
why_it_may_matter
~~~

软诊断可以发现：

- Dashboard 与 Flow Record 可能不一致；
- Artifact Registry 路径不存在；
- testing=done 没有可定位的验证引用；
- Wiki backlink 或 fingerprint 可能陈旧；
- Session Digest candidate 似乎被当成已确认事实；
- Project Graph edge 缺少 source-verified 证据。

软诊断不得：

- 自动把某个状态改成 done、pending 或 blocked；
- 自动创建 Change Brief；
- 自动决定哪个证据在业务上足够；
- 阻断普通讨论和开发；
- 把 warning 表述为任务失败。

## 7. 硬安全区

硬拒绝必须位于真实副作用边界，而不是路由或推理入口。

候选类型包括：

- resolved write path 明确逃出已授权 root；
- 当前 scope 明确为 read-only，但操作准备写入；
- destructive operation 没有对应用户授权；
- 写入协议要求原子替换，但临时文件/rename 步骤失败；
- 工具返回非成功 exit code，Agent 却准备声明该机械步骤成功；
- 同一个确定性请求可证明会产生重复不可逆副作用。

硬安全区不得扩张到：

- 需求是否合理；
- 设计是否最优；
- 测试数量是否足够；
- 是否应该创建文档；
- 是否应该进入某个生命周期阶段。

## 8. Guardrail 晋升门槛

一个新 Guardrail 必须同时满足全部条件：

1. 有真实失败记录，不是理论风险；
2. 在多个运行中重复，或单次后果足够严重；
3. 顶级模型在明确提醒后仍不能稳定自我纠正；
4. 后果涉及越权、破坏、不可逆副作用或虚假机械成功；
5. 判定不需要理解业务语义；
6. 最小 Python 实现明显小于完整 Skill/Runtime 平台；
7. 失败时存在清楚的说明、人工处理或原路径 fallback；
8. 前后 Eval 能证明正确性收益，且没有明显增加普通用户成本。

任一条件不满足，继续使用 Skill 规则、Eval 或软诊断。

## 9. Guardrail 设计约束

获准实现的 Guardrail 必须：

- 一个真实 failure case 对应一个独立 Change Brief；
- 默认局部接入，不成为所有 Skill 的统一入口；
- 只使用完成任务所需的最小输入；
- 返回 evidence，而不是业务结论；
- 能被禁用、替换或删除；
- 不要求普通用户手工运行；
- 不感知 Agent 产品名称或模型等级；
- 不引入后台服务；
- 不因已有两个或三个工具就自动合并成 Runtime；
- 在 CI 中只运行确定性离线测试，不自动调用 Agent/LLM。

## 10. 当前已有能力如何定位

| 能力 | V3 定位 |
| --- | --- |
| Initialization Gate | Skill 合同与 Eval；当前不下沉为统一 Runtime Gate |
| LLM Wiki Doctor | 独立只读诊断工具 |
| text/doc integrity checks | 仓库开发者质量门禁 |
| Black-box Eval sidecar | Developer-only 行为证据工具 |
| Task Control reducer | `project-task-dispatch` Domain-specific 控制面，不外推为全局生命周期 Runtime |
| Project Graph visualizer | 显式触发的 mechanical-artifact 工具 |

这些能力可以继续独立演进。共享实现只有在出现重复代码、共同故障和明确净收益后再评估。

## 11. 模型支持策略

PDC 优先面向具备较强自主规划、工具使用和自我纠正能力的前沿模型。

项目不承诺用固定工作流把较弱模型提升到顶级模型的表现。若未来需要支持新的模型或 Agent 产品：

1. 先运行该模型的真实 Eval；
2. 记录反复失败而不是推测能力；
3. 区分语义能力不足和机械错误；
4. 语义能力不足记录为模型支持边界；
5. 机械错误只有满足第 8 节门槛才新增 Guardrail。

PDC 不在运行时自动识别“强模型”或“弱模型”，也不维护模型特定工作流分支。

## 12. 用户成本边界

普通团队用户不需要：

- 安装 Runtime 或 MCP；
- 运行 Eval、Doctor 或 Guardrail CLI；
- 填写 Change Brief、Flow Record 或 JSON；
- 选择模型能力等级；
- 理解软诊断和硬安全的内部分类。

用户只在范围、风险、不可逆写入或真实业务决策需要时参与确认。

## 13. 演进路径

### S0：保持当前 PDC

- 继续使用 v0.1.0 的 Skill-first 架构；
- 继续通过顶级模型和现有 Eval 观察行为；
- 不实现 Runtime P0。

### S1：记录真实失败

- 失败进入 `cases/failures/` 或独立 Bug/Change Brief；
- 记录模型、提示、上下文、实际后果和能否自我纠正；
- 不因一次轻微偏差立即加 Gate。

### S2：单点 Guardrail

- 只有满足第 8 节全部门槛才实施；
- 一次只解决一个故障类别；
- 优先只读或副作用边界检查；
- 前后 Eval 验证净收益。

### S3：共享内核评估

只有三个以上已证明价值的 Guardrail 出现真实重复实现，并且共享内核能降低维护成本而不接管语义，才评估抽取小型 safety utilities。

### S4：重新考虑 Runtime

只有出现以下证据才重新打开 Runtime 讨论：

- 多个独立 Host 的真实复用需求；
- 重复的高风险状态破坏无法靠局部 Guardrail 解决；
- 局部工具已经形成稳定共同契约；
- 前后数据证明统一层降低总复杂度、用户成本和错误率；
- 顶级模型行为 Eval 证明没有能力上限损失。

即使满足这些条件，也先评估小型共享库，不自动进入 MCP。

## 14. 成功指标

V3 的成功不是 Skill 更长或工具更多，而是：

- 顶级模型仍能自由调整流程；
- 普通任务没有新增强制步骤；
- 轻微偏差仍可通过对话快速纠正；
- 高风险机械事故有更低发生率；
- 新增 Python 代码与真实失败数量相称；
- 没有为未使用模型维护兼容状态机；
- 每个 Guardrail 都有可定位 failure、前后证据和退出策略。

Token 和工具调用收益必须测量，不能从 Skill 变短或 Python 增加推断。

## 15. 非目标

- 消灭所有概率性偏差；
- 让所有模型表现一致；
- 把 PDC 改造成通用工作流引擎；
- 用 Python 判断业务语义；
- 强制每个任务创建生命周期状态；
- 统一所有现有脚本；
- 提前建设 JSON CLI 平台或 MCP；
- 用 Guardrail 代替用户确认；
- 为架构完整性增加没有失败证据的组件。

## 16. 最终判断

PDC 的核心竞争力是模型能够理解项目协议、根据上下文调整流程并自我纠正。这个能力会随着前沿模型提升而提升，不应被固定生命周期状态机封顶。

因此当前架构决策是：

> Skill / LLM 主导全部语义和流程；现有确定性工具保持独立；新的 Python Guardrail 只能由真实、高风险、重复且不可稳定自纠正的机械故障触发；当前不建设 Project Lifecycle Runtime、JSON CLI 平台或 MCP Adapter。

V3 提高的是系统安全下限，不是替模型决定如何工作。
