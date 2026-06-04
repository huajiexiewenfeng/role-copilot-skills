---
name: project-review
description: Use when reviewing project changes for code risk, test gaps, requirement consistency, scope drift, stale context, LLM Wiki sync, tool-bridge consistency, or readiness before commit, PR, or merge.
---

# Project Review

## Purpose

Review project work for correctness, scope, verification, lifecycle consistency, artifact drift, dashboard drift, and handoff readiness.

This skill uses a review stance. Findings come first and are ordered by severity.

## When to Use

Use when the user asks for:

- review, risk check, before commit, before PR, before merge, handoff readiness
- scope drift, wiki drift, artifact drift, or dashboard drift check
- lifecycle quality check after a project flow
- evaluator or Dolores trigger decision from project process risk

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

## Required First Check

1. Resolve project root.
2. Inspect git status and diff.
3. Identify active Change Brief, Bug Brief, working-context, or relevant `.llm-wiki/log.md` entry.
4. Check verification evidence.
5. Check artifact registry and dashboard evidence when present.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
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
9. Check dashboard drift.
10. Check external bridge consistency.
11. Use requesting-code-review as an additional quality pass when available, but keep this skill's findings-first output.
12. Include Lifecycle Quality and evaluator/Dolores trigger decision when process risk appears.
13. Report findings first, then open questions, verification gaps, context gaps, residual risk, and summary.

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

Summary:
```

If no issues are found:

```text
Findings:
- No blocking or major issues found.

Verification gaps:
Context/wiki gaps:
Artifact/dashboard gaps:
Lifecycle quality:
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

## Boundaries

- Do not rewrite code during review unless the user asks for fixes.
- Do not bury blocking findings under summaries.
- Do not report no findings without checking verification and lifecycle drift.
- Do not run evaluator or Dolores for every ordinary review.
- Do not treat dashboard as a source of truth.

## Common Mistakes

- Performing only code review and ignoring lifecycle state.
- Missing changed files outside active scope.
- Ignoring missing wiki/artifact/dashboard updates.
- Treating external bridge output as authoritative without scope checks.
- Turning Dolores into a generic summary.