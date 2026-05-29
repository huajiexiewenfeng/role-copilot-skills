# Lifecycle MVP

Read `north-star.md` first when changing lifecycle behavior.

Use this reference to run the first usable Project Develop Copilot lifecycle.

## Entries

| Entry | Purpose | Required output |
|---|---|---|
| project init | Initialize project protocol and `.llm-wiki` | wiki skeleton and module registry |
| project ingest | Capture source material | source proxy and ingest index entry |
| project develop | Develop a requirement | context summary, requirement page, plan handoff |
| project fix | Diagnose and fix a bug | bug page, diagnosis, verification |
| project finish | Sync verified work | updated wiki summaries and final report |
| project review | Check consistency | findings and risks |

Project entries own project context. Superpowers-style skills are bridged only after project context recovery. See `superpowers-bridge.md`.

Project Develop Copilot also bridges other top-level skills and tools through the same context-first rule. See `tool-bridge.md`.

## Project Root Resolution

Resolve project root in this order:

1. User-provided project path.
2. Current working directory when it contains `.git`, build files, or project docs.
3. Nearest ancestor containing `.git`.

Project root must be broad enough to include shared docs, build files, Git history, and cross-module context. Working context can later narrow active scopes.

If multiple roots are plausible, ask:

```text
Which project root should I use: <path-a> or <path-b>?
```

## Init Procedure

During `project init`:

1. Inspect:
   - `.git`
   - build files such as `pom.xml`, `package.json`, `settings.gradle`, `build.gradle`, `go.mod`, `Cargo.toml`
   - `docs/`
   - `.llm-wiki/`
   - `docs/ai-coding/`
   - `.codegraph/`
2. Create missing wiki directories:
   - `.llm-wiki/ingest`
   - `.llm-wiki/sources`
   - `.llm-wiki/requirements`
   - `.llm-wiki/bugs`
   - `.llm-wiki/working-context`
   - `.llm-wiki/modules`
3. Create starter files if missing:
   - `.llm-wiki/index.md`
   - `.llm-wiki/log.md`
   - `.llm-wiki/AGENTS.md`
   - `.llm-wiki/ingest/index.md`
   - `.llm-wiki/modules/index.md`
4. Detect top-level modules and services conservatively.
5. Mark only the user-selected or clearly requested scope as `active`; mark others as `discovered` or `reference-only`.
6. If `docs/ai-coding/` exists, run legacy migration summary rules.

## Starter File Content

Use short, useful starter content.

`.llm-wiki/index.md`:

```markdown
# Project LLM Wiki

## Purpose

This wiki is maintained by agents as a project knowledge index. Source code, tests, configuration, build files, and original project documents remain the source of truth.

## Main Indexes

- [[ingest/index]]
- [[modules/index]]

## Current Gaps

- No project sources have been ingested yet.
```

`.llm-wiki/log.md`:

```markdown
# LLM Wiki Log

## <date> | project init

- Initialized project LLM Wiki.
```

`.llm-wiki/AGENTS.md`:

```markdown
# Agent Rules

- Do not store secrets or long original content in this wiki.
- Use source code, tests, configuration, build files, and original documents as truth.
- Store only indexes, summaries, relationships, status, and gaps.
- Keep active work scoped to the current requirement or bug.
```

`.llm-wiki/ingest/index.md`:

```markdown
# Ingest Index

| Source | Type | Wiki Entry | Status | Notes |
|---|---|---|---|---|
```

`.llm-wiki/modules/index.md`:

```markdown
# Modules Index

| Module | Path | Type | Context | Status |
|---|---|---|---|---|
```

## MVP Non-Goals

- Do not build a task management system.
- Do not require CI integration.
- Do not force every service in a monorepo into context.
- Do not deep-read every PRD, PDF, or Word document.
- Do not update legacy `docs/ai-coding` unless explicitly asked.
