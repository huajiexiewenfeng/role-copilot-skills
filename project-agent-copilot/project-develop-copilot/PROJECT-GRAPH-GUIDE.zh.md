# Project Graph 使用教程

本文介绍 Project Develop Copilot（PDC）如何发现、核对并确认跨项目关系：

```text
project-graph-candidates-scan
  -> project-graph-auto-edge
  -> project-graph-human-edge
```

这条流程的核心不是自动生成一张看起来完整的图，而是保证每条关系都经过明确的证据和人工确认。

## 1. Project Graph 解决什么问题

在多服务项目中，跨项目关系经常散落在源码和配置里：

- 哪个服务调用了这个 Feign 接口；
- 一个 HTTP 回调从哪里发出、由谁接收；
- 哪个项目发布 MQTT Topic，哪些项目订阅；
- 某个配置项、数据库表或 DTO 由谁维护；
- 排查问题时应该进入哪个外部项目核对。

如果只靠聊天记录或老同事记忆，AI 很容易猜错关系。Project Graph 把关系分成“线索、建议、事实和入口”四层，让自动扫描和人工确认各自承担合适的职责。

可以先记住：

```text
candidate = 发现了一条可能存在的关系
proposal  = 已核对部分证据，等待人工判断
edge      = 人工确认后写入的关系事实
pin       = 指向 edge 的常用导航入口
```

## 2. 它和 Base Graph 有什么区别

Base Graph 和 Project Graph 解决的问题不同。

| 能力 | Base Graph | Project Graph |
|---|---|---|
| 主要作用 | 项目目录、系统总览、本机路径解析 | 当前业务项目视角下的跨项目关系事实 |
| 典型文件 | `project-catalog.md`、`overview.md`、`registry.local.json` | `candidates.md`、`proposals.md`、`edges.md`、`cross-refs/index.md` |
| 信息粒度 | 哪些项目存在、在哪里、系统大致如何协作 | 谁调用谁、哪个 Topic、接口或配置连接两个项目 |
| 是否能直接支撑开发 | 不能作为精确契约事实 | 只有新鲜且已验证的 edge 可以 |

一句话：

```text
Base Graph 帮你找到项目。
Project Graph 帮你确认项目之间的关系。
源码和运行证据负责证明关系是否真实。
```

Base Graph 的初始化和登记方式见《Base Graph 使用教程》。

## 3. 开始前准备什么

至少准备两个业务项目，例如：

```text
D:/code/order-service
D:/code/payment-service
```

当前操作项目假设是：

```text
order-service
```

开始前确认：

1. 当前业务项目已经运行过 `project-init`；
2. 当前项目存在 `.llm-wiki/project-graph/`；
3. 外部项目有稳定的逻辑 `project_id`；
4. 需要跨项目核对时，可以通过 Base Graph 或 registry 找到外部项目；
5. 外部项目默认只读。

当前项目常见结构：

```text
.llm-wiki/
  registry.local.json
  cross-refs/
    index.md
  project-graph/
    edges.md
    candidates.md
    proposals.md
    scan-report.md
    scan-state.local.json
```

其中以下本机文件不应该提交到 Git：

```gitignore
.llm-wiki/registry.local.json
.llm-wiki/cross-refs/registry.local.json
.llm-wiki/project-graph/scan-state.local.json
```

`proposals.md` 可以在第一次运行 `project-graph-auto-edge` 时创建，不要求业务项目初始化后一定已经有内容。

## 4. 第一步：准备业务项目的 Project Graph

如果项目还没有 `.llm-wiki`，先说：

```text
使用 project-init 初始化当前业务项目。
```

初始化后，至少确认：

```text
.llm-wiki/project-graph/edges.md
.llm-wiki/project-graph/candidates.md
.llm-wiki/project-graph/scan-report.md
.llm-wiki/cross-refs/index.md
```

这些文件的职责必须分开：

| 层 | 文件 | 作用 | 能否驱动开发决策 |
|---|---|---|---|
| Candidate | `project-graph/candidates.md` | 扫描或人工发现的关系线索 | 不能 |
| Proposal | `project-graph/proposals.md` | 等待人工判断的 edge 建议 | 不能 |
| Fact | `project-graph/edges.md` | 人工确认后的关系事实 | 仅新鲜且已验证的 edge 可以 |
| Pin | `cross-refs/index.md` | 团队常用入口，只引用 `edge_id` | 跟随引用的 edge |

`contract_summary`、`verification_status` 和 `last_verified` 等确认事实只存放在 `edges.md`。`cross-refs/index.md` 不复制这些字段。

## 5. 第二步：扫描 candidate

在当前业务项目中说：

```text
扫描当前项目的 Project Graph 候选关系，只维护 candidates。
不要写 edge、proposal 或 cross-ref pin。
```

也可以限定范围：

```text
使用 project-graph-candidates-scan 扫描 order-service 的支付模块，
重点检查 Feign、HTTP 回调和 MQTT Topic，只维护候选关系。
```

扫描器会从当前项目中寻找关系信号，例如：

- Feign Client 和 HTTP Client 接口；
- 配置或代码中的 HTTP URL；
- MQ Topic、Producer、Consumer Group 和 Queue Binding；
- RPC Client、SDK 依赖、回调 URL 和 Webhook；
- 可能体现跨服务归属的表、Schema 或共享配置；
- Wiki 中记录的上下游系统名称。

扫描阶段只允许修改当前项目：

```text
.llm-wiki/project-graph/candidates.md
.llm-wiki/project-graph/scan-report.md
.llm-wiki/project-graph/scan-state.local.json
.llm-wiki/log.md
```

扫描阶段禁止修改：

```text
.llm-wiki/project-graph/edges.md
.llm-wiki/project-graph/proposals.md
.llm-wiki/cross-refs/index.md
任何外部项目文件
任何 Base Graph tracked file
```

即使扫描器觉得证据已经很充分，也必须停留在 `pending` candidate，交给后续 proposal 和人工确认流程。

### candidate 的基本规则

新候选应满足：

```text
source = scan
status = pending
edge_id = 空
```

候选中常见字段：

```text
candidate_id
candidate_fingerprint
relation
source
local_anchor
remote_project
remote_anchor
evidence
confidence
status
edge_id
discovered_at
last_seen
```

注意：

- `remote_project` 暂时不确定时可以写 `unknown`；
- `remote_project=unknown` 的 candidate 不能提升为 edge；
- 重复发现同一 fingerprint 时应更新证据和 `last_seen`，不能重复新增；
- `source=manual` 的候选不会因为长期 pending 被自动归档；
- 当前项目的 candidates 只能记录“当前项目参与”的关系；
- 外部项目到另一个外部项目的发现只能进入 scan report。

## 6. 扫描后检查什么

扫描结果应报告：

```text
scan scope:
files inspected:
new candidates:
duplicate fingerprints skipped:
stale candidates archived:
external-to-external findings:
validation result:
next command:
```

检查重点：

- 新 candidate 的 `status` 是 `pending`；
- `edge_id` 为空；
- evidence 使用仓库相对路径、类名、方法、配置键或 Topic；
- fingerprint 不包含绝对路径、行号、机器名或盘符；
- 没有修改 edge、proposal、pin 或外部项目；
- `remote_project=unknown` 的候选没有被强行补成猜测的项目名。

如果某条候选已经值得进一步核对，下一步通常是：

```text
project-graph-auto-edge <candidate_id>
```

## 7. 第三步：生成 proposal

选中一个 candidate 后说：

```text
通过 Base Graph 定位外部项目并核对源码，
为这个 candidate 生成 edge proposal，但不要写 confirmed edge。
```

更明确的写法：

```text
使用 project-graph-auto-edge 处理 cand-20260807-001。
通过 Base Graph 解析 remote project，分别核对本地和外部项目证据。
只生成 proposal，不要修改 edges.md 和 cross-refs/index.md。
```

`project-graph-auto-edge` 会：

1. 根据 candidate id、fingerprint 或描述找到目标候选；
2. 读取现有 candidate、proposal、edge 和 pin，避免冲突；
3. 在需要时通过 Base Graph 将项目提示解析成规范 `project_id`；
4. 核对本地类、方法、接口、Topic、配置或 Wiki 入口；
5. 以只读方式核对外部项目的对应证据；
6. 确认规范方向并生成 edge fingerprint；
7. 写入 `proposals.md`；
8. 把 candidate 从 `pending` 改为 `proposed`；
9. 保持 candidate 的 `edge_id` 为空；
10. 停止并等待人工接受或拒绝。

proposal 常见字段：

```text
proposal_id
source_candidate_id
proposed_edge_id
fingerprint
type
from_project / from_anchor
to_project / to_anchor
contract_summary
verification_status
verification_evidence
proposed_cross_ref_id
proposed_local_entry
proposed_why_pinned
human_status
human_note
```

默认状态：

```text
proposal.human_status = pending
candidate.status = proposed
candidate.edge_id = 空
edges.md = 不变
cross-refs/index.md = 不变
```

如果证据不足但仍值得人工查看，可以把 proposal 标记为 `needs-more-evidence`。不能发明类名、Topic、接口或项目归属来补齐 proposal。

## 8. proposal 为什么还不是事实

proposal 即使已经写了：

```text
verification_status = source-verified
```

它仍然只是“待人工确认的证据建议”。

原因是：

- 自动工具可能识别错项目或方向；
- 两段代码可能名称相似但没有实际调用；
- 一个 Topic 可能存在多个订阅者；
- 当前证据可能遗漏网关、代理或运行配置；
- proposed edge id 和 pin 还没有最终写入。

proposal 不能直接驱动 `project-develop` 或 `project-fix`。只有 `project-graph-human-edge` 接受 proposal 并写入 `edges.md` 后，它才成为当前项目的 confirmed edge。

## 9. 第四步：人工确认 edge

### 接受 proposal

对 Codex 说：

```text
确认 prop-20260807-001。
使用 project-graph-human-edge 写入 edge，并创建 cross-ref pin。
```

接受时会：

1. 再次检查 edge fingerprint 和 id 是否冲突；
2. 确认 `project_id` 和 anchor 不是本机绝对路径；
3. 用 `source=auto` 写入或更新 `edges.md`；
4. 将 proposal 标记为 `accepted`；
5. 将 candidate 标记为 `promoted`；
6. 将 candidate 的 `edge_id` 指向 confirmed edge；
7. 默认在 `cross-refs/index.md` upsert 一个 pin；
8. 在 `.llm-wiki/log.md` 记录结果。

### 拒绝 proposal

```text
拒绝 prop-20260807-001。
原因：本地 Feign Client 实际由网关适配，不直接调用 payment-service。
```

拒绝时：

- proposal 标记为 `rejected`；
- 不写 `edges.md`；
- 不写 `cross-refs/index.md`；
- candidate 标记为 `rejected` 或 `blocked`；
- candidate 的 `edge_id` 保持为空；
- 日志记录人工原因。

### 手工登记 edge

如果关系已经由研发明确确认，也可以不经过扫描和 proposal：

```text
使用 project-graph-human-edge 手工登记这条关系：
type: http
from_project: order-service
from_anchor: OrderCallbackController
to_project: payment-service
to_anchor: PaymentNotifyController
contract_summary: payment-service 调用 order-service 的支付通知接口，orderId 是幂等键
```

手工登记的 edge 使用：

```text
source = manual
```

如果要写成 `source-verified` 或 `runtime-verified`，仍必须在当前会话核对对应证据，不能仅凭人工填写状态或日期。

## 10. edge 和 cross-ref pin 如何配合

`edges.md` 保存关系事实，例如：

```markdown
| edge_id | fingerprint | type | source | from_project | from_anchor | to_project | to_anchor | contract_summary | verification_status | last_verified |
|---|---|---|---|---|---|---|---|---|---|---|
| edge-20260807-001 | `feign:order-service:paymentclient:payment-service:paymentcontroller` | feign | auto | order-service | `PaymentClient` | payment-service | `PaymentController` | order-service 通过 Feign 创建支付单 | source-verified | 2026-08-07 |
```

`cross-refs/index.md` 只保存常用导航入口：

```markdown
| id | edge_id | local_entry | why_pinned | owner_note |
|---|---|---|---|---|
| xref-payment-create | edge-20260807-001 | `PaymentClient#createPayment` | 支付创建链路入口 |  |
```

pin 里不能复制：

- `contract_summary`；
- `verification_status`；
- `last_verified`；
- `remote_project`；
- `remote_anchor`。

查询时先通过 pin 找到 `edge_id`，再进入 `edges.md` 读取关系事实。如果 edge 后来过期，pin 可以保留，但查询必须报告它引用的 edge 已过期。

确认 edge 时默认创建 pin。只有人在确认时明确说“跳过 pin”，才允许不创建，并且必须在 `.llm-wiki/log.md` 记录原因。

## 11. Feign 跨项目调用示例

假设：

```text
order-service 的 PaymentClient
调用 payment-service 的 PaymentController#createPayment
```

规范方向是：

```text
caller/client -> provider/server
order-service -> payment-service
```

### 11.1 扫描 candidate

```text
使用 project-graph-candidates-scan 扫描 order-service 支付模块中的 Feign 关系。
```

候选应表达：

```text
relation: feign-client
local_anchor: PaymentClient#createPayment
remote_project: payment-service 或 unknown
remote_anchor: PaymentController#createPayment 或 unknown-anchor
status: pending
edge_id: 空
```

### 11.2 生成 proposal

```text
使用 project-graph-auto-edge 处理该 Feign candidate。
通过 Base Graph 找到 payment-service，
核对本地 Feign 声明和外部 Controller 映射，只生成 proposal。
```

需要核对两侧证据：

```text
本地：PaymentClient 的服务名、方法、HTTP 路径和请求 DTO
外部：PaymentController 的路径、方法、请求 DTO 和实际所属项目
```

只有两侧都匹配，proposal 才可以建议 `source-verified`。如果只看了本地 Feign Client，应保持 `unverified` 或 `needs-more-evidence`。

### 11.3 人工确认

```text
确认这个 Feign proposal，写入 edge，并创建 PaymentClient 的 cross-ref pin。
```

接受后检查：

- edge 方向是 `order-service -> payment-service`；
- edge 的 source 是 `auto`；
- proposal 是 `accepted`；
- candidate 是 `promoted` 且关联正确 edge id；
- pin 只引用 edge id；
- 外部 payment-service 没有被修改。

## 12. MQTT 发布订阅示例

假设：

```text
device-service 发布 topic：drone/{deviceId}/status
monitor-service 订阅该 topic
alarm-service 也订阅该 topic
```

MQTT 的规范方向是：

```text
publisher -> subscriber
```

多个订阅者必须拆成多条 edge：

```text
edge 1: device-service -> monitor-service
edge 2: device-service -> alarm-service
```

不能为了简化写成一条：

```text
device-service -> monitor-service, alarm-service
```

### 12.1 扫描候选

在 `device-service` 中说：

```text
使用 project-graph-candidates-scan 扫描 MQTT 发布关系，
重点检查 drone/{deviceId}/status 的发布方和远程项目提示。
```

如果扫描器只知道本项目发布 Topic，不知道订阅项目，应保留：

```text
remote_project = unknown
status = pending
```

不能根据 Topic 名称猜测订阅者。

### 12.2 生成 proposal

```text
通过 Base Graph 查找可能订阅该 Topic 的项目，
只读核对 monitor-service 和 alarm-service 的订阅配置，
分别生成 proposal。
```

需要核对：

- 发布端实际 Topic 模板；
- 是否有环境前缀、租户前缀或设备类型前缀；
- 订阅端 Topic Filter 是否匹配；
- QoS、Consumer Group 或共享订阅是否影响关系语义；
- 发布端和订阅端是否属于规范 `project_id`。

Topic 名称相同但环境前缀不同，不能直接确认关系。只有配置和代码均匹配时，才建议 `source-verified`。

### 12.3 人工确认

分别确认两个 proposal：

```text
确认 monitor-service 的 MQTT proposal，写入 edge 和 pin。
确认 alarm-service 的 MQTT proposal，写入另一条 edge 和 pin。
```

最终应得到两条独立 edge，便于后续判断某个订阅方是否过期、下线或变更。

## 13. 验证状态如何使用

`verification_status` 不是从低到高的数字评分，而是证据类型：

| 状态 | 含义 | 能否直接驱动开发 |
|---|---|---|
| `unverified` | 人确认过意图，但没有当前源码或运行证据 | 不能 |
| `source-verified` | 本地和外部两侧源码、接口或配置证据已核对 | 新鲜且相关时可以 |
| `runtime-verified` | 除源码外，还有日志、trace、线上行为或部署配置证据 | 新鲜且相关时可以 |

注意：

- `source-verified` 不是只看当前项目源码；跨项目关系需要核对两侧；
- `runtime-verified` 必须先有源码证据，再有运行证据；
- `last_verified` 来自实际验证日期，不能由用户手工填写后直接接受；
- 不在 edge 中持久化 `stale`，而是根据 `last_verified` 和当前阈值计算；
- 默认 edge 新鲜度阈值为 30 天；
- proposal 中的验证状态仍是“待确认的证据元数据”。

只有新鲜、相关并且 `source-verified` 或 `runtime-verified` 的 confirmed edge 可以驱动 `project-develop` 或 `project-fix`。

## 14. 查询和维护入口

完成 edge 后，可以使用以下入口：

### 查询关系

```text
使用 project-query 查询这个 Feign 接口或 MQTT Topic 对应的外部项目和 confirmed edge。
```

查询顺序：

```text
pin -> edge -> candidate
```

### 重新扫描候选

```text
使用 project-graph-candidates-scan 刷新当前项目候选关系。
```

### 审计图谱一致性

```text
使用 project-maintain 审计当前项目的 Project Graph，
检查重复 fingerprint、失效 pin、过期 edge 和未处理 candidate。
```

### 生成可视化

```text
使用 project-graph-visualize 生成或刷新 Base Graph 的 Project Graph HTML 可视化。
```

可视化只是现有图谱数据的展示，不会替代 candidate、proposal 和人工 edge 确认流程。

## 15. 推荐验收清单

### candidate 扫描

- [ ] 只扫描当前业务项目；
- [ ] 新候选状态为 `pending`；
- [ ] candidate 的 `edge_id` 为空；
- [ ] evidence 使用相对路径或稳定 anchor；
- [ ] 没有修改 edge、proposal、pin、Base 或外部项目；
- [ ] 外部到外部的发现没有进入当前 candidates。

### proposal 生成

- [ ] remote project 已解析为规范 project id，或明确保持 unresolved；
- [ ] 本地证据已核对；
- [ ] 外部证据按需只读核对；
- [ ] proposal 的方向符合关系类型；
- [ ] candidate 从 `pending` 变为 `proposed`；
- [ ] `edges.md` 和 `cross-refs/index.md` 没有变化；
- [ ] proposal 没有被描述为 confirmed fact。

### 人工确认

- [ ] edge id 和 fingerprint 唯一；
- [ ] 接受 proposal 后 edge 的 source 是 `auto`；
- [ ] 手工登记 edge 的 source 是 `manual`；
- [ ] accepted proposal 能找到 confirmed edge；
- [ ] promoted candidate 能找到 confirmed edge；
- [ ] rejected/blocked candidate 的 `edge_id` 为空；
- [ ] pin 引用存在的 edge id；
- [ ] 跳过 pin 时日志记录了人工原因；
- [ ] 图谱记录中没有本机绝对路径；
- [ ] 外部项目没有被修改。

## 16. 常见错误

### 错误 1：扫描后直接写 edge

扫描器只能写 candidate。正确流程是 candidate -> proposal -> human edge。

### 错误 2：proposal 标注 source-verified 就当成事实

proposal 仍然需要人工接受。确认事实只存在于 `edges.md`。

### 错误 3：只核对调用方，就写 source-verified

跨项目关系需要核对本地和外部两侧证据。只看一侧时应保持 `unverified` 或请求更多证据。

### 错误 4：为了当前项目好看而反转方向

Feign/HTTP/RPC 使用 caller -> provider，MQTT 使用 publisher -> subscriber。方向不能根据当前项目位置调整。

### 错误 5：一个 MQTT Topic 的多个订阅者合成一条 edge

每个 publisher -> subscriber 关系单独一条 edge。

### 错误 6：把 contract summary 复制到 pin

pin 只保存导航入口和 `edge_id`。关系事实只存放在 `edges.md`。

### 错误 7：业务项目会话直接修改 Base Graph overview

业务项目可以生成 Base Graph handoff 或更新建议，但不能直接写 Base tracked files。

### 错误 8：验证外部关系时顺手修改外部项目

外部项目默认只读。需要外部修改时，生成 context handoff 并在对方项目单独执行。

### 错误 9：把本机路径写进 edge 或 candidate

图谱使用逻辑 project id 和仓库相对 anchor。本机目录只保存在被 Git 忽略的 registry 文件中。

## 17. 一句话使用流程

```text
1. 用 project-init 准备业务项目的 Project Graph 文件。
2. 用 project-graph-candidates-scan 扫描当前项目，只写 pending candidate。
3. 选择 candidate，用 project-graph-auto-edge 定位外部项目并核对两侧证据。
4. auto-edge 只写 proposal，并把 candidate 改成 proposed。
5. 由人使用 project-graph-human-edge 接受或拒绝 proposal。
6. 接受后写 confirmed edge、promoted candidate 和 cross-ref pin。
7. 查询和开发时只依赖新鲜且已验证的 confirmed edge。
```

## 18. 最重要的原则

```text
Base Graph 负责找到项目。
Candidate 负责保留线索。
Proposal 负责等待判断。
Edge 负责保存人工确认后的关系事实。
Pin 负责快速找到 edge。
外部项目默认只读。
```

如果只记住一句话：

**自动化可以发现关系、整理证据和提出建议，但只有经过人工确认的 edge 才是 Project Graph 事实。**
