# Project Agent Copilot

Project Agent Copilot 是 Role Copilot Skills 中的项目研发角色组。

它用于组织项目研发相关的 domain skills，例如开发、PRD、UI 实现、评审、测试和发布。每个子目录都是一个可以独立安装的项目研发领域 skill。

## Skills

| Skill | Use When |
|---|---|
| `project-develop-copilot` | 用于项目开发生命周期：init、ingest、develop、fix、finish、review，并维护项目本地上下文和 LLM Wiki。 |

## 计划中的 Domain Skills

- `project-prd-copilot`
- `project-ui-copilot`
- `project-review-copilot`
- `project-test-copilot`
- `project-release-copilot`

## 原则

- 项目本地原始资料和代码是事实来源。
- 各 domain skill 通过 `.llm-wiki` 共享项目上下文。
- 不把一个 domain skill 扩大成整个项目研发角色组。
