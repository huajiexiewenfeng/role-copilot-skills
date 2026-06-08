# 历史 Session 提纯与导入

修改本文档前，先阅读：

- `north-star.md`
- `llm-wiki-mvp.md`
- `ingest-mvp.md`
- `flow-record.md`
- `lifecycle-router.md`
- `scoped-working-context.md`

## 定位

历史 Session 提纯与导入，是 Project Develop Copilot 面向真实团队协作的上下文迁移能力。

它解决的问题是：

```text
很多需求、设计、Bug、方案、风险和验证过程，已经在同事与 AI 的历史会话中讨论过。
团队不希望重新开一个新 session 再从头讲一遍，也不希望这些有价值的上下文只停留在聊天记录里。
```

这个能力不是简单“导入聊天记录”，而是：

```text
历史会话
-> 提取项目相关内容
-> 过滤噪声和不确定内容
-> 生成候选 Session Digest
-> 用户确认导入范围
-> 写入项目 .llm-wiki
-> 关联需求、设计、执行计划、Bug、模块、Flow Record 和 dashboard
```

核心原则：

```text
聊天记录不是项目知识。
经过提纯、归纳、确认后的内容，才可以进入项目知识库。
```

## 适用场景

使用 `project-session-extract` 处理以下情况：

- 用户粘贴了一段历史 AI 对话，希望提取项目上下文。
- 同事已经和 AI 聊了很久，希望把里面有价值的结论沉淀到项目 `.llm-wiki`。
- 用户提供了历史 session 的 Markdown、文本、JSON 或导出文件。
- 用户说“不想重新开 session，希望把之前聊过的内容内化到项目 wiki”。
- 用户希望从旧会话中恢复需求讨论、设计决策、执行计划、Bug 分析或验证证据。
- 用户希望判断一段历史会话是否可以关联到已有 `flow_id`。
- 用户希望把之前会话中的好内容转为项目可查询、可追溯、可复用的上下文。

不使用该能力处理以下情况：

- 普通 PRD、设计文档、PDF、Word、Markdown、URL、日志或会议纪要，优先走 `project-ingest`。
- 用户只是询问当前项目 wiki 中已有内容，优先走 `project-query`。
- 用户已经明确要开发需求或修 Bug，优先进入 `project-develop` 或 `project-fix`，历史 session 只作为补充来源。
- 用户要求完整保存原始聊天记录，除非明确说明允许归档原文，并且确认没有敏感信息。

## 与 project-ingest 的关系

`project-ingest` 负责把项目源材料纳入 `.llm-wiki`，例如：

- PRD
- 设计文档
- Markdown
- PDF / Word
- URL
- 日志
- 会议纪要
- 客户反馈
- 临时资料

`project-session-extract` 负责从历史会话中提纯项目知识，例如：

- 需求澄清结论
- 设计取舍
- 实现计划
- Bug 分析链路
- 测试和验证记录
- 模块范围判断
- 未决问题
- 风险提醒
- 已经形成但尚未进入 wiki 的共识

两者的协作规则：

| 输入情况 | 处理方式 |
|---|---|
| 用户提供普通文档 | 使用 `project-ingest` |
| 用户提供历史聊天或 AI session | 使用 `project-session-extract` |
| 历史会话中提到一个 PRD 链接 | `project-session-extract` 提取链接，必要时建议再用 `project-ingest` 导入原始 PRD |
| 历史会话中已经形成一个执行计划 | 先提纯为候选 Session Digest，再判断是否关联 Change Brief / Bug Brief / Flow Record |
| 历史会话中包含大量日志 | 只提取症状、结论和证据，不复制大段日志；必要时建议日志单独走 `project-ingest` 的 cautious-summary |

重要边界：

```text
project-session-extract 不直接替代 project-ingest。
它只负责从会话里识别有价值的项目知识和 source candidates。
真正的原始文档归档，仍由 project-ingest 负责。
```

## 与 LLM Wiki 的关系

`.llm-wiki` 是项目级、代码级、生命周期级的共享知识库。

历史 Session 提纯后，写入标准目录：

```text
.llm-wiki/
  session-digests/
    README.md
    <session_digest_id>.md
```

`session-digests/` 的职责：

- 保存历史会话提纯后的项目知识摘要。
- 保存用户确认过的导入内容。
- 记录哪些内容没有导入以及原因。
- 作为需求、Bug、设计、执行计划、模块上下文的证据来源。
- 帮助后续 agent 快速理解“这个结论是从哪段历史会话沉淀来的”。

默认不保存完整原始聊天记录。

如果用户确认导入，允许更新以下 wiki 区域：

```text
.llm-wiki/session-digests/
.llm-wiki/requirements/
.llm-wiki/bugs/
.llm-wiki/modules/
.llm-wiki/contexts/
.llm-wiki/working-context/
.llm-wiki/sources/
.llm-wiki/artifacts/index.md
.llm-wiki/dashboard/progress.html
.llm-wiki/log.md
```

写入规则：

- 只有用户确认的内容才能作为项目事实写入需求、Bug、模块或 Flow Record。
- 未确认内容可以保存在 Session Digest 中，但状态必须标记为 `candidate`。
- 与当前代码、当前 wiki 或用户最新指令冲突的内容，必须标记为 `conflict`，不能直接覆盖。
- 过期尝试、临时猜测、聊天噪声、情绪表达、重复 prompt 不进入项目事实。

## 与 Flow Record 的关系

Flow Record 用一个稳定的 `flow_id` 串联：

```text
需求 / 设计 / 执行计划 / 开发 / 测试 / 归档
```

历史 Session 提纯可以为 Flow Record 提供证据，但不能滥建 Flow Record。

关联规则：

1. 如果历史 session 明确讨论的是已有需求或 Bug，复用已有 `flow_id`。
2. 如果历史 session 与已有 Flow Record 高度相似，但证据不充分，标记为候选匹配并询问用户。
3. 如果历史 session 中形成了一个明确交付物，才建议生成新的候选 `flow_id`。
4. 如果一段 session 涉及多个无关主题，拆成多个候选主题，不强行合成一个 Flow Record。
5. 如果一段 session 只是背景讨论，不创建 Flow Record，只写入 Session Digest。

禁止：

- 每个聊天主题都创建一个 Flow Record。
- 把 session id 直接当作 `flow_id`，除非整个 session 只围绕一个交付物。
- 用不确定的聊天结论覆盖已有需求状态。
- 把“曾经讨论过”当成“已经确认完成”。

## 输入处理

支持输入：

```text
粘贴的聊天内容
Markdown transcript
txt transcript
JSON export
历史 session 摘要
同事提供的 AI 对话整理
agent handoff
旧 session 生成的设计或计划文档
```

输入识别字段：

```text
source_type: pasted-chat | transcript-file | exported-json | handoff | summary | unknown
source_label: 稳定来源标识
source_date: 会话日期，未知则写 unknown
provided_by: 用户或同事，未知则写 unknown
access_mode: pasted | local-file | exported | linked
sensitivity: normal | cautious | sensitive
```

路径记录规则：

- 项目内文件使用仓库相对路径。
- 项目外文件不要把 `C:\Users\...`、`D:\workspace\...` 等个人绝对路径写入长期 wiki。
- 项目外来源使用稳定标签，例如 `external/session/<filename>`。
- 如果需要保留来源，可在 Session Digest 中记录“来源类型”和“来源标签”，不记录个人机器路径。

大文件、二进制、远程链接、疑似敏感内容，需要先确认再深度读取。

## 提纯规则

只提取长期有效的项目知识。

应该保留：

```text
需求目标
用户故事
验收标准
业务规则
设计决策
方案取舍
接口约定
数据结构
模块边界
微服务调用关系
代码路径
Bug 症状
根因证据
修复方案
测试方法
验证结果
上线或发布注意事项
风险
未决问题
下一步动作
源文档线索
```

应该过滤或标记为不导入：

```text
寒暄和闲聊
重复 prompt
无效尝试
临时猜测
已经被推翻的结论
过期计划
大段原始日志
密钥、token、cookie、私钥
个人隐私
客户敏感数据
无法找到证据的断言
和当前代码或 wiki 冲突但未确认的内容
```

每条提取结果都要分类：

```text
confirmed      用户或材料明确确认，可作为项目事实
candidate      有价值但未确认，只能作为候选上下文
conflict       与当前证据冲突，需要人工判断
stale          可能过期，不应直接使用
do-not-import  不应进入项目知识库
```

## 标准流程

### 1. 恢复项目上下文

先确定 `project_root` 和 `.llm-wiki`。

如果项目还没有 `.llm-wiki`：

- 用户只是想预览提纯结果，可以继续生成候选摘要。
- 用户想导入项目知识，必须先进入 `project-init`。

读取最小必要上下文：

```text
.llm-wiki/README.md
.llm-wiki/requirements/
.llm-wiki/bugs/
.llm-wiki/modules/index.md
.llm-wiki/artifacts/index.md
.llm-wiki/log.md
```

如果用户明确要求“先看当前项目有没有相关内容”，使用 `project-query` 组装 Project Context Pack。

### 2. 识别历史 session 来源

判断输入类型、时间、来源、敏感级别和可读范围。

输出来源摘要：

```text
Session source:
Source type:
Source label:
Session date:
Sensitivity:
Read mode:
```

### 3. 提取候选知识

从历史 session 中提取：

- 需求候选
- 设计候选
- 执行计划候选
- Bug / fix 候选
- 模块上下文
- 代码路径
- 接口和数据约定
- 测试和验证证据
- 风险和未决问题
- source candidates
- Flow Record 候选关联

提取时必须区分：

```text
事实
推断
用户确认
agent 建议
已经废弃的尝试
需要二次确认的内容
```

### 4. 生成候选 Session Digest

在写入 `.llm-wiki` 前，先向用户展示候选摘要。

候选摘要必须包括：

- 这段历史 session 的一句话总结。
- 可以导入的内容。
- 不建议导入的内容。
- 可能关联的需求、Bug、模块或 Flow Record。
- 需要用户确认的问题。
- 建议写入的 wiki 位置。

此阶段默认不写入 `.llm-wiki`，除非用户明确说“保存候选摘要”。

### 5. 用户确认导入

确认问题必须短，不做复杂表单。

推荐格式：

```text
我建议导入以下内容：
1. <需求或设计结论>
2. <Bug / fix 结论>
3. <模块上下文或风险>

不建议导入：
- <噪声或过期内容>

是否确认写入 .llm-wiki？
```

如果历史 session 涉及多个独立主题，应先让用户选择导入哪个主题：

```text
这段会话包含 3 个独立主题：A、B、C。
我建议先导入 A，因为它有明确需求和执行计划。是否先导入 A？
```

### 6. 写入 `.llm-wiki`

用户确认后，写入：

```text
.llm-wiki/session-digests/<session_digest_id>.md
```

必要时更新：

```text
.llm-wiki/log.md
.llm-wiki/artifacts/index.md
.llm-wiki/requirements/<flow_id>.md
.llm-wiki/bugs/<bug_id>.md
.llm-wiki/working-context/<flow_id>.md
.llm-wiki/modules/<scope>/sources.md
.llm-wiki/modules/<scope>/context.md
.llm-wiki/dashboard/progress.html
```

更新原则：

- 如果只是补充背景，只写 Session Digest 和 log。
- 如果确认关联已有需求，在需求文档中追加证据链接。
- 如果确认关联已有 Bug，在 Bug Brief 中追加症状、根因或修复证据。
- 如果确认是一个新的需求或 Bug，才创建新的 Change Brief / Bug Brief。
- 如果影响 dashboard 可视状态，刷新 dashboard。
- 如果只增加候选信息，不改变 dashboard 状态。

### 7. 导入后报告

完成后输出：

```text
Session source:
Digest path:
Imported items:
Linked flow_id:
Updated files:
Not imported:
Conflicts:
Next action:
```

## Session Digest 文档模板

```markdown
# Session Digest: <标题>

- Digest id: `<session_digest_id>`
- Source type: `<pasted-chat | transcript-file | exported-json | handoff | summary>`
- Source label: `<normalized-source-label>`
- Session date: `<known-or-unknown>`
- Extracted at: `YYYY-MM-DD`
- Import status: `candidate | confirmed | imported | partial | rejected`
- Related flow_id: `<flow_id-or-candidate>`
- Related scope: `<module/service/domain-or-unknown>`
- Sensitivity: `normal | cautious | sensitive`

## 一句话总结

<这段历史 session 对项目最有价值的结论>

## 可导入内容

| 内容 | 类型 | 状态 | 证据 | 建议写入位置 |
|---|---|---|---|---|

## 不建议导入内容

| 内容 | 原因 |
|---|---|

## 需求 / 设计候选

| 候选项 | 状态 | 建议 flow_id | 证据 | 下一步 |
|---|---|---|---|---|

## Bug / Fix 候选

| 候选项 | 状态 | 建议 bug_id | 证据 | 下一步 |
|---|---|---|---|---|

## Scope Context

- Active scope:
- Read-only scope:
- Candidate scope:
- Excluded scope:

## 设计决策

| 决策 | 状态 | 证据 | 关联目标 |
|---|---|---|---|

## 源材料线索

| Source candidate | 价值 | 建议动作 |
|---|---|---|

## 验证证据

| 证据 | 状态 | 关联目标 |
|---|---|---|

## 风险和未决问题

| 项目 | 类型 | 下一步 |
|---|---|---|

## 导入计划

| 内容 | 目标文件 | 动作 | 确认状态 |
|---|---|---|---|

## 导入记录

- Imported at:
- Imported by:
- Updated files:
- Dashboard refreshed: `yes | no`
```

## 命名规则

Session Digest id 使用：

```text
session-YYYYMMDD-<short-topic-slug>
```

示例：

```text
session-20260608-dji-live-capacity
session-20260608-smartgo-login-plan
session-20260608-media-file-callback
```

如果历史 session 有平台自带 id：

- 在 metadata 中记录原始 session id。
- 文件名仍保持项目可读。

如果一个历史 session 拆出多个独立主题：

```text
session-20260608-topic-a
session-20260608-topic-b
session-20260608-topic-c
```

不要把多个无关主题强行放进一个文件。

## 冲突处理

历史 session 可能和当前事实冲突。

冲突来源：

- 历史 session 比当前代码旧。
- 历史 session 比当前 `.llm-wiki` 旧。
- 用户后来改变了需求。
- agent 当时做过错误推断。
- 旧计划没有真正执行。

处理规则：

```text
当前代码 > 当前用户确认 > 当前 .llm-wiki > 历史 session > agent 推断
```

如果冲突：

- 不直接覆盖当前 wiki。
- 在 Session Digest 中标记 `conflict`。
- 摘要说明冲突点。
- 向用户提出一个短确认问题。

示例：

```text
历史 session 认为登录接口走 /mas/login，但当前代码和 wiki 显示使用 /api/auth/login。
是否将历史结论标记为过期，并只保留为背景证据？
```

## 安全规则

必须遵守：

- 默认不保存完整原始聊天记录。
- 不导入密钥、token、cookie、私钥、账号密码。
- 不导入个人隐私或客户敏感原文。
- 不复制大段日志，只提取症状和证据。
- 不把 agent 的猜测写成项目事实。
- 不把没有验证的方案写成已完成。
- 不把历史 session 的状态直接同步到 dashboard，除非有确认和证据。

敏感内容处理：

| 情况 | 处理 |
|---|---|
| 出现 token / cookie / 密码 | 脱敏，不写入原文 |
| 出现客户隐私 | 只写业务含义，不写具体身份 |
| 出现大段日志 | 提取症状、时间、错误类型、影响范围 |
| 出现疑似机密代码或配置 | 询问用户是否允许总结 |
| 用户要求完整保存原文 | 先提醒风险，再等待确认 |

## Dashboard 规则

Session Digest 本身不是进度。

只有当导入内容改变以下内容时，才刷新 dashboard：

- 新增或更新 Flow Record。
- 确认某个需求进入设计、执行、开发、测试或归档阶段。
- 新增可展示的文档证据。
- 更新 dashboard 需要展示的风险、阻塞或下一步。

如果只是保存历史上下文，不改变 dashboard 状态。

## 输出规范

提纯预览输出：

```text
我从这段历史 session 中提取到以下候选项目知识：

可以导入：
1. ...
2. ...

建议关联：
- flow_id:
- requirement:
- module:

不建议导入：
- ...

需要确认：
1. ...

是否确认写入 .llm-wiki/session-digests/？
```

导入完成输出：

```text
已导入历史 session 提纯结果。

Digest:
Linked flow_id:
Updated files:
Dashboard:
Not imported:
Next:
```

## 完成标准

一次历史 Session 提纯任务完成，需要满足：

- 已识别项目根目录和 `.llm-wiki` 状态。
- 已识别历史 session 输入来源和敏感级别。
- 已提取候选项目知识。
- 已过滤不应导入的内容。
- 已判断是否关联已有 Flow Record。
- 已展示候选导入摘要。
- 已获得用户确认，或明确停留在预览状态。
- 如果确认导入，已写入 `.llm-wiki/session-digests/`。
- 已更新必要的 wiki 索引、log、关联文档和 dashboard。
- 已报告导入内容、未导入内容、冲突和下一步。

这项能力的完成状态不是“读完聊天记录”，而是：

```text
历史会话中有价值的项目知识，已经变成可查询、可追溯、可复用、可选择导入的项目上下文。
```

## 后续实现要求

实现 `project-session-extract` skill 时，必须将本文档作为核心参考。

该 skill 的正式能力应包括：

- session 输入识别
- project root 解析
- `.llm-wiki` 状态检查
- 候选摘要生成
- 敏感信息过滤
- Flow Record 匹配
- 用户确认导入
- Session Digest 写入
- wiki 关联更新
- dashboard 条件刷新
- 导入结果报告

它不是试验性 MVP，而是 Project Develop Copilot 正式生命周期中的上下文迁移入口。
