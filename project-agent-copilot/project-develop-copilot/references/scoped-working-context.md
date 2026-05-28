# Scoped Working Context

Full repositories and all documents may be indexed, but current work must activate only the relevant subset.

## Document Context States

- discovered
- indexed
- summarized
- candidate
- active
- excluded

## Code Scope States

- active: can be read deeply and modified.
- read-only: can be read at API, DTO, contract, or README boundary.
- candidate: may become active if evidence requires it.
- excluded: do not read or modify.

## Multi-Scope Changes

For cross-service changes, create `.llm-wiki/working-context/<change-id>.md` when the project already has a working-context directory or when the change is complex enough to need one.

Record:

- active scopes
- read-only scopes
- excluded scopes
- scope roles
- cross-service contracts
- write permissions
- escalation log

Scoped context owns local implementation rules. Change working context owns cross-scope coordination.
