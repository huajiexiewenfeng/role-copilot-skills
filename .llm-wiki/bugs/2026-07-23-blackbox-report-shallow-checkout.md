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

`BlackboxEvalReportTest.setUp` runs `git rev-parse HEAD~1`. GitHub Actions checks out one commit by default, so all eleven tests in the class error before exercising report behavior.

## Expected

Report tests should create and control their own Git commit fixtures and pass in both full-history and shallow source checkouts.

## Evidence

- Full-history checkout: the selected report test passed.
- One-commit local shallow clone: the same test reproduced `fatal: ambiguous argument 'HEAD~1'`.
- The workflow uses `actions/checkout@v4` without a custom `fetch-depth`.
- The test reads commits from the source repository instead of a test-owned repository.

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

## External Findings

None. The failure is local to repository test setup.

## Fix Plan

Create a two-commit source repository inside the test temporary directory, point the loaded runner's `REPO_ROOT` at it, and keep all report behavior and production code unchanged.

## Verification

- status: passed
- commands_or_checks: selected report test; complete report test class; full unittest discovery; text quality; document integrity; scaffold drift; one-commit shallow-clone regression
- result_summary: selected test passed; 11/11 report tests passed; 153/153 full tests passed; all three repository gates passed; selected test passed from a one-commit shallow clone
- limitation: GitHub-hosted CI will run only after push
- residual_risk: live Actions status is pending

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | GitHub Actions traceback summary | 2026-07-23 |
| design | done | full-history versus shallow-clone comparison | 2026-07-23 |
| plan | done | test-owned two-commit source repository | 2026-07-23 |
| development | done | report tests now own a two-commit temporary source repository | 2026-07-23 |
| testing | done | 153 tests and all repository gates passed; shallow regression passed | 2026-07-23 |
| archive | done | `handoff/2026-07-23-blackbox-report-shallow-checkout-handoff.md` | 2026-07-23 |

## Artifacts

- `.llm-wiki/bugs/2026-07-23-blackbox-report-shallow-checkout.md`
- `.llm-wiki/handoff/2026-07-23-blackbox-report-shallow-checkout-handoff.md`

## Open Questions

None.

## Residual Risk

Only the post-push GitHub Actions run remains to confirm the hosted environment.
