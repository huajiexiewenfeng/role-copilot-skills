# Bug Brief: 2026-07-23-blackbox-report-shallow-checkout

## Summary

- title: Black-box report tests require an unavailable parent commit in shallow CI checkouts
- status: verified
- flow_id: 2026-07-23-blackbox-report-shallow-checkout
- severity: CI blocking
- owner: Codex
- updated_at: 2026-07-23

## Routing

- intent: failed-test
- primary_stage: project-fix
- secondary_bridges: systematic-debugging, test-driven-development, verification-before-completion
- confidence: high
- reason: all eleven GitHub Actions errors share one setup failure
- next_gate: Scope Lock Gate
- routed_at: 2026-07-23

## Source

- path/url/log/user_report: user-provided GitHub Actions traceback
- source_proxy: summarized here; raw log remains outside the repository
- sensitivity: internal CI output

## Symptom

`BlackboxEvalReportTest.setUp` runs `git rev-parse HEAD~1`. GitHub Actions checks out one commit by default, so all eleven tests in the class error before exercising report behavior. After that failure was removed, the Windows job exposed a second test-only path comparison between an 8.3 temporary-directory spelling and the CLI's resolved long-path spelling.

## Expected

Report tests should create and control their own Git commit fixtures and pass in both full-history and shallow source checkouts.

## Evidence

- Full-history checkout: the selected report test passed.
- One-commit local shallow clone: the same test reproduced `fatal: ambiguous argument 'HEAD~1'`.
- The workflow uses `actions/checkout@v4` without a custom `fetch-depth`.
- The test reads commits from the source repository instead of a test-owned repository.
- Hosted Ubuntu CI passed after the first fix.
- Hosted Windows CI then reached all 153 tests and failed only `test_prepare_cli_prints_paths_and_records_optional_verified_skill`: expected `RUNNER~1`, observed `runneradmin`.

## Reproduction

- status: reproduced
- command_or_steps: clone the repository with `--depth 1 --no-local`, then run the selected `BlackboxEvalReportTest`
- observed: setup errors while resolving `HEAD~1`
- expected: the test owns two distinct valid source commits and reaches report assertions
- limitation: none

## Scope

- active: `scripts/tests/test_blackbox_eval.py`
- read_only: `scripts/blackbox_eval.py`, `.github/workflows/project-develop-copilot-ci.yml`
- candidate: none
- excluded: production routing and initialization contracts, other Skills, user-facing eval workflow
- escalation_history: none

## Diagnosis

The report test fixture is coupled to the history depth of the repository running the test. Increasing checkout depth would mask that test-isolation defect. A temporary two-commit Git repository gives the report validator real immutable commits without depending on CI checkout shape.

The CLI correctly emits the resolved workspace path returned by `prepare_run`. The Windows-only assertion failure came from constructing expected output from the unresolved `TemporaryDirectory` spelling. Resolving the expected workspace before enumerating its run directory compares the same canonical path without weakening the CLI contract.

## External Findings

None. The failure is local to repository test setup.

## Fix Plan

Create a two-commit source repository inside the test temporary directory, point the loaded runner's `REPO_ROOT` at it, and resolve the CLI test's expected workspace path before comparing printed paths. Keep all report behavior and production code unchanged.

## Verification

- status: partial
- commands_or_checks: selected report test; complete report test class; full unittest discovery; text quality; document integrity; scaffold drift; one-commit shallow-clone regression
- result_summary: first fix passed the selected test, 11/11 report tests, 153/153 full tests, all three repository gates, the one-commit shallow regression, and hosted Ubuntu; after the Windows finding, the corrected selected CLI test and complete CLI class passed 1/1 and 3/3, and all repository gates passed again
- limitation: post-follow-up full local discovery exceeded the 20-minute command budget without emitting a failure; hosted CI is required for the final complete run
- residual_risk: Windows path-normalization follow-up requires hosted verification

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | GitHub Actions traceback summary | 2026-07-23 |
| design | done | full-history versus shallow-clone comparison | 2026-07-23 |
| plan | done | test-owned two-commit source repository | 2026-07-23 |
| development | done | report tests own a two-commit temporary source repository; Windows CLI expectation now uses a resolved path | 2026-07-23 |
| testing | active | first fix passed locally and on Ubuntu; Windows follow-up pending | 2026-07-23 |
| archive | active | `handoff/2026-07-23-blackbox-report-shallow-checkout-handoff.md` requires final hosted result | 2026-07-23 |

## Artifacts

- `.llm-wiki/bugs/2026-07-23-blackbox-report-shallow-checkout.md`
- `.llm-wiki/handoff/2026-07-23-blackbox-report-shallow-checkout-handoff.md`

## Open Questions

None.

## Residual Risk

Only the post-push GitHub Actions run remains to confirm the hosted environment.
