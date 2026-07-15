# Context Digest / Session Digest

This reference defines how `project-session-extract` turns historical AI/team chat into recallable project context.

The default output is a **Context Digest**. It helps future agents and users quickly recover what was discussed. It is not a requirement, bug, Flow Record, scope update, dashboard update, or verification record.

## Core Model

```text
historical chat/session
-> brief candidate list
-> user selects useful items
-> Context Digest Markdown draft
-> user confirms writing
-> .llm-wiki/session-digests/<digest_id>.md
-> optional Lifecycle Promotion
```

Context Digest is the buffer layer. Lifecycle Promotion is a separate decision.

## Why This Exists

Historical conversations are usually messy. A single session may contain:

- requirement hints
- bug symptoms
- design decisions
- failed attempts
- verification notes
- tooling discussion
- ordinary chat
- outdated ideas

Forcing all of that into requirement, bug, or Flow Record types too early creates false project truth. The first goal is context recovery. Structure comes later, only when the user chooses what matters.

## Default Behavior

`project-session-extract` should:

1. Identify the session source and sensitivity.
2. Extract a short candidate list.
3. Ask the user which items to keep.
4. Draft a Context Digest Markdown preview.
5. Write the digest only after user confirmation.
6. Keep project truth unchanged by default.

By default it must not:

- create or update requirements
- create or update bugs
- create or update Flow Records
- refresh dashboard
- change active scope
- claim verification status
- treat digest content as source of truth

## Candidate List

First preview should stay lightweight:

```text
我从这段历史 session 中提取到这些候选上下文：
建议导入：
1. ...
2. ...

可选导入：
1. ...

不建议导入：
- ...

下一步：
请告诉我要保留哪些条目。你选定后，我会先整理成 Session Digest Markdown 草稿，不会直接写入 `.llm-wiki`。
```

Use simple buckets:

- `recommended`: useful for future context recovery
- `optional`: possibly useful, but noisy or indirect
- `do-not-import`: raw noise, secrets, unrelated content, stale attempts, or content that should not be preserved

Do not ask the user to classify every item as requirement/bug/tooling. If classification helps reading, mention it lightly inside the item text.

## Context Digest Template

Use this template for the Markdown draft and final file:

```markdown
# Context Digest: <title>

- digest_id:
- source_type:
- source_label:
- session_date:
- extracted_date:
- import_status: candidate | imported
- import_type: recall-context
- project_truth_update: no
- scope_update: no
- flow_record_update: no
- sensitivity:

## What This Context Is About

## Start Here Next Time

## Key Points

## Useful Clues

## Involved Files / Modules / Commands

## Uncertain Or Needs Reconfirmation

## Not Imported

## Promotion Candidates

## Import Record
```

## Field Rules

- `source_type`: `pasted-chat | transcript-file | exported-json | handoff | summary | unknown`
- `source_label`: stable label, not a personal absolute path
- `import_type`: always `recall-context` unless a future design adds another explicit import mode
- `project_truth_update`: default `no`
- `scope_update`: default `no`
- `flow_record_update`: default `no`
- `Promotion Candidates`: list possible lifecycle targets without writing them

Do not record personal workstation paths such as `C:\Users\...` or `D:\workspace\...` as durable source labels. Use a stable label such as `external/session/<name>` or `codex-session-jsonl/<topic>`.

## Lifecycle Promotion

Lifecycle Promotion is the act of turning selected digest items into lifecycle objects:

- requirement
- bug
- design decision
- working-context
- execution plan
- verification record
- handoff
- Flow Record
- dashboard evidence

Promotion requires explicit user confirmation. A confirmed Context Digest alone is not enough.

Promotion flow:

```text
Context Digest item
-> user selects item for promotion
-> agent proposes lifecycle target
-> user confirms target
-> route to project-develop / project-fix / project-finish / project-review
-> write lifecycle object with evidence
```

## Authority Order

When digest content conflicts with current evidence, use this authority order:

```text
current source code and runtime evidence
-> current user confirmation
-> current .llm-wiki requirement/bug/module pages
-> promoted digest items
-> unpromoted Context Digest recall notes
-> historical session statements
-> agent inference
```

Unpromoted Context Digest content is recall context, not project truth.

## Relationship To Other Skills

`project-ingest` handles source documents such as PRDs, links, Markdown, PDF, Word, logs, meeting notes, and customer feedback.

`project-session-extract` handles conversations and transcripts. If a conversation mentions a real source document, record it as a source candidate and recommend `project-ingest` when the source itself should be preserved.

`project-query` may use Context Digests to recover previous discussion, but must distinguish recall context from confirmed project truth.

`project-develop` and `project-fix` may use Context Digests to recover background, but must reconfirm or promote items before treating them as requirements or bug evidence.

`project-finish` may record that a digest item was confirmed or rejected by actual implementation evidence, but should not silently change lifecycle state because a digest exists.

`project-review` should flag any case where an unpromoted digest item created or changed requirement, bug, Flow Record, dashboard, scope, or verification state.

## Dashboard Rule

Context Digest import does not refresh dashboard by default.

Dashboard may change only after explicit Lifecycle Promotion that affects visible Flow Record state, evidence, risk, blocker, or next action.

## Done Criteria

A session extraction is complete when:

- source and sensitivity were identified
- a brief candidate list was shown first
- the user selected items
- a Context Digest Markdown draft was shown
- the user confirmed writing
- `.llm-wiki/session-digests/<digest_id>.md` was written
- project truth, scope, Flow Record, dashboard, and verification state remained unchanged unless separate promotion was confirmed
