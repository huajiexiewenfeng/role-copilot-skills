---
name: project-fix
description: Use when diagnosing or fixing a project bug, error, failed test, regression, incident, log symptom, or unexpected behavior with scoped project context and LLM Wiki bug summaries.
---

# Project Fix

## Purpose

Diagnose and fix bugs through scoped context, evidence, reproduction, implementation, verification, and bug knowledge sync.

## Required Shared References

Read these role-level references:

- `../references/develop-fix-mvp.md`
- `../references/scoped-working-context.md`
- `../references/templates.md`
- `../references/llm-wiki-mvp.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root.

## Workflow

1. Resolve `project_root`.
2. Capture or ingest the bug source when it is external.
3. Run Context Enrichment Gate.
4. Summarize:
   - observed behavior
   - expected behavior
   - affected scope
   - evidence
   - recent changes
   - working context page, if used
5. Reproduce the issue or state why reproduction is not currently possible.
6. Diagnose likely cause before changing code.
7. Fix only active scopes unless escalation is justified.
8. Verify the fix.
9. Create or update `.llm-wiki/working-context/<bug-id>.md` when diagnosis or fix crosses modules.
10. Update `.llm-wiki/bugs/<bug-id>.md` after verification.

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

## Working Context
```

## Safety

- Do not patch randomly before diagnosis.
- Do not expand write scope without evidence.
- If verification cannot run, state why and record residual risk.
