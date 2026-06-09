---
name: devops-package-copilot
description: Use this skill when acting as the DevOps Agent Copilot to package/build local projects from natural language, especially Chinese requests like "打包某个项目", "再打一次", "换个版本打包", or "打全部模块". The skill discovers project-local docs/docker-build-*.md rules, reuses session-scoped packaging context including the last confirmed version, asks only for missing critical values, avoids repeated confirmation for ordinary follow-up builds in the same session, runs existing local scripts, and summarizes build artifacts or failures.
---

# DevOps Package Copilot

## Purpose

Turn natural-language packaging requests into confirmed local script executions.

This skill belongs to the DevOps Agent Copilot role. It does not replace project build scripts. It reads project-local packaging documentation, builds an execution plan, asks for only critical missing information, and calls the existing script after user confirmation.

## Core Rule

Use project-local documentation as the source of truth:

```text
<project-root>/docs/docker-build-*.md
```

If no matching document exists, stop and ask the user for the packaging rules or the correct project path.

## Session Context

Maintain a packaging context inside the current conversation/session. Reuse it for follow-up requests like "再打一次", "换成 v1.3.1", "这次打 dock-api", or "打全部".

Track:

- `project_root`
- `rule_docs`
- `script_entry`
- `modules`
- `version`
- `package_type`
- `platform`
- `skip_maven`
- `dry_run`
- `last_branch`
- `last_commit`
- `last_command`
- `last_artifact_hint`

Only reuse context within the same session. When the user changes `project_root`, reload `docs/docker-build-*.md` and do not mix settings from the previous project.

After the user provides or confirms a version once, reuse that version for later builds in the same session by default. Change it only when the user explicitly provides a new version or asks to change the version. When the user changes `project_root`, clear the version and ask again.

Re-read branch and commit before every execution plan.

## Workflow

1. Identify the packaging intent and project name/module hints from the user request.
2. Resolve `project_root`.
   - Use the path provided by the user.
   - If missing and no session context exists, ask for the project path.
   - If missing but session context exists, reuse the current `project_root`.
3. Search `<project-root>/docs` for `docker-build-*.md`.
4. Read the matching docs and extract:
   - script entry, for example `scripts\build.cmd`
   - required parameters
   - supported modules
   - module config file, for example `scripts\modules.json`
   - version format
   - default platform
   - artifact output location
   - manifest/log hints
5. If the docs point to a module config file and it exists, read it to validate supported module names and artifact/image hints.
6. Apply defaults.
7. Ask only for missing critical values.
8. Read current Git branch and commit when the project is a Git repository.
9. Show the execution plan and exact command.
10. Decide whether confirmation is required.
11. Run the command when allowed by the confirmation policy.
12. If Maven fails before compiling the requested module because the root reactor cannot resolve unrelated parent POMs, imported BOMs, or sibling modules, use the Maven reactor fallback rules in `references/docker-build-docs-workflow.md` before giving up.
13. Summarize success, artifact locations, manifest/log hints, fallback commands used, or failure diagnosis.

For detailed parsing and reporting rules, read:

- `references/docker-build-docs-workflow.md`
- `references/execution-report-format.md`

## Defaults

Use these defaults unless project docs override them or the user explicitly says otherwise:

- `skip_maven`: `false`; do not add `-SkipMaven`.
- `dry_run`: `false`; do not add `-DryRun`.
- `package_type`: temporary test package.
- `version`: reuse the last confirmed session version unless the user provides a new version or switches project root.
- `modules`: if the user says "打包 <name> 项目" and `<name>` appears in supported modules, use `<name>` as the module.
- Multi-module or `ALL`: use only when the user explicitly asks for multiple modules or all modules.
- On Windows, quote Maven `-D...=...` arguments, for example `"-Dmaven.test.skip=true"` and `"-Dmaven.repo.local=..."`, so PowerShell does not split them into invalid lifecycle phases.

Never guess:

- `project_root`
- `version`
- unsupported module names
- release/publish actions
- script parameters that are not documented in `docs/docker-build-*.md`

## Minimal Questions

Ask only when needed:

- Missing project path and no session context exists.
- Missing version and no session version exists.
- Requested module is absent from docs.
- User asks for all modules but docs do not mention `ALL`.
- Multiple possible project roots or rule docs are ambiguous.

Do not ask about `SkipMaven` or `DryRun` during the normal path. Use defaults and show them in the execution plan only if the project docs document these parameters.

Never invent command parameters. The real packaging command must follow `docs/docker-build-*.md`. Only fill values into documented command shapes and documented flags.

## Confirmation Policy

For the first build of a project root in the current session, show:

```text
Project root:
Rule docs:
Branch:
Commit:
Modules:
Version:
Package type:
Defaults:
Command:
```

Then ask for confirmation.

For ordinary follow-up builds in the same session, do not ask for confirmation again. Show the reused context and command, then execute.

Ordinary follow-up builds are requests that:

- use the same `project_root`
- use the same documented script entry
- use the existing session version or a user-provided replacement version
- package a single documented module
- do not request release, publish, push, deploy, `ALL`, destructive cleanup, or optional behavior changes such as `-SkipMaven` or `-DryRun`

Confirmation is still required when:

- switching `project_root`
- first reading a new project's packaging rules
- packaging `ALL` or many modules
- building a release package
- pushing, publishing, or deploying
- using optional parameters that change build semantics
- running any command whose shape was not already shown in the current session

Do not execute from a guessed command.

## Safety

- Do not publish to production.
- Do not delete artifacts, Docker images, remote tags, or release files.
- Do not push images unless the user explicitly asks and the project docs support it.
- Do not run destructive cleanup commands as part of this skill.
- If the command fails, preserve the command and key error output. Do not retry blindly; only use documented fallback rules when the error matches the failure class.
- Do not use `-SkipMaven` after a failed Maven build unless a jar at the configured `jarPath` was created or refreshed during the current packaging attempt.

## Common User Requests

```text
打包 smart-go-file 项目，路径 D:\workspace\drone\develop\smartghub\drone-cloud-api，版本 v1.3.0
再打一次
这次打 dock-api
换成 v1.3.1 再打一次
打全部模块
只生成执行计划，不真正打包
```
