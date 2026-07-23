---
name: project-fix
description: Use when diagnosing or fixing a project bug, error, failed test, regression, incident, log symptom, or unexpected behavior with scoped project context and LLM Wiki bug summaries.
---

# Project Fix

## Purpose

Diagnose and fix bugs through scoped context, evidence, reproduction, implementation, verification, and bug knowledge sync.

This skill owns the bug stage of Project Develop Copilot. It does not own top-level routing, final completion claims, or broad review.

## When to Use

Use when the user reports or wants to fix:

- bug, error, exception, failed test, regression, incident, runtime symptom, unexpected behavior, or log evidence
- suspected bug in a scoped module or service
- bug work that may need systematic debugging, TDD, or verification bridges

## When Not to Use

- Do not use for feature requests without a bug symptom; use `project-develop`.
- Do not use for lightweight explanation of a log unless the user does not want lifecycle state.
- Do not use for final sync after a fix is complete; use `project-finish`.
- Do not use for merge-readiness review; use `project-review`.

## Owned Gates

- Context Recovery Gate
- Lifecycle Anchor Gate
- Work Definition Gate
- Scope Lock Gate
- External Bridge Gate
- Verification Gate before fix completion claims

## Initialization Gate

Run after resolving the project root and before any lifecycle or source work in this child.

- `wiki_required: true`
- `on_missing_wiki: route project-init`
- `pending_primary_stage: project-fix`
- Preserve the user's original request as `pending_intent`.
- If `<project_root>/.llm-wiki/` is absent, stop and return a Context Handoff to `project-init`; resume only after the router receives initialization readiness and a supported next gate.
- Do not create a partial `.llm-wiki/`, Bug Brief, working-context, test, or code change inside this child as a substitute for initialization.

On the missing-wiki branch, emit this minimal handoff:

```text
bootstrap_handoff:
  project_root: <resolved project root>
  pending_intent: <preserved user request>
  pending_primary_stage: project-fix
  requested_stage_or_bridge: project-init
  current_gate: Initialization Gate
```

## Required First Check

1. Resolve project root.
2. Run the Initialization Gate before resolving child references or creating lifecycle state.
3. Resolve optional shared references from `../references/` or local `references/`. If `bug-brief.md`, `flow-record.md`, or `scoped-working-context.md` is missing, continue in degraded mode using the minimum rules in this skill; report the missing deep references and keep bug evidence, scope, and Flow Record updates conservative.
4. Create or resume Bug Brief.
5. Capture or ingest external bug source.
6. Identify active, read-only, candidate, and excluded scopes.
7. If the bug involves external calls, upstream/downstream services, Feign, MQTT, HTTP, RPC, shared DB, or shared config, check Project Graph pins/edges/candidates and perform the cross-project boundary check before relying on external contract behavior.
8. Run Work Definition Gate before broad diagnosis or edits.

## Core Process

Read as needed:

- `../references/north-star.md`
- `../references/lifecycle-gates.md`
- `../references/bug-brief.md`
- `../references/project-graph.md`
- `../references/cross-project-refs.md`
- `../references/base-graph.md`
- `../references/flow-record.md`
- `../references/session-digest.md`
- `../references/scoped-working-context.md`
- `../references/tool-bridge.md`
- `../references/superpowers-bridge.md`
- `../references/templates.md`

Reference availability policy:

- Shared references are deep references, not startup requirements.
- Do not stop solely because `../references/` is missing.
- In degraded mode, require a minimal Bug Brief before edits: symptom, expected behavior, evidence, reproduction status, likely scope, fix plan, verification plan, and `bug_id` or `flow_id`.
- Do not mark diagnosis, fix, or verification complete unless evidence exists.

## Anti-Corruption Debugging Rule

Historical bug notes, dead-end records, session digests, and wiki findings are useful clues, but stale or provisional notes cannot close root-cause analysis. Treat `freshness-expired`, `stale-source-anchor`, `coarse-stale-source-anchor`, `missing-verified-commit`, `unreachable-verified-commit`, `unverifiable-anchor`, `dirty_at_capture`, and `needs_commit_resolution` as clue-only signals.

Confirm the suspected cause against current logs, source code, tests, configuration, or runtime evidence before using it as the reason for a fix. If current evidence contradicts the wiki, prefer current evidence and mark the wiki item for re-verification.

Workflow:

1. Resolve project root and Bug Brief.
2. Capture source, symptom, expected behavior, evidence, and likely scope.
3. Search `.llm-wiki/session-digests/` entries for related recall context such as symptoms, failed attempts, suspected root causes, reproduction notes, and verification history. Use them as bug evidence only when selected digest items were explicitly promoted or reconfirmed.
4. Mark stale or conflict digest items before relying on them.
5. Create or update the Bug Brief Flow Record with source evidence.
6. Run Context Recovery Gate.
7. If the bug crosses service/project boundaries, check Project Graph evidence in order: `.llm-wiki/cross-refs/index.md` pin -> `.llm-wiki/project-graph/edges.md` -> `.llm-wiki/project-graph/candidates.md`.
   - If a pin matches, follow `edge_id`; do not treat pin fields as contract facts.
   - If only a candidate matches, it is a clue only; perform source verification before using it for a fix decision.
   - If no edge or candidate exists, suggest manual registration via `project-maintain graph-register` only after the fix evidence is clear enough.
   - If a registry mapping is missing, ask for the local path. With Base Graph available, write Base Graph `.llm-wiki/registry.local.json` after confirmation; without Base, write only current project `.llm-wiki/registry.local.json`.
   - Before reading remote wiki or source, output a cross-project boundary check with `scope: read-only`.
   - If the fix decision depends on the remote contract, use `verification_required: source`.
   - Use an external edge for fix decisions only when it is `source-verified`, not stale, and directly relevant to the bug. If it is stale, `wiki-checked`, `draft`, `blocked`, or candidate-only, re-verify source or treat it as risk.
   - Do not base edits on `wiki-checked`, `draft`, stale, blocked, or candidate-only evidence.
   - Record remote evidence in the Bug Brief `## External Findings` section with `project_id`, `edge_id`, evidence, verification status, conclusion, impact, and suggested handoff.
   - Do not write external project files or Base tracked files from a business-project bug session.
8. Reproduce the issue or state why reproduction is not currently possible.
9. Bridge to systematic-debugging only after evidence and scoped context are captured.
10. Diagnose likely cause before changing code and update the Flow Record `design` step when diagnosis evidence exists.
11. Use test-driven-development for regression coverage when feasible.
12. Record or confirm the fix plan and update the Flow Record `plan` step before edits.
13. Run Scope Lock Gate before edits.
14. If the fix needs candidate or excluded scope, run scope escalation before editing.
15. Fix only active scopes unless escalation is justified.
16. Verify the fix or record limitation.
17. Update Bug Brief, Flow Record, and working-context after verification.
18. Return diagnosis, verification, Flow Record updates, external findings, residual risk, and next gate.

## Mode / Entry Selection

| Mode | Use when |
|---|---|
| `evidence-intake` | symptom or log exists but scope/reproduction is unclear |
| `reproduction` | issue needs a command, test, or manual steps |
| `diagnosis` | evidence exists and likely cause must be found |
| `fix` | scope is locked and user asked to fix |
| `verification` | fix exists and result must be checked |

## Inputs

- Bug Brief or bug id
- log, error, failed test, incident report, or user description
- project root
- active and candidate scopes
- Session Digests when they contain related recall context; use as bug evidence only after explicit promotion or current confirmation
- recent changes or git diff when relevant

## Outputs

Final report:

```text
Diagnosis:
Fix:
Files changed:
Scope escalation:
External findings:
Regression coverage:
Verification:
Bug Brief updates:
Flow Record updates:
Artifacts:
Residual risk:
Next action:
```

## Context Handoff

Before systematic-debugging, TDD, or other external bridges, provide:

```markdown
## Context Handoff

- lifecycle_session:
- user_intent:
- active_sources:
- active_scope:
- read_only_scope:
- candidate_scope:
- excluded_scope:
- current_gate:
- requested_stage_or_bridge:
- constraints:
```

## Return Handoff

After debugging, fixing, or verification, return:

```markdown
## Return Handoff

- stage_or_bridge_used: project-fix
- result_summary:
- changed_assumptions:
- recommended_scope_changes:
- artifacts:
- verification_notes:
- external_findings:
- lifecycle_updates_needed:
- next_gate:
```

## Boundaries

- Do not patch randomly before diagnosis.
- Do not expand write scope without evidence or user confirmation.
- Do not let systematic-debugging own project scope.
- Do not claim fixed without verification or explicit limitation.
- Do not copy sensitive raw logs into `.llm-wiki`.
- Do not edit remote project wiki, source, config, or registry during cross-project evidence gathering. Generate a context handoff if remote project changes are needed.

## Common Mistakes

- Jumping straight into external debugging without Bug Brief.
- Editing candidate scope before escalation.
- Treating reproduction-blocked as reproduced.
- Forgetting residual risk when verification cannot run.
- Updating dashboard as fixed before verification evidence exists.
- Making fix decisions from `wiki-checked` external evidence when the remote contract needs source verification.
