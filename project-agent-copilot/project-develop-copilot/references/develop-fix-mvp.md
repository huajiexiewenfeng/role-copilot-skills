# Develop and Fix MVP

For new features and bug fixes, project context is read at the start of the flow, before brainstorming, planning, debugging, or implementation.

## Context Enrichment Gate

1. Resolve project root.
2. Read `.llm-wiki/index.md` if present.
3. Read `.llm-wiki/modules/index.md` if present.
4. Read `.llm-wiki/ingest/index.md` if relevant.
5. Detect unindexed source documents in configured source directories.
6. Select active, candidate, and excluded sources.
7. Select active, read-only, and excluded code scopes.
8. Produce a context summary and gaps.

## project develop Flow

1. Run Context Enrichment Gate.
2. If Superpowers brainstorming is available, use it after context summary.
3. Define requirement scope and acceptance criteria.
4. Create or update `.llm-wiki/requirements/<change-id>.md`.
5. Hand off to implementation planning.
6. Do not modify code until user confirms implementation.

## project fix Flow

1. Capture bug source or ingest it when external.
2. Run Context Enrichment Gate.
3. Summarize symptom, expected behavior, affected scope, and evidence.
4. Reproduce or define why reproduction is not possible.
5. Diagnose likely cause before code changes.
6. Fix only active scopes.
7. Verify and update `.llm-wiki/bugs/<bug-id>.md`.
