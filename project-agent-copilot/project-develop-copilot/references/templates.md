# Templates

## Source Proxy

```markdown
# Source: <name>

## Source

- type:
- path/url:
- captured_at:
- processing_mode:

## Summary

## Key Points

## Related

- requirements:
- bugs:
- modules:

## Gaps

## Next Action
```

## Requirement Summary

```markdown
# Requirement: <change-id>

## Source Artifacts

## Summary

## Scope

## Out of Scope

## Acceptance Criteria

## Active Context

## Status

## Related
```

## Working Context

```markdown
# Working Context: <change-id>

## Purpose

## Active Scopes

## Read-Only Scopes

## Excluded Scopes

## Source Context

## Cross-Scope Contracts

## Scope Escalation Log

## Verification Plan

## Status
```

## Bug Summary

```markdown
# Bug: <bug-id>

## Source

## Symptom

## Expected

## Scope

## Diagnosis

## Fix

## Verification

## Related
```

## Progress Dashboard Starter

Use `progress-dashboard-template.html` when creating:

```text
.llm-wiki/dashboard/progress.html
```

Minimum facts to fill during init:

```text
projectName:
stage: init | refresh
lastUpdated:
activeScope: project
progress: 0
summary:
nextAction:
evidence:
```

Keep visible labels in the detected project/user language. Preserve paths, lifecycle ids, status ids, and command names in their original form.
