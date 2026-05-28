# Ingest MVP

Use `project ingest` when a source material should become discoverable by project development flows.

## Supported Sources

- URL
- Markdown
- PDF
- Word
- plain text
- meeting notes
- customer feedback
- log or error report

## Flow

1. Identify source type and path or URL.
2. Ask for confirmation before deep reading binary, large, or sensitive-looking sources.
3. Create or update an entry in `.llm-wiki/ingest/index.md`.
4. Create a source proxy in `.llm-wiki/sources/`.
5. Link to requirement, bug, module, or open question when clear.
6. Record gaps when the relationship is uncertain.

## Default Modes

| Source type | Default handling |
|---|---|
| Markdown | summary ingest |
| URL | summary ingest when accessible |
| PDF | path index first, summarize after confirmation |
| Word | path index first, summarize after confirmation |
| logs | summarize symptoms, do not copy secrets |
| sensitive-looking files | path index only |
