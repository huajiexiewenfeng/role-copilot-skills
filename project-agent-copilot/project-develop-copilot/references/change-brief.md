# Change Brief

Read `north-star.md` first. Change Brief is the lightweight internal OpenSpec-style mechanism for Project Develop Copilot.

## Purpose

Change Brief solves one practical problem:

```text
How does the agent know what requirement is being developed, which sources and plans belong to it, whether it is ready to execute, and what still needs confirmation?
```

It is not a full OpenSpec clone.
It is not a separate tool.
It is not a form users must manually fill.

The agent maintains Change Brief pages inside `.llm-wiki`.
Users provide source material, intent, and key confirmations through normal conversation.

## File

Use one page per change:

```text
.llm-wiki/requirements/<change-id>.md
```

For complex or cross-module work, also use:

```text
.llm-wiki/working-context/<change-id>.md
```

## User Effort Rule

Minimize user operations.

Users should not need to edit Change Brief files directly.
They can simply say things like:

```text
Use project-develop for this requirement. The source is docs/ingest/media-transfer.md.
```

or:

```text
按这个计划执行。
```
The agent must infer and maintain the Change Brief, then ask only for key confirmations that materially affect scope, acceptance, risk, or execution.

## Change ID

`project-develop` generates or reuses `change-id` during Clarification Gate.

Use this order:

1. User-provided issue, ticket, requirement, or task id.
2. Existing matching requirement page.
3. Source id or source filename.
4. Short agent-generated kebab-case title.

Rules:

- Keep it short, stable, readable, and path-safe.
- Prefer English/kebab-case for filenames.
- Do not create a new id when a matching existing requirement is confirmed.
- If only a candidate match exists, ask before reusing it.

## Minimum Structure

Use this compact shape:

```markdown
# Change Brief: <change-id>

## Summary

- title:
- status: draft | clarified | planned | ready | executing | done | blocked

## Sources

- 

## Scope

- active:
- reference-only:
- excluded:

## Acceptance

- 

## Plan

- active_plan:
- status: none | candidate | confirmed | stale
- evidence:

## Open Questions

- 

## Notes

- 
```

The selected output language controls headings, prose, summaries, and notes.
Keep paths, commands, code identifiers, and status values stable in English.

## Status

Use a small status set:

| Status | Meaning |
|---|---|
| `draft` | Change exists, but scope or acceptance is still unclear. |
| `clarified` | Goal, scope, and acceptance are clear enough to plan. |
| `planned` | A plan exists, but execution is not confirmed. |
| `ready` | Plan or implementation direction is confirmed and can execute. |
| `executing` | Implementation is in progress. |
| `done` | Work is completed and synced. |
| `blocked` | Work cannot proceed; blocker is recorded. |

## Plan Status

Keep plan linkage minimal:

| Plan Status | Rule |
|---|---|
| `none` | No plan exists yet. |
| `candidate` | A possible plan exists, but must not be executed without confirmation. |
| `confirmed` | User or existing brief confirmed this plan belongs to the change. |
| `stale` | Plan no longer matches current scope, acceptance, or source material. |

## Develop Decision Logic

`project-develop` uses the Change Brief to decide the mode:

```text
No Change Brief:
  create draft
  run Clarification Gate

Brief exists but scope or acceptance is missing:
  ask the smallest necessary question
  bridge brainstorming when discussion is useful

Brief clarified but no plan:
  bridge brainstorming if needed
  write or request implementation plan

Brief has candidate plan:
  summarize evidence
  ask user whether to confirm it as active_plan

Brief has confirmed plan and status ready:
  execute unless the user asks to revisit the requirement

User explicitly says "execute" or "按计划执行":
  execute if scope, acceptance, and plan are sufficient
  otherwise ask one blocking question
```

## Brainstorming Bridge

Change Brief does not replace Superpowers brainstorming.

Use this order:

```text
Context Enrichment Gate
-> Change Brief lookup/create
-> Clarification Gate
-> brainstorming when requirement, scope, acceptance, or tradeoffs need discussion
-> update Change Brief
-> plan or execute
```

The user does not need to ask for brainstorming explicitly.

## Finish And Review

`project-finish` updates the Change Brief after verified work:

- status
- plan status
- verification notes
- implementation notes
- residual risk

`project-review` checks:

- code changes match the Change Brief
- scope did not drift
- candidate plans were not executed without confirmation
- verification matches acceptance
- wiki status is not stale

## Non-Goals

Do not add these in MVP:

- source hash fingerprints
- split/merge requirement graph
- complex requirement entity model
- separate OpenSpec directory
- mandatory OpenSpec CLI or tooling
- user-maintained forms

## Completion Rule

A Change Brief is good enough when it lets the next agent answer:

```text
What is this change?
Which sources belong to it?
Which scope is active?
What acceptance behavior matters?
Is there a confirmed plan?
Can I execute, or do I need one key confirmation?
```
