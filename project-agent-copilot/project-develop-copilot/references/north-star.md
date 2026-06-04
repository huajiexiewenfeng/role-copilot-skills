# North Star

Read this first when designing, changing, reviewing, or extending Project Develop Copilot. If any implementation choice is unclear, return to this document before adding more rules.

## Mission

Project Develop Copilot is the upgraded successor of project-coding-skills. It internalizes project LLM Wiki and project-coding-skills ideas, then bridges mature top-level skills and tools into one practical project development lifecycle.

Its primary user experience is a lifecycle router: users can enter naturally from a PRD, design discussion, project-wiki question, bug, log, review request, finish request, or resume request without choosing the correct child skill first. The router decides whether the request should stay lightweight, run a read-only project query, or enter the full project lifecycle.

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
   - `.llm-wiki` can be queried directly for discussion context through `project-query`
3. Bridge top-level skills and tools after project context recovery:
   - Superpowers-style brainstorming, planning, TDD, debugging, execution, verification, and review
   - OpenSpec-style requirement discussion, change spec, acceptance criteria, and implementation plan
   - existing codegraph or codeGraphify outputs when present
   - evaluator and conversation review skills when lifecycle quality needs improvement
4. Provide a natural lifecycle router:
   - users face Project Develop Copilot, not isolated child skills
   - lightweight questions stay lightweight
   - project wiki query and discussion context can use `project-query` without entering implementation lifecycle
   - full work creates or resumes a lifecycle session
   - every full entry is resumable
   - every full entry is scoped
   - every full entry returns to lifecycle
   - Change Brief, Bug Brief, and working-context pages carry lifecycle state
5. Provide real, installable project workflow skills:
   - `project-develop-copilot` as the top-level lifecycle router
   - `project-query` for read-only project wiki query and discussion context
   - `project-init`
   - `project-ingest`
   - `project-develop`
   - `project-fix`
   - `project-finish`
   - `project-review`

## Responsibility Split

Project Develop Copilot owns project lifecycle and context:

- lifecycle routing
- lightweight-answer boundary
- project root resolution
- `.llm-wiki` protocol
- ingest/source proxies
- scoped working context
- working-context pages for complex or cross-module work
- Change Brief and Bug Brief state
- routing records
- lifecycle gates
- external skill bridge contracts
- artifact registry
- progress dashboard state when enabled
- finish sync
- review of wiki drift, scope drift, artifact drift, and dashboard drift
- evaluator and Dolores-style review hooks for skill evolution

External skills and tools own their own expertise:

- Superpowers owns thinking and execution discipline
- OpenSpec-style mechanisms own specification discipline
- codegraph owns graph-derived insight when graph data already exists
- skill-evaluator owns focused skill failure analysis
- conversation-review / Dolores owns full conversation trace review

External tools receive scoped project context. They do not choose project scope from scratch, and they do not declare project work finished. Their outputs must return through a structured handoff into the lifecycle session.

## Lifecycle-First Rule

Every full lifecycle entry follows lifecycle-first rules:

1. Route natural user intent.
2. Decide lightweight-answer vs full lifecycle.
3. Resolve project root.
4. Discover new or stale context.
5. Create or resume lifecycle session.
6. Save a short routing record.
7. Recover `.llm-wiki` indexes and summaries.
8. Identify active sources.
9. Select active, read-only, candidate, and excluded scopes.
10. Create or reuse working-context when the task is cross-module.
11. Bridge to external skills or tools only after context is scoped.
12. Verify, sync knowledge, register artifacts, update dashboard state when enabled, and review drift.

Lightweight-answer is still a valid lifecycle router result. It is used when the user only wants explanation, file location, concept discussion, or design discussion without execution. It must not create Change Briefs, modify code, update dashboards, or claim project completion unless the user explicitly upgrades the work.

Read-only project query is a separate router result. It is used when the user wants to discuss the project based on `.llm-wiki`, locate related requirements, bugs, source proxies, development notes, artifacts, or previous decisions, but has not asked to implement or change state. It should return a Project Context Pack with evidence, confidence, and possible next routes. It must not create Change Briefs, Bug Briefs, working-context pages, dashboard updates, or code edits by default.

## Gate Stack

The complete version must implement the following gates as explicit behavior, not only as documentation labels:

- Context Discovery Gate
- Context Enrichment Gate
- Clarification Gate
- Bug Evidence Gate
- Context Lock Gate
- External Skill Bridge Gate
- Verification Gate
- Knowledge Sync Gate
- Artifact Sync Gate
- Progress Dashboard Sync Gate
- Review Gate

A child skill may own a subset of gates, but the router owns the obligation to keep the gate sequence coherent.

## Domain Skill Contract

Each project domain skill must be router-friendly. It should expose:

- Purpose
- When to Use
- When Not to Use
- Owned Gates
- Required First Check
- Core Process
- Mode / Entry Selection
- Inputs
- Outputs
- Context Handoff
- Return Handoff
- Boundaries
- Common Mistakes

This follows the Superpowers / Thinking Skills style: the skill must be easy for a router to choose, easy for an agent to execute, and hard to misuse.

## Complete Version Target

This version is not another fragmented prototype. It targets Level 3.5 before broad testing:

```text
Level 1: project init + project ingest + project finish wiki sync
Level 2: project develop/fix + scoped working context
Level 3: artifact registry + context freshness + review checks
Level 3.5: continuous evolution hooks + evaluator/Dolores artifacts
Level 4: CI/wiki lint/reminder automation + automated eval runner
```

Level 3.5 means the complete implementation includes the top-level router, lifecycle session, gate stack, artifact registry, progress dashboard protocol, review drift checks, and evaluator / Dolores trigger and artifact conventions. Fully automated CI integration, reminders, GitHub issue/PR automation, and automated eval runners are extension points for Level 4.

## Non-Goals

- Do not rebuild Superpowers inside project skills.
- Do not bridge project-coding-skills as an external runtime dependency.
- Do not require OpenSpec tooling.
- Do not require codegraph generation.
- Do not copy a full Obsidian vault workflow.
- Do not make `.llm-wiki` a large documentation warehouse.
- Do not deep-read every service or document by default.
- Do not make evaluator or Dolores block ordinary delivery by default.
- Do not make the progress dashboard a source of truth.

## Done Means

For the complete Level 3.5 version to be considered ready for broad testing:

- the top-level `project-develop-copilot` router is installable and discoverable
- all seven project stage skills are installable and discoverable
- natural user entry points route correctly without the user choosing child skills
- lightweight explanation and design discussion stay lightweight
- full requirement work creates or resumes a Change Brief
- full bug work creates or resumes a Bug Brief
- routing records are saved for full lifecycle sessions
- project init creates a usable `.llm-wiki`
- project ingest captures source material without copying long or sensitive content
- project develop and project fix load only relevant scoped context
- working-context handles complex or cross-module work
- external skills receive scoped context and return structured handoff
- project finish updates wiki only after verification or an explicit limitation
- project review checks code risk, test gaps, scope drift, tool-bridge consistency, wiki drift, artifact drift, and progress dashboard drift when enabled
- progress dashboard state is backed by `.llm-wiki`, artifacts, verification records, or git diff evidence
- skill failures can enter evaluator review without blocking normal delivery
- full lifecycle conversations can enter Dolores-style review when explicitly requested or when review finds process-level risk
- reusable failures and golden paths can be saved as abstract eval or case artifacts without raw private conversation data
- a real project can run through init, ingest, develop or fix, finish, review, dashboard sync, and lifecycle review without needing the old project-coding-skills
