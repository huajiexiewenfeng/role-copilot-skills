# Project Agent Copilot

面向项目研发工作流的角色型 skills，例如开发、PRD、UI 实现、评审、测试和发布协作。

[English](./README.md) | 简体中文

## 这是什么？

Project Agent Copilot 是 Role Copilot Skills 中的项目研发角色组。

它面向已经有源码、项目文档、开发约定和稳定研发流程的团队。Copilot 不替代这些系统，而是帮助 Agent 恢复项目上下文、让原始资料可发现、在受控模块范围内工作，并把有价值的知识同步回轻量项目 LLM Wiki。

这个角色组会拆成多个 domain skills。`project-develop-copilot` 是第一颗 domain skill；后续可以继续补充 PRD、UI、评审、测试、发布或重构等方向的 skills。

## 当前 Skills

| Skill | 使用场景 |
|---|---|
| `project-develop-copilot` | 用于项目开发生命周期：init、ingest、develop、fix、finish、review，并维护项目本地上下文和 LLM Wiki。 |

计划中的 domain skills：

- `project-prd-copilot`
- `project-ui-copilot`
- `project-review-copilot`
- `project-test-copilot`
- `project-release-copilot`

## 安装

安装开发 skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot
```

本地开发时，在仓库根目录执行：

```bash
npx skills add .
```

## 典型流程

```text
用户请求或原始资料
-> project-develop-copilot
-> 定位项目根目录
-> 发现项目资料和旧上下文
-> 构建受控工作上下文
-> 讨论、计划、修复或实现
-> 验证变更
-> 将有价值知识同步到 .llm-wiki
```

## 上下文模型

Project Agent Copilot 使用轻量项目 LLM Wiki 作为共享上下文层：

```text
.llm-wiki/
  index.md
  log.md
  AGENTS.md
  ingest/
  sources/
  requirements/
  bugs/
  modules/
```

这个 wiki 不替代源码、PRD、issue、设计文档、测试或代码。它是索引和摘要层，用来记录重要资料在哪里、含义是什么、关联哪个模块或需求，以及还存在哪些缺口。

旧版 `docs/ai-coding/` 目录视为迁移来源。新的项目上下文应写入 `.llm-wiki`，不再继续扩张旧目录。

## 安全边界

- 源码、测试、配置、构建文件和用户决策是事实来源。
- `.llm-wiki` 只保存索引、摘要、关系、状态和缺口，不保存大段原始内容。
- 不默认把 monorepo 里的所有服务都拉进上下文。
- 使用 scoped working context 区分 active、candidate、read-only 和 excluded 模块。
- 除非用户明确要求，不更新旧版 `docs/ai-coding/`。
- 在上下文恢复或需求讨论阶段，不修改代码；只有用户确认实现后才进入代码修改。

## 示例

```text
Use project init for this repository and migrate legacy docs/ai-coding into .llm-wiki.
```

```text
Use project ingest for docs/prd/new-payment-flow.md.
```

```text
Use project develop for the payment callback requirement. It should only touch order-service and payment-service.
```

```text
Use project fix with this log file and diagnose the suspected notification-service bug.
```
