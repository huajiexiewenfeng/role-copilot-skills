# Project Task Specification

> Supported task kinds: `discussion | design | development | test | review |
> deployment`. Replace every `{{...}}` token before preview. Preserve the
> requested task kind: a discussion or design task must not silently become a
> development task.

## Task Identity

```yaml
subtaskId: "{{subtask_id}}"
logicalProject: "{{logical_project}}"
taskKind: "{{task_kind}}"
objective: "{{task_objective}}"
```

## Current State

### Relevant source anchors

{{current_source_anchors}}

### Existing behavior and constraints

{{current_behavior}}

### Evidence confidence

{{project_evidence_confidence}}

## Problem and Target Behavior

### Problem

{{problem_statement}}

### Target behavior or requested result

{{target_behavior}}

## Owned Scope

{{owned_scope}}

## Excluded Scope

{{excluded_scope}}

## Components and Flow

{{components_and_flow}}

## Interfaces and Contracts

### Inputs

{{inputs}}

### Outputs

{{outputs}}

### API, event, and DTO details

{{interface_details}}

### Error semantics

{{error_semantics}}

## Data and State

### Data model

{{data_model}}

### State transitions and idempotency

{{state_transitions}}

## Configuration and Deployment

{{configuration_deployment}}

## Compatibility and Failure Semantics

{{compatibility_failure_semantics}}

## Upstream Dependencies

| Upstream subtask | Required result | Availability rule |
|---|---|---|
{{upstream_dependency_rows}}

## Downstream Consumers

{{downstream_consumers}}

## Shared Decisions That Cannot Be Redesigned Locally

{{frozen_shared_decisions}}

## Task-kind Instructions

- `discussion`: analyze and return decisions, unknowns, and recommendations; do
  not edit code unless a later user request changes the task kind.
- `design`: produce an executable technical design and contract differences; do
  not implement it.
- `development`: implement only the owned scope, run project-local tests, and
  create local commits according to the handoff.
- `test`: build or execute the requested project-local verification and report
  evidence; do not expand into unrelated fixes.
- `review`: inspect the supplied changes and return evidence-backed findings; do
  not mutate the project unless explicitly requested.
- `deployment`: perform or describe only the approved deployment operation and
  its validation, respecting the target environment authority.

## Project-local Verification

{{project_local_verification}}

No cross-project integration tests are required by default.

## Acceptance

{{project_acceptance}}

## Expected Deliverables

{{expected_deliverables}}
