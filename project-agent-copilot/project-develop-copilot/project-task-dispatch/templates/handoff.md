# {{handoff_title}}

{{handoff_summary}}

## {{destination_heading}}

{{destination_explanation}}

## {{execution_boundary_heading}}

{{execution_boundary}}

## {{dependency_heading}}

{{dependency_summary}}

## {{result_heading}}

Return a human-readable delivery checklist containing acceptance IDs, changed
files, actual tests/results, repository/branch/HEAD/local commit, risks,
blockers, and incomplete work. Normal commentary does not use JSON receipts.
Final is SUBMITTED evidence and remains subject to Manager Review.

## {{technical_appendix_heading}}

```yaml
dispatchId: "{{dispatch_id}}"
subtaskId: "{{subtask_id}}"
projectSessionKey: "{{project_session_key}}"
workItemIds: {{work_item_ids}}
role: "{{role}}"
writePolicy: "{{write_policy}}"
mode: "{{mode}}"
awaitResult: "{{await_result}}"
taskKind: "{{task_kind}}"
targetProject: "{{target_project}}"
routeMode: "{{route_mode}}"
environment: "local"
codexProjectId: "{{codex_project_id}}"
hostId: "{{host_id}}"
repositoryRoot: "{{repository_root}}"
expectedBranch: "{{expected_branch}}"
baselineHead: "{{baseline_head}}"
dirtyBoundary: {{dirty_boundary}}
contractRevision: "{{contract_revision}}"
readOnlyFallback: "{{read_only_fallback}}"
targetWorkdir: "{{read_only_fallback_target_workdir_or_none}}"
allowNestedDelegation: false
createBranch: false
switchBranch: false
createWorktree: false
merge: false
rebase: false
reset: false
push: false
dependencies:
{{dependency_list}}
deliveryProtocol: "{{delivery_protocol}}"
expectedOutput: "development-delivery-checklist"
```

Writable work is valid only with `routeMode=VERIFIED_CODEX_PROJECT`.
`BASE_PATH_FALLBACK` is allowed only with `writePolicy=READ_ONLY`,
`readOnlyFallback=true`, and an explicit target workdir.
