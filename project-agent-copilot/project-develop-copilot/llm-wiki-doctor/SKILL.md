---
name: llm-wiki-doctor
description: Use when checking, scoring, diagnosing, or explaining a project-local .llm-wiki health state, LLM Wiki Doctor output, wiki maturity score, empty wiki skeletons after project init, Project Graph evidence warnings, or llm_wiki_doctor pre-commit/CI failures.
---

# LLM Wiki Doctor

## Purpose

Run and interpret LLM Wiki Doctor for a project-local `.llm-wiki`.

Default to read-only diagnosis. Use deterministic `validate` for hard validator findings and `report` for human-facing Chinese maturity reports. Do not repair files unless the user explicitly asks for repair or completion.

## Required First Check

1. Resolve the project root.
2. Confirm `.llm-wiki` exists. If it does not exist, route to `project-init`.
3. Resolve the doctor script from `.llm-wiki/tools/llm_wiki_doctor.py`, then the bundled `../scripts/llm_wiki_doctor.py`.
4. For CI, pre-commit, project-finish, or blocking failures, run `validate`.
5. Otherwise run `report` and explain the Chinese report.

## Commands

Human diagnosis:

```text
python <doctor> report --root . --format text
```

Machine checks:

```text
python <doctor> validate --root . --changed --format text --fail-on error
python <doctor> validate --root . --base origin/main --format json --fail-on error
```

Structured maturity signals:

```text
python <doctor> score --root . --format json
```

## Interpretation Rules

- Treat `validate` findings as deterministic script output.
- Treat `score` as directional maturity guidance, not a KPI.
- Report `not-applicable` dimensions instead of penalizing simple projects.
- Use script signals as evidence for semantic judgments. Do not invent project facts from the score.
- Keep Project Graph findings visible: `missing-graph-evidence`, `invalid-edge-id`, `dangling-cross-ref`, `duplicate-edge-fingerprint`, and `leaked-local-path`.

## Repair Boundary

Default to read-only. When the user explicitly asks to repair, route structural repairs to `project-maintain` unless the repair is limited to installing or running the doctor. Never auto-fill semantic content such as module responsibilities, API contracts, requirement scope, bug conclusions, confirmed Project Graph edges, or verification status.
