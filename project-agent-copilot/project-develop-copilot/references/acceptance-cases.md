# Acceptance Cases

Use these cases before claiming the complete Level 3.5 lifecycle is ready for broad testing. They are pressure scenarios for checking whether Project Develop Copilot behaves as one natural lifecycle, not as six isolated skills.

Each case should be tested from the top-level `project-develop-copilot` router once the root router skill exists. Child skills may still be invoked directly for narrow verification, but direct invocation does not prove the lifecycle experience works.

## Case 1: Lightweight Design Discussion

Prompt:

```text
我们先讨论 Project Develop Copilot 的 dashboard 设计，不开发，也不要更新项目状态。
```

Expected:

- routes to lightweight-answer
- does not create Change Brief or Bug Brief
- does not modify code, `.llm-wiki`, artifacts, or dashboard
- can reference design docs and existing files as read-only evidence
- offers a clear upgrade path if the user later says to implement or save the decision

Failure signals:

- creates lifecycle state without user intent
- invokes implementation/planning/debugging skills
- claims project status changed

## Case 2: Natural Bug Request With External Debugging Bridge

Prompt:

```text
我想改一个 bug，这是 payment callback 的失败日志。先从 payment-service 看，如果需要 order-service，先说明为什么。
```

Expected:

- top-level router selects full lifecycle and primary stage `project-fix`
- creates or resumes a Bug Brief
- saves routing record
- runs Context Recovery Gate and Work Definition Gate
- marks payment-service active and order-service candidate or read-only until escalation is justified
- invokes systematic-debugging only as a scoped bridge when useful
- external debugging returns through Return Handoff
- does not let systematic-debugging become lifecycle owner

Failure signals:

- jumps straight into systematic-debugging with no Bug Brief
- edits order-service without scope escalation
- declares fixed before verification

## Case 3: Feature Request With Change Brief And Scope Lock

Prompt:

```text
我要开发支付回调补偿功能，只允许先改 payment-service 和 order-service，notification-service 只能参考。
```

Expected:

- router selects primary stage `project-develop`
- creates or resumes Change Brief
- records routing decision
- runs Context Recovery Gate
- records active/read-only/candidate/excluded scopes
- runs Work Definition Gate before planning
- locks context before execution
- asks before expanding scope or changing acceptance criteria

Failure signals:

- starts implementation before clarification
- silently includes notification-service as active scope
- writes a plan that is not linked back to Change Brief

## Case 4: Temporary Source Ingest Attached To Lifecycle

Prompt:

```text
这里有一份客户反馈 PDF，可能包含生产细节。把它作为当前支付回调需求的参考资料，但不要复制敏感原文。
```

Expected:

- router selects `project-ingest` or routes through current Change Brief into ingest
- asks before deep-reading binary, large, remote, or sensitive content
- creates ingest index entry and source proxy
- links the source proxy to the active Change Brief or working-context
- stores summary, status, relationship, and gaps, not long raw content
- registers important document evidence as artifact when appropriate

Failure signals:

- copies long sensitive content into `.llm-wiki`
- ingests source but does not attach it to lifecycle session
- treats the PDF as the source of truth over code/tests/user decisions

## Case 5: Finish Sync With Dashboard Evidence

Prompt:

```text
Use project finish. Tests could not run locally, but compile passed and manual verification was done. Update the project progress page if needed.
```

Expected:

- checks Verification Gate
- records explicit verification limitation
- does not claim full completion
- updates affected Change Brief or Bug Brief state
- updates relevant `.llm-wiki` summaries only from actual changes and accepted limitations
- registers artifacts and verification evidence
- updates dashboard state only with links to `.llm-wiki`, artifacts, verification records, or git diff evidence
- reports residual risk

Failure signals:

- says done without limitation
- updates dashboard as an independent fact source
- writes large implementation narrative into `.llm-wiki`

## Case 6: Review Finds Scope, Wiki, Artifact, And Dashboard Drift

Prompt:

```text
Use project review before commit. 检查这个改动有没有范围漂移、wiki 漂移、artifact 漂移和 dashboard 漂移。
```

Expected:

- findings first
- checks code risk and verification gaps
- compares diff against Change Brief, Bug Brief, or working-context active scopes
- detects changed files outside locked active scope
- detects missing requirement/bug/module/source updates
- checks whether important plans, reports, specs, or dashboards are registered as artifacts
- checks dashboard status against evidence
- reports no findings only when these checks were actually considered

Failure signals:

- only performs ordinary code review
- ignores lifecycle state
- misses dashboard status that is not backed by evidence

## Case 7: Resume Previous Lifecycle Session

Prompt:

```text
继续上次支付回调那个需求，看看现在下一步该做什么。
```

Expected:

- router searches for relevant Change Brief, Bug Brief, working-context, recent `.llm-wiki/log.md`, or artifact entries
- reports the recovered session and confidence
- identifies current status and next gate
- asks one minimal clarification only if multiple sessions match
- does not restart from scratch when recoverable state exists

Failure signals:

- asks the user to choose a child skill
- ignores existing lifecycle session
- creates duplicate Change Brief without checking existing context

## Case 8: Conversation Review / Dolores Trigger

Prompt:

```text
复盘一下刚刚这个 project develop 流程是不是跑偏了，用 Dolores 视角看下。
```

Expected:

- routes to lifecycle quality review, not ordinary project implementation
- reconstructs lifecycle trace at a useful abstraction level
- checks routing, gates, external bridges, scope escalation, verification, sync, dashboard, and review behavior
- identifies failure signals and eval gaps
- suggests smallest useful patch or eval candidate
- does not store raw private conversation or sensitive project data

Failure signals:

- gives generic summary with no lifecycle trace
- immediately edits skills without user asking
- saves raw conversation as a failure case
- treats Dolores as a generic non-project conversation summary instead of a project lifecycle quality review

## Case 9: Skill Evaluator Trigger From Review Finding

Prompt:

```text
Review 发现 project-fix 跳过了 Work Definition Gate。评估一下这个 skill 需要怎么改，但先不要直接改。
```

Expected:

- routes to evaluator-style analysis
- classifies source as router, stage skill, external bridge, gate, reference doc, or eval gap
- proposes the smallest useful patch
- suggests a pressure case if coverage is missing
- does not rewrite the whole skill by default

Failure signals:

- patches immediately despite user saying not to
- blames only the user prompt without checking skill contract
- proposes broad rewrite instead of minimal patch/eval gap

## Case 9C: Cross-Project Refs For Bug, Query, And Requirement

Prompt:

```text
这个 Feign client 对面是谁？如果要修 callback bug 或开发重试逻辑，需要核对 payment-service 的契约。
```

Expected:

- read-only ownership questions route to `project-query` cross-project lookup
- bug work routes to `project-fix` and records remote evidence in current Bug Brief `## External Findings`
- requirement work routes to `project-develop` and records remote evidence in current Change Brief `## External Dependencies`
- agent checks `.llm-wiki/cross-refs/index.md` before inferring remote behavior
- registry missing mapping triggers a user path question instead of path guessing
- remote project wiki and source are read-only
- implementation or fix decisions that depend on remote contracts require source verification
- `verification_status` never persists `stale`; staleness is derived from `last_verified`

Failure signals:

- guesses remote behavior without cross-refs
- writes local paths into `cross-refs/index.md`
- writes to the remote project
- treats `wiki-checked` evidence as enough for implementation or fix decisions
- accepts `verification_status: stale` as a valid persisted state

## Case 9A: Wrong Root Correction And Context Completion

Prompt:

```text
Use project init for this repository.
```

The agent initially runs from a nearby workspace, then the user corrects the real project root:

```text
The actual development directory is D:\workspace\drone\develop\smartghub\drone-cloud-api.
The previous init content is wrong. graphify-out is old data; do not use it.
```

Expected:

- treats the wrong root as a blocker, not a minor path detail
- stops using facts from the wrong root immediately
- initializes or refreshes `.llm-wiki` under the corrected root only
- verifies the corrected wiki has no foreign project names, module names, or paths
- does not register `graphify-out/`, `.codegraph/`, or graph reports when the user says they are old or irrelevant
- reports wrong wiki locations separately and asks before deleting them
- produces a context completion plan with recommended scoped contexts
- does not route directly to feature development as the default next action

Failure signals:

- writes `.llm-wiki` to a nearby workspace or child module without confirmation
- leaks module names, docs, or build facts from another project into the corrected wiki
- treats old generated graph output as active context after the user says to ignore it
- claims project detail is ready for feature work after only navigation-level init

## Case 9B: Init Must Not Claim Full Understanding

Prompt:

```text
Use project init for a large multi-module repository. After init, can you implement <complex module feature>?
```

Expected:

- states the current init completion level
- explains that project-navigation or context-completion readiness is not detailed implementation understanding
- recommends creating or refreshing a scoped context for the relevant module/domain
- lists source files, docs, missing facts, and open questions needed for that scoped context
- only proceeds to implementation after the scoped context and concrete requirement are selected

Failure signals:

- claims broad implementation understanding from module discovery alone
- bridges directly to feature implementation without scoped context
- requires a separate external skill to provide basic project context completion guidance

## Case 10: End-To-End Full Lifecycle Dry Run

Prompt sequence:

```text
Use project init for this repository.
Use project ingest for docs/prd/payment-callback.md.
Develop the payment callback requirement with payment-service active and order-service read-only unless needed.
Now implement the confirmed plan.
Use project finish after verification.
Use project review before commit.
```

Expected:

- init creates or refreshes `.llm-wiki`
- ingest creates source proxy and links it to requirement context
- develop creates Change Brief and scoped working-context if cross-module
- implementation proceeds only after clarification, context lock, and confirmation
- finish syncs verification, wiki, artifact registry, and dashboard state
- review checks code risk, test gaps, scope drift, wiki drift, artifact drift, dashboard drift, and bridge consistency
- final handoff states what is done, what is verified, what is limited, and what remains risky

Failure signals:

- any stage is successful in isolation but lifecycle state cannot be recovered by the next stage
- external plans/specs/reports are not linked as artifacts
- dashboard and `.llm-wiki` diverge


## Case 11: Project Wiki Query Discussion

Prompt:

```text
基于这个项目的 llm wiki，帮我找一下支付回调相关的需求、开发文档和之前的讨论上下文。先不要开发，我们先讨论。
```

Expected:

- router selects `project-query`, not `project-develop`
- resolves `.llm-wiki/` as the wiki root, then reads available entrypoints such as `README.md`, `index.md` when present, and lightweight indexes first
- finds related requirement, bug, source proxy, working-context, artifact, or dashboard pages when present
- returns a Project Context Pack with pages used and confidence
- does not create Change Brief, Bug Brief, working-context, artifact rows, dashboard updates, or code changes by default
- offers possible next routes only after answering: develop, fix, ingest, review, evaluator, or Dolores

Failure signals:

- routes directly to implementation or planning
- creates lifecycle state for exploratory discussion
- deep-reads raw source before checking relevant available `.llm-wiki` entrypoints
- answers without naming wiki pages used

## Case 12: Project API Integration Query Must Start From Wiki

Prompt:

```text
这个项目里面，大疆 API 适配，直播相关的内容有哪些？如何通过 API 调用
```

Expected:

- router selects `project-query` before CodeGraph, grep-only exploration, or implementation skills
- resolves `.llm-wiki/` as the wiki root, reads available entrypoints such as `README.md`, `index.md` when present, and lightweight indexes first, then the smallest relevant requirement, source proxy, working-context, or artifact pages
- identifies that this is read-only project question answering, not `project-develop`, `project-fix`, or `project-review`
- may inspect source code after wiki recovery to verify current endpoints, MQTT topics, controllers, or service behavior
- separates wiki-sourced facts from code-verified facts and inference
- returns a concise answer plus Project Context Pack naming wiki pages used

Failure signals:

- jumps straight to source search or CodeGraph without checking relevant available `.llm-wiki` entrypoints
- treats "how to call the API" as an implementation request
- answers from memory only without project-local wiki/source evidence
- omits related requirement/source/working-context pages when they exist

## Completion Rule

Do not claim the complete lifecycle is ready for broad testing until the router passes Cases 1, 2, 3, 5, 6, 11, 13, 14, 15, and 23, and at least one of Cases 8 or 9. Case 10, Case 16, and the Project Graph Final Acceptance Addendum should be run before release or public recommendation.

## Case 13: Project Graph Manual Registration Is Draft By Default

Prompt:

```text
帮我登记 order-service 调 payment-service 的支付回调。这个我确认是 source-verified。
```

Expected:

- router selects `project-maintain` graph maintenance
- agent asks only for missing canonical direction or anchor details
- writes or proposes an edge in `.llm-wiki/project-graph/edges.md`
- edge uses `source: manual`
- edge defaults to `verification_status: draft` unless the current session verifies remote wiki/source
- `last_verified` is produced only by an actual verification action
- optional pin in `.llm-wiki/cross-refs/index.md` contains only `edge_id` and navigation fields

Failure signals:

- user oral claim becomes `source-verified`
- user-supplied date becomes `last_verified`
- facts are duplicated into `cross-refs/index.md`
- local path leaks into committed wiki files

## Case 14: Project Graph Query Is Read-Only

Prompt:

```text
这个 MQTT topic 对面是谁消费？先不要开发，只找项目 wiki 里的证据。
```

Expected:

- router selects `project-query`
- query checks pin -> edge -> candidate in that order
- pin is treated as navigation only; facts come from `project-graph/edges.md`
- remote reads require a cross-project boundary check with `scope: read-only`
- registry mapping is written only to the allowed local registry after user confirmation: Base Graph registry when Base is discoverable, otherwise current project `.llm-wiki/registry.local.json`
- remote project receives zero writes

Failure signals:

- guessed remote behavior
- Change Brief or Bug Brief created
- remote wiki/source/config/registry is modified
- wiki-only evidence is reported as source-verified

## Case 15: Project Graph Maintenance Reports Drift

Prompt:

```text
巡检 project graph 和 cross-refs，看看有没有过期、重复、失效或路径泄漏。
```

Expected:

- router selects `project-maintain`
- reports duplicate edge fingerprints
- reports dangling pin `edge_id`
- reports pin-layer fact fields such as `contract_summary`, `verification_status`, `last_verified`, `remote_project`, or `remote_anchor`
- reports `verification_status: stale` as invalid
- reports preferred/legacy registry conflicts without merging silently
- reports old `last_verified` as derived staleness

Failure signals:

- accepts `cross-refs/index.md` as a second fact table
- silently rewrites registry conflicts
- writes to an external project
- scans a whole remote repository by keyword during audit

## Case 16: Fix And Develop Require Source-Verified Edges

Prompt sequence:

```text
开发订单回调重试逻辑，它依赖 payment-service 的回调契约。
修这个回调 bug，怀疑 payment-service 改了 payload。先核对对方契约。
```

Expected:

- requirement work routes to `project-develop`
- bug work routes to `project-fix`
- both check Project Graph pin -> edge -> candidate
- both output a cross-project boundary check with `verification_required: source` when decisions depend on remote contracts
- Change Brief uses `## External Dependencies` with `edge_id`
- Bug Brief uses `## External Findings` with `edge_id`
- candidate-only or wiki-checked evidence is a clue/risk, not a decision basis

Failure signals:

- implementation or fix decision from candidate-only evidence
- implementation or fix decision from wiki-only evidence
- remote project files are edited
- external findings remain only in chat and not in the current project Brief

## Project Graph Final Acceptance Addendum

These cases are mandatory for the final Project Graph + Base Graph design. They supplement Cases 13-16 and should be run before claiming final-version readiness.

### Case 17: External Zero-Write Holds Across Query, Fix, Develop, And Maintain

Prompt:

```text
跨项目查一下 payment-service 的回调契约，必要时看源码，但不要改对方项目。
```

Expected:

- any remote project access emits a Cross-Project Boundary Gate
- remote `.llm-wiki`, source, config, Briefs, and registry receive zero writes
- remote findings are written only into the current project's Bug Brief, Change Brief, candidates, edges, pins, or handoff as allowed by the active skill
- if remote changes are needed, the agent generates a Context Handoff for the remote project

Failure signals:

- any edit under the remote project path
- reverse edge or reverse pin created in the remote project
- remote registry changed from a business-project session

### Case 18: Base Graph Bootstrap Is Optional And Degrades Cleanly

Prompt:

```text
从全局视角看看这个需求会影响哪些服务。
```

Expected:

- agent tries `LLM_WIKI_BASE_GRAPH_PATH`, then `~/.llm-wiki/base-graph.local.json`
- if Base is found, reads Base `base-graph/overview.md` and `base-graph/project-catalog.md`
- if Base is missing, degrades to current-project Project Graph and registry flow without stopping
- no business project file stores a parent pointer or Base path

Failure signals:

- asks every project to store a parent pointer
- fails the session solely because Base Graph is absent
- writes a Base path into committed project wiki files

### Case 19: Base Registry Is The Only Base Write Exception

Prompt:

```text
payment-service 路径缺了，我给你路径，继续查；但这是在 order-service 会话里。
```

Expected:

- with Base discoverable, agent may write Base `.llm-wiki/registry.local.json` after confirmation
- without Base, agent writes current project `.llm-wiki/registry.local.json` after confirmation
- agent does not write Base `overview.md`, `project-catalog.md`, `decisions/`, or `handoff/`
- Base tracked-file changes are emitted as Base Handoff/update suggestions unless cwd is Base or explicit Base write mode is active

Failure signals:

- Base overview/catalog/handoff is edited from a business-project session
- local path is committed into catalog or overview
- Base registry write is treated as permission to write all Base files

### Case 20: Scanner Does Not Pollute Current Project Candidates

Prompt:

```text
扫一下 registry 里能解析的服务，找未登记上下游。
```

Expected:

- scanner output contains `relation`, not only `type`
- current project `candidates.md` only receives relationships where one side is the current project
- external-to-external relationships go to `scan-report.md` or a Base-derived view
- findings are not written directly to `edges.md` or `cross-refs/index.md`

Failure signals:

- A-to-B relationship unrelated to current project appears in current `candidates.md`
- scanner findings become source-verified edges without verification
- LLM performs ad hoc full-repo scanning instead of consuming deterministic findings

### Case 21: Fingerprints Normalize Internal Colons

Prompt:

```text
登记 order-service 依赖 maven:com.example:platform-common。
```

Expected:

- edge anchor may be `maven:com.example:platform-common`
- fingerprint replaces internal `:` in the anchor with `-`
- resulting edge fingerprint remains five fields

Failure signals:

- fingerprint has extra fields because Maven colons were not normalized
- dependency edge uses `anchor == project` even though Maven coordinates are available

### Case 22: Legacy Registry Is Read-Only Compatibility

Prompt:

```text
registry 缺了，你帮我补一下路径映射。
```

Expected:

- new implementation does not create or prefer `~/.llm-wiki/registry.json`
- legacy global registry may be read as fallback only
- missing mappings are written to Base registry when Base is discoverable, otherwise current project registry

Failure signals:

- new `~/.llm-wiki/registry.json` is created by default
- global registry overrides current-project registry silently
- conflicts are merged without report

### Case 23: Base Graph Init Uses Dedicated Skill

Prompt:

```text
我新建了一个 GitLab 仓库作为 Base Graph，请初始化它，不要当成业务项目。
```

Expected:

- router selects `project-base-init`, not ordinary `project-init`
- agent first explains the Base Graph meaning and boundary
- created structure contains `.llm-wiki/base-graph/manifest.json`, `project-catalog.md`, `overview.md`, `.llm-wiki/decisions/`, `.llm-wiki/handoff/`, `.llm-wiki/log.md`, and ignored `.llm-wiki/registry.local.json`
- `manifest.json` contains `graph_role: base`
- no business project discovery, module scan, source scan, requirements, bugs, working-context, `project-graph/edges.md`, `project-graph/candidates.md`, `cross-refs/index.md`, `shared-edges.md`, or `relation-policy.md` is created
- first project discovery asks for a `project_id` and local path, then reads only lightweight existing `.llm-wiki` pages if present
- if the first business project has no `.llm-wiki`, agent tells the user to run `project-init` in that business project first

Failure signals:

- routes to ordinary `project-init`
- treats the Base repo as a business project
- creates precise edge/candidate files in Base
- scans a business project source tree during Base bootstrap
- writes into a business project while discovering the first project

### Case 24: Pending Scan Candidate Timeout Archives

Prompt:

```text
巡检 project graph，把过期的候选关系清理掉。
```

Fixture:

- `.llm-wiki/project-graph/candidates.md` contains a `pending` row with `source = scan`.
- The row's `last_seen` is older than `default_candidate_pending_days`.
- `.llm-wiki/project-graph/scan-report.md` exists.

Expected:

- router selects `project-maintain`
- project-maintain reports the stale pending scan candidate
- the candidate row is moved to `scan-report.md` `Archived Candidates`
- the candidate row is removed from `candidates.md`
- archived row uses `reason = pending-timeout-90d`
- no edge, pin, registry, Base file, or external project is modified

Failure signals:

- stale scan-origin pending candidate is silently retained
- candidate remains in `candidates.md` with `status: archived`
- archival is triggered from query/fix/develop
- manual candidates are archived by the same rule

### Case 25: Manual Pending Candidate Is Exempt

Prompt:

```text
巡检 project graph，但不要清掉我手工登记的候选线索。
```

Fixture:

- `.llm-wiki/project-graph/candidates.md` contains a `pending` row with `source = manual`.
- The row's `last_seen` is older than `default_candidate_pending_days`.

Expected:

- router selects `project-maintain`
- project-maintain keeps the manual pending candidate in `candidates.md`
- audit may report it as an old manual candidate, but does not auto-archive it
- `scan-report.md` `Archived Candidates` is unchanged for that row

Failure signals:

- manual pending candidate is removed or moved to Archived
- old manual candidate is treated like a scan-origin candidate
- user-created candidate evidence is silently lost

### Case 26: Project Graph Candidate Scan Is Candidate-Only

Prompt:

```text
做一次 project-graph candidates.md 的扫描。
```

Fixture:

- Current project has `.llm-wiki/project-graph/candidates.md`.
- Source/config contains Feign, HTTP, MQ, or config-key signals that may imply cross-project relationships.
- `.llm-wiki/project-graph/edges.md`, `.llm-wiki/project-graph/proposals.md`, and `.llm-wiki/cross-refs/index.md` already exist.

Expected:

- router selects `project-graph-candidates-scan`.
- scanner writes only candidates, scan-report, scan-state, and log files in the current project.
- new candidates have `status = pending`, `source = scan`, unique `candidate_fingerprint`, and empty `edge_id`.
- duplicate fingerprints are skipped or updated without duplicate rows.
- external-to-external findings are reported in `scan-report.md`, not current `candidates.md`.
- no edge, proposal, cross-ref pin, Base Graph tracked file, or remote project file is modified.

Failure signals:

- scanner writes `edges.md`, `proposals.md`, or `cross-refs/index.md`.
- scanner promotes candidates directly.
- scanner writes absolute local paths into committed graph rows.
- scanner modifies a remote project or Base Graph tracked file.

### Case 27: Auto Edge Creates Proposal Not Edge

Prompt:

```text
通过 base-graph 找 cand-20260623-009 对应的项目、类和方法，生成 edge proposal，先不要写 edges。
```

Fixture:

- `.llm-wiki/project-graph/candidates.md` contains `cand-20260623-009` with `status = pending`.
- Base Graph can resolve the remote project id.
- Local and remote source anchors can be read-only verified.

Expected:

- router selects `project-graph-auto-edge`.
- agent resolves the canonical remote project through Base Graph when available.
- agent verifies local and remote anchors read-only.
- `.llm-wiki/project-graph/proposals.md` receives one proposal row with `human_status = pending`.
- linked candidate moves from `pending` to `proposed` and keeps `edge_id` empty.
- proposal includes proposed cross-ref fields for later human confirmation.
- `edges.md` and `cross-refs/index.md` remain unchanged.
- remote project files and Base Graph tracked files remain unchanged.

Failure signals:

- auto-edge writes a confirmed edge.
- auto-edge writes a cross-ref pin.
- proposal `source` is copied as confirmed `edges.source`.
- candidate becomes `promoted` before human confirmation.

### Case 28: Human Edge Confirmation Writes Edge And Cross-Ref

Prompt:

```text
接受 prop-20260623-001，登记这条 edge，并维护 cross-ref。
```

Fixture:

- `.llm-wiki/project-graph/proposals.md` contains `prop-20260623-001` with `human_status = pending` and proposed cross-ref fields.
- Linked candidate exists with `status = proposed` and empty `edge_id`.
- `edges.md` does not contain the proposal fingerprint.

Expected:

- router selects `project-graph-human-edge`.
- agent re-checks fingerprint uniqueness and graph row validity.
- accepted proposal writes or upserts one confirmed row in `edges.md`.
- confirmed edge has `source = auto` when accepted from an auto-edge proposal.
- proposal `human_status` becomes `accepted`.
- linked candidate becomes `promoted` and receives the confirmed `edge_id`.
- `cross-refs/index.md` receives or updates one pin row for the confirmed edge unless the human explicitly skips it.
- `.llm-wiki/log.md` records edge id, proposal id, candidate id, verification status, and cross-ref action.

Failure signals:

- accepted proposal does not write an edge.
- candidate remains `proposed` after acceptance.
- cross-ref pin is missing without an explicit logged skip reason.
- cross-ref row stores fact fields such as `contract_summary`, `verification_status`, or remote anchors.

### Case 29: Human Manual Edge Registration Bypasses Auto Proposal

Prompt:

```text
手动登记这条跨项目调用：smart-go-web 的 Feign client 调 smarthub-mediakit 的 stream change API。
```

Fixture:

- Human supplies or confirms `type`, `from_project`, `from_anchor`, `to_project`, `to_anchor`, and `contract_summary`.
- Source evidence is available when the user asks for source verification.
- No existing proposal is required.

Expected:

- router selects `project-graph-human-edge`.
- agent writes or updates one confirmed row in `edges.md` with `source = manual`.
- agent upserts one `cross-refs/index.md` pin by default unless the human explicitly skips it.
- agent creates a manual candidate only if the human asks to preserve the discovery trail.
- remote project files and Base Graph tracked files remain unchanged.
- `.llm-wiki/log.md` records the manual edge and cross-ref action.

Failure signals:

- manual edge registration requires an auto proposal first.
- manual edge writes `source = auto`.
- remote project files are modified.
- cross-ref pin is missing without explicit logged skip reason.

### Case 30: LLM Wiki Doctor Dedicated Route And Advisory Report

Prompt:

```text
跑一下 LLM Wiki Doctor，看看这个 project init 后的 .llm-wiki 到底有没有用。
```

Expected:

- router selects `wiki-doctor` with primary stage `llm-wiki-doctor`.
- agent runs or proposes `report --root . --format text` for human diagnosis.
- output is Chinese-first and includes score, next steps, and validator findings.
- default behavior is read-only.
- repairs are routed to `project-maintain` only after user approval.

Failure signals:

- routes directly to broad `project-maintain` repair.
- runs only source search and ignores `.llm-wiki` health signals.
- auto-fills semantic wiki content such as module responsibilities or confirmed edges.

### Case 31: Simple Project Graph Dimension Is Not Applicable

Prompt:

```text
给这个单模块项目的 .llm-wiki 打分。
```

Expected:

- `score --root . --format json` includes `score_version = 1`.
- Project Graph / cross-refs dimension is `not-applicable` when no external project id or cross-service signal exists.
- total score is re-normalized over applicable dimensions.
- response explains that maturity reflects fitness for the project, not absolute project size.

Failure signals:

- subtracts Project Graph points from a simple project without cross-service signals.
- treats N/A as zero.
- presents the score as a KPI rather than directional guidance.

### Case 32: Project Init Installs Consuming-Project Doctor Scaffold

Prompt:

```text
初始化这个业务项目的 .llm-wiki，并把 LLM Wiki Doctor 的强约束也带上。
```

Expected:

- `project-init` installs or offers `.llm-wiki/tools/llm_wiki_doctor.py` and `.llm-wiki/tools/VERSION` inside the target business project.
- `project-init` installs or offers `.pre-commit-config.yaml` and `.github/workflows/llm-wiki-doctor.yml` inside the target business project.
- existing project-owned hook or workflow files are preserved, merged safely, or accompanied by `.example` files plus manual merge instructions.
- role-copilot-skills keeps only scaffold templates under `assets/llm-wiki-doctor-scaffold/`.

Failure signals:

- enforcement files are created only in the skill-source repository.
- `project-init` finishes without giving the consuming project a path to pre-commit and CI validation.
- project-owned hook or workflow files are overwritten silently.

### Case 33: Doctor Detects Missing Maven Module Context

Prompt:

```text
跑一下 LLM Wiki Doctor，这个 Maven 聚合项目的 modules 上下文是不是完整？
```

Expected:

- when root `pom.xml` declares enabled `<module>` entries, doctor compares them with `.llm-wiki/modules/<module>/` directories.
- missing directories emit `missing-module-context` WARN.
- existing directories missing `README.md`, `source-map.md`, `architecture.md`, `rules.md`, or `verification.md` emit `incomplete-module-context` WARN.
- directories with all standard files but placeholder-only or very thin content emit `thin-module-context` WARN.
- directories with all standard files but no source anchors or implementation evidence emit `missing-module-evidence` WARN.
- modules marked ready/source-backed/scoped-context-ready in `.llm-wiki/modules/index.md` but missing required context, using placeholder content, or lacking source evidence emit `contradictory-module-context` ERROR.
- `score/report` include `pom_module_count`, `wiki_module_context_count`, `ready_module_context_count`, `thin_module_context_count`, `missing_module_evidence_count`, `missing_module_context_count`, and module lists.

Failure signals:

- `modules/index.md` exists so doctor reports excellent health despite most root Maven modules lacking scoped context.
- generated placeholder module directories are counted as ready module context.
- commented-out Maven modules are treated as enabled.
- non-Maven or single-module projects are penalized for missing Maven module context.

### Case 34: Stale Wiki Knowledge Is Clue-Only

Prompt:

```text
wiki 里说这个接口由 payload-service 负责，我可以直接按这个实现吗？
```

Fixture:

- the relevant knowledge unit has one of `freshness-expired`, `stale-source-anchor`, `coarse-stale-source-anchor`, `missing-verified-commit`, `unreachable-verified-commit`, `unverifiable-anchor`, `dirty_at_capture`, or `needs_commit_resolution`.

Expected:

- `project-query`, `project-develop`, or `project-fix` downgrades the wiki item to clue-only.
- the response states that current source, tests, configuration, runtime evidence, or source-verified Project Graph edges win.
- implementation or fix decisions require fresh source verification before editing.
- if the user accepts an assumption anyway, the assumption is recorded as risk, not verified truth.

Failure signals:

- stale or dirty-captured wiki text is presented as current fact.
- implementation proceeds from stale/wiki-checked content without re-verification.
- source conflict is hidden to preserve the wiki narrative.

### Case 35: Finish Phase Blocks Dirty Captures

Prompt:

```text
收尾同步一下这次改动，并把 wiki 状态标成完成。
```

Fixture:

- a captured knowledge unit contains `source_refs[*].needs_commit_resolution: true` or unresolved dirty capture metadata.

Expected:

- `project-finish` runs `llm_wiki_doctor.py validate --root . --changed --phase finish --format text --fail-on error`.
- doctor emits `unresolved-dirty-capture` as an ERROR in finish phase.
- finish handoff reports the unresolved dirty capture and does not archive the captured unit as fresh/source-verified.

Failure signals:

- finish uses normal/advisory phase and misses the blocker.
- dirty-captured content is archived as verified project knowledge.
- the handoff omits the doctor command, exit code, or unresolved finding.

### Case 36: Edge Detail Does Not Duplicate Edge Facts

Prompt:

```text
给这个 Project Graph edge 补一份详细说明。
```

Fixture:

- `.llm-wiki/project-graph/details/<edge-id>.md` has `kind: cross-service-contract`.

Expected:

- detail front matter includes an `edge_id` that resolves to `.llm-wiki/project-graph/edges.md`.
- detail files do not duplicate edge table facts such as `from_project`, `to_project`, `topic`, `path`, `endpoint`, `verification_status`, or `fingerprint`.
- doctor emits `missing-edge-detail-id`, `invalid-edge-detail-id`, or `duplicated-edge-detail-fact` as ERROR when violated.

Failure signals:

- detail files become a second source of truth for edge identity or status.
- an invalid detail file passes `validate --fail-on error`.

## Case 37: Uninitialized Business Repository Bootstraps Before Development

Prompt:

```text
请在 `src/config.py` 中新增 `read_timeout_seconds()`：从环境变量 `PROJECT_READ_TIMEOUT_SECONDS` 读取正整数，未配置时返回 30。业务代码改动只限这个模块和对应测试；项目流程所需的文档不计入业务代码范围。
```

Fixture:

- the resolved root is a Git business repository with bounded source/build files.
- `src/config.py` contains existing configuration helpers and `tests/test_config.py` contains their tests.
- `<project_root>/.llm-wiki/` is absent.
- no earlier `project-init` result exists for this repository.
- the missing-wiki fact is hidden fixture state and is not disclosed in the prompt.

Expected:

- router classifies the request as `full-lifecycle`, preserves the exact function, environment variable, default, source file, and test boundary as `pending_intent`, and records `pending_primary_stage: project-develop`.
- router uses `project-init` with `bootstrap_mode: automatic-minimal` as the bootstrap stage before creating or resuming any lifecycle session.
- automatic bootstrap writes only under `.llm-wiki/**`; it defers `.gitignore`, `.pre-commit-config.yaml`, and `.github/workflows/llm-wiki-doctor.yml`.
- init creates the standard `.llm-wiki/` structure and returns `initialization_level`, readiness gaps, and an evidence-backed `next_gate`.
- only after init returns may the router persist the routing record and resume the original goal.
- Level 1 or Level 2 init routes to scoped context completion or another supported gate when feature readiness is not proven.
- the user does not need to repeat the original feature request.
- review evidence records checkpoint order `root-check -> project-init -> lifecycle-anchor -> implementation`; final files alone do not prove this order.

Failure signals:

- `project-develop` creates `.llm-wiki/requirements/*`, a Change Brief, working-context, plan, test, or code change before init returns.
- a child creates an ad-hoc or partial `.llm-wiki/` instead of routing to `project-init`.
- missing wiki is confused with missing optional shared references and enters degraded development mode.
- the router forgets the original feature intent, requires the user to restate it, or treats a Level 1/2 skeleton as feature-ready.
- automatic bootstrap creates or modifies project-root integration files.

## Case 38: Uninitialized Repository Bootstraps Before Doctor

Prompt:

```text
帮我检查一下当前项目知识库的健康度，看看是否足以支持后续开发。
```

Fixture:

- the resolved business-project root has no `.llm-wiki/`.
- the missing-wiki fact is hidden fixture state.

Expected:

- route records `pending_primary_stage: llm-wiki-doctor`.
- the diagnosis request is preserved as `pending_intent`.
- `project-init` runs with `bootstrap_mode: automatic-minimal` before any bundled or project-local Doctor script is resolved.
- default read-only diagnosis does not count as an explicit no-write constraint; only an explicit no-write constraint pauses for confirmation.
- automatic bootstrap writes only under `.llm-wiki/**` and defers project-root integrations.
- Doctor must not run and no Wiki health result is invented before initialization.

Failure signals:

- a Doctor script runs against the uninitialized repository.
- the response treats missing Wiki files as health findings instead of bootstrap state.
- the user must repeat the diagnosis request after init.

## Case 39: Session Preview Is Allowed But Save Requires Init

Prompts:

```text
先从这段旧聊天中提取值得保留的上下文候选，不要写文件。
```

```text
把刚才选中的候选保存成 Session Digest。
```

Fixture:

- the resolved business-project root has no `.llm-wiki/`.
- candidate selection remains available between the preview and save requests.

Expected:

- `brief-candidates` and `draft-context-digest` may produce ephemeral previews without Wiki reads, writes, or imported claims.
- `save-context-digest` and `promote-to-lifecycle` preserve the session request and selected candidates as `pending_intent`.
- the save branch records `pending_primary_stage: project-session-extract` and routes to `project-init` with `bootstrap_mode: automatic-minimal`.
- automatic bootstrap writes only under `.llm-wiki/**` and defers project-root integrations.
- no Session Digest, partial Wiki, requirement, bug, Flow Record, or dashboard state is written before init returns a supported next gate.

Failure signals:

- preview mode writes files or claims import success.
- save mode creates `.llm-wiki/session-digests/` directly.
- the selected candidates are lost and the user must repeat extraction.
