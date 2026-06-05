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

- Review Gate
- Verification Gate check
- Artifact Sync Gate check
- Progress Dashboard Sync Gate check
- Evolution Gate
- Project Lifecycle Evaluation Gate

## Project Lifecycle Evaluation Lens

`project-review` owns review for Project Develop Copilot lifecycle work.

It may evaluate:

- lifecycle trace: whether init, ingest, develop, fix, finish, or review followed the project workflow
- project context integrity: whether `.llm-wiki`, scopes, sources, working-context, artifacts, dashboard, Change Briefs, and Bug Briefs stay consistent with source evidence and user decisions
- project skill rule gaps: whether a failure shows that a project skill needs a rule, acceptance case, or smaller patch
- cross-session project continuity: whether the agent recovered from project-local `.llm-wiki` evidence instead of relying on unrecorded chat memory

It must not become a general-purpose Dolores or `skill-evaluator` replacement. For non-project skill failures, use the appropriate external review skill. For project workflow failures, report project skill improvement recommendations inside `project-review`.

## Required First Check

1. Resolve project root.
2. Inspect git status and diff.
3. Identify active Change Brief, Bug Brief, working-context, or relevant `.llm-wiki/log.md` entry.
4. Check verification evidence.
5. Check artifact registry and dashboard evidence when present.
6. If process risk is present, identify the lifecycle step and whether the failure is an artifact issue, lifecycle issue, context integrity issue, project skill rule gap, eval gap, or user-decision gap.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/flow-record.md`
- `../references/progress-dashboard.md`
- `../references/continuous-evolution.md`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md`

Workflow:

1. Resolve project root.
2. Inspect current git status and diff.
3. Identify active requirement, bug, working context, source, artifact, or dashboard context.
4. Check code risk and behavior correctness.
5. Check verification gaps.
6. Check scope drift against active/read-only/candidate/excluded scopes.
7. Check wiki drift.
8. Check artifact drift.
9. Check dashboard drift: existence, evidence support, Flow Record cards, risk visibility, verification claims, and language consistency.
10. Check Flow Record drift.
11. Check external bridge consistency.
12. Check project root and wiki placement when init/recovery occurred.
13. Check cross-session project continuity when prior context or previous chat state affects the work.
14. Use requesting-code-review as an additional quality pass when available, but keep this skill's findings-first output.
15. Include Lifecycle Quality and evaluator/Dolores trigger decision when process risk appears.
16. If the failure suggests a project skill rule gap, propose the smallest project-skill patch and an acceptance/eval case. Do not evaluate unrelated non-project skills here.
17. Report findings first, then open questions, verification gaps, context gaps, residual risk, and summary.

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
- Flow Record `done` step has no evidence
- `development` done but no changed files or implementation evidence
- `testing` done but no verification evidence or accepted limitation
- `archive` done but no handoff/release/done evidence
- same source/design document has duplicate active flow_id values
```

If no issues are found:

```text
Findings:
- No blocking or major issues found.

Verification gaps:
Context/wiki gaps:
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
- Do not run evaluator or Dolores for every ordinary review.
- Do not treat dashboard as a source of truth.
- Do not turn project-review into a general-purpose Dolores or skill-evaluator replacement.
- Do not rely on unrecorded chat memory as project source of truth; prefer `.llm-wiki/log.md`, working-context, artifacts, Change Briefs, and Bug Briefs.

## Common Mistakes

- Performing only code review and ignoring lifecycle state.
- Missing changed files outside active scope.
- Ignoring missing wiki/artifact/dashboard updates.
- Treating external bridge output as authoritative without scope checks.
- Turning Dolores into a generic summary.
- Missing wrong-root `.llm-wiki` writes or foreign project facts after project-init recovery.
- Reporting process failure without recommending the minimal project skill rule or acceptance-case improvement.
