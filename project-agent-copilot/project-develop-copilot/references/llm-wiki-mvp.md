# LLM Wiki MVP

Project `.llm-wiki` is maintained by the agent. Users provide or edit original source materials; the agent maintains the index layer.

## Contract

- `.llm-wiki` does not replace PRD, issue, design, code, tests, or configuration.
- `.llm-wiki` does not store long original content.
- `.llm-wiki` stores indexes, summaries, relationships, status, and gaps.
- When wiki conflicts with source material or code, source material and code win.

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
