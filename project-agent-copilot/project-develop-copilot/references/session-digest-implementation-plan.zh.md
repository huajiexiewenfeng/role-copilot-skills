# 历史 Session 提纯与导入执行计划

> **For agentic workers:** 执行本计划前，必须先阅读 `references/session-digest.md`、`references/north-star.md`、`references/flow-record.md`、`references/lifecycle-router.md`。本计划目标是交付正式可用的 `project-session-extract` skill，不是试验性 MVP。

**Goal:** 将“历史 session 上下文归纳、提纯、确认导入 `.llm-wiki`”能力落成 Project Develop Copilot 的正式生命周期入口。

**Architecture:** 新增 `project-session-extract` 子 skill，负责历史聊天和 session transcript 的提纯；通过根 router 接入自然语言入口；通过 `.llm-wiki/session-digests/` 保存确认后的提纯结果；必要时关联 requirement、bug、module、working-context、Flow Record、dashboard。

**Tech Stack:** Codex / agent skills Markdown, `.llm-wiki` Markdown protocol, Flow Record, static dashboard, optional `project-query` / `project-ingest` / `project-develop` / `project-fix` handoff。

---

## 目标效果

完成后，用户可以这样使用：

```text
把这段历史 AI session 提取成项目上下文，先给我看候选导入内容。
```

或者：

```text
同事之前和 AI 聊了这个需求，帮我提纯后导入当前项目的 llm-wiki。
```

skill 应该完成：

```text
历史 session
-> 识别项目根目录和 .llm-wiki
-> 判断输入类型和敏感级别
-> 提取候选项目知识
-> 过滤噪声和敏感内容
-> 匹配已有 requirement / bug / Flow Record / module
-> 展示候选 Session Digest
-> 等待用户确认
-> 写入 .llm-wiki/session-digests/
-> 更新必要 wiki 关系和 log
-> 必要时刷新 dashboard
```

用户不需要维护复杂表单。LLM 负责归纳、匹配、建议导入位置和维护 wiki，用户只负责确认导入范围。

---

## 文件结构

### 新增文件

- `project-agent-copilot/project-develop-copilot/project-session-extract/SKILL.md`
  - 历史 session 提纯入口 skill。
  - 负责输入识别、候选摘要、确认导入、wiki 写入规则和 handoff。

- `project-agent-copilot/project-develop-copilot/references/session-digest-implementation-plan.zh.md`
  - 本执行计划。

### 修改文件

- `project-agent-copilot/project-develop-copilot/SKILL.md`
  - 根 router 增加历史 session / transcript / conversation 导入路由。

- `project-agent-copilot/project-develop-copilot/project-init/SKILL.md`
  - init / refresh 支持 `.llm-wiki/session-digests/` 标准目录。

- `project-agent-copilot/project-develop-copilot/project-ingest/SKILL.md`
  - 明确普通文档走 ingest，历史聊天走 `project-session-extract`。

- `project-agent-copilot/project-develop-copilot/project-query/SKILL.md`
  - 查询项目上下文时纳入 `session-digests/` 作为证据来源。

- `project-agent-copilot/project-develop-copilot/project-develop/SKILL.md`
  - 开发需求时，如果历史 session 已有确认的设计或计划，可作为 active source / candidate source。

- `project-agent-copilot/project-develop-copilot/project-fix/SKILL.md`
  - 修 Bug 时，如果历史 session 包含症状、根因、修复尝试或验证证据，可作为候选 bug evidence。

- `project-agent-copilot/project-develop-copilot/project-finish/SKILL.md`
  - finish 时可将本次真实执行结果反向补充到相关 Session Digest 的导入状态或后续状态。

- `project-agent-copilot/project-develop-copilot/project-review/SKILL.md`
  - review 时检查 Session Digest 是否被错误当成项目事实、是否存在未确认导入或冲突未处理。

- `project-agent-copilot/project-develop-copilot/README.zh.md`
  - 用户文档增加历史 session 提纯入口说明。

- `project-agent-copilot/project-develop-copilot/README.md`
  - 英文说明补充简短入口描述。

### 本地安装同步

实现完成后，同步到本地安装目录：

```text
C:\Users\admin\.codex\skills\project-develop-copilot\
C:\Users\admin\.codex\skills\project-session-extract\
C:\Users\admin\.codex\skills\references\
```

如果本地安装采用扁平化结构，需要保证 `project-session-extract/SKILL.md` 可以找到相邻或上级 `references/session-digest.md`。

---

## Task 1: 新增 project-session-extract skill

**Files:**

- Create: `project-agent-copilot/project-develop-copilot/project-session-extract/SKILL.md`

**Purpose:** 让历史 session 提纯成为正式可触发的子 skill，而不是只停留在设计文档。

- [ ] Step 1: 创建 skill frontmatter。

```yaml
---
name: project-session-extract
description: Use when extracting, summarizing, distilling, reviewing, or importing historical chat/session context into a project .llm-wiki, including pasted conversations, transcript files, exported AI sessions, colleague chats, old agent handoffs, or conversation summaries.
---
```

- [ ] Step 2: 写入 Purpose。

```markdown
# Project Session Extract

## Purpose

Extract durable project knowledge from historical AI or team chat sessions, then let the user confirm what should be imported into `.llm-wiki`.

This skill does not import raw chat by default. It creates a candidate Session Digest first, filters noise and sensitive content, maps useful context to project wiki targets, and writes only confirmed knowledge.
```

- [ ] Step 3: 写入 Required Shared References。

```markdown
## Required Shared References

Read these role-level references:

- `../references/session-digest.md`
- `../references/north-star.md`
- `../references/llm-wiki-mvp.md`
- `../references/flow-record.md`
- `../references/lifecycle-router.md`
- `../references/scoped-working-context.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root. If no shared `references/` directory is available and the user wants to write `.llm-wiki`, stop and tell the user the child skill install is incomplete.
```

- [ ] Step 4: 写入 When to Use / When Not to Use。

必须覆盖这些触发语义：

```text
历史 session
旧会话
聊天记录
transcript
conversation
同事和 AI 聊过
提纯上下文
导入 llm-wiki
恢复之前讨论的结论
```

必须明确普通 PRD / PDF / Word / Markdown / URL / logs 走 `project-ingest`。

- [ ] Step 5: 写入 Workflow。

Workflow 必须包括：

```text
1. Resolve project root and .llm-wiki.
2. Identify session source.
3. Classify sensitivity.
4. Read minimal wiki context.
5. Extract candidate project knowledge.
6. Match requirement / bug / module / Flow Record.
7. Produce candidate Session Digest preview.
8. Ask for concise import confirmation.
9. Write .llm-wiki/session-digests/<session_digest_id>.md after confirmation.
10. Update related wiki files only when necessary.
11. Report imported / not imported / conflicts / next action.
```

- [ ] Step 6: 写入 Output Format。

预览输出必须长这样：

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

导入完成输出必须长这样：

```text
已导入历史 session 提纯结果。

Digest:
Linked flow_id:
Updated files:
Dashboard:
Not imported:
Next:
```

- [ ] Step 7: 验收。

检查：

```powershell
Get-Content project-agent-copilot/project-develop-copilot/project-session-extract/SKILL.md
```

预期：

- frontmatter 存在。
- `project-session-extract` 名称正确。
- 引用了 `session-digest.md`。
- 明确“先候选摘要，后确认导入”。
- 明确不默认复制完整聊天原文。

---

## Task 2: 根 router 接入历史 session 路由

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/SKILL.md`

**Purpose:** 用户不用记住新 skill 名称，只要自然表达“把历史聊天提纯导入 wiki”，router 就能转入 `project-session-extract`。

- [ ] Step 1: 在 `When to Use` 增加触发场景。

增加类似内容：

```markdown
- Extracting, distilling, reviewing, or importing historical AI/team chat sessions, transcript files, old conversation summaries, or colleague AI discussions into project `.llm-wiki`.
```

- [ ] Step 2: 在 `Owned Gates` 增加 Session Context Import Routing Gate。

```markdown
- Session Context Import Routing Gate when the user wants to turn historical chat/session context into project-local `.llm-wiki` knowledge.
```

- [ ] Step 3: 在 `Core Process` 分类中增加：

```markdown
   - historical session extraction / session digest import
```

- [ ] Step 4: 在 `Mode / Entry Selection` 表格中增加一行。

```markdown
| User provides or references historical AI/team chat, session transcript, old conversation summary, colleague AI discussion, or asks to distill/import previous session context into `.llm-wiki` | session-context-import | `project-session-extract` |
```

- [ ] Step 5: 在 `Outputs` 增加 session-context-import 输出。

```markdown
For session-context-import:

- candidate Session Digest preview
- import recommendation
- related Flow Record / requirement / bug / module candidates
- confirmation question before `.llm-wiki` writes
- imported digest path and updated wiki files after approval
```

- [ ] Step 6: 验收。

执行：

```powershell
Select-String -Path project-agent-copilot/project-develop-copilot/SKILL.md -Pattern "project-session-extract","session-context-import","Session Context Import"
```

预期三类关键词都存在。

---

## Task 3: project-init 支持 session-digests 标准目录

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/project-init/SKILL.md`

**Purpose:** 项目初始化或 refresh 后，`.llm-wiki` 能容纳历史 session 提纯结果。

- [ ] Step 1: 在标准目录结构中加入：

```text
.llm-wiki/session-digests/
  README.md
```

- [ ] Step 2: 在 init / refresh 说明中加入：

```markdown
Create or preserve `.llm-wiki/session-digests/` for confirmed historical session digests. Do not scan it as raw source material; treat it as distilled project evidence.
```

- [ ] Step 3: 在 refresh 规则中加入：

```markdown
When `.llm-wiki/session-digests/` exists, include it in evidence discovery for project context, but do not promote candidate digest items to project truth without explicit confirmation.
```

- [ ] Step 4: 验收。

```powershell
Select-String -Path project-agent-copilot/project-develop-copilot/project-init/SKILL.md -Pattern "session-digests","historical session"
```

预期能看到目录和 refresh 规则。

---

## Task 4: project-ingest 增加边界提示

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/project-ingest/SKILL.md`

**Purpose:** 避免把历史聊天当成普通资料 ingest，也避免 `project-session-extract` 替代真实 source ingest。

- [ ] Step 1: 在 Purpose 或 Workflow 前增加 Relationship to Session Extract。

```markdown
## Relationship to Project Session Extract

Use `project-session-extract` instead of `project-ingest` when the input is a historical AI/team chat, transcript, exported session, colleague conversation, or old agent handoff.

If a session contains real PRD, design document, URL, log, or meeting note links, `project-session-extract` should identify them as source candidates. Confirmed source documents may then be ingested through `project-ingest`.
```

- [ ] Step 2: 在 Manual Inbox 规则旁边补充：

```markdown
Manual copied transcript files may be routed to `project-session-extract` when their content is primarily conversation rather than source documentation.
```

- [ ] Step 3: 验收。

```powershell
Select-String -Path project-agent-copilot/project-develop-copilot/project-ingest/SKILL.md -Pattern "project-session-extract","transcript","conversation"
```

---

## Task 5: project-query 纳入 Session Digest 证据

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/project-query/SKILL.md`

**Purpose:** 后续用户查询项目上下文时，确认导入的历史 session 摘要能被发现。

- [ ] Step 1: 在查询来源中加入：

```text
.llm-wiki/session-digests/
```

- [ ] Step 2: 在 Project Context Pack 输出中加入：

```markdown
- Related session digests:
```

- [ ] Step 3: 增加查询规则：

```markdown
Session Digests are supporting evidence. Treat `candidate` items as possible context, not confirmed project truth. Prefer current code, current user confirmation, and current requirement/bug pages when conflicts exist.
```

- [ ] Step 4: 验收。

```powershell
Select-String -Path project-agent-copilot/project-develop-copilot/project-query/SKILL.md -Pattern "session-digests","Related session digests","supporting evidence"
```

---

## Task 6: project-develop / project-fix / project-finish / project-review 串联使用规则

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/project-develop/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-fix/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-finish/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-review/SKILL.md`

**Purpose:** 让历史 session 提纯结果贯穿开发生命周期，而不是孤立归档。

- [ ] Step 1: `project-develop` 增加规则。

```markdown
When confirmed Session Digests exist for the active requirement, treat them as supporting source evidence. Use them to recover prior requirement discussion, design choices, acceptance criteria, scope decisions, and plan candidates. Do not treat candidate or conflict items as confirmed without user confirmation.
```

- [ ] Step 2: `project-fix` 增加规则。

```markdown
When confirmed Session Digests exist for the active bug or incident, use them as supporting evidence for symptoms, failed attempts, suspected root causes, reproduction notes, and verification history. Mark stale or conflict items before relying on them.
```

- [ ] Step 3: `project-finish` 增加规则。

```markdown
When finishing work linked to a Session Digest, update the related requirement/bug/Flow Record first. If the digest had candidate items that are now confirmed or rejected by implementation evidence, record that outcome in the digest or log when useful.
```

- [ ] Step 4: `project-review` 增加规则。

```markdown
Review whether Session Digest content was promoted correctly:

- candidate items are not written as project truth
- conflicts are not silently overwritten
- dashboard cards do not claim progress from unconfirmed session memory
- linked flow_id values match actual requirement or bug evidence
```

- [ ] Step 5: 验收。

```powershell
Select-String -Path project-agent-copilot/project-develop-copilot/project-develop/SKILL.md -Pattern "Session Digests"
Select-String -Path project-agent-copilot/project-develop-copilot/project-fix/SKILL.md -Pattern "Session Digests"
Select-String -Path project-agent-copilot/project-develop-copilot/project-finish/SKILL.md -Pattern "Session Digest"
Select-String -Path project-agent-copilot/project-develop-copilot/project-review/SKILL.md -Pattern "Session Digest"
```

---

## Task 7: README 文档补充用户入口

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/README.zh.md`
- Modify: `project-agent-copilot/project-develop-copilot/README.md`

**Purpose:** 团队成员能知道这个能力怎么用，但不需要学习复杂术语。

- [ ] Step 1: `README.zh.md` 增加一节。

```markdown
## 历史 session 提纯

如果同事已经和 AI 聊过很久，不需要重新开一个 session 从头讲。

可以直接说：

```text
把这段历史 session 提取成项目上下文，先给我看候选导入内容。
```

Project Develop Copilot 会先生成候选 Session Digest，标出可以导入、不建议导入、可能关联的需求/Bug/Flow Record。只有你确认后，才会写入 `.llm-wiki/session-digests/` 并更新相关项目上下文。
```

- [ ] Step 2: `README.md` 增加英文短说明。

```markdown
## Historical Session Extraction

Use this when a teammate already discussed useful project context with an AI assistant. The copilot distills the old session into a candidate Session Digest and imports only confirmed knowledge into `.llm-wiki`.
```

- [ ] Step 3: 验收。

```powershell
Select-String -Path project-agent-copilot/project-develop-copilot/README.zh.md -Pattern "历史 session 提纯","Session Digest"
Select-String -Path project-agent-copilot/project-develop-copilot/README.md -Pattern "Historical Session Extraction","Session Digest"
```

---

## Task 8: 本地安装同步

**Files:**

- Copy from repo to local installed skills:
  - `project-session-extract/`
  - root `SKILL.md`
  - updated child skill `SKILL.md` files
  - `references/session-digest.md`
  - `references/session-digest-implementation-plan.zh.md`

**Purpose:** 用户能在本地 Codex 真实调用，而不是只在 GitHub 仓库里存在。

- [ ] Step 1: 确认本地安装布局。

```powershell
Get-ChildItem C:\Users\admin\.codex\skills | Where-Object { $_.Name -like "project*" } | Select-Object Name
```

- [ ] Step 2: 同步新增 skill。

```powershell
Copy-Item -Recurse -Force `
  D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot\project-session-extract `
  C:\Users\admin\.codex\skills\project-session-extract
```

- [ ] Step 3: 同步 references。

```powershell
Copy-Item -Force `
  D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot\references\session-digest.md `
  C:\Users\admin\.codex\skills\references\session-digest.md

Copy-Item -Force `
  D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot\references\session-digest-implementation-plan.zh.md `
  C:\Users\admin\.codex\skills\references\session-digest-implementation-plan.zh.md
```

- [ ] Step 4: 同步更新后的 existing skills。

```powershell
Copy-Item -Force D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot\SKILL.md C:\Users\admin\.codex\skills\project-develop-copilot\SKILL.md
Copy-Item -Force D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot\project-init\SKILL.md C:\Users\admin\.codex\skills\project-init\SKILL.md
Copy-Item -Force D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot\project-ingest\SKILL.md C:\Users\admin\.codex\skills\project-ingest\SKILL.md
Copy-Item -Force D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot\project-query\SKILL.md C:\Users\admin\.codex\skills\project-query\SKILL.md
Copy-Item -Force D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot\project-develop\SKILL.md C:\Users\admin\.codex\skills\project-develop\SKILL.md
Copy-Item -Force D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot\project-fix\SKILL.md C:\Users\admin\.codex\skills\project-fix\SKILL.md
Copy-Item -Force D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot\project-finish\SKILL.md C:\Users\admin\.codex\skills\project-finish\SKILL.md
Copy-Item -Force D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot\project-review\SKILL.md C:\Users\admin\.codex\skills\project-review\SKILL.md
```

- [ ] Step 5: 验收。

```powershell
Get-Content C:\Users\admin\.codex\skills\project-session-extract\SKILL.md -TotalCount 20
Get-Content C:\Users\admin\.codex\skills\references\session-digest.md -TotalCount 20
```

预期：

- 本地存在 `project-session-extract`。
- 本地 references 存在 `session-digest.md`。
- 当前会话重新加载 skill 后，skill 列表能出现 `project-session-extract`。

---

## Task 9: 真实项目测试流程

**Files:**

- Test target: 任意已初始化 `.llm-wiki` 的真实项目，例如：

```text
D:\workspace\drone\develop\smartghub\drone-cloud-api
D:\workspace\drone\cloudsmartgo\smart-go-web
```

**Purpose:** 验证这不是文档能力，而是真能把历史 session 提纯并导入项目 wiki。

- [ ] Step 1: 准备一段模拟历史 session。

示例：

```text
用户：我们需要修复 DJI 直播容量统计问题。
AI：现在 FPV 和 dock camera 可能同时占用容量，建议区分 payload 和 dock stream。
用户：重点是 dock camera 不应该被 FPV 清理逻辑影响。
AI：执行计划是先查 stream key，再改容量统计，再补测试。
用户：这个需求先放 drone-cloud-api，涉及直播模块和 MQTT 回调。
```

- [ ] Step 2: 调用自然入口。

用户输入：

```text
把这段历史 session 提取成项目上下文，先给我看候选导入内容。项目路径是 D:\workspace\drone\develop\smartghub\drone-cloud-api
```

预期：

- router 进入 `session-context-import`。
- primary stage 是 `project-session-extract`。
- 输出候选 Session Digest。
- 不直接写 `.llm-wiki`。

- [ ] Step 3: 用户确认导入。

用户输入：

```text
确认导入，关联到 dji-live-capacity 这个 flow。
```

预期：

- 写入 `.llm-wiki/session-digests/session-YYYYMMDD-dji-live-capacity.md`。
- 更新 `.llm-wiki/log.md`。
- 如果已有 requirement/Flow Record，追加证据链接。
- 未确认内容不进入 requirement truth。

- [ ] Step 4: 查询验证。

用户输入：

```text
查询 dji-live-capacity 相关上下文。
```

预期：

- `project-query` 返回 related session digest。
- 输出区分 confirmed / candidate。

- [ ] Step 5: review 验证。

用户输入：

```text
review 一下这次 session digest 导入有没有污染项目上下文。
```

预期：

- `project-review` 检查 candidate 是否被错误提升。
- 检查 dashboard 是否从未确认历史 session 中造假进度。

---

## Task 10: GitHub 同步

**Files:**

- All modified files under:

```text
D:\tmp\github\role-copilot-skills\project-agent-copilot\project-develop-copilot
```

**Purpose:** 将新能力同步到团队可安装的 GitHub 仓库。

- [ ] Step 1: 检查状态。

```powershell
git -C D:\tmp\github\role-copilot-skills status --short
```

- [ ] Step 2: 只 stage 本次相关文件。

```powershell
git -C D:\tmp\github\role-copilot-skills add `
  project-agent-copilot/project-develop-copilot/project-session-extract/SKILL.md `
  project-agent-copilot/project-develop-copilot/references/session-digest.md `
  project-agent-copilot/project-develop-copilot/references/session-digest-implementation-plan.zh.md `
  project-agent-copilot/project-develop-copilot/SKILL.md `
  project-agent-copilot/project-develop-copilot/project-init/SKILL.md `
  project-agent-copilot/project-develop-copilot/project-ingest/SKILL.md `
  project-agent-copilot/project-develop-copilot/project-query/SKILL.md `
  project-agent-copilot/project-develop-copilot/project-develop/SKILL.md `
  project-agent-copilot/project-develop-copilot/project-fix/SKILL.md `
  project-agent-copilot/project-develop-copilot/project-finish/SKILL.md `
  project-agent-copilot/project-develop-copilot/project-review/SKILL.md `
  project-agent-copilot/project-develop-copilot/README.zh.md `
  project-agent-copilot/project-develop-copilot/README.md
```

- [ ] Step 3: 提交。

```powershell
git -C D:\tmp\github\role-copilot-skills commit -m "feat: add historical session digest skill"
```

- [ ] Step 4: 推送。

```powershell
git -C D:\tmp\github\role-copilot-skills push
```

- [ ] Step 5: 验收。

```powershell
git -C D:\tmp\github\role-copilot-skills status --short
```

预期：

- 本次相关文件已提交并推送。
- 未跟踪或未提交的无关文件不被误提交。

---

## 完成标准

这项能力完成后，必须满足：

- `references/session-digest.md` 是中文正式设计文档。
- `project-session-extract/SKILL.md` 存在，并能被 skill 系统触发。
- 根 router 能将历史 session / transcript / conversation 导入请求路由到 `project-session-extract`。
- `project-init` 会创建或保留 `.llm-wiki/session-digests/`。
- `project-ingest` 明确不吞掉历史 session 场景。
- `project-query` 能把确认导入的 Session Digest 作为项目上下文证据。
- `project-develop` / `project-fix` 能使用确认的 Session Digest 作为 supporting evidence。
- `project-finish` 能在真实执行后更新相关 digest 状态。
- `project-review` 能检查 Session Digest 是否污染项目事实。
- 本地安装后的 skill 能真实使用。
- 至少通过一个真实项目或模拟 transcript 的端到端测试。
- 代码已同步到 GitHub。

完成后的用户体验应该是：

```text
用户只需要把历史 session 或 transcript 给 Project Develop Copilot。
LLM 负责提纯、过滤、匹配、建议导入位置。
用户确认后，内容进入 .llm-wiki，并能被后续开发、修 Bug、查询、review 复用。
```

这不是一个额外割裂的工具，而是 Project Develop Copilot 对“历史会话上下文迁移”的正式吸收能力。
