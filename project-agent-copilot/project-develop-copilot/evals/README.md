# Evals

Manual eval definitions and developer tooling for Project Develop Copilot lifecycle behavior live here.

Do not store raw private conversations, customer data, credentials, or sensitive project context.

## Current Eval Set

- `project-develop-copilot-evals.md`: 35 manual P0 lifecycle and routing regression definitions.
- `runbook.md`: how to run and score the evals manually.
- `blackbox/README.md`: developer-only black-box sidecar for Eval 2, 32, 33, 34, and 35.

There is no automated Agent runner. The developer-only black-box sidecar prepares, checkpoints, grades, and reports file-based Eval 2/32/33/34/35 Runs without invoking an Agent or LLM. Deterministic repository-integrity CI may validate the sidecar, static text, links, and canonical definition facts; automated Agent lifecycle and Runtime Eval CI remain deferred.

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
