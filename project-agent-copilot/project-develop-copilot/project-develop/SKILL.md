---
name: project-develop
description: Use when developing a project requirement or feature with project-local context, scoped modules, active sources, LLM Wiki requirement summaries, implementation planning, or bridging Superpowers/OpenSpec-style planning inside scoped project context.
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

- Context Enrichment Gate
- Clarification Gate
- Lifecycle Session Gate for Change Brief creation/resume when routed here
- Context Lock Gate
- External Skill Bridge Gate

## Required First Check

1. Resolve project root.
2. Confirm this is full lifecycle requirement work, not lightweight-answer.
3. Create or resume Change Brief.
4. Recover relevant `.llm-wiki`, source proxies, modules, and working-context.
5. Identify active, read-only, candidate, and excluded scopes before planning or implementation.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/change-brief.md`
- `../references/scoped-working-context.md`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md`
- `../references/templates.md`

Authority order:

1. User's current request and explicit decisions.
2. Source code, tests, configuration, build files, and runtime evidence.
3. Original requirement sources such as PRD, issue, design doc, meeting notes, URL, PDF, Word, or Markdown.
4. `.llm-wiki` index and summaries.
5. Legacy `docs/ai-coding` or generated AI docs.

Workflow:

1. Resolve project root and output language when relevant.
2. Create or resume Change Brief.
3. Run Context Enrichment Gate before brainstorming, planning, or implementation.
4. Produce a concise context summary.
5. Run Clarification Gate before implementation planning.
6. Guide the user conversationally through requirement discussion.
7. Use brainstorming after scoped context recovery when tradeoffs or acceptance behavior need discussion.
8. Capture an OpenSpec-style change summary even when no OpenSpec tool is installed.
9. Do not enter implementation planning until requirement summary, acceptance criteria, active scope, and non-goals are confirmed or accepted as assumptions.
10. Provide Context Handoff before external planning/TDD/execution bridges.
11. Run Context Lock Gate before implementation.
12. Ask for implementation confirmation unless the user already explicitly asked to implement now.
13. Update Change Brief and working-context after clarification, planning, or implementation.
14. Return decisions, plan or changes, verification notes, artifacts, and next gate.

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
- active, read-only, candidate, and excluded scopes
- non-goals and constraints
- open questions
- OpenSpec-style change summary
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
- lifecycle_updates_needed:
- next_gate:
```

OpenSpec-style summary:

```text
Change:
Why:
Acceptance criteria:
Active sources:
Active scopes:
Out of scope:
Plan:
Risks:
Verification:
```

## Boundaries

- Do not pull all services in a monorepo into context by default.
- Do not use candidate or excluded modules as write scopes.
- Do not expand scope without evidence or user confirmation.
- Do not update legacy `docs/ai-coding` unless explicitly asked.
- Do not copy secrets or long original content into `.llm-wiki`.
- Do not modify production code during requirement discussion, context recovery, or planning unless the user explicitly asks to proceed.
- Do not generate or require codegraph unless scope is ambiguous, cross-module impact is complex, or the user asks for it.
- Do not force full brainstorming/spec output for every feature.

## Common Mistakes

- Starting implementation during clarification.
- Creating plans without linking them to Change Brief.
- Letting brainstorming or writing-plans choose project scope from scratch.
- Expanding scope because a plan suggests it, without evidence or user confirmation.
- Treating lightweight design discussion as full lifecycle.
- Forgetting Return Handoff after planning or implementation.