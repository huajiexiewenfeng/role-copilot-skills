# Docker Build Docs Workflow

## Goal

Read project-local `docs/docker-build-*.md` files and derive a safe packaging execution plan.

## Discovery

Given `project_root`, search:

```powershell
Get-ChildItem -LiteralPath "$project_root\docs" -Filter "docker-build-*.md" -File
```

Prefer a guide document when several files exist:

1. `docker-build-guide.md`
2. `docker-build-usage.md`
3. other `docker-build-*.md` files

Read all matching files when the guide and usage files appear complementary.

## Extracted Fields

Extract these facts from the docs:

| Field | Examples |
| --- | --- |
| script entry | `scripts\build.cmd` |
| script implementation | `scripts\build.ps1` |
| module config | `scripts\modules.json` |
| modules | `drone-gateway`, `dock-api`, `ALL` |
| version format | `vMAJOR.MINOR.PATCH`, `v1.3.0` |
| parameters | `-Modules`, `-Version`, `-SkipMaven`, `-Platform`, `-DryRun` |
| artifact directory | `release\<project>-<version>-<timestamp>\` |
| image archive | `images-<version>-<timestamp>.tar` |
| manifest | `build-manifest.json` |

If the docs are garbled because of encoding but command examples are readable, rely on command blocks, parameter names, module lists, and paths.

## Module Config

If the docs mention a module config file such as `scripts\modules.json`, read it when present. Use it to validate module names and discover artifact/image hints.

Expected shape:

```json
{
  "modules": {
    "drone-gateway": {
      "modulePath": "base-service/drone-gateway",
      "jarPath": "base-service/drone-gateway/target/drone-gateway.jar",
      "dockerContext": "docker/drone-gateway",
      "imageBaseName": "drone-gateway"
    }
  }
}
```

When both Markdown and module config exist, treat the module config as the stricter source for supported module names.

## Planning Rules

Use the docs as source of truth. If user intent conflicts with docs, explain the conflict and ask for confirmation or correction.

Derive command shape from docs. Common shape:

```bat
scripts\build.cmd -Modules <modules> -Version <version>
```

Only use parameters that are documented in `docs/docker-build-*.md`. Never invent or assume flags from other projects.

Omit optional flags unless required or explicitly requested:

- Omit `-SkipMaven` by default.
- Omit `-DryRun` by default.
- Use `-Platform` only when the project docs explicitly document it.

## Module Resolution

- If the user provides a module name and it appears in docs, use it.
- If the user says "打包 <name> 项目" and `<name>` appears in docs, use `<name>` as the module.
- If the user says "打全部", "全部模块", or "全量打包", use `ALL` only when docs mention `ALL` or `all`.
- If the requested module is not documented, ask whether to continue and point to the supported module list.

## Version Resolution

Version is critical. Ask when missing.

Accept versions that look like:

```text
v1.3.0
1.3.0
```

If docs require a leading `v`, normalize `1.3.0` to `v1.3.0` only after telling the user in the execution plan.

Do not carry over the previous version unless the user says "同版本", "再打一遍同版本", or equivalent.

## Git Context

Before confirmation, inspect Git state from `project_root`:

```powershell
git branch --show-current
git rev-parse --short HEAD
git status --short
```

Show branch and commit every time. If there are uncommitted changes, mention them. Do not block packaging unless the user or project docs require a clean tree.

## Execution

Run from `project_root`.

Use the exact script entry from docs. On Windows, prefer the documented `.cmd` entry when available because it may wrap PowerShell execution policy details.

Do not run until the user explicitly confirms the displayed command.

## Failure Handling

When a build fails, report:

- failed phase if visible: Maven, Docker build, image export, manifest generation, or unknown
- exact command
- key error lines
- likely next checks

Do not retry with different parameters unless the user asks.
