# Docker Compose Sync Workflow

Use this reference when updating deployment `*.yml` or `*.yaml` files after release images are built.

## Inputs

Collect or infer:

- Project root that contains module configuration and application files.
- Release base directory that contains version directories, or a target version/deployment directory that can be used to infer it.
- Deployment root that contains compose files.
- Version, for example `v1.3.1`.
- Module names or image base names.
- Optional build manifest path, usually `release/<name-version-timestamp>/build-manifest.json`.
- Optional image tar bundle path, usually `images-<version>-<timestamp>.tar`.

## Prepare Version Directory

Use this flow before editing compose files when the user asks for a versioned release such as `v1.3.1`.

1. Identify the target version string exactly, including the leading `v`.
2. Resolve `release_base`.
   - If the user gives a path that already ends with the version, its parent is `release_base`.
   - If the user gives a deeper deployment subpath such as `deploy\v1.3.1\服务器+工控机\cloud`, walk upward until the version folder is found.
   - If the user gives only a parent path, search its immediate children for version folders.
3. Check whether `release_base\<version>` exists.
   - If it does not exist, create it.
   - Preserve any requested subpath under the version folder.
4. Search the target deployment path for compose files:
   - `*.yml`
   - `*.yaml`
5. If no compose files exist, find a source version folder to copy from.
   - Prefer the greatest semantic version lower than the target version.
   - Treat `v1.3.0` as lower than `v1.3.1`.
   - Ignore directories that do not parse as `vMAJOR.MINOR.PATCH` unless the user explicitly selects them.
   - Do not copy from a higher version unless the user explicitly requests it.
6. Copy the corresponding deployment subtree or compose files from the source version to the target version.
   - If the requested target is `v1.3.1\服务器+工控机\cloud`, copy `服务器+工控机\cloud` from the source version when present.
   - If the exact subpath does not exist in the source version, stop and ask which source path to use.
   - Do not overwrite existing target compose files without telling the user and getting confirmation.

Report whether the target directory was reused or created, and which source version was copied.

## Locate Image Tags

Prefer manifest data when available:

- `module`
- `imageBaseName` or `releaseImage`
- `dockerContext`
- `modulePath`
- `jarPath`

If there is no manifest, read module config such as `scripts/modules.json` and map requested module names to `imageBaseName`.

When the user references a tar bundle, infer the manifest path from the same release directory:

```text
release\drone-cloud-api-v1.3.1-20260603-113327\
  images-v1.3.1-20260603-113327.tar
  build-manifest.json
```

Use `build-manifest.json` as the source of module names and release image tags. Do not inspect the tar unless the manifest is missing or unreliable.

If only the tar exists and the manifest is missing, use `docker load --input` only when the user explicitly permits loading images into Docker. Otherwise ask for the manifest or module list.

Search deployment files under the requested deployment root:

```text
*.yml
*.yaml
```

Match image lines conservatively:

```text
image: <imageBaseName>-release:<oldVersion>
```

Update only matched services for requested modules.

## Avoid False Positives

Do not update names that merely contain the module name but are different images.

Example: when updating `stream-gateway-release:v1.3.1`, do not update:

```text
stream-gateway-init-release:v1.3.0
```

unless the user explicitly requested the init image.

## Environment Variable Sync

Environment sync is a completion gate for every updated Java/Spring service unless the user explicitly asks to update image tags only. Do not report the release update as complete until application placeholders have been compared with the compose service environment and every missing variable is either added or reported as skipped with a reason.

For each updated Java/Spring service:

1. Locate application configuration files under the module path:
   - `src/main/resources/application.properties`
   - `src/main/resources/application-*.properties`
   - `src/main/resources/application.yml`
   - `src/main/resources/application-*.yml`
   - `src/main/resources/application.yaml`
   - `src/main/resources/application-*.yaml`
2. Extract non-commented Spring-style placeholders:
   - `${ENV_NAME:default}`
   - `${ENV_NAME}`
3. Ignore commented lines.
4. Compare extracted `ENV_NAME` values with the compose service's `environment` entries.
5. Add missing variables using the default from application config.
6. If no default exists, add an empty value only when the project convention already uses explicit empty values. Otherwise report it as needing review.
7. Never overwrite existing compose values.
8. Keep legacy compose variables when they may still be consumed by older code, but still add the new placeholders required by the updated service.
9. Report variables in four groups: added, already present, skipped because no default was available, and skipped because service/module mapping was ambiguous.

Use compose-specific operational values when already present. For example, if compose has:

```text
MYSQL_HOST=${HOST_IP:-192.168.0.160}
```

do not replace it with the application default.

## Service Matching

Match compose service blocks by one of these signals:

- The service block contains `image: <imageBaseName>-release:<tag>`.
- The service name clearly maps to the requested module.
- The user explicitly names the compose service.

If multiple blocks match, stop and ask which one to update.

## Verification

After editing:

1. Confirm the target version directory exists.
2. Confirm compose files exist in the target deployment path.
3. Re-scan compose files for requested image names.
4. Confirm the new release tag is present.
5. Confirm known non-target images stayed unchanged.
6. Re-run the application-vs-compose environment comparison for updated services.
7. Fail the verification mentally and continue editing if any mandatory placeholder is still absent from compose and not listed as skipped with a reason.
8. Show `git diff` for changed deployment files when available.

Report:

- Target version directory, and whether it was created or reused.
- Source version directory if compose files were copied.
- Files changed.
- Image tags updated.
- Environment variables added.
- Any variables intentionally left unchanged because compose already had a value.
- Any ambiguous or missing mappings.
