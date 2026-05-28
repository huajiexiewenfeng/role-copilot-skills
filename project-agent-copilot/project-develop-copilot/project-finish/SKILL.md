---
name: project-finish
description: Use when finishing verified project work, syncing actual changes back to LLM Wiki, updating requirement or bug status, recording verification, and preparing handoff.
---

# Project Finish

## Purpose

Finish project work by syncing verified implementation knowledge back into `.llm-wiki` and preparing a concise handoff.

## Required Shared References

Read these role-level references:

- `../references/finish-mvp.md`
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
3. Summarize actual code and behavior changes.
4. Update only affected `.llm-wiki` pages:
   - `.llm-wiki/log.md`
   - related requirement summary
   - related bug summary
   - related module summary
   - related source proxy status
   - related working context status
5. Mark related `.llm-wiki/working-context/<change-id>.md` as verified, done, blocked, or skipped when one exists.
6. Record remaining gaps or skipped updates.
7. Report implementation summary, verification, wiki updates, and next action.

## Safety

- Do not claim work is complete without verification evidence or an explicit limitation.
- Do not write large implementation narratives into `.llm-wiki`.
- Do not update unrelated modules or sources.
