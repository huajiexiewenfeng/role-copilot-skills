---
name: project-develop-copilot
description: Use when starting, ingesting, developing, fixing, finishing, or reviewing project work with project-local context, LLM Wiki, scoped modules, legacy docs/ai-coding migration, requirements, bugs, or multi-service changes.
---

# Project Develop Copilot

## Purpose

Coordinate project development work through one lifecycle entry point.

This skill belongs to the Project Agent Copilot role group. It does not replace source code, PRDs, issues, design docs, Superpowers, OpenSpec, CodeGraph, or project scripts. It reads project-local facts, builds a scoped working context, maintains a lightweight `.llm-wiki`, and hands off to planning, debugging, implementation, or review workflows at the right time.

## Source Of Truth

Use this authority order:

1. User's current request and explicit decisions.
2. Source code, tests, configuration, build files, and runtime evidence.
3. Original source materials such as PRD, issue, design doc, meeting notes, logs, PDF, Word, or Markdown.
4. `.llm-wiki` index and summaries.
5. Legacy `docs/ai-coding` or generated AI docs.

When sources conflict, name the conflict and prefer the highest authority source. Do not silently merge incompatible facts.

## Session Context

Maintain project work context inside the current conversation/session.

Track:

- `project_root`
- `entry`: init, ingest, develop, fix, finish, or review
- `active_change_id`
- `active_sources`
- `candidate_sources`
- `active_scopes`
- `read_only_scopes`
- `excluded_scopes`
- `legacy_context_found`
- `last_verification`
- `wiki_updates`

Only reuse context within the same project root. When the user changes project root, clear the session context and resolve the new project from scratch.

## Entry Routing

Infer the entry if the user does not name it:

| User intent | Entry |
|---|---|
| initialize project context, adopt repo, migrate old context | `project init` |
| add PRD, link, PDF, Word, Markdown, log, meeting note, feedback | `project ingest` |
| build a new feature or requirement | `project develop` |
| diagnose or fix a bug, error, regression, failed test, incident | `project fix` |
| complete work, sync docs, prepare handoff | `project finish` |
| inspect diff, check consistency, review risk | `project review` |

## Core Workflow

Always start by resolving `project_root`.

Use the user-provided path when present. Otherwise use the current working directory if it looks like a project root. If multiple roots are plausible, ask one concise question before writing files.

### project init

Read `references/lifecycle-mvp.md`, `references/llm-wiki-mvp.md`, and `references/legacy-ai-coding-migration.md`.

Steps:

1. Resolve `project_root`.
2. Inspect top-level folders, build files, `.git`, `docs/`, existing `.llm-wiki/`, and legacy `docs/ai-coding/`.
3. Create missing `.llm-wiki` directories and starter files.
4. Create or update `.llm-wiki/modules/index.md` with discovered modules and statuses.
5. If legacy `docs/ai-coding/` exists, summarize it as legacy migration input without deleting or rewriting it.
6. Write `.llm-wiki/log.md` entry describing what was initialized or refreshed.
7. Report created files, discovered modules, legacy context, and open questions.

### project ingest

Read `references/ingest-mvp.md`, `references/llm-wiki-mvp.md`, and `references/templates.md`.

Steps:

1. Resolve source path, URL, or pasted material.
2. Classify source type and sensitivity.
3. Ask before deep-reading binary, large, or sensitive-looking material.
4. Create or update `.llm-wiki/ingest/index.md`.
5. Create a source proxy page in `.llm-wiki/sources/`.
6. Link to requirement, bug, module, or open question when clear.
7. Report source proxy path, ingest status, and suggested next action.

### project develop

Read `references/develop-fix-mvp.md`, `references/scoped-working-context.md`, and `references/templates.md`.

Steps:

1. Run Context Enrichment Gate before brainstorming or planning.
2. Discover unindexed source docs in configured source directories.
3. Select active, candidate, and excluded sources.
4. Select active, read-only, and excluded code scopes.
5. Produce a context summary with facts, assumptions, gaps, and questions.
6. If context is sufficient, use brainstorming or planning skills as appropriate.
7. Create or update `.llm-wiki/requirements/<change-id>.md`.
8. Do not modify production code until the user confirms implementation or asks to proceed.

### project fix

Read `references/develop-fix-mvp.md`, `references/scoped-working-context.md`, and `references/templates.md`.

Steps:

1. Capture or ingest the bug source.
2. Run Context Enrichment Gate.
3. Summarize observed behavior, expected behavior, affected scope, evidence, and recent changes.
4. Reproduce the issue or state why reproduction is not currently possible.
5. Diagnose before changing code.
6. Fix only active scopes unless escalation is justified.
7. Verify the fix.
8. Update `.llm-wiki/bugs/<bug-id>.md` after verification.

### project finish

Read `references/finish-mvp.md`, `references/llm-wiki-mvp.md`, and `references/templates.md`.

Steps:

1. Confirm what verification was run.
2. Summarize actual code and behavior changes.
3. Update only affected `.llm-wiki` pages.
4. Record remaining gaps and skipped updates.
5. Report verification evidence and wiki pages updated.

### project review

Use a code-review stance:

1. Inspect changed files and related `.llm-wiki` entries.
2. Check behavior risks, missing tests, scope drift, and stale context.
3. Report findings first, ordered by severity.
4. Include open questions and residual risk.

## Defaults

- Default `.llm-wiki` location: `<project_root>/.llm-wiki`.
- Default source directories: `docs/inbox`, `docs/prd`, `docs/design`, `docs/meeting`, `docs/feedback`, `requirements`, `product`, `docs`.
- Default Markdown handling: summary ingest.
- Default PDF/Word handling: path index first, deep read after confirmation.
- Default monorepo handling: discover all top-level modules, activate only selected or clearly relevant scopes.
- Default legacy handling: treat `docs/ai-coding` as read-only migration source.

## Minimal Questions

Ask only when needed:

- Project root is ambiguous.
- Source path or URL is missing.
- Binary, large, or sensitive-looking source requires deep reading.
- Multiple scopes could be active and choosing wrong would affect implementation.
- User asks to implement before scope or acceptance criteria are clear.

Do not ask the user to manually maintain `.llm-wiki`; update it as part of the workflow.

## Safety

- Do not delete, move, or rewrite original source documents.
- Do not delete or rewrite legacy `docs/ai-coding`.
- Do not copy secrets, tokens, credentials, internal endpoints, customer data, or production logs into `.llm-wiki`.
- Do not pull unrelated services into active context by default.
- Do not modify code during context recovery or requirement discussion.
- If verification cannot run, state why and record residual risk.

## Output Formats

For context recovery, report:

```text
Project root:
Entry:
Active sources:
Candidate sources:
Active scopes:
Read-only scopes:
Excluded scopes:
Known facts:
Assumptions:
Gaps / questions:
Recommended next step:
```

For finish, report:

```text
Implementation summary:
Verification:
Wiki updates:
Remaining gaps:
Next action:
```
