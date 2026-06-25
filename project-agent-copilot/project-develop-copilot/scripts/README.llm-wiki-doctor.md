# LLM Wiki Doctor

`llm_wiki_doctor.py` is the Project Develop Copilot validator for repo-local `.llm-wiki` artifacts.

It is distributed in the skill source repo under:

```text
project-agent-copilot/project-develop-copilot/scripts/llm_wiki_doctor.py
project-agent-copilot/project-develop-copilot/scripts/tests/test_llm_wiki_doctor.py
project-agent-copilot/project-develop-copilot/scripts/git-hooks/pre-commit-llm-wiki-doctor
```

Business repos should vendor a fixed copy under:

```text
.llm-wiki/tools/llm_wiki_doctor.py
.llm-wiki/tools/VERSION
.llm-wiki/tools/pre-commit-llm-wiki-doctor
.llm-wiki/project-ids.json
```

## Checks

- `orphan-design-doc`: warns when requirement, design, bug, or plan documents outside `.llm-wiki` are not registered by exact source path or `original_path`.
- `missing-graph-evidence`: warns when cross-service `.llm-wiki` artifacts do not include `## Project Graph Evidence` or `## Project Graph Gaps`.
- `invalid-graph-edge`: warns when `Project Graph Evidence` references an edge id that is not present in `.llm-wiki/project-graph/edges.md`.

Phase 1 is WARN-first. With `--fail-on error`, WARN findings remain visible but do not fail the command.

## Repo-local Usage

Run all checks:

```text
python .llm-wiki/tools/llm_wiki_doctor.py --root . --all --format text --fail-on error
```

Run changed-file checks:

```text
python .llm-wiki/tools/llm_wiki_doctor.py --root . --changed --format text --fail-on error
```

Run PR/base checks:

```text
python .llm-wiki/tools/llm_wiki_doctor.py --root . --base origin/main --format json --fail-on error
```

Run unit tests from the skill source repo:

```text
python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests
```

Run unit tests from a business repo after vendoring:

```text
python -m unittest discover .llm-wiki/tools/tests
```

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

Do not invent edge ids.

## pre-commit Hook

Business repos can copy the hook sample:

```text
cp .llm-wiki/tools/pre-commit-llm-wiki-doctor .git/hooks/pre-commit
```

The hook should run the repo-vendored doctor, not the installed skill copy.

## CI

CI should call the repo-vendored script:

```text
python .llm-wiki/tools/llm_wiki_doctor.py --root . --all --format json --fail-on error
```

Publish WARN findings to job summary or PR comments so Phase 1 measurements are visible even when exit code is zero.
