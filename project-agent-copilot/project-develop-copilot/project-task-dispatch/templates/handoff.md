# {{handoff_title}}

{{handoff_summary}}

## {{destination_heading}}

{{destination_explanation}}

## {{execution_boundary_heading}}

{{execution_boundary}}

## {{dependency_heading}}

{{dependency_summary}}

## {{result_heading}}

{{expected_output_human_readable}}

## {{technical_appendix_heading}}

```yaml
dispatchId: "{{dispatch_id}}"
subtaskId: "{{subtask_id}}"
mode: "{{mode}}"
awaitResult: "{{await_result}}"
taskKind: "{{task_kind}}"
sessionProject: "{{session_project}}"
targetProject: "{{target_project}}"
targetWorkdir: "{{target_workdir}}"
routeMode: "{{route_mode}}"
environment: "local"
codexProjectId: "{{codex_project_id_or_none}}"
hostId: "{{host_id_or_none}}"
currentBranchPolicy: "keep-current-branch"
createBranch: false
switchBranch: false
createWorktree: false
push: false
dependencies:
{{dependency_list}}
deliveryProtocol: "{{delivery_protocol}}"
documentCount: 3
expectedOutput: "{{expected_output_machine_readable}}"
```
