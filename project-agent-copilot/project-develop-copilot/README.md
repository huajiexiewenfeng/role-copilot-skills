# Project Develop Copilot

Project Develop Copilot is a skill collection for real project development work. It has two core goals:

1. Bridge top-level skills and tools into one project lifecycle.
2. Internalize a project-level LLM Wiki as the shared context memory.

It combines project LLM Wiki maintenance, scoped context recovery, requirement development, bug fixing, finish sync, and review into one coherent development lifecycle.

It does not replace Superpowers-style skills. It prepares project context, active scopes, and `.llm-wiki` state first, then bridges to brainstorming, planning, TDD, debugging, execution, verification, and review skills inside that controlled context.

It also supports OpenSpec-style requirements, existing codegraph context, and Obsidian LLM Wiki ideas as bridges, not hard dependencies. The older project-coding-skills work is treated as the predecessor whose proven project-development ideas are internalized here. See `references/tool-bridge.md`.

When goals, scope, or implementation choices are unclear, use `references/north-star.md` as the source of alignment.

For current MVP gaps and implementation priority, use `references/capability-gap-audit.md`.

For MVP validation scenarios, use `references/acceptance-cases.md`.

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

Superpowers-style skills are invoked after project context recovery, not before it. See `references/superpowers-bridge.md`.

Other top-level tools follow the same context-first bridge rule. See `references/tool-bridge.md`.

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
  working-context/
  modules/
```

The wiki is the internalized project subset of the LLM Wiki idea: an index and summary layer, not a replacement for source files, PRDs, issues, design docs, tests, or code. It records where important material is, what it means, which module or requirement it relates to, and what gaps remain.

Use `working-context/` only for complex or cross-module work that needs active scopes, read-only scopes, excluded scopes, contracts, escalation, and verification to stay together.

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
