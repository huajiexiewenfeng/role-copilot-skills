# North Star

Read this first when designing, changing, reviewing, or extending Project Develop Copilot. If any implementation choice is unclear, return to this document before adding more rules.

## Mission

Project Develop Copilot is the upgraded successor of project-coding-skills. It internalizes project LLM Wiki and project-coding-skills ideas, then bridges mature top-level skills and tools into one practical project development lifecycle. It exposes a lifecycle router so users can enter naturally from a PRD, bug, log, review request, or resume request without choosing the correct child skill first.

## Core Goals

1. Internalize project-coding-skills as the predecessor:
   - project init and refresh
   - project-local coding context
   - feature development context recovery
   - bug-fix context recovery
   - multi-module and microservice scope isolation
   - legacy `docs/ai-coding` migration
2. Internalize project LLM Wiki:
   - users maintain original materials
   - agents maintain `.llm-wiki`
   - `.llm-wiki` stores indexes, summaries, relationships, status, and gaps
   - `.llm-wiki` is code-aware, local to the project, and tied to lifecycle gates
3. Bridge top-level skills and tools after project context recovery:
   - Superpowers-style brainstorming, planning, TDD, debugging, execution, verification, and review
   - OpenSpec-style requirement discussion, change spec, acceptance criteria, and implementation plan
   - existing codegraph or codeGraphify outputs when present
4. Provide a natural lifecycle router:
   - users face Project Develop Copilot, not isolated child skills
   - every entry is resumable
   - every entry is scoped
   - every entry returns to lifecycle
   - Change Brief, Bug Brief, and working-context pages carry lifecycle state
5. Provide real, installable project workflow skills:
   - `project-init`
   - `project-ingest`
   - `project-develop`
   - `project-fix`
   - `project-finish`
   - `project-review`

## Responsibility Split

Project Develop Copilot owns project context:

- lifecycle routing
- project root resolution
- `.llm-wiki` protocol
- ingest/source proxies
- scoped working context
- working-context pages for complex or cross-module work
- Change Brief and Bug Brief state
- artifact registry
- progress dashboard state when enabled
- finish sync
- review of wiki drift, scope drift, artifact drift, and dashboard drift

External skills and tools own their own expertise:

- Superpowers owns thinking and execution discipline
- OpenSpec-style mechanisms own specification discipline
- codegraph owns graph-derived insight when graph data already exists

External tools receive scoped project context. They do not choose project scope from scratch.

## Lifecycle-First Rule

Every entry follows lifecycle-first rules:

1. Route natural user intent.
2. Resolve project root.
3. Discover new or stale context.
4. Create or resume lifecycle session.
5. Recover `.llm-wiki` indexes and summaries.
6. Identify active sources.
7. Select active, read-only, candidate, and excluded scopes.
8. Create or reuse working-context when the task is cross-module.
9. Bridge to external skills or tools only after context is scoped.
10. Verify, sync knowledge, register artifacts, update dashboard state when enabled, and review drift.

## Non-Goals

- Do not rebuild Superpowers inside project skills.
- Do not bridge project-coding-skills as an external runtime dependency.
- Do not require OpenSpec tooling.
- Do not require codegraph generation.
- Do not copy a full Obsidian vault workflow.
- Do not make `.llm-wiki` a large documentation warehouse.
- Do not deep-read every service or document by default.

## Done Means

For the MVP to be considered complete:

- all six project skills are installable and discoverable
- project init creates a usable `.llm-wiki`
- project ingest captures source material without copying long or sensitive content
- project develop and project fix load only relevant scoped context
- working-context handles complex or cross-module work
- project finish updates wiki only after verification or an explicit limitation
- project review checks code risk, test gaps, scope drift, tool-bridge consistency, wiki drift, artifact drift, and progress dashboard drift when enabled
- users can start from natural intent without manually choosing the correct child skill
- lifecycle sessions keep requirement, bug, scope, plan, verification, and handoff state recoverable
- finish and review check artifact drift, and progress dashboard drift when enabled
- a real project can run through init, ingest, develop or fix, finish, and review without needing the old project-coding-skills
