# Tool Bridge

Project Develop Copilot is an orchestration layer for project development. It should bridge top-level skills and tools instead of reimplementing them.

It is also the upgraded successor of the older project-coding-skills approach. Proven project-coding-skills ideas should be internalized into these project skills, not bridged as an external runtime dependency.

## Goals

1. Bridge mature top-level skills and tools into a project lifecycle.
2. Internalize a project-level LLM Wiki as the shared context memory.

## Bridge Rule

Run project context recovery first:

1. Resolve project root.
2. Recover `.llm-wiki` indexes and summaries.
3. Select active, read-only, candidate, and excluded scopes.
4. Create or reuse working-context when the task is cross-module.
5. Hand the scoped context to the external skill or tool.
6. Sync decisions, status, gaps, and verified outcomes back to `.llm-wiki`.

External tools must not bypass scoped context or write long transcripts into `.llm-wiki`.

## Supported Bridges

| Bridge | Use | Rule |
|---|---|---|
| Superpowers-style skills | brainstorming, planning, TDD, debugging, execution, verification, review | Use after Context Enrichment Gate. See `superpowers-bridge.md`. |
| OpenSpec-style mechanism | requirement discussion, change spec, acceptance criteria, implementation plan | Use the mechanism and concepts when useful; do not require OpenSpec tooling. Store concise summaries in requirement or working-context pages. |
| codegraph / codeGraphify | existing generated code graph or module dependency insight | Use when `.codegraph/`, generated graph files, or an installed graph tool already exists. Do not force generation during MVP. |
| Obsidian LLM Wiki ideas | index, source proxy, summaries, links, gaps, maintenance log | Internalize the project subset as `.llm-wiki`; do not depend on a separate Obsidian workflow. |

## Internalized Predecessor

Do not bridge project-coding-skills as an external skill. Treat it as the predecessor and design source for:

- project init and refresh
- project-local coding context
- feature development context recovery
- bug-fix context recovery
- legacy `docs/ai-coding` migration
- module and microservice scope isolation

When a project still has `docs/ai-coding/`, migrate useful summaries into `.llm-wiki` during `project-init`; do not keep growing the legacy directory.

## OpenSpec-Style Handoff

When using an OpenSpec-style mechanism, keep the handoff small:

```text
Change:
Why:
Acceptance criteria:
Active sources:
Active scopes:
Out of scope:
Plan:
Risks:
Verification:
```

## codegraph Rule

If graph context exists, use it as read-only supporting context to understand modules, dependencies, and likely impact. Do not let graph output override source code, tests, build files, or runtime evidence.

## Non-Goals

- Do not rebuild Superpowers inside project skills.
- Do not bridge project-coding-skills as an external runtime dependency.
- Do not require OpenSpec tooling.
- Do not require codegraph generation.
- Do not copy an entire Obsidian vault workflow.
- Do not make `.llm-wiki` a large documentation warehouse.
