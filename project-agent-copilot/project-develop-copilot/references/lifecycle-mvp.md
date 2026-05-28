# Lifecycle MVP

Use this reference for the first usable version of Project Develop Copilot.

## Entries

| Entry | Purpose | Required output |
|---|---|---|
| project init | Initialize project protocol and `.llm-wiki` | `.llm-wiki` skeleton and module registry |
| project ingest | Capture source material | source proxy and ingest index entry |
| project develop | Develop a requirement | context summary, working context, plan handoff |
| project fix | Diagnose and fix a bug | bug summary, diagnosis, verification |
| project finish | Sync verified work | updated wiki summaries and final report |
| project review | Check consistency | findings and risks |

## Project Root Resolution

Resolve project root in this order:

1. User-provided project path.
2. Current working directory when it contains `.git`, build files, or project docs.
3. Nearest ancestor containing `.git`.

If multiple roots are plausible, ask one concise question before writing files.

## MVP Non-Goals

- Do not build a task management system.
- Do not require CI integration.
- Do not force every service in a monorepo into context.
- Do not deep-read every PRD, PDF, or Word document.
- Do not update legacy `docs/ai-coding` unless explicitly asked.
