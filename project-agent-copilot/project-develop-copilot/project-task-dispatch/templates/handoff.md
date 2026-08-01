# Task Handoff

## Routing

```yaml
dispatchId: "{{dispatch_id}}"
subtaskId: "{{subtask_id}}"
mode: "{{mode}}"
awaitResult: "{{await_result}}"
taskKind: "{{task_kind}}"
routeMode: "{{route_mode}}"
sessionProject: "{{session_project}}"
targetProject: "{{target_project}}"
targetWorkdir: "{{target_workdir}}"
codexProjectId: "{{codex_project_id_or_none}}"
hostId: "{{host_id_or_none}}"
environment: "local"
```

Before acting, resolve `targetWorkdir` to an absolute path and confirm it equals
the routed project root. A mismatch is a blocker.

## Git Policy

```yaml
currentBranchPolicy: keep-current-branch
createBranch: false
switchBranch: false
createWorktree: false
push: false
```

For Development mode, inspect the current branch and working tree before editing.
Preserve pre-existing changes. Commit only task-owned changes. Stop if existing
changes overlap the same files or behavior.

## Dependencies

```yaml
dependencies:
{{dependency_list}}
upstreamResultsAvailable: "{{upstream_results_available}}"
```

Do not start until every required upstream result is available. Independent
tasks may run without waiting for unrelated dependency chains.

## Delivery Protocol

```yaml
deliveryProtocol: "{{delivery_protocol}}"
documentCount: 3
bundleChecksum: "{{bundle_checksum}}"
```

Do not begin execution until `TASK_PACKAGE_END` has arrived and all document and
bundle checksums are valid. Stop on a missing, duplicate, or reordered chunk.

## Expected Output

```yaml
expectedOutput: "{{expected_output}}"
```

- Dispatch with `awaitResult=false` returns the task-kind result directly to its
  owning Codex task; the parent does not track or validate a later receipt.
- Dispatch with `awaitResult=true` returns the receipt-first JSON envelope from
  `references/task-control-plane.md`; it requires no local commit or tests.
- Development mode returns the exact receipt defined in
  `references/development-receipt.md`.
- `NO_CHANGE_REQUIRED` must explain why no change is needed and must not create
  an empty commit.

## Execution Boundary

Work only inside `targetWorkdir` unless the package explicitly grants an
additional read-only evidence path. Do not modify the session project when using
`BASE_PATH_FALLBACK`.
