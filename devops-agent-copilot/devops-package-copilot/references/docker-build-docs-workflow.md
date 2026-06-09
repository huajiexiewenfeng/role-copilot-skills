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
| local prerequisites | sibling/framework install commands documented by the project |

If the docs are garbled because of encoding but command examples are readable, rely on command blocks, parameter names, module lists, and paths.

If project docs declare local prerequisites, such as installing sibling framework artifacts before packaging, treat them as project-owned build rules. Show the prerequisite command and reason before running it. Do not hard-code project names, sibling directories, or artifact coordinates in this skill.

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

Use `modulePath`, `jarPath`, and `dockerContext` for fallback decisions. Do not hard-code module names.

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

On Windows, quote every Maven `-D...=...` argument:

```powershell
mvn ... "-Dmaven.test.skip=true"
mvn ... "-Dmaven.repo.local=D:\path\to\repo"
```

Unquoted `-D` arguments can be split by PowerShell and surface as errors such as `Unknown lifecycle phase ".test.skip=true"`.

## Maven Reactor Fallback

Use this fallback only when all are true:

- The documented build script failed during Maven project reading or early reactor setup.
- The key error is about unresolved parent POMs, unresolved import POMs/BOMs, missing sibling module POMs, or `The build could not read ... projects`.
- The requested packaging scope is a single documented module, not `ALL`.
- The module config gives a `modulePath` and `jarPath`.
- The failure happened before a module-specific compile/test error for the requested module.

Do not use this fallback for real source compilation failures, test failures, Docker build failures, image export failures, unknown module names, or release/publish/deploy requests.

Fallback process:

1. Resolve requested module `modulePath`.
2. Find nearest ancestor at or above `modulePath` that has a `pom.xml` and lists the module or child path in `<modules>`.
3. Build from that narrower aggregator:

```powershell
mvn -f <nearest-aggregator>\pom.xml -pl <leaf-module-artifact-or-directory> -am clean package "-Dmaven.test.skip=true"
```

4. If this succeeds, confirm configured `jarPath` exists and `LastWriteTime` is newer than fallback build start time.
5. Run the documented script with documented `-SkipMaven` only if docs support it and the jar freshness check passed:

```bat
scripts\build.cmd -Modules <module> -Version <version> -SkipMaven
```

6. Final report must state the normal script Maven phase failed, list the fallback Maven command, and state `-SkipMaven` reused the newly built jar.

If the narrower Maven build fails, stop and report it. Do not continue to `-SkipMaven` with an old jar.

## Local Prerequisites

Some enterprise multi-repo workspaces require sibling framework or BOM projects to be installed into the local Maven repository before the target project can build. This is a project prerequisite, not a skill-specific rule.

Prefer project docs or module config to discover prerequisites. Acceptable forms include:

- `docs/docker-build-prerequisites.md`
- `docs/docker-build-guide.md`
- `scripts/modules.json`

Example module config shape:

```json
{
  "localPrerequisites": [
    {
      "reason": "Install shared BOM artifacts required by Maven dependency resolution",
      "cwd": "../shared-framework",
      "command": "mvn install -DskipTests"
    }
  ]
}
```

Before running a prerequisite command, show it unless it was already confirmed in the current session. After running it, retry only the original build or the Maven reactor fallback. Never invent prerequisites from memory; if source evidence suggests one, explain the evidence and suggest adding it to project docs/config.

## Failure Handling

When a build fails, report:

- failed phase if visible: Maven, Docker build, image export, manifest generation, or unknown
- exact command
- key error lines
- fallback commands attempted, if any
- likely next checks

Do not retry with different parameters unless the user asks or Maven reactor fallback criteria are satisfied.
