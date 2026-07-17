# Evals

Manual and future automated eval definitions for Project Develop Copilot lifecycle behavior live here.

Do not store raw private conversations, customer data, credentials, or sensitive project context.

## Current Eval Set

- `project-develop-copilot-evals.md`: 32 manual P0 lifecycle and routing regression definitions.
- `runbook.md`: how to run and score the evals manually.

The manual Eval set has no automated Agent runner. Deterministic repository-integrity CI may validate static text, link, and canonical definition facts; automated Agent lifecycle and Runtime Eval CI remain deferred.

## Required Rule

Any new or changed Gate rule must include at least one eval case or explicitly update an existing case. If no eval is added, the change should explain why the existing cases already cover the behavior.

## Scoring

Each case is scored:

```text
PASS: all required behavior is present and no forbidden behavior occurs
PARTIAL: route is mostly correct but one required check or report is missing
FAIL: wrong route, forbidden behavior, unsafe write, or unsupported lifecycle claim
```

Run reports should include:

```text
date:
runner:
skill version or commit:
project fixture:
cases run:
pass:
partial:
fail:
notes:
```
