# Failure Case: Lifecycle Artifact Drift After Cross-Module Implementation

## Date

2026-06-08

## Trigger

A media-file compatibility task started in `dji-dock3-adapter` and later expanded into a minimal `mission-data` private-event implementation.

## What Failed

1. The final implementation handoff was written under `.llm-wiki/working-context/` instead of `.llm-wiki/handoff/`.
2. The `mission-data` implementation got an execution plan but no child Change Brief / requirement page.
3. The locally installed child `project-develop` skill referenced `../references/*.md`, but the `references/` directory was missing.

## Why It Matters

- Dashboard and artifact registry links drifted away from the real handoff location.
- The mission-data work could not be cleanly associated with a Flow Record until after the fact.
- Missing references made the agent infer Flow Record rules from existing wiki pages instead of reading the canonical protocol.

## Expected Future Behavior

- `project-develop` must stop before writing an execution plan unless the Change Brief exists and contains `flow_id`, scope, acceptance criteria, non-goals, and `## Flow Record`.
- If scope expansion creates a meaningful child deliverable, create a child Change Brief with `parent_flow_id` before writing the child execution plan.
- `project-finish` must write final handoff artifacts under `.llm-wiki/handoff/` and update Flow Record, artifact registry, and dashboard links to that path.
- Any child stage skill must verify the shared `references/` directory exists before lifecycle work. If missing, stop and instruct the user to install the top-level package or restore `references/`.

## Regression Checks

- Search generated artifacts for old handoff paths:
  - `.llm-wiki/working-context/*handoff*.md`
  - dashboard links pointing to `working-context/*handoff*.md`
- Search execution plans and verify each has a matching Change Brief:
  - `.llm-wiki/working-context/*execution-plan*.md`
  - `.llm-wiki/requirements/<flow-id>.md`
- Check child skill installation:
  - `project-develop/references/change-brief.md`
  - `project-finish/references/flow-record.md`
