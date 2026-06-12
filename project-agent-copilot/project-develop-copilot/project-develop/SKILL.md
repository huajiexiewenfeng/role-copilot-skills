---
name: project-develop
description: Use when developing or changing a project requirement, feature, API/protocol behavior, or code path with project-local context; use before implementation whenever a change needs a requirement/doc anchor, scoped context, acceptance criteria, or `.llm-wiki` Flow Record.
---

# Project Develop

## Purpose

Develop a feature or requirement from scoped project context into clarified requirements, an implementation plan, and, when the user confirms, code changes.

This skill owns the requirement/feature development stage. It does not own top-level routing, bug diagnosis, final finish sync, or merge-readiness review.

## When to Use

Use when the user asks to:

- discuss, clarify, plan, or implement a feature or requirement
- turn PRD/design/source material into scoped project work
- create or update a Change Brief
- bridge to brainstorming, writing-plans, TDD, or executing-plans after project context is scoped
- continue requirement work already represented by a Change Brief or working-context

## When Not to Use

- Do not use for lightweight design discussion when the user explicitly says not to save or implement.
- Do not use for bug symptoms, logs, failed tests, or regressions; use `project-fix`.
- Do not use for final status sync after implementation; use `project-finish`.
- Do not use for findings-first review; use `project-review`.

## Owned Gates

- Context Recovery Gate
- Lifecycle Anchor Gate for Change Brief creation/resume when routed here
- Work Definition Gate
- Scope Lock Gate
- External Bridge Gate

## Required First Check

1. Resolve project root.
2. Resolve optional shared references from `../references/` or local `references/`. If `change-brief.md` or `flow-record.md` is missing, continue in degraded mode using the minimum rules in this skill; report the missing deep references, keep the Change Brief and Flow Record conservative, and do not invent unsupported lifecycle facts.
3. Confirm this is full lifecycle requirement work, not lightweight-answer.
4. Before any code edit, decide and state the documentation mode: update existing Change Brief, create new Change Brief, create child Change Brief, or no durable doc needed only when the user explicitly requests throwaway/exploratory work.
5. Create or resume Change Brief in `.llm-wiki/requirements/<change-id>.md`.
6. Recover relevant `.llm-wiki`, source proxies, modules, and working-context.
7. If the requirement involves external calls, upstream/downstream services, Feign, MQTT, HTTP, RPC, shared DB, or shared config, check Project Graph pins/edges/candidates and run the Cross-Project Boundary Gate before relying on external contract behavior.
8. Identify active, read-only, candidate, and excluded scopes before planning or implementation.
9. Before writing any execution plan, verify the Change Brief exists, contains `flow_id`, acceptance criteria, scope, non-goals, and a `## Flow Record` table. If it does not, create or update the Change Brief first.


## Lifecycle Anchor Gate

Before modifying production code, tests, configuration, public APIs, protocol methods, DTOs, topics, database schema, or user-visible behavior, the Lifecycle Anchor Gate requires a `.llm-wiki` documentation anchor.

Even if the requirement is one sentence, create or update a Change Brief that states:

- why the change exists
- what changes
- what does not change
- acceptance criteria
- active scope
- verification plan
- Flow Record

Do not treat a small code diff as exempt from this gate. If the user asks to "just continue" or "just make the change", still perform the documentation-mode decision first unless they explicitly say the work is throwaway or exploratory.

## Change Brief Selection

Update an existing Change Brief when:

- the original Flow is still active or not yet implemented
- the change only clarifies scope, acceptance criteria, field meaning, or non-goals
- no independent delivery or verification loop is needed

Create a new Change Brief when:

- the prior requirement is implemented, committed, verified, or waiting deployment
- the change adds an API, protocol method, topic, DTO, field, endpoint, behavior, or compatibility surface
- external callers, tests, deployment notes, or acceptance criteria change
- the change is small but creates a new observable contract

Create a child Change Brief when:

- the work belongs to a larger parent requirement
- it can be developed, tested, or deployed independently
- adding it to the parent would make the parent vague or oversized

Create or update a working-context document before implementation when:

- the change touches multiple files
- TDD steps are needed
- the change affects protocol/API compatibility
- the change has important non-goals
- verification may be blocked or staged

For truly tiny changes, the Change Brief may contain the implementation plan inline, but it still needs a Flow Record.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/change-brief.md`
- `../references/project-graph.md`
- `../references/cross-project-refs.md`
- `../references/flow-record.md`
- `../references/session-digest.md`
- `../references/scoped-working-context.md`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md`
- `../references/templates.md`

Reference availability policy:

- Shared references are deep references, not startup requirements.
- Do not stop solely because `../references/` is missing.
- In degraded mode, require a minimal Change Brief anchor before code edits: why, what changes, non-goals, active scope, acceptance, verification plan, and `flow_id`.
- If detailed templates are unavailable, write compact Markdown sections instead of blocking the work.

Authority order:

1. User's current request and explicit decisions.
2. Source code, tests, configuration, build files, and runtime evidence.
3. Original requirement sources such as PRD, issue, design doc, meeting notes, URL, PDF, Word, or Markdown.
4. `.llm-wiki` index and summaries.
5. Legacy `docs/ai-coding` or generated AI docs.

When Session Digests exist for the active discussion, treat them as recall context first. Use them to recover prior requirement discussion, design choices, acceptance criteria, scope decisions, and plan candidates, but do not treat them as source evidence or project truth unless selected items were explicitly promoted through Lifecycle Promotion.

Workflow:

1. Resolve project root and output language when relevant.
2. Search existing Change Briefs, working-context pages, artifacts, and source indexes for a matching `flow_id`.
3. Search `.llm-wiki/session-digests/` entries for related recall context. Use promoted digest items as evidence only when promotion is explicitly recorded.
4. Create or resume Change Brief.
5. Run Context Recovery Gate before brainstorming, planning, or implementation.
6. If the requirement crosses service/project boundaries, check Project Graph evidence in order: `.llm-wiki/cross-refs/index.md` pin -> `.llm-wiki/project-graph/edges.md` -> `.llm-wiki/project-graph/candidates.md`.
   - If a pin matches, follow `edge_id`; do not treat pin fields as contract facts.
   - If only a candidate matches, it is a clue only; perform source verification before using it for an implementation decision.
   - If no edge or candidate exists, suggest manual registration via `project-maintain` only after the contract evidence is clear enough.
   - If a registry mapping is missing, ask for the local path and write only `.llm-wiki/registry.local.json` after confirmation.
   - Before reading remote wiki or source, output Cross-Project Boundary Gate with `scope: read-only`.
   - If implementation depends on the remote contract, use `verification_required: source`.
   - Do not base implementation decisions on `wiki-checked`, `draft`, or candidate-only evidence.
   - Record remote evidence in the Change Brief `## External Dependencies` section with `project_id`, `edge_id`, dependency, verification status, required contract, implementation impact, and handoff.
7. Produce a concise context summary.
8. Run Work Definition Gate before implementation planning.
9. Guide the user conversationally through requirement discussion.
10. Use brainstorming after scoped context recovery when tradeoffs or acceptance behavior need discussion; treat it as a discussion/design method only, and keep durable project outputs in `.llm-wiki` unless the user explicitly requests Superpowers artifacts.
11. Capture an OpenSpec-style change summary even when no OpenSpec tool is installed.
12. Create or update the Change Brief Flow Record so the source/design document, execution plan, development, testing, and archive steps can be tracked on the dashboard.
13. If a candidate Flow Record match exists, ask one confirmation question before reusing it.
14. Do not create `.llm-wiki/working-context/*execution-plan*.md` until the Change Brief exists and links to the same `flow_id`.
15. If planning reveals a new implementation scope or child deliverable, create a child Change Brief with `parent_flow_id` before writing its execution plan.
16. Do not enter implementation planning until requirement summary, acceptance criteria, active scope, non-goals, and required source-verified external contracts are confirmed or accepted as assumptions.
17. Provide Context Handoff before external planning/TDD/execution bridges.
18. Run Scope Lock Gate before implementation.
19. Ask for implementation confirmation unless the user already explicitly asked to implement now.
20. Update Change Brief and working-context after clarification, planning, or implementation.
21. Return decisions, plan or changes, verification notes, artifacts, Flow Record updates, external dependency status, and next gate.

## Mode / Entry Selection

| Mode | Use when |
|---|---|
| `requirement-discussion` | user wants to discuss or clarify before planning |
| `plan-confirmation` | requirement is clarified and a plan should be written or confirmed |
| `execution-handoff` | user explicitly asks to implement and context is locked |
| `scope-escalation` | implementation needs candidate or excluded scope |
| `resume-change` | an existing Change Brief or working-context should continue |

## Inputs

- user request and explicit decisions
- Change Brief
- PRD/design/source proxy
- `.llm-wiki/index.md`, modules, ingest index, requirements, working-context
- active/read-only/candidate/excluded scopes
- acceptance criteria and non-goals

## Outputs

- requirement summary
- acceptance criteria
- active sources
- related Session Digests when used
- external dependencies and verification status when cross-project refs are involved
- active, read-only, candidate, and excluded scopes
- non-goals and constraints
- open questions
- OpenSpec-style change summary
- Flow Record status updates
- flow_id reused or created
- Context Handoff for external bridges
- Return Handoff after planning or implementation
- recommendation: continue discussion, write plan, implement, finish, or review

## Context Handoff

Before brainstorming, planning, TDD, execution, or any external bridge, output:

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

## Return Handoff

After planning or implementation, report:

```markdown
## Return Handoff

- stage_or_bridge_used: project-develop
- result_summary:
- changed_assumptions:
- recommended_scope_changes:
- artifacts:
- verification_notes:
- external_dependencies:
- lifecycle_updates_needed:
- next_gate:
```

OpenSpec-style summary:

```text
Change:
Why:
Acceptance criteria:
Active sources:
External dependencies:
Active scopes:
Out of scope:
Plan:
Risks:
Verification:
```

Map this summary into the Change Brief and Flow Record. Do not create a separate OpenSpec directory or OpenSpec change unless the repository already uses OpenSpec and the user explicitly asks to operate that toolchain. If this work later needs continuation or archive evidence, prepare the final project handoff under `.llm-wiki/handoff/` through `project-finish`.

## Team-Shared Wiki Rules

`.llm-wiki` is a team-shared project knowledge base, not a workstation scratchpad. When writing requirement, design, working-context, source, index, manifest, or module pages under `.llm-wiki`:

- Use project-relative or `.llm-wiki`-relative paths, such as `../sources/proxies/<batch-id>/<source>.md`, `../modules/<module>/context.md`, or `../../dji-dock3-adapter/...`.
- Do not write workstation-specific absolute paths such as `C:\Users\...`, `D:\workspace\...`, `/Users/...`, or `/home/...` into durable `.llm-wiki` pages.
- For external local files used as evidence, ingest or summarize them through project-ingest first, then cite the wiki-local proxy/original path. If they are only inspected temporarily, describe them as temporary local references and do not persist their absolute paths.
- Do not create new durable requirement/design artifacts under `docs/superpowers/` unless the user explicitly asks for Superpowers output or the repository has an active team convention to keep that feature's source artifacts there.
- If a source exists both in the original repository path and under `.llm-wiki/sources/originals/`, prefer the wiki-local source path when writing team-shared wiki pages; use original paths only as transient investigation context.

## Brainstorming Override

When bridging to brainstorming, project-develop owns durable project outputs. Brainstorming may shape questions, tradeoff analysis, and design review, but its generic instruction to write validated specs under `docs/superpowers/specs/` is overridden unless the user explicitly requested a Superpowers spec or the repository has an active team convention for that feature. In the normal project-local workflow, write requirement and design results to `.llm-wiki/requirements/<change-id>.md`, and create `.llm-wiki/working-context/<change-id>.md` when broader implementation context is needed.

## Boundaries

- Do not pull all services in a monorepo into context by default.
- Do not use candidate or excluded modules as write scopes.
- Do not expand scope without evidence or user confirmation.
- Do not let an execution plan be the first durable artifact for a requirement; the Change Brief comes first.
- Do not create an execution plan for a candidate scope that has become active without first adding or updating its parent or child Change Brief.
- Do not update legacy `docs/ai-coding` unless explicitly asked.
- Do not copy secrets or long original content into `.llm-wiki`.
- Do not modify production code during requirement discussion, context recovery, or planning unless the user explicitly asks to proceed.
- Do not generate or require codegraph unless scope is ambiguous, cross-module impact is complex, or the user asks for it.
- Do not force full brainstorming/spec output for every feature. In project-local `.llm-wiki` workflows, do not inherit brainstorming's default `docs/superpowers/specs/` output path.
- Do not edit remote project wiki, source, config, or registry during cross-project evidence gathering. Generate a context handoff if remote project changes are needed.

## Common Mistakes

- Starting implementation during clarification.
- Starting code changes for a small API/protocol gap without first choosing whether to update an existing Change Brief, create a new Change Brief, or create a child Change Brief.
- Creating plans without linking them to Change Brief.
- Creating execution plans without first creating the requirement/Change Brief page.
- Treating a newly added implementation scope as "just part of the plan" instead of giving it a parent-linked child Flow Record.
- Letting brainstorming or writing-plans choose project scope from scratch.
- Letting brainstorming write new durable docs under `docs/superpowers/` when the project target is `.llm-wiki`.
- Persisting local workstation absolute paths in `.llm-wiki` requirement, source, module, or working-context pages.
- Expanding scope because a plan suggests it, without evidence or user confirmation.
- Treating lightweight design discussion as full lifecycle.
- Making implementation decisions from `wiki-checked` external evidence when the remote contract needs source verification.
- Forgetting Return Handoff after planning or implementation.
