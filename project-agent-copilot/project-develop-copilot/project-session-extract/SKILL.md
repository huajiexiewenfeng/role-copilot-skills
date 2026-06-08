---
name: project-session-extract
description: Use when extracting, summarizing, distilling, reviewing, or importing historical chat/session context into a project .llm-wiki, including pasted conversations, transcript files, exported AI sessions, colleague chats, old agent handoffs, or conversation summaries.
---

# Project Session Extract

## Purpose

Extract durable project knowledge from historical AI or team chat sessions, then let the user confirm what should be imported into `.llm-wiki`.

This skill does not import raw chat by default. It creates a candidate Session Digest first, filters noise and sensitive content, maps useful context to project wiki targets, and writes only confirmed knowledge.

## When to Use

Use when the user asks to:

- extract, summarize, distill, or import a historical session, old chat, transcript, conversation, AI session, colleague AI discussion, or agent handoff
- turn previous session context into project `.llm-wiki` knowledge
- recover prior requirement discussion, design decisions, execution plans, bug analysis, verification notes, risks, or open questions from chat history
- decide whether historical conversation content should link to an existing requirement, bug, module, working-context page, or Flow Record
- preview useful project knowledge from a pasted session before importing it

Example triggers:

- "把之前的 session 总结一下导入 wiki"
- "从这段历史聊天里提取有用的项目上下文"
- "同事之前和 AI 聊了很多，帮我沉淀到 llm-wiki"
- "我不想开新 session，但想把旧会话的好内容内化"
- "把这个 conversation / transcript / chat history 提纯成项目知识"

## When Not to Use

- Do not use for ordinary PRDs, design docs, Markdown, PDF, Word, URLs, logs, meeting notes, or customer feedback; route those to `project-ingest`.
- Do not use for read-only project wiki questions unless the user wants to import or extract historical session context; route those to `project-query`.
- Do not start implementation from this skill. After confirmed import, route feature work to `project-develop` and bug work to `project-fix`.
- Do not archive full raw transcripts unless the user explicitly asks and sensitivity has been checked.

## Owned Gates

- Context Discovery Gate
- Session Source Gate
- Sensitivity Gate
- Candidate Digest Gate
- Import Confirmation Gate
- Knowledge Sync Gate after user confirmation
- Flow Record Mapping Gate when a digest may link to a requirement or bug

## Required Shared References

Read these role-level references:

- `../references/session-digest.md`
- `../references/north-star.md`
- `../references/llm-wiki-mvp.md`
- `../references/flow-record.md`
- `../references/lifecycle-router.md`
- `../references/scoped-working-context.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root. If no shared `references/` directory is available and the user wants to write `.llm-wiki`, stop and tell the user the child skill install is incomplete; install the top-level `project-develop-copilot` package or restore the shared `references/` directory before writing project wiki state.

## Required First Check

1. Resolve `project_root` and `.llm-wiki` when import is requested.
2. If `.llm-wiki` does not exist and the user wants to import, route to `project-init` first.
3. Identify the input source: pasted chat, transcript file, exported JSON, handoff, summary, or unknown.
4. Classify sensitivity: `normal`, `cautious`, or `sensitive`.
5. Decide whether the user asked for `preview-only`, `save-candidate`, or `import-after-confirmation`.
6. Read the smallest relevant wiki context before matching existing requirements, bugs, modules, or Flow Records.
7. Never write project truth from historical session memory without user confirmation.

## Core Process

Read as needed:

- `../references/session-digest.md`
- `../references/flow-record.md`
- `.llm-wiki/README.md`
- `.llm-wiki/requirements/`
- `.llm-wiki/bugs/`
- `.llm-wiki/modules/index.md`
- `.llm-wiki/artifacts/index.md`
- `.llm-wiki/log.md`
- `.llm-wiki/session-digests/`

Workflow:

1. Resolve project root and `.llm-wiki`.
2. Identify session source and normalize source metadata without storing personal absolute paths in durable wiki pages.
3. Classify sensitivity and ask before deep-reading large, binary, remote, or sensitive-looking input.
4. Read minimal wiki indexes to find related requirements, bugs, modules, working-context pages, artifacts, and Flow Records.
5. Extract candidate project knowledge:
   - requirements and acceptance criteria
   - design decisions and tradeoffs
   - implementation constraints and plan candidates
   - bug symptoms, root-cause evidence, failed attempts, and fix candidates
   - module, service, API, topic, DTO, or code-path context
   - verification evidence
   - risks, open questions, and source candidates
6. Classify extracted items as `confirmed`, `candidate`, `conflict`, `stale`, or `do-not-import`.
7. Match existing requirement, bug, module, working-context, and Flow Record evidence.
8. Produce a candidate Session Digest preview before writing `.llm-wiki`.
9. Ask one concise confirmation question before importing.
10. After confirmation, write `.llm-wiki/session-digests/<session_digest_id>.md`.
11. Update related requirement, bug, module, working-context, artifact registry, log, or dashboard only when the user confirmed the relationship and the evidence supports it.
12. Report imported items, skipped items, conflicts, updated files, and next route.

## Import Rules

- Store confirmed distilled summaries under `.llm-wiki/session-digests/`.
- Do not store full raw transcripts by default.
- Candidate items may be saved in the digest, but must not update requirement or bug truth without confirmation.
- Conflict items must be marked and reported; do not silently overwrite newer wiki or code evidence.
- If the session mentions a real PRD, document, URL, log, or meeting note, record it as a source candidate and recommend `project-ingest` when needed.
- Refresh dashboard only when confirmed imported evidence changes visible Flow Record state, document evidence, risk, blocker, or next action.

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

Use the template from `references/session-digest.md`. The written digest must include:

- digest id
- source type and source label
- session date when known
- extracted date
- import status
- related `flow_id` or candidate relation
- related scope
- sensitivity
- one-sentence summary
- importable content
- not-imported content
- requirement/design candidates
- bug/fix candidates
- scope context
- design decisions
- source candidates
- verification evidence
- risks and open questions
- import plan and import record

## Output Format

For preview:

```text
我从这段历史 session 中提取到以下候选项目知识：

可以导入：
1. ...
2. ...

建议关联：
- flow_id:
- requirement:
- module:

不建议导入：
- ...

需要确认：
1. ...

是否确认写入 .llm-wiki/session-digests/？
```

For completed import:

```text
已导入历史 session 提纯结果。

Digest:
Linked flow_id:
Updated files:
Dashboard:
Not imported:
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

For this skill, `lifecycle_session` may be `none` until the user confirms importing content into a requirement, bug, or Flow Record.

## Return Handoff

Return:

```markdown
## Return Handoff

- stage_or_bridge_used: project-session-extract
- result_summary:
- session_digest:
- imported_items:
- candidate_items:
- conflicts:
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
- Do not expose or store sensitive raw content.
- Do not claim work is planned, implemented, tested, or archived only because an old session discussed it.
