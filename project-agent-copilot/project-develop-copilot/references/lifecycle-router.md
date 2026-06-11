# Lifecycle Router

The lifecycle router is the natural entry point for Project Develop Copilot. It decides whether a user request should stay lightweight or enter the full project lifecycle, then chooses one primary stage and optional secondary bridges.

The router does not solve the whole task by itself. It preserves lifecycle continuity.

## Routing Principle

```text
Every natural entry is routed.
Lightweight entries stay light.
Full entries create or resume lifecycle state.
External skills are bridges, not lifecycle owners.
Every full entry returns to finish, review, sync, or an explicit stop.
```

## First Decision: Lightweight Or Full Lifecycle

Use `lightweight-answer` when the user only wants a tiny direct answer. Use `read-only-query` / `project-query` when the user wants to query project `.llm-wiki`, find related requirements, bugs, source proxies, artifacts, or assemble discussion context without starting implementation.

`No skills`, `no child skill`, and `no lifecycle` are aliases for `lightweight-answer` with `primary_stage: none`. This is a deliberate route, not a fallback failure. It means answer directly without invoking a child project skill, without invoking an external bridge, and without writing lifecycle state.

Examples:

- “这个设计文档在哪？”
- “先讨论这个 dashboard 方案，不开发。”
- “解释一下 Gate Stack 是什么。”
- “现在这个 README 大概说了什么？”

Lightweight-answer must not create Change Brief, Bug Brief, working-context, Flow Record, handoff, artifact registry rows, dashboard updates, `.llm-wiki` writes, external bridge calls, child skill calls, or code changes by default.

Use `full-lifecycle` when the user asks to develop, fix, ingest, finish, review, continue, update status, execute a plan, commit, or handle project evidence such as PRDs, logs, diffs, failed tests, or verification results.

## Routing Table

| User signal | Primary route | Notes |
|---|---|---|
| asks where a single file/doc is | lightweight-answer | Tiny read-only lookup. |
| asks to query project `.llm-wiki`, find related requirements/docs/bugs/artifacts, or assemble discussion context | `project-query` | Read-only project wiki query; no lifecycle session by default. |
| asks to explain project design, README, reference, or skill | lightweight-answer | Upgrade only if the user asks to save or edit. |
| says “先讨论”, “不开发”, “只是设计” | lightweight-answer | Respect discussion boundary. |
| asks init/adopt/refresh project context | `project-init` | Create or refresh `.llm-wiki`. |
| provides PRD/doc/log/PDF/URL/meeting notes to add | `project-ingest` | Attach to lifecycle session if one exists. |
| asks feature/requirement/design change/implementation plan | `project-develop` | Create or resume Change Brief. |
| asks bug/error/log/failed test/regression/incident | `project-fix` | Create or resume Bug Brief. |
| asks finish/done/sync/update progress/handoff | `project-finish` | Verify and sync before completion claims. |
| asks review/risk/before commit/PR/merge | `project-review` | Findings first; check lifecycle drift. |
| says continue/resume/next step | resume | Find existing Change Brief, Bug Brief, working-context, log, or artifact. |
| asks evaluator/skill failure/flow went wrong | lifecycle-quality | Usually route through `project-review` or evaluator bridge. |
| asks Dolores/conversation self-review | lifecycle-quality | Review lifecycle trace, not ordinary implementation. |

## Routing Decision Tree

Use this order before relying on keyword matching:

```text
1. Is the user asking to change code, project state, .llm-wiki, dashboard, artifacts, verification status, or lifecycle records?
   yes -> full lifecycle, dashboard-refresh, wiki-maintenance, session-context-import, or lifecycle-quality
   no  -> continue

2. Does the user need project evidence from .llm-wiki or linked project files?
   no  -> lightweight-answer
   yes -> continue

3. Is the request read-only?
   yes -> project-query
   no  -> continue

4. Is the requested write limited to refreshing visible dashboard/progress from existing evidence?
   yes -> dashboard-refresh via project-query
   no  -> continue

5. Is the requested write about structure, visibility, broken links, stale indexes, missing cards, artifact registry drift, safety, or consistency?
   yes -> project-maintain
   no  -> continue

6. Is the user asking to evaluate whether the project lifecycle, routing, gate behavior, skill behavior, or prior conversation flow went wrong?
   yes -> lifecycle-quality via project-review or evaluator/conversation-review bridge
   no  -> continue

7. Is the user providing source material to add?
   yes -> project-ingest
   no  -> continue

8. Is the user reporting a bug, failed test, runtime symptom, log, incident, or regression?
   yes -> project-fix
   no  -> continue

9. Is the user asking to finish, sync implementation status, prepare handoff, or claim done?
   yes -> project-finish
   no  -> project-develop for requirement/feature/plan/implementation work
```

If a request matches more than one route, prefer the least state-changing route that still satisfies the user:

```text
lightweight-answer < project-query < dashboard-refresh < project-maintain < full lifecycle
```

Ask one minimal routing question only when this order still leaves two plausible routes with different write behavior.

## Ambiguous Pair Rules

| Ambiguous request | Route | Why |
|---|---|---|
| "What does the wiki say about login?" | `project-query` | Reads project evidence but does not change lifecycle state. |
| "Discuss the login approach first, do not implement" | lightweight-answer or `project-query` | Respect the no-write/no-implementation boundary; use query only if wiki evidence is needed. |
| "Start developing login" | `project-develop` | User asks to change requirement/implementation state. |
| "Refresh dashboard" | dashboard-refresh via `project-query` | Visible projection update only; does not imply finish. |
| "Finish this and update dashboard" | `project-finish` | Completion/status change requires verification and Flow Record update before projection. |
| "Why is this requirement not visible on dashboard?" | `project-maintain` | Structural visibility or drift problem. |
| "Find related docs for this requirement" | `project-query` | Read-only evidence map. |
| "Review code risk before commit" | `project-review` | Delivery readiness review, not lifecycle-quality by default. |
| "Review whether this workflow went off track" | lifecycle-quality | Process/routing/gate review, not ordinary code review. |
| "Continue" | resume | Recover active session first; ask only if multiple sessions match. |

## Natural Lifecycle Quality Intent

Route to `lifecycle-quality` when the user describes the intent in natural language, even without saying a special alias:

- "evaluate whether this flow went wrong"
- "did the project develop process drift?"
- "review the routing/gates/context recovery we used"
- "find the smallest skill rule or eval gap"
- "先评估流程有没有跑偏"
- "这次 project develop 是不是选错阶段了"

Aliases such as `Dolores`, `skill-evaluator`, `conversation self-review`, `eval gap`, and `golden case` are supported, but they are not required.

Do not route to lifecycle-quality merely because the user says `review`, `continue`, `finish`, `bug`, `next step`, or `summary`. Those are normal delivery routes unless the user asks to evaluate the process itself or review finds high-risk process failure.


## Lifecycle Quality Routing

Lifecycle quality routing is the Project Develop Copilot equivalent of Thinking Skills self-review and evaluator triggers.

| User language | Route | Notes |
|---|---|---|
| "skill-evaluator", "evaluator", "evaluate this skill" | lifecycle-quality -> evaluator bridge | Focused skill behavior analysis. |
| "eval gap", "failure case", "golden case" | lifecycle-quality -> evaluator bridge | Produce abstract eval/case suggestion. |
| "这个 skill 为什么跑偏", "这个 router 是不是选错了" | lifecycle-quality -> evaluator bridge | Diagnose likely source: router, stage skill, bridge, gate, reference, or eval gap. |
| "self-review", "conversation self-review" | lifecycle-quality -> Dolores bridge | Review conversation as lifecycle trace. |
| "Dolores", "用 Dolores 视角复盘" | lifecycle-quality -> Dolores bridge | Check routing, gates, bridges, scope, verification, sync, dashboard, review. |
| "lifecycle trace", "routing trace", "gate trace" | lifecycle-quality -> Dolores bridge | Reconstruct trace rather than summarize normally. |
| "先不要直接改，评估一下" | lifecycle-quality -> evaluator bridge | Do not patch until user asks to apply. |

Non-trigger examples:

| User language | Route |
|---|---|
| "继续" | resume normal lifecycle |
| "下一步做什么" | resume normal lifecycle |
| "帮我修这个 bug" | `project-fix` |
| "review 一下代码" | `project-review` |
| "总结一下改了什么" | normal handoff or `project-finish` |

Do not turn normal work into evaluator or Dolores unless the user explicitly asks for lifecycle-quality review or a review gate finds process-level risk.

## Primary Stage And Secondary Bridge

Choose exactly one primary stage for full lifecycle work.

Secondary bridges are optional and must be scoped:

| Primary stage | Common secondary bridges |
|---|---|
| `project-query` | obsidian-wiki-query style project wiki lookup, optional handoff to develop/fix/review |
| `project-develop` | brainstorming, writing-plans, test-driven-development, executing-plans |
| `project-fix` | systematic-debugging, test-driven-development, verification-before-completion |
| `project-finish` | verification-before-completion |
| `project-review` | requesting-code-review, skill-evaluator, conversation-review / Dolores |

A secondary bridge receives Context Handoff and returns Return Handoff. It must not choose project scope from scratch or declare project completion.

## Routing Record

For every full lifecycle entry, save a short routing record in the relevant lifecycle session.

Requirement / feature:

```text
.llm-wiki/requirements/<change-id>.md
```

Bug / incident:

```text
.llm-wiki/bugs/<bug-id>.md
```

Cross-module work:

```text
.llm-wiki/working-context/<change-id>.md
```

Review-only work without an obvious existing session:

```text
.llm-wiki/log.md
```

Minimal format:

```markdown
## Routing

- intent:
- primary_stage:
- secondary_bridges:
- confidence:
- reason:
- next_gate:
- routed_at:
```

Routing record is a decision trace, not a chain-of-thought log. Keep it short and recoverable.

## Resume Rules

When the user says continue, resume, previous, 上次, 刚刚, or next step:

1. Check active Change Briefs.
2. Check active Bug Briefs.
3. Check working-context pages.
4. Check `.llm-wiki/log.md` for recent lifecycle entries.
5. Check artifact registry for recent plans, specs, reports, and dashboards.
6. If exactly one likely session exists, resume it.
7. If multiple plausible sessions exist, ask one minimal clarification question.

Do not create a duplicate lifecycle session before checking recoverable state.

## Low Confidence Behavior

Ask one minimal routing question when:

- project root is unknown and cannot be inferred
- multiple active lifecycle sessions match
- the request could be lightweight or full lifecycle and the user has not made the intent clear
- the requested scope may be risky or destructive

Avoid long forms. The router should reduce friction, not create ceremony.

## Handoff Contract

Context Handoff:

```markdown
## Context Handoff

- lifecycle_session:
- user_intent:
- active_sources:
- active_scope:
- read_only_scope:
- candidate_scope:
- excluded_scope:
- current_gate:
- requested_stage_or_bridge:
- constraints:
```

Return Handoff:

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

## Common Routing Failures

- Treating every project question as full lifecycle instead of `project-query` or lightweight-answer.
- Treating every bug as direct systematic-debugging.
- Treating every feature as direct implementation.
- Skipping Change Brief or Bug Brief.
- Forgetting routing record.
- Letting external skills own project scope.
- Finishing without verification or explicit limitation.
- Updating dashboard without evidence.
- Running evaluator or Dolores when the user only wanted normal delivery.
