# Lifecycle Gates

Lifecycle Gates are the executable checkpoints that keep Project Develop Copilot from becoming a set of disconnected skills. A gate is not a ceremonial heading. It is a rule for what must be known, recorded, or explicitly limited before the lifecycle can move forward.

## Gate Principles

- Run the lightest gate that keeps the next action safe.
- Do not silently skip an owned gate.
- If a gate cannot be completed, record the limitation and the next safest action.
- Gate output should be short, structured, and recoverable.
- Gates protect lifecycle state; they should not become long user forms.

## Gate Table

| Gate | Required before | Minimum output | Default owner |
|---|---|---|---|
| Lightweight Answer Boundary | any project-related response | lightweight vs full lifecycle decision | router |
| Context Discovery Gate | any full lifecycle work | project root, new/stale context signals, relevant `.llm-wiki` availability | router, `project-init`, `project-ingest` |
| Lifecycle Session Gate | feature/bug/finish/review work | Change Brief, Bug Brief, working-context, or explicit reason none exists | router |
| Routing Record Gate | full lifecycle entry | short routing record in lifecycle session or `.llm-wiki/log.md` | router |
| Context Enrichment Gate | planning, debugging, implementation, scoped review | active sources, relevant wiki pages, active/read-only/candidate/excluded scope | `project-develop`, `project-fix`, `project-review` |
| Clarification Gate | requirement planning or implementation | goal, acceptance criteria, non-goals, scope, open questions | `project-develop` |
| Bug Evidence Gate | bug diagnosis or fix | symptom, expected behavior, evidence, reproduction status, severity | `project-fix` |
| Context Lock Gate | executing a plan or editing code | locked scope, accepted assumptions, escalation rule | `project-develop`, `project-fix` |
| External Skill Bridge Gate | calling external skills/tools | Context Handoff and expected Return Handoff | router, stage skill |
| Verification Gate | finish, done claim, review readiness | command/result/limitation/manual evidence/residual risk | `project-finish`, `project-review` |
| Verification Provenance Gate | promoting verification to done/verified, accepting limitations, pre-merge readiness | executor/raw output/exit code/authority/trust level | `project-finish`, `project-review` |
| Test Integrity Gate | production-code changes with test changes, mocks, or changed expectations | test diff risk, mock scope, assertion strength, coverage loss, independent check need | `project-review`, `project-finish` |
| Knowledge Sync Gate | finish or accepted state update | updated requirement/bug/module/source summaries | `project-finish` |
| Artifact Sync Gate | finish/review/dashboard update | artifact registry entries for important plans/reports/specs/dashboards | `project-finish`, `project-review` |
| Progress Dashboard Sync Gate | progress page update or review | dashboard facts linked to evidence | `project-finish`, `project-review` |
| Review Gate | before handoff, commit, PR, merge, broad testing | findings-first review or explicit no-finding statement | `project-review` |
| Evolution Gate | lifecycle quality review | evaluator or Dolores trigger decision and artifact suggestion | router, `project-review` |

## Gate Details

### Lightweight Answer Boundary

Use this gate before any project-related response. It decides whether the user wants a lightweight answer or a full lifecycle entry.

Minimum decision:

```markdown
- mode: lightweight-answer | full-lifecycle | lifecycle-quality
- reason:
- upgrade_trigger:
```

Do not write this record to disk for ordinary lightweight answers unless the user asks to save the discussion.

### Context Discovery Gate

Minimum output:

```markdown
- project_root:
- wiki_status: exists | missing | stale | unknown
- new_or_stale_context:
- likely_sources:
- limitation:
```

If project root is unknown and cannot be inferred, ask one minimal question.

### Lifecycle Session Gate

Minimum output:

```markdown
- session_type: change-brief | bug-brief | working-context | none
- session_path:
- status:
- reason:
```

A full feature or bug lifecycle should not proceed without a session unless there is an explicit reason and a safer temporary record in `.llm-wiki/log.md`.

### Routing Record Gate

Minimum format:

```markdown
## Routing

- intent:
- primary_stage:
- secondary_bridges:
- confidence:
- reason:
- next_gate:
- routed_at:
```

Record conclusions, not long reasoning.

### Context Enrichment Gate

Minimum output:

```markdown
- active_sources:
- relevant_wiki_pages:
- active_scope:
- read_only_scope:
- candidate_scope:
- excluded_scope:
- stale_context:
- next_gate:
```

Do not deep-read every document or module by default.

### Clarification Gate

Minimum output:

```markdown
- requirement_summary:
- acceptance_criteria:
- non_goals:
- active_scope:
- open_questions:
- ready_to_plan: yes | no | with-assumptions
```

If the user asks only to discuss, do not force a formal plan.

### Bug Evidence Gate

Minimum output:

```markdown
- symptom:
- expected:
- evidence:
- reproduction_status: reproduced | not-reproduced | blocked
- likely_scope:
- severity:
- safe_next_action:
```

Do not make broad code changes when evidence is missing unless the user explicitly accepts the risk.

### Context Lock Gate

Minimum output:

```markdown
- locked_active_scope:
- locked_read_only_scope:
- locked_candidate_scope:
- locked_excluded_scope:
- accepted_assumptions:
- escalation_rule:
```

Changing locked scope, accepted assumptions, or acceptance criteria requires scope escalation or plan deviation.

### External Skill Bridge Gate

Context Handoff:

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

Return Handoff:

```markdown
## Return Handoff

- stage_or_bridge_used:
- result_summary:
- changed_assumptions:
- recommended_scope_changes:
- artifacts:
- verification_notes:
- lifecycle_updates_needed:
- next_gate:
```

External skills are bridges, not lifecycle owners.

### Verification Gate

Minimum output:

```markdown
- verification_status: passed | failed | partial | blocked | not-run
- commands_or_manual_checks:
- result_summary:
- limitation:
- residual_risk:
```

Do not claim full completion when verification is partial, blocked, or not run.

Verification records are evidence, not authority. Do not treat an agent-written verification note as independently trustworthy unless the provenance is recorded by the Verification Provenance Gate.

### Verification Provenance Gate

Use this gate whenever verification affects lifecycle status, dashboard status, handoff readiness, commit/PR readiness, or a done/verified claim.

Minimum output:

```markdown
- verification_status: passed | failed | partial | blocked | not-run
- executor: agent-local | ci | human | external-reviewer | unknown
- command_or_check:
- raw_output_ref:
- exit_code:
- scope:
- authority: agent-local | ci-backed | human-accepted | reviewer-accepted | none
- trust_level: agent-local | ci-backed | reviewed | user-accepted-limitation | blocked
- limitation_acceptor:
- residual_risk:
```

Rules:

- Agent-authored summaries alone are not sufficient verification evidence. Prefer raw command output, test report files, CI URLs, review notes, or captured manual-check evidence.
- `accepted limitation` requires a non-agent acceptor: user, project owner, CI policy, or external reviewer. An agent may propose a limitation, but must not self-accept it.
- If the acceptor is missing, treat the state as `partial`, `blocked`, or `limitation proposed`, not `done`.
- Local agent-run tests may support `passed-agent-local`, but should not be promoted to final pre-merge confidence without CI, external review, or explicit user acceptance.

### Test Integrity Gate

Use this gate when implementation changes include tests, mocks, fixtures, expected values, assertions, snapshots, or verification helpers.

Minimum output:

```markdown
- production_changes:
- test_changes:
- mocks_or_fixtures_changed:
- assertions_added_or_removed:
- expected_behavior_changed:
- coverage_or_scope_reduced:
- over_mocking_risk: low | medium | high | unknown
- independent_verification_needed: yes | no
- conclusion:
```

Rules:

- If production code and tests changed in the same work, inspect whether tests still exercise real behavior.
- Flag tests that only assert mocks, remove meaningful assertions, loosen expectations, delete coverage, or encode changed behavior without requirement evidence.
- Passing tests with high over-mocking risk are not enough for `verified`; mark the trust level as `agent-local` or `needs-review`.
- Do not use new mocks or rewritten expectations to explain away a failing verification command without recording the risk and independent check needed.

### Knowledge Sync Gate

Minimum output:

```markdown
- updated_pages:
- status_changes:
- decisions_recorded:
- gaps_recorded:
- limitation:
```

Do not copy long raw source content into `.llm-wiki`.

### Artifact Sync Gate

Minimum artifact row:

```markdown
| id | type | path | owner | related_session | status | last_checked | notes |
|---|---|---|---|---|---|---|---|
```

Register important specs, plans, reports, dashboards, review notes, verification logs, generated diagrams, and external skill outputs.

### Progress Dashboard Sync Gate

Minimum output:

```markdown
- dashboard_path:
- changed_sections:
- evidence_links:
- stale_or_missing_evidence:
- limitation:
```

Dashboard state must trace back to `.llm-wiki`, artifact registry, verification records, or git diff evidence.

### Review Gate

Minimum checks:

```markdown
- code_risk:
- test_gap:
- requirement_or_bug_consistency:
- scope_drift:
- wiki_drift:
- artifact_drift:
- dashboard_drift:
- bridge_consistency:
- lifecycle_quality:
```

Findings should lead. If no findings, say what was checked and what residual risk remains.

### Evolution Gate

Minimum output:

```markdown
- evaluator_needed: yes | no
- dolores_review_needed: yes | no
- reason:
- suggested_case_or_eval:
- blocking: yes | no
```

Default blocking is `no`. Enter improvement mode only when the user asks or when a high-risk process failure must be handled before continuing.

## Common Gate Failures

- Treating gates as decorative headings.
- Asking long forms when one minimal question would resolve the gate.
- Running external skills before scoped context exists.
- Updating dashboard without evidence.
- Marking work done with partial verification but no limitation.
- Letting the same agent create weak verification evidence and then self-accept it as final.
- Treating an `accepted limitation` as valid when no user, CI policy, owner, or external reviewer accepted it.
- Marking tests as verified after changing mocks or expectations without a Test Integrity Gate check.
- Saving raw sensitive content instead of summaries and source proxies.
- Creating new lifecycle sessions instead of resuming existing ones.
