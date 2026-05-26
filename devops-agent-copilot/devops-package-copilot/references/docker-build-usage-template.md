# Docker Build Usage Template

Use this template when a project needs a clearer `docs/docker-build-usage.md` for DevOps Package Copilot.

The command and parameters in this file must reflect the real project script. Do not copy optional flags from other projects unless the script actually supports them.

```markdown
# Docker Build Usage

## Script Entry

Windows:

```bat
scripts\build.cmd
```

PowerShell implementation:

```text
scripts\build.ps1
```

Module config:

```text
scripts\modules.json
```

## Command Format

```bat
scripts\build.cmd -Modules <modules|ALL> -Version <version> [-SkipMaven] [-DryRun]
```

## Defaults

| Option | Default |
| --- | --- |
| SkipMaven | false |
| DryRun | false |
| Package type | temporary test package |

## Required Parameters

| Parameter | Required | Rule |
| --- | --- | --- |
| Modules | yes | module name, comma-separated module list, or ALL |
| Version | yes | format: vMAJOR.MINOR.PATCH |

## Optional Parameters

List only parameters that the script actually supports.

| Parameter | Rule |
| --- | --- |
| SkipMaven | Optional. Reuse existing jars and skip Maven. |
| DryRun | Optional. Validate config without running Maven or Docker. |

## Supported Modules

```text
drone-gateway
dock-api
stream-gateway
user-center
ALL
```

If `scripts\modules.json` exists, it is the strict source of truth for supported modules.

## Artifact Output

```text
release\<project-name>-<version>-<timestamp>\
images-<version>-<timestamp>.tar
build-manifest.json
```

## Common Commands

Single module:

```bat
scripts\build.cmd -Modules drone-gateway -Version v1.3.0
```

Multiple modules:

```bat
scripts\build.cmd -Modules dock-api,drone-gateway -Version v1.3.0
```

All modules:

```bat
scripts\build.cmd -Modules ALL -Version v1.3.0
```

Dry run:

```bat
scripts\build.cmd -Modules ALL -Version v1.3.0 -DryRun
```

## Safety Rules

- Do not push images by default.
- Do not deploy to production.
- Do not delete local or remote artifacts.
- Confirm the exact command before execution.
```
