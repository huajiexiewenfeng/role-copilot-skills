# Base Graph 使用教程

## 1. 你要准备什么

你需要准备两类仓库：

```text
1. Base Graph 仓库
   用来放全局项目目录、系统 overview、本机 registry。

2. 业务项目仓库
   每个业务项目都有自己的 .llm-wiki。
```

可以用 Maven 来理解：

```text
Base Graph        = parent pom
业务项目 .llm-wiki = module 自己的 pom
外部项目 .llm-wiki = dependencies
```

Base Graph 不是业务项目。
它不保存精确接口事实，不保存 bug，不保存需求，也不保存源码真相。

它只负责：

- 项目清单；
- 本机路径映射；
- 系统级 overview；
- 跨项目排查入口；
- Base 层 handoff / decisions / log。

## 2. 第一步：创建 Base Graph 仓库

例如你在 GitLab 创建一个新仓库：

```text
llm-wiki-base-graph
```

克隆到本机：

```bash
git clone <your-gitlab-url> D:/code/llm-wiki-base-graph
cd D:/code/llm-wiki-base-graph
```

这个仓库可以是空仓库。

## 3. 第二步：用 `project-base-init` 初始化

在 Base Graph 仓库目录里，对 Codex 说：

```text
使用 project-base-init 初始化这个 Base Graph 仓库。
```

或者更明确一点：

```text
这是一个独立 Base Graph 仓库，不是业务项目。请用 project-base-init 初始化。
```

初始化后应该得到：

```text
.llm-wiki/
  registry.local.json
  base-graph/
    manifest.json
    project-catalog.md
    overview.md
  decisions/
    README.md
  handoff/
    README.md
  log.md
.gitignore
```

`.gitignore` 应该包含：

```gitignore
.llm-wiki/registry.local.json
```

## 4. 初始化后检查什么

### 4.1 检查 manifest

打开：

```text
.llm-wiki/base-graph/manifest.json
```

应该类似：

```json
{
  "$schema_version": 2,
  "graph_role": "base",
  "graph_id": "llm-wiki-base-graph",
  "name": "LLM Wiki Base Graph",
  "default_stale_days": 30,
  "project_catalog": "project-catalog.md",
  "overview": "overview.md"
}
```

重点看：

```json
"graph_role": "base"
```

### 4.2 检查不要出现业务项目文件

Base Graph 仓库里不应该有：

```text
.llm-wiki/project-graph/edges.md
.llm-wiki/project-graph/candidates.md
.llm-wiki/cross-refs/index.md
shared-edges.md
relation-policy.md
.llm-wiki/requirements/
.llm-wiki/bugs/
.llm-wiki/modules/
```

如果出现了，说明 Base Graph 被误当成业务项目初始化了。

## 5. 第三步：配置 Base Graph 发现方式

业务项目要能找到 Base Graph，有两种方式。

### 方式 A：环境变量

设置：

```bash
LLM_WIKI_BASE_GRAPH_PATH=D:/code/llm-wiki-base-graph
```

Windows PowerShell 当前会话可以这样：

```powershell
$env:LLM_WIKI_BASE_GRAPH_PATH="D:/code/llm-wiki-base-graph"
```

如果要长期生效，可以写入系统环境变量。

### 方式 B：bootstrap 文件

创建：

```text
~/.llm-wiki/base-graph.local.json
```

Windows 上通常是：

```text
C:/Users/<你的用户名>/.llm-wiki/base-graph.local.json
```

内容：

```json
{
  "$schema_version": 1,
  "base_graph_path": "D:/code/llm-wiki-base-graph"
}
```

推荐优先用环境变量测试，稳定后再放 bootstrap 文件。

## 6. 第四步：准备业务项目

假设你有两个业务项目：

```text
D:/code/order-service
D:/code/payment-service
```

每个业务项目都应该先有自己的 `.llm-wiki`。

如果没有，进入业务项目目录后说：

```text
使用 project-init 初始化这个业务项目。
```

注意：

```text
Base Graph 用 project-base-init。
业务项目用 project-init。
```

不要混用。

## 7. 第五步：把业务项目登记到 Base Graph

在 Base Graph 仓库里，或者让 agent 在 Base Graph write mode 下登记项目。

你可以说：

```text
把 order-service 登记到 Base Graph。
project_id: order-service
path: D:/code/order-service
domain: order
repo: <git-url>
```

再登记：

```text
把 payment-service 登记到 Base Graph。
project_id: payment-service
path: D:/code/payment-service
domain: payment
repo: <git-url>
```

登记后会更新两个地方。

### 7.1 本机 registry

`.llm-wiki/registry.local.json`：

```json
{
  "$schema_version": 1,
  "projects": {
    "order-service": {
      "path": "D:/code/order-service",
      "wiki": ".llm-wiki"
    },
    "payment-service": {
      "path": "D:/code/payment-service",
      "wiki": ".llm-wiki"
    }
  }
}
```

这个文件不入库。

### 7.2 项目目录

`.llm-wiki/base-graph/project-catalog.md`：

```markdown
| project_id | display_name | domain | owner | repo | status | notes |
|---|---|---|---|---|---|---|
| order-service | Order Service | order |  | <git-url> | active | 订单域 |
| payment-service | Payment Service | payment |  | <git-url> | active | 支付域 |
```

这个文件入库。

注意：

```text
project-catalog.md 不写本机路径。
本机路径只写 registry.local.json。
```

## 8. 第六步：写 Base Overview

打开：

```text
.llm-wiki/base-graph/overview.md
```

可以写成：

```markdown
# Base Graph Overview

## Domains

| domain | projects | notes |
|---|---|---|
| order | order-service | 订单创建、订单状态、回调入口 |
| payment | payment-service | 支付、退款、支付回调 |

## Key Cross-Service Flows

| flow | projects | summary | evidence |
|---|---|---|---|
| 订单支付 | order-service, payment-service | order-service 发起支付，payment-service 回调订单状态 | 业务项目 Project Graph |

## Common Entry Points

| topic | starting_project | related_projects | notes |
|---|---|---|---|
| 支付回调问题 | order-service | payment-service | 先看 order-service 的回调入口，再核对 payment-service 回调契约 |
```

这里写的是慢变架构说明，不要写精确接口契约全文。

## 9. 第七步：在业务项目里测试 Base Graph 是否生效

进入业务项目：

```bash
cd D:/code/order-service
```

对 Codex 说：

```text
从全局视角看，order-service 的支付回调可能涉及哪些项目？
```

理想行为：

1. agent 发现 Base Graph；
2. 读取 Base Graph 的 `overview.md` 和 `project-catalog.md`；
3. 知道可能涉及 `payment-service`；
4. 再回到当前项目自己的 `.llm-wiki/project-graph/edges.md` 或 `cross-refs/index.md` 找精确证据；
5. 如果需要验证外部契约，只读进入 `payment-service`。

## 10. 第八步：测试跨项目 registry 解析

在 `order-service` 里问：

```text
payment-service 的本机路径能解析到吗？
```

理想行为：

- 优先查当前项目 `.llm-wiki/registry.local.json`；
- 如果没有，再查 Base Graph `.llm-wiki/registry.local.json`；
- 找到 `payment-service -> D:/code/payment-service`；
- 只读访问对方 `.llm-wiki`。

如果解析失败，agent 应该问你路径，而不是猜路径。

## 11. 第九步：测试只读边界

在 `order-service` 里说：

```text
查看 payment-service 的支付回调契约，但不要修改 payment-service。
```

理想行为：

agent 应该输出类似边界说明：

```markdown
- remote_project: payment-service
- resolved_path: D:/code/payment-service
- reason: verify payment callback contract
- scope: read-only
- anchors_to_read:
  - ...
```

然后只读 `payment-service` 的 `.llm-wiki` 或源码。

不应该发生：

- 修改 `payment-service/.llm-wiki`；
- 修改 `payment-service` 源码；
- 在 `payment-service` 里创建 reverse edge；
- 修改 `payment-service` registry。

## 12. 第十步：测试 Base 写入边界

在业务项目 `order-service` 里说：

```text
这个支付链路应该更新到 Base Graph overview。
```

理想行为：

- agent 不直接修改 Base Graph 的 `overview.md`；
- agent 生成 Base Handoff 或更新建议；
- 只有当你切到 Base Graph 仓库，或显式进入 Base write mode，才真正写 Base 入库文件。

可以接受的输出：

```markdown
## Base Graph Handoff

- affected_projects: order-service, payment-service
- suggested_catalog_changes:
- suggested_overview_changes:
- evidence:
- verification_status:
```

## 13. 推荐测试清单

### Base 初始化测试

```text
用 project-base-init 初始化空仓库。
```

检查：

- 有 `manifest.json`；
- `graph_role = base`；
- 有 `project-catalog.md`；
- 有 `overview.md`；
- 有 `registry.local.json`；
- `.gitignore` 忽略 registry；
- 没有业务项目文件。

### 业务项目发现测试

```text
登记 order-service 和 payment-service。
```

检查：

- Base registry 有本机路径；
- project-catalog 有逻辑项目；
- catalog 不含本机路径。

### 全局视角查询测试

```text
从全局视角看支付回调涉及哪些项目？
```

检查：

- agent 先读 Base overview/catalog；
- 然后回到当前项目 Project Graph 找精确证据；
- 不把 Base overview 当成精确事实。

### 跨项目只读测试

```text
核对 payment-service 的回调契约，不要修改对方项目。
```

检查：

- 输出 read-only boundary；
- 只读对方 wiki / source；
- 不写对方项目。

### Base 写入边界测试

```text
把这个发现同步到 Base Graph。
```

检查：

- 业务项目会话只生成 Base Handoff；
- 不直接写 Base tracked files；
- 切到 Base 仓库后才允许写。

## 14. 未来有 `llm-wiki` 工具后的测试

当前 `llm-wiki` CLI 还没有实现。

未来实现后，可以这样测：

### 在 Base Graph 仓库

```bash
llm-wiki base audit
```

期望：

```text
OK manifest graph_role=base
OK project-catalog has no local path
OK registry.local.json is ignored
OK no forbidden project-graph/edges.md
OK no forbidden cross-refs/index.md
```

### 在业务项目仓库

```bash
llm-wiki doctor
```

或：

```bash
llm-wiki graph audit
```

期望：

```text
OK edges.md schema valid
OK cross-refs pin-only
OK registry ignored
WARN no Base Graph found
```

如果 Base Graph 已配置，则不应该 WARN。

## 15. 常见错误

### 错误 1：用 project-init 初始化 Base Graph

错误结果：

```text
Base 仓库里出现 requirements/ bugs/ modules/ project-graph/edges.md
```

正确做法：

```text
Base Graph 用 project-base-init。
业务项目用 project-init。
```

### 错误 2：把本机路径写进 project-catalog

错误：

```markdown
| payment-service | D:/code/payment-service |
```

正确：

```markdown
| payment-service | Payment Service | payment | ... |
```

本机路径只写：

```text
.llm-wiki/registry.local.json
```

### 错误 3：把 Base overview 当成精确契约

Base overview 只能说：

```text
支付回调涉及 order-service 和 payment-service。
```

不能当成：

```text
payment-service 的 payload 字段一定是 xxx。
```

精确契约必须回到业务项目 `.llm-wiki` 和源码验证。

### 错误 4：业务项目会话直接改 Base tracked files

错误：

```text
在 order-service 会话里直接修改 Base overview.md
```

正确：

```text
生成 Base Handoff。
切到 Base Graph 仓库后再应用。
```

## 16. 一句话使用流程

```text
1. 新建独立 Base Graph 仓库。
2. 用 project-base-init 初始化。
3. 设置 LLM_WIKI_BASE_GRAPH_PATH 或 base-graph.local.json。
4. 给每个业务项目跑 project-init。
5. 把业务项目 project-id 和路径登记到 Base registry。
6. 在 project-catalog.md 写项目清单。
7. 在 overview.md 写系统总览。
8. 在业务项目中通过 Base 找到相关项目。
9. 精确事实回到业务项目 Project Graph 和源码验证。
10. 外部项目默认 read-only。
```

## 17. 最重要的原则

```text
Base Graph 是地图，不是事实库。
Project Graph 是当前项目视角下的关系事实表。
外部项目 .llm-wiki 是 dependence，只读取证，不复制、不代写。
```

如果记住一句话，就是：

**Base Graph 帮你知道有哪些项目、在哪里、从全局怎么看；真正能用于开发和修复的事实，仍然来自业务项目自己的 `.llm-wiki` 和源码验证。**
