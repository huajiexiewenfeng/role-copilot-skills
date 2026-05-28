# Project Agent Copilot

Role-focused skills for project engineering workflows such as development, PRD handling, UI implementation, review, testing, and release coordination.

English | [简体中文](./README.zh.md)

## What Is This?

Project Agent Copilot is the project engineering role group in Role Copilot Skills.

It is designed for teams that already have source code, project documents, development conventions, and recurring engineering workflows. The Copilot does not replace those systems. It helps the agent recover project context, keep source material discoverable, work within scoped modules, and sync useful knowledge back into a lightweight project LLM Wiki.

This role group is intentionally split into domain skills. `project-develop-copilot` is the first domain skill; future skills may focus on PRD, UI, review, testing, release, or refactoring workflows.

## Current Skills

| Skill | Use When |
|---|---|
| `project-develop-copilot` | Coordinate project development lifecycle work: init, ingest, develop, fix, finish, and review with project-local context and LLM Wiki. |

Planned domain skills:

- `project-prd-copilot`
- `project-ui-copilot`
- `project-review-copilot`
- `project-test-copilot`
- `project-release-copilot`

## Install

Install the development skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot
```

For local development from the repository root:

```bash
npx skills add .
```

## Typical Workflow

```text
User request or source material
-> project-develop-copilot
-> resolve project root
-> discover project sources and legacy context
-> build scoped working context
-> discuss, plan, fix, or implement
-> verify the change
-> sync useful knowledge to .llm-wiki
```

## Context Model

Project Agent Copilot uses a lightweight project LLM Wiki as the shared context layer:

```text
.llm-wiki/
  index.md
  log.md
  AGENTS.md
  ingest/
  sources/
  requirements/
  bugs/
  modules/
```

The wiki is not a replacement for source files, PRDs, issues, design docs, tests, or code. It is an index and summary layer that records where important material is, what it means, which module or requirement it relates to, and what gaps remain.

Legacy `docs/ai-coding/` directories are treated as migration sources. New project context should be written to `.llm-wiki` rather than continuing to grow the old directory.

## Safety And Boundaries

- Source code, tests, configuration, build files, and user decisions are the source of truth.
- `.llm-wiki` should store indexes, summaries, relationships, status, and gaps, not long original content.
- Do not pull every service in a monorepo into context by default.
- Use scoped working context to separate active, candidate, read-only, and excluded modules.
- Do not update legacy `docs/ai-coding/` unless explicitly asked.
- Do not modify code during context recovery or requirement discussion unless the user confirms implementation.

## Examples

```text
Use project init for this repository and migrate legacy docs/ai-coding into .llm-wiki.
```

```text
Use project ingest for docs/prd/new-payment-flow.md.
```

```text
Use project develop for the payment callback requirement. It should only touch order-service and payment-service.
```

```text
Use project fix with this log file and diagnose the suspected notification-service bug.
```
