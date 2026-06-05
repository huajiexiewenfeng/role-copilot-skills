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
# Change Brief: <change-id>

## Summary

- title:
- status: draft | clarified | planned | ready | executing | done | blocked
- flow_id: <change-id>

## Sources

- 

## Scope

- active:
- reference-only:
- excluded:

## Acceptance

- 

## Plan

- active_plan:
- status: none | candidate | confirmed | stale
- evidence:

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | pending |  |  |
| design | pending |  |  |
| plan | pending |  |  |
| development | pending |  |  |
| testing | pending |  |  |
| archive | pending |  |  |

## Open Questions

- 

## Notes

- 
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
# Bug Brief: <bug-id>

## Summary

- title:
- status: draft | triaged | reproduced | diagnosed | planned | ready | executing | verified | done | blocked
- flow_id: <bug-id>
- severity:

## Source

## Symptom

## Expected

## Scope

## Diagnosis

## Fix

## Verification

## Flow Record

| Step | Status | Evidence | Updated |
|---|---|---|---|
| source | pending |  |  |
| design | pending |  |  |
| plan | pending |  |  |
| development | pending |  |  |
| testing | pending |  |  |
| archive | pending |  |  |

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
