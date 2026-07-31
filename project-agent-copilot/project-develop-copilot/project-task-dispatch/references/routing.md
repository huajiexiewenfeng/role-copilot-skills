# Project Resolution and Routing

Use Project Graph, Base Graph, and Codex Projects as corroborating evidence:

- Project Graph identifies logical ownership, contracts, and dependencies.
- Base Graph resolves the logical project to its machine-local registry path.
- Codex `list_projects` identifies saved project IDs, paths, hosts, and Git state.

Neither source alone is a complete execution route.

## Normalization

Resolve the Base Graph registry in its documented precedence order. Convert the
result to an absolute normalized path, normalize separators and case according to
the local platform, and resolve equivalent path syntax. Compare this normalized
path to the normalized path of each Codex Project.

Do not match by label alone. A route is verified only when exactly one Codex
Project has the same normalized path as the Base Graph root.

## VERIFIED_CODEX_PROJECT

Use this route when Base Graph and exactly one saved Codex Project identify the
same directory.

Record:

```yaml
routeMode: VERIFIED_CODEX_PROJECT
logicalProjectId: "{{logical_project_id}}"
baseGraphPath: "{{absolute_base_graph_path}}"
codexProjectId: "{{codex_project_id}}"
codexProjectLabel: "{{codex_project_label}}"
codexProjectPath: "{{absolute_codex_project_path}}"
hostId: "{{host_id}}"
isGitRepository: "{{is_git_repository}}"
```

Create the Codex task with:

```text
target.type = project
target.projectId = matched projectId
target.environment.type = local
```

In user-facing shorthand this is `environment.type = local`. The task runs in
the saved project's current checkout and current branch.

## BASE_PATH_FALLBACK

Use this route when Base Graph resolves an existing project root but
`list_projects` has no saved Codex Project with the same normalized path.

Record:

```yaml
routeMode: BASE_PATH_FALLBACK
sessionProject: "{{current_codex_project}}"
targetProject: "{{logical_target_project}}"
targetWorkdir: "{{absolute_base_graph_path}}"
```

Create the task under the current Codex Project in local mode. Put
`targetWorkdir` in the package as a mandatory execution boundary. The child:

1. resolves and compares the absolute path before acting;
2. runs all source, build, test, and Git commands from `targetWorkdir`;
3. verifies `git rev-parse --show-toplevel` for Git development work;
4. avoids modifying the session project;
5. stops if the directory is missing, inaccessible, or unexpected.

Serialize Development tasks that share the same fallback directory.

## BLOCKED

Use `BLOCKED` when:

- Base Graph cannot resolve the project root;
- registry evidence conflicts;
- several Codex Projects match the normalized path;
- the directory does not exist;
- the current Codex Project required for fallback cannot be resolved.

A batch containing a blocked route cannot be approved until the route is fixed
or the affected task is removed.

## Checkout and Branch Policy

- Keep the current checkout and current branch.
- Do not create a worktree unless the user explicitly requests one.
- Do not switch branches unless the user explicitly requests it.
- Do not create a branch, merge, rebase, reset, or push by default.
- Inspect branch and `git status` before Development work.
- Preserve unrelated dirty files.
- Stop when pre-existing changes overlap task-owned files or behavior.
- Consolidate one logical project into one task by default.
- Serialize explicitly separate tasks that use the same checkout.
