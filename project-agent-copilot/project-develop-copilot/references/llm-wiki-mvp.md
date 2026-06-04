# LLM Wiki MVP

Read `north-star.md` first when changing the project wiki contract.

Project `.llm-wiki` is maintained by the agent. Users provide or edit original source materials; the agent maintains the index layer.

This is the internalized project subset of the LLM Wiki idea: small, local, code-aware, and tied to the development lifecycle. It is not a full Obsidian vault workflow.

## Contract

- `.llm-wiki` does not replace PRD, issue, design, code, tests, or configuration.
- `.llm-wiki` does not store long original content.
- `.llm-wiki` stores indexes, summaries, relationships, status, and gaps.
- When wiki conflicts with source material or code, source material and code win.
- `.llm-wiki` is updated at lifecycle gates: init, ingest, develop or fix, finish, and review.

## MVP Structure

```text
.llm-wiki/
  index.md
  log.md
  AGENTS.md
  ingest/
    index.md
  sources/
  requirements/
  bugs/
  working-context/
  modules/
    index.md
    <scope>/
      index.md
```

## File Responsibilities

- `index.md`: project knowledge entry point.
- `log.md`: chronological wiki maintenance log.
- `AGENTS.md`: local rules for agents maintaining the wiki.
- `ingest/index.md`: source material registry.
- `sources/`: source proxy pages.
- `requirements/`: requirement summaries and status.
- `bugs/`: bug summaries, diagnosis, and verification status.
- `working-context/`: task-scoped context for complex or cross-module work.
- `modules/index.md`: module and service registry.
- `modules/<scope>/index.md`: long-lived context for one active module, service, or domain.

## Scope Context Storage

Do not create a separate project-root `scope-context/`, `contexts/`, or new `docs/ai-coding/<scope>/` structure as the Project Develop Copilot primary context store.

Use these locations instead:

- Project-level context belongs in `.llm-wiki/index.md`, `.llm-wiki/modules/index.md`, and shared registries.
- Scope-level long-lived context belongs under `.llm-wiki/modules/<scope>/`.
- Change-level or bug-level working context belongs in `.llm-wiki/working-context/<change-id>.md`.
- Legacy `docs/ai-coding/<scope>/` remains read-only source context unless the user explicitly asks to maintain it.

This keeps one project knowledge entry point while preserving scoped context isolation. A requirement may involve multiple active scopes; in that case, each module keeps its own local context under `modules/<scope>/`, and the cross-module coordination lives in `working-context/<change-id>.md`.
