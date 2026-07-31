# Shared Baseline

> This document is frozen and byte-identical across every child task in one
> dispatch batch. Replace every `{{...}}` token before preview. If a section does
> not apply, state `Not applicable` with the confirmed reason instead of deleting
> the section.

## Dispatch Metadata

```yaml
dispatchId: "{{dispatch_id}}"
designRevision: "{{design_revision}}"
confirmedAt: "{{confirmed_at}}"
parentProject: "{{parent_project}}"
```

## Parent Objective

{{parent_objective}}

### Required outcomes

{{required_outcomes}}

## Non-goals

{{non_goals}}

## End-to-end Architecture

### Participants

{{participants}}

### System flow

{{system_flow}}

### Dependency order

{{dependency_order}}

## Shared Contracts

### HTTP and RPC

{{http_rpc_contracts}}

### MQTT and asynchronous events

{{mqtt_event_contracts}}

### DTOs, enums, and errors

{{dto_enum_error_contracts}}

### Storage and artifact contracts

{{storage_artifact_contracts}}

Shared contracts in this section are frozen for all child tasks. A child may
report a conflict through its expected output, but must not redesign a shared
contract independently.

## Data and Naming Formats

{{data_date_file_object_key_formats}}

## Ownership Boundaries

| Logical project | Owned responsibilities | Explicit exclusions |
|---|---|---|
{{ownership_rows}}

## Confirmed Decisions

{{confirmed_decisions}}

## Evidence and Confidence

| Source | Revision or SHA-256 | Confidence | Notes |
|---|---|---|---|
{{evidence_rows}}

Evidence priority:

1. decisions confirmed by the user in the active conversation;
2. approved requirement or design documents;
3. fresh source-verified or runtime-verified Project Graph edges;
4. current source, tests, interfaces, and configuration;
5. Base Graph catalog and machine-local registry;
6. referenced chats and session summaries as clue-only context.

Label candidate, stale, unverified, or clue-only evidence. Never include
credentials, tokens, passwords, access keys, or unrelated environment data.

## Global Acceptance

{{global_acceptance}}

### Cross-project consistency

- Every project task uses the contracts and formats in this document.
- Ownership is mutually exclusive unless an explicit shared change is listed.
- Dependencies point to named outputs rather than informal assumptions.
- Dispatch mode ends after successful task delivery.
- Development mode completes only under the receipt rules in the handoff.
- Cross-project integration tests are outside the default acceptance scope.
