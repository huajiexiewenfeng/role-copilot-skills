# LLM Wiki Doctor

`llm_wiki_doctor.py` is the Project Develop Copilot validator, scorer, and Chinese-first report generator for repo-local `.llm-wiki` artifacts.

The skill source script lives at:

```text
project-agent-copilot/project-develop-copilot/scripts/llm_wiki_doctor.py
```

Consuming business projects should use the vendored copy installed by `project-init`:

```text
.llm-wiki/tools/llm_wiki_doctor.py
.llm-wiki/tools/VERSION
.pre-commit-config.yaml
.github/workflows/llm-wiki-doctor.yml
.llm-wiki/project-ids.json
```

The source repo keeps the consuming-project templates under:

```text
project-agent-copilot/project-develop-copilot/assets/llm-wiki-doctor-scaffold/
```

## Commands

Machine checks:

```text
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --all --phase normal --format text --fail-on error
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --changed --phase normal --format text --fail-on error
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --base origin/main --phase normal --format json --fail-on error
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --changed --phase finish --format text --fail-on error
```

Human diagnosis:

```text
python .llm-wiki/tools/llm_wiki_doctor.py report --root . --phase advisory --format text
python .llm-wiki/tools/llm_wiki_doctor.py score --root . --phase advisory --format json
```

`validate` is deterministic and may block on ERROR findings. `score` and `report` are advisory and always exit 0.

Use phases consistently:

- `advisory`: human diagnosis and maturity reporting.
- `normal`: pre-commit and CI blocking checks.
- `finish`: project-finish checks before archiving captured knowledge or handoff state.

Legacy no-subcommand invocations still map to `validate`, but new documentation and automation should use the explicit subcommand form.

## Checks

ERROR:

- `leaked-local-path`: committed `.llm-wiki` Markdown contains workstation paths or local-only registry names.
- `invalid-edge-id`: Project Graph Evidence references an edge id missing from `.llm-wiki/project-graph/edges.md`.
- `dangling-cross-ref`: `cross-refs/index.md` pins an edge id missing from `.llm-wiki/project-graph/edges.md`.
- `duplicate-edge-fingerprint`: confirmed edge fingerprints repeat.
- `contradictory-module-context`: `.llm-wiki/modules/index.md` marks a Maven module as ready/source-backed, but the scoped context directory or standard files are missing.
- `missing-source-refs`: captured/current knowledge lacks source references.
- `missing-verified-commit`: captured source references lack a verified commit.
- `unresolved-dirty-capture`: finish phase found dirty-captured knowledge that has not been resolved to a clean verified commit.
- `missing-edge-detail-id`: edge detail front matter lacks `edge_id`.
- `invalid-edge-detail-id`: edge detail front matter points to an unknown edge id.
- `duplicated-edge-detail-fact`: edge detail front matter duplicates canonical edge table facts such as project ids, topic, path, endpoint, verification status, or fingerprint.

WARN:

- `orphan-design-doc`: requirement, design, bug, or plan documents outside `.llm-wiki` are not registered by exact source path or `original_path`.
- `missing-graph-evidence`: cross-service `.llm-wiki` artifacts do not include `## Project Graph Evidence` or `## Project Graph Gaps`.
- `unresolved-project-id`: structured project fields reference ids not found in committed `.llm-wiki/project-ids.json`.
- `missing-origin`: a knowledge unit lacks origin metadata.
- `freshness-expired`: a knowledge unit has exceeded its kind-specific TTL.
- `unreachable-verified-commit`: a source reference points to a commit not reachable from the current repo.
- `stale-source-anchor`: a verified Java class/method/function span changed after the verified commit.
- `coarse-stale-source-anchor`: a coarse file/module source reference changed after the verified commit.
- `unverifiable-anchor`: a source reference is missing enough path/anchor metadata or uses an unsupported anchor type.
- `suspicious-confidence`: metadata claims human-confirmed confidence without `confirmed_by: human`.
- `missing-module-context`: root `pom.xml` enables a Maven module but `.llm-wiki/modules/<module>/` is missing.
- `incomplete-module-context`: `.llm-wiki/modules/<module>/` exists but is missing one or more standard scoped-context files.
- `thin-module-context`: all standard module context files exist, but they are still placeholder-only or too thin to guide real work.
- `missing-module-evidence`: all standard module context files exist, but they do not cite recognizable source anchors such as concrete files, classes, configs, endpoints, topics, tables, or tests.

For Maven aggregator projects, `score` and `report` also emit module coverage signals:

- `pom_module_count`
- `wiki_module_context_count`
- `missing_module_context_count`
- `missing_module_context_modules`
- `ready_module_context_count`
- `ready_module_context_modules`
- `thin_module_context_count`
- `thin_module_context_modules`
- `missing_module_evidence_count`
- `missing_module_evidence_modules`
- `module_context_ready_ratio`

Projects without root `<modules>` in `pom.xml` treat module-context coverage as not applicable.

## project-ids.json

The doctor reads project vocabulary from committed `.llm-wiki/project-ids.json`.

Example:

```json
{
  "local_projects": ["current-repo-project-id"],
  "projects": [
    {
      "id": "external-project-id",
      "aliases": ["old-name-or-runtime-name"]
    }
  ]
}
```

Rules:

- `projects` is the known project vocabulary.
- `local_projects` identifies projects that belong to the current repo and should not be treated as external just because their ids appear in text.
- `aliases` normalize old names or runtime names to canonical ids.
- Confirmed edges are used for edge-id validation only; do not derive project vocabulary from `edges.md`.
- `unresolved-project-id` scans structured fields only; it does not scan free prose.

## Scaffold Sync

From the skill source repo, sync the source script into the consuming-project scaffold:

```text
python project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py
python project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py --check
```

`--check` fails if the scaffolded doctor copy is stale or missing. Skill-source CI should run unit tests plus this drift check. Consuming-project CI should run the vendored `.llm-wiki/tools/llm_wiki_doctor.py validate` command.

## pre-commit And CI

The scaffolded `.pre-commit-config.yaml` runs:

```text
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --changed --phase normal --format text --fail-on error
```

The scaffolded GitHub Actions workflow runs:

```text
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --base origin/main --phase normal --format json --fail-on error
```

WARN findings should remain visible in terminal output, job summaries, PR comments, or handoff text, but they do not block unless a future policy explicitly changes severity.

## Fixing Findings

### orphan-design-doc

Register project-relative Markdown sources with exact paths:

```markdown
- original_path: `docs/plans/example.md`
```

Or explicitly ignore non-requirement documents:

```markdown
<!-- llm-wiki-ignore: orphan-design-doc reason="retained user guide" -->
```

### missing-graph-evidence

Use confirmed Project Graph evidence when it exists:

```markdown
## Project Graph Evidence

| Edge | Relation | Verification | Used For |
|---|---|---|---|
| `edge-YYYYMMDD-NNN` | `<from> -> <to> <boundary>` | source-verified | <why this edge matters> |
```

Use a gap when no confirmed edge exists:

```markdown
## Project Graph Gaps

- No confirmed edge records `<relation>` yet; source verification or candidate creation is required.
```

Do not invent edge ids or project ids.

### missing-module-context / incomplete-module-context

Create a source-backed module context under `.llm-wiki/modules/<module>/` with the standard scoped-context files:

```text
README.md
source-map.md
architecture.md
rules.md
verification.md
```

Do not auto-fill semantic content. Start with source-backed stub notes when needed, and keep unfinished modules marked as missing/discovered instead of ready.

### thin-module-context / missing-module-evidence

Replace placeholder module pages with real project knowledge. A ready module context should identify source anchors and describe:

- responsibility and ownership boundary;
- important entry points, APIs, listeners, scheduled jobs, configs, topics, tables, or tests;
- module-specific rules and known risk;
- how to verify changes in that module.

The doctor deliberately does not auto-fill these facts because they are semantic project knowledge. It only points out which module needs human or source-backed completion.

### contradictory-module-context

Either downgrade the module status in `.llm-wiki/modules/index.md`, or add the missing directory, standard files, and real source-backed content. This is an ERROR because the wiki currently claims a ready state that the file tree or file content contradicts.
