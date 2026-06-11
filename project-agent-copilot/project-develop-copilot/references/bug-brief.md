# Bug Brief

Read `flow-record.md` when changing bug lifecycle state.

Bug Brief is the lifecycle session for bug, incident, regression, failed test, runtime error, log symptom, or unexpected behavior work.

It is lighter than a full requirement spec, but it must preserve enough evidence, scope, diagnosis, fix plan, verification, and residual risk for another agent to resume safely.

## Default Path

```text
.llm-wiki/bugs/<bug-id>.md
```

Use a stable, human-readable bug id when possible:

```text
YYYY-MM-DD-short-symptom
```

## Minimum Template

```markdown
# Bug Brief: <bug-id>

## Summary

- title:
- status: draft | triaged | reproduced | diagnosed | planned | ready | executing | verified | done | blocked
- flow_id: <bug-id>
- severity:
- owner:
- updated_at:

## Routing

- intent:
- primary_stage:
- secondary_bridges:
- confidence:
- reason:
- next_gate:
- routed_at:

## Source

- path/url/log/user_report:
- source_proxy:
- sensitivity:

## Symptom

## Expected

## Evidence

## Reproduction

- status: reproduced | not-reproduced | blocked
- command_or_steps:
- observed:
- expected:
- limitation:

## Scope

- active:
- read_only:
- candidate:
- excluded:
- escalation_history:

## Diagnosis

## External Findings

- project-id:
- xref-id:
- evidence:
- verification_status:
- derived_staleness:
- conclusion:
- impact_on_current_project:
- suggested_handoff:

## Fix Plan

## Verification

- status: passed | failed | partial | blocked | not-run
- commands_or_checks:
- result_summary:
- limitation:
- residual_risk:

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | pending |  |  |
| design | pending |  |  |
| plan | pending |  |  |
| development | pending |  |  |
| testing | pending |  |  |
| archive | pending |  |  |

## Artifacts

## Open Questions

## Residual Risk
```

## Status Rules

| Status | Meaning |
|---|---|
| `draft` | Bug is reported but not yet triaged. |
| `triaged` | Symptom, source, and likely scope are recorded. |
| `reproduced` | Reproduction is available or evidence is strong enough to proceed. |
| `diagnosed` | Likely cause is identified with evidence. |
| `planned` | Fix plan exists but execution is not confirmed or not started. |
| `ready` | Scope, plan, and risk are clear enough to execute. |
| `executing` | Fix is in progress. |
| `verified` | Fix has verification evidence but may still need finish/review sync. |
| `done` | Finish sync and review readiness are complete or explicitly accepted. |
| `blocked` | Progress requires user input, missing access, missing environment, or accepted limitation. |

## Bug Evidence Gate

Before broad diagnosis or code edits, record:

```markdown
- symptom:
- expected:
- evidence:
- reproduction_status:
- likely_scope:
- severity:
- safe_next_action:
```

If reproduction is blocked, explain the limitation and choose the safest next action.

## External Findings Rules

Use `## External Findings` when a bug may cross into another project through Feign, MQTT, HTTP, RPC, shared DB, shared config, or another integration point.

Rules:

- Start from `.llm-wiki/cross-refs/index.md` when a cross-project integration point may be involved.
- Use logical `project-id` and `xref-id`; do not persist local paths.
- Store evidence from the remote project as wiki-relative or source-relative anchors, not copied remote content.
- `verification_status` must be one of `draft`, `wiki-checked`, `source-verified`, or `blocked`.
- Do not write `stale` as a status. Use `derived_staleness: fresh | expired | unknown`.
- If the fix decision depends on the remote contract, require `source-verified` evidence before editing active scope.
- If only `wiki-checked` evidence exists, record the finding as a clue or risk and do not make fix decisions from it alone.
- If the remote project must change, create a context handoff for that project instead of editing it from the current lifecycle session.

## Scope Rules

- Start with the narrowest active scope supported by evidence.
- Put suspected but unproven modules in `candidate` or `read_only`.
- Do not edit read-only, candidate, or excluded scope without scope escalation.
- Record escalation reason before expanding active scope.
- If a debugging bridge recommends new scope, route that recommendation through Return Handoff before editing.

## External Debugging Bridge

Systematic debugging and similar skills are bridges. They receive Context Handoff and return Return Handoff.

They must not:

- choose project scope from scratch
- bypass Bug Evidence Gate
- edit outside active scope without escalation
- declare the bug fixed without Verification Gate

## Verification Rules

Bug work is not done until verification is recorded or the user explicitly accepts a limitation.

Use:

```markdown
- verification_status:
- commands_or_checks:
- observed_result:
- limitation:
- residual_risk:
```

Partial verification can support handoff, but the final response must not claim full completion.

## Flow Record Rules

Bug work uses the same Flow Record model as requirements:

```text
source -> design/diagnosis -> plan/fix direction -> development -> testing -> archive
```

Mapping:

- `source`: user report, log, failed test, incident note, or source proxy
- `design`: diagnosis or behavior decision
- `plan`: fix plan
- `development`: changed files or implementation summary
- `testing`: reproduction/verification evidence
- `archive`: handoff, done note, or accepted limitation

Do not mark `testing` or `archive` as `done` without verification evidence or explicit accepted limitation.

## Common Mistakes

- Treating a log as enough to edit broad code without scope.
- Starting systematic-debugging before Bug Brief exists.
- Not distinguishing reproduced, not-reproduced, and blocked.
- Expanding from one service to another without evidence.
- Updating wiki or dashboard as if the fix is verified when tests did not run.
- Saving sensitive raw logs instead of source proxies and summaries.
