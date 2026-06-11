---
name: project-develop-copilot
description: Use when the user wants project development help from natural intent, including requirements, bugs, logs, design discussion, file lookup, progress, finish, review, resume, or routing into project lifecycle skills.
---

# Project Develop Copilot

## Purpose

`project-develop-copilot` is the top-level lifecycle router for project development work.

It helps users enter naturally without choosing a child skill first. It decides whether the request should stay lightweight or enter the full project lifecycle, then routes full work into the right stage while preserving scope, lifecycle state, handoff, verification, knowledge sync, artifact sync, dashboard sync, and review.

It does not replace `project-query`, `project-init`, `project-ingest`, `project-develop`, `project-fix`, `project-finish`, or `project-review`. It owns routing and lifecycle continuity; stage skills own stage execution.

## When to Use

Use this skill when the user asks for project development help from natural language, including:

- Finding, explaining, querying, or discussing project `.llm-wiki`, requirements, bugs, design docs, README files, skills, references, artifacts, or current project status.
- Developing a feature, requirement, PRD, design change, implementation plan, or scoped project change.
- Diagnosing or fixing a bug, failed test, runtime error, log symptom, regression, incident, or unexpected behavior.
- Ingesting PRDs, logs, PDFs, URLs, meeting notes, customer feedback, or temporary source material into project context.
- Extracting, distilling, reviewing, or importing historical AI/team chat sessions, transcript files, old conversation summaries, colleague AI discussions, or previous agent handoffs into project `.llm-wiki`.
- Finishing work, syncing project knowledge, updating progress, preparing handoff, or checking done status.
- Refreshing or updating the static project dashboard/progress page without claiming work is finished.
- Checking, auditing, maintaining, or repairing project `.llm-wiki` structure, visibility, Flow Records, artifact registry entries, module backlinks, dashboard consistency, logs, links, or safety issues.
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

## Required First Check

Before doing project work:

1. Decide whether the request is `lightweight-answer` or `full-lifecycle`.
2. If lightweight-answer applies, answer from available evidence without creating lifecycle state.
3. If full lifecycle applies, resolve or ask for the project root when it is not obvious.
4. Create or resume a Lifecycle Session: Change Brief, Bug Brief, or working-context.
5. Save or update a short routing record.
6. Select one primary stage skill.
7. Select optional external bridge skills only after project scope is known.

## Core Process

1. Read `references/north-star.md` when goals, scope, or lifecycle ownership are unclear.
2. Read `references/lifecycle-router.md` for routing decisions and routing record format.
3. Classify the user request:
   - lightweight-answer
   - project wiki query / discussion context
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
| User says to discuss design and not implement | lightweight-answer | none |
| User provides PRD/source material to index | full-lifecycle | `project-ingest` |
| User provides or references historical AI/team chat, session transcript, old conversation summary, colleague AI discussion, previous agent handoff, or asks to distill/import previous session context into `.llm-wiki` | session-context-import | `project-session-extract` |
| User asks to initialize/adopt/refresh project context | full-lifecycle | `project-init` |
| User asks for a feature, requirement, plan, or implementation | full-lifecycle | `project-develop` |
| User reports a bug, log, error, failed test, or incident | full-lifecycle | `project-fix` |
| User asks to update, refresh, or sync the static dashboard/progress page only | dashboard-refresh | `project-query` |
| User asks why wiki pages cannot be found, or asks to check, audit, lint, repair, or maintain `.llm-wiki` structure, links, Flow Records, module backlinks, artifacts, logs, dashboard consistency, or safety | wiki-maintenance | `project-maintain` |
| User asks finish, done, sync, update status, or handoff | full-lifecycle | `project-finish` |
| User asks review, risk check, before commit/PR/merge | full-lifecycle | `project-review` |
| User says continue or resume previous work | full-lifecycle | resume then choose stage |
| User asks skill failure review, skill-evaluator, eval gap, failure case, golden case, self-review, conversation self-review, lifecycle trace review, or Dolores | lifecycle-quality | `project-review`, evaluator bridge, or Dolores bridge |

If confidence is low, ask one minimal routing question. Do not start a long intake form.

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
- "杩欎釜 skill 涓轰粈涔堣窇鍋?, "杩欎釜娴佺▼鏄笉鏄窇鍋忎簡", "鍏堜笉瑕佺洿鎺ユ敼锛岃瘎浼颁竴涓?
- "review the conversation trace", "did this lifecycle go wrong", "find the smallest patch"

Do not trigger lifecycle-quality for ordinary delivery requests such as "缁х画", "淇?bug", "review 浠ｇ爜", "瀹屾垚浜嗗悧", or "鎬荤粨涓€涓? unless the user also asks to evaluate the process or review the conversation lifecycle.

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
