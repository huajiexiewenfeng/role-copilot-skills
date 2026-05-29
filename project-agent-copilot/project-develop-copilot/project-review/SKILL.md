---
name: project-review
description: Use when reviewing project changes for code risk, test gaps, requirement consistency, scope drift, stale context, LLM Wiki sync, tool-bridge consistency, or readiness before commit, PR, or merge.
---

# Project Review

## Purpose

Review project work for correctness, scope, verification, and context consistency before handoff, commit, PR, or merge.

This skill uses a review stance. Findings come first and are ordered by severity.

## Review Inputs

Use available evidence:

- git diff
- changed files
- tests and verification output
- active requirement or bug summary
- active working context page
- `.llm-wiki` updates
- source material and acceptance criteria

## Required Shared References

Read these references when relevant:

- `../references/north-star.md`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md` when Superpowers-style review skills are available.

## Workflow

1. Resolve `project_root`.
2. Inspect current git status and diff.
3. Identify active requirement, bug, or source context when present.
4. Check:
   - correctness and behavior risks
   - scope drift
   - missing tests or verification
   - stale or missing `.llm-wiki` updates
   - stale or missing working-context status
   - cross-scope contract risks
   - accidental unrelated file changes
5. Use requesting-code-review as an additional quality pass when available, but keep this skill's findings-first output format.
6. Report findings first.
7. Include open questions, residual risks, and suggested fixes.

## Review Checklist

Code risk:

- changed behavior matches requirement or bug summary
- no unrelated files or modules were modified
- active scopes match changed files
- read-only scopes were not modified without escalation

Verification:

- tests, compile, lint, or manual checks are recorded
- skipped verification has an explicit reason
- verification covers changed behavior or residual risk is stated

Wiki drift:

- related requirement or bug page status matches the change
- working-context status matches implementation state
- affected module summaries are updated when behavior or contracts changed
- source proxy status is updated when a source was implemented, superseded, or invalidated

Tool-bridge consistency:

- Superpowers/OpenSpec-style outputs did not override source code, tests, user decisions, or original source materials
- external tool output stayed inside active/read-only scopes
- scope escalation is recorded when external output required broader scope
- codegraph output, if used, is treated as read-only supporting context

## Severity

- `blocker`: likely incorrect behavior, unsafe scope expansion, missing verification for risky change, or source-of-truth conflict.
- `major`: meaningful bug risk, incomplete wiki sync, missing test for important behavior, or unclear cross-scope contract.
- `minor`: small maintainability, documentation, or handoff issue.

## Output

Use this format:

```text
Findings:
- [severity] file/path:line - issue

Open questions:

Verification gaps:

Context/wiki gaps:

Summary:
```

If no issues are found, say:

```text
Findings:
- No blocking or major issues found.

Verification gaps:
Context/wiki gaps:
Residual risk:
Summary:
```

## Safety

- Do not rewrite code during review unless the user asks for fixes.
- Do not bury blocking findings under summaries.
- If no issues are found, say so and mention remaining test or context risk.
