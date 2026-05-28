# Develop and Fix MVP

For new features and bug fixes, project context is read at the start of the flow, before brainstorming, planning, debugging, or implementation.

## Context Enrichment Gate

1. Resolve project root.
2. Read `.llm-wiki/index.md` if present.
3. Read `.llm-wiki/modules/index.md` if present.
4. Read `.llm-wiki/ingest/index.md` if present and relevant.
5. Detect unindexed source documents in configured source directories.
6. Select active, candidate, and excluded sources.
7. Select active, read-only, and excluded code scopes.
8. Read active module summaries and source proxies.
9. Produce a context summary and gaps.

## Source Directory Discovery

Look for these directories when they exist:

```text
docs/inbox
docs/prd
docs/design
docs/meeting
docs/feedback
requirements
product
docs
```

Do not deep-read everything. Compare discovered files against `.llm-wiki/ingest/index.md` and report unindexed or changed files.

## project develop Flow

1. Run Context Enrichment Gate.
2. Summarize current project facts, active sources, active scopes, assumptions, and gaps.
3. If Superpowers brainstorming is available, use it after context summary.
4. Define requirement scope and acceptance criteria.
5. Create or update `.llm-wiki/requirements/<change-id>.md`.
6. Hand off to implementation planning.
7. Do not modify code until user confirms implementation.

## Requirement Page Minimum

```markdown
# Requirement: <change-id>

## Summary

## Source Artifacts

## Scope

## Out of Scope

## Acceptance Criteria

## Active Sources

## Active Scopes

## Candidate Context

## Gaps

## Status
```

## project fix Flow

1. Capture bug source or ingest it when external.
2. Run Context Enrichment Gate.
3. Summarize symptom, expected behavior, affected scope, evidence, and recent changes.
4. Reproduce the issue or state why reproduction is not possible.
5. Diagnose likely cause before code changes.
6. Fix only active scopes unless escalation is justified.
7. Verify the fix.
8. Update `.llm-wiki/bugs/<bug-id>.md` after verification.

## Bug Page Minimum

```markdown
# Bug: <bug-id>

## Source

## Symptom

## Expected

## Scope

## Evidence

## Diagnosis

## Fix

## Verification

## Related
```

## Context Summary Output

Before planning or implementation, output:

```text
Project root:
Active sources:
Candidate sources:
Active scopes:
Read-only scopes:
Excluded scopes:
Known facts:
Assumptions:
Gaps / questions:
Recommended next step:
```
