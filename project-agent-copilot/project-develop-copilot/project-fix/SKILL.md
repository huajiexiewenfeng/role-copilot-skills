---
name: project-fix
description: Use when diagnosing or fixing a project bug, error, failed test, regression, incident, log symptom, or unexpected behavior with scoped project context and LLM Wiki bug summaries.
---

# Project Fix

## Purpose

Diagnose and fix bugs through scoped context, evidence, reproduction, implementation, verification, and bug knowledge sync.

## Required Shared References

Read these role-level references:

- `../references/north-star.md`
- `../references/develop-fix-mvp.md`
- `../references/scoped-working-context.md`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md`
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
5. Reproduce the issue or state why reproduction is not currently possible using the Reproduction Evidence format.
6. Bridge to systematic-debugging after evidence and scoped context are captured when available.
7. Diagnose likely cause before changing code.
8. Use test-driven-development for regression coverage when feasible.
9. If the fix needs a candidate or excluded scope, run Bug Scope Escalation before editing.
10. Fix only active scopes unless escalation is justified.
11. Verify the fix.
12. Create or update `.llm-wiki/working-context/<bug-id>.md` when diagnosis or fix crosses modules.
13. Update `.llm-wiki/bugs/<bug-id>.md` after verification.
14. Report final diagnosis and verification.

## Reproduction Evidence

Use this format:

```text
Reproduction:
Command or steps:
Input:
Observed:
Expected:
Evidence:
Status: reproduced | not-reproduced | blocked
```

If not reproduced:

1. State what was tried.
2. State what evidence still supports the diagnosis.
3. Avoid risky fixes unless evidence is strong or the user approves.
4. Record residual risk in the bug page.

## Bug Scope Escalation

Before editing a module outside active scope, report:

```text
Bug scope escalation:
From:
To:
Evidence:
Why active scope is insufficient:
Risk:
Verification needed:
```

Ask for approval unless the evidence is direct, the change is low risk, and the user already asked to proceed.

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

## Final Report

Report:

```text
Diagnosis:
Fix:
Files changed:
Scope escalation:
Regression coverage:
Verification:
Wiki updates:
Residual risk:
Next action:
```

## Safety

- Do not patch randomly before diagnosis.
- Do not expand write scope without evidence.
- If verification cannot run, state why and record residual risk.
