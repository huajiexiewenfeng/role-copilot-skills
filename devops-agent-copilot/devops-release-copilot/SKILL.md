---
name: devops-release-copilot
description: Use this skill when acting as the DevOps Agent Copilot for release preparation after images are built, especially requests like "发布 v1.3.1", "准备 v1.3.1 部署目录", "更新 docker compose", "同步镜像号", "把刚打包的镜像更新到 compose", or "检查 application 环境变量并补到 compose". The skill prepares versioned release directories from a version number, creates missing target version folders, copies docker-compose YAML from the nearest previous version when needed, maps packaged tar/manifest image tags to deployment files, updates Docker Compose YAML safely, compares application configuration placeholders with compose environment variables, verifies diffs, and summarizes release handoff artifacts without deploying or pushing unless explicitly requested.
---

# DevOps Release Copilot

## Purpose

Prepare versioned release handoff changes after build artifacts or Docker images exist.

This skill belongs to the DevOps Agent Copilot role. It does not replace packaging, CI, deployment, or production release systems. It helps Codex prepare version directories, copy baseline deployment files from the nearest previous version, update deployment files from known release artifacts, keep Docker Compose image tags aligned, and ensure required runtime environment variables are visible in compose files.

## Relationship To Packaging

Use `devops-package-copilot` for building images and tar bundles.

Use this skill after packaging, or when the user directly asks to update release/deployment files. If the user asks to both build and update deployment files, run the packaging workflow first, then use this skill for the deployment-file update.

## Session Context

Track release context inside the current conversation/session:

- `project_root`
- `release_base`
- `target_version_dir`
- `source_version_dir`
- `deploy_root`
- `version`
- `modules`
- `image_tags`
- `tar_bundle`
- `release_dir`
- `manifest_path`
- `compose_files`
- `updated_files`
- `env_sync_scope`
- `last_branch`
- `last_commit`

Reuse context only inside the same session. When the user changes `project_root`, `deploy_root`, or `version`, re-read files and do not mix old release context with the new one.

## Workflow

1. Identify release intent.
   - Examples: update compose image versions, sync release tags, prepare deployment handoff, check environment variables.
2. Resolve critical paths.
   - `project_root`: usually the built project.
   - `release_base`: parent directory that contains version folders, for example `deploy`.
   - `target_version_dir`: the directory for the requested version, for example `deploy\v1.3.1`.
   - `deploy_root`: directory inside the version folder that contains deployment files such as `*.yml` or `*.yaml`.
   - If a path is missing and cannot be inferred from session context, ask for it.
3. Prepare the version directory.
   - Search under `release_base` for a folder whose name exactly matches the requested version, such as `v1.3.1`.
   - If the target version folder does not exist, create it.
   - Search the target deployment path for `*.yml` and `*.yaml`.
   - If no compose files exist in the target deployment path, find the nearest previous version folder under the same `release_base` and copy its deployment files or deployment subtree into the target version folder.
   - Preserve subpaths such as `服务器+工控机\cloud` when the user points to that subdirectory.
4. Resolve modules and version.
   - Prefer the latest build manifest when available.
   - If the user mentions a tar bundle, read the adjacent `build-manifest.json` when present.
   - Otherwise use modules and version explicitly named by the user.
   - Never update unrelated services just because their tags look old.
5. Inspect deployment files.
   - Search only under the requested deployment directory unless the user says otherwise.
   - Locate matching `image:` lines for each requested module.
   - Update stable release tags such as `<imageBaseName>-release:<version>`.
6. Synchronize runtime environment variables when requested or naturally implied by the release update.
   - Compare application configuration placeholders with each service's compose `environment`.
   - Add missing variables with defaults only when they can be read from application configuration.
   - Do not overwrite existing compose values.
   - For the detailed compose workflow, read `references/compose-sync-workflow.md`.
7. Verify.
   - Confirm the target version directory exists.
   - Confirm compose files exist in the target deployment path.
   - Re-read changed compose lines.
   - Run `git diff` in the deployment repository if it is a Git worktree.
   - Confirm no unintended init/job images were changed.
8. Report.
   - List target version directory and whether it was created or reused.
   - List source version directory if files were copied from a previous version.
   - List updated files.
   - List image tags changed.
   - List environment variables added.
   - Mention skipped or ambiguous items.

## Image Tag Rules

Prefer stable release tags in deployment files:

```text
<imageBaseName>-release:<version>
```

Do not switch compose files to timestamp tags unless the user explicitly asks. Timestamp tags are useful for traceability and tar contents, but deployment compose files normally use stable release tags.

When a build manifest contains both:

```text
stream-gateway-20260603-113327:v1.3.1
stream-gateway-release:v1.3.1
```

update compose to:

```text
stream-gateway-release:v1.3.1
```

## Minimal Questions

Ask only for missing critical values:

- Deployment directory is unknown.
- Version is unknown and cannot be inferred from a target directory, tar name, build manifest, or session version.
- The release base contains no previous version folder to copy from and the target version has no compose files.
- Version is unknown and no build manifest or session version exists.
- Requested service name does not match project module config or compose services.
- Multiple compose files contain plausible matches and the intended target is unclear.
- Environment variable defaults are required but no application config can be found.

Do not ask whether to inspect application configuration when the user says environment variables should be synchronized; inspect it.

## Safety

- Do not deploy, restart services, run `docker compose up`, push images, or publish release artifacts unless explicitly requested.
- Do not update unrelated image tags.
- Do not overwrite existing compose environment values.
- Do not delete deployment files, old release artifacts, Docker images, generated tar files, or previous version directories.
- Do not copy from a later version into an earlier target version unless the user explicitly chooses that source.
- Preserve user edits in dirty worktrees. If unrelated files are modified, leave them alone.
- If a compose value conflicts with an application default, keep the compose value and report the difference.

## Common User Requests

```text
把刚刚打包的 stream-gateway v1.3.1 更新到 D:\deploy\cloud 下的 compose 文件
```

```text
stream-gateway mission-data elevation-service 镜像打完后，同步 docker compose 镜像号
```

```text
如果新增镜像有环境变量变动，也从 application 配置文件同步到 compose
```

```text
准备 v1.3.1 发布部署文件，只更新 release tag，不部署
```

```text
通过版本号 v1.3.1 准备发布目录；如果没有目录就创建，如果没有 yml 就从最近版本复制，再更新本次 tar 镜像包里的版本号
```
