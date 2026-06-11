# Lifecycle Gates

Lifecycle Gates are the executable checkpoints that keep Project Develop Copilot from becoming a set of disconnected skills.

A gate is not a ceremonial heading. It is a rule for what must be known, recorded, or explicitly limited before the lifecycle can move forward.

## Gate Principles

- Run the lightest gate that keeps the next action safe.
- Do not silently skip an owned gate.
- If a gate cannot be completed, record the limitation and the next safest action.
- Gate output should be short, structured, and recoverable.
- Gates protect lifecycle state; they should not become long user forms.
- Prefer fewer gates with explicit sub-checks over many overlapping gate names.

## Gate Table

| Gate | Consolidates | Required before | Minimum output | Default owner |
|---|---|---|---|---|
| Lightweight Boundary | Lightweight Answer Boundary | any project-related response | lightweight vs read-only vs full lifecycle decision | router |
| Context Recovery Gate | Context Discovery, Context Enrichment | any full lifecycle, project query, init, ingest, maintenance, review, or scoped work | project root, wiki status, active sources, relevant pages, active/read-only/candidate/excluded scope | router, `project-init`, `project-query`, `project-ingest`, `project-develop`, `project-fix`, `project-maintain`, `project-review` |
| Lifecycle Anchor Gate | Lifecycle Session, Routing Record, Documentation Anchor | feature, bug, finish, review, handoff, or executable lifecycle work | Change Brief, Bug Brief, working-context, routing record, or explicit no-anchor reason | router, `project-develop`, `project-fix` |
| Work Definition Gate | Clarification, Bug Evidence | requirement planning, implementation planning, bug diagnosis, or fix | requirement goal/acceptance/non-goals or bug symptom/evidence/reproduction/severity | `project-develop`, `project-fix` |
| Scope Lock Gate | Context Lock | executing a plan or editing code | locked scope, accepted assumptions, escalation rule | `project-develop`, `project-fix` |
| External Bridge Gate | External Skill Bridge | calling external skills/tools | Context Handoff and expected Return Handoff | router, stage skills |
| Session Import Gate | Session Source, Sensitivity, Candidate Digest, Import Confirmation, Session Digest, Lifecycle Promotion | extracting or importing historical chat/session context | source, sensitivity, candidate digest, confirmation, promotion decision | `project-session-extract`, router |
| Verification Gate | Verification, Verification Provenance, Test Integrity | finish, done claim, review readiness, testing status, accepted limitation | command/manual result, raw evidence/provenance, test integrity risk, limitation acceptor, residual risk | `project-finish`, `project-review` |
| Finish Sync Gate | Knowledge Sync, Artifact Sync, Progress Dashboard Sync | finish or accepted state update | Flow Record update, wiki sync, artifact registry update, dashboard projection from evidence | `project-finish`, `project-query`, `project-maintain`, `project-review` |
| Review & Wiki Integrity Gate | Review, Evolution, Maintenance visibility/safety checks | before handoff/commit/PR/merge, lifecycle-quality review, wiki repair, dashboard/artifact drift checks | findings-first review, wiki visibility/safety findings, evaluator decision when needed | `project-review`, `project-maintain`, router |

## Gate Details

### Lightweight Boundary

Use this gate before any project-related response. It decides whether the user wants a lightweight answer, read-only project query, maintenance action, session import, or full lifecycle entry.

Minimum decision:

```markdown
- mode: lightweight-answer | read-only-query | wiki-maintenance | session-context-import | full-lifecycle | dashboard-refresh | lifecycle-quality
- primary_stage:
- reason:
- upgrade_trigger:
```

Rules:

- Do not write this record to disk for ordinary lightweight answers unless the user asks to save the discussion.
- Lightweight answers and read-only queries must not create Change Briefs, Bug Briefs, Flow Records, dashboard updates, or code changes by default.

### Context Recovery Gate

Minimum output:

```markdown
- project_root:
- wiki_status: exists | missing | stale | unknown
- active_sources:
- relevant_wiki_pages:
- active_scope:
- read_only_scope:
- candidate_scope:
- excluded_scope:
- stale_context:
- limitation:
- next_gate:
```

Rules:

- If project root is unknown and cannot be inferred, ask one minimal question.
- Do not deep-read every document or module by default.
- In degraded mode without shared references, recover only the evidence needed for the current action and report the limitation.

### Lifecycle Anchor Gate

Minimum output:

```markdown
- anchor_type: change-brief | bug-brief | working-context | log-only | none
- anchor_path:
- flow_id:
- routing:
  - intent:
  - primary_stage:
  - secondary_bridges:
  - confidence:
  - reason:
  - next_gate:
- reason:
```

Rules:

- Before production code, tests, configuration, public APIs, protocol methods, DTOs, topics, database schema, or user-visible behavior changes, require a documentation anchor unless the user explicitly requests throwaway/exploratory work.
- A full feature or bug lifecycle should not proceed without a Change Brief, Bug Brief, working-context page, or explicit safer temporary record.
- Do not write execution plans before the related Change Brief or Bug Brief exists and links to the same `flow_id`.

### Work Definition Gate

For requirement work, minimum output:

```markdown
- requirement_summary:
- acceptance_criteria:
- non_goals:
- active_scope:
- open_questions:
- ready_to_plan: yes | no | with-assumptions
```

For bug work, minimum output:

```markdown
- symptom:
- expected:
- evidence:
- reproduction_status: reproduced | not-reproduced | blocked
- likely_scope:
- severity:
- safe_next_action:
```

Rules:

- If the user asks only to discuss, do not force a formal plan.
- Do not make broad code changes when requirement or bug evidence is missing unless the user explicitly accepts the risk.

### Scope Lock Gate

Minimum output:

```markdown
- locked_active_scope:
- locked_read_only_scope:
- locked_candidate_scope:
- locked_excluded_scope:
- accepted_assumptions:
- escalation_rule:
```

Rules:

- Changing locked scope, accepted assumptions, or acceptance criteria requires scope escalation or plan deviation.
- Candidate and read-only scopes must not be edited without explicit escalation.

### External Bridge Gate

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

Rules:

- External skills are bridges, not lifecycle owners.
- External tool output must return through the lifecycle session before finish or dashboard projection.

### Session Import Gate

Minimum output:

```markdown
- session_source:
- source_type:
- sensitivity:
- candidate_digest:
- selected_items:
- not_imported:
- confirmation_status:
- lifecycle_promotion: none | proposed | confirmed
- written_digest:
- next_route:
```

Rules:

- Historical chat/session context becomes a Session Digest first.
- Do not copy raw transcripts by default.
- Do not update requirements, bugs, Flow Records, dashboard, scope, or project truth unless selected digest items are explicitly promoted.
- Sensitive content must be summarized or redacted.

### Verification Gate

Minimum output:

```markdown
- verification_status: passed | failed | partial | blocked | not-run
- executor: agent-local | ci | human | external-reviewer | unknown
- command_or_check:
- raw_output_ref:
- exit_code:
- scope:
- test_integrity:
  - production_changes:
  - test_changes:
  - mocks_or_fixtures_changed:
  - assertions_added_or_removed:
  - expected_behavior_changed:
  - over_mocking_risk: low | medium | high | unknown
- authority: agent-local | ci-backed | human-accepted | reviewer-accepted | none
- limitation_acceptor:
- residual_risk:
```

Rules:

- Do not claim full completion when verification is partial, blocked, or not run.
- Agent-authored summaries alone are not sufficient verification evidence. Prefer raw command output, test report files, CI URLs, review notes, or captured manual-check evidence.
- `accepted limitation` requires a non-agent acceptor: user, project owner, CI policy, or external reviewer.
- If production code and tests changed together, check whether tests still exercise real behavior and record over-mocking or weakened-assertion risk.

### Finish Sync Gate

Minimum output:

```markdown
- flow_id:
- flow_record_updates:
- wiki_updates:
- artifact_updates:
- dashboard_projection:
- handoff_path:
- unsupported_done_claims_downgraded:
- residual_risk:
```

Rules:

- Flow Record is the lifecycle status authority for a concrete requirement, bug, or working context.
- Artifact registry is the authority for artifact existence, path, owner, status, and discoverability.
- Dashboard is a projection generated from Flow Record, artifact registry, verification evidence, and selected log notes.
- Log is an audit trail, not a lifecycle status authority.
- Handoff is archive/continuation material, not a source that silently rewrites lifecycle status.
- Dashboard refresh must rebuild visible cards from Flow Records and artifact evidence, not create status facts.
- When dashboard or handoff disagrees with Flow Record, repair the projection or flag drift; do not silently change Flow Record to match stale projection.
- When Flow Record disagrees with current code, tests, verification evidence, or user decision, route through finish or review before changing done/verified status.

### Review & Wiki Integrity Gate

Minimum output:

```markdown
- findings:
- verification_gaps:
- context_wiki_gaps:
- artifact_dashboard_gaps:
- session_digest_gaps:
- lifecycle_quality:
- project_skill_improvement:
- residual_risk:
```

Rules:

- Review findings come first and are ordered by severity.
- Maintenance checks must keep repairs narrow and evidence-backed.
- Detect scope drift, wiki drift, artifact drift, dashboard drift, handoff path drift, and Session Digest promotion mistakes.
- Lifecycle-quality review should identify routing/gate failures and suggest the smallest useful project-skill patch or eval case.

## Owner Mapping

| Skill | Owned Gates |
|---|---|
| `project-develop-copilot` | Lightweight Boundary, Context Recovery Gate, Lifecycle Anchor Gate, External Bridge Gate, Session Import Gate, Finish Sync Gate, Review & Wiki Integrity Gate |
| `project-init` | Context Recovery Gate, Finish Sync Gate |
| `project-ingest` | Context Recovery Gate, Finish Sync Gate |
| `project-query` | Lightweight Boundary, Context Recovery Gate, Finish Sync Gate |
| `project-maintain` | Context Recovery Gate, Finish Sync Gate, Review & Wiki Integrity Gate |
| `project-develop` | Context Recovery Gate, Lifecycle Anchor Gate, Work Definition Gate, Scope Lock Gate, External Bridge Gate |
| `project-fix` | Context Recovery Gate, Lifecycle Anchor Gate, Work Definition Gate, Scope Lock Gate, External Bridge Gate, Verification Gate |
| `project-session-extract` | Context Recovery Gate, Session Import Gate, Finish Sync Gate |
| `project-finish` | Verification Gate, Finish Sync Gate |
| `project-review` | Verification Gate, Finish Sync Gate, Review & Wiki Integrity Gate |

## Completion Standard

The consolidated Gate set is complete when:

- the named Gate count is 10 or fewer
- child skill `Owned Gates` use only names from the Gate Table
- verification provenance and test integrity are sub-checks of Verification Gate
- knowledge, artifact, and dashboard sync are sub-checks of Finish Sync Gate
- dashboard is explicitly a projection, not a status source
- P0 evals still pass after the consolidation
