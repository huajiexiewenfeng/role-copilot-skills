---
name: project-develop
description: Use when developing a project requirement or feature with project-local context, scoped modules, active sources, LLM Wiki requirement summaries, implementation planning, or bridging Superpowers/OpenSpec-style planning inside scoped project context.
---

# Project Develop

## Purpose

Develop a feature or requirement from scoped project context into an implementation plan and, when the user confirms, into code changes.

This skill belongs to the Project Develop Copilot skill collection. It is one domain skill, not the whole project workflow suite. Use sibling skills for init, ingest, bug fixing, finish sync, and review.

## Source Of Truth

Use this authority order:

1. User's current request and explicit decisions.
2. Source code, tests, configuration, build files, and runtime evidence.
3. Original requirement sources such as PRD, issue, design doc, meeting notes, URL, PDF, Word, or Markdown.
4. `.llm-wiki` index and summaries.
5. Legacy `docs/ai-coding` or generated AI docs.

When sources conflict, name the conflict and prefer the highest authority source.

## Required Shared References

Read these role-level references as needed:

- `../references/develop-fix-mvp.md`
- `../references/scoped-working-context.md`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md`
- `../references/templates.md`
- `../references/llm-wiki-mvp.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root.

## Workflow

1. Resolve `project_root`.
2. Run Context Enrichment Gate before brainstorming or planning:
   - read `.llm-wiki/index.md` if present
   - read `.llm-wiki/modules/index.md` if present
   - read `.llm-wiki/ingest/index.md` if relevant
   - read the matching requirement page if one exists
   - read the matching `.llm-wiki/working-context/<change-id>.md` if one exists
   - discover unindexed source docs in configured source directories
   - select active, candidate, and excluded sources
   - select active, read-only, and excluded code scopes
3. Produce a context summary:
   - project root
   - active sources
   - candidate sources
   - active scopes
   - read-only scopes
   - excluded scopes
   - working context page, if used
   - known facts
   - assumptions
   - gaps or questions
4. If context is insufficient, ask only the smallest necessary question.
5. Bridge to Superpowers-style skills after context recovery when available:
   - brainstorming for requirement discussion
   - writing-plans for implementation planning
   - test-driven-development before code-facing implementation
   - executing-plans when a written plan exists
6. Create or update `.llm-wiki/requirements/<change-id>.md`.
7. Create or update `.llm-wiki/working-context/<change-id>.md` when the change spans multiple modules, uses multiple services, or needs scope escalation tracking.
8. Do not modify production code until the user confirms implementation or asks to proceed.

## Requirement Page Minimum

```markdown
# Requirement: <change-id>

## Summary

## Source Artifacts

## Scope

## Out of Scope

## Acceptance Criteria

## Active Sources

## Active Scopes

## Candidate Context

## Working Context

## Gaps

## Status
```

## Safety

- Do not pull all services in a monorepo into context by default.
- Do not use candidate or excluded modules as write scopes.
- Do not expand scope without evidence or user confirmation.
- Do not update legacy `docs/ai-coding` unless explicitly asked.
- Do not copy secrets or long original content into `.llm-wiki`.
