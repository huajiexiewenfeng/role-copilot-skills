# LLM Wiki Doctor Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an installable `llm-wiki-doctor` child skill and upgrade `llm_wiki_doctor.py` into isolated `validate` / `score` / `report` flows with Chinese-first maturity reports.

**Architecture:** Keep deterministic validators and maturity scoring separated. The Python script owns repeatable checks and measurable signals; the child skill owns natural-language routing, interpretation, and repair handoff. CI, pre-commit, and project-finish use `validate`; human-triggered diagnosis uses `report`.

**Tech Stack:** Python standard library, `unittest`, Markdown skill docs, existing `npx skills add . --list` validation.

---

## File Map

- Modify `project-agent-copilot/project-develop-copilot/scripts/llm_wiki_doctor.py`: add subcommands, canonical checks, score signals, Chinese report formatting, and legacy no-subcommand compatibility.
- Modify `project-agent-copilot/project-develop-copilot/scripts/tests/test_llm_wiki_doctor.py`: add failing tests for subcommands, canonical checks, N/A dimensions, and Chinese reports.
- Create `project-agent-copilot/project-develop-copilot/llm-wiki-doctor/SKILL.md`: natural-language doctor entry.
- Modify `project-agent-copilot/project-develop-copilot/SKILL.md`: route `wiki-doctor` mode.
- Modify `project-maintain/SKILL.md`, `project-finish/SKILL.md`, and `project-review/SKILL.md`: use `validate` for blocking checks and delegate scoring to `llm-wiki-doctor`.
- Modify README surfaces and `scripts/README.llm-wiki-doctor.md`: document the new skill and subcommands.
- Modify `evals/project-develop-copilot-evals.md` and, if needed, `references/acceptance-cases.md`: add routing and scoring coverage.

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

- [ ] **Step 2: Add validate subcommand and legacy compatibility tests.** Add tests asserting `validate --all --format json --fail-on error` and legacy `--all --format json --fail-on error` both emit `orphan-design-doc` with exit code 0 when only WARN findings exist.

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

Expected: tests fail because subcommands and new canonical checks are not implemented yet. Do not commit this failing state on `main`.

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

- [ ] **Step 3: Add subparsers.** `main()` must register `validate`, `score`, and `report`; `score` needs `--root` and `--format`; `report` needs scan args plus `--format` and `--fail-on`.

- [ ] **Step 4: Rename validator output.** Change the check name emitted for unknown Project Graph evidence edges to `invalid-edge-id`.

- [ ] **Step 5: Add table helpers.** Add `table_rows_with_header(text)` and `cell_by_header(headers, row, name)` so graph checks can read Markdown tables predictably.

- [ ] **Step 6: Add graph checks.** Implement `check_dangling_cross_refs(root, registry)`, `check_duplicate_edge_fingerprints(root)`, and `check_leaked_local_paths(root, paths)`. All three emit WARN findings with canonical check names.

- [ ] **Step 7: Wire checks into `run_checks`.** Append the new checks after existing orphan and missing-evidence checks.

- [ ] **Step 8: Run tests.**

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
score --format json returns score_version = 1, score < 60 for a nearly empty wiki, and next_steps mention .llm-wiki/README.md.
score --format json marks Project Graph / cross-refs as not-applicable when only one local project exists and no cross-service signal is present.
report --format text prints # LLM Wiki Doctor 报告 and ## 建议行动计划.
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

- [ ] **Step 3: Add effective text helpers.** Add helpers that remove headings, table dividers, and placeholder phrases before measuring useful text. Keep thresholds conservative and file-type aware enough to avoid penalizing short but complete pages.

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
```

- [ ] **Step 5: Implement N/A scoring.** Project Graph / cross-refs is `not-applicable` when registry contains no external project and no Markdown file has cross-service signals. Re-normalize total score over applicable dimensions only.

- [ ] **Step 6: Implement next step generation.** Generate up to 10 Chinese next steps from low-scoring dimensions. Do not produce repair actions that invent module responsibilities, API contracts, requirements, bug conclusions, or confirmed graph edges.

- [ ] **Step 7: Implement formatters.** Add `score_report_to_dict(report)` and `format_score_report_text(report, findings=None)`. The text report must order sections as:

```text
# LLM Wiki Doctor 报告
## 关键结论
## 建议行动计划
## 总体评分
## 成熟度维度
## Validator 发现
```

- [ ] **Step 8: Implement command runners.** Add `run_score_command(args)` and `run_report_command(args)`. `score` always returns 0. `report` returns the validator exit code and never fails because of score.

- [ ] **Step 9: Run tests.**

```powershell
python -m unittest discover project-agent-copilot\project-develop-copilot\scripts\tests
```

Expected: all doctor tests pass.

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
python <doctor> report --root . --format text --fail-on error
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
## Task 6: Update README And Doctor Usage Docs

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
python .llm-wiki/tools/llm_wiki_doctor.py report --root . --format text --fail-on error
python .llm-wiki/tools/llm_wiki_doctor.py score --root . --format json
```

- [ ] **Step 4: Update check names.** Replace old check names with canonical names. The final Checks section must include:

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

## Task 7: Add Eval And Acceptance Coverage

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

- [ ] **Step 3: Update acceptance cases if a validator section exists.** Use the canonical seven check names exactly as listed in Task 6.

- [ ] **Step 4: Run grep for old names.**

```powershell
rg -n "invalid-graph-edge|invalid-edge-id|dangling-cross-ref|duplicate-edge-fingerprint|leaked-local-path" project-agent-copilot\project-develop-copilot
```

Expected: no old check name remains except in deliberate migration notes.

## Task 8: Validate Package, Tests, And Git Hygiene

**Files:**
- All modified files from prior tasks.

- [ ] **Step 1: Run unit tests.**

```powershell
python -m unittest discover project-agent-copilot\project-develop-copilot\scripts\tests
```

Expected: all tests pass.

- [ ] **Step 2: Run skill package listing.**

```powershell
npx.cmd skills add . --list
```

Expected: output lists `llm-wiki-doctor` and existing project skills.

- [ ] **Step 3: Run source grep checks.**

```powershell
rg -n "invalid-graph-edge" project-agent-copilot\project-develop-copilot
rg -n "llm-wiki-doctor|wiki-doctor|llm_wiki_doctor.py validate|score_version" project-agent-copilot\project-develop-copilot
```

Expected: first command returns no matches; second command shows script, skill, router, README, evals, and design/plan references.

- [ ] **Step 4: Check Git status.**

```powershell
git status --short
```

Expected: only intended files are modified or added. The existing untracked `project-agent-copilot/project-develop-copilot/internal-trial-guides/` remains untracked and unstaged.

- [ ] **Step 5: Commit implementation after reviewing staged diff.**

Use explicit path staging so unrelated files are not included:

```powershell
git add -- README.md README.zh.md project-agent-copilot/README.md project-agent-copilot/README.zh.md project-agent-copilot/project-develop-copilot
```

Then commit:

```powershell
git commit -m "feat(project-develop): add llm-wiki doctor skill"
```

- [ ] **Step 6: Push.**

```powershell
git push origin main
```

Expected: GitHub `main` includes the new skill, upgraded doctor script, tests, docs, and evals.

## Self-Review

Spec coverage:

- Child skill creation is covered by Task 4.
- Router update is covered by Task 5.
- `validate` / `score` / `report` split is covered by Tasks 1-3.
- Canonical Project Graph checks are covered by Tasks 1-2 and Task 7.
- Chinese-first report and score metadata are covered by Task 3.
- README and usage docs are covered by Task 6.
- Evals and acceptance coverage are covered by Task 7.
- Verification and Git hygiene are covered by Task 8.

Placeholder scan:

- The plan contains no unresolved work markers.
- Every task names concrete files and commands.
- Code-changing steps include concrete snippets or exact behavior.

Type consistency:

- `ScoreDimension`, `ScoreReport`, `score_report_to_dict`, `format_score_report_text`, `run_score_command`, and `run_report_command` are consistently named across tasks.
- Canonical check names match the design document.