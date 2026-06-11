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
- runs Context Enrichment Gate and Bug Evidence Gate
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
- runs Context Enrichment Gate
- records active/read-only/candidate/excluded scopes
- runs Clarification Gate before planning
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
Review 发现 project-fix 跳过了 Bug Evidence Gate。评估一下这个 skill 需要怎么改，但先不要直接改。
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
- reads `.llm-wiki/index.md` and lightweight indexes first
- finds related requirement, bug, source proxy, working-context, artifact, or dashboard pages when present
- returns a Project Context Pack with pages used and confidence
- does not create Change Brief, Bug Brief, working-context, artifact rows, dashboard updates, or code changes by default
- offers possible next routes only after answering: develop, fix, ingest, review, evaluator, or Dolores

Failure signals:

- routes directly to implementation or planning
- creates lifecycle state for exploratory discussion
- deep-reads raw source before checking `.llm-wiki` indexes
- answers without naming wiki pages used
```

## Case 12: Project API Integration Query Must Start From Wiki

Prompt:

```text
这个项目里面，大疆 API 适配，直播相关的内容有哪些？如何通过 API 调用
```

Expected:

- router selects `project-query` before CodeGraph, grep-only exploration, or implementation skills
- reads `.llm-wiki/index.md` and lightweight indexes first, then the smallest relevant requirement, source proxy, working-context, or artifact pages
- identifies that this is read-only project question answering, not `project-develop`, `project-fix`, or `project-review`
- may inspect source code after wiki recovery to verify current endpoints, MQTT topics, controllers, or service behavior
- separates wiki-sourced facts from code-verified facts and inference
- returns a concise answer plus Project Context Pack naming wiki pages used

Failure signals:

- jumps straight to source search or CodeGraph without checking `.llm-wiki`
- treats "how to call the API" as an implementation request
- answers from memory only without project-local wiki/source evidence
- omits related requirement/source/working-context pages when they exist

## Completion Rule

Do not claim the complete lifecycle is ready for broad testing until the router passes Cases 1, 2, 3, 5, 6, 11, and at least one of Cases 8 or 9. Case 10 should be run before release or public recommendation.
