---
name: project-review
description: Use when reviewing project changes for code risk, test gaps, requirement consistency, scope drift, stale context, LLM Wiki sync, or readiness before commit, PR, or merge.
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

Read `../references/superpowers-bridge.md` when Superpowers-style review skills are available.

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

## Safety

- Do not rewrite code during review unless the user asks for fixes.
- Do not bury blocking findings under summaries.
- If no issues are found, say so and mention remaining test or context risk.
