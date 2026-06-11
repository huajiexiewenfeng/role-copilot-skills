---
name: project-query
description: Use when answering, discussing, locating, or synthesizing project questions from a project-local `.llm-wiki`, including finding related requirements, bugs, source proxies, working-context pages, design docs, artifacts, dashboard state, and development notes without starting implementation.
---

# Project Query

## Purpose

Answer and discuss project questions from a project-local `.llm-wiki` and its linked source materials.

This skill is the Project Develop Copilot equivalent of an Obsidian LLM Wiki query flow. It helps the user quickly find relevant requirements, development docs, bug notes, artifacts, dashboard state, and source proxies, then assemble a small discussion context for follow-up thinking.

It is read-only by default. It does not create Change Briefs, Bug Briefs, working-context pages, dashboard updates, or code changes unless the user explicitly asks to save or act on the discussion. When the user explicitly asks to update or refresh the dashboard, this skill may run `dashboard-refresh` mode and update only dashboard-related files.

## When to Use

Use when the user asks to:

- answer a project question from `.llm-wiki`
- find the requirement, bug, design doc, source proxy, or artifact related to a topic
- discuss project architecture, decisions, progress, or tradeoffs using existing project context
- summarize what the project wiki says about a feature, module, bug, or decision
- answer "what exists in this project / how is it called / how was it designed" questions about a module, integration, API, or feature; start from `.llm-wiki` context first, then verify key facts against source code when needed
- assemble context for later development without starting development yet
- compare related requirements, bugs, source materials, or working-context pages
- locate evidence before deciding whether to create a requirement, fix a bug, or review a change
- update, refresh, or sync the static project dashboard/progress page from existing `.llm-wiki` evidence

Example triggers:

- "鍩轰簬杩欎釜椤圭洰鐨?llm wiki 鍥炵瓟"
- "浠庨」鐩?wiki 閲屾壘涓€涓嬭繖涓渶姹?
- "杩欎釜鍔熻兘涔嬪墠鏈変粈涔堝紑鍙戞枃妗?
- "甯垜鎵惧埌鐩稿叧 requirement / bug / working-context"
- "鍏堟妸涓婁笅鏂囨壘鍑烘潵锛屾垜浠璁轰竴涓?
- "what does the project wiki say about this module"
- "find related project docs before we decide what to do"
- "杩欎釜椤圭洰閲岄潰锛屽ぇ鐤?API 閫傞厤锛岀洿鎾浉鍏崇殑鍐呭鏈夊摢浜涳紵濡備綍閫氳繃 API 璋冪敤"
- "鏇存柊椤圭洰鐪嬫澘"
- "鍒锋柊 dashboard"
- "鍚屾椤圭洰鐘舵€侀〉"
- "update progress dashboard"

## When Not to Use

- Do not use for implementation after the user clearly asks to develop; route to `project-develop`.
- Do not use for bug diagnosis/fix after the user clearly asks to fix; route to `project-fix`.
- Do not use for adding new source material; route to `project-ingest`.
- Do not use for finish sync; route to `project-finish`.
- Do not use for commit/PR review; route to `project-review`.
- Do not save synthesis back to `.llm-wiki` unless the user explicitly asks to save it.
- Do not use dashboard refresh to imply finish, done, verified, or review-passed status; route to `project-finish` or `project-review` for those claims.

## Owned Gates

- Lightweight Answer Boundary
- Context Discovery Gate
- Project Wiki Query Gate
- Optional Upgrade Gate
- Progress Dashboard Sync Gate in explicit `dashboard-refresh` mode

## Required First Check

1. Resolve project root.
2. Resolve optional shared references from `../references/` or local `references/`. If `lifecycle-router.md`, `flow-record.md`, or `progress-dashboard.md` is missing, continue in degraded mode using the minimum rules in this skill; report the missing deep references and keep answers read-only unless the user explicitly asks to write dashboard state.
3. Confirm `.llm-wiki` exists.
4. Decide whether this is read-only project query or full lifecycle work.
5. Identify likely query targets: requirements, bugs, sources, working-context, modules, artifacts, dashboard, session-digests, log.
6. If the user asks only to refresh dashboard/progress state, enter `dashboard-refresh` mode.
7. If the user asks to act beyond dashboard refresh, route to the appropriate lifecycle stage after answering or ask one minimal clarification.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-router.md`
- `../references/lifecycle-gates.md`
- `../references/progress-dashboard.md`
- `../references/flow-record.md`
- `.llm-wiki/index.md`
- `.llm-wiki/modules/index.md`
- `.llm-wiki/ingest/index.md`
- `.llm-wiki/artifacts/index.md`
- `.llm-wiki/log.md`
- `.llm-wiki/session-digests/`
- relevant `.llm-wiki/requirements/*.md`
- relevant `.llm-wiki/bugs/*.md`
- relevant `.llm-wiki/sources/*.md`
- relevant `.llm-wiki/working-context/*.md`

Reference availability policy:

- Shared references are deep references, not startup requirements.
- Do not stop solely because `../references/` is missing.
- In degraded mode, query can still read `.llm-wiki` indexes and return evidence/inference separation.
- Dashboard refresh in degraded mode must not claim done/verified/progress status unless existing Flow Record evidence is clear.

Workflow:

1. Resolve project root and `.llm-wiki` root.
2. Read `.llm-wiki/index.md` first.
3. Search lightweight indexes before deep-reading pages.
4. Read the smallest relevant set of wiki pages.
5. Fall back to original source files only when wiki summaries are insufficient or stale.
6. Separate sourced wiki facts from inference.
7. Return a concise answer and a Project Context Pack.
8. In `dashboard-refresh` mode, update only `.llm-wiki/dashboard/progress.html`, dashboard artifact metadata, and a short `.llm-wiki/log.md` entry when needed. Build flow board cards from Flow Records in Change Briefs, Bug Briefs, and working-context pages using `progress-dashboard.md` projection rules.
9. Before reporting a dashboard refresh complete, run the Progress Dashboard consistency checks: every distinct `flow_id` and `parent_flow_id`/child Flow Record discovered from `.llm-wiki` must have visible board cards for each eligible Flow Record row, matching `dashboardData.flowRecords` entries, and correct lane counts. Fix drift before returning.
10. Offer upgrade routes only when useful: develop, fix, ingest, finish, review, evaluator, or Dolores.

## Mode / Entry Selection

| Mode | Use when |
|---|---|
| `quick-lookup` | user asks where a requirement/doc/page/artifact is |
| `wiki-answer` | user asks a question answerable from project wiki pages |
| `discussion-context` | user wants context assembled before discussion |
| `evidence-map` | user asks which docs, requirements, bugs, or artifacts relate to a topic |
| `dashboard-refresh` | user explicitly asks to refresh or update the static project dashboard/progress page |
| `upgrade-candidate` | query reveals a likely requirement, bug, stale source, or review issue |

## Inputs

- user question
- project root
- `.llm-wiki` root
- topic, module, requirement, bug, source, artifact, or dashboard hint
- optional current conversation context

## Outputs

Answer format:

```markdown
## Answer

## Project Context Pack

- project_root:
- wiki_pages_used:
- source_proxies_used:
- artifacts_used:
- related_requirements:
- related_bugs:
- related_modules:
- related_session_digests:
- open_questions:
- confidence:

## Evidence

## Inference

## Possible Next Routes
```

Rules:

- Name the wiki pages used.
- State when evidence is insufficient.
- Do not expose sensitive raw content.
- Do not present inference as sourced fact.
- Treat Session Digests as recall context by default. They help recover what was discussed, but they are not confirmed project truth, scope, Flow Record, dashboard, or verification evidence unless selected items were explicitly promoted through Lifecycle Promotion. Prefer current code, current user confirmation, and current requirement/bug pages when conflicts exist.
- Keep the context pack small enough to feed into later discussion or lifecycle work.

Dashboard-refresh completion rules:

- Do not report completion if a child Flow Record appears only in evidence links or parent-card prose.
- Do not report completion if visible board cards and `dashboardData.flowRecords` disagree for any `flow_id`.
- Do not report completion if lane count badges do not match the visible cards in each lane.

## Context Handoff

If the user upgrades after query, provide a handoff:

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

For pure query mode, `lifecycle_session` can be `none`.

## Return Handoff

Return:

```markdown
## Return Handoff

- stage_or_bridge_used: project-query
- result_summary:
- changed_assumptions:
- recommended_scope_changes:
- artifacts:
- verification_notes:
- lifecycle_updates_needed:
- next_gate:
```

For read-only query, `lifecycle_updates_needed` is usually `none`.

For dashboard refresh:

```markdown
## Dashboard Refresh

- dashboard_path:
- evidence_used:
- flow_records_used:
- updated_sections:
- unchanged_sections:
- unsupported_claims_downgraded:
- next_action:
```

## Boundaries

- Do not modify code.
- Do not create or update `.llm-wiki` by default.
- In `dashboard-refresh` mode, modify only `.llm-wiki/dashboard/progress.html`, `.llm-wiki/artifacts/index.md` dashboard metadata when needed, and `.llm-wiki/log.md`.
- In `dashboard-refresh` mode, do not create Change Briefs or mark plan/development/testing/archive done; show unmatched source/design docs as candidate or pending.
- Do not create Change Brief, Bug Brief, or working-context unless the user explicitly asks to save or act.
- Do not deep-read every source or module.
- Do not treat stale wiki summaries as authoritative over source code, tests, or current user decisions.
- Do not route to full lifecycle just because a topic is development-related.

## Common Mistakes

- Treating every project question as `project-develop`.
- Creating Change Briefs for exploratory discussion.
- Ignoring `.llm-wiki` indexes and jumping straight to raw source files.
- Letting "real code first" override the query boundary. For project questions like "what exists here" or "how is this API called", use `project-query` first to recover requirement/source/working-context evidence, then inspect code only to verify current behavior.
- Returning a broad essay instead of a small context pack.
- Failing to name the wiki pages used.
- Hiding uncertainty when wiki evidence is stale or missing.
- Treating dashboard refresh as project finish.
