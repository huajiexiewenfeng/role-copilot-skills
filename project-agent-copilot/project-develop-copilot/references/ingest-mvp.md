# Ingest MVP

Use `project ingest` when source material should become discoverable by project development flows.

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
2. If source is a local file, record path, name, extension, size, and modified time.
3. If source is a URL, record URL, page title if known, and capture time.
4. Ask for confirmation before deep reading binary, large, or sensitive-looking sources.
5. Choose processing mode.
6. Create or update `.llm-wiki/ingest/index.md`.
7. Create a source proxy in `.llm-wiki/sources/`.
8. Link to requirement, bug, module, or open question when clear.
9. Report what was captured and what should happen next.

## Default Modes

| Source type | Default handling |
|---|---|
| Markdown | summary ingest |
| URL | summary ingest when accessible |
| PDF | path index first, summarize after confirmation |
| Word | path index first, summarize after confirmation |
| logs | summarize symptoms, do not copy secrets |
| sensitive-looking files | path index only |

## Ingest Index Entry

Append or update one row:

```markdown
| `<source path or url>` | `<type>` | `sources/<slug>.md` | `<status>` | `<short note>` |
```

Use these statuses:

- `indexed`
- `summarized`
- `needs-confirmation`
- `sensitive-path-only`
- `stale`
- `missing`

## Source Proxy Requirements

Every source proxy must include:

- original source path or URL
- processing mode
- short summary or cautious description
- key points
- related requirements, bugs, or modules when clear
- gaps or confirmation needed

Do not copy long source content. Do not copy secrets or production data.

## Slug Rule

Create a readable lowercase filename when possible:

```text
<date>-<short-source-name>.md
```

Example:

```text
2026-05-28-payment-callback-prd.md
```
