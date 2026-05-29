# Project Develop Copilot

Project Develop Copilot 是面向真实项目开发的 skill 集合。它有两个核心目标：

1. 桥接各个顶级 skills 和 tools，纳入统一项目生命周期。
2. 内化项目级 LLM Wiki，作为共享上下文记忆层。

它把项目 LLM Wiki 维护、受控上下文恢复、需求开发、bug 修复、完成同步和交付前评审组合成一条连贯的开发生命周期。

它不替代 Superpowers 类 skills，而是先准备项目上下文、active scopes 和 `.llm-wiki` 状态，再在这个受控上下文里桥接 brainstorming、planning、TDD、debugging、execution、verification 和 review。

它也可以桥接 OpenSpec 风格需求机制、已有 codegraph 上下文，以及 Obsidian LLM Wiki 思想，但这些都是桥接对象，不是硬依赖。旧版 project-coding-skills 是前身，它已经验证过的项目开发思想应内化到这里；当前集合是升级版。见 `references/tool-bridge.md`。

[English](./README.md) | 简体中文

## Skills

| Skill | 使用场景 |
|---|---|
| `project-init` | 初始化或刷新项目 LLM Wiki，发现模块，并迁移旧版 `docs/ai-coding`。 |
| `project-ingest` | 将 PRD、链接、Markdown、PDF、Word、日志、会议纪要或临时资料摄入项目 LLM Wiki。 |
| `project-develop` | 基于受控项目上下文和需求摘要开发需求或功能。 |
| `project-fix` | 基于受控上下文、证据、验证和 bug 摘要诊断并修复项目问题。 |
| `project-finish` | 在验证后同步实际变更到 LLM Wiki，并准备交付说明。 |
| `project-review` | 检查项目变更的代码风险、测试缺口、范围漂移、过期上下文和 wiki 同步。 |

## 安装

安装单个 skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot/project-develop
```

本地开发时，在仓库根目录执行：

```bash
npx skills add .
```

## 生命周期

```text
project-init
-> project-ingest
-> project-develop 或 project-fix
-> project-finish
-> project-review
```

`project-init` 和 `project-ingest` 负责完善项目上下文。`project-develop` 和 `project-fix` 在受控上下文内进入实际开发。`project-finish` 将验证后的结果同步回 wiki。`project-review` 在交付前检查代码、测试、范围和上下文一致性。

Superpowers 类 skills 应在项目上下文恢复之后调用，而不是在它之前调用。见 `references/superpowers-bridge.md`。

其他顶级工具也遵循同样的 context-first 桥接规则。见 `references/tool-bridge.md`。

## 上下文模型

共享项目上下文层是 `.llm-wiki`：

```text
.llm-wiki/
  index.md
  log.md
  AGENTS.md
  ingest/
  sources/
  requirements/
  bugs/
  working-context/
  modules/
```

这个 wiki 是 LLM Wiki 思想在项目开发中的内化子集：它是索引和摘要层，不替代源码、PRD、issue、设计文档、测试或代码。它记录重要资料在哪里、含义是什么、关联哪个模块或需求，以及还存在哪些缺口。

`working-context/` 只用于复杂或跨模块工作，用来把 active scopes、read-only scopes、excluded scopes、契约、范围升级和验证计划放在同一个任务上下文里。

旧版 `docs/ai-coding/` 目录视为迁移来源。新的项目上下文应写入 `.llm-wiki`。

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
