# Execution Report Format

## Before Execution

Use this confirmation format:

```markdown
I found packaging rules in:

- `docs/docker-build-guide.md`
- `docs/docker-build-usage.md`

Execution plan:

- Project root: `<path>`
- Branch: `<branch>`
- Commit: `<commit>`
- Working tree: `<clean | has local changes>`
- Modules: `<modules>`
- Version: `<version>`
- Package type: `<temporary test | release>`
- Defaults: full Maven + Docker build, no dry run
- Command: `<command>`

Confirm execution?
```

If the user asked for plan only, stop here and do not ask for execution confirmation.

For ordinary follow-up builds in the same session, use this no-confirmation format:

```markdown
Reusing the current packaging session:

- Project root: `<path>`
- Script: `<script>`
- Version: `<version>`
- Changed modules: `<modules>`
- Command: `<command>`

Starting build.
```

## Success Report

After a successful build, use:

```markdown
Build succeeded.

- Project root: `<path>`
- Modules: `<modules>`
- Version: `<version>`
- Command: `<command>`
- Artifact directory: `<release/...>` if found or inferred
- Image archive: `<images-...tar>` if found
- Manifest: `<build-manifest.json>` if found
- Next step: copy the tar to Linux and run `docker load -i <file>` if that is documented
```

Prefer concrete paths discovered from the filesystem over inferred paths.

## Failure Report

After a failed build, use:

```markdown
Build failed.

- Project root: `<path>`
- Modules: `<modules>`
- Version: `<version>`
- Command: `<command>`
- Failed phase: `<phase or unknown>`
- Key error: `<short error excerpt>`
- Suggested checks:
  1. ...
  2. ...
```

Keep failure reports concise. Preserve the command so the user can rerun or adjust it.

## Session Follow-Up

For follow-up requests, say what is being reused and what changed:

```markdown
Reusing the current packaging session:

- Project root: `<path>`
- Script: `<script>`
- Previous modules: `<old>`
- New modules: `<new>`
- Version: `<reused version>` or `<old -> new>`
```

Then show the normal execution plan only when confirmation is required. For ordinary follow-up builds, show the no-confirmation format and execute.
