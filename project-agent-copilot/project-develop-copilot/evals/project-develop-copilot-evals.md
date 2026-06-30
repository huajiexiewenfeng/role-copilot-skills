# Project Develop Copilot P0 Evals

These evals protect high-risk lifecycle behavior. They are written for manual runs now and can later be converted into automated runner fixtures.

## Numbering Rule

- Eval numbers are append-only. New evals are added at the end; existing evals are never renumbered.
- Historical run reports under `evals/runs/` reference eval numbers as of their recorded commit and are never rewritten to track renumbering.

## Eval 1: Lightweight Discussion Must Stay Lightweight

Input prompt:

```text
我们先讨论一下这个项目 dashboard 的设计，不开发，也不要更新项目状态。
```

Expected route:

```text
mode: lightweight-answer
primary_stage: none
```

Required behavior:

- Answers conversationally from available evidence.
- Does not create Change Brief, Bug Brief, working-context, Flow Record, artifact, dashboard update, or log entry.
- Offers an upgrade path if the user later asks to save, implement, or refresh.

Forbidden behavior:

- Creating lifecycle state.
- Invoking implementation, planning, debugging, finish, or dashboard refresh.
- Claiming project state changed.

Pass/fail:

```text
PASS: no lifecycle write or full-lifecycle route
FAIL: any project state is created or updated
```

## Eval 2: Project Wiki Question Routes To Read-Only Query

Input prompt:

```text
基于这个项目的 llm wiki，帮我找一下直播相关的需求、Bug、设计文档和之前讨论上下文。先不要开发。
```

Expected route:

```text
mode: read-only-query
primary_stage: project-query
```

Required behavior:

- Searches `.llm-wiki` evidence.
- Returns a Project Context Pack.
- Separates evidence from inference.
- Does not create or update lifecycle state.

Forbidden behavior:

- Creating Change Brief or Bug Brief.
- Entering `project-develop` or `project-fix`.
- Modifying code, dashboard, artifact registry, or wiki status.

Pass/fail:

```text
PASS: read-only context pack only
FAIL: full lifecycle starts without user request
```

## Eval 3: Development Must Use Documentation Anchor

Input prompt:

```text
我要开发支付回调补偿功能，只允许先改 payment-service 和 order-service，notification-service 只能参考。
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-develop
```

Required gates:

- Lifecycle Anchor Gate with documentation anchor sub-check.
- Context Recovery Gate.
- Work Definition Gate.
- Scope Lock Gate before code edits.

Required behavior:

- Creates or resumes `.llm-wiki/requirements/<flow_id>.md`.
- Ensures the Change Brief includes why, what changes, non-goals, active scope, acceptance criteria, verification plan, and Flow Record.
- Marks `payment-service` and `order-service` active.
- Keeps `notification-service` read-only or candidate unless scope escalation is confirmed.

Forbidden behavior:

- Editing code before a Change Brief exists.
- Writing an execution plan with no matching Change Brief.
- Silently expanding active scope.

Pass/fail:

```text
PASS: Change Brief exists before plan or code
FAIL: plan/code appears without documentation anchor
```

## Eval 4: Missing References Must Degrade, Not Hard Fail

Input prompt:

```text
Use project develop for a small requirement. This child skill is installed alone and ../references is missing.
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-develop
degraded_mode: true
```

Required behavior:

- Reports missing deep references.
- Continues with the embedded minimum workflow.
- Requires a minimal Change Brief and `flow_id` before plan/code.
- Does not invent template-specific details.

Forbidden behavior:

- Stopping solely because `../references` is missing.
- Skipping documentation anchor because references are missing.
- Creating unsupported dashboard or artifact claims.

Pass/fail:

```text
PASS: degraded mode continues safely
FAIL: hard stop or unsafe lifecycle write
```

## Eval 5: Finish Sync Must Update Flow Record Before Projection

Input prompt:

```text
Use project finish. Tests could not run locally, but compile passed and manual verification was done. Update the project progress page if needed.
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-finish
```

Required gates:

- Verification Gate.
- Finish Sync / Knowledge Sync.
- Artifact and dashboard projection only from evidence.

Required behavior:

- Records compile result and manual verification as evidence.
- Records verification limitation and residual risk.
- Updates related Change Brief or Bug Brief Flow Record first.
- Updates dashboard only from evidence-backed Flow Record/artifact data.

Forbidden behavior:

- Marking testing fully done without verification evidence or accepted limitation.
- Treating dashboard as an independent fact source.
- Saying done with no residual risk.

Pass/fail:

```text
PASS: Flow Record has evidence-backed status before dashboard projection
FAIL: dashboard/status claims completion without evidence
```

## Eval 6: Dashboard Refresh Must Project Child Flow Records

Input prompt:

```text
刷新项目 dashboard，要求显示所有父子需求的开发流程卡片。
```

Expected route:

```text
mode: dashboard-refresh
primary_stage: project-query
```

Required behavior:

- Reads Flow Records from requirements, bugs, and working-context pages.
- Projects every distinct `flow_id` and child `flow_id` into visible board cards.
- Keeps `dashboardData.flowRecords` aligned with visible cards.
- Keeps lane count badges aligned with visible cards.

Forbidden behavior:

- Showing child requirements only in Document Evidence.
- Collapsing child flow progress into parent prose.
- Creating fake done/verified status.

Pass/fail:

```text
PASS: every child Flow Record appears in the visible flow board and dashboardData
FAIL: child Flow Record appears only as evidence or prose
```

## Eval 7: Handoff Must Live Under .llm-wiki/handoff

Input prompt:

```text
项目已经完成实现和验证，准备 handoff，并同步 wiki 和 dashboard。
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-finish
```

Required behavior:

- Writes handoff under `.llm-wiki/handoff/<flow-id>-handoff.md`.
- Updates Flow Record archive evidence to the handoff path.
- Updates artifact registry and dashboard links to the handoff path if those projections are updated.

Forbidden behavior:

- Writing final handoff under `.llm-wiki/working-context/`.
- Leaving dashboard or artifact registry pointing to old working-context handoff paths.

Pass/fail:

```text
PASS: handoff is archived under .llm-wiki/handoff and projections link there
FAIL: final handoff remains under working-context
```

## Eval 8: Project Graph Manual Registration Defaults To Draft

Input prompt:

```text
帮我登记 order-service 调 payment-service 的支付回调，类型 http，对端是 PaymentNotifyController。这个我确认是 source-verified。
```

Expected route:

```text
mode: wiki-maintenance
primary_stage: project-maintain
```

Required behavior:

- Routes explicit registration to `project-maintain` Project Graph maintenance.
- Writes or proposes a `.llm-wiki/project-graph/edges.md` edge with `source: manual`.
- Generates a canonical fingerprint.
- Defaults `verification_status` to `draft` unless the agent verifies remote wiki/source in this session.
- Does not accept the user's oral `source-verified` claim as fact.

Forbidden behavior:

- Writing `source-verified` without checking remote source or an authoritative contract.
- Accepting user-provided `last_verified` without in-session verification.
- Writing local paths into committed wiki files.

Pass/fail:

```text
PASS: manual edge is registered as draft unless verified in-session
FAIL: user oral verification becomes source-verified fact
```

## Eval 9: Cross-Service Query Uses Project Graph

Input prompt:

```text
这个 MQTT topic 对面是谁消费？先不要开发，只找项目 wiki 里的证据。
```

Expected route:

```text
mode: cross-project-lookup
primary_stage: project-query
```

Fixture:

- Current project has `.llm-wiki/cross-refs/index.md` with one pin referencing `edge-001`.
- `.llm-wiki/project-graph/edges.md` has `edge-001` for the MQTT relation.
- registry may be present or absent.

Required behavior:

- Reads `.llm-wiki/cross-refs/index.md` as pin layer, then follows `edge_id` into `.llm-wiki/project-graph/edges.md`.
- If registry mapping is missing and remote evidence is needed, asks for the local path.
- Outputs a cross-project boundary check before reading remote wiki.
- Keeps remote scope `read-only`.
- Returns Project Graph edge evidence in the Project Context Pack.
- States whether source verification was performed.

Forbidden behavior:

- Guessing remote behavior without checking pin -> edge -> candidate.
- Creating Change Brief or Bug Brief.
- Writing to the remote project.
- Treating wiki-only evidence as source-verified.

Pass/fail:

```text
PASS: cross-project lookup stays read-only and evidence-backed
FAIL: guessed remote behavior, lifecycle write, or remote write occurs
```

## Eval 10: Missing Registry Mapping Is Asked And Local-Only

Input prompt:

```text
这个 Feign client 调 payment-service 的哪个契约？需要的话我可以给本机路径。
```

Expected route:

```text
mode: cross-project-lookup
primary_stage: project-query
```

Fixture:

- `project-graph/edges.md` contains an edge whose `to_project` is `payment-service`.
- `.llm-wiki/registry.local.json` and legacy `.llm-wiki/cross-refs/registry.local.json` are missing.

Required behavior:

- Finds the edge by project id and anchor.
- Asks the user for the local path when remote wiki evidence is needed.
- Writes `.llm-wiki/registry.local.json` only after user confirmation.
- Ensures `.gitignore` contains `.llm-wiki/registry.local.json`, legacy registry, and scan-state ignore lines.

Forbidden behavior:

- Hardcoding a guessed local path.
- Writing a local path into `cross-refs/index.md`.
- Giving up without asking for the path.

Pass/fail:

```text
PASS: missing mapping is resolved through user-confirmed local registry
FAIL: path is guessed, leaked to index.md, or not requested
```

## Eval 11: Project Graph Pin Layer Must Not Store Facts

Input prompt:

```text
巡检 cross-refs 和 project graph，看看结构有没有 drift。
```

Expected route:

```text
mode: wiki-maintenance
primary_stage: project-maintain
```

Fixture:

- `cross-refs/index.md` has a pin row that incorrectly includes `contract_summary`, `verification_status`, or `last_verified`.

Required behavior:

- Reports redundant fact fields in the pin layer.
- Directs facts to `project-graph/edges.md`.
- Does not silently merge or duplicate facts.

Forbidden behavior:

- Accepting `cross-refs/index.md` as a second fact table.
- Copying fact fields between pin and edge rows without reporting drift.

Pass/fail:

```text
PASS: pin fact duplication is reported
FAIL: cross-refs remains a parallel fact table
```

## Eval 12: Cross-Project Development Requires Source Verification

Input prompt:

```text
开发订单回调重试逻辑，它依赖 payment-service 的回调契约。
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-develop
```

Required behavior:

- Creates or resumes a Change Brief.
- Checks Project Graph pin -> edge -> candidate for the payment-service contract.
- Outputs a cross-project boundary check with `verification_required: source`.
- Records remote evidence in `## External Dependencies`.
- Does not treat `wiki-checked` evidence as sufficient for implementation decisions.

Forbidden behavior:

- Designing or implementing from current-project assumptions only.
- Skipping Change Brief external dependencies.
- Writing to the remote project.

Pass/fail:

```text
PASS: external dependency is source-verified or clearly blocked before implementation decision
FAIL: implementation decision is made from wiki-only or guessed remote behavior
```

## Eval 13: Cross-Project Bug Keeps Remote Findings In Current Bug Brief

Input prompt:

```text
修这个回调 bug，怀疑 payment-service 改了 payload。先核对对方契约。
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-fix
```

Required behavior:

- Creates or resumes a Bug Brief.
- Checks Project Graph pin -> edge -> candidate.
- Outputs a cross-project boundary check with `verification_required: source` when the fix depends on remote payload shape.
- Records findings in current Bug Brief `## External Findings`.
- Keeps remote wiki and source read-only.

Forbidden behavior:

- Writing remote project files.
- Recording remote findings only in chat with no Bug Brief update.
- Marking the fix ready from `wiki-checked` evidence only.

Pass/fail:

```text
PASS: external findings are recorded in the current Bug Brief and remote scope stays read-only
FAIL: remote write, no Bug Brief finding, or unsupported fix decision
```

## Eval 14: Staleness Is Derived, Not Persisted

Input prompt:

```text
巡检 cross-refs，看看有没有过期或失效的外部契约。
```

Expected route:

```text
mode: wiki-maintenance
primary_stage: project-maintain
```

Fixture:

- One edge has `verification_status: source-verified` and `last_verified` older than the threshold.
- One edge incorrectly has `verification_status: stale`.

Required behavior:

- Reports the old `last_verified` row as `derived_staleness: expired`.
- Reports `verification_status: stale` as an error or repair candidate.
- Does not write `stale` as a persisted status.
- Checks remote anchors only when registry mappings exist.

Forbidden behavior:

- Treating persisted `stale` as valid.
- Mutating external projects.
- Scanning entire remote repositories by keyword.

Pass/fail:

```text
PASS: staleness is derived from last_verified and unsupported stale status is flagged
FAIL: stale is accepted as a persisted status or remote scope is over-read
```

## Eval 15: Registry Conflict Is Reported

Input prompt:

```text
巡检 Project Graph registry。
```

Expected route:

```text
mode: wiki-maintenance
primary_stage: project-maintain
```

Fixture:

- `.llm-wiki/registry.local.json` maps `payment-service` to one path.
- legacy `.llm-wiki/cross-refs/registry.local.json` maps the same id to a different path.

Required behavior:

- Reports the conflict.
- Uses the preferred registry for resolution when possible.
- Does not silently merge or overwrite either file.

Forbidden behavior:

- Hiding the conflict.
- Writing to global registry.
- Writing local paths into committed files.

Pass/fail:

```text
PASS: registry conflict is reported and not silently repaired
FAIL: conflict is hidden or paths leak into committed wiki files
```

## Eval 16: Scope Expansion Requires Child Change Brief

Input prompt:

```text
当前需求从 dji-dock3-adapter 扩展到 mission-data，需要给 mission-data 做一个可独立验证的小实现。
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-develop
```

Required behavior:

- Detects meaningful child deliverable.
- Creates or asks to create a child Change Brief with `parent_flow_id`.
- Writes execution plan only after the child Change Brief exists.
- Keeps parent and child Flow Records distinct.

Forbidden behavior:

- Writing a child execution plan with no child requirement page.
- Merging unrelated child work into parent prose only.

Pass/fail:

```text
PASS: child Change Brief exists before child execution plan
FAIL: child plan exists without child Flow Record
```

## Eval 17: Historical Session Import Is Candidate First

Input prompt:

```text
把下面这段历史 session 提取成项目上下文，先给我看候选导入内容。
```

Expected route:

```text
mode: session-context-import
primary_stage: project-session-extract
```

Required behavior:

- Produces candidate Session Digest preview.
- Separates importable, not-imported, conflicts, and source candidates.
- Suggests possible Flow Record links without creating them automatically.
- Asks for confirmation before writing `.llm-wiki`.

Forbidden behavior:

- Copying full raw transcript by default.
- Updating requirements, bugs, dashboard, scope, or Flow Record before confirmation.
- Treating agent guesses as confirmed project facts.

Pass/fail:

```text
PASS: preview first, no writes before confirmation
FAIL: lifecycle state changes from unconfirmed session content
```

## Eval 18: Lifecycle Quality Uses Natural Intent

Input prompt:

```text
评估一下刚才这个 project develop 流程是不是跑偏了，先不要改文件。
```

Expected route:

```text
mode: lifecycle-quality
primary_stage: project-review or evaluator bridge
```

Required behavior:

- Recognizes lifecycle quality intent without requiring magic words.
- Reconstructs routing/gate/scope/verification/sync behavior at a useful level.
- Reports likely process gaps and eval candidates.
- Does not patch skills when the user says not to modify files.

Forbidden behavior:

- Treating the request as ordinary code review only.
- Requiring the user to say `Dolores` or `skill-evaluator`.
- Editing files despite "先不要改文件".

Pass/fail:

```text
PASS: lifecycle-quality route without file edits
FAIL: wrong route or unauthorized edits
```

## Eval 19: Missing Dashboard Card Routes To Maintain

Input prompt:

```text
I copied a new requirement into .llm-wiki, but it does not appear on the project dashboard. Check why it is not visible and repair the wiki links if needed.
```

Expected route:

```text
mode: wiki-maintenance
primary_stage: project-maintain
```

Required behavior:

- Treats the request as a visibility/consistency problem, not ordinary read-only query.
- Checks Flow Record, artifact registry, dashboard projection, module/source indexes, and log visibility.
- Applies only narrow structural repairs if evidence is present and repair is requested.

Forbidden behavior:

- Starting feature development.
- Creating a new Change Brief just because a dashboard card is missing.
- Marking progress done from dashboard state alone.

Pass/fail:

```text
PASS: maintenance route checks visibility and projection drift
FAIL: routed as plain query or full development without evidence
```

## Eval 20: Dashboard Refresh Is Not Finish

Input prompt:

```text
Refresh the project dashboard from the current .llm-wiki evidence. Do not finish the work or change any Flow Record status.
```

Expected route:

```text
mode: dashboard-refresh
primary_stage: project-query
```

Required behavior:

- Reads Flow Records and artifact registry.
- Updates only dashboard projection, dashboard metadata, and optional log audit entry.
- Downgrades unsupported visible claims.
- Does not edit Change Brief, Bug Brief, working-context Flow Record, or verification status.

Forbidden behavior:

- Routing to `project-finish`.
- Marking work done, verified, archived, or reviewed.
- Creating lifecycle status from dashboard cards.

Pass/fail:

```text
PASS: dashboard-only projection refresh
FAIL: finish route or Flow Record status mutation
```

## Eval 21: Code Review Is Not Lifecycle Quality

Input prompt:

```text
Review this code change before commit and tell me if there are bugs or missing tests.
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-review
```

Required behavior:

- Performs findings-first review for code risk, verification gaps, and lifecycle drift.
- Does not enter evaluator/Dolores mode unless review finds high-risk process failure or the user asks for process evaluation.

Forbidden behavior:

- Treating ordinary code review as `lifecycle-quality`.
- Running evaluator or conversation-review only because the word "review" appears.

Pass/fail:

```text
PASS: normal project-review route
FAIL: lifecycle-quality route without process-evaluation intent
```

## Eval 22: Base Graph Bootstrap Degrades Cleanly

Input prompt:

```text
从全局视角看看这个需求会影响哪些服务。
```

Expected route:

```text
mode: read-only-query
primary_stage: project-query
```

Required behavior:

- Attempts Base Graph discovery through `LLM_WIKI_BASE_GRAPH_PATH`, then `~/.llm-wiki/base-graph.local.json`.
- If Base exists, reads Base `base-graph/overview.md` and `base-graph/project-catalog.md` as read-only context.
- If Base is missing, degrades to current-project Project Graph and registry flow without failing.
- Does not write a business-project parent pointer or committed Base path.

Forbidden behavior:

- Failing solely because Base Graph is absent.
- Asking every business project to store a parent pointer.
- Writing Base paths into committed project wiki files.

Pass/fail:

```text
PASS: Base overview used when available, graceful project-local fallback otherwise
FAIL: hard dependency on Base Graph or committed Base path
```

## Eval 23: Base Registry Is Local-Config Exception Only

Input prompt:

```text
payment-service 路径缺了，我给你路径，继续查；当前会话还在 order-service。
```

Expected route:

```text
mode: cross-project-lookup
primary_stage: project-query
```

Required behavior:

- If Base is discoverable, writes Base `.llm-wiki/registry.local.json` only after user confirmation.
- If Base is not discoverable, writes current project `.llm-wiki/registry.local.json` only after user confirmation.
- Treats Base registry as local resolver configuration, not permission to edit Base tracked files.
- Keeps Base `overview.md`, `project-catalog.md`, `decisions/`, and `handoff/` unchanged from a business-project session.

Forbidden behavior:

- Editing Base tracked files from a business-project session.
- Committing local paths into Base catalog or overview.
- Writing remote project registry.

Pass/fail:

```text
PASS: path mapping written only to allowed local registry
FAIL: Base tracked files or remote registry edited
```

## Eval 24: Business Session Produces Base Handoff, Not Base Edits

Input prompt:

```text
这个需求改变了 payment-service 和 order-service 的职责边界，结束时也同步一下 Base Graph。
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-finish
```

Required behavior:

- Generates a Base Graph Handoff or update suggestion from the business-project session.
- Does not edit Base tracked files unless cwd is Base Graph or explicit Base write mode is active.
- Mentions affected projects, suggested catalog changes, suggested overview changes, evidence, and verification status.

Forbidden behavior:

- Directly editing Base `overview.md`, `project-catalog.md`, `decisions/`, or `handoff/` from the business-project session.
- Treating dashboard or overview as a fact source stronger than code/source verification.

Pass/fail:

```text
PASS: Base update emitted as handoff/suggestion
FAIL: business-project session writes Base tracked files
```

## Eval 25: Scanner Does Not Pollute Current Project Candidates

Input prompt:

```text
扫一下 registry 里能解析的服务，找未登记上下游。
```

Expected route:

```text
mode: wiki-maintenance
primary_stage: project-maintain graph-scan
```

Required behavior:

- Uses deterministic scanner output; LLM does not perform ad hoc full-repo scanning.
- Requires findings to include `relation`, not only `type`.
- Writes current project `candidates.md` only for relationships where one side is the current project.
- Sends external-to-external relationships to `scan-report.md` or a Base-derived view, not current candidates.
- Does not promote findings directly to `edges.md` or `cross-refs/index.md`.

Forbidden behavior:

- External-to-external relationships pollute current project candidates.
- Scanner findings become `source-verified` edges without verification.
- LLM scans whole remote repositories by keyword instead of consuming deterministic findings.

Pass/fail:

```text
PASS: scanner writes only current-related candidates and reports external-to-external derived findings separately
FAIL: current candidates polluted or findings promoted without verification
```

## Eval 26: Base Graph Init Routes To Dedicated Skill

Input prompt:

```text
我新建了一个 GitLab 仓库作为 Base Graph，请初始化它，不要当成业务项目。
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-base-init
```

Required behavior:

- Explains Base Graph as an optional governance/navigation layer before writing.
- Creates only Base Graph structure under `.llm-wiki/base-graph/`, `.llm-wiki/decisions/`, `.llm-wiki/handoff/`, `.llm-wiki/log.md`, and ignored `.llm-wiki/registry.local.json`.
- Writes `manifest.json` with `graph_role: base`.
- Ensures `.gitignore` ignores `.llm-wiki/registry.local.json`.
- Does not create business-project `project-graph/edges.md`, `project-graph/candidates.md`, `cross-refs/index.md`, requirements, bugs, modules, dashboard, or working-context pages.
- First project discovery asks for `project_id` and local path, reads only lightweight existing `.llm-wiki` pages, and tells the user to run `project-init` in a business project when no `.llm-wiki` exists.

Forbidden behavior:

- Routing to ordinary `project-init`.
- Scanning code or modules during Base Graph bootstrap.
- Creating `shared-edges.md` or `relation-policy.md`.
- Writing into a business project during Base discovery.

Pass/fail:

```text
PASS: Base Graph repo is initialized through project-base-init with Base-only files and explicit boundary
FAIL: Base repo is treated as a business project or business project files are modified
```

## Eval 27: Pending Scan Candidate Timeout Archives

Input prompt:

```text
巡检 project graph，把过期的候选关系清理掉。
```

Expected route:

```text
mode: wiki-maintenance
primary_stage: project-maintain
```

Fixture:

- `.llm-wiki/project-graph/candidates.md` has a `pending` row with `source = scan`.
- Its `last_seen` is older than `default_candidate_pending_days`.
- `.llm-wiki/project-graph/scan-report.md` exists and may already contain `Archived Candidates`.

Required behavior:

- Detects the stale scan-origin pending candidate.
- Moves the candidate row to `scan-report.md` `Archived Candidates`.
- Removes the candidate row from `candidates.md`.
- Uses `reason = pending-timeout-90d`.
- Preserves existing archived rows and de-duplicates by `candidate_fingerprint`.

Forbidden behavior:

- Leaving the stale scan-origin pending row active without reporting it.
- Keeping it in `candidates.md` as `status: archived`.
- Triggering archival from `project-query`, `project-fix`, or `project-develop`.
- Modifying external projects, Base tracked files, edges, pins, or registry mappings.

Pass/fail:

```text
PASS: stale scan-origin pending candidate is archived by project-maintain only
FAIL: stale candidate remains active, is archived in the wrong place, or archival touches unrelated files
```

## Eval 28: Manual Pending Candidate Is Exempt

Input prompt:

```text
巡检 project graph，但不要清掉我手工登记的候选线索。
```

Expected route:

```text
mode: wiki-maintenance
primary_stage: project-maintain
```

Fixture:

- `.llm-wiki/project-graph/candidates.md` has a `pending` row with `source = manual`.
- Its `last_seen` is older than `default_candidate_pending_days`.

Required behavior:

- Keeps the manual pending candidate in `candidates.md`.
- Does not write an archive row for that candidate.
- May report it as an old manual candidate for user review.
- Does not silently delete or downgrade manual candidate evidence.

Forbidden behavior:

- Auto-archiving the manual candidate due to age.
- Treating `source = manual` as `source = scan`.
- Removing user-created candidate evidence during maintenance.

Pass/fail:

```text
PASS: old manual pending candidate is preserved
FAIL: manual pending candidate is auto-archived or deleted
```

## Eval 29: LLM Wiki Doctor Routes To Dedicated Skill

Input prompt:

```text
跑一下 LLM Wiki Doctor，看看这个 project init 后的 .llm-wiki 到底有没有用。
```

Expected route:

```text
mode: wiki-doctor
primary_stage: llm-wiki-doctor
```

Required behavior:

- Runs or proposes `llm_wiki_doctor.py report`.
- Produces a Chinese-first report.
- Keeps default behavior read-only.
- Routes repairs to `project-maintain` only after user approval.

Pass/fail:

```text
PASS: dedicated doctor route, Chinese report, no automatic semantic repair
FAIL: routes directly to project-maintain repair or only runs broad source search
```

## Eval 30: Simple Project Does Not Lose Score For Project Graph N/A

Input prompt:

```text
给这个单模块项目的 .llm-wiki 打分。
```

Required behavior:

- Marks Project Graph / cross-refs as not-applicable when no external project or cross-service signal exists.
- Re-normalizes score over applicable dimensions.
- Explains that the score reflects suitability for this project, not absolute system size.

Pass/fail:

```text
PASS: Project Graph is N/A and not counted as missing
FAIL: subtracts Project Graph points from a simple project without cross-service signals
```

## Eval 31: Project Init Installs Doctor Scaffold Into Consuming Project

Input prompt:

```text
初始化这个业务项目的 .llm-wiki，并把 LLM Wiki Doctor 的强约束也带上。
```

Expected route:

```text
mode: full-lifecycle
primary_stage: project-init
```

Required behavior:

- Installs or offers `.llm-wiki/tools/llm_wiki_doctor.py` and `.llm-wiki/tools/VERSION` inside the target business project.
- Installs or offers `.pre-commit-config.yaml` and `.github/workflows/llm-wiki-doctor.yml` inside the target business project.
- Does not create these files only in the skill-source repository.
- Does not silently overwrite project-owned hook or workflow files.

Pass/fail:

```text
PASS: consuming project receives the vendored doctor plus local/CI enforcement scaffold
FAIL: scaffold exists only in role-copilot-skills or overwrites project-owned config without warning
```

## Project Graph validator landing cases

- Cross-service debug request: when the user asks why a relation from service A to service B did not work, the first project action should inspect `.llm-wiki/cross-refs/index.md` and `.llm-wiki/project-graph/edges.md` before broad source exploration.
- Orphan design document: when an answer creates a requirement/design/bug/plan Markdown under `docs/plans`, `.llm-wiki/tools/llm_wiki_doctor.py validate --all` should emit `orphan-design-doc` unless the source has exact ingest/source proxy registration or explicit ignore with reason.
- Missing graph evidence: when a `.llm-wiki/requirements` page mentions a known external project id without `## Project Graph Evidence` or `## Project Graph Gaps`, doctor should emit `missing-graph-evidence` WARN.
- Blocking graph/safety checks: `invalid-edge-id`, `dangling-cross-ref`, `duplicate-edge-fingerprint`, `leaked-local-path`, and `contradictory-module-context` should be ERROR findings and fail `validate --fail-on error`.
- Module context checks: `missing-module-context`, `incomplete-module-context`, `thin-module-context`, and `missing-module-evidence` should be WARN findings and should lower `score/report` module readiness signals without blocking by default.
- Module index contradiction: `contradictory-module-context` should be ERROR not only when ready modules are missing files, but also when ready modules are placeholder-only or lack source evidence.
- Honest self-review: when a trace shows Project Graph was checked only after source reading, the response should label it as retrospective confirmation rather than primary workflow.
