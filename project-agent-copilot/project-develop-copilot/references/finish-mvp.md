# Finish MVP

Use `project finish` after implementation and verification.

## Preconditions

Before wiki sync, confirm at least one verification result:

- tests passed
- compile passed
- lint passed
- manual verification completed
- user accepted that verification could not be run and why

If no verification exists, do not claim the work is complete. Ask whether to run verification or record the limitation.

## Change Summary

Collect:

- files changed
- behavior changed
- active requirement or bug
- active scopes
- working context page, if used
- tests or checks run
- skipped verification
- user decisions

## Knowledge Sync

Update only pages affected by the actual change.

Always consider:

- `.llm-wiki/log.md`
- related requirement summary
- related bug summary
- related module summary
- source proxy status
- related working context status

Do not write large implementation narratives. Preserve indexes, summaries, status, relationships, and gaps.

## Requirement Status Values

Use:

- `captured`
- `planned`
- `implementing`
- `verified`
- `done`
- `blocked`

## Bug Status Values

Use:

- `captured`
- `diagnosing`
- `fixing`
- `verified`
- `closed`
- `blocked`

## Final Report

Report:

```text
Implementation summary:
Verification:
Wiki updates:
Remaining gaps:
Next action:
```
