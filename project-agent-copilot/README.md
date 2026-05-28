# Project Agent Copilot

Project Agent Copilot is the project engineering role group in Role Copilot Skills.

It coordinates domain skills for project work such as development, PRD handling, UI implementation, review, testing, and release. Each child directory is an installable skill for one project engineering domain.

## Skills

| Skill | Use When |
|---|---|
| `project-develop-copilot` | Use for project development lifecycle work: init, ingest, develop, fix, finish, and review with project-local context and LLM Wiki. |

## Planned Domain Skills

- `project-prd-copilot`
- `project-ui-copilot`
- `project-review-copilot`
- `project-test-copilot`
- `project-release-copilot`

## Principles

- Project-local source material and code are the source of truth.
- Domain skills should share project context through `.llm-wiki`.
- Do not force one domain skill to own the whole project engineering role.
