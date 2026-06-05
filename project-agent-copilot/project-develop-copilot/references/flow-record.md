# Flow Record

Read `north-star.md`, `change-brief.md`, and `progress-dashboard.md` when changing this document.

## Purpose

Flow Record is the lightweight project lifecycle record that links project documents and execution state.

It solves this practical problem:

```text
How do we know which requirement document, design document, execution plan, implementation, test evidence, and archive note belong to the same piece of work?
```

The answer is one stable `flow_id`, usually the same value as `change_id` or `bug_id`.

```text
source/design document
-> flow_id
-> Change Brief or Bug Brief
-> plan
-> implementation
-> testing
-> archive
-> dashboard card
```

## Design Judgment

This design is useful and should stay small.

Good:

- one stable id connects scattered documents and status
- dashboard can show progress without becoming source of truth
- future agents can resume from `.llm-wiki`, not chat memory
- old copied documents can be shown as candidate work until confirmed

Risks:

- over-modeling it into a full issue tracker
- forcing users to maintain forms
- creating fake progress when evidence is missing
- splitting one real change into too many tiny records
- merging unrelated document changes into one vague record

The MVP rule is:

```text
One meaningful deliverable gets one Flow Record.
```

## Identity

Use this order to choose `flow_id`:

1. Existing `change_id` or `bug_id`.
2. User-provided issue, ticket, requirement, or task id.
3. Existing matching Change Brief or Bug Brief.
4. Source document slug.
5. Short agent-generated kebab-case id.

Rules:

- Keep it stable, readable, and path-safe.
- Prefer English/kebab-case for filenames.
- Do not create a new id if an existing record clearly matches.
- Ask before reusing a candidate match when the evidence is ambiguous.
- Do not encode temporary status into the id.

## Matching Existing Records

Before creating a new Flow Record, search:

```text
.llm-wiki/requirements/
.llm-wiki/bugs/
.llm-wiki/working-context/
.llm-wiki/artifacts/index.md
.llm-wiki/log.md
```

Match by:

- same user-provided id or issue/ticket id
- same source document path
- same source proxy id
- same title and acceptance behavior
- same active module/scope and same plan evidence

Decision:

```text
clear match:
  reuse existing flow_id

candidate match:
  summarize evidence
  ask one confirmation question before reusing

no match:
  create a new flow_id
```

Never create duplicate Flow Records only because the user phrased the same requirement differently in chat.

## Storage

Primary storage:

```text
.llm-wiki/requirements/<flow_id>.md
.llm-wiki/bugs/<flow_id>.md
```

Optional cross-module or complex work:

```text
.llm-wiki/working-context/<flow_id>.md
```

Dashboard projection:

```text
.llm-wiki/dashboard/progress.html
```

Artifact registry:

```text
.llm-wiki/artifacts/index.md
```

## Minimal Shape

Inside a Change Brief or Bug Brief:

```markdown
## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | pending |  |  |
| design | pending |  |  |
| plan | pending |  |  |
| development | pending |  |  |
| testing | pending |  |  |
| archive | pending |  |  |
```

Status values:

| Status | Meaning |
|---|---|
| `pending` | Step has not started or evidence is missing. |
| `active` | Step is currently being worked on. |
| `done` | Step has supporting evidence. |
| `blocked` | Step cannot progress; blocker is recorded. |
| `skipped` | Step is intentionally not needed for this record. |

## Step Semantics

| Step | Evidence examples | Who updates |
|---|---|---|
| `source` | PRD, issue, meeting note, copied Markdown, PDF/Word proxy, source summary | `project-ingest`, `project-develop`, `project-query dashboard-refresh` |
| `design` | design doc, architecture decision, brainstorming summary, API contract, UX note | `project-develop` |
| `plan` | confirmed implementation plan, execution checklist, accepted approach | `project-develop` |
| `development` | changed files, implementation summary, branch/commit note, working-context update | `project-develop`, `project-fix`, `project-finish` |
| `testing` | test command, compile result, manual verification, accepted limitation | `project-finish`, `project-review` |
| `archive` | handoff summary, done note, final artifact, release/deploy note | `project-finish` |

Do not mark `development`, `testing`, or `archive` as `done` without evidence.

## Lifecycle

### Ingest

`project-ingest` may create source proxies and indexes. It does not need to create a Flow Record for every document.

When a document looks like a concrete requirement, design, bug, or delivery item, it can mark it as a candidate Flow Record in the ingest summary.

### Develop

`project-develop` creates or resumes the Flow Record when the user starts requirement/design discussion or execution.

It should:

- map active source/design documents to one `flow_id`
- create or update the Change Brief
- update source/design/plan steps as evidence appears
- ask only for blocking confirmation when the match or execution plan is ambiguous

### Fix

`project-fix` uses the same idea through Bug Briefs.

Bug flow records normally use:

```text
source -> design/diagnosis -> plan/fix direction -> development -> testing -> archive
```

### Dashboard Refresh

`project-query dashboard-refresh` reads existing Flow Records and updates the static dashboard.

It must not invent completion. If a source/design document has no Flow Record, show it as `candidate` or `pending` and recommend creating or confirming the Change Brief.

### Finish

`project-finish` closes the loop after verification or accepted limitation.

It updates:

- development evidence
- testing evidence
- archive/handoff evidence
- dashboard projection
- artifact registry when useful

### Review

`project-review` checks drift:

- dashboard card matches Flow Record
- Flow Record evidence exists
- code changes match active scope
- testing status matches verification evidence
- archive/done status is not claimed prematurely

## Dashboard Projection

Dashboard cards are views of Flow Records, not separate tasks.

Minimum card fields:

```text
flow_id:
title:
step: source | design | plan | development | testing | archive
status: pending | active | done | blocked | skipped
source:
evidence:
updated:
```

Recommended lanes:

```text
需求/来源
设计
执行计划
开发
测试
归档
```

The same `flow_id` may appear in multiple lanes when each card represents a distinct step with distinct evidence.

## Split And Merge Rules

Split one source document into multiple Flow Records only when:

- different acceptance behavior must be verified separately
- different modules or owners will execute independently
- one part can finish while another remains blocked
- the user or project source clearly separates them

Do not split only because a document has many paragraphs.

Merge candidate records only when:

- they point to the same deliverable
- scope and acceptance are the same
- one active plan can cover them

When unsure, keep records separate as candidates and ask one confirmation question.

## User Effort Rule

The user should not fill Flow Record tables manually.

The user can say:

```text
这个需求按这个设计走。
```

or:

```text
更新项目看板。
```

The agent maintains records from evidence and asks only when a decision changes scope, execution, verification, or risk.

## Non-Goals

- no separate issue tracker
- no required OpenSpec CLI
- no source hash requirement in MVP
- no graph database
- no mandatory user-maintained forms
- no automatic claim that copied docs are active work

## Good Enough

A Flow Record is good enough when the next agent can answer:

```text
What is the work?
Which documents belong to it?
What is designed?
Is there a confirmed execution plan?
What has been developed?
What has been tested?
Is it archived or still active?
Which dashboard card should show it?
```
