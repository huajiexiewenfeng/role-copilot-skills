---
name: project-finish
description: Use when finishing verified project work, syncing actual changes back to LLM Wiki, updating requirement or bug status, recording verification, and preparing handoff.
---

# Project Finish

## Purpose

Finish project work by syncing verified implementation knowledge back into `.llm-wiki` and preparing a concise handoff.

## Required Shared References

Read these role-level references:

- `../references/north-star.md`
- `../references/finish-mvp.md`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md`
- `../references/llm-wiki-mvp.md`
- `../references/templates.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root.

## Workflow

1. Resolve `project_root`.
2. Confirm verification evidence:
   - tests passed
   - compile passed
   - lint passed
   - manual verification completed
   - or user accepted that verification could not be run
3. Use verification-before-completion when available before claiming completion.
4. Summarize actual code and behavior changes.
5. Map changed files to affected wiki pages.
6. Update only affected `.llm-wiki` pages:
   - `.llm-wiki/log.md`
   - related requirement summary
   - related bug summary
   - related module summary
   - related source proxy status
   - related working context status
7. Mark related `.llm-wiki/working-context/<change-id>.md` as verified, done, blocked, or skipped when one exists.
8. If verification was skipped, record the exact reason, user decision, and residual risk.
9. Record remaining gaps or skipped updates.
10. Report implementation summary, verification, wiki updates, and next action.

## Changed File Mapping

Map changed files before wiki sync:

```text
Changed file:
Module:
Related requirement:
Related bug:
Related source proxy:
Wiki pages to update:
Reason:
```

Rules:

- Code or contract behavior change: consider module summary and requirement or bug page.
- Test-only change: record verification and affected requirement or bug when relevant.
- Config/build change: record module or project-level note when it changes behavior.
- Source interpretation changed: update the related source proxy status.

## Source Proxy Status

Use:

- `implemented`: source requirement was implemented.
- `superseded`: newer source or user decision replaced it.
- `invalidated`: source no longer matches code or accepted behavior.
- `open`: source remains relevant but unfinished.

## Working Context Status

Use:

- `verified`: implementation is verified but may still need handoff.
- `done`: work is complete and handed off.
- `blocked`: work cannot finish; record blocker.
- `skipped`: no working-context update was needed; explain why.

## Safety

- Do not claim work is complete without verification evidence or an explicit limitation.
- Do not write large implementation narratives into `.llm-wiki`.
- Do not update unrelated modules or sources.
