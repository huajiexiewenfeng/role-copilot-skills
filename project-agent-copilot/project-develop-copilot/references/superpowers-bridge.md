# Superpowers Bridge

Use this reference to combine Project Develop Copilot with Superpowers-style skills without mixing responsibilities.

For the broader bridge contract across tools such as OpenSpec-style mechanisms and codegraph, see `tool-bridge.md`. Project-coding-skills is not bridged; its proven ideas are internalized as this collection's predecessor.

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
| `project-develop` | After Context Enrichment Gate and during Clarification Gate, naturally use brainstorming for requirement discussion before implementation planning. The user does not need to explicitly request brainstorming. Use writing-plans for implementation planning, test-driven-development before code-facing implementation, and executing-plans when a written plan exists. |
| `project-fix` | After bug evidence and scoped context are captured, use systematic-debugging. Use test-driven-development when creating regression coverage is feasible. |
| `project-finish` | Before claiming completion, use verification-before-completion when available, then sync verified facts to `.llm-wiki`. |
| `project-review` | Use code-review stance. When requesting-code-review is available, use it as an additional quality pass, then report findings in project-review format. |

## Brainstorming Modes

Brainstorming is a requirement clarification capability. It is not the project state system.

Change Brief is the project state system. Brainstorming outputs must be summarized back into `.llm-wiki/requirements/<change-id>.md`.

Use two modes:

### Light Mode

Default mode for `project-develop`.

Use brainstorming's discipline:

- understand user intent
- ask one high-value question at a time
- explore 2-3 viable approaches when useful
- discuss tradeoffs
- get confirmation before planning or implementation

But do not force a separate `docs/superpowers/specs/` file or git commit.

Write the result into Change Brief:

- summary
- scope
- acceptance
- non-goals
- plan status
- open questions

### Full Spec Mode

Use only when:

- the requirement is complex enough to need a standalone design spec
- the user asks for a spec
- the team has explicitly adopted `docs/superpowers/specs/`
- multiple subsystems need a reviewed design before planning

When full spec mode writes `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, register that spec as a source or plan-related artifact in the Change Brief. Do not let the spec become an unlinked parallel documentation track.

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
- Do not skip requirement clarification after ingest. Brainstorming belongs after scoped context recovery and before implementation planning.
- Do not make the user name Superpowers or brainstorming explicitly; bridge it when the discussion needs requirement exploration, tradeoff analysis, or scope clarification.
- Do not let brainstorming create unlinked parallel docs; summarize outputs into Change Brief.
- Do not force full spec mode for every feature.
- Do not use Superpowers output to override source code, tests, user decisions, or original requirement sources.
- Do not expand active scopes just because a plan suggests it; require evidence or user confirmation.
- Do not write long Superpowers reasoning transcripts into `.llm-wiki`; store summaries, decisions, status, and gaps.
