# Project Agent Copilot

项目研发方向的 skill 集合容器。

[English](./README.md) | 简体中文

## 这是什么？

Project Agent Copilot 是 Role Copilot Skills 中的项目研发角色容器。

它面向已经有源码、项目文档、开发约定和稳定研发流程的团队。这个目录本身不是一个大而全的 skill，而是用来承载项目方向的多个 skill 集合，例如开发、PRD、UI、测试、发布等。

当前第一个落地集合是 `project-develop-copilot`。

## 当前集合

| 集合 | 包含 |
|---|---|
| [`project-develop-copilot`](./project-develop-copilot/README.zh.md) | `project-init`、`project-ingest`、`project-develop`、`project-fix`、`project-finish`、`project-review` |

计划中的集合：

- `project-prd-copilot`
- `project-ui-copilot`
- `project-test-copilot`
- `project-release-copilot`

## 安装

安装一个项目开发 skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot/project-develop
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
    project-develop/
    project-fix/
    project-finish/
    project-review/
```

## 边界

保持这个目录只是角色容器。真正可安装、可触发的流程 skill 应放在某个集合目录内部。集合自己的共享 references 应和集合放在一起，不放在整个角色容器的全局层。
