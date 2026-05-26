# Role Copilot Skills

面向企业团队提效的角色型 Agent Copilot Skills 集合。

[English](./README.md) | 简体中文

## 这是什么？

Role Copilot Skills 是一组按企业角色组织的 Agent Copilot skills。

这个仓库不是把所有 prompt 平铺在一起，而是按实际岗位和团队流程来组织。每个一级目录是一个 Agent Copilot 角色，每个二级目录是一个可以独立安装的 Codex skill。

```text
角色 Copilot
-> 角色下的具体 skills
-> 项目本地规则和工具
-> 经确认的执行动作或结构化结果
```

目标是把团队里的高频流程沉淀成可复用的 AI 辅助能力，同时保留真实业务规则、现有脚本和安全边界。

## 为什么需要它？

企业团队里已经有很多稳定流程：

- HR 团队要筛简历、写候选人详情报告、准备面试问题。
- DevOps 团队要打包服务、诊断 CI 失败、整理发布说明。
- 研发团队要初始化项目上下文、开发功能、做代码审查。

通用 AI 可以帮忙，但 Agent 需要知道自己当前扮演什么角色：

- 这个角色负责什么？
- 应该收集哪些信息？
- 哪些本地文档或脚本是事实来源？
- 哪些动作必须确认？
- 最终结果应该怎么汇报？

Role Copilot Skills 就是把这些角色工作流沉淀成可安装、可复用的 skills。

## 仓库结构

```text
role-copilot-skills/
  devops-agent-copilot/
    devops-package-copilot/
  hr-agent-copilot/
    hr-resume-screening/
    hr-candidate-detail-report/
    hr-interview-question-generator/
```

当前仓库已经包含：

```text
devops-agent-copilot/
  devops-package-copilot/
```

后续会逐步补充更多角色和 skill。

## 当前 Skills

### DevOps Agent Copilot

| Skill | 使用场景 |
|---|---|
| `devops-package-copilot` | 用户用自然语言要求打包项目时，读取项目本地 `docs/docker-build-*.md` 规则，复用当前会话里的打包上下文，生成真实脚本命令，并调用已有打包脚本。 |

计划中的 DevOps skills：

- `devops-ci-diagnose-copilot`
- `devops-release-copilot`

### HR Agent Copilot

计划或外部已有 skills：

- `hr-resume-screening`
- `hr-candidate-detail-report`
- `hr-interview-question-generator`

## 安装

安装单个 skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/devops-agent-copilot/devops-package-copilot
```

本地开发时，在仓库根目录执行：

```bash
npx skills add .
```

安装后重启 Codex 或你的 Agent Runtime，让 skill 被重新发现。

## 使用示例

自然地使用 DevOps 打包 skill：

```text
打包 smart-go-file 项目，路径 D:\workspace\drone\develop\smartghub\drone-cloud-api，版本 v1.3.0
```

```text
再打一次
```

```text
这次打 dock-api
```

```text
换成 v1.3.1 再打一次
```

skill 会读取项目本地打包文档：

```text
<project-root>/docs/docker-build-*.md
```

它不会猜测打包参数。真实命令必须来自项目文档。

## 设计原则

- **先有角色，再有 skill**：按企业角色组织能力，例如 DevOps、HR。
- **一个 skill 解决一个高频流程**：避免做成泛泛的大 prompt。
- **项目文档是事实来源**：Agent 读取本地文档，不猜命令。
- **复用会话上下文**：同一个打包 session 里，不把重复操作变成问卷。
- **高风险动作必须确认**：首次执行、切换项目、release、deploy、push、删除等动作需要确认。
- **不替代已有脚本**：skill 负责编排现有工具和脚本，不重写已有流程。
- **输出结构化**：结果要方便交接、审计，也方便后续 skill 复用。

## 项目状态

当前仓库处于早期阶段。

第一颗已实现的 skill 是 `devops-package-copilot`。它面向已有本地打包脚本和 `docs/docker-build-*.md` 文档的企业项目，负责把自然语言打包请求转换为真实、可执行的脚本命令。

后续会继续补充 CI 诊断、发布助手，以及更多角色型 Copilot skills。
