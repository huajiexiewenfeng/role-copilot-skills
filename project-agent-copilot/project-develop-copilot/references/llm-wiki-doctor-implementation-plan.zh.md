# LLM Wiki Doctor Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an installable `llm-wiki-doctor` child skill and upgrade `llm_wiki_doctor.py` into isolated `validate` / `score` / `report` flows with Chinese-first maturity reports.

**Architecture:** Keep deterministic validators and maturity scoring separated. The Python script owns repeatable checks and measurable signals; the child skill owns natural-language routing, interpretation, and repair handoff. CI, pre-commit, and project-finish use `validate`; human-triggered diagnosis uses `report`.

**Tech Stack:** Python standard library, `unittest`, Markdown skill docs, existing `npx skills add . --list` validation.

**Execution model:** Implement on a feature branch, for example `feat/llm-wiki-doctor`. Do not commit red TDD states on `main`, and do not finish by pushing directly to `main`. The implementation must open a PR and let CI run `validate --fail-on error` before merge.

---

## File Map

- Modify `project-agent-copilot/project-develop-copilot/scripts/llm_wiki_doctor.py`: add subcommands, canonical checks, score signals, Chinese report formatting, and legacy no-subcommand compatibility.
- Modify `project-agent-copilot/project-develop-copilot/scripts/tests/test_llm_wiki_doctor.py`: add failing tests for subcommands, canonical checks, N/A dimensions, and Chinese reports.
- Create `project-agent-copilot/project-develop-copilot/llm-wiki-doctor/SKILL.md`: natural-language doctor entry.
- Modify `project-agent-copilot/project-develop-copilot/SKILL.md`: route `wiki-doctor` mode.
- Modify `project-maintain/SKILL.md`, `project-finish/SKILL.md`, and `project-review/SKILL.md`: use `validate` for blocking checks and delegate scoring to `llm-wiki-doctor`.
- Modify README surfaces and `scripts/README.llm-wiki-doctor.md`: document the new skill and subcommands.
- Modify `evals/project-develop-copilot-evals.md` and, if needed, `references/acceptance-cases.md`: add routing and scoring coverage.
- Create `.llm-wiki/tools/llm_wiki_doctor.py` and `.llm-wiki/tools/VERSION`: vendored project-local doctor used by CI and pre-commit.
- Create or modify `project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py`: sync and drift-check the vendored doctor.
- Create `.pre-commit-config.yaml`: local hook that runs `validate` only.
- Create `.github/workflows/llm-wiki-doctor.yml`: PR/push workflow that runs tests, vendoring drift check, and `validate --fail-on error`.

## Task 1: Add Failing CLI And Canonical Validator Tests

**Files:**
- Modify: `project-agent-copilot/project-develop-copilot/scripts/tests/test_llm_wiki_doctor.py`

- [ ] **Step 1: Add CLI helper.** Add `import subprocess`, then add:

```python
def run_doctor_cli(root: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(MODULE_PATH), *args, "--root", str(root)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
```

- [ ] **Step 2: Add validate subcommand and legacy compatibility tests.** Add tests asserting `validate --all --format json --fail-on error` and legacy `--all --format json --fail-on error` both emit `orphan-design-doc` with exit code 0 when only WARN findings exist. Also add tests proving `invalid-edge-id`, `dangling-cross-ref`, `duplicate-edge-fingerprint`, and `leaked-local-path` are ERROR findings and make `--fail-on error` return exit code 1.

- [ ] **Step 3: Rename existing invalid edge expectations.** Replace every `invalid-graph-edge` test expectation with `invalid-edge-id`.

- [ ] **Step 4: Add deterministic Project Graph validator tests.** Add tests for:

```text
dangling-cross-ref: cross-refs/index.md references edge-20990101-999.
duplicate-edge-fingerprint: edges.md has two rows with fingerprint `same`.
leaked-local-path: a committed .llm-wiki markdown page contains C:\Users\admin\secret.
```

- [ ] **Step 5: Run tests and verify failure.**

```powershell
python -m unittest discover project-agent-copilot\project-develop-copilot\scripts\tests
```

Expected: tests fail because subcommands and new canonical checks are not implemented yet. Keep this red TDD state on the feature branch; do not commit or push it to `main`.

## Task 2: Implement Validate Subcommand And Canonical Checks

**Files:**
- Modify: `project-agent-copilot/project-develop-copilot/scripts/llm_wiki_doctor.py`

- [ ] **Step 1: Add subcommand normalization.** Add:

```python
def normalize_argv(argv: list[str] | None) -> list[str]:
    values = list(sys.argv[1:] if argv is None else argv)
    if not values or values[0] not in {"validate", "score", "report"}:
        return ["validate", *values]
    return values
```

- [ ] **Step 2: Split validate command.** Move existing main behavior into `run_validate_command(args)`, preserving `--root`, `--all`, `--changed`, `--base`, `--format`, and `--fail-on` behavior.

- [ ] **Step 3: Add subparsers.** `main()` must register `validate`, `score`, and `report`; `score` needs `--root` and `--format`; `report` needs `--root`, optional scan scope, and `--format`, but must not expose `--fail-on` because report is advisory and always exits 0.

- [ ] **Step 4: Rename validator output.** Change the check name emitted for unknown Project Graph evidence edges to `invalid-edge-id`.

- [ ] **Step 5: Add table helpers.** Add `table_rows_with_header(text)` and `cell_by_header(headers, row, name)` so graph checks can read Markdown tables predictably.

- [ ] **Step 6: Add graph checks.** Implement `check_dangling_cross_refs(root, registry)`, `check_duplicate_edge_fingerprints(root)`, and `check_leaked_local_paths(root, paths)`. These three emit ERROR findings with canonical check names. Keep `orphan-design-doc`, `missing-graph-evidence`, and `unresolved-project-id` as WARN. Change `invalid-edge-id` to ERROR.

- [ ] **Step 7: Wire checks into `run_checks`.** Append the new checks after existing orphan and missing-evidence checks.

- [ ] **Step 8: Enforce committed vocabulary sources and structured unresolved scans.** Keep `.llm-wiki/project-ids.json` as the first-version committed vocabulary file. Do not read `registry.local.json` for validate vocabulary. Use Base Graph `project-catalog.md` only as an optional supplement when it is available. Treat `edges.md` project ids as graph rows to validate, not as the unresolved-project-id vocabulary source. Implement `unresolved-project-id` only over structured fields: edge `from_project` / `to_project`, cross-ref project columns, Project Graph Evidence project columns, explicit `project:` / `from_project:` / `to_project:` fields, and relation cells that contain explicit `project-id -> project-id`, backticked ids, or `project: id`. Do not scan free-form paragraphs.

- [ ] **Step 9: Run tests.**

```powershell
python -m unittest discover project-agent-copilot\project-develop-copilot\scripts\tests
```

Expected: validator tests pass; score/report tests are not added yet.
## Task 3: Add Score Signals And Chinese Report Output

**Files:**
- Modify: `project-agent-copilot/project-develop-copilot/scripts/llm_wiki_doctor.py`
- Modify: `project-agent-copilot/project-develop-copilot/scripts/tests/test_llm_wiki_doctor.py`

- [ ] **Step 1: Add failing score tests.** Add tests for these behaviors:

```text
score --format json returns score_version = 1, score < 60 for a nearly empty wiki, includes fact_ids/signals, and next_steps mention closing concrete gaps such as .llm-wiki/README.md.
score --format json marks Project Graph / cross-refs as not-applicable when only one local project exists and no cross-service signal is present.
report --format text prints # LLM Wiki Doctor 报告 and ## 建议行动计划, and returns exit code 0 even when validate findings include ERROR.
report --format json contains findings and score objects.
```

- [ ] **Step 2: Add score dataclasses.** Add:

```python
SCORE_VERSION = 1

@dataclass(frozen=True)
class ScoreDimension:
    name: str
    max_score: int
    score: int | None
    applicability: str
    source: str
    message: str

@dataclass(frozen=True)
class ScoreReport:
    score_version: int
    score: int
    level: str
    dimensions: list[ScoreDimension]
    signals: dict[str, object]
    next_steps: list[str]
```

- [ ] **Step 3: Add page-type-aware empty-template helpers.** Add helpers that remove headings, table dividers, and placeholder phrases before measuring useful text. Apply anchor-resolution gap rules only to module pages, source proxies, and structured Project Graph evidence pages. For narrative pages such as README, requirements, bugs, working-context, and handoff, use required section/placeholder signals instead of anchor absence. Keep thresholds conservative and file-type aware enough to avoid penalizing short but complete pages.

- [ ] **Step 4: Build deterministic signals.** Implement `build_score_report(root)` with at least these signals:

```text
wiki_exists
readme_effective_length
module_index_exists
source_index_exists
validator_errors
validator_warnings
graph_applicable
graph_file_presence
fact_ids
```

- [ ] **Step 5: Implement N/A scoring and fact de-duplication.** Project Graph / cross-refs is `not-applicable` when registry contains no external project and no Markdown file has cross-service signals. Re-normalize total score over applicable dimensions only. Add `fact_id` or equivalent IDs to signals so one underlying fact affects the maturity total only once; do not subtract again in `Validator 健康度` if another dimension already absorbed the same fact.

- [ ] **Step 6: Implement next step generation.** Generate up to 10 Chinese next steps from low-scoring dimensions. Do not produce repair actions that invent module responsibilities, API contracts, requirements, bug conclusions, or confirmed graph edges. Action plans must target closing concrete gaps, not reaching a numeric score.

- [ ] **Step 7: Implement formatters.** Add `score_report_to_dict(report)` and `format_score_report_text(report, findings=None)`. The text report must order sections as:

```text
# LLM Wiki Doctor 报告
## 关键结论
## 建议行动计划
## 总体评分
## 成熟度维度
## Validator 发现
```

- [ ] **Step 8: Implement command runners.** Add `run_score_command(args)` and `run_report_command(args)`. `score` always returns 0. `report` also always returns 0 because it is a consulting command; CI and project-finish must use `validate` for blocking behavior.

- [ ] **Step 9: Run tests.**

```powershell
python -m unittest discover project-agent-copilot\project-develop-copilot\scripts\tests
```

Expected: all doctor tests pass, including ERROR exit-code coverage for the four deterministic blocking checks and report exit-code 0 coverage.

## Task 4: Add The `llm-wiki-doctor` Child Skill

**Files:**
- Create: `project-agent-copilot/project-develop-copilot/llm-wiki-doctor/SKILL.md`

- [ ] **Step 1: Create SKILL.md.** Use this structure:

```markdown
---
name: llm-wiki-doctor
description: Use when checking, scoring, diagnosing, or explaining a project-local .llm-wiki health state, LLM Wiki Doctor output, wiki maturity score, empty wiki skeletons after project init, Project Graph evidence warnings, or llm_wiki_doctor pre-commit/CI failures.
---

# LLM Wiki Doctor

## Purpose

Run and interpret LLM Wiki Doctor for a project-local `.llm-wiki`.

Default to read-only diagnosis. Use deterministic `validate` for hard validator findings and `report` for human-facing Chinese maturity reports. Do not repair files unless the user explicitly asks for repair or completion.

## Required First Check

1. Resolve the project root.
2. Confirm `.llm-wiki` exists. If it does not exist, route to `project-init`.
3. Resolve the doctor script from `.llm-wiki/tools/llm_wiki_doctor.py`, then the bundled `../scripts/llm_wiki_doctor.py`.
4. For CI, pre-commit, project-finish, or blocking failures, run `validate`.
5. Otherwise run `report` and explain the Chinese report.

## Commands

Human diagnosis:

```text
python <doctor> report --root . --format text
```

Machine checks:

```text
python <doctor> validate --root . --changed --format text --fail-on error
python <doctor> validate --root . --base origin/main --format json --fail-on error
```

Structured maturity signals:

```text
python <doctor> score --root . --format json
```

## Interpretation Rules

- Treat `validate` findings as deterministic script output.
- Treat `score` as directional maturity guidance, not a KPI.
- Report `not-applicable` dimensions instead of penalizing simple projects.
- Use script signals as evidence for semantic judgments. Do not invent project facts from the score.
- Keep Project Graph findings visible: `missing-graph-evidence`, `invalid-edge-id`, `dangling-cross-ref`, `duplicate-edge-fingerprint`, and `leaked-local-path`.

## Repair Boundary

Default to read-only. When the user explicitly asks to repair, route structural repairs to `project-maintain` unless the repair is limited to installing or running the doctor. Never auto-fill semantic content such as module responsibilities, API contracts, requirement scope, bug conclusions, confirmed Project Graph edges, or verification status.
```

- [ ] **Step 2: Validate skill discovery.**

```powershell
npx.cmd skills add . --list
```

Expected: output includes `llm-wiki-doctor`.

## Task 5: Update Router And Stage Skills

**Files:**
- Modify: `project-agent-copilot/project-develop-copilot/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-maintain/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-finish/SKILL.md`
- Modify: `project-agent-copilot/project-develop-copilot/project-review/SKILL.md`

- [ ] **Step 1: Add router triggers.** Add natural-language triggers for LLM Wiki Doctor, wiki maturity score, empty wiki skeletons after project init, and doctor CI/pre-commit findings.

- [ ] **Step 2: Add route row.** Add:

```markdown
| User asks to run LLM Wiki Doctor, score `.llm-wiki`, check whether project-init produced a useful wiki, or explain doctor/pre-commit/CI findings | wiki-doctor | `llm-wiki-doctor` |
```

- [ ] **Step 3: Update tie-breaker.** Use:

```text
lightweight-answer < read-only-query < wiki-doctor < dashboard-refresh < wiki-maintenance < full-lifecycle
```

- [ ] **Step 4: Update project-maintain.** Replace doctor command examples with `validate` subcommand examples and add: maturity scoring belongs to `llm-wiki-doctor`; structural repairs after user approval belong to `project-maintain`.

- [ ] **Step 5: Update project-finish and project-review.** Finish blocking checks use `validate`. Review can cite `report` as diagnostic evidence, but PR/merge blocking uses `validate --fail-on error`.

## Task 6: Add Machine Enforcement Artifacts

**Files:**
- Create: `.llm-wiki/tools/llm_wiki_doctor.py`
- Create: `.llm-wiki/tools/VERSION`
- Create/Modify: `project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py`
- Create: `.pre-commit-config.yaml`
- Create: `.github/workflows/llm-wiki-doctor.yml`

- [ ] **Step 1: Add the vendoring sync script.** Implement `sync-doctor.py` with Python standard library only. It must copy `project-agent-copilot/project-develop-copilot/scripts/llm_wiki_doctor.py` into `.llm-wiki/tools/llm_wiki_doctor.py`, create parent directories, and write `.llm-wiki/tools/VERSION` with the source path plus current Git commit when available. Add a `--check` mode that compares the source and vendored copy and exits non-zero when they drift.

- [ ] **Step 2: Run the sync script.** Create the vendored files before README examples reference them.

```powershell
python project-agent-copilot\project-develop-copilot\scripts\sync-doctor.py
```

Expected: `.llm-wiki/tools/llm_wiki_doctor.py` exists and matches the source script.

- [ ] **Step 3: Verify drift detection locally.**

```powershell
python project-agent-copilot\project-develop-copilot\scripts\sync-doctor.py --check
```

Expected: exit code 0 when source and vendored copy match. A temporary edit to either copy should make `--check` fail; revert the temporary edit immediately after this verification.

- [ ] **Step 4: Add pre-commit enforcement.** Add a local pre-commit hook that runs only deterministic validation and blocks only ERROR findings:

```text
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --changed --format text --fail-on error
```

Do not run `score` or `report` from pre-commit. WARN findings must not block commits.

- [ ] **Step 5: Add CI enforcement.** Create a GitHub Actions workflow for PR and push events on `ubuntu-latest`. Use Linux paths and commands:

```bash
python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests
python project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py --check
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --base origin/main --format json --fail-on error
```

The workflow must fetch enough history for `origin/main` to resolve. If the workflow uses `npx`, use `npx`, not `npx.cmd`. Keep path handling in scripts on `pathlib` so Windows local runs and Linux CI runs share the same behavior.

- [ ] **Step 6: Treat CI as the merge gate.** Configure the workflow as the required PR status check in repository branch protection. The repository setting is outside code review diff, but the implementation PR must call it out explicitly. CI and pre-commit use `validate`; `score` and `report` remain consulting commands and never gate merge.

## Task 7: Update README And Doctor Usage Docs

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`
- Modify: `project-agent-copilot/README.md`
- Modify: `project-agent-copilot/README.zh.md`
- Modify: `project-agent-copilot/project-develop-copilot/README.md`
- Modify: `project-agent-copilot/project-develop-copilot/README.zh.md`
- Modify: `project-agent-copilot/project-develop-copilot/scripts/README.llm-wiki-doctor.md`

- [ ] **Step 1: Add `llm-wiki-doctor` to skill tables.**

English row:

```markdown
| `llm-wiki-doctor` | Run or explain LLM Wiki Doctor validate/score/report output, including Chinese maturity reports, empty wiki skeleton detection, and Project Graph validator findings. |
```

Chinese row:

```markdown
| `llm-wiki-doctor` | 运行或解释 LLM Wiki Doctor 的 validate/score/report 输出，包括中文成熟度报告、空壳 wiki 识别和 Project Graph validator 发现。 |
```

- [ ] **Step 2: Update collection lists.** Add `llm-wiki-doctor` beside `project-maintain` in top-level, role-level, and inner collection descriptions.

- [ ] **Step 3: Rewrite script README commands.** Use:

```text
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --all --format text --fail-on error
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --changed --format text --fail-on error
python .llm-wiki/tools/llm_wiki_doctor.py validate --root . --base origin/main --format json --fail-on error
python .llm-wiki/tools/llm_wiki_doctor.py report --root . --format text
python .llm-wiki/tools/llm_wiki_doctor.py score --root . --format json
```

- [ ] **Step 4: Update check names.** Replace old check names with canonical names. The final Checks section must include severities: ERROR for `leaked-local-path`, `invalid-edge-id`, `dangling-cross-ref`, and `duplicate-edge-fingerprint`; WARN for the remaining checks. The check list must include:

```text
orphan-design-doc
missing-graph-evidence
unresolved-project-id
invalid-edge-id
dangling-cross-ref
duplicate-edge-fingerprint
leaked-local-path
```

- [ ] **Step 5: Run README grep.**

```powershell
rg -n "invalid-graph-edge|invalid-edge-id|llm-wiki-doctor|validate --root|score --root|report --root" README.md README.zh.md project-agent-copilot\README.md project-agent-copilot\README.zh.md project-agent-copilot\project-develop-copilot\README.md project-agent-copilot\project-develop-copilot\README.zh.md project-agent-copilot\project-develop-copilot\scripts\README.llm-wiki-doctor.md
```

Expected: no `invalid-graph-edge`; new skill and subcommands are documented.

## Task 8: Add Eval And Acceptance Coverage

**Files:**
- Modify: `project-agent-copilot/project-develop-copilot/evals/project-develop-copilot-evals.md`
- Modify if needed: `project-agent-copilot/project-develop-copilot/references/acceptance-cases.md`

- [ ] **Step 1: Add Eval 29.** Append this case without nesting fenced code blocks inside another fence:

    ## Eval 29: LLM Wiki Doctor Routes To Dedicated Skill

    Input prompt:

        跑一下 LLM Wiki Doctor，看看这个 project init 后的 .llm-wiki 到底有没有用。

    Expected route:

        mode: wiki-doctor
        primary_stage: llm-wiki-doctor

    Required behavior:

    - Runs or proposes `llm_wiki_doctor.py report`.
    - Produces a Chinese-first report.
    - Keeps default behavior read-only.
    - Routes repairs to `project-maintain` only after user approval.

    Pass/fail:

        PASS: dedicated doctor route, Chinese report, no automatic semantic repair
        FAIL: routes directly to project-maintain repair or only runs broad source search

- [ ] **Step 2: Add Eval 30.** Append this case:

    ## Eval 30: Simple Project Does Not Lose Score For Project Graph N/A

    Input prompt:

        给这个单模块项目的 .llm-wiki 打分。

    Required behavior:

    - Marks Project Graph / cross-refs as not-applicable when no external project or cross-service signal exists.
    - Re-normalizes score over applicable dimensions.
    - Explains that the score reflects suitability for this project, not absolute system size.

    Pass/fail:

        PASS: Project Graph is N/A and not counted as missing
        FAIL: subtracts Project Graph points from a simple project without cross-service signals

- [ ] **Step 3: Update acceptance cases if a validator section exists.** Use the canonical seven check names exactly as listed in Task 7.

- [ ] **Step 4: Run grep for old names.**

```powershell
rg -n "invalid-graph-edge|invalid-edge-id|dangling-cross-ref|duplicate-edge-fingerprint|leaked-local-path" project-agent-copilot\project-develop-copilot
```

Expected: no old check name remains except in deliberate migration notes.

## Task 9: Validate Package, Tests, And Git Hygiene

**Files:**
- All modified files from prior tasks.

Run both local Windows commands and the Linux-equivalent commands that CI will execute. The final PR must prove the machine-enforced path works, not only the developer-local path.

- [ ] **Step 1: Run unit tests locally and with CI-equivalent paths.**

Windows / PowerShell:

```powershell
python -m unittest discover project-agent-copilot\project-develop-copilot\scripts\tests
```

Linux / CI equivalent:

```bash
python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests
```

Expected: all tests pass.

- [ ] **Step 2: Run skill package listing.**

```powershell
npx.cmd skills add . --list
```

Expected: output lists `llm-wiki-doctor` and existing project skills.

- [ ] **Step 3: Run source grep checks.**

```powershell
rg -n "invalid-graph-edge" project-agent-copilot\project-develop-copilot --glob "!references/llm-wiki-doctor-*.md"
rg -n "project-ids\.(yml|yaml)" project-agent-copilot README.md README.zh.md --glob "!references/*补丁*.md"
rg -n "llm-wiki-doctor|wiki-doctor|llm_wiki_doctor.py validate|score_version" project-agent-copilot\project-develop-copilot
```

Expected: first command returns no production-doc or code matches for the retired check name; second command returns no `.yml` / `.yaml` project-id vocabulary references; third command shows script, skill, router, README, evals, and design/plan references.

- [ ] **Step 4: Check Git status.**

```powershell
git status --short
```

Expected: only intended files are modified or added. The existing untracked `project-agent-copilot/project-develop-copilot/internal-trial-guides/` remains untracked and unstaged.

- [ ] **Step 5: Commit implementation after reviewing staged diff.**

Use explicit path staging so unrelated files are not included. Do not stage whole directories such as `project-agent-copilot/project-develop-copilot`, because unrelated local directories may exist under them. Stage only files that were actually created or modified from this list:

```powershell
git add -- README.md README.zh.md `
  .pre-commit-config.yaml `
  .github/workflows/llm-wiki-doctor.yml `
  .llm-wiki/tools/llm_wiki_doctor.py `
  .llm-wiki/tools/VERSION `
  project-agent-copilot/README.md `
  project-agent-copilot/README.zh.md `
  project-agent-copilot/project-develop-copilot/README.md `
  project-agent-copilot/project-develop-copilot/README.zh.md `
  project-agent-copilot/project-develop-copilot/SKILL.md `
  project-agent-copilot/project-develop-copilot/llm-wiki-doctor/SKILL.md `
  project-agent-copilot/project-develop-copilot/project-maintain/SKILL.md `
  project-agent-copilot/project-develop-copilot/project-finish/SKILL.md `
  project-agent-copilot/project-develop-copilot/project-review/SKILL.md `
  project-agent-copilot/project-develop-copilot/scripts/llm_wiki_doctor.py `
  project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py `
  project-agent-copilot/project-develop-copilot/scripts/tests/test_llm_wiki_doctor.py `
  project-agent-copilot/project-develop-copilot/scripts/README.llm-wiki-doctor.md `
  project-agent-copilot/project-develop-copilot/evals/project-develop-copilot-evals.md `
  project-agent-copilot/project-develop-copilot/references/acceptance-cases.md
```

If optional files were not changed, remove those paths from the staging command instead of staging a parent directory. Then commit:

```powershell
git commit -m "feat(project-develop): add llm-wiki doctor skill"
```

- [ ] **Step 6: Push the feature branch and open PR.**

```powershell
git push origin feat/llm-wiki-doctor
```

Expected: a PR is opened from the feature branch. Merge only after CI passes and branch protection accepts the `llm-wiki-doctor` workflow. Do not push directly to `main`.

## Self-Review

Spec coverage:

- Child skill creation is covered by Task 4.
- Router update is covered by Task 5.
- `validate` / `score` / `report` split is covered by Tasks 1-3.
- Canonical Project Graph checks are covered by Tasks 1-2 and Task 8.
- Chinese-first report and score metadata are covered by Task 3.
- Machine enforcement artifacts are covered by Task 6.
- README and usage docs are covered by Task 7.
- Evals and acceptance coverage are covered by Task 8.
- Verification and Git hygiene are covered by Task 9.

Placeholder scan:

- The plan contains no unresolved work markers.
- Every task names concrete files and commands.
- Code-changing steps include concrete snippets or exact behavior.

Type consistency:

- `ScoreDimension`, `ScoreReport`, `score_report_to_dict`, `format_score_report_text`, `run_score_command`, and `run_report_command` are consistently named across tasks.
- Canonical check names match the design document.