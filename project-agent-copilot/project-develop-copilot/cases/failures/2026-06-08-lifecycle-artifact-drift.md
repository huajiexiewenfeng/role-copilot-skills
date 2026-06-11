# Failure Case: Lifecycle Artifact Drift After Cross-Module Implementation

## Date

2026-06-08

## Trigger

A media-file compatibility task started in `dji-dock3-adapter` and later expanded into a minimal `mission-data` private-event implementation.

## What Failed

1. The final implementation handoff was written under `.llm-wiki/working-context/` instead of `.llm-wiki/handoff/`.
2. The `mission-data` implementation got an execution plan but no child Change Brief / requirement page.
3. The locally installed child `project-develop` skill referenced `../references/*.md`, but the `references/` directory was missing.
4. The first dashboard refresh listed the child requirement only in Document Evidence / `dashboardData.evidence`, but did not project the child Flow Record into the visible Development Flow Board lanes.

## Why It Matters

- Dashboard and artifact registry links drifted away from the real handoff location.
- The mission-data work could not be cleanly associated with a Flow Record until after the fact.
- Missing references made the agent infer Flow Record rules from existing wiki pages instead of reading the canonical protocol.
- The dashboard hid child-flow progress even though the child Flow Record existed, making the board disagree with the project lifecycle source of truth.

## Expected Future Behavior

- `project-develop` must stop before writing an execution plan unless the Change Brief exists and contains `flow_id`, scope, acceptance criteria, non-goals, and `## Flow Record`.
- If scope expansion creates a meaningful child deliverable, create a child Change Brief with `parent_flow_id` before writing the child execution plan.
- `project-finish` must write final handoff artifacts under `.llm-wiki/handoff/` and update Flow Record, artifact registry, and dashboard links to that path.
- Any child stage skill must resolve optional shared references before lifecycle work. If missing, continue in degraded mode using the minimum embedded workflow, report the missing deep references, and avoid unsupported template-specific or projection-specific claims.
- `project-query dashboard-refresh` must project every distinct parent and child `flow_id` into the visible board and `dashboardData.flowRecords`; child flows must not be collapsed into parent prose or evidence links only.

## Regression Checks

- Search generated artifacts for old handoff paths:
  - `.llm-wiki/working-context/*handoff*.md`
  - dashboard links pointing to `working-context/*handoff*.md`
- Search execution plans and verify each has a matching Change Brief:
  - `.llm-wiki/working-context/*execution-plan*.md`
  - `.llm-wiki/requirements/<flow-id>.md`
- Check child skill installation behavior:
  - direct child-skill install without `../references/` does not hard fail
  - degraded mode still requires documentation anchor, `flow_id`, scope, and evidence-backed updates
  - missing deep references are reported in the result
- After dashboard refresh, check child Flow Record projection:
  - every distinct `flow_id` from requirements/bugs/working-context appears in visible board cards
  - every child `flow_id` has matching `dashboardData.flowRecords`
  - lane count badges match visible cards
