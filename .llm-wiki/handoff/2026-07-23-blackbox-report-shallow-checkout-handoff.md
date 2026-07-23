# Handoff: 2026-07-23-blackbox-report-shallow-checkout

## Status

- flow_id: `2026-07-23-blackbox-report-shallow-checkout`
- development: done
- testing: active
- archive: active
- next_gate: verify the Windows path-normalization follow-up and push it

## Implementation Summary

`BlackboxEvalReportTest` now creates a temporary Git repository with two real commits and points the loaded eval runner at that repository. The tests still exercise immutable commit validation, but no longer depend on the source checkout exposing `HEAD~1`.

The Windows job exposed one additional test-only mismatch after the report setup errors were removed: `TemporaryDirectory` supplied an 8.3 short path while `prepare_run` returned the resolved long path. The CLI test now resolves its expected workspace path before comparing printed paths.

Production eval behavior, GitHub Actions checkout depth, and user-facing Skill behavior are unchanged.

## Verification

| Check | Result | Exit |
|---|---|---:|
| original selected failure | passed, 1/1 | 0 |
| complete `BlackboxEvalReportTest` | passed, 11/11 | 0 |
| full `scripts/tests` discovery | passed, 153/153 | 0 |
| one-commit shallow checkout regression | passed, 1/1 | 0 |
| corrected prepare CLI test | passed, 1/1 | 0 |
| complete `BlackboxEvalCliTest` after follow-up | passed, 3/3 | 0 |
| post-follow-up full local discovery | exceeded 20-minute command budget; no failure emitted before termination | 124 |
| `check_text_quality.py` | no findings | 0 |
| `check_doc_integrity.py` | no findings | 0 |
| `sync-doctor.py --check` | clean | 0 |
| `git diff --check` | clean | 0 |

Verification provenance:

- executor: agent-local
- Python: bundled Codex runtime
- reproduction: local clone with `--depth 1 --no-local` and exactly one reachable commit
- authority: current source, tests, Git, and command output
- trust level: passed-agent-local
- GitHub-hosted CI: first-fix Ubuntu passed; first-fix Windows exposed the short-path assertion; follow-up run pending push
- LLM Wiki Doctor finish command: not applicable; this repository has no `.llm-wiki/tools/llm_wiki_doctor.py`

## Test Integrity

- production_changes: no
- test_changes: yes; fixture setup only
- assertions_changed: no
- expected_values_changed: no
- behavior_under_test: unchanged
- bypass_risk: low; the replacement fixture uses real commits and keeps the production commit-resolution checks active

## Residual Risk

Hosted Ubuntu passed the first fix. Hosted Windows reached all 153 tests, then exposed the separate short-path/long-path test assertion. The affected CLI class passes locally after the correction, but a new full local discovery exceeded the command budget; final complete verification is pending the follow-up hosted run.

## Return Handoff

- stage_or_bridge_used: project-fix + systematic-debugging + test-driven-development + project-finish
- result_summary: shallow-checkout dependency removed from report tests
- changed_assumptions: report tests do not require source checkout history
- recommended_scope_changes: none
- artifacts: Bug Brief, this handoff, isolated test fixture change
- verification_notes: 153/153 tests and all local repository gates passed
- lifecycle_updates_needed: record hosted CI outcome externally after push
- next_gate: direct push to `main`, then GitHub Actions observation
