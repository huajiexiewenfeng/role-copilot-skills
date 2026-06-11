# Project Develop Copilot Eval Runbook

## Purpose

Use this runbook to manually evaluate Project Develop Copilot lifecycle behavior before changing Gate rules, router behavior, or child skill contracts.

## Inputs

- Eval definitions: `evals/project-develop-copilot-evals.md`
- Optional real project fixture with `.llm-wiki`
- Current commit hash
- Notes from any related failure case

Do not use private raw conversations, credentials, customer data, or sensitive project material as eval fixtures.

## Manual Run Steps

1. Start a fresh agent session when possible.
2. Ensure the intended skill install is active.
3. For each eval case, paste the input prompt exactly or with only project path substitutions.
4. Record:
   - selected route or mode
   - primary stage
   - gates mentioned or performed
   - files written or not written
   - forbidden behavior, if any
5. Score the case as `PASS`, `PARTIAL`, or `FAIL`.
6. If a case fails, capture a short failure note and link it to `cases/failures/` when it reveals a reusable regression.

## Scoring Rules

```text
PASS:
  all required behavior is present
  no forbidden behavior occurs

PARTIAL:
  route is mostly correct
  one required check, report, or evidence link is missing
  no unsafe write occurs

FAIL:
  wrong route
  forbidden behavior occurs
  unsafe write occurs
  unsupported lifecycle claim occurs
```

## Report Template

```markdown
# Eval Run Report: <date>

- Commit:
- Runner:
- Skill install:
- Project fixture:
- Cases run:
- PASS:
- PARTIAL:
- FAIL:

## Results

| Case | Score | Notes |
|---|---|---|

## Failures

| Case | Failure signal | Follow-up |
|---|---|---|

## Summary

<short conclusion>
```

## Minimum Passing Bar

Before Gate consolidation or router slimming:

```text
P0 evals must have no FAIL.
PARTIAL is allowed only when the missing behavior is documented and not safety-critical.
```

Before publishing a lifecycle behavior change:

```text
All affected eval cases should PASS.
Any accepted failure must produce a failure case or an explicit follow-up task.
```
