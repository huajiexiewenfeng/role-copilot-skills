---
name: project-review
description: Use when reviewing project changes for code risk, test gaps, requirement consistency, scope drift, stale context, LLM Wiki sync, tool-bridge consistency, or readiness before commit, PR, or merge.
---

# Project Review

## Purpose

Review project work for correctness, scope, verification, lifecycle consistency, artifact drift, dashboard drift, handoff readiness, and Project Develop Copilot skill improvement.

This skill uses a review stance. Findings come first and are ordered by severity. It is the project-facing review gate for lifecycle and context failures, but it does not replace general-purpose conversation review or skill evaluation outside Project Develop Copilot.

## When to Use

Use when the user asks for:

- review, risk check, before commit, before PR, before merge, handoff readiness
- scope drift, wiki drift, artifact drift, or dashboard drift check
- lifecycle quality check after a project flow
- evaluator or Dolores trigger decision from project process risk
- wrong-root recovery, foreign project facts, or cross-session project continuity check
- project skill rule gap or project lifecycle eval gap review

## When Not to Use

- Do not use to implement fixes unless the user explicitly asks.
- Do not use for initial bug diagnosis; use `project-fix`.
- Do not use for ordinary lightweight design discussion unless the user asks to review the process.
- Do not use as a replacement for verification commands.

## Owned Gates

- Verification Gate check
- Finish Sync Gate check
- Review & Wiki Integrity Gate

## Project Lifecycle Evaluation Lens

`project-review` owns review for Project Develop Copilot lifecycle work.

It may evaluate:

- lifecycle trace: whether init, ingest, develop, fix, finish, or review followed the project workflow
- project context integrity: whether `.llm-wiki`, scopes, sources, working-context, artifacts, dashboard, Change Briefs, and Bug Briefs stay consistent with source evidence and user decisions
- project skill rule gaps: whether a failure shows that a project skill needs a rule, acceptance case, or smaller patch
- cross-session project continuity: whether the agent recovered from project-local `.llm-wiki` evidence instead of relying on unrecorded chat memory

It must not become a general-purpose Dolores or `skill-evaluator` replacement. For non-project skill failures, use the appropriate external review skill. For project workflow failures, report project skill improvement recommendations inside `project-review`.

## Initialization Gate

Run after resolving the project root and before lifecycle-quality, wiki-integrity, dashboard-drift, or full-lifecycle review.

- `wiki_required_for: lifecycle-or-wiki-review`
- `on_missing_wiki: route project-init`
- `pending_primary_stage: project-review`
- Preserve the requested review scope as `pending_intent`.
- `allowed_without_wiki: quick-diff-review`
- The exception applies only when the user explicitly limits the task to source or diff findings. It stays read-only with respect to lifecycle state and must not claim lifecycle or wiki integrity.
- Otherwise, if `<project_root>/.llm-wiki/` is absent, stop and return a Context Handoff to `project-init`. Do not create a partial wiki or review record inside this child as a substitute for initialization.

On the missing-wiki branch outside the read-only exception, emit this minimal handoff:

```text
bootstrap_handoff:
  project_root: <resolved project root>
  pending_intent: <preserved review scope>
  pending_primary_stage: project-review
  requested_stage_or_bridge: project-init
  current_gate: Initialization Gate
```

## Source / Diff Only Review

When `review_mode: quick-diff-review` is selected for a repository without `.llm-wiki/`:

1. Inspect only git status/diff, changed source, related tests, test-integrity risk, and available verification evidence.
2. Stay read-only with respect to project lifecycle state.
3. Explicitly skip wiki, artifact, dashboard, and Flow Record integrity checks.
4. Report that lifecycle and wiki integrity were not assessed.
5. Stop after findings, open questions, verification gaps, and source-level residual risk; do not continue into the lifecycle-review workflow below.

## Required First Check

1. Resolve project root.
2. Run the Initialization Gate, or explicitly record the `quick-diff-review` exception.
3. Resolve optional shared references from `../references/` or local `references/`. If `flow-record.md`, `progress-dashboard.md`, or `continuous-evolution.md` is missing, continue in degraded mode using the minimum rules in this skill; report the missing deep references and keep findings grounded in available diff, wiki, and evidence.
4. Inspect git status and diff.
5. Identify active Change Brief, Bug Brief, working-context, or relevant `.llm-wiki/log.md` entry when lifecycle review is in scope.
6. Check verification evidence, raw output, exit code, executor, authority, trust level, and limitation acceptor.
7. Check whether production code and tests/mocks/fixtures/expected values changed together.
8. Check artifact registry and dashboard evidence when present, unless `quick-diff-review` is active.
9. If process risk is present, identify the lifecycle step and whether the failure is an artifact issue, lifecycle issue, context integrity issue, project skill rule gap, eval gap, or user-decision gap.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/flow-record.md`
- `../references/session-digest.md`
- `../references/progress-dashboard.md`
- `../references/continuous-evolution.md`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md`

Reference availability policy:

- Shared references are deep references, not startup requirements.
- Do not stop solely because `../references/` is missing.
- In degraded mode, review must still check diff, verification evidence, scope drift, wiki drift, Flow Record evidence, and dashboard claims when files are available. The separate `quick-diff-review` exception skips lifecycle/wiki checks rather than treating absent wiki state as degraded lifecycle evidence.
- Do not propose project-skill evolution patches from missing deep references alone; only report the missing reference as a process gap.

Workflow:

1. Resolve project root.
2. Inspect current git status and diff.
   - If `quick-diff-review` is active, use the reduced workflow above and stop before step 3.
3. Identify active requirement, bug, working context, source, artifact, or dashboard context.
4. Check code risk and behavior correctness.
5. Check verification gaps.
6. Check verification provenance: raw output reference, exit code, executor, authority, trust level, and limitation acceptor.
7. If tests/mocks/fixtures/expected values changed, check test integrity: real behavior coverage, assertion strength, over-mocking, deleted coverage, and changed expected behavior.
8. Check scope drift against active/read-only/candidate/excluded scopes.
9. Check wiki drift.
10. Check artifact drift.
11. Check dashboard drift as projection drift: existence, evidence support, Flow Record cards, risk visibility, verification claims, trust level, and language consistency. Dashboard must not be treated as status authority.
12. Check Flow Record drift against current user decision, code, tests, verification output, and artifact registry evidence.
13. Check Session Digest integrity when historical session context affected the work.
14. Check external bridge consistency.
15. Check project root and wiki placement when init/recovery occurred.
16. Check cross-session project continuity when prior context or previous chat state affects the work.
17. Use requesting-code-review as an additional quality pass when available, but keep this skill's findings-first output.
18. Include Lifecycle Quality and evaluator/Dolores trigger decision when process risk appears.
19. If the failure suggests a project skill rule gap, propose the smallest project-skill patch and an acceptance/eval case. Do not evaluate unrelated non-project skills here.
20. Report findings first, then open questions, verification gaps, context gaps, residual risk, and summary.

## Project Graph / Wiki Doctor Review Items

For Project Develop Copilot lifecycle reviews, check:

- Whether requirement, design, bug, or plan documents outside `.llm-wiki` would trigger `orphan-design-doc`.
- Whether cross-service `.llm-wiki` artifacts include either `## Project Graph Evidence` with valid edge ids or `## Project Graph Gaps`.
- Whether self-review distinguishes primary workflow, retrospective confirmation, and ideal workflow instead of overstating Project Graph usage.
- Whether WARN findings from `.llm-wiki/tools/llm_wiki_doctor.py` have a visible outlet in handoff, job summary, or PR comment.
- `report` output may be cited as advisory maturity evidence, but commit/PR/merge blocking must use `validate --fail-on error`.
## Mode / Entry Selection

| Mode | Use when |
|---|---|
| `quick-diff-review` | user wants a narrow code risk pass |
| `full-lifecycle-review` | user asks before commit/PR/merge or drift checks |
| `dashboard-drift-review` | progress page/status may be stale or unsupported |
| `dolores-trigger-review` | user asks to review whether the lifecycle flow went wrong |
| `evaluator-trigger-review` | one skill/gate failure needs focused improvement analysis |

## Inputs

- git diff and changed files
- tests and verification output
- active Change Brief or Bug Brief
- working-context page
- `.llm-wiki` updates
- artifact registry
- progress dashboard
- source material and acceptance criteria
- user corrections that affect project root, scope, source status, or lifecycle behavior
- cross-session handoff notes when available

## Outputs

Use this format:

```text
Findings:
- [severity] file/path:line - issue

Open questions:

Verification gaps:
Verification provenance:
Test integrity:

Context/wiki gaps:

Artifact/dashboard gaps:

Lifecycle quality:

Project skill improvement:

Summary:
```

Flow Record drift checklist:

```text
- dashboard card has no matching Flow Record
- dashboard card step/status differs from Flow Record
- dashboard, handoff, or log claims stronger progress than Flow Record supports
- Flow Record appears stale compared with current code, tests, verification output, or user decision
- Flow Record `done` step has no evidence
- `development` done but no changed files or implementation evidence
- `testing` done but no verification evidence or accepted limitation
- `testing` done with only agent-local evidence but no trust-level label
- accepted limitation has no non-agent acceptor
- verification record has no raw output, exit code, executor, authority, or scope
- production code and tests/mocks changed together but no Verification Gate test-integrity result exists
- tests were weakened, over-mocked, or expected values changed without requirement evidence
- `archive` done but no handoff/release/done evidence
- same source/design document has duplicate active flow_id values
```

Session Digest integrity checklist:

```text
- recall-Session Digest item was written as confirmed project truth without Lifecycle Promotion
- conflict digest item silently overwrote newer code or wiki evidence
- dashboard card claims progress from unconfirmed historical session memory
- linked flow_id does not match actual requirement or bug evidence
- raw sensitive session content was copied into `.llm-wiki`
- digest import created a requirement, bug, Flow Record, scope update, dashboard update, or verification claim without explicit promotion confirmation
```

If no issues are found:

```text
Findings:
- No blocking or major issues found.

Verification gaps:
Context/wiki gaps:
Session Digest gaps:
Artifact/dashboard gaps:
Lifecycle quality:
Project skill improvement:
Residual risk:
Summary:
```

## Context Handoff

Before requesting-code-review, evaluator, Dolores, or another bridge, provide scoped context and the review focus.

## Return Handoff

Return:

```markdown
## Return Handoff

- stage_or_bridge_used: project-review
- result_summary:
- changed_assumptions:
- recommended_scope_changes:
- artifacts:
- verification_notes:
- lifecycle_updates_needed:
- next_gate:
```

Lifecycle Quality output:

```markdown
## Lifecycle Quality

- evaluator_needed: yes | no
- dolores_review_needed: yes | no
- reason:
- suggested_artifact:
- blocking: yes | no
```

Project skill improvement output when a project workflow failed:

```markdown
## Project Skill Improvement

- failure_type:
- likely_project_skill_gap:
- smallest_useful_patch:
- suggested_acceptance_case:
- overfitting_risk:
```

## Boundaries

- Do not rewrite code during review unless the user asks for fixes.
- Do not bury blocking findings under summaries.
- Do not report no findings without checking verification and lifecycle drift.
- Do not treat agent-local verification as independent external audit.
- Do not accept `accepted limitation` unless the acceptor is a user, project owner, CI policy, or external reviewer.
- Do not ignore test integrity when production code and tests/mocks/fixtures/expected values changed together.
- Do not run evaluator or Dolores for every ordinary review.
- Do not treat dashboard as a source of truth.
- Do not treat handoff or log text as lifecycle status authority when Flow Record and verification evidence disagree.
- Do not turn project-review into a general-purpose Dolores or skill-evaluator replacement.
- Do not rely on unrecorded chat memory as project source of truth; prefer `.llm-wiki/log.md`, working-context, artifacts, Change Briefs, and Bug Briefs.

## Common Mistakes

- Performing only code review and ignoring lifecycle state.
- Missing changed files outside active scope.
- Ignoring missing wiki/artifact/dashboard updates.
- Missing self-referential verification risk: the same agent wrote the tests, verification record, limitation, and dashboard status.
- Missing over-mocking or weakened assertions after a previously failing test.
- Treating external bridge output as authoritative without scope checks.
- Turning Dolores into a generic summary.
- Missing wrong-root `.llm-wiki` writes or foreign project facts after project-init recovery.
- Reporting process failure without recommending the minimal project skill rule or acceptance-case improvement.
