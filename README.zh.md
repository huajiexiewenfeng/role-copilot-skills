# Role Copilot Skills

面向企业团队提效的角色型 Agent Copilot Skills 集合。

[English](./README.md) | 简体中文

## 这是什么？

Role Copilot Skills 是一组按企业角色组织的 Agent Copilot skills。

这个仓库不是把所有 prompt 平铺在一起，而是按实际岗位和团队流程来组织。每个一级目录是一个 Agent Copilot 角色容器。角色容器下面可以放一个或多个 skill 集合，真正可安装的 Codex skill 位于集合内部。

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

其中项目开发集合承担一个特殊角色：把已有顶级 skills 和 tools 桥接进项目生命周期，同时内化轻量 project LLM Wiki 作为上下文记忆层。

## 仓库结构

```text
role-copilot-skills/
  devops-agent-copilot/
    devops-package-copilot/
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
      llm-wiki-doctor/
      project-base-init/
      project-graph-candidates-scan/
      project-graph-auto-edge/
      project-graph-human-edge/
  hr-agent-copilot/
    hr-resume-screening-copilot/
    hr-candidate-detail-report-copilot/
    hr-interview-question-generator-copilot/
```

当前仓库已经包含：

```text
devops-agent-copilot/
  devops-package-copilot/
project-agent-copilot/
  project-develop-copilot/
    project-init/
    project-ingest/
    project-develop/
    project-fix/
    project-finish/
    project-review/
hr-agent-copilot/
  hr-resume-screening-copilot/
  hr-candidate-detail-report-copilot/
  hr-interview-question-generator-copilot/
```

后续会逐步补充更多角色和 skill。

## 当前 Skills

### DevOps Agent Copilot

[角色 README](./devops-agent-copilot/README.zh.md) | [English](./devops-agent-copilot/README.md)

| Skill | 使用场景 |
|---|---|
| `devops-package-copilot` | 用户用自然语言要求打包项目时，读取项目本地 `docs/docker-build-*.md` 规则，复用当前会话里的打包上下文，生成真实脚本命令，并调用已有打包脚本。 |

计划中的 DevOps skills：

- `devops-ci-diagnose-copilot`
- `devops-release-copilot`

### Project Agent Copilot

[角色 README](./project-agent-copilot/README.zh.md) | [English](./project-agent-copilot/README.md)

| Skill | 使用场景 |
|---|---|
| `project-develop-copilot` | 将自然语言项目开发请求路由到合适的项目生命周期 skill。 |
| `project-init` | 初始化或刷新项目 LLM Wiki，发现模块，并迁移旧版 `docs/ai-coding`。 |
| `project-ingest` | 将 PRD、链接、Markdown、PDF、Word、日志、会议纪要或临时资料摄入项目 LLM Wiki。 |
| `project-query` | 基于 `.llm-wiki`、Project Graph pin/edge/candidate 和必要源码证据回答只读项目问题。 |
| `project-develop` | 基于受控项目上下文和需求摘要开发需求或功能。 |
| `project-fix` | 基于受控上下文、证据、验证和 bug 摘要诊断并修复项目问题。 |
| `project-finish` | 在验证后同步实际变更到 LLM Wiki，并准备交付说明。 |
| `project-review` | 检查项目变更的代码风险、测试缺口、范围漂移、过期上下文和 wiki 同步。 |
| `project-maintain` | 巡检和修复 `.llm-wiki` 结构、Project Graph 一致性、过期 candidates、cross-ref pins、registry、可见性漂移和内置 doctor 发现。 |
| `llm-wiki-doctor` | 运行或解释 LLM Wiki Doctor 的 validate/score/report 输出，包括中文成熟度报告、空壳 wiki 识别和 Project Graph validator 发现。 |
| `project-base-init` | 初始化或刷新独立 Base Graph 仓库，用于多项目 catalog 和 overview 协调。 |
| `project-graph-candidates-scan` | 扫描当前项目的 Project Graph 关系候选，不写 edge 或 cross-ref pin。 |
| `project-graph-auto-edge` | 通过 Base Graph 和源码证据把 candidate 转成供人工确认的 edge proposal。 |
| `project-graph-human-edge` | 接受、拒绝或手动登记 Project Graph edge，并维护 `cross-refs/index.md` pin。 |

Project Graph 维护拆成三个显式技能，方便 agent 明确调用对应阶段：先扫描 candidates，再生成 proposal，最后由人工确认或手动登记 edge。只有 `project-graph-human-edge` 写入 confirmed edge 时才维护 `cross-refs/index.md`。

安装 `project-develop-copilot` 现在也会带上 `scripts/llm_wiki_doctor.py` 校验器、测试、`llm-wiki-doctor` skill 和面向业务项目的 scaffold 模板。`project-init` 会把 vendored doctor、pre-commit 配置和 CI workflow 安装到每个业务项目里，让 `validate` 在 project finish 或 PR merge 前拦截结构性 ERROR；人工诊断使用 `report` 和 `score`。详细用法见 `project-agent-copilot/project-develop-copilot/scripts/README.llm-wiki-doctor.md`。

计划中的 Project skills：

- `project-prd-copilot`
- `project-ui-copilot`
- `project-test-copilot`
- `project-release-copilot`

### HR Agent Copilot

[角色 README](./hr-agent-copilot/README.zh.md) | [English](./hr-agent-copilot/README.md)

| Skill | 使用场景 |
|---|---|
| `hr-resume-screening-copilot` | 根据 JD 对简历做第一轮筛选、排序和 100 分制评分。 |
| `hr-candidate-detail-report-copilot` | 输出候选人明细报告，解释得分原因、优势、短板、风险点和面试验证点。 |
| `hr-interview-question-generator-copilot` | 为候选人生成定制化面试题、参考答案要点、追问和弱回答信号。 |

## 安装

安装单个 skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/devops-agent-copilot/devops-package-copilot
```

安装一个 HR skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-resume-screening-copilot
```

安装一个 Project skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot/project-develop
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

