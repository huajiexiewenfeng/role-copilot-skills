# Tool Bridge

Read `north-star.md` first when changing this bridge.

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
| Superpowers-style skills | brainstorming, planning, TDD, debugging, execution, verification, review | Use after Context Recovery Gate and the relevant Work Definition or Scope Lock checks. See `superpowers-bridge.md`. |
| OpenSpec-style mechanism | requirement discussion, change spec, acceptance criteria, implementation plan | Use the lightweight Change Brief mechanism in `change-brief.md`; do not require OpenSpec tooling. Store concise summaries in requirement or working-context pages. |
| codegraph / codeGraphify | generated code graph, module dependency insight, impact navigation, or ambiguous cross-module scope | Optional enhancement. Detect existing graph context during init, use or suggest during develop/fix when scope is unclear, and verify graph-derived assumptions during review. Do not require generation. |
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

For the internalized MVP mechanism, use `change-brief.md`.

OpenSpec-style handoff is a field mapping into the project lifecycle, not a separate OpenSpec lifecycle. Do not create `openspec/changes/` unless the repository already uses OpenSpec and the user asks to operate that toolchain.

Map the fields as follows:

| OpenSpec-style field | Project lifecycle target |
|---|---|
| `Change` | Change Brief title, `change_id` / `flow_id`, and requirement summary |
| `Why` | Change Brief background / problem statement |
| `Acceptance criteria` | Change Brief acceptance criteria and Flow Record design evidence |
| `Active sources` | Change Brief source links and artifact registry entries |
| `Active scopes` | active scope in Change Brief and working-context |
| `Out of scope` | excluded scope / non-goals |
| `Plan` | execution plan or working-context plan linked to the same `flow_id` |
| `Risks` | risk notes for review and handoff |
| `Verification` | verification evidence and Flow Record testing step |

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

Final continuation or archive notes still belong under `.llm-wiki/handoff/`; the OpenSpec-style handoff above is the requirement/change summary that feeds Change Brief, Flow Record, and working-context.

## codegraph Rule

If graph context exists, use it as read-only supporting context to understand modules, dependencies, and likely impact. Do not let graph output override source code, tests, build files, or runtime evidence.

## Non-Goals

- Do not rebuild Superpowers inside project skills.
- Do not bridge project-coding-skills as an external runtime dependency.
- Do not require OpenSpec tooling.
- Do not require codegraph generation.
- Do not copy an entire Obsidian vault workflow.
- Do not make `.llm-wiki` a large documentation warehouse.
