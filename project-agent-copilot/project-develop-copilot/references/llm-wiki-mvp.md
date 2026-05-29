# LLM Wiki MVP

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
- `modules/<scope>.md`: only created for active scopes.
