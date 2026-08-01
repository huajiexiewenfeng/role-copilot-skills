# Bug Brief: pdc-project-task-dispatch-receipt-envelope

## Summary

- title: Project Task Dispatch Receipt Envelope Is Not Deterministic
- status: completed
- bug_id: `pdc-project-task-dispatch-receipt-envelope`
- parent_flow_id: `pdc-project-task-dispatch-control-plane`

## Symptom

Real child tasks returned semantically complete receipt fields, but some fields
were concatenated and one long task response was truncated before its receipt
footer. The coordinating task had to normalize the replies manually before the
control-plane reducer could accept them.

## Expected Behavior

Every tracked child response carries one bounded, versioned, machine-readable
receipt before optional human details. The parent extracts and validates the
receipt directly from raw task text without repairing formatting.

## Evidence

- Five real cross-project version queries completed successfully.
- Three replies concatenated YAML-like receipt fields.
- One long reply was truncated before its receipt footer.
- `task_control.py` accepts an already parsed mapping but has no raw-text
  envelope extractor.

## Scope

- active:
  - Define a versioned JSON receipt envelope with exact markers.
  - Require the envelope before optional human-readable details.
  - Parse one envelope deterministically from raw task text.
  - Reject missing, duplicate, truncated, malformed, oversized, or unsupported
    envelopes.
  - Allow explicitly tracked Dispatch results without Development commit/test
    requirements.
  - Add focused protocol and contract regression tests.
- excluded:
  - Databases, dashboards, workflow engines, or automatic synchronization.
  - Changes to routing, task-package transport, or Development final receipts.
  - A third user-facing dispatch mode.

## Diagnosis

The control plane defines semantic fields but not a canonical wire envelope.
Plain YAML-like prose is model-format-sensitive, a trailing receipt is vulnerable
to output truncation, and the reducer cannot consume raw thread text.

## Fix And Verification

- Add the regression tests first and verify they fail because the extractor and
  versioned schema do not exist.
- Implement the smallest JSON envelope extractor and schema update.
- Update the Skill and references to make tracked Dispatch an explicit flag,
  not a new mode.
- Run focused tests, the complete skill test collection, Skill validation, and
  scoped diff checks.

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | done | Real five-project dispatch outputs and current control-plane source | 2026-08-01 |
| design | done | Versioned receipt-first JSON envelope and tracked Dispatch flag | 2026-08-01 |
| plan | done | User approved the minimal fix | 2026-08-01 |
| development | done | Versioned receipt-first JSON envelope, raw-text parser, parent start action, and tracked Dispatch flag | 2026-08-01 |
| testing | done | Source 30/30, installed 32/32, directed parent 3/3, source and installed Skill validation, installed package build, JSON and scoped diff checks | 2026-08-01 |
| archive | done | This verified Bug Brief is the closure entry point; publication is recorded by Git history | 2026-08-01 |
