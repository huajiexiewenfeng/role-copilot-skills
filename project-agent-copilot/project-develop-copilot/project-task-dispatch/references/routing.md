# Project Resolution and Routing 2.0

Project Graph identifies logical ownership and dependencies. Base Graph resolves
each repository identity and local root. Codex `list_projects` supplies saved
Project IDs, paths, hosts, and Git observations. A route is writable only when
all three sources corroborate one destination.

## Normalize and verify

Resolve Base Graph paths in documented precedence order, make them absolute,
normalize separators/case for the platform, and compare them with normalized
Codex Project paths. Never select by label alone.

For every route record:

```yaml
projectSessionKey: PS-api-worker
repositoryId: repo-api
repositoryRoot: D:/projects/api
projectId: opaque-saved-project-id
hostId: local
expectedBranch: feature/api-v2
baselineHead: 0123456789abcdef0123456789abcdef01234567
dirtyBoundary:
  mode: CLEAN | PRESERVE
  paths: []
  fingerprint: null
bindingState: UNBOUND | CREATE_PENDING | BOUND | MISSING
```

## VERIFIED_CODEX_PROJECT

Exactly one saved Project matches the Base Graph repository root. Create with:

```text
target.type = project
target.projectId = exact projectId
target.environment.type = local
```

Writable `WRITE` Project Worker Sessions require this route.

## BASE_PATH_FALLBACK

This is permitted only when all are true:

- the task is `READ_ONLY`;
- no exact saved Project exists;
- the user explicitly accepts fallback;
- `readOnlyFallback=true` is recorded;
- the prompt fixes `targetWorkdir` and prohibits writes.

It cannot be upgraded to Development. A later write request requires registering
or selecting an exact saved Project.

## BLOCKED

Use `BLOCKED` for no exact writable Project, ambiguous matches, missing path,
host mismatch, or repository identity conflict. Record a `PROJECT_ROUTE` blocker
with evidence, owner, and exit condition. Do not create a Worker in the Base
Graph Project to impersonate the target repository.

## Git preflight

Each repository owns its own branch and HEAD. Before assignment verify cwd, Git
root, `expectedBranch`, baseline relationship, and dirty boundary. Preserve
existing changes. Do not create/switch branches or worktrees and do not
merge/rebase/reset/push/clean without separate authorization.
