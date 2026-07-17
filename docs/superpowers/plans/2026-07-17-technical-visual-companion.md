# Technical Visual Companion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the `visual-agent-copilot` role container and its first installable skill, `technical-visual-companion`, which converts confirmed technical designs into one verified offline Visual Companion HTML.

**Architecture:** Keep the role container thin and place the complete workflow inside `technical-visual-companion`. The skill selects 1–3 diagram types from source-backed relationships, generates one standalone HTML without a fixed page template, validates deterministic file rules through a standard-library Python CLI, then requires desktop and mobile browser inspection before completion.

**Tech Stack:** Markdown skill instructions, semantic HTML, scoped CSS, inline SVG, Python 3.11+ standard library (`argparse`, `html.parser`, `json`, `unittest`), in-app browser viewport inspection, `npx skills` package discovery, Skill Creator eval viewer.

## Global Constraints

- Work in an isolated worktree created from `D:\tmp\github\role-copilot-skills`.
- Preserve all unrelated staged, unstaged, and untracked work in the main worktree.
- Add the top-level role container exactly as `visual-agent-copilot`.
- Add the installable skill exactly as `technical-visual-companion`.
- Accept only confirmed conversation content or user-specified local files; never scan an unspecified repository tree.
- Default output is `docs/visuals/<topic-slug>.html`; an explicit user path overrides it.
- Do not overwrite an existing HTML without explicit approval.
- First-version user delivery is exactly one standalone HTML file.
- Final HTML uses UTF-8 without BOM and embeds all CSS and SVG.
- Final HTML contains no JavaScript, iframe, CDN, external font, fetch, XHR, WebSocket, or other network dependency.
- Select 1–3 diagram types automatically; do not force three diagrams when fewer are sufficient.
- Preserve confirmed names, counts, versions, boundaries, order, states, and rollback semantics.
- Browser inspection at desktop and 390px width is required; without browser capability, stop with visual verification pending rather than claim completion.
- Do not add a fixed HTML template or reusable page asset that forces every output into the same composition.
- Do not implement PNG, PDF, PPT, Mermaid, interactive HTML, publishing, Git auto-commit, product UI, or technical-design completion in version one.

---

### Task 1: Scaffold the Role Container and Installable Skill Contract

**Files:**
- Create: `visual-agent-copilot/README.md`
- Create: `visual-agent-copilot/README.zh.md`
- Create: `visual-agent-copilot/technical-visual-companion/SKILL.md`
- Create: `visual-agent-copilot/technical-visual-companion/scripts/tests/test_skill_contract.py`

**Interfaces:**
- Consumes: approved design at `docs/superpowers/specs/2026-07-17-visual-agent-copilot-technical-visual-companion-design.md`.
- Produces: installable skill root, exact frontmatter identity, and a repeatable static contract test extended by later tasks.

- [ ] **Step 1: Write the failing structure and frontmatter test**

Create `test_skill_contract.py` with a repository-relative fixture:

```python
from pathlib import Path
import re
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[2]
ROLE_ROOT = SKILL_ROOT.parent


class TechnicalVisualCompanionContractTest(unittest.TestCase):
    def test_role_and_skill_files_exist(self):
        for path in (
            ROLE_ROOT / "README.md",
            ROLE_ROOT / "README.zh.md",
            SKILL_ROOT / "SKILL.md",
        ):
            self.assertTrue(path.is_file(), path)

    def test_frontmatter_identity_and_trigger_boundary(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^name: technical-visual-companion$")
        description = re.search(r"(?m)^description: (.+)$", text)
        self.assertIsNotNone(description)
        for phrase in (
            "confirmed technical",
            "static HTML",
            "architecture",
            "sequence",
            "state",
        ):
            self.assertIn(phrase, description.group(1))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify RED**

Run from the repository root:

```powershell
C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover visual-agent-copilot/technical-visual-companion/scripts/tests -p "test_*.py" -v
```

Expected: FAIL because the role and skill files do not exist.

- [ ] **Step 3: Create the minimal role READMEs**

Both READMEs must identify Visual Agent Copilot as the visual-communication role container, list `technical-visual-companion` as the first skill, and include this installation command:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/visual-agent-copilot/technical-visual-companion
```

The Chinese README describes the role as “把复杂内容转化为易理解、可交付的视觉表达”; the English README uses “turn complex content into understandable, deliverable visual communication”.

- [ ] **Step 4: Create the minimal SKILL.md frontmatter and purpose**

Use this exact frontmatter:

```yaml
---
name: technical-visual-companion
description: Use this skill whenever the user asks to turn a confirmed technical design into a polished offline static HTML visual, including architecture, system boundaries, service interactions, sequence flows, deployment topology, state transitions, failure recovery, or multiple complementary technical diagrams. Do not use it to invent or complete an unconfirmed design, build a product UI, or produce Mermaid, slides, PDF, or PNG-only output.
---
```

The initial body states that the skill consumes confirmed facts and produces one verified HTML; it does not yet contain the full workflow added in Task 4.

- [ ] **Step 5: Run the contract test and verify GREEN**

Run the Task 1 test command. Expected: 2 tests pass.

- [ ] **Step 6: Commit Task 1**

```powershell
git add -- visual-agent-copilot/README.md visual-agent-copilot/README.zh.md visual-agent-copilot/technical-visual-companion/SKILL.md visual-agent-copilot/technical-visual-companion/scripts/tests/test_skill_contract.py
git commit -m "feat(visual): scaffold technical visual companion"
```

### Task 2: Add Diagram Selection and Visual Language References

**Files:**
- Create: `visual-agent-copilot/technical-visual-companion/references/diagram-selection.md`
- Create: `visual-agent-copilot/technical-visual-companion/references/visual-language.md`
- Modify: `visual-agent-copilot/technical-visual-companion/scripts/tests/test_skill_contract.py`

**Interfaces:**
- Consumes: `SKILL_ROOT` from Task 1 tests.
- Produces: relationship-to-diagram rules and a reusable visual language without a fixed page template.

- [ ] **Step 1: Extend the contract test and verify RED**

Add these tests:

```python
    def test_diagram_selection_covers_required_relationships(self):
        text = (SKILL_ROOT / "references" / "diagram-selection.md").read_text(encoding="utf-8")
        for phrase in (
            "System boundary",
            "Sequence or swimlane",
            "State machine",
            "Deployment topology",
            "Data flow",
            "Comparison matrix",
            "Timeline",
        ):
            self.assertIn(phrase, text)
        self.assertIn("one to three", text.lower())
        self.assertIn("one diagram", text.lower())

    def test_visual_language_is_adaptive_not_template_driven(self):
        text = (SKILL_ROOT / "references" / "visual-language.md").read_text(encoding="utf-8")
        for phrase in (
            "Superpowers Visual Companion",
            "semantic color",
            "desktop",
            "mobile",
            "cards alone",
            "Do not use a fixed page template",
        ):
            self.assertIn(phrase, text)
```

Run the Task 1 command. Expected: FAIL because both reference files are missing.

- [ ] **Step 2: Write diagram-selection.md**

Define the exact mapping from the approved design:

- boundary/responsibility/upstream-downstream -> system boundary or responsibility map;
- calls/synchronous-asynchronous interaction -> sequence or swimlane;
- state/retry/failure/recovery -> state machine;
- nodes/networks/ports/containers -> deployment topology;
- source/process/destination -> data flow;
- options/versions/capabilities -> comparison matrix;
- staged execution/release -> phase flow or timeline.

Add selection rules: identify the questions the visual must answer, score candidate diagrams by relationship coverage and non-duplication, choose one to three, and choose one diagram when it is sufficient. Explicit user diagram/count requests override automatic selection.

- [ ] **Step 3: Write visual-language.md**

Define Superpowers Visual Companion as a design language, not a copied layout. Require clear hierarchy, restrained rounded technical panels, soft grids and shadows, explicit arrows or lanes, stable processing/success/waiting/failure colors, inline SVG for relational diagrams, and a vertical semantic alternative below 720px. State: “Do not use cards alone to represent relationships” and “Do not use a fixed page template”.

- [ ] **Step 4: Run tests and commit**

Expected: all four Task 1–2 contract tests pass.

```powershell
git add -- visual-agent-copilot/technical-visual-companion/references/diagram-selection.md visual-agent-copilot/technical-visual-companion/references/visual-language.md visual-agent-copilot/technical-visual-companion/scripts/tests/test_skill_contract.py
git commit -m "docs(visual): define diagram and visual language contracts"
```

### Task 3: Implement the Deterministic Offline HTML Validator

**Files:**
- Create: `visual-agent-copilot/technical-visual-companion/references/html-contract.md`
- Create: `visual-agent-copilot/technical-visual-companion/scripts/validate_html.py`
- Create: `visual-agent-copilot/technical-visual-companion/scripts/tests/test_validate_html.py`

**Interfaces:**
- Consumes: a final HTML path, zero or more required terms, and optional maximum bytes.
- Produces: `validate_html(path: Path, required_terms: tuple[str, ...], max_bytes: int) -> dict`; CLI JSON with `overall`, `errors`, and `metrics`; exit 0 for passed and 1 for failed.

- [ ] **Step 1: Write validator tests and verify RED**

Create test helpers that write UTF-8 fixtures in `TemporaryDirectory`. The valid fixture must contain one doctype, one `<html>`, one `<section>`, one accessible SVG (`role="img"`, `<title>`, `<desc>`), `@media (max-width: 720px)`, and `prefers-reduced-motion`.

Use these concrete assertions after loading the module through `importlib.util`:

```python
VALID_HTML = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><style>
@media (max-width: 720px) { section { display: block; } }
@media (prefers-reduced-motion: reduce) { * { animation: none; } }
@media (prefers-color-scheme: dark) { :root { color-scheme: dark; } }
</style></head><body><section><h2>系统边界</h2>
<svg role="img"><title>边界图</title><desc>服务关系</desc></svg>
</section></body></html>"""

def test_valid_offline_html_passes(self):
    path = self.write_bytes(VALID_HTML.encode("utf-8"))
    report = self.validator.validate_html(path, ("系统边界",), 2_000_000)
    self.assertEqual("passed", report["overall"])
    self.assertEqual([], report["errors"])

def test_bom_script_iframe_and_external_resource_fail(self):
    invalid = VALID_HTML.replace(
        "</body>",
        '<script></script><iframe></iframe><img src="https://example.com/a.png"></body>',
    )
    path = self.write_bytes(b"\xef\xbb\xbf" + invalid.encode("utf-8"))
    errors = self.validator.validate_html(path, (), 2_000_000)["errors"]
    for code in ("utf8-bom", "script-forbidden", "iframe-forbidden", "external-resource-forbidden"):
        self.assertIn(code, errors)

def test_missing_svg_accessibility_and_responsive_rules_fail(self):
    invalid = "<!doctype html><html><body><section><svg></svg></section></body></html>"
    path = self.write_bytes(invalid.encode("utf-8"))
    errors = self.validator.validate_html(path, (), 2_000_000)["errors"]
    for code in (
        "svg-accessibility-incomplete",
        "responsive-rule-missing",
        "reduced-motion-rule-missing",
        "color-scheme-rule-missing",
    ):
        self.assertIn(code, errors)

def test_required_terms_are_enforced(self):
    path = self.write_bytes(VALID_HTML.encode("utf-8"))
    errors = self.validator.validate_html(path, ("missing-service",), 2_000_000)["errors"]
    self.assertIn("required-term-missing:missing-service", errors)
```

Add a CLI subprocess test that passes the concrete invalid path returned by `self.write_bytes(...)` to `subprocess.run([sys.executable, str(MODULE_PATH), "--html", str(path)], ...)`, then asserts exit code 1 and parsed JSON `overall=failed`.

Import the module using `importlib.util.spec_from_file_location`, matching the repository's existing standard-library test style.

Run discovery because the skill directories intentionally contain hyphens and are not Python package names:

```powershell
C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover visual-agent-copilot/technical-visual-companion/scripts/tests -p "test_validate_html.py" -v
```

Expected: FAIL because `validate_html.py` does not exist.

- [ ] **Step 2: Implement the parser and validation result**

Use `html.parser.HTMLParser` to count HTML, sections, SVGs, SVG titles/descriptions, scripts, iframes, and external `src`, `srcset`, `href`, `poster`, `action`, or `data` attributes. Validate strict UTF-8, no BOM, one doctype, one HTML root, at least one section and SVG, complete SVG accessibility, narrow-screen, reduced-motion and dark-scheme tokens, maximum size, and every required term. Scan raw markup for HTTP(S), `@import url`, `fetch(`, `XMLHttpRequest`, and `WebSocket` references so CSS and text-hidden network dependencies cannot bypass attribute checks.

Return this stable shape:

```python
{
    "overall": "passed" if not errors else "failed",
    "errors": errors,
    "metrics": {
        "sizeBytes": len(raw),
        "sectionCount": parser.sections,
        "svgCount": parser.svgs,
        "scriptCount": parser.scripts,
        "iframeCount": parser.iframes,
        "externalResourceCount": len(parser.external_resources),
    },
}
```

Use stable error codes including `utf8-bom`, `invalid-utf8`, `doctype-count`, `html-root-count`, `section-missing`, `svg-missing`, `script-forbidden`, `iframe-forbidden`, `external-resource-forbidden`, `network-reference-forbidden`, `svg-accessibility-incomplete`, `responsive-rule-missing`, `reduced-motion-rule-missing`, `color-scheme-rule-missing`, `size-limit-exceeded`, and `required-term-missing:<term>`.

The CLI accepts repeatable `--required-term` flags:

```text
validate_html.py --html PATH --required-term TERM --required-term TERM [--max-bytes 2000000]
```

It writes UTF-8 JSON to stdout and returns 0/1 based on `overall`.

- [ ] **Step 3: Write html-contract.md**

Document every validator rule, the exact CLI, the 2 MB default ceiling, the fact that required terms come from the task's visual fact model, and the limitation that structural validation does not prove visual quality or factual correctness.

- [ ] **Step 4: Run validator and full contract tests**

Run discovery for all tests. Expected: all validator and existing contract tests pass.

- [ ] **Step 5: Commit Task 3**

```powershell
git add -- visual-agent-copilot/technical-visual-companion/references/html-contract.md visual-agent-copilot/technical-visual-companion/scripts/validate_html.py visual-agent-copilot/technical-visual-companion/scripts/tests/test_validate_html.py
git commit -m "feat(visual): validate offline companion HTML"
```

### Task 4: Complete the Skill Workflow and Stop Gates

**Files:**
- Modify: `visual-agent-copilot/technical-visual-companion/SKILL.md`
- Modify: `visual-agent-copilot/technical-visual-companion/scripts/tests/test_skill_contract.py`

**Interfaces:**
- Consumes: the three references and validator CLI from Tasks 2–3.
- Produces: end-to-end instructions that generate exactly one verified HTML or stop before generation.

- [ ] **Step 1: Extend the contract test and verify RED**

Add one test that requires these exact workflow tokens in SKILL.md:

```python
    def test_workflow_preserves_sources_and_requires_visual_verification(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "Confirmed Input Gate",
            "Visual Fact Model",
            "Diagram Selection",
            "Generate One HTML",
            "Deterministic Validation",
            "Desktop Visual Review",
            "390px Mobile Review",
            "Completion Gate",
            "docs/visuals/<topic-slug>.html",
            "do not scan",
            "do not overwrite",
            "visual verification pending",
        ):
            self.assertIn(phrase, text)
```

Expected: FAIL against the minimal Task 1 body.

- [ ] **Step 2: Write required reads and compatibility**

The completed SKILL.md must direct the agent to read all three references before generation. State compatibility requirements: filesystem write access, Python 3.11+, and a browser capable of desktop and explicit 390px viewport inspection. If browser capability is unavailable, the candidate may remain on disk but completion must be reported as “visual verification pending”.

- [ ] **Step 3: Write the eight-stage workflow**

Use these exact stage headings:

1. `Confirmed Input Gate`
2. `Visual Fact Model`
3. `Diagram Selection`
4. `Generate One HTML`
5. `Deterministic Validation`
6. `Desktop Visual Review`
7. `390px Mobile Review`
8. `Completion Gate`

Under the fact model, require theme, actors, boundaries, responsibilities, connections, order, states, success, failure/rollback, exclusions, and preserved names/counts/versions. Under generation, require one new file at the default or explicit path, no fixed template, and no overwrite. Under validation, run `scripts/validate_html.py` with each preserved fact as a repeated `--required-term`.

- [ ] **Step 4: Write stop gates and output wording**

Stop before generation for unchosen alternatives, source conflicts, missing sequence/state facts, unapproved overwrite, needed unspecified scans, or unapproved sensitive content. A successful response contains only a concise result, final absolute path, diagram types/count, and verification summary; it must not expose temporary artifacts as deliverables.

- [ ] **Step 5: Run tests and commit**

Expected: all skill and validator tests pass.

```powershell
git add -- visual-agent-copilot/technical-visual-companion/SKILL.md visual-agent-copilot/technical-visual-companion/scripts/tests/test_skill_contract.py
git commit -m "feat(visual): define companion generation workflow"
```

### Task 5: Integrate the Role Into Repository Documentation and CI

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`
- Create: `.github/workflows/visual-agent-copilot-ci.yml`

**Interfaces:**
- Consumes: installable path and tests from Tasks 1–4.
- Produces: discoverable role documentation, installation command, and Python 3.11 CI coverage.

- [ ] **Step 1: Add Visual Agent Copilot to both root READMEs**

Update repository structure, available skills, installation, and examples. The skill row uses:

```text
technical-visual-companion | Turn confirmed technical designs into one verified offline Visual Companion HTML with automatically selected diagrams.
```

The Chinese row uses:

```text
technical-visual-companion | 将已确认技术方案转化为一份经过离线、响应式和浏览器验收的 Visual Companion HTML。
```

Add the exact install command from Task 1 and one example request: “把这份已确认的部署方案生成一个静态 HTML，自动选择最合适的图。”

- [ ] **Step 2: Add focused CI**

Create a workflow named `Visual Agent Copilot CI`, triggered when `visual-agent-copilot/**` or its workflow changes. Use checkout v4, setup-python v5 with Python 3.11, then run:

```yaml
- name: Run visual companion tests
  run: python -m unittest discover visual-agent-copilot/technical-visual-companion/scripts/tests -p "test_*.py" -v
```

- [ ] **Step 3: Verify package discovery**

Run:

```powershell
npx.cmd skills add . --list
```

Expected: output includes `technical-visual-companion` at `visual-agent-copilot/technical-visual-companion`.

- [ ] **Step 4: Run tests, YAML text check, and diff check**

```powershell
C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover visual-agent-copilot/technical-visual-companion/scripts/tests -p "test_*.py" -v
Select-String -Path README.md,README.zh.md -Pattern 'visual-agent-copilot','technical-visual-companion'
git diff --check
```

Expected: tests pass, both names appear in both READMEs, and diff check is silent.

- [ ] **Step 5: Commit Task 5**

```powershell
git add -- README.md README.zh.md .github/workflows/visual-agent-copilot-ci.yml
git commit -m "docs: add visual agent copilot role"
```

### Task 6: Add the Three-Case Eval Set

**Files:**
- Create: `visual-agent-copilot/technical-visual-companion/evals/evals.json`
- Create: `visual-agent-copilot/technical-visual-companion/evals/files/complex-runtime-orchestration.md`
- Create: `visual-agent-copilot/technical-visual-companion/evals/files/simple-cache-migration.md`
- Create: `visual-agent-copilot/technical-visual-companion/evals/files/conflicting-release-flow.md`

**Interfaces:**
- Consumes: Skill Creator `evals.json` schema and the completed skill.
- Produces: one complex success case, one simple success case, and one mandatory stop case for paired evaluation.

- [ ] **Step 1: Write realistic confirmed and conflicting source fixtures**

The complex fixture contains an explicitly approved runtime orchestration design with boundary, synchronous sequence, two-phase service activation, success states, and rollback. Include stable facts such as exactly three dynamic services and nine persistent services.

The simple fixture contains a confirmed cache migration with exactly two components and three ordered steps, no state machine, and no rollback branch.

The conflicting fixture contains two mutually exclusive unresolved startup orders and labels both as pending selection.

- [ ] **Step 2: Write evals.json**

Use `skill_name: technical-visual-companion` and these exact eval intentions:

1. Complex input produces one HTML with 2–3 complementary diagrams, required terms, offline contract, and responsive layout.
2. Simple input produces one HTML with 1–2 diagrams and does not invent a state machine or third diagram.
3. Conflicting input produces no HTML and reports the unresolved startup-order conflict.

Each eval lists its fixture under `files`, a realistic user prompt that explicitly identifies the source file as confirmed or unresolved, and objective expectations plus one qualitative expectation about diagram choice.

- [ ] **Step 3: Validate eval JSON and review it with the user**

Run:

```powershell
C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m json.tool visual-agent-copilot/technical-visual-companion/evals/evals.json > $null
```

Expected: exit 0. Present the three prompts and expectations to the user before running evals; revise them if requested.

- [ ] **Step 4: Commit the approved eval set**

```powershell
git add -- visual-agent-copilot/technical-visual-companion/evals
git commit -m "test(visual): add companion evaluation cases"
```

### Task 7: Run Paired Evaluation, Human Review, and One Improvement Loop

**Files:**
- Create outside the repository: `D:\tmp\github\technical-visual-companion-workspace\iteration-1`
- Potentially modify after review: files under `visual-agent-copilot/technical-visual-companion/`

**Interfaces:**
- Consumes: three approved evals; one run with the skill and one baseline without the skill for each eval.
- Produces: outputs, timing, grading, benchmark, static review HTML, user feedback, and an evidence-backed skill revision if needed.

- [ ] **Step 1: Launch all six runs together**

For each eval, create descriptive directories (`complex-orchestration`, `simple-migration`, `conflicting-design`) with `with_skill/outputs` and `without_skill/outputs`. Dispatch the same prompt and fixture to paired workers in the same turn. The with-skill worker reads `visual-agent-copilot/technical-visual-companion/SKILL.md`; the baseline worker receives no skill path. Record `total_tokens` and `duration_ms` immediately in each `timing.json`.

- [ ] **Step 2: Grade objective expectations**

Run `validate_html.py` against generated HTML outputs, verify diagram counts and required terms, and verify no HTML exists for the conflict case. Write each `grading.json` using the exact `text`, `passed`, and `evidence` fields from Skill Creator schema.

- [ ] **Step 3: Aggregate the benchmark**

From `C:\Users\admin\.codex-clean-20260710\skills\skill-creator`, run:

```powershell
C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m scripts.aggregate_benchmark D:\tmp\github\technical-visual-companion-workspace\iteration-1 --skill-name technical-visual-companion
```

Expected: `benchmark.json` and `benchmark.md` contain with-skill and without-skill pass rate, time, and token summaries.

- [ ] **Step 4: Generate the static human review viewer**

```powershell
C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe C:\Users\admin\.codex-clean-20260710\skills\skill-creator\eval-viewer\generate_review.py D:\tmp\github\technical-visual-companion-workspace\iteration-1 --skill-name technical-visual-companion --benchmark D:\tmp\github\technical-visual-companion-workspace\iteration-1\benchmark.json --static D:\tmp\github\technical-visual-companion-workspace\iteration-1\review.html
```

Expected: the viewer shows paired HTML outputs, formal grades, and benchmark data. Ask the user to review visual clarity, diagram choice, template repetition, and factual fidelity.

- [ ] **Step 5: Apply one focused revision only when feedback identifies a real gap**

Translate feedback into a general rule in SKILL.md or the relevant reference. Do not special-case fixture names or copy an eval output into assets. Add or tighten a contract test when the feedback is objectively testable, then rerun all unit tests and all three paired evals into `iteration-2`.

- [ ] **Step 6: Commit the reviewed revision**

If files changed after review:

```powershell
git add -- visual-agent-copilot/technical-visual-companion
git commit -m "refactor(visual): improve companion generation guidance"
```

If feedback requires no change, record that result in the final handoff and do not create an empty commit.

### Task 8: Final Verification and Handoff

**Files:**
- Verify only; no required new file.

**Interfaces:**
- Consumes: reviewed skill, validator, tests, READMEs, CI, and evaluation result.
- Produces: a verified implementation branch ready for merge or PR.

- [ ] **Step 1: Run the complete unit suite**

```powershell
C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover visual-agent-copilot/technical-visual-companion/scripts/tests -p "test_*.py" -v
C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests -p "test_*.py" -v
```

Expected: all new visual tests and existing Project Develop Copilot tests pass.

- [ ] **Step 2: Verify package and repository documentation**

```powershell
npx.cmd skills add . --list
Select-String -Path README.md,README.zh.md,visual-agent-copilot/README.md,visual-agent-copilot/README.zh.md -Pattern 'technical-visual-companion'
git diff --check
```

Expected: package listing contains the skill, all four READMEs name it, and diff check is silent.

- [ ] **Step 3: Verify scope and Git cleanliness**

Confirm no fixed HTML template was added, no product code changed, no eval workspace was committed, and no unrelated main-worktree changes entered the branch. Run `git status --short` and inspect every remaining path.

- [ ] **Step 4: Report completion evidence**

The final handoff names the branch, commits, unit test counts, package discovery result, eval comparison, human review decision, and any remaining limitation. Do not claim the skill is complete if browser-based eval outputs were not reviewed by the user.
