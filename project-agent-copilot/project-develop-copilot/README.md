# Project Develop Copilot

Project Develop Copilot is a skill collection for real project development work. It combines project LLM Wiki maintenance, scoped context recovery, requirement development, bug fixing, finish sync, and review into one coherent development lifecycle.

English | [Simplified Chinese](./README.zh.md)

## Skills

| Skill | Use When |
|---|---|
| `project-init` | Initialize or refresh project-local LLM Wiki, discover modules, and migrate legacy `docs/ai-coding`. |
| `project-ingest` | Ingest PRDs, links, Markdown, PDF, Word, logs, meeting notes, or temporary source material into the project LLM Wiki. |
| `project-develop` | Develop a requirement or feature with scoped project context and requirement summaries. |
| `project-fix` | Diagnose and fix project bugs with scoped context, evidence, verification, and bug summaries. |
| `project-finish` | Finish verified work by syncing actual changes back to LLM Wiki and preparing handoff. |
| `project-review` | Review project changes for code risk, test gaps, scope drift, stale context, and wiki sync. |

## Install

Install one skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot/project-develop
```

For local development from the repository root:

```bash
npx skills add .
```

## Lifecycle

```text
project-init
-> project-ingest
-> project-develop or project-fix
-> project-finish
-> project-review
```

`project-init` and `project-ingest` enrich project context. `project-develop` and `project-fix` consume scoped context for actual work. `project-finish` writes verified outcomes back into the wiki. `project-review` checks code, tests, scope, and context consistency before handoff.

## Context Model

The shared project context layer is `.llm-wiki`:

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

The wiki is an index and summary layer, not a replacement for source files, PRDs, issues, design docs, tests, or code. It records where important material is, what it means, which module or requirement it relates to, and what gaps remain.

Legacy `docs/ai-coding/` directories are migration sources. New project context should be written to `.llm-wiki`.

## Safety

- Source code, tests, configuration, build files, and user decisions are the source of truth.
- `.llm-wiki` stores indexes, summaries, relationships, status, and gaps, not long original content.
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
