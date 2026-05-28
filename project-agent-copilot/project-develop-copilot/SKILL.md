---
name: project-develop-copilot
description: Use when starting, ingesting, developing, fixing, finishing, or reviewing project work with project-local context, LLM Wiki, scoped modules, legacy docs/ai-coding migration, requirements, bugs, or multi-service changes.
---

# Project Develop Copilot

Project Develop Copilot is the project development lifecycle entry point.

It is not another large skills system. It coordinates proven practices such as Superpowers, OpenSpec concepts, LLM Wiki, CodeGraph, and legacy project coding context so people, agents, documents, code, and project knowledge work around the same change.

This skill is the first domain skill under the Project Agent Copilot role group. It does not own every project engineering workflow; future domain skills may cover PRD, UI, review, testing, and release workflows.

## Core Rules

- Keep one user-facing entry point for project development work.
- Maintain project `.llm-wiki` as an index, summary, relationship, status, and gap layer.
- Do not treat `.llm-wiki` as the source of truth; source files, code, tests, configuration, and user decisions win.
- Do not copy Superpowers workflows. Invoke or follow them when available.
- Do not require OpenSpec CLI, CodeGraph, or old `docs/ai-coding`.
- Prefer MVP flow over advanced automation.

## Entry Routing

When the user asks for:

- `project init`: read `references/lifecycle-mvp.md`, `references/llm-wiki-mvp.md`, and `references/legacy-ai-coding-migration.md`.
- `project ingest`: read `references/ingest-mvp.md`, `references/llm-wiki-mvp.md`, and `references/templates.md`.
- `project develop`: read `references/develop-fix-mvp.md`, `references/scoped-working-context.md`, and `references/templates.md`.
- `project fix`: read `references/develop-fix-mvp.md`, `references/scoped-working-context.md`, and `references/templates.md`.
- `project finish`: read `references/finish-mvp.md`, `references/llm-wiki-mvp.md`, and `references/templates.md`.
- `project review`: run a review stance over code, tests, requirements, and wiki consistency.

If the user does not name an entry but asks to work on a project requirement, bug, PRD, source document, or code change, infer the closest entry.

## Required Gate Order

For `project develop` and `project fix`:

1. Resolve project root.
2. Run context discovery.
3. Build scoped working context.
4. Read only active context.
5. Produce context summary, gaps, and questions.
6. Then use brainstorming, planning, debugging, or implementation skills as needed.

For `project finish`:

1. Confirm implementation verification.
2. Summarize actual changes.
3. Update `.llm-wiki`.
4. Report remaining gaps.
