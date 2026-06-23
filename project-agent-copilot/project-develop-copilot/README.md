# Project Develop Copilot

Project Develop Copilot is a skill collection for real project development work. It has two core goals:

1. Bridge top-level skills and tools into one project lifecycle.
2. Internalize a project-level LLM Wiki as the shared context memory.

It combines project LLM Wiki maintenance, scoped context recovery, cross-project refs, requirement development, bug fixing, finish sync, and review into one coherent development lifecycle.

It does not replace Superpowers-style skills. It prepares project context, active scopes, and `.llm-wiki` state first, then bridges to brainstorming, planning, TDD, debugging, execution, verification, and review skills inside that controlled context.

It also supports OpenSpec-style requirements, existing codegraph context, and Obsidian LLM Wiki ideas as bridges, not hard dependencies. The older project-coding-skills work is treated as the predecessor whose proven project-development ideas are internalized here. See `references/tool-bridge.md`.

When goals, scope, or implementation choices are unclear, use `references/north-star.md` as the source of alignment.

For the complete lifecycle implementation plan, use `references/full-lifecycle-implementation-plan.zh.md`. For current capability gaps, use `references/capability-gap-audit.md`.

For lifecycle validation scenarios, use `references/acceptance-cases.md`.

For the Chinese internal trial user guide, see `USER-GUIDE.zh.md`.

English | [Simplified Chinese](./README.zh.md)

## Skills

| Skill | Use When |
|---|---|
| `project-develop-copilot` | Route natural project development intent into lightweight answers or the full project lifecycle. |
| `project-query` | Query project `.llm-wiki` to answer what exists in the project, how modules or APIs are called, which cross-project refs point to remote contracts, and which requirements, bugs, source proxies, artifacts, or discussion context relate to a topic without starting implementation. |
| `project-maintain` | Check, audit, repair, and maintain project `.llm-wiki` visibility, Flow Records, cross-project refs, artifact registry entries, dashboard consistency, module backlinks, logs, links, and safety boundaries. |
| `project-base-init` | Initialize or refresh an independent Base Graph repository that coordinates many project-local `.llm-wiki` directories without treating the Base repo as a business project. |
| `project-graph-candidates-scan` | Scan the current project for Project Graph relationship candidates; it writes candidates and scan reports only, not confirmed edges or cross-ref pins. |
| `project-graph-auto-edge` | Resolve candidates through Base Graph and local/remote source evidence into human-reviewable edge proposals. |
| `project-graph-human-edge` | Accept, reject, or manually register Project Graph edges, and maintain `cross-refs/index.md` pins when confirmed edges are written. |
| `project-init` | Initialize or refresh project-local LLM Wiki, discover modules, and migrate legacy `docs/ai-coding`. |
| `project-ingest` | Ingest PRDs, links, Markdown, PDF, Word, logs, meeting notes, or temporary source material into the project LLM Wiki. |
| `project-session-extract` | Distill historical AI/team chat sessions, transcripts, old conversations, or handoffs into recallable Session Digests first; promote selected digest items into lifecycle objects only after explicit confirmation. |
| `project-develop` | Develop a requirement or feature with scoped project context, requirement summaries, and source-verified external dependencies when cross-project contracts affect the change. |
| `project-fix` | Diagnose and fix project bugs with scoped context, cross-project external findings when needed, evidence, verification, and bug summaries. |
| `project-finish` | Finish verified work by syncing actual changes back to LLM Wiki and preparing handoff. |
| `project-review` | Review project changes for code risk, test gaps, scope drift, stale context, and wiki sync. |

## Install

Install the top-level router skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot
```

For local development from the repository root, list all available skills:

```bash
npx skills add . --list
```

Child stage skills can still be installed directly for narrow testing, but the normal user-facing entry is project-develop-copilot.

Install integrity check:

```bash
test -d ~/.codex/skills/project-develop/references || test -d ~/.agents/skills/project-develop/references
```

Child stage skills can use the shared `references/` directory when it is installed next to the skill folder. If a child skill is installed directly without `references/`, it must continue in degraded mode using the minimum rules embedded in that child skill and report the missing deep references.

## Lifecycle

```text
project-develop-copilot
-> lightweight-answer

or

project-develop-copilot
-> project-query / project-maintain / project-base-init / project-init / project-ingest
-> project-develop or project-fix
-> project-finish
-> project-review
```

`project-develop-copilot` is the natural entry router. `project-query` handles read-only project wiki lookup, cross-project lookup, and discussion context. `project-maintain` keeps the project `.llm-wiki` discoverable, structurally consistent, and safe. `project-init` and `project-ingest` enrich project context. `project-develop` and `project-fix` consume scoped context for actual work and record external dependencies/findings when cross-project contracts matter. `project-finish` writes verified outcomes back into the wiki. `project-review` checks code, tests, scope, and context consistency before handoff.

Superpowers-style skills are invoked after project context recovery, not before it. See `references/superpowers-bridge.md`.

Other top-level tools follow the same context-first bridge rule. See `references/tool-bridge.md`.

## Historical Session Extraction

Use `project-session-extract` when a teammate already discussed useful project context with an AI assistant. The copilot first produces a brief candidate list, lets the user choose what to keep, drafts a Session Digest, and writes it only after confirmation.

Session Digests are recall context by default. They do not update requirements, bugs, Flow Records, dashboard, scope, or project truth. Selected digest items enter the lifecycle only through explicit Lifecycle Promotion. Raw transcripts are not copied by default.

## Read-Only Project Query

Use `project-query` when the user wants to discuss the project from its `.llm-wiki` without starting implementation. Typical prompts include:

```text
Based on this project's llm wiki, find the requirements and development notes related to payment callback. Do not develop yet; let's discuss first.
Find the related requirement docs, bug notes, and previous decisions for notification retries.
What does the project wiki say about this module and its current risks?
What APIs or integration points exist for this feature, and how should they be called?
这个项目里面，大疆 API 适配，直播相关的内容有哪些？如何通过 API 调用
```

For "what exists here" or "how do I call this API" questions, `project-query` should recover `.llm-wiki` evidence first, then inspect source code only to verify current endpoints, topics, service behavior, or examples. Do not route these questions directly to implementation, debugging, or review unless the user explicitly asks to change, fix, or assess code.

The expected response is a Project Context Pack:

- Answer
- Relevant requirements, bugs, source proxies, artifacts, and working-context pages
- Evidence vs inference
- Confidence and missing or stale context
- Possible next routes, such as ingesting missing docs, creating a Change Brief, creating a Bug Brief, starting review, or running Lifecycle Quality Review

`project-query` is different from `lightweight-answer`: it actively searches project `.llm-wiki` and assembles evidence. It is also different from full lifecycle work: it stays read-only unless the user explicitly asks to continue into development, fixing, ingest, review, or skill evolution.

## Project Graph And Cross-Project Refs

Project Graph is a `.llm-wiki` evidence lifecycle with three explicit maintenance child skills. `project-init` creates `project-graph/edges.md`, `project-graph/candidates.md`, `project-graph/proposals.md`, `project-graph/scan-report.md`, and pin-only `cross-refs/index.md` for business projects; `project-base-init` creates only the independent Base Graph structure for catalog and overview coordination; `project-query` uses pin -> edge -> candidate/proposal lookup for read-only questions like "which service owns this topic"; `project-develop` records source-verified external dependencies in Change Briefs; `project-fix` records external findings in Bug Briefs; `project-maintain` audits and repairs graph consistency.

Project Graph maintenance skills:

- `project-graph-candidates-scan`: scan the current project and maintain candidates.
- `project-graph-auto-edge`: resolve candidates into proposals through Base Graph and source evidence.
- `project-graph-human-edge`: accept, reject, or manually register confirmed edges and cross-ref pins.

Facts live only in `project-graph/edges.md` after human confirmation. `cross-refs/index.md` is a pin layer that references `edge_id`; local paths live in ignored registry files. Remote project wiki and source are read-only by default.

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
  artifacts/
  cross-refs/
  project-graph/
  dashboard/
  handoff/
  session-digests/
  migration/
  registry.local.json   (gitignored, local paths only)
```

The wiki is the internalized project subset of the LLM Wiki idea: an index and summary layer, not a replacement for source files, PRDs, issues, design docs, tests, or code. It records where important material is, what it means, which module or requirement it relates to, and what gaps remain.

Use `working-context/` only for complex or cross-module work that needs active scopes, read-only scopes, excluded scopes, contracts, escalation, and verification to stay together.

Legacy `docs/ai-coding/` directories are migration sources. New project context should be written to `.llm-wiki`.

## Glossary

| Term | Short meaning | Main file | Similar concept |
|---|---|---|---|
| Change Brief / Bug Brief | Requirement or bug lifecycle page maintained by the agent. | `requirements/`, `bugs/`, `references/change-brief.md`, `references/bug-brief.md` | mini-RFC / bug report |
| Flow Record | Evidence-backed lifecycle status rows for one deliverable. | `references/flow-record.md` | lifecycle status + evidence index |
| Session Digest | Confirmed summary of historical chat/session context; recall context by default. | `session-digests/`, `references/session-digest.md` | conversation digest |
| Scoped Working Context | Active/read-only/candidate/excluded context for complex or cross-module work. | `working-context/`, `references/scoped-working-context.md` | monorepo sparse context |
| Lifecycle Gate | Lightweight checkpoint before a risky lifecycle transition. | `references/lifecycle-gates.md` | readiness checklist |
| Project Graph edge | Verified or draft cross-project relationship fact. | `project-graph/edges.md`, `references/project-graph.md` | service dependency edge |
| candidate | Suspected cross-project relationship that is not yet a fact. | `project-graph/candidates.md` | discovery finding |
| proposal | Human-review queue row generated from a candidate before it becomes a confirmed edge. | `project-graph/proposals.md` | auto-edge review item |
| pin | Team navigation bookmark that references an `edge_id`; it stores no facts. | `cross-refs/index.md` | curated link |
| fingerprint | Stable de-duplication key for graph edges or candidates. | `references/project-graph.md` | relationship identity key |
| verification_status / derived staleness | Verification level stored on an edge; freshness derived from `last_verified`. | `project-graph/edges.md`, `references/cross-project-refs.md` | contract confidence / freshness |
| registry.local.json | Local-only project path resolver; must be gitignored. | `.llm-wiki/registry.local.json` | local workspace mapping |
| cross-project boundary check | Read-only remote evidence check under Context Recovery / External Bridge rules. | `references/cross-project-refs.md` | remote evidence access guard |
| Base Graph | Optional machine-level registry plus architecture overview/catalog for large cross-service discussions. | `references/base-graph.md` | platform graph overview |

## Project Graph Quick Use

- Ask “这个接口/topic/配置/回调对面是谁” to query pins, edges, candidates, and read-only remote evidence.
- Ask “帮我登记这个跨项目调用” or “确认这个 proposal” to run `project-graph-human-edge`; human edge writes update `edges.md` and upsert `cross-refs/index.md` by default.
- Ask “扫一下未登记上下游” or “做一次 project-graph candidates.md 的扫描” to run `project-graph-candidates-scan`.
- Ask “通过 base-graph 找到对应项目，生成 edge proposal” to run `project-graph-auto-edge`.
- Ask "initialize this Base Graph repository" to run `project-base-init`; use ordinary `project-init` only for business project repositories.
- Base Graph is optional and discovered through `LLM_WIKI_BASE_GRAPH_PATH` or `~/.llm-wiki/base-graph.local.json`.
- Base Graph `registry.local.json` is a local-config exception; business-project sessions may write it after confirmation, but must not write Base tracked files such as `overview.md`, `project-catalog.md`, `decisions/`, or `handoff/`.
- `~/.llm-wiki/registry.json` is legacy read-only compatibility. New implementations should not create or prefer it.

## Safety

- Source code, tests, configuration, build files, and user decisions are the source of truth.
- `.llm-wiki` stores indexes, summaries, relationships, status, and gaps, not long original content.
- Do not pull every service in a monorepo into context by default.
- Use scoped working context to separate active, candidate, read-only, and excluded modules.
- Do not update legacy `docs/ai-coding/` unless explicitly asked.
- Do not modify code during context recovery or requirement discussion unless the user confirms implementation.

## Examples

```text
Based on this project's llm wiki, find the payment callback requirement docs and previous development context. Do not develop yet; let's discuss first.
```

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
