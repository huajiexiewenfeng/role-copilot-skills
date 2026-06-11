# Change Brief

Read `north-star.md` and `flow-record.md` first. Change Brief is the lightweight internal OpenSpec-style mechanism for Project Develop Copilot.

## Purpose

Change Brief solves one practical problem:

```text
How does the agent know what requirement is being developed, which sources and plans belong to it, whether it is ready to execute, and what still needs confirmation?
```

It also acts as the project's lightweight flow record:

```text
design/source document -> execution plan -> development -> testing -> archive
```

Every meaningful requirement or design document that enters development should map to one stable `change-id` / `flow_id`, so the dashboard can show where that work is in the lifecycle and which evidence supports each step.

It is not a full OpenSpec clone.
It is not a separate tool.
It is not a form users must manually fill.
It is the destination for OpenSpec-style summaries produced during requirement discussion or planning.

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

This `change-id` is also the default `flow_id`. Follow `flow-record.md` matching rules before creating a new id.

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
- Do not create duplicate Change Briefs for the same source/design document and acceptance behavior.

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

## External Dependencies

- project-id:
- xref-id:
- dependency_type:
- required_contract:
- evidence:
- verification_status:
- derived_staleness:
- impact_on_change:
- fallback_or_handoff:

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | pending |  |  |
| design | pending |  |  |
| plan | pending |  |  |
| development | pending |  |  |
| testing | pending |  |  |
| archive | pending |  |  |

## Open Questions

- 

## Notes

- 
```

The selected output language controls headings, prose, summaries, and notes.
Keep paths, commands, code identifiers, and status values stable in English.

## External Dependencies Rules

Use `## External Dependencies` when a requirement depends on another project through Feign, MQTT, HTTP, RPC, shared DB, shared config, or another cross-service contract.

Rules:

- Start from `.llm-wiki/cross-refs/index.md` when a cross-project integration point may be involved.
- Use logical `project-id` and `xref-id`; do not persist local paths.
- Store evidence from the remote project as wiki-relative or source-relative anchors, not copied remote content.
- `verification_status` must be one of `draft`, `wiki-checked`, `source-verified`, or `blocked`.
- Do not write `stale` as a status. Use `derived_staleness: fresh | expired | unknown`.
- If implementation depends on the remote contract, require `source-verified` evidence before treating the dependency as ready.
- If only `wiki-checked` evidence exists, keep the dependency as a planning risk and do not make implementation decisions from it alone.
- If the remote project must change, create a context handoff for that project instead of editing it from the current lifecycle session.

## Flow Record Rules

The Flow Record is not another source of truth. It is a compact index that links lifecycle steps to evidence.

Use this small status set for each step:

| Status | Meaning |
|---|---|
| `pending` | Step has not started or evidence is missing. |
| `active` | Step is currently being worked on. |
| `done` | Step has supporting evidence. |
| `blocked` | Step cannot progress; blocker is recorded. |
| `skipped` | Step is intentionally not needed for this change. |

Evidence should be a path or short note pointing to:

- original source or design document
- confirmed implementation plan
- changed files or implementation summary
- verification notes, command output, or manual test notes
- handoff/archive note

Do not mark `development`, `testing`, or `archive` as `done` without matching evidence. If the user only asks to refresh dashboard, update the dashboard from existing Flow Records but do not invent new done states.

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
- Flow Record development/testing/archive steps
- verification notes
- implementation notes
- residual risk

`project-review` checks:

- code changes match the Change Brief
- dashboard cards match Flow Record evidence
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
- treating OpenSpec-style handoff as an independent lifecycle outside Change Brief / Flow Record
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
