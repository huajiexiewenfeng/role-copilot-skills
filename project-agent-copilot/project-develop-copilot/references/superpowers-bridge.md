# Superpowers Bridge

Use this reference to combine Project Develop Copilot with Superpowers-style skills without mixing responsibilities.

## Boundary

Project skills own:

- project root resolution
- `.llm-wiki` indexes and summaries
- source ingestion and source proxies
- scoped working context
- active, read-only, candidate, and excluded code scopes
- finish sync and wiki drift checks

Superpowers-style skills own:

- brainstorming
- writing plans
- test-driven development discipline
- systematic debugging
- executing implementation plans
- verification before completion
- requesting or receiving code review

Do not let Superpowers-style skills choose project scope from scratch. Run project context recovery first, then invoke Superpowers inside the active scope.

## Bridge Points

| Project entry | Superpowers bridge |
|---|---|
| `project-develop` | After Context Enrichment Gate, use brainstorming and writing-plans when available. Use test-driven-development before implementation when the change is code-facing. Use executing-plans when a written plan exists. |
| `project-fix` | After bug evidence and scoped context are captured, use systematic-debugging. Use test-driven-development when creating regression coverage is feasible. |
| `project-finish` | Before claiming completion, use verification-before-completion when available, then sync verified facts to `.llm-wiki`. |
| `project-review` | Use code-review stance. When requesting-code-review is available, use it as an additional quality pass, then report findings in project-review format. |

## Context Handoff

Before invoking Superpowers-style skills, provide this handoff:

```text
Project root:
Requirement or bug:
Active sources:
Active scopes:
Read-only scopes:
Excluded scopes:
Working context:
Acceptance criteria or expected behavior:
Known facts:
Gaps:
```

## Return Handoff

After Superpowers-style work, update project context:

- requirement or bug summary status
- working-context status and scope escalation log
- module summaries when behavior or contracts changed
- source proxy status when source interpretation changed
- `.llm-wiki/log.md` for meaningful lifecycle events

## Safety

- Do not invoke implementation planning before project context recovery.
- Do not use Superpowers output to override source code, tests, user decisions, or original requirement sources.
- Do not expand active scopes just because a plan suggests it; require evidence or user confirmation.
- Do not write long Superpowers reasoning transcripts into `.llm-wiki`; store summaries, decisions, status, and gaps.
