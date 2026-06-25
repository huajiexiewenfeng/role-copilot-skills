# Project Agent Copilot

项目研发方向的 skill 集合容器。

[English](./README.md) | 简体中文

## 这是什么？

Project Agent Copilot 是 Role Copilot Skills 中的项目研发角色容器。

它面向已经有源码、项目文档、开发约定和稳定研发流程的团队。这个目录本身不是一个大而全的 skill，而是用来承载项目方向的多个 skill 集合，例如开发、PRD、UI、测试、发布等。

当前第一个落地集合是 `project-develop-copilot`。

项目方向的集合应遵循两个原则：桥接成熟的顶级 skills 和 tools，而不是重写它们；同时把 project LLM Wiki 内化为轻量项目上下文层，而不是依赖另一套独立知识库流程。

对于 `project-develop-copilot`，在继续完成或修改 skill 集合之前，以 `project-develop-copilot/references/north-star.md` 作为对齐文档。

## 当前集合

| 集合 | 包含 |
|---|---|
| [`project-develop-copilot`](./project-develop-copilot/README.zh.md) | `project-develop-copilot`、`project-init`、`project-ingest`、`project-query`、`project-develop`、`project-fix`、`project-finish`、`project-review`、`project-maintain`、`project-base-init`、`project-graph-candidates-scan`、`project-graph-auto-edge`、`project-graph-human-edge` |

计划中的集合：

- `project-prd-copilot`
- `project-ui-copilot`
- `project-test-copilot`
- `project-release-copilot`

## 安装

安装项目开发 router skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot
```

本地开发时，在仓库根目录执行：

```bash
npx skills add .
```

## 典型流程

```text
project-agent-copilot/
  project-develop-copilot/
    project-init/
    project-ingest/
    project-query/
    project-develop/
    project-fix/
    project-finish/
    project-review/
    project-maintain/
    project-base-init/
    project-graph-candidates-scan/
    project-graph-auto-edge/
    project-graph-human-edge/
```

## Project Graph 维护

当跨项目关系需要显式维护，而不是普通只读查询时，使用 Project Graph 技能。`project-graph-candidates-scan` 只更新候选关系，`project-graph-auto-edge` 通过 Base Graph / 源码证据生成可人工确认的 proposal，`project-graph-human-edge` 是正常流程里唯一写 confirmed edge 和 cross-ref pin 的入口。这个集合也内置 `scripts/llm_wiki_doctor.py` 和可复用 pre-commit hook，让项目可以在本地提交、project finish、CI/PR 边界执行 wiki / graph 卫生检查。

## 只读项目问答

当用户问“这个项目里有什么”、“某个模块或 API 怎么调用”、“之前的需求或设计文档怎么说”，或者询问某个主题关联哪些 `.llm-wiki` 证据时，使用 `project-query`。它应该先恢复项目 wiki 上下文，再按需回到源码核对当前接口、MQTT topic、服务行为或示例。

例如：

```text
这个项目里面，大疆 API 适配，直播相关的内容有哪些？如何通过 API 调用
```

这类问题应保持只读并路由到 `project-query`，不要直接进入实现、调试或评审。

## 边界

保持这个目录只是角色容器。真正可安装、可触发的流程 skill 应放在某个集合目录内部。集合自己的共享 references 应和集合放在一起，不放在整个角色容器的全局层。
