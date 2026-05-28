# Scoped Working Context

Full repositories and all documents may be indexed, but current work must activate only the relevant subset.

## Document Context States

- `discovered`: found on disk or in source directories, not indexed yet.
- `indexed`: registered in ingest index or source proxy.
- `summarized`: has a useful source proxy summary.
- `candidate`: may be relevant but should not enter deep context yet.
- `active`: relevant to the current task and allowed in deep context.
- `excluded`: intentionally out of current task scope.

## Code Scope States

- `active`: can be read deeply and modified.
- `read-only`: can be read at API, DTO, contract, README, or interface boundary.
- `candidate`: may become active if evidence requires it.
- `excluded`: do not read or modify.

## Scope Selection Rule

Start narrow:

1. Activate scopes named by the user.
2. Activate scopes directly required by active source materials.
3. Mark direct dependencies as read-only or candidate.
4. Mark unrelated top-level services as discovered or excluded.

Do not activate all services in a monorepo because they exist.

## Escalation Rule

Candidate can become active only when there is evidence:

- build or test failure points to it
- API or DTO contract must change
- source material explicitly names it
- implementation cannot proceed without it
- user approves the scope expansion

When expanding scope, report:

```text
Scope escalation:
From:
To:
Reason:
Risk:
Verification needed:
```

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
