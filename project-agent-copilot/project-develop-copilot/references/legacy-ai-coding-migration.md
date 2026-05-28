# Legacy docs/ai-coding Migration

`docs/ai-coding` is legacy project coding context. New projects should not create it. Existing projects may migrate it during `project init` or `project refresh`.

Do not delete, move, or rewrite legacy files during MVP migration.

## Migration Mapping

| Legacy file | New target |
|---|---|
| `docs/ai-coding/contexts.md` | `.llm-wiki/modules/index.md` |
| `docs/ai-coding/<scope>/project-profile.md` | `.llm-wiki/modules/<scope>.md` |
| `docs/ai-coding/<scope>/architecture-summary.md` | `.llm-wiki/modules/<scope>.md` |
| `docs/ai-coding/<scope>/coding-rules.md` | `.llm-wiki/modules/<scope>.md` |
| `docs/ai-coding/<scope>/ai-context-sources.md` | `.llm-wiki/ingest/index.md` and `.llm-wiki/sources/` |
| `docs/ai-coding/<scope>/feature-prompt-context.md` | `.llm-wiki/modules/<scope>.md` |
| `docs/ai-coding/<scope>/open-questions.md` | `.llm-wiki/modules/<scope>.md` and `.llm-wiki/log.md` |

## Caution Rules

- Treat legacy AI docs as supporting context, not authority.
- Preserve source paths in migrated summaries.
- Convert stale facts, garbled content, and prompt placeholders into cautions or open questions.
- Source code, tests, build files, configuration, and user decisions override legacy docs.
