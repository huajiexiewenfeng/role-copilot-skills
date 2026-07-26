---
name: project-session-extract
description: Use when extracting, summarizing, distilling, reviewing, or importing historical chat/session context into a project .llm-wiki as recallable Session Digests first, including pasted conversations, transcript files, exported AI sessions, colleague chats, old agent handoffs, or conversation summaries; promote selected digest items into requirements, bugs, Flow Records, or dashboard only after explicit user confirmation.
---

# Project Session Extract

## Purpose

Extract recallable project context from historical AI or team chat sessions, then let the user decide what should be saved as a Session Digest and what, if anything, should later be promoted into the project lifecycle.

This skill does not import raw chat by default. It creates a concise candidate Session Digest first, filters noise and sensitive content, and writes only the user-confirmed digest. Requirements, bugs, Flow Records, dashboard state, scope, and project truth are not updated by default.

## Core Model

Use a two-layer model:

```text
historical chat/session
-> Session Digest
-> user restores context
-> selected digest items
-> Lifecycle Promotion when explicitly confirmed
```

Layer 1, Session Digest:

- restores context for later conversations
- may contain mixed requirements, bugs, design notes, risks, tooling notes, and ordinary discussion
- does not update project truth, scope, Flow Records, or dashboard
- is the default output of this skill

Layer 2, Lifecycle Promotion:

- turns selected digest items into requirement, bug, design, working-context, execution plan, verification, handoff, Flow Record, or dashboard evidence
- requires explicit user confirmation
- should route to `project-develop`, `project-fix`, `project-finish`, or `project-review` as appropriate

## When to Use

Use when the user asks to:

- extract, summarize, distill, or import a historical session, old chat, transcript, conversation, AI session, colleague AI discussion, or agent handoff
- save previous session context into project `.llm-wiki` for later recall
- recover prior requirement discussion, design decisions, execution plans, bug analysis, verification notes, risks, or open questions from chat history
- preview useful context from a pasted session before importing it
- decide whether selected historical conversation content should later be promoted into a requirement, bug, module, working-context page, or Flow Record

Example triggers:

- "把之前的 session 总结一下导入 wiki"
- "从这段历史聊天里提取后续可召回的上下文"
- "同事之前和 AI 聊了很多，帮我沉淀到 llm-wiki"
- "我不想重新开 session，想把旧会话的好内容内化"
- "把这个 conversation / transcript / chat history 提纯成上下文摘要"

## When Not to Use

- Do not use for ordinary PRDs, design docs, Markdown, PDF, Word, URLs, logs, meeting notes, or customer feedback; route those to `project-ingest`.
- Do not use for read-only project wiki questions unless the user wants to import or extract historical session context; route those to `project-query`.
- Do not start implementation from this skill. After confirmed lifecycle promotion, route feature work to `project-develop` and bug work to `project-fix`.
- Do not archive full raw transcripts unless the user explicitly asks and sensitivity has been checked.

## Owned Gates

- Context Recovery Gate
- Session Import Gate
- Finish Sync Gate when writing a confirmed Session Digest

## Initialization Gate

Run after identifying the requested mode and before reading project Wiki state or writing a Session Digest.

- `wiki_required_for: save-context-digest-or-promote-to-lifecycle`
- `allowed_without_wiki: brief-candidates-or-draft-context-digest`
- `on_missing_wiki: route project-init`
- `pending_primary_stage: project-session-extract`
- Preserve the user's historical-session request and selected candidate items as `pending_intent`.
- If `<project_root>/.llm-wiki/` is absent and the mode is `save-context-digest` or `promote-to-lifecycle`, stop and return a Context Handoff to `project-init`.
- Do not create a partial `.llm-wiki/`, `session-digests/` directory, requirement, bug, Flow Record, or dashboard state as a substitute for initialization.

On the missing-wiki write branch, emit this minimal handoff:

```text
bootstrap_handoff:
  project_root: <resolved project root>
  pending_intent: <preserved session request and selected candidates>
  pending_primary_stage: project-session-extract
  requested_stage_or_bridge: project-init
  bootstrap_mode: automatic-minimal
  current_gate: Initialization Gate
```

## Without Wiki Preview Boundary

When `.llm-wiki/` is absent, `brief-candidates` and `draft-context-digest` may continue as ephemeral previews. These modes:

- must not write files
- must not claim a Session Digest was imported
- must not perform duplicate detection against unavailable Wiki state
- must preserve the candidate selection so a later `save-context-digest` request can bootstrap through `project-init` without repeating the extraction

## Required Shared References

Read these role-level references as needed:

- `../references/session-digest.md`
- `../references/north-star.md`
- `../references/llm-wiki-mvp.md`
- `../references/flow-record.md`
- `../references/lifecycle-router.md`
- `../references/scoped-working-context.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root. If no shared `references/` directory is available and the user wants to write `.llm-wiki`, continue in degraded mode using the minimum rules in this skill; report the missing deep references and write only confirmed, conservative Session Digest content.

Reference availability policy:

- Shared references are deep references, not startup requirements.
- Do not stop solely because `../references/` is missing.
- In degraded mode, still produce a candidate Session Digest preview and ask for confirmation before writes.
- Do not create or update requirement, bug, module, Flow Record, or dashboard state from session content unless the relationship is clear and confirmed.

## Required First Check

1. Identify the input source: pasted chat, transcript file, exported JSON, handoff, summary, or unknown.
2. Classify sensitivity: `normal`, `cautious`, or `sensitive`.
3. Decide whether the user asked for `brief-candidates`, `draft-context-digest`, `save-context-digest`, or `promote-to-lifecycle`.
4. Resolve `project_root` and `.llm-wiki` when project Wiki access or import is requested.
5. Run the Initialization Gate before Wiki access or writes; use the Without Wiki Preview Boundary only for the two preview modes.
6. Read only the smallest relevant wiki context needed for recall and duplicate avoidance.
7. Do not force matching to existing requirements, bugs, modules, or Flow Records unless promotion is requested.
8. Never write project truth from historical session memory without user confirmation.

## Core Process

Read as needed:

- `../references/session-digest.md`
- `../references/flow-record.md`
- `.llm-wiki/README.md`
- `.llm-wiki/session-digests/`
- `.llm-wiki/log.md`
- `.llm-wiki/requirements/`, `.llm-wiki/bugs/`, `.llm-wiki/modules/index.md`, and `.llm-wiki/artifacts/index.md` only when promotion or duplicate detection needs them

Workflow:

1. Resolve project root and `.llm-wiki`.
2. Identify session source and normalize source metadata without storing personal absolute paths in durable wiki pages.
3. Classify sensitivity and ask before deep-reading large, binary, remote, or sensitive-looking input.
4. Read minimal wiki indexes only to avoid duplicates and recover broad project context.
5. Produce a brief candidate list first:
   - `recommended`: likely useful for future context recovery
   - `optional`: possibly useful but noisy or indirect
   - `do-not-import`: raw noise, secrets, outdated attempts, or unrelated content
6. Let the user choose candidate items.
7. Draft a Session Digest Markdown preview from the selected items.
8. Ask for confirmation on the Markdown preview before writing.
9. After confirmation, write `.llm-wiki/session-digests/<session_digest_id>.md`.
10. Do not update requirement, bug, module, working-context, Flow Record, artifact registry, log, or dashboard unless the user explicitly asks for Lifecycle Promotion.
11. If promotion is requested, map selected digest items to lifecycle targets and ask for confirmation before writing those target pages.
12. Report imported digest, skipped items, unresolved context, and possible next promotion routes.

## Import Rules

- Store confirmed Session Digests under `.llm-wiki/session-digests/`.
- Do not store full raw transcripts by default.
- Digest items may be mixed and messy; use light headings to aid reading, not rigid maintenance types.
- Candidate items may be saved in the digest, but must not update requirement, bug, module, Flow Record, dashboard, or scope without a separate promotion confirmation.
- Conflict items must be marked and reported; do not silently overwrite newer wiki or code evidence.
- If the session mentions a real PRD, document, URL, log, or meeting note, record it as a source candidate and recommend `project-ingest` when needed.
- Refresh dashboard only when the user explicitly confirms Lifecycle Promotion that changes visible Flow Record state, document evidence, risk, blocker, or next action.

## Authority Order

Use this order when historical session content conflicts with current evidence:

```text
current source code and runtime evidence
-> current user confirmation
-> current .llm-wiki requirement/bug/module pages
-> historical session statements
-> agent inference
```

## Session Digest Template

The written digest must include:

- digest id
- source type and source label
- session date when known
- extracted date
- import status
- import type: `recall-context`
- project truth update: `no` by default
- scope update: `no` by default
- Flow Record update: `no` by default
- sensitivity
- one-sentence summary
- what this context is about
- key points for later context recovery
- useful requirement/design/bug/risk/tooling clues when present
- involved files, modules, APIs, commands, or artifacts when useful
- uncertain or needs reconfirmation
- not-imported content
- promotion candidates
- import record

Default template:

```markdown
# Session Digest: <title>

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

## Output Format

For the first preview, keep it brief:

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

For Markdown draft preview:

```text
下面是拟写入的 Session Digest 草稿。请确认是否写入 .llm-wiki/session-digests/<id>.md。
<markdown draft>
```

For completed import:

```text
Digest:
Import type: recall-context
Project truth updated: no
Scope updated: no
Flow Record updated: no
Updated files:
Not imported:
Promotion candidates:
Next:
```

## Context Handoff

When called by the root router, accept:

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

For this skill, `lifecycle_session` may be `none` until the user confirms promoting digest content into a requirement, bug, or Flow Record.

## Return Handoff

Return:

```markdown
## Return Handoff

- stage_or_bridge_used: project-session-extract
- result_summary:
- context_digest:
- imported_digest_items:
- optional_digest_items:
- conflicts:
- promotion_candidates:
- linked_flow_records:
- updated_files:
- verification_notes:
- lifecycle_updates_needed:
- next_gate:
```

## Boundaries

- Do not modify production code.
- Do not create requirements, bugs, or Flow Records from ambiguous session content without confirmation.
- Do not promote candidate digest items to project truth.
- Do not treat Session Digest import as a scope update, requirement update, bug update, Flow Record update, dashboard update, or verification update.
- Do not force mixed historical context into rigid types before the user has recovered context and selected what matters.
- Do not expose or store sensitive raw content.
- Do not claim work is planned, implemented, tested, or archived only because an old session discussed it.
