# DevOps Agent Copilot

面向打包、CI 诊断、发布准备和 DevOps 流程辅助的角色型 Agent Copilot。

[English](./README.md) | 简体中文

## 这是什么？

DevOps Agent Copilot 是 Role Copilot Skills 里的 DevOps 角色组。

它面向已经有构建脚本、CI/CD 流程、部署约定和发布交接习惯的团队。Copilot 不替代这些系统，而是帮助 Agent 读取项目本地规则、组织上下文、安全调用命令，并整理执行结果。

## 当前 Skills

| Skill | 使用场景 |
|---|---|
| `devops-package-copilot` | 用户用自然语言要求打包项目时，读取项目本地 `docs/docker-build-*.md` 规则，并调用已有打包脚本。 |
| `devops-release-copilot` | 镜像打包完成后，准备发布交接：同步镜像 tag、Docker Compose 文件和 application 环境变量。 |

计划中的 skills：

- `devops-ci-diagnose-copilot`

## 安装

安装打包 skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/devops-agent-copilot/devops-package-copilot
```

安装发布 skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/devops-agent-copilot/devops-release-copilot
```

## 典型流程

```text
用户请求
-> 读取项目本地打包文档
-> 复用当前打包 session 上下文
-> 补齐关键缺失参数
-> 生成真实脚本命令
-> 必要时确认
-> 调用已有脚本
-> 汇总产物或失败原因
```

## 安全模型

- 项目文档是事实来源。
- Agent 不能发明脚本参数。
- 每个项目路径第一次执行需要确认。
- 同一 session 的普通后续打包可以复用上下文，不重复确认。
- release、deploy、push、publish、cleanup、全量模块打包仍然需要确认。

## 示例

```text
打包 smart-go-file 项目，路径 D:\workspace\drone\develop\smartghub\drone-cloud-api，版本 v1.3.0
```

```text
再打一次
```

```text
这次打 dock-api
```
