# Project Develop Copilot Phase 0 Repository Integrity Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 Project Develop Copilot 建立独立、确定性、跨 Windows/Linux 一致的仓库文本与文档完整性门禁，并回迁已确认的 LLM Wiki Discovery 修正。

**Architecture:** 两个只依赖 Python 标准库的独立检查器分别负责文本字节/字符质量和 Markdown/Case/Eval 引用闭合；它们扫描 Project Develop Copilot Skill 根目录，通过现有 GitHub Actions 工作流执行，不进入消费项目的 LLM Wiki Doctor。Skill 行为变化通过旧版快照与新版的三组人工 Agent Eval 对照验证，临时评测工作区位于仓库外，不演变成 Phase 1 Lifecycle Runner。

**Tech Stack:** Python 3.11+ 标准库、`unittest`、Markdown、GitHub Actions、PowerShell、Skill Creator 静态 Review Viewer。

## Global Constraints

- `flow_id`: `pdc-phase0-repository-integrity`。
- 生产扫描根目录只允许是 `project-agent-copilot/project-develop-copilot`；不得默认扫描整个 monorepo。
- 新脚本不得引入第三方 Python 依赖、网络访问、本机安装目录依赖或自动修复写入。
- 阻断文本规则只包含严格 UTF-8、UTF-8 BOM、U+FFFD 和已确认的多字符 mojibake 序列；合法单字 `杩`、`绔`、`瀹`、`鍙` 不得单独触发。
- 已知 mojibake 必须在 Python 源码中写成 `\uNNNN` 转义；测试使用 `chr(0xFFFD)` 生成 replacement character，避免检查器扫描并阻断自身。
- Phase 0 不实现未校准阈值的异常字符密度 heuristic；以后若加入，它只能是 non-blocking 提示并需先有误报评测。
- Case ID 和 Eval ID 始终按字符串处理；允许非连续、append-only 顺序和 `9A`、`9B`、`9C`。
- Markdown Phase 0 只验证本地文件目标，不验证同文档 heading fragment 的 slug；外部 URL 不联网。
- 不重写 `evals/runs/` 历史报告，不重编号现有 Case/Eval。
- 不引入 Acceptance Manifest、Lifecycle Eval Runner、Trace Schema、Quick/Standard/Strict、Route Registry、Dashboard/状态/版本重构。
- 临时 Eval Workspace、快照、Agent 输出和 Review Viewer 不提交到仓库。
- 未获得用户单独授权前，不执行 commit、push、PR 或发布；每个任务以 diff 和测试证据代替 commit checkpoint。

## Command Convention

在当前 PowerShell 会话先解析 Python。普通开发机优先使用 PATH；Codex Desktop 无 PATH Python 时使用随应用提供的运行时。仓库文档不保存任何用户名或盘符绝对路径。

```powershell
$RepoRoot = (Get-Location).Path
$SkillRoot = Join-Path $RepoRoot 'project-agent-copilot\project-develop-copilot'
$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) {
    $Python = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
}
if (-not (Test-Path -LiteralPath $Python)) {
    throw 'Python 3.11 or newer is required.'
}
& $Python --version
```

Expected: 当前 Codex 环境输出 `Python 3.12.13`；CI 固定使用 Python 3.11。

## Context Handoff

- lifecycle_session: `.llm-wiki/requirements/pdc-phase0-repository-integrity.md`
- user_intent: 按已批准设计继续优化 Project Develop Copilot 的 Phase 0 仓库自一致性。
- active_sources: 校准后的正式改进计划、当前源码/测试/CI、一次性安装版差异。
- active_scope: Project Develop Copilot 文本修复、Discovery 规则、两个检查器、测试、现有 CI、相关状态文档。
- read_only_scope: 已安装 Skill、现有 LLM Wiki Doctor/scaffold、历史 Eval Run。
- candidate_scope: none。
- excluded_scope: Manifest、Runtime Runner、模式、Registry、Dashboard/状态/版本治理、其他 Copilot。
- current_gate: Work Definition Gate 已完成；进入 External Bridge Gate 的 `writing-plans` 产物审阅。
- requested_stage_or_bridge: 用户确认本计划后进入 `subagent-driven-development` 或 `executing-plans`。
- constraints: TDD、严格 UTF-8、无本机路径依赖、无 commit/push/PR。

## Task Index

1. 冻结旧版 Skill 并定义三组行为 Eval。
2. 以 TDD 新增文本质量检查器。
3. 以 TDD 新增 Markdown 与 Case/Eval 完整性检查器。
4. 修复已确认 mojibake 与 BOM 并让文本门禁转绿。
5. 回迁 Discovery 合同并校准 Acceptance/Eval 事实。
6. 扩展现有 CI，同时保留既有 Ubuntu 检查身份。
7. 运行旧版/新版 Skill 对照并生成静态 Review Viewer。
8. 完成验证、生命周期证据同步与交接。

## File Map

| Responsibility | Files |
|---|---|
| 文本质量门禁 | Create `project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py`; create `scripts/tests/test_check_text_quality.py` |
| 文档与 ID 门禁 | Create `project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py`; create `scripts/tests/test_check_doc_integrity.py` |
| 文本修复 | Modify root `SKILL.md`, `project-query/SKILL.md`, `project-session-extract/SKILL.md`, `references/session-digest.md`; remove the confirmed BOM from `references/change-brief.md` |
| Discovery 回迁 | Modify root `SKILL.md`, `project-query/SKILL.md`, `project-develop/SKILL.md`, `references/acceptance-cases.md`, `references/case11-project-query-run-2026-06-04.md` |
| Eval 与事实校准 | Modify `evals/project-develop-copilot-evals.md`, `evals/README.md`, `references/capability-gap-audit.md`, `references/project-develop-copilot-improvement-plan.zh.md` |
| CI | Modify `.github/workflows/project-develop-copilot-ci.yml` |
| 生命周期状态 | Modify `.llm-wiki/requirements/pdc-phase0-repository-integrity.md`, `.llm-wiki/index.md`, `.llm-wiki/log.md`, this working-context page |
| 临时行为评测 | Create only under sibling `../project-develop-copilot-phase0-eval-workspace/`; never add to repository |

## Dependency Order

```text
old-skill snapshot
    -> text checker red gate
    -> document checker tests
    -> mojibake/BOM repair + Discovery port
    -> documentation calibration
    -> CI integration
    -> old/new behavior eval + human review
    -> final verification and lifecycle sync
```

---

### Task 1: Freeze the Old Skill and Define the Three Behavior Evals

**Files:**

- Temporary create: `../project-develop-copilot-phase0-eval-workspace/skill-snapshot/`
- Temporary create: `../project-develop-copilot-phase0-eval-workspace/baseline-extract/`
- Temporary create: `../project-develop-copilot-phase0-eval-workspace/baseline-skill.tar`
- Temporary create: `../project-develop-copilot-phase0-eval-workspace/evals/evals.json`
- Temporary create: `../project-develop-copilot-phase0-eval-workspace/fixtures/wiki-with-index/`
- Temporary create: `../project-develop-copilot-phase0-eval-workspace/fixtures/wiki-without-index/`
- Repository changes: none

**Interfaces:**

- Consumes: current source Skill at baseline commit `3761b0f1379974a1798436ee6f3652dbe4679673`.
- Produces: immutable `old_skill` snapshot, three reviewed eval definitions, two privacy-safe fixtures.

- [ ] **Step 1: Export the exact baseline commit and refuse to overwrite an earlier snapshot**

```powershell
$RepoRoot = (Get-Location).Path
$BaselineCommit = '3761b0f1379974a1798436ee6f3652dbe4679673'
$SkillRelative = 'project-agent-copilot/project-develop-copilot'
$EvalWorkspace = Join-Path (Split-Path $RepoRoot -Parent) 'project-develop-copilot-phase0-eval-workspace'
$Snapshot = Join-Path $EvalWorkspace 'skill-snapshot'
$Archive = Join-Path $EvalWorkspace 'baseline-skill.tar'
$ExtractRoot = Join-Path $EvalWorkspace 'baseline-extract'
foreach ($target in @($Snapshot, $Archive, $ExtractRoot)) {
    if (Test-Path -LiteralPath $target) {
        throw "Baseline artifact already exists: $target"
    }
}
New-Item -ItemType Directory -Path $EvalWorkspace -Force | Out-Null
git cat-file -e "$BaselineCommit^{commit}"
if ($LASTEXITCODE -ne 0) { throw "Baseline commit is unavailable: $BaselineCommit" }
git archive --format=tar --output=$Archive $BaselineCommit -- $SkillRelative
if ($LASTEXITCODE -ne 0) { throw 'git archive failed' }
New-Item -ItemType Directory -Path $ExtractRoot | Out-Null
& tar.exe -xf $Archive -C $ExtractRoot
if ($LASTEXITCODE -ne 0) { throw 'baseline archive extraction failed' }
$ExportedSkill = Join-Path $ExtractRoot 'project-agent-copilot\project-develop-copilot'
if (-not (Test-Path -LiteralPath (Join-Path $ExportedSkill 'SKILL.md'))) {
    throw 'The baseline archive does not contain the expected Skill root.'
}
Copy-Item -LiteralPath $ExportedSkill -Destination $Snapshot -Recurse
```

Expected: the snapshot contains only files tracked under the Skill path at the named baseline commit. It cannot absorb the untracked improvement plan or lifecycle documents from the current worktree.

- [ ] **Step 2: Create privacy-safe fixture content with `apply_patch`**

`fixtures/wiki-with-index/.llm-wiki/index.md`:

```markdown
# Fixture Wiki

- [Payment callback](requirements/payment-callback.md)
```

`fixtures/wiki-with-index/.llm-wiki/requirements/payment-callback.md`:

```markdown
# Payment Callback

The callback requirement is discussion-only in this fixture. No implementation or dashboard update is authorized.
```

`fixtures/wiki-without-index/.llm-wiki/README.md`:

```markdown
# Fixture Wiki Without Root Index

Use the available module and requirement entrypoints. The missing root index is intentional.
```

`fixtures/wiki-without-index/.llm-wiki/modules/index.md`:

```markdown
# Modules

- payment
```

`fixtures/wiki-without-index/.llm-wiki/requirements/payment-callback.md`:

```markdown
# Payment Callback

The callback context is available even though `.llm-wiki/index.md` is absent.
```

- [ ] **Step 3: Create the temporary eval set with `apply_patch`**

```json
{
  "skill_name": "project-develop-copilot",
  "evals": [
    {
      "id": 1,
      "prompt": "这个 skill 为什么跑偏？这次任务明明只想讨论，却创建了 Change Brief。先不要改文件，评估一下路由、Gate 和 handoff，找最小修正。",
      "expected_output": "识别 lifecycle-quality 意图，进入 project-review、evaluator 或 Dolores bridge，保持零写入且不直接修 Skill。",
      "files": [],
      "expectations": [
        "The route is lifecycle-quality rather than ordinary code review.",
        "The response examines routing, gates, scope, verification, or handoff.",
        "No file is created or modified."
      ]
    },
    {
      "id": 2,
      "prompt": "基于这个项目的 llm wiki，帮我找支付回调相关的需求、开发文档和之前讨论。先讨论，不要开发，也不要刷新 dashboard。",
      "expected_output": "选择 read-only-query/project-query，命名使用的 Wiki 页面并保持 fixture 零写入。",
      "files": [
        "fixtures/wiki-with-index/.llm-wiki/index.md",
        "fixtures/wiki-with-index/.llm-wiki/requirements/payment-callback.md"
      ],
      "expectations": [
        "The route is read-only-query with project-query as the primary stage.",
        "The answer names the wiki evidence it used.",
        "No Change Brief, dashboard update, code change, or fixture change occurs."
      ]
    },
    {
      "id": 3,
      "prompt": "这个项目已有 .llm-wiki 目录，但故意没有根 index.md。请判断它有没有项目 Wiki，并从可用入口找出支付回调上下文；不要创建 index.md，也不要改文件。",
      "expected_output": "把 .llm-wiki 目录识别为 Wiki，读取 README、modules 或 requirement 入口，不声称 Wiki 不存在且保持零写入。",
      "files": [
        "fixtures/wiki-without-index/.llm-wiki/README.md",
        "fixtures/wiki-without-index/.llm-wiki/modules/index.md",
        "fixtures/wiki-without-index/.llm-wiki/requirements/payment-callback.md"
      ],
      "expectations": [
        "The existing .llm-wiki directory is recognized as a project wiki.",
        "Available entrypoints are read even though the root index is absent.",
        "The response does not go source-first and does not create or modify files."
      ]
    }
  ]
}
```

- [ ] **Step 4: Verify snapshot fidelity and repository isolation**

Run:

```powershell
$ExportedSkill = Join-Path $ExtractRoot 'project-agent-copilot\project-develop-copilot'
git diff --no-index --exit-code -- $ExportedSkill $Snapshot
if ($LASTEXITCODE -ne 0) { throw 'Snapshot differs from the baseline export.' }
$BaselineSpec = '{0}:{1}/SKILL.md' -f $BaselineCommit, $SkillRelative
$ExpectedBlob = git rev-parse $BaselineSpec
$ActualBlob = git hash-object (Join-Path $Snapshot 'SKILL.md')
if ($ExpectedBlob -ne $ActualBlob) { throw 'Snapshot SKILL.md blob does not match the baseline commit.' }
git status --short
```

Expected: the extracted tree and snapshot are identical, the root `SKILL.md` blob matches the baseline commit, and repository status contains no Eval Workspace path.

- [ ] **Step 5: Review checkpoint**

Record the snapshot path and eval IDs in the task transcript. Do not commit or stage either workspace.

---

### Task 2: Add the Deterministic Text Quality Checker with TDD

**Files:**

- Create: `project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py`
- Create: `project-agent-copilot/project-develop-copilot/scripts/tests/test_check_text_quality.py`

**Interfaces:**

- Consumes: one Skill root directory.
- Produces: `list[Finding]`, sorted diagnostics, CLI exit 0 for clean and 1 for blocking findings.
- Public surface:
  - `iter_text_files(root: Path) -> list[Path]`
  - `scan_file(root: Path, path: Path) -> list[Finding]`
  - `run_checks(root: str | Path) -> list[Finding]`
  - `format_finding(finding: Finding) -> str`
  - `main(argv: list[str] | None = None) -> int`

- [ ] **Step 1: Write seven failing unit tests**

Create tests with these exact method names and assertions:

```python
import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_text_quality.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_text_quality", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TextQualityTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checker = load_checker()

    def write(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_bytes(self, relative_path: str, content: bytes) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def test_clean_simplified_traditional_and_legal_single_characters_pass(self):
        content = "正常中文與繁體中文 " + " ".join(chr(value) for value in (0x6769, 0x7ED4, 0x7039, 0x9359))
        self.write("clean.md", content)
        self.assertEqual([], self.checker.run_checks(self.root))

    def test_invalid_utf8_and_utf8_bom_are_blocking(self):
        self.write_bytes("bad.md", b"line one\n\xff")
        self.write_bytes("bom.md", b"\xef\xbb\xbf# heading\n")
        self.write("locked.md", "content")
        original_read_bytes = Path.read_bytes

        def guarded_read_bytes(path):
            if path.name == "locked.md":
                raise OSError("denied")
            return original_read_bytes(path)

        with mock.patch.object(Path, "read_bytes", guarded_read_bytes):
            rules = {finding.rule_id for finding in self.checker.run_checks(self.root)}
        self.assertEqual({"file-read-error", "invalid-utf8", "utf8-bom"}, rules)

    def test_replacement_character_is_blocking(self):
        self.write("replacement.md", "clean\n" + chr(0xFFFD) + "\n")
        self.assertEqual("unicode-replacement-character", self.checker.run_checks(self.root)[0].rule_id)

    def test_known_multichar_mojibake_is_blocking(self):
        value = "".join(chr(codepoint) for codepoint in (0x6769, 0x6B0E, 0x91DC))
        self.write("mojibake.md", value)
        self.assertEqual("known-mojibake-sequence", self.checker.run_checks(self.root)[0].rule_id)

    def test_binary_and_generated_directories_are_ignored(self):
        self.write_bytes("image.png", b"\xff\x00")
        self.write_bytes("build/generated.md", b"\xff")
        self.assertEqual([], self.checker.run_checks(self.root))

    def test_findings_continue_across_files_and_sort_stably(self):
        self.write("z.md", chr(0xFFFD))
        self.write_bytes("a.md", b"\xef\xbb\xbftext")
        findings = self.checker.run_checks(self.root)
        self.assertEqual(["a.md", "z.md"], [finding.path for finding in findings])

    def test_cli_exit_and_output_contract(self):
        self.write("clean.md", "clean")
        clean_output = io.StringIO()
        with contextlib.redirect_stdout(clean_output):
            clean_status = self.checker.main(["--root", str(self.root)])
        self.assertEqual(0, clean_status)
        self.assertEqual("text quality: no findings\n", clean_output.getvalue())
        self.write("bad.md", chr(0xFFFD))
        bad_output = io.StringIO()
        with contextlib.redirect_stdout(bad_output):
            bad_status = self.checker.main(["--root", str(self.root)])
        self.assertEqual(1, bad_status)
        self.assertIn("bad.md:1: unicode-replacement-character:", bad_output.getvalue())
```

The test helper must import the script with `importlib.util`, create a `TemporaryDirectory`, and write all fixture files relative to that directory. Do not place literal blocked sequences or literal U+FFFD in the test source.

- [ ] **Step 2: Run the focused suite and verify RED**

Run:

```powershell
& $Python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests -p 'test_check_text_quality.py' -v
```

Expected: ERROR because `check_text_quality.py` does not exist.

- [ ] **Step 3: Implement the minimal checker**

Create the complete script below. Keep the blocked sequences escaped in source so the checker does not flag itself.

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MANAGED_SUFFIXES = frozenset({".md", ".py", ".yml", ".yaml", ".json", ".html", ".txt"})
MANAGED_FILENAMES = frozenset({"VERSION", "pre-commit-llm-wiki-doctor"})
EXCLUDED_DIRS = frozenset({".git", "__pycache__", ".pytest_cache", "node_modules", "dist", "build"})

KNOWN_MOJIBAKE_SEQUENCES = (
    ("PDC-MOJIBAKE-001", "\u6769\u6b0e\u91dc"),
    ("PDC-MOJIBAKE-002", "\u7f01\u0445\u753b"),
    ("PDC-MOJIBAKE-003", "\u9369\u8f70\u7c2c"),
    ("PDC-MOJIBAKE-004", "\u6924\u572d\u6d30"),
    ("PDC-MOJIBAKE-005", "\u752f\ue1bd\u579c"),
    ("PDC-MOJIBAKE-006", "\u934f\u581f\u59b8"),
    ("PDC-MOJIBAKE-007", "\u93c7\u5b58\u67ca"),
    ("PDC-MOJIBAKE-008", "\u9352\u950b\u67ca"),
    ("PDC-MOJIBAKE-009", "\u935a\u5c7e\ue11e"),
    ("PDC-MOJIBAKE-010", "\u93b6\u5a41\u7ba3"),
    ("PDC-MOJIBAKE-011", "\u6d60\u5ea4\u7e56"),
    ("PDC-MOJIBAKE-012", "\u935a\u5c7c\u7c28"),
    ("PDC-MOJIBAKE-013", "\u93b4\u621c\u7b09"),
    ("PDC-MOJIBAKE-014", "\u93b6\u5a45\u7e56"),
    ("PDC-MOJIBAKE-015", "\u93b4\u621c\u7ca0"),
    ("PDC-MOJIBAKE-016", "\u5be4\u9e3f\ue185"),
    ("PDC-MOJIBAKE-017", "\u9359\ue21e\u20ac\u590a"),
    ("PDC-MOJIBAKE-018", "\u6d93\u5d85\u7f13\u7481"),
    ("PDC-MOJIBAKE-019", "\u6d93\u5b29\u7af4\u59dd"),
    ("PDC-MOJIBAKE-020", "\u6d93\u5b2e\u6f70"),
    ("PDC-MOJIBAKE-021", "\u7487\u5cf0\u61a1"),
)


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    rule_id: str
    message: str


def iter_text_files(root: Path) -> list[Path]:
    root = root.resolve()
    files: list[Path] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part.lower() in EXCLUDED_DIRS for part in relative.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in MANAGED_SUFFIXES or path.name in MANAGED_FILENAMES:
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def scan_file(root: Path, path: Path) -> list[Finding]:
    root = root.resolve()
    relative = path.relative_to(root).as_posix()
    try:
        raw = path.read_bytes()
    except OSError as error:
        return [Finding(relative, 1, "file-read-error", f"unable to read file: {type(error).__name__}")]

    findings: list[Finding] = []
    if raw.startswith(b"\xef\xbb\xbf"):
        findings.append(Finding(relative, 1, "utf8-bom", "leading UTF-8 BOM"))

    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        line = raw[: error.start].count(b"\n") + 1
        findings.append(
            Finding(relative, line, "invalid-utf8", f"invalid UTF-8 at byte {error.start}")
        )
        return sorted(findings)

    for line_number, line in enumerate(text.splitlines(), start=1):
        if chr(0xFFFD) in line:
            findings.append(
                Finding(
                    relative,
                    line_number,
                    "unicode-replacement-character",
                    "contains Unicode replacement character",
                )
            )
        for sequence_id, sequence in KNOWN_MOJIBAKE_SEQUENCES:
            if sequence in line:
                findings.append(
                    Finding(
                        relative,
                        line_number,
                        "known-mojibake-sequence",
                        f"contains {sequence_id}",
                    )
                )
    return sorted(findings)


def run_checks(root: str | Path) -> list[Finding]:
    resolved = Path(root).resolve()
    if not resolved.is_dir():
        return [Finding(".", 1, "invalid-root", "root is not a directory")]
    findings: list[Finding] = []
    for path in iter_text_files(resolved):
        findings.extend(scan_file(resolved, path))
    return sorted(findings)


def format_finding(finding: Finding) -> str:
    return f"{finding.path}:{finding.line}: {finding.rule_id}: {finding.message}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Project Develop Copilot text quality.")
    parser.add_argument("--root", type=Path, default=SKILL_ROOT)
    args = parser.parse_args(argv)
    findings = run_checks(args.root)
    if not findings:
        print("text quality: no findings")
        return 0
    for finding in findings:
        print(format_finding(finding))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

This implementation records `file-read-error` and returns to the outer loop, so one unreadable file cannot hide findings in later files. The anomaly-density heuristic remains explicitly deferred by the Change Brief and design; this deterministic checker has no warning-only channel.

- [ ] **Step 4: Run the focused suite and verify GREEN**

Expected: `Ran 7 tests` and `OK`.

- [ ] **Step 5: Prove the gate catches the current repository before repair**

Run:

```powershell
& $Python project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py --root project-agent-copilot/project-develop-copilot
```

Expected: exit 1 with stable `known-mojibake-sequence` findings in the four already-confirmed mojibake files plus one `utf8-bom` finding in `references/change-brief.md`; valid single-character fixture remains clean.

- [ ] **Step 6: Review checkpoint**

Run `git diff --check` and inspect only the two new checker/test files. Do not commit.

---

### Task 3: Add the Markdown and Case/Eval Integrity Checker with TDD

**Files:**

- Create: `project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py`
- Create: `project-agent-copilot/project-develop-copilot/scripts/tests/test_check_doc_integrity.py`

**Interfaces:**

- Consumes: Markdown under one Skill root.
- Produces: deterministic local-link and canonical Case/Eval reference findings.
- Public surface:
  - `iter_markdown_files(root: Path) -> list[Path]`
  - `read_markdown_files(root: Path) -> tuple[dict[Path, str], list[Finding]]`
  - `collect_definitions(root: Path, documents: dict[Path, str]) -> tuple[set[str], set[str], list[Finding]]`
  - `check_local_links(root: Path, documents: dict[Path, str]) -> list[Finding]`
  - `check_case_eval_references(root: Path, documents: dict[Path, str], case_ids: set[str], eval_ids: set[str]) -> list[Finding]`
  - `run_checks(root: str | Path) -> list[Finding]`
  - `main(argv: list[str] | None = None) -> int`

- [ ] **Step 1: Write ten failing tests**

Use this complete fixture and test shape. Canonical definitions remain limited to the two named files; historical headings must not become definitions.

````python
import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_doc_integrity.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_doc_integrity", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DocIntegrityTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checker = load_checker()
        self.write("references/acceptance-cases.md", "")
        self.write("evals/project-develop-copilot-evals.md", "")

    def write(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_bytes(self, relative_path: str, content: bytes) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def findings(self):
        return self.checker.run_checks(self.root)

    def test_valid_file_image_anchor_query_and_fragment_pass(self):
        self.write("docs/target file.md", "# Target\n")
        self.write_bytes("docs/image.png", b"PNG")
        self.write(
            "docs/source.md",
            "[target](target%20file.md?view=1#target)\n![image](image.png)\n[anchor](#local)\n",
        )
        self.assertEqual([], self.findings())

    def test_missing_or_outside_root_local_link_fails(self):
        self.write("docs/Target.md", "# Target\n")
        self.write(
            "docs/source.md",
            "[missing](missing.md)\n[wrong case](target.md)\n[outside](../../escape.md)\n[drive](C" + ":/temp.md)\n",
        )
        self.assertEqual(
            ["broken-local-link"] * 4,
            [finding.rule_id for finding in self.findings()],
        )

    def test_external_uri_and_links_inside_fenced_or_inline_code_are_ignored(self):
        self.write(
            "docs/source.md",
            "[web](https://example.com)\n[mail](mailto:test@example.com)\n`[inline](missing.md)`\n```text\n[fenced](missing.md)\n```\n",
        )
        self.assertEqual([], self.findings())

    def test_duplicate_case_id_fails(self):
        self.write(
            "references/acceptance-cases.md",
            "## Case 1: First\n## Case 1: Duplicate\n",
        )
        self.assertIn("duplicate-case-id", {finding.rule_id for finding in self.findings()})

    def test_duplicate_eval_id_fails(self):
        self.write(
            "evals/project-develop-copilot-evals.md",
            "## Eval 1: First\n## Eval 1: Duplicate\n",
        )
        self.assertIn("duplicate-eval-id", {finding.rule_id for finding in self.findings()})

    def test_plural_completion_rule_and_capability_missing_case_fail(self):
        self.write(
            "references/acceptance-cases.md",
            "## Case 1: Defined\n## Completion Rule\nPass Cases 1, 2, and 9A.\n",
        )
        self.write("references/capability-gap-audit.md", "Run Case 2 before release.\n")
        missing = [finding.message for finding in self.findings() if finding.rule_id == "missing-case-reference"]
        self.assertTrue(any("2" in message for message in missing))
        self.assertTrue(any("9A" in message for message in missing))

    def test_missing_eval_reference_fails(self):
        self.write("evals/project-develop-copilot-evals.md", "## Eval 1: Defined\n")
        self.write("evals/README.md", "Run Eval 2 before changing the rule.\n")
        self.assertIn("missing-eval-reference", {finding.rule_id for finding in self.findings()})

    def test_reference_parser_ignores_totals_and_dates(self):
        self.write(
            "references/acceptance-cases.md",
            "## Case 9A: Lettered A\n## Case 9B: Lettered B\n## Case 10: Fixture\n",
        )
        self.write(
            "references/summary.md",
            "Case 9A/9B/9C has 39 definitions. Acceptance Case 10 passed on 2026-06-04.\n",
        )
        missing = [
            finding.message
            for finding in self.findings()
            if "missing-case-reference" == finding.rule_id
        ]
        self.assertEqual(["Case 9C has no canonical definition"], missing)
        self.assertFalse(any(value in message for message in missing for value in ("39", "2026", "06", "04")))
        self.write(
            "references/acceptance-cases.md",
            "## Case 9A: Lettered A\n## Case 9B: Lettered B\n## Case 9C: Lettered C\n"
            "## Case 10: Fixture\n",
        )
        missing = [finding for finding in self.findings() if "missing-case-reference" == finding.rule_id]
        self.assertEqual([], missing)

    def test_invalid_utf8_and_file_read_error_are_blocking(self):
        self.write_bytes("docs/bad.md", b"line one\n\xff")
        self.write("docs/locked.md", "content")
        self.assertIn("invalid-utf8", {finding.rule_id for finding in self.findings()})
        original_read_bytes = Path.read_bytes

        def guarded_read_bytes(path):
            if path.name == "locked.md":
                raise OSError("denied")
            return original_read_bytes(path)

        with mock.patch.object(Path, "read_bytes", guarded_read_bytes):
            _, read_findings = self.checker.read_markdown_files(self.root)
        self.assertIn("file-read-error", {finding.rule_id for finding in read_findings})

    def test_non_contiguous_and_9a_9b_9c_ids_pass_with_stable_cli_output(self):
        self.write(
            "references/acceptance-cases.md",
            "## Case 9: Base\n## Completion Rule\nPass Cases 9, 9A, 9B, and 9C.\n"
            "## Case 9A: A\n## Case 9B: B\n## Case 9C: C\n",
        )
        self.write("evals/project-develop-copilot-evals.md", "## Eval 1: Defined\n## Eval 3: Gap Allowed\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = self.checker.main(["--root", str(self.root)])
        self.assertEqual(0, status)
        self.assertEqual("document integrity: no findings\n", output.getvalue())
````

- [ ] **Step 2: Run the focused suite and verify RED**

Run:

```powershell
& $Python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests -p 'test_check_doc_integrity.py' -v
```

Expected: ERROR because `check_doc_integrity.py` does not exist.

- [ ] **Step 3: Implement the exact parser boundaries**

Create the complete script below. Its reference grammar is deliberately narrow: every `Case/Cases/Eval/Evals` marker consumes only the immediately adjacent connector-delimited ID list. Supported connectors are `/`, `、`, English/Chinese commas, `and/or`, and numeric range separators. Ordinary prose terminates the list, so totals and dates are not reinterpreted as IDs.

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


SKILL_ROOT = Path(__file__).resolve().parents[1]
CASE_DEFINITIONS = Path("references/acceptance-cases.md")
EVAL_DEFINITIONS = Path("evals/project-develop-copilot-evals.md")
REFERENCE_SCAN_EXCLUDED_PREFIXES = ("evals/runs/",)
EXCLUDED_DIRS = frozenset({".git", "__pycache__", ".pytest_cache", "node_modules", "dist", "build"})

ID_PATTERN = r"\d{1,3}[A-Z]?"
LIST_SEPARATOR_PATTERN = (
    r"(?:\s*(?:/|、|[-–])\s*|\s*(?:,|，)\s*(?:(?:and|or)\s+)?|"
    r"\s+(?:and|or|to|through)\s+)"
)
HEADING_RE = re.compile(
    rf"^\s{{0,3}}#{{2,6}}\s+(Case|Eval)\s+({ID_PATTERN})\s*:",
    re.IGNORECASE,
)
REFERENCE_LIST_RE = re.compile(
    rf"\b(Cases?|Evals?)\s+({ID_PATTERN}(?:{LIST_SEPARATOR_PATTERN}{ID_PATTERN})*)",
    re.IGNORECASE,
)
REFERENCE_ID_RE = re.compile(rf"\b{ID_PATTERN}\b", re.IGNORECASE)
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\n]+)\)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
DRIVE_PATH_RE = re.compile(r"^[A-Za-z]:[\\/]")
URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    rule_id: str
    message: str


def iter_markdown_files(root: Path) -> list[Path]:
    root = root.resolve()
    files: list[Path] = []
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if any(part.lower() in EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.is_file():
            files.append(path.resolve())
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def read_markdown_files(root: Path) -> tuple[dict[Path, str], list[Finding]]:
    root = root.resolve()
    documents: dict[Path, str] = {}
    findings: list[Finding] = []
    for path in iter_markdown_files(root):
        relative = path.relative_to(root).as_posix()
        try:
            raw = path.read_bytes()
        except OSError as error:
            findings.append(
                Finding(relative, 1, "file-read-error", f"unable to read file: {type(error).__name__}")
            )
            continue
        try:
            documents[path] = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            line = raw[: error.start].count(b"\n") + 1
            findings.append(
                Finding(relative, line, "invalid-utf8", f"invalid UTF-8 at byte {error.start}")
            )
    return documents, sorted(findings)


def strip_code(text: str) -> str:
    output: list[str] = []
    open_fence: tuple[str, int] | None = None
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if open_fence is None and match:
            fence = match.group(1)
            open_fence = (fence[0], len(fence))
            output.append("")
            continue
        if open_fence is not None:
            if (
                match
                and match.group(1)[0] == open_fence[0]
                and len(match.group(1)) >= open_fence[1]
                and not match.group(2).strip()
            ):
                open_fence = None
            output.append("")
            continue
        output.append(INLINE_CODE_RE.sub("", line))
    return "\n".join(output)


def collect_definitions(
    root: Path,
    documents: dict[Path, str],
) -> tuple[set[str], set[str], list[Finding]]:
    root = root.resolve()
    case_ids: set[str] = set()
    eval_ids: set[str] = set()
    findings: list[Finding] = []
    canonical = ((CASE_DEFINITIONS, "case", case_ids), (EVAL_DEFINITIONS, "eval", eval_ids))
    for relative_path, expected_kind, registry in canonical:
        path = (root / relative_path).resolve()
        text = documents.get(path)
        if text is None:
            findings.append(
                Finding(
                    relative_path.as_posix(),
                    1,
                    "missing-definition-file",
                    "canonical definition file is missing or unreadable",
                )
            )
            continue
        for line_number, line in enumerate(strip_code(text).splitlines(), start=1):
            match = HEADING_RE.match(line)
            if not match or match.group(1).lower() != expected_kind:
                continue
            identifier = match.group(2).upper()
            if identifier in registry:
                findings.append(
                    Finding(
                        relative_path.as_posix(),
                        line_number,
                        f"duplicate-{expected_kind}-id",
                        f"duplicate {expected_kind} ID {identifier}",
                    )
                )
            else:
                registry.add(identifier)
    return case_ids, eval_ids, sorted(findings)


def _exists_with_exact_case(root: Path, candidate: Path) -> bool:
    try:
        relative = candidate.relative_to(root)
    except ValueError:
        return False
    current = root
    for part in relative.parts:
        try:
            names = {child.name for child in current.iterdir()}
        except OSError:
            return False
        if part not in names:
            return False
        current = current / part
    return current.exists()


def _local_link_is_broken(root: Path, source: Path, raw_target: str) -> bool | None:
    target = raw_target.strip()
    if target.startswith("<"):
        closing = target.find(">")
        if closing < 0:
            return True
        target = target[1:closing]
    else:
        pieces = target.split(maxsplit=1)
        target = pieces[0] if pieces else ""

    if not target or target.startswith("#") or target.startswith("//"):
        return None
    if DRIVE_PATH_RE.match(target):
        return True
    if URI_SCHEME_RE.match(target):
        return None
    if target.startswith(("/", "\\")):
        return True

    path_part = target.split("#", 1)[0].split("?", 1)[0]
    decoded = unquote(path_part).replace("\\", "/")
    if not decoded:
        return None
    if DRIVE_PATH_RE.match(decoded) or decoded.startswith(("/", "//")):
        return True

    parts = list(source.parent.relative_to(root).parts)
    for part in Path(decoded).parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return True
            parts.pop()
            continue
        parts.append(part)
    candidate = root.joinpath(*parts)
    try:
        candidate.resolve(strict=False).relative_to(root)
    except (OSError, ValueError):
        return True
    return not _exists_with_exact_case(root, candidate)


def check_local_links(root: Path, documents: dict[Path, str]) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    for source, text in sorted(
        documents.items(),
        key=lambda item: item[0].relative_to(root).as_posix(),
    ):
        relative = source.relative_to(root).as_posix()
        for line_number, line in enumerate(strip_code(text).splitlines(), start=1):
            for match in LINK_RE.finditer(line):
                if _local_link_is_broken(root, source, match.group(1)):
                    findings.append(
                        Finding(
                            relative,
                            line_number,
                            "broken-local-link",
                            f"unresolvable local target: {match.group(1).strip()}",
                        )
                    )
    return sorted(findings)


def _line_references(line: str) -> set[tuple[str, str]]:
    references: set[tuple[str, str]] = set()
    for match in REFERENCE_LIST_RE.finditer(line):
        kind = "case" if match.group(1).lower().startswith("case") else "eval"
        for identifier in REFERENCE_ID_RE.findall(match.group(2)):
            references.add((kind, identifier.upper()))
    return references


def check_case_eval_references(
    root: Path,
    documents: dict[Path, str],
    case_ids: set[str],
    eval_ids: set[str],
) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    for path, text in sorted(
        documents.items(),
        key=lambda item: item[0].relative_to(root).as_posix(),
    ):
        relative = path.relative_to(root).as_posix()
        if relative.startswith(REFERENCE_SCAN_EXCLUDED_PREFIXES):
            continue
        for line_number, line in enumerate(strip_code(text).splitlines(), start=1):
            for kind, identifier in sorted(_line_references(line)):
                registry = case_ids if kind == "case" else eval_ids
                if identifier in registry:
                    continue
                findings.append(
                    Finding(
                        relative,
                        line_number,
                        f"missing-{kind}-reference",
                        f"{kind.title()} {identifier} has no canonical definition",
                    )
                )
    return sorted(findings)


def run_checks(root: str | Path) -> list[Finding]:
    resolved = Path(root).resolve()
    if not resolved.is_dir():
        return [Finding(".", 1, "invalid-root", "root is not a directory")]
    documents, findings = read_markdown_files(resolved)
    case_ids, eval_ids, definition_findings = collect_definitions(resolved, documents)
    findings.extend(definition_findings)
    findings.extend(check_local_links(resolved, documents))
    findings.extend(check_case_eval_references(resolved, documents, case_ids, eval_ids))
    return sorted(findings)


def format_finding(finding: Finding) -> str:
    return f"{finding.path}:{finding.line}: {finding.rule_id}: {finding.message}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Project Develop Copilot documentation integrity.")
    parser.add_argument("--root", type=Path, default=SKILL_ROOT)
    args = parser.parse_args(argv)
    findings = run_checks(args.root)
    if not findings:
        print("document integrity: no findings")
        return 0
    for finding in findings:
        print(format_finding(finding))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

The `file-read-error` and `invalid-utf8` branches skip only the affected document and continue. External URIs never trigger network access. Fragment slug validation and heuristic density reporting remain out of scope.

- [ ] **Step 4: Run the focused suite and verify GREEN**

Expected: `Ran 10 tests` and `OK`.

- [ ] **Step 5: Run against the current Skill tree**

```powershell
& $Python project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py --root project-agent-copilot/project-develop-copilot
```

Expected before Task 5: exit 1 only for confirmed repository defects, including Case 12 being hidden by the stray fence after Case 11. The new total/date regression test must stay green: `39` and `2026-06-04` are not IDs. Record the current 31 Eval definitions; Task 5 repairs the fence and makes the repository scan green with all 39 Case definitions visible.

- [ ] **Step 6: Review checkpoint**

Inspect both new files, focused test output, and deterministic path casing behavior. Do not commit.

---

### Task 4: Repair Confirmed Mojibake and BOM and Make the Text Gate Green

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/SKILL.md:180-189`
- Modify: `project-agent-copilot/project-develop-copilot/project-query/SKILL.md:31-43`
- Modify: `project-agent-copilot/project-develop-copilot/project-session-extract/SKILL.md:49-55`
- Modify: `project-agent-copilot/project-develop-copilot/project-session-extract/SKILL.md:216-236`
- Modify: `project-agent-copilot/project-develop-copilot/references/session-digest.md:61-75`
- Rewrite bytes only: `project-agent-copilot/project-develop-copilot/references/change-brief.md` (remove leading UTF-8 BOM; preserve text)

**Interfaces:**

- Consumes: Task 2 red findings.
- Produces: valid Chinese trigger/output blocks, one BOM-free reference template, and a clean text-quality scan.

- [ ] **Step 1: Record the failing diagnostics before editing**

Run the Task 2 CLI and save its console output in the execution transcript. Expected findings cover the root Router, `project-query`, `project-session-extract`, `references/session-digest.md`, and the leading BOM in `references/change-brief.md`. Treat any additional file as new evidence to review before editing.

- [ ] **Step 2: Replace the root Router phrases with complete Chinese**

Required lifecycle-quality examples:

```text
"这个 skill 为什么跑偏？", "这个流程是不是跑偏了", "先不要直接改，评估一下"
```

Required ordinary delivery examples:

```text
"继续", "修 bug", "review 代码", "完成了吗", "总结一下"
```

- [ ] **Step 3: Replace the complete `project-query` trigger block**

The corrected Chinese entries must include exactly these meanings:

```text
基于这个项目的 llm wiki 回答
从项目 wiki 里找一下这个需求
这个功能之前有什么开发文档
帮我找到相关 requirement / bug / working-context
先把上下文找出来，我们讨论一下
这个项目里面，大疆 API 适配，直播相关的内容有哪些？如何通过 API 调用
更新项目看板
刷新 dashboard
同步项目状态页
```

- [ ] **Step 4: Replace both Session Digest candidate/output blocks**

Required trigger meanings:

```text
把之前的 session 总结一下导入 wiki
从这段历史聊天里提取后续可召回的上下文
同事之前和 AI 聊了很多，帮我沉淀到 llm-wiki
我不想重新开 session，想把旧会话的好内容内化
把这个 conversation / transcript / chat history 提纯成上下文摘要
```

Required preview headings and sentence:

```text
我从这段历史 session 中提取到这些候选上下文：
建议导入：
可选导入：
不建议导入：
下一步：
请告诉我要保留哪些条目。你选定后，我会先整理成 Session Digest Markdown 草稿，不会直接写入 `.llm-wiki`。
```

In both files, move the closing triple-backtick fence to its own line. In `project-session-extract/SKILL.md`, also restore: `下面是拟写入的 Session Digest 草稿。请确认是否写入 .llm-wiki/session-digests/<id>.md。`

- [ ] **Step 5: Remove only the confirmed BOM from the Change Brief template**

Use byte-preserving .NET decoding and UTF-8 without BOM; abort if the expected leading U+FEFF is absent:

```powershell
$Template = Join-Path $SkillRoot 'references\change-brief.md'
$StrictUtf8 = New-Object System.Text.UTF8Encoding($false, $true)
$Raw = [IO.File]::ReadAllBytes($Template)
$Text = $StrictUtf8.GetString($Raw)
if ($Text.Length -eq 0 -or [int]$Text[0] -ne 0xFEFF) {
    throw 'Expected leading UTF-8 BOM was not found; stop instead of rewriting.'
}
[IO.File]::WriteAllText($Template, $Text.Substring(1), (New-Object System.Text.UTF8Encoding($false)))
```

Verify the content after the first character is byte-for-byte equivalent to the pre-edit decoded text; no wording change belongs in this step.

- [ ] **Step 6: Run focused tests and the full text gate**

```powershell
& $Python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests -p 'test_check_text_quality.py' -v
& $Python project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py --root project-agent-copilot/project-develop-copilot
```

Expected: 7 tests pass; CLI prints `text quality: no findings` and exits 0.

- [ ] **Step 7: Review checkpoint**

Use `Get-Content -Encoding UTF8` for human inspection. Do not infer corruption from PowerShell 5.1 default decoding. Do not commit.

---

### Task 5: Port the Discovery Contract and Calibrate Acceptance/Eval Facts

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/SKILL.md:70-82`
- Modify: `project-agent-copilot/project-develop-copilot/project-query/SKILL.md:60-112`
- Modify: `project-agent-copilot/project-develop-copilot/project-develop/SKILL.md:183-191`
- Modify: `project-agent-copilot/project-develop-copilot/references/acceptance-cases.md:332-379`
- Modify: `project-agent-copilot/project-develop-copilot/references/case11-project-query-run-2026-06-04.md:9-39`
- Modify: `project-agent-copilot/project-develop-copilot/evals/project-develop-copilot-evals.md` by appending Eval 32
- Modify: `project-agent-copilot/project-develop-copilot/evals/README.md`
- Modify: `project-agent-copilot/project-develop-copilot/references/capability-gap-audit.md`

**Interfaces:**

- Consumes: verified installed-vs-source diff plus Tasks 2–4 gates.
- Produces: one source-owned Discovery contract, permanent manual Eval 32, accurate 39-Case/32-Eval facts.

- [ ] **Step 1: Add the root LLM Wiki Discovery Rule**

Insert after the Project Graph-first rule:

```markdown
## LLM Wiki Discovery Rule

Treat a discovered `.llm-wiki/` directory as proof that the project has an LLM Wiki. Do not use `.llm-wiki/index.md` as the existence sentinel.

When `.llm-wiki/index.md` is missing, report only that the root index is missing or optional, then continue with available wiki targets such as `.llm-wiki/README.md`, `.llm-wiki/log.md`, `.llm-wiki/modules/index.md`, `.llm-wiki/requirements/`, `.llm-wiki/bugs/`, `.llm-wiki/sources/`, `.llm-wiki/working-context/`, `.llm-wiki/artifacts/index.md`, and Project Graph files. Fall back to source only after checking the relevant available wiki entries or when the wiki evidence is insufficient or stale.
```

- [ ] **Step 2: Remove `project-query`'s hard `index.md first` dependency**

Make these exact contract changes:

- Required First Check treats `.llm-wiki/` itself as existence proof and `index.md` as optional navigation.
- Read list adds `.llm-wiki/README.md` and qualifies `.llm-wiki/index.md` with `when present`.
- Workflow builds an entrypoint map from available files and lightweight directories before deep reads.
- Ordinary query remains zero-write; only explicit `dashboard-refresh` may write its limited projection files.

- [ ] **Step 3: Port the remaining installed corrections without directory overwrite**

- `project-develop/SKILL.md`: Inputs list `.llm-wiki/README.md` and `.llm-wiki/index.md` when present.
- Acceptance Cases 11 and 12: resolve `.llm-wiki/` first, then available README/index/lightweight entrypoints.
- Acceptance Case 11: remove the stray closing code fence after its Failure signals so Case 12 remains a real Markdown heading and all 39 canonical Case definitions are parser-visible.
- `case11-project-query-run-2026-06-04.md`: update the documented lookup order to the same optional-index contract and ensure a final newline.

- [ ] **Step 4: Append permanent Eval 32**

````markdown
## Eval 32: Wiki Directory Exists Without Root Index

Input prompt:

```text
这个项目已经有 `.llm-wiki/README.md`、模块索引和需求文档，但故意没有 `.llm-wiki/index.md`。帮我从项目 Wiki 找支付回调上下文，先不要开发，也不要创建或修改文件。
```

Expected route:

```text
mode: read-only-query
primary_stage: project-query
```

Required behavior:

- Treats the existing `.llm-wiki/` directory as the local project Wiki.
- Reads available README, module, requirement, source, or working-context entrypoints before source fallback.
- States that the root index is optional or missing without claiming the Wiki is absent.
- Keeps the fixture and lifecycle state unchanged.

Forbidden behavior:

- Declaring that no project Wiki exists solely because `.llm-wiki/index.md` is missing.
- Going source-first before checking available Wiki entrypoints.
- Creating an index, Change Brief, dashboard update, artifact row, or code change.

Pass/fail:

```text
PASS: available Wiki entrypoints are used with zero writes
FAIL: Wiki absence is claimed, source-first routing occurs, or any file changes
```
````

- [ ] **Step 5: Calibrate capability and eval documentation**

- Repair malformed `north-star.md` text into real relative Markdown links.
- State that Acceptance numbering covers numeric 1–36 plus 9A/9B/9C, totaling 39 definitions.
- State that the manual Eval file has 32 definitions after Eval 32 and still has no automated Agent runner.
- Distinguish deterministic repository-integrity CI from deferred Agent lifecycle/runtime CI.
- Narrow `Do not build automated CI integration before Case 10 passes` to automated Agent lifecycle or Runtime Eval integration, so it does not contradict this deterministic static CI.
- Preserve ordinary `project-query` read-only behavior and explicit Dashboard Refresh authorization.

- [ ] **Step 6: Run both repository gates**

```powershell
& $Python project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py --root project-agent-copilot/project-develop-copilot
& $Python project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py --root project-agent-copilot/project-develop-copilot
$env:PDC_SKILL_ROOT = (Resolve-Path -LiteralPath $SkillRoot).Path
@'
import importlib.util
import os
import sys
from pathlib import Path

root = Path(os.environ["PDC_SKILL_ROOT"]).resolve()
module_path = root / "scripts" / "check_doc_integrity.py"
spec = importlib.util.spec_from_file_location("check_doc_integrity", module_path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

documents, read_findings = module.read_markdown_files(root)
case_ids, eval_ids, definition_findings = module.collect_definitions(root, documents)
if read_findings or definition_findings:
    raise SystemExit(f"definition scan findings: {read_findings + definition_findings}")

expected_cases = {str(value) for value in range(1, 37)} | {"9A", "9B", "9C"}
expected_evals = {str(value) for value in range(1, 33)}
if case_ids != expected_cases:
    raise SystemExit(
        f"Case set mismatch; missing={sorted(expected_cases - case_ids)}, "
        f"extra={sorted(case_ids - expected_cases)}"
    )
if not expected_evals.issubset(eval_ids) or len(eval_ids) != 32:
    raise SystemExit(
        f"Eval set mismatch; missing={sorted(expected_evals - eval_ids)}, "
        f"extra={sorted(eval_ids - expected_evals)}"
    )
print("canonical definitions: 39 Cases; 32 Evals")
'@ | & $Python -
if ($LASTEXITCODE -ne 0) { throw 'Canonical Case/Eval set assertion failed.' }
```

Expected: both gates print their clean success line and exit 0; the executable set assertion prints `canonical definitions: 39 Cases; 32 Evals`.

- [ ] **Step 7: Review checkpoint**

Run targeted `git diff --` on only the files in this task and compare the five installed-vs-source targets manually. Do not copy the installed directory wholesale and do not commit.

---

### Task 6: Extend the Existing CI Without Replacing It

**Files:**

- Modify: `.github/workflows/project-develop-copilot-ci.yml`

**Interfaces:**

- Consumes: all unit tests and both checker CLIs.
- Produces: the existing Ubuntu check plus a Windows repository-integrity check in the same workflow.

- [ ] **Step 1: Preserve existing workflow and job identity**

Keep workflow name `Project Develop Copilot CI`, job id `llm-wiki-doctor`, and display name `LLM Wiki Doctor script and scaffold`. Add the two checker steps after unit tests and before scaffold drift:

```yaml
      - name: Check repository text quality
        run: python project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py --root project-agent-copilot/project-develop-copilot

      - name: Check repository document integrity
        run: python project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py --root project-agent-copilot/project-develop-copilot
```

- [ ] **Step 2: Add a separate Windows job without renaming the protected Ubuntu check**

```yaml
  repository-integrity-windows:
    name: Repository integrity on Windows
    runs-on: windows-latest
    env:
      PYTHONUTF8: "1"
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Run repository integrity unit tests
        run: python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests

      - name: Check repository text quality
        run: python project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py --root project-agent-copilot/project-develop-copilot

      - name: Check repository document integrity
        run: python project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py --root project-agent-copilot/project-develop-copilot

      - name: Check scaffold drift
        run: python project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py --check
```

- [ ] **Step 3: Run the local equivalent on Windows**

```powershell
& $Python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests
& $Python project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py --root project-agent-copilot/project-develop-copilot
& $Python project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py --root project-agent-copilot/project-develop-copilot
& $Python project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py --check
```

Expected: 47 existing + 7 text + 10 document tests = `Ran 64 tests`, all OK; both gates exit 0; scaffold check exits 0.

- [ ] **Step 4: Review checkpoint**

Inspect YAML indentation and `git diff --check`. Do not add a second workflow and do not commit.

---

### Task 7: Run Old-vs-New Skill Evals and Generate the Static Review Viewer

**Files:**

- Temporary create: `../project-develop-copilot-phase0-eval-workspace/iteration-1/`
- Temporary create: `../project-develop-copilot-phase0-eval-workspace/iteration-1/review.html`
- Repository changes: none

**Interfaces:**

- Consumes: Task 1 `old_skill` snapshot, current `new_skill` source, three evals and independent fixture copies.
- Produces: per-run response, before/after directory comparison, timing, grading, aggregate benchmark, static viewer, human feedback.

- [ ] **Step 1: Materialize the exact Skill Creator directory contract**

Create this layout; `eval_metadata.json` is intentionally present both at the eval root for `aggregate_benchmark.py` and inside each run for `generate_review.py`.

```text
iteration-1/
  eval-1-lifecycle-quality/
    eval_metadata.json
    new_skill/run-1/
      eval_metadata.json
      inputs/pristine/
      inputs/project/
      outputs/
    old_skill/run-1/
      eval_metadata.json
      inputs/pristine/
      inputs/project/
      outputs/
  eval-2-read-only-query/
    eval_metadata.json
    new_skill/run-1/
      eval_metadata.json
      inputs/pristine/
      inputs/project/
      outputs/
    old_skill/run-1/
      eval_metadata.json
      inputs/pristine/
      inputs/project/
      outputs/
  eval-3-wiki-without-index/
    eval_metadata.json
    new_skill/run-1/
      eval_metadata.json
      inputs/pristine/
      inputs/project/
      outputs/
    old_skill/run-1/
      eval_metadata.json
      inputs/pristine/
      inputs/project/
      outputs/
```

Use `new_skill` and `old_skill` exactly. The aggregator discovers config directories alphabetically and computes the first minus the second; these names therefore make delta equal new minus old.

Prepare the directories from `evals/evals.json` with UTF-8 without BOM:

```powershell
$RepoRoot = (Get-Location).Path
$EvalWorkspace = Join-Path (Split-Path $RepoRoot -Parent) 'project-develop-copilot-phase0-eval-workspace'
$Snapshot = Join-Path $EvalWorkspace 'skill-snapshot'
$Iteration = Join-Path $EvalWorkspace 'iteration-1'
if (Test-Path -LiteralPath $Iteration) {
    throw 'iteration-1 already exists; review it before choosing a new iteration.'
}
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$EvalDefinitions = (Get-Content -LiteralPath (Join-Path $EvalWorkspace 'evals\evals.json') -Raw -Encoding UTF8 | ConvertFrom-Json).evals
$Slugs = @{ 1 = 'lifecycle-quality'; 2 = 'read-only-query'; 3 = 'wiki-without-index' }
$FixtureRoots = @{
    1 = $null
    2 = (Join-Path $EvalWorkspace 'fixtures\wiki-with-index')
    3 = (Join-Path $EvalWorkspace 'fixtures\wiki-without-index')
}
foreach ($eval in $EvalDefinitions) {
    $EvalDir = Join-Path $Iteration ('eval-{0}-{1}' -f $eval.id, $Slugs[[int]$eval.id])
    New-Item -ItemType Directory -Path $EvalDir -Force | Out-Null
    $Metadata = [ordered]@{
        eval_id = [int]$eval.id
        prompt = [string]$eval.prompt
        expected_output = [string]$eval.expected_output
        expectations = @($eval.expectations)
    }
    $MetadataJson = ($Metadata | ConvertTo-Json -Depth 8) + "`n"
    [IO.File]::WriteAllText((Join-Path $EvalDir 'eval_metadata.json'), $MetadataJson, $Utf8NoBom)
    foreach ($Configuration in @('new_skill', 'old_skill')) {
        $Run = Join-Path $EvalDir (Join-Path $Configuration 'run-1')
        New-Item -ItemType Directory -Path (Join-Path $Run 'outputs') -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $Run 'inputs') -Force | Out-Null
        [IO.File]::WriteAllText((Join-Path $Run 'eval_metadata.json'), $MetadataJson, $Utf8NoBom)
        $FixtureSource = $FixtureRoots[[int]$eval.id]
        foreach ($Name in @('pristine', 'project')) {
            $Destination = Join-Path $Run (Join-Path 'inputs' $Name)
            if ($null -eq $FixtureSource) {
                New-Item -ItemType Directory -Path $Destination | Out-Null
            } else {
                Copy-Item -LiteralPath $FixtureSource -Destination $Destination -Recurse
            }
        }
    }
}
```

Expected: six `run-1` directories, six run-local metadata files, and three eval-root metadata files.

- [ ] **Step 2: Execute three capacity-aware new/old pairs**

The runtime has four total agent slots, so run one eval's `new_skill` and `old_skill` workers concurrently, capture timing immediately, then repeat for the next eval. Do not use one worker to produce both sides. Resolve designated Skill roots as:

```powershell
$NewSkillRoot = Join-Path $RepoRoot 'project-agent-copilot\project-develop-copilot'
$OldSkillRoot = $Snapshot
```

Give each isolated worker this executor prompt, substituting the four bracketed values:

```text
You are one isolated Project Develop Copilot behavior-eval worker.

Designated Skill root: <new-or-old-skill-root>
Fixture project root: <run-dir>/inputs/project
Eval ID: <eval-id>
User prompt:
<eval-prompt>

Read and follow the designated Skill root's SKILL.md and only the references it routes you to. Treat the fixture project root as the user's project. Do not use another installed or source copy of Project Develop Copilot. Obey the user's read-only boundary: do not create, modify, rename, or delete fixture files. Return only the answer you would give the user; do not grade yourself and do not write benchmark artifacts.
```

The coordinator, not the eval worker, writes the returned answer to `outputs/response.md`, records wall-clock duration and token data when available in `timing.json`, and records observed tool-call/error counts in `outputs/metrics.json`. All JSON must be UTF-8 without BOM.

After every run compare the untouched fixture:

```powershell
$PristineFixture = Join-Path $Run 'inputs\pristine'
$RunFixture = Join-Path $Run 'inputs\project'
git diff --no-index --exit-code -- $PristineFixture $RunFixture
if ($LASTEXITCODE -ne 0) { throw "Read-only fixture changed: $Run" }
```

Each completed run must contain:

```text
eval_metadata.json
outputs/response.md
outputs/metrics.json
timing.json
grading.json
```

Do not require the old version to fail. The pass bar is that all `new_skill` runs pass and no new result is weaker than the paired `old_skill` result.

- [ ] **Step 3: Grade objective assertions with the exact schema**

For each run grade the expectations from its metadata using concrete response/tool/diff evidence. `grading.json` must have this complete shape:

```json
{
  "summary": {
    "pass_rate": 1.0,
    "passed": 3,
    "failed": 0,
    "total": 3
  },
  "expectations": [
    {
      "text": "verbatim expectation from eval_metadata.json",
      "passed": true,
      "evidence": "specific response, tool, or zero-diff evidence"
    }
  ],
  "execution_metrics": {
    "total_tool_calls": 0,
    "output_chars": 0,
    "errors_encountered": 0
  },
  "user_notes_summary": {
    "uncertainties": [],
    "needs_review": [],
    "workarounds": []
  }
}
```

`timing.json` must contain `total_duration_seconds` and `total_tokens`. Recalculate `summary` from the expectation array; do not type the example values blindly.

- [ ] **Step 4: Aggregate, verify the contract, and generate the static viewer**

```powershell
$SkillCreatorRoot = Join-Path $env:CODEX_HOME 'skills\skill-creator'
if (-not (Test-Path -LiteralPath (Join-Path $SkillCreatorRoot 'scripts\aggregate_benchmark.py'))) {
    throw 'Installed skill-creator scripts are unavailable.'
}
$env:ITERATION_PATH = $Iteration
Push-Location $SkillCreatorRoot
& $Python -m scripts.aggregate_benchmark $Iteration --skill-name project-develop-copilot
if ($LASTEXITCODE -ne 0) { throw 'Benchmark aggregation failed.' }
@'
import json
import os
from pathlib import Path
from scripts.aggregate_benchmark import generate_markdown

iteration = Path(os.environ["ITERATION_PATH"])
path = iteration / "benchmark.json"
data = json.loads(path.read_text(encoding="utf-8"))
runs = data["runs"]
assert len(runs) == 6, f"expected 6 runs, got {len(runs)}"
assert {run["eval_id"] for run in runs} == {1, 2, 3}
assert {run["configuration"] for run in runs} == {"new_skill", "old_skill"}
summary_order = [key for key in data["run_summary"] if key != "delta"]
assert summary_order == ["new_skill", "old_skill"], summary_order
data["metadata"]["runs_per_configuration"] = 1
data["metadata"]["executor_model"] = "Codex isolated subagents"
data["metadata"]["analyzer_model"] = "Codex coordinator plus human review"
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(iteration / "benchmark.md").write_text(generate_markdown(data), encoding="utf-8")
'@ | & $Python -
if ($LASTEXITCODE -ne 0) { throw 'Benchmark contract validation failed.' }
Pop-Location
& $Python (Join-Path $SkillCreatorRoot 'eval-viewer\generate_review.py') $Iteration --skill-name 'project-develop-copilot' --benchmark (Join-Path $Iteration 'benchmark.json') --static (Join-Path $Iteration 'review.html')
if ($LASTEXITCODE -ne 0) { throw 'Static review generation failed.' }
```

Expected: the benchmark contains six runs and both configs for eval IDs 1–3; `run_summary` orders `new_skill` before `old_skill` so delta is new minus old; `benchmark.json`, `benchmark.md`, and `review.html` exist outside the repository. Because each run has local metadata, the Viewer must show the real prompt rather than `(No prompt found)`.

- [ ] **Step 5: Human review gate**

Present the static viewer to the user. Do not claim behavior acceptance until the user reviews all three comparisons or explicitly accepts a documented limitation.

- [ ] **Step 6: Review checkpoint**

Confirm `git status --short` contains no Eval Workspace paths. Do not commit temporary outputs.

---

### Task 8: Run Final Verification and Sync Lifecycle Evidence

**Files:**

- Modify after evidence: `.llm-wiki/requirements/pdc-phase0-repository-integrity.md`
- Modify after evidence: `.llm-wiki/log.md`
- Modify after evidence: `project-agent-copilot/project-develop-copilot/references/project-develop-copilot-improvement-plan.zh.md`
- Read-only verification: all Phase 0 changed files

**Interfaces:**

- Consumes: Tasks 1–7 outputs plus user Eval review.
- Produces: evidence-backed development/testing status, residual-risk note, review-ready handoff.

- [ ] **Step 1: Run focused and full unit tests**

```powershell
& $Python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests -p 'test_check_text_quality.py' -v
& $Python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests -p 'test_check_doc_integrity.py' -v
& $Python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests
```

Expected after the whole-branch parser regressions: 7 focused text tests, 12 focused document tests, and 66 total tests all pass (19 focused checker tests in total).

- [ ] **Step 2: Run deterministic repository checks**

```powershell
& $Python project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py --root project-agent-copilot/project-develop-copilot
& $Python project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py --root project-agent-copilot/project-develop-copilot
& $Python project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py --check
git diff --check HEAD --
```

Expected: both checkers report no findings, scaffold drift exits 0, and Git reports no whitespace errors.

- [ ] **Step 3: Validate modified Skill packages**

```powershell
$SkillCreatorRoot = Join-Path $env:CODEX_HOME 'skills\skill-creator'
& $Python (Join-Path $SkillCreatorRoot 'scripts\quick_validate.py') project-agent-copilot/project-develop-copilot
& $Python (Join-Path $SkillCreatorRoot 'scripts\quick_validate.py') project-agent-copilot/project-develop-copilot/project-query
& $Python (Join-Path $SkillCreatorRoot 'scripts\quick_validate.py') project-agent-copilot/project-develop-copilot/project-develop
& $Python (Join-Path $SkillCreatorRoot 'scripts\quick_validate.py') project-agent-copilot/project-develop-copilot/project-session-extract
```

Expected: all four validations pass.

- [ ] **Step 4: Audit scope and encoding**

Build the audit set from both tracked differences against `HEAD` and untracked files, then independently decode that exact set. This closes the coverage gap left by the Skill-root checker for `.github` and `.llm-wiki`.

```powershell
$env:PHASE0_REPO_ROOT = $RepoRoot
@'
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

root = Path(os.environ["PHASE0_REPO_ROOT"]).resolve()
text_suffixes = {
    ".md", ".py", ".yml", ".yaml", ".json", ".html", ".txt",
    ".xml", ".toml", ".ini", ".cfg", ".ps1", ".sh",
}
text_names = {"VERSION", "pre-commit-llm-wiki-doctor"}
durable_wiki_prefix = ".llm-wiki/"
drive_path_re = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")
posix_home_re = re.compile(r"/(?:Users|home)/[^/\s`]+")


def git_paths(arguments: list[str]) -> list[str]:
    output = subprocess.run(
        ["git", "-c", "core.quotepath=false", *arguments],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    return [item.decode("utf-8") for item in output.split(b"\0") if item]


tracked = git_paths(["diff", "--name-only", "-z", "HEAD", "--"])
untracked = git_paths(["ls-files", "--others", "--exclude-standard", "-z"])
paths = sorted(set(tracked + untracked))
if not paths:
    raise SystemExit("scope audit unexpectedly found no changed or untracked files")

issues: list[str] = []
for relative in paths:
    path = root / relative
    print(relative)
    if not path.is_file():
        continue
    if path.suffix.lower() not in text_suffixes and path.name not in text_names:
        continue
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        issues.append(f"{relative}: utf8-bom")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        issues.append(f"{relative}:{error.start}: invalid-utf8")
        continue
    if chr(0xFFFD) in text:
        issues.append(f"{relative}: unicode-replacement-character")
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.rstrip(" \t") != line:
            issues.append(f"{relative}:{line_number}: trailing-whitespace")
        if relative.startswith(durable_wiki_prefix):
            if drive_path_re.search(line):
                issues.append(f"{relative}:{line_number}: workstation-drive-path")
            if posix_home_re.search(line):
                issues.append(f"{relative}:{line_number}: workstation-home-path")

print(f"changed_or_untracked={len(paths)}")
if issues:
    raise SystemExit("\n".join(issues))
print("changed-file encoding audit: no findings")
'@ | & $Python -
if ($LASTEXITCODE -ne 0) { throw 'Changed-file scope or encoding audit failed.' }
git status --short
git diff --stat HEAD --
git ls-files --others --exclude-standard
```

Review the printed union, not only `git diff`. The script rejects drive-letter and POSIX user-home paths from durable `.llm-wiki` text; generic documented placeholders such as `$CODEX_HOME` remain allowed. Confirm no installed Skill path, username, secret, temporary Eval Workspace, Manifest, permanent Runner, mode, Registry, Dashboard, state-schema, or version-governance file entered repository scope. The sibling Eval Workspace is allowed only as an external artifact and must not appear in the printed Git file list.

- [ ] **Step 5: Sync lifecycle facts only after evidence exists**

Update the Change Brief and log with:

- exact changed file list;
- 66-test result;
- both checker results;
- scaffold result;
- Skill validation result;
- old/new Eval review result and reviewer authority;
- residual risks, including any accepted behavior limitation.

Mark `development` and `testing` done only when their evidence exists. Keep `archive` pending until `project-finish` and `project-review` complete. Do not mark the whole flow done from this task alone.

- [ ] **Step 6: Return Handoff**

```markdown
## Return Handoff

- stage_or_bridge_used: project-develop + writing-plans + selected execution bridge
- result_summary: Phase 0 Repository Integrity Gate implemented and verified, or limited with explicit evidence
- changed_assumptions: canonical Acceptance count is 39 definitions; Eval count becomes 32
- recommended_scope_changes: none
- artifacts: checker scripts, tests, updated Skill contracts, CI evidence, temporary Review Viewer
- verification_notes: exact commands and outcomes from Steps 1–5
- external_dependencies: none
- lifecycle_updates_needed: project-finish, then project-review
- next_gate: Verification Gate / Finish Sync Gate / Review & Wiki Integrity Gate
```

- [ ] **Step 7: Stop before repository publication actions**

Report the verified local result and leave all changes uncommitted. Ask for separate authorization if the user wants commit, push, PR, or release work.

## Spec Coverage

| Approved requirement | Implemented by | Verified by |
|---|---|---|
| Strict UTF-8, no BOM, no U+FFFD, no confirmed mojibake | Tasks 2 and 4 | Tasks 2, 6, and 8 |
| Legal Chinese single characters do not block | Task 2 | Focused legal-character test and both CI platforms |
| Stable, complete diagnostics across files, including unreadable files | Tasks 2 and 3 | Focused `file-read-error`, ordering, and continuation tests |
| Uncalibrated anomaly-density heuristic does not become a blocker | Design/Brief deferral plus Tasks 2 and 8 | No heuristic rule in checker; scope review confirms no warning-only channel was invented |
| Local Markdown links and Case/Eval references close | Task 3 | Document checker tests, repository scan, Task 8 |
| Preserve numeric 1–36 plus 9A/9B/9C without renumbering | Tasks 3 and 5 | 39-definition repository assertion |
| Port `.llm-wiki/` directory discovery and optional root index | Task 5 | Acceptance 11/12, Eval 32, Task 7 no-index comparison |
| Ordinary Project Query stays read-only; Dashboard Refresh remains explicit | Task 5 | Existing Eval 2 plus Task 7 query comparison |
| Existing Doctor/scaffold behavior does not regress | Tasks 6 and 8 | 47 baseline tests, final 66-test suite, sync check |
| Existing CI runs deterministic gates | Task 6 | Ubuntu protected job plus Windows integrity job |
| Three old/new behavior comparisons receive human review | Tasks 1 and 7 | Static Review Viewer and reviewer feedback |
| Tracked and untracked files across Skill, `.github`, and `.llm-wiki` are audited | Task 8 | Exact Git union plus independent strict UTF-8/BOM/U+FFFD/trailing-whitespace pass |
| Draft fact errors are corrected without introducing a permanent Manifest/Runner | Tasks 3 and 5 | Both checkers, scope audit, lifecycle review |

Self-review result at planning time: every approved Phase 0 criterion has a task and verification owner; the final independent read-only review reported no blockers after the connector-list and canonical-set assertions were added.

## Plan Self-Review Checklist

- [x] Every approved Phase 0 acceptance criterion maps to at least one task.
- [x] Both checkers remain independent from `llm_wiki_doctor.py`.
- [x] The scanner root cannot pull unrelated Copilot modules into scope.
- [x] Case 1–36 plus 9A/9B/9C are treated as 39 definitions; Eval 32 is append-only.
- [x] Completion Rule parsing continues through definitions that appear later in the file.
- [x] Literal blocked mojibake and literal U+FFFD do not appear in scanned Python sources.
- [x] File read failures are tested, reported, and do not stop later files; anomaly-density heuristic remains explicitly deferred.
- [x] Local path comparison is case-exact and stable across Windows/Linux.
- [x] Installed Skill is read-only and absent from CI/runtime dependencies.
- [x] Temporary Eval assets stay outside the repository.
- [x] Eval layout supplies eval-root and run-local metadata, six `run-1` directories, and new-minus-old delta ordering.
- [x] Final audit unions `git diff HEAD` with untracked files before encoding checks.
- [x] No Manifest, Runner, mode, Registry, Dashboard/state/version refactor entered the plan.
- [x] No commit, push, PR, or completion claim occurs without user authorization and verification evidence.
