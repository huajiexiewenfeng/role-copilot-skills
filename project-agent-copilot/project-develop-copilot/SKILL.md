---
name: project-develop-copilot
description: Use when the user wants project development help from natural intent, including Chinese prompts for 项目开发、项目文档、跨项目关系、项目图谱仓库、Base Graph、需求、bug、日志、评审、继续, or routing into project lifecycle skills.
---

# Project Develop Copilot

## Purpose

`project-develop-copilot` is the top-level lifecycle router for project development work.

It helps users enter naturally without choosing a child skill first. It decides whether the request should stay lightweight or enter the full project lifecycle, then routes full work into the right stage while preserving scope, lifecycle state, handoff, verification, knowledge sync, artifact sync, dashboard sync, and review.

It does not replace `project-query`, `project-base-init`, `project-graph-visualize`, `project-init`, `project-ingest`, `project-develop`, `project-fix`, `project-finish`, or `project-review`. It owns routing and lifecycle continuity; stage skills own stage execution.

## When to Use

Use this skill when the user asks for project development help from natural language, including:

- Finding, explaining, querying, or discussing project `.llm-wiki`, requirements, bugs, design docs, README files, skills, references, artifacts, or current project status.
- Investigating cross-service or cross-project integration points such as Feign clients, MQTT topics, HTTP/RPC interfaces, shared DB tables, shared config, upstream/downstream services, or external contracts.
- Developing a feature, requirement, PRD, design change, implementation plan, or scoped project change.
- Diagnosing or fixing a bug, failed test, runtime error, log symptom, regression, incident, or unexpected behavior.
- Ingesting PRDs, logs, PDFs, URLs, meeting notes, customer feedback, or temporary source material into project context.
- Extracting, distilling, reviewing, or importing historical AI/team chat sessions, transcript files, old conversation summaries, colleague AI discussions, or previous agent handoffs into project `.llm-wiki`.
- Finishing work, syncing project knowledge, updating progress, preparing handoff, or checking done status.
- Refreshing or updating the static project dashboard/progress page without claiming work is finished.
- Checking, auditing, maintaining, or repairing project `.llm-wiki` structure, visibility, Flow Records, artifact registry entries, module backlinks, dashboard consistency, logs, links, or safety issues.
- Running LLM Wiki Doctor, scoring `.llm-wiki` maturity, checking whether project-init produced a useful wiki, diagnosing empty wiki skeletons, or explaining doctor/pre-commit/CI findings.
- Scanning Project Graph candidates through `project-graph-candidates-scan`.
- Resolving candidates into evidence-backed edge proposals through `project-graph-auto-edge`.
- Confirming, rejecting, manually registering, or pinning Project Graph edges through `project-graph-human-edge`.
- Generating, refreshing, rebuilding, previewing, or validating an offline Base Graph / Project Graph interactive HTML through `project-graph-visualize`.
- Auditing or repairing Project Graph structure through `project-maintain`.
- Initializing an independent Base Graph repository that coordinates many project-local `.llm-wiki` directories, including Chinese requests such as 初始化 Base Graph、初始化项目图谱仓库、创建跨项目导航层、注册多项目目录、跨项目总览仓库.
- Reviewing before commit, merge, PR, handoff, release, or broader testing.
- Continuing, resuming, or asking what to do next for previous project work.
- Evaluating whether a project skill flow went wrong, asking for skill-evaluator, conversation self-review, self-review, Dolores, eval gap, failure case, golden case, or lifecycle trace review.

## When Not to Use

- Use an ordinary direct answer when the user is not asking about a project, repository, project skill, `.llm-wiki`, or project lifecycle.
- Use a specialized external skill directly only when the user explicitly wants that skill outside project lifecycle context.
- Do not create lifecycle state for lightweight explanation, file lookup, or design discussion unless the user asks to save or execute the decision.
- Do not route to code implementation when the user says they only want to discuss, inspect, or design.
- Do not claim project work is complete from this router alone.

## Owned Gates

The router owns lifecycle coherence across gates:

- Lightweight Boundary
- Context Recovery Gate
- Lifecycle Anchor Gate
- External Bridge Gate
- Session Import Gate
- Finish Sync Gate when the user explicitly asks to refresh dashboard/progress state
- Review & Wiki Integrity Gate when the user reports missing, stale, hard-to-find, inconsistent `.llm-wiki` state or lifecycle-quality risk

Stage skills own their stage-specific gates, but this router must ensure the next gate is explicit before handing off.

Cross-project evidence is handled as a Context Recovery / External Bridge sub-check, not as a separate lifecycle Gate. Remote wiki/source access must stay read-only and must return through the current lifecycle session.

## Cross-Service Project Graph First Rule

When a request mentions cross-service, cross-repository, upstream/downstream, Feign, MQTT, HTTP, WebSocket, API gateway, shared DB, shared configuration, event bus, or two or more registry project ids, inject a Project Graph first step before routing into `project-fix`, `project-develop`, or `project-query`.

The injected step is:

1. Read `.llm-wiki/cross-refs/index.md`.
2. Read `.llm-wiki/project-graph/edges.md`.
3. Read `.llm-wiki/project-graph/candidates.md` when confirmed edges do not cover the relation.
4. Use the graph only to narrow source-reading scope.
5. If graph evidence is missing, stale, draft, or indirect, verify from source before making implementation decisions.

This is a router navigation rule, not a validator guarantee. Do not claim Project Graph was the primary workflow unless the actual trace shows it was used before source exploration.

## LLM Wiki Discovery Rule

Treat a discovered `.llm-wiki/` directory as proof that the project has an LLM Wiki. Do not use `.llm-wiki/index.md` as the existence sentinel.

When `.llm-wiki/index.md` is missing, report only that the root index is missing or optional, then continue with available wiki targets such as `.llm-wiki/README.md`, `.llm-wiki/log.md`, `.llm-wiki/modules/index.md`, `.llm-wiki/requirements/`, `.llm-wiki/bugs/`, `.llm-wiki/sources/`, `.llm-wiki/working-context/`, `.llm-wiki/artifacts/index.md`, and Project Graph files. Fall back to source only after checking the relevant available wiki entries or when the wiki evidence is insufficient or stale.

## Initialization Gate

Run this gate after resolving the business-project root and intended route, but before creating or resuming lifecycle state or invoking a wiki-backed child skill.

- `wiki_required_for: full-lifecycle-or-wiki-backed`
- `on_missing_wiki: route project-init`
- `excluded_mode: lightweight-answer-or-mechanical-artifact`
- `read_only_missing_wiki: confirm-before-init`
- Preserve the original request as `pending_intent` and the selected route as `pending_primary_stage`.
- If `<project_root>/.llm-wiki/` is absent, stop the pending stage and hand off to `project-init`. Do not create a partial wiki, Change Brief, Bug Brief, routing record, plan, or code change first.
- Keep the bootstrap routing handoff in memory until `project-init` creates the standard wiki; then persist the routing record in the appropriate lifecycle session.
- Resume the pending stage only when the `project-init` return handoff identifies a supported `next_gate`. Initialization Level 1 or 2 alone must not be treated as feature-ready.
- Explicit `project-init` and `project-base-init` requests are gate destinations, not inputs to this gate.
- If the pending request is explicitly read-only or forbids writes, report the missing wiki and ask before `project-init` writes; offer a source-only `lightweight-answer` alternative without losing the pending intent.
- A source-only answer stays `lightweight-answer`. A clearly source/diff-only review may use the narrow `quick-diff-review` exception, but it must not claim lifecycle or wiki integrity.

## Required First Check

Before doing project work:

1. Decide whether the request is `lightweight-answer` or `full-lifecycle`.
2. If lightweight-answer applies, answer from available evidence without creating lifecycle state.
3. If `mechanical-artifact` applies, route directly to the deterministic child skill without Change Brief, Flow Record, planning, finish sync, or other lifecycle state.
4. If full lifecycle or any wiki-backed route applies, resolve or ask for the project root when it is not obvious.
5. Select the intended primary stage without invoking it.
6. Run the Initialization Gate for business-project full-lifecycle or wiki-backed work.
7. If the gate routes to `project-init`, wait for its return handoff and keep `pending_intent` plus `pending_primary_stage` intact.
8. For full-lifecycle routes, create or resume a Lifecycle Session: Change Brief, Bug Brief, or working-context.
9. Save or update a short routing record for full-lifecycle routes.
10. Invoke one primary stage skill, then select optional external bridge skills only after project scope is known.

## Core Process

1. Read `references/north-star.md` when goals, scope, or lifecycle ownership are unclear.
2. Read `references/lifecycle-router.md` for routing decisions and routing record format.
3. Classify the user request:
   - lightweight-answer
   - project wiki query / discussion context
   - cross-project lookup / evidence gathering
   - init / ingest
   - historical session extraction / Session Digest import
   - requirement or feature development
   - bug or incident fixing
   - finish or progress sync
   - dashboard refresh
   - review
   - resume
   - evaluator / self-review / Dolores / lifecycle-quality review
4. Recover project context only as much as the route requires.
5. For full lifecycle work, establish the lifecycle session and next gate.
6. Hand off to the primary stage skill with concise scoped context.
7. After the stage returns, make sure the lifecycle still has a next action: verify, sync, review, update dashboard, evaluate flow quality, or stop with a clear limitation.

## Mode / Entry Selection

| Situation | Mode | Primary stage |
|---|---|---|
| User asks a tiny file/doc lookup or simple concept explanation | lightweight-answer | none |
| User asks to query project `.llm-wiki`, find related requirements/docs/bugs/artifacts, or assemble discussion context | read-only-query | `project-query` |
| User asks which service owns an interface/topic/client/config/callback, or asks for cross-service contract evidence without requesting a change | cross-project-lookup | `project-query` |
| User asks to register a known cross-project integration point manually, confirm a proposal, reject a proposal, or pin an accepted relationship | wiki-maintenance | `project-graph-human-edge` |
| User asks to generate, refresh, rebuild, preview, or validate Base Graph / Project Graph `graph.html` or another interactive graph HTML | mechanical-artifact | `project-graph-visualize` |
| User asks to scan for missing upstream/downstream relationship candidates | wiki-maintenance | `project-graph-candidates-scan` |
| User asks to turn a candidate into an evidence-backed edge proposal through Base Graph or source verification | wiki-maintenance | `project-graph-auto-edge` |
| User asks for large-scope requirement discussion across services | read-only-query | query Base Graph overview first when Base is discoverable |
| User says to discuss design and not implement | lightweight-answer | none |
| User asks to initialize, create, adopt, or refresh a Base Graph repository, graph-base repo, base-project-graph, platform graph catalog, platform overview repo, 项目图谱仓库, 跨项目导航层, Base Graph 初始化, or 多项目 `.llm-wiki` 总目录 | full-lifecycle | `project-base-init` |
| User provides PRD/source material to index | full-lifecycle | `project-ingest` |
| User provides or references historical AI/team chat, session transcript, old conversation summary, colleague AI discussion, previous agent handoff, or asks to distill/import previous session context into `.llm-wiki` | session-context-import | `project-session-extract` |
| User asks to initialize/adopt/refresh project context | full-lifecycle | `project-init` |
| User asks to run LLM Wiki Doctor, score `.llm-wiki`, check whether project-init produced a useful wiki, or explain doctor/pre-commit/CI findings | wiki-doctor | `llm-wiki-doctor` |
| User asks for a feature, requirement, plan, or implementation | full-lifecycle | `project-develop` |
| User reports a bug, log, error, failed test, or incident | full-lifecycle | `project-fix` |
| User asks to update, refresh, or sync the static dashboard/progress page only | dashboard-refresh | `project-query` |
| User asks why wiki pages cannot be found, or asks to check, audit, lint, repair, or maintain `.llm-wiki` structure, links, Flow Records, module backlinks, artifacts, logs, dashboard consistency, Project Graph consistency, or safety | wiki-maintenance | `project-maintain` |
| User asks finish, done, sync, update status, or handoff | full-lifecycle | `project-finish` |
| User asks review, risk check, before commit/PR/merge | full-lifecycle | `project-review` |
| User says continue or resume previous work | full-lifecycle | resume then choose stage |
| User asks skill failure review, skill-evaluator, eval gap, failure case, golden case, self-review, conversation self-review, lifecycle trace review, or Dolores | lifecycle-quality | `project-review`, evaluator bridge, or Dolores bridge |

If confidence is low, ask one minimal routing question. Do not start a long intake form.

## Routing Tie-breakers

When multiple routes seem plausible, choose the least state-changing route that still satisfies the user:

```text
lightweight-answer < read-only-query < mechanical-artifact < wiki-doctor < dashboard-refresh < wiki-maintenance < full-lifecycle
```

Use this quick decision order:

1. No project evidence needed and no write requested -> `lightweight-answer`.
2. Project evidence needed, but read-only -> `read-only-query` / `project-query`.
   - If the evidence crosses another project through Project Graph pins/edges/candidates, use `cross-project-lookup` and keep remote scope read-only.
3. Only visible dashboard/progress projection requested -> `dashboard-refresh` / `project-query`.
4. LLM Wiki Doctor, wiki maturity score, empty wiki skeleton, or doctor/pre-commit/CI finding explanation requested -> `wiki-doctor` / `llm-wiki-doctor`.
5. Project Graph candidate scan requested (`graph-scan`, `candidates scan`, `自动扫描候选关系`, `扫一下 candidates`) -> `wiki-maintenance` / `project-graph-candidates-scan`.
6. Project Graph auto proposal requested (`auto-edge`, `自动登记`, `生成 edge proposal`, `通过 base-graph 找项目类方法但先确认`) -> `wiki-maintenance` / `project-graph-auto-edge`.
7. Project Graph human confirmation/manual edge requested (`human-edge`, `手动登记`, `确认 proposal`, `接受 proposal`, `拒绝 proposal`) -> `wiki-maintenance` / `project-graph-human-edge`.
8. Wiki visibility, broken links, stale indexes, dashboard/card drift, artifact registry drift, Project Graph audit/repair, safety, or consistency requested -> `wiki-maintenance` / `project-maintain`.
9. Base Graph repository initialization, adoption, or refresh requested, including Chinese prompts like 初始化项目图谱仓库 or 跨项目导航层 -> full lifecycle / `project-base-init`.
10. Requirement, bug, source ingest, implementation, finish, verification, handoff, or review readiness requested -> full lifecycle.
11. Process/routing/gate/conversation-flow evaluation requested -> `lifecycle-quality`.

Natural lifecycle-quality intent is enough. The user does not need to say `Dolores` or `skill-evaluator`; phrases like "did this flow go wrong", "review whether the lifecycle drifted", or "评估这次流程是否跑偏" should route to lifecycle-quality. Ordinary `review code`, `continue`, `finish`, `bug`, and `next step` stay on normal delivery routes unless the user asks to evaluate the process itself.

## No Child Skill Mode

`no skills`, `no child skill`, and `no lifecycle` requests are aliases for `lightweight-answer` with `primary_stage: none`.

Use this mode when the user wants a quick answer, a tiny lookup, a lightweight explanation, or a design discussion that should not be saved or executed yet.

In this mode:

- Do not call a child project skill.
- Do not call an external bridge skill.
- Do not create or modify `.llm-wiki` files.
- Do not create Change Brief, Bug Brief, Flow Record, handoff, artifact registry rows, dashboard updates, or code changes.
- Cite evidence when useful, then answer directly.

Upgrade out of this mode only when the user explicitly asks to save, ingest, plan, execute, fix, review, finish, refresh dashboard, or otherwise update project lifecycle state.


## Lifecycle Quality Trigger Phrases

Use `lifecycle-quality` mode when the user explicitly uses language such as:

- skill-evaluator, evaluator, evaluate this skill, eval gap, failure case, golden case
- self-review, conversation self-review, Dolores, lifecycle trace, routing trace, gate trace
- "这个 skill 为什么跑偏？", "这个流程是不是跑偏了", "先不要直接改，评估一下"
- "review the conversation trace", "did this lifecycle go wrong", "find the smallest patch"

Do not trigger lifecycle-quality for ordinary delivery requests such as "继续", "修 bug", "review 代码", "完成了吗", or "总结一下" unless the user also asks to evaluate the process or review the conversation lifecycle.

## Inputs

Possible inputs include:

- user request
- repository path or project root
- PRD/design/log/source paths
- `.llm-wiki` pages
- Change Brief, Bug Brief, or working-context
- git diff or changed files
- external skill output
- dashboard file or artifact registry

## Outputs

For lightweight-answer:

- concise answer
- evidence references when useful
- no lifecycle state changes unless requested

For read-only query:

- answer from `.llm-wiki` and linked evidence
- Project Context Pack
- related requirements/bugs/sources/artifacts
- possible next routes
- no lifecycle state changes unless requested

For dashboard-refresh:

- recover project dashboard evidence from `.llm-wiki`
- update only `.llm-wiki/dashboard/progress.html` and related dashboard artifact metadata/log when needed
- do not mark work done unless finish/verification evidence already exists

For session-context-import:

- brief Session Digest candidate list first
- user selection of items to keep
- Session Digest Markdown draft before `.llm-wiki` writes
- confirmation question before writing `.llm-wiki/session-digests/`
- no requirement, bug, Flow Record, dashboard, scope, or project-truth update by default
- optional Lifecycle Promotion candidates only when the user asks to promote selected digest items
- imported digest path after approval

For full lifecycle:

- routing decision
- lifecycle session path or recovery summary
- active source/scope summary
- selected primary stage
- optional secondary bridges
- next gate

## Context Handoff

When handing off to a child stage skill or external bridge, use a short structured handoff:

```markdown
## Context Handoff

- project_root:
- lifecycle_session:
- user_intent:
- pending_intent:
- pending_primary_stage:
- active_sources:
- active_scope:
- read_only_scope:
- candidate_scope:
- excluded_scope:
- current_gate:
- requested_stage_or_bridge:
- constraints:
```

Do not include long reasoning. Include only enough context for the next skill to act safely.

## Return Handoff

When a child stage or external bridge returns, fold the result back into lifecycle state:

```markdown
## Return Handoff

- stage_or_bridge_used:
- result_summary:
- changed_assumptions:
- recommended_scope_changes:
- artifacts:
- verification_notes:
- lifecycle_updates_needed:
- next_gate:
```

If the returned result suggests new scope, new sources, changed acceptance criteria, or missing verification, route to the correct gate before proceeding.

## Boundaries

- Lightweight-answer and read-only query must not create Change Brief, Bug Brief, dashboard updates, or code changes by default.
- `mechanical-artifact` routes such as `project-graph-visualize` may write only their declared artifact output and must not create lifecycle documents, plans, finish-sync records, or commits unless the user explicitly asks.
- Full lifecycle work must not call external implementation/debugging/planning skills before project scope is established.
- External skills are bridges, not lifecycle owners.
- Completion claims must go through verification, knowledge sync, artifact sync, dashboard sync when enabled, and review as appropriate.
- Evaluator and Dolores are non-blocking by default unless the user explicitly asks to enter improvement mode or review finds high-risk process failure.
- `.llm-wiki` stores indexes, summaries, relationships, status, and gaps; it is not a raw document warehouse.

## Common Mistakes

- Forcing lightweight design discussion into full lifecycle.
- Letting users choose child skills manually when natural routing is possible.
- Jumping into `systematic-debugging`, planning, TDD, or execution before scoped project context exists.
- Creating duplicate Change Briefs or Bug Briefs instead of resuming existing sessions.
- Treating dashboard state as a source of truth instead of evidence-backed summary.
- Answering "why can I not see this wiki document" as a plain query when the underlying issue is missing artifact, module, dashboard, or log visibility.
- Declaring project work done from the router without finish/review gates.
- Running evaluator or Dolores on every normal task and making the workflow feel heavy.
