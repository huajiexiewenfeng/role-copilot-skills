# Minimum Skill Improvement Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the developer-only, product-neutral black-box evaluation sidecar for Project Develop Copilot Eval 2 and Eval 32, including Git evidence, deterministic grading, file-based Judge/Diagnosis contracts, review aging, and before/after reports.

**Architecture:** A single Python 3.11 standard-library CLI owns `prepare`, `grade`, and `report`. Canonical Eval Markdown remains normative; small JSON profiles provide executable parameters, disposable Git fixtures provide observable state, and Agent/Judge/Diagnosis inputs cross the boundary only through files. The runner never invokes an Agent, an LLM SDK, or a Skill patch operation.

**Tech Stack:** Python 3.11 standard library, Git CLI, JSON/Markdown, `unittest`, Windows and Ubuntu CI.

## Global Constraints

- Implement only Eval 2 and Eval 32.
- Keep ordinary Project Develop Copilot users and routing behavior unchanged.
- Use Python 3.11-compatible standard-library code; add no package dependency.
- Use Git subprocess argument arrays with `shell=False`; isolate global/system Git config.
- Keep `answer.md`, Judge files, reports, and all Run assets outside the Fixture Git repository.
- Keep all Run workspaces outside the source repository by default.
- Never call an Agent or online LLM from Python or CI.
- Never reset, clean, checkout, delete, patch, commit, push, or publish a Skill automatically.
- Preserve canonical Eval numbering and treat `evals/project-develop-copilot-evals.md` as normative.
- Record both canonical and effective Prompt hashes; label the appended canary question as a prompt variant.
- Use exactly three independent canary pairs per Fixture and require two adopted preferred observations.
- Treat all source/stale canaries as explicitly inactive legacy evidence, not current source truth.
- A source/stale literal never causes a deterministic FAIL; Judge adoption decides whether it was treated as current.
- Deterministic safety failures cannot be overridden by Judge.
- Use `quote-normalization-v1`; do not use fuzzy, semantic, edit-distance, or case-insensitive quote matching.
- Capture untracked content only up to 65,536 bytes per file and 1,048,576 bytes per Run.
- Do not follow symlinks, junctions, or reparse points while collecting evidence.
- Store JSON and Markdown as strict UTF-8 without BOM and with a final newline.
- Keep `RUN_ERROR`/`NEEDS_REVIEW` separate from PASS/PARTIAL/FAIL.
- Freeze and verify the baseline artifact hash manifest when a valid diagnosis is first accepted, before reading any separate Human Patch decision.
- Canned answers prove only Grader/Harness mechanics; the manual Agent smoke gate completes Level A, and only a real approved before/after failure can prove `Improvement Loop Proven`.

## Working Directory And Test Interpreter

Run all commands from the repository root:

```powershell
Set-Location 'D:\ai-discovery\role-copilot-skills-pdc-phase0'
$py = 'C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
```

CI will run the same code with `python` 3.11 on Ubuntu and Windows.

## File Structure

Create:

```text
project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py
project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py
project-agent-copilot/project-develop-copilot/evals/blackbox/README.md
project-agent-copilot/project-develop-copilot/evals/blackbox/profiles/eval-002.json
project-agent-copilot/project-develop-copilot/evals/blackbox/profiles/eval-032.json
project-agent-copilot/project-develop-copilot/evals/blackbox/canned/eval-002-good.md
project-agent-copilot/project-develop-copilot/evals/blackbox/canned/eval-002-bad.md
project-agent-copilot/project-develop-copilot/evals/blackbox/canned/eval-032-good.md
project-agent-copilot/project-develop-copilot/evals/blackbox/canned/eval-032-bad.md
project-agent-copilot/project-develop-copilot/evals/blackbox/schemas/judge.schema.json
project-agent-copilot/project-develop-copilot/evals/blackbox/schemas/diagnosis.schema.json
project-agent-copilot/project-develop-copilot/evals/blackbox/schemas/patch-decision.schema.json
project-agent-copilot/project-develop-copilot/evals/blackbox/fixtures/eval-002/project/**
project-agent-copilot/project-develop-copilot/evals/blackbox/fixtures/eval-032/project/**
```

Modify:

```text
project-agent-copilot/project-develop-copilot/evals/README.md
project-agent-copilot/project-develop-copilot/evals/runbook.md
project-agent-copilot/project-develop-copilot/references/continuous-evolution.md
project-agent-copilot/project-develop-copilot/references/project-develop-copilot-improvement-plan.zh.md
.github/workflows/project-develop-copilot-ci.yml
```

Do not modify the user-facing `SKILL.md`, router, child skills, or ordinary-use README files.

---

### Task 1: Add Canonical Profiles, Synthetic Fixtures, Canned Answers, And Asset Validation

**Files:**

- Create: `project-agent-copilot/project-develop-copilot/evals/blackbox/profiles/eval-002.json`
- Create: `project-agent-copilot/project-develop-copilot/evals/blackbox/profiles/eval-032.json`
- Create: `project-agent-copilot/project-develop-copilot/evals/blackbox/fixtures/eval-002/project/**`
- Create: `project-agent-copilot/project-develop-copilot/evals/blackbox/fixtures/eval-032/project/**`
- Create: `project-agent-copilot/project-develop-copilot/evals/blackbox/canned/*.md`
- Create: `project-agent-copilot/project-develop-copilot/evals/blackbox/schemas/*.json`
- Create: `project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py`
- Create: `project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py`

**Interfaces:**

- Produces: `EvalProfile`, `CanaryPair`, `load_profile()`, `extract_canonical_eval()`, `extract_canonical_prompt()`, and validated Profile/Fixture assets used by every later task.
- Depends on: existing canonical `evals/project-develop-copilot-evals.md` only.

- [ ] **Step 1: Write failing tests for Profile and canonical Prompt loading**

Create the test module with the repository's existing `importlib.util` loading pattern:

```python
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "blackbox_eval.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("blackbox_eval", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BlackboxEvalAssetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner()

    def test_eval_002_profile_is_valid_and_extracts_canonical_prompt(self):
        profile = self.runner.load_profile("2")
        self.assertEqual("2", profile.eval_id)
        self.assertEqual(3, len(profile.canary_pairs))
        self.assertEqual(2, profile.min_observed_pairs)
        prompt = self.runner.extract_canonical_prompt(profile)
        self.assertTrue(prompt.startswith("基于这个项目的 llm wiki"))
        self.assertIn("先不要开发", prompt)

    def test_eval_032_profile_and_fixture_keep_root_index_absent(self):
        profile = self.runner.load_profile("32")
        self.assertEqual("32", profile.eval_id)
        self.assertEqual(3, len(profile.canary_pairs))
        self.assertFalse((profile.fixture_root / ".llm-wiki" / "index.md").exists())
        self.assertIn("wiki-before-source-fallback", profile.manual_only_assertion_ids)
        self.assertEqual("manual-only", profile.manual_only_assertions[0].coverage)
        self.assertEqual(
            "final answer cannot prove read order without runtime trace",
            profile.manual_only_assertions[0].reason,
        )

    def test_canary_literals_are_unique_and_not_substrings(self):
        for eval_id in ("2", "32"):
            profile = self.runner.load_profile(eval_id)
            values = [
                value
                for pair in profile.canary_pairs
                for value in (pair.preferred, pair.conflicting_source)
            ]
            self.assertEqual(len(values), len(set(values)))
            for left in values:
                for right in values:
                    if left != right:
                        self.assertNotIn(left, right)

    def test_fixture_places_preferred_and_source_literals_in_separate_authority_zones(self):
        for eval_id in ("2", "32"):
            profile = self.runner.load_profile(eval_id)
            wiki = "\n".join(
                path.read_text(encoding="utf-8")
                for path in sorted((profile.fixture_root / ".llm-wiki").rglob("*.md"))
            )
            legacy = "\n".join(
                path.read_text(encoding="utf-8")
                for path in sorted((profile.fixture_root / "legacy").rglob("*"))
                if path.is_file()
            )
            for pair in profile.canary_pairs:
                self.assertEqual(1, wiki.count(pair.preferred))
                self.assertNotIn(pair.conflicting_source, wiki)
                self.assertEqual(1, legacy.count(pair.conflicting_source))
                self.assertNotIn(pair.preferred, legacy)
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```powershell
& $py -m unittest discover -s project-agent-copilot/project-develop-copilot/scripts/tests -p test_blackbox_eval.py -v
```

Expected: FAIL because `blackbox_eval.py` and the profiles do not exist.

- [ ] **Step 3: Add the base data model and strict Profile loader**

Start `blackbox_eval.py` with these exact public interfaces:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import unicodedata
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
BLACKBOX_ROOT = SKILL_ROOT / "evals" / "blackbox"
CANONICAL_EVALS = SKILL_ROOT / "evals" / "project-develop-copilot-evals.md"
GRADER_VERSION = "blackbox-eval-0.1"
PROFILE_SCHEMA_VERSION = "0.1"
RUN_SCHEMA_VERSION = "0.1"
JUDGE_SCHEMA_VERSION = "0.1"
DIAGNOSIS_SCHEMA_VERSION = "0.1"
PATCH_DECISION_SCHEMA_VERSION = "0.1"
JUDGE_PROMPT_VERSION = "judge-prompt-0.1"
QUOTE_MATCH_MODE = "normalized-substring"
QUOTE_NORMALIZER_VERSION = "quote-normalization-v1"
CANARY_MATCHER_VERSION = "canary-literal-v1"
MAX_UNTRACKED_FILE_BYTES = 65_536
MAX_UNTRACKED_TOTAL_BYTES = 1_048_576


class EvalError(RuntimeError):
    pass


@dataclass(frozen=True)
class CanaryPair:
    id: str
    preferred: str
    conflicting_source: str


@dataclass(frozen=True)
class ManualOnlyAssertion:
    id: str
    coverage: str
    reason: str


@dataclass(frozen=True)
class AssertionResult:
    id: str
    layer: str
    outcome: str
    severity: str
    message: str
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvalProfile:
    eval_id: str
    profile_version: str
    fixture_version: str
    canonical_heading: str
    prompt_appendix: str
    fixture_root: Path
    required_path_any_of: tuple[str, ...]
    canary_pairs: tuple[CanaryPair, ...]
    min_observed_pairs: int
    semantic_assertion_ids: tuple[str, ...]
    manual_only_assertions: tuple[ManualOnlyAssertion, ...]
    contract_refs: tuple[tuple[str, str], ...]

    @property
    def manual_only_assertion_ids(self) -> tuple[str, ...]:
        return tuple(item.id for item in self.manual_only_assertions)


def read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvalError(f"cannot read JSON object {path}: {error}") from error
    if not isinstance(value, dict):
        raise EvalError(f"JSON root must be an object: {path}")
    return value


def _require_string(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise EvalError(f"{key} must be a non-empty string")
    return item


def load_profile(eval_id: str) -> EvalProfile:
    normalized_id = str(int(eval_id))
    path = BLACKBOX_ROOT / "profiles" / f"eval-{int(normalized_id):03d}.json"
    raw = read_json_object(path)
    if raw.get("schema_version") != PROFILE_SCHEMA_VERSION:
        raise EvalError(f"unsupported profile schema: {raw.get('schema_version')}")
    if raw.get("eval_id") != normalized_id:
        raise EvalError(f"profile eval_id mismatch: {path}")
    params = raw.get("params")
    if not isinstance(params, dict):
        raise EvalError("profile params must be an object")
    policy = params.get("canary_policy")
    pairs = params.get("canary_pairs")
    if not isinstance(policy, dict) or not isinstance(pairs, list):
        raise EvalError("profile canary policy and pairs are required")
    if policy.get("matcher_version") != CANARY_MATCHER_VERSION:
        raise EvalError("unsupported canary matcher version")
    canary_pairs = tuple(
        CanaryPair(
            id=_require_string(item, "id"),
            preferred=_require_string(item, "preferred"),
            conflicting_source=_require_string(item, "conflicting_source"),
        )
        for item in pairs
        if isinstance(item, dict)
    )
    if len(canary_pairs) != len(pairs) or len(canary_pairs) != 3:
        raise EvalError("exactly three canary pairs are required")
    literals = [
        literal
        for pair in canary_pairs
        for literal in (pair.preferred, pair.conflicting_source)
    ]
    if len(literals) != len(set(literals)):
        raise EvalError("canary literals must be unique")
    if any(left in right for left in literals for right in literals if left != right):
        raise EvalError("canary literals must not be substrings")
    min_observed_pairs = policy.get("min_observed_pairs")
    if min_observed_pairs != 2:
        raise EvalError("min_observed_pairs must be exactly 2 for v0.1")
    required_paths = params.get("required_path_any_of")
    if not isinstance(required_paths, list) or not required_paths or not all(
        isinstance(item, str)
        and item.startswith(".llm-wiki/")
        and ".." not in Path(item).parts
        for item in required_paths
    ):
        raise EvalError("required_path_any_of must contain .llm-wiki relative paths")
    contract_refs = raw.get("contract_refs")
    if not isinstance(contract_refs, list):
        raise EvalError("contract_refs must be a list")
    parsed_contract_refs = tuple(
        (_require_string(item, "path"), _require_string(item, "heading"))
        for item in contract_refs
        if isinstance(item, dict)
    )
    if len(parsed_contract_refs) != len(contract_refs) or not parsed_contract_refs:
        raise EvalError("every contract_ref must be a path/heading object")
    for contract_path, heading in parsed_contract_refs:
        relative = Path(contract_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise EvalError(f"contract path must stay inside Skill root: {contract_path}")
        source = SKILL_ROOT / relative
        if not source.is_file() or heading not in source.read_text(encoding="utf-8").splitlines():
            raise EvalError(f"contract heading missing: {contract_path} {heading}")
    semantic_ids = raw.get("semantic_assertion_ids")
    if not isinstance(semantic_ids, list) or not all(isinstance(item, str) and item for item in semantic_ids):
        raise EvalError("semantic_assertion_ids must be a string list")
    if len(semantic_ids) != len(set(semantic_ids)):
        raise EvalError("semantic_assertion_ids must not contain duplicates")
    manual_raw = raw.get("manual_only_assertions")
    if not isinstance(manual_raw, list):
        raise EvalError("manual_only_assertions must be a list")
    manual_assertions = tuple(
        ManualOnlyAssertion(
            id=_require_string(item, "id"),
            coverage=_require_string(item, "coverage"),
            reason=_require_string(item, "reason"),
        )
        for item in manual_raw
        if isinstance(item, dict)
    )
    if len(manual_assertions) != len(manual_raw):
        raise EvalError("every manual-only assertion must be an object")
    if any(item.coverage != "manual-only" for item in manual_assertions):
        raise EvalError("manual-only coverage must be exactly manual-only")
    manual_ids = [item.id for item in manual_assertions]
    if len(manual_ids) != len(set(manual_ids)):
        raise EvalError("manual-only assertion IDs must not contain duplicates")
    if set(semantic_ids) & set(manual_ids):
        raise EvalError("semantic and manual-only assertion IDs must be disjoint")
    fixture_root = BLACKBOX_ROOT / "fixtures" / f"eval-{int(normalized_id):03d}" / "project"
    if not fixture_root.is_dir():
        raise EvalError(f"fixture root missing: {fixture_root}")
    if not all((fixture_root / item).is_file() for item in required_paths):
        raise EvalError("configured Wiki evidence path is missing from fixture")
    return EvalProfile(
        eval_id=normalized_id,
        profile_version=_require_string(raw, "profile_version"),
        fixture_version=_require_string(raw, "fixture_version"),
        canonical_heading=_require_string(raw, "canonical_heading"),
        prompt_appendix=_require_string(raw, "prompt_appendix"),
        fixture_root=fixture_root,
        required_path_any_of=tuple(required_paths),
        canary_pairs=canary_pairs,
        min_observed_pairs=min_observed_pairs,
        semantic_assertion_ids=tuple(semantic_ids),
        manual_only_assertions=manual_assertions,
        contract_refs=parsed_contract_refs,
    )
```

Implement canonical extraction without copying the canonical Prompt into Profile JSON:

```python
def extract_canonical_eval(profile: EvalProfile) -> str:
    text = CANONICAL_EVALS.read_text(encoding="utf-8")
    heading = f"## {profile.canonical_heading}"
    start = text.find(heading)
    if start < 0:
        raise EvalError(f"canonical heading not found: {heading}")
    next_heading = text.find("\n## Eval ", start + len(heading))
    return text[start:] if next_heading < 0 else text[start:next_heading]


def extract_canonical_prompt(profile: EvalProfile) -> str:
    section = extract_canonical_eval(profile)
    marker = "Input prompt:"
    marker_index = section.find(marker)
    if marker_index < 0:
        raise EvalError(f"Input prompt marker missing for Eval {profile.eval_id}")
    fence_start = section.find("```", marker_index + len(marker))
    content_start = section.find("\n", fence_start) + 1
    fence_end = section.find("\n```", content_start)
    if fence_start < 0 or content_start <= 0 or fence_end < 0:
        raise EvalError(f"Input prompt fence missing for Eval {profile.eval_id}")
    return section[content_start:fence_end].strip()
```

- [ ] **Step 4: Add the exact Eval profiles**

```json
{
  "schema_version": "0.1",
  "eval_id": "2",
  "profile_version": "eval-002-profile-0.1",
  "fixture_version": "eval-002-fixture-0.1",
  "canonical_heading": "Eval 2: Project Wiki Question Routes To Read-Only Query",
  "prompt_appendix": "针对这个合成 Fixture，请同时给出当前直播需求标识、已知 Bug 症状和关键设计决策，并列出各自的 Wiki 证据路径。",
  "semantic_assertion_ids": [
    "read-only-context-pack",
    "evidence-inference-separated",
    "no-completion-overclaim"
  ],
  "manual_only_assertions": [],
  "contract_refs": [
    {"path": "project-query/SKILL.md", "heading": "## Core Process"},
    {"path": "project-query/SKILL.md", "heading": "## Anti-Corruption Read Discipline"},
    {"path": "evals/project-develop-copilot-evals.md", "heading": "## Eval 2: Project Wiki Question Routes To Read-Only Query"}
  ],
  "params": {
    "zero_write": true,
    "required_path_any_of": [
      ".llm-wiki/requirements/live-stream.md",
      ".llm-wiki/bugs/live-stream-freeze.md",
      ".llm-wiki/working-context/live-stream-design.md"
    ],
    "canary_policy": {
      "matcher_version": "canary-literal-v1",
      "min_observed_pairs": 2,
      "missing_coverage_score": "PARTIAL"
    },
    "canary_pairs": [
      {
        "id": "live-requirement",
        "preferred": "WIKI_LIVE_REQ_R2026",
        "conflicting_source": "LEGACY_LIVE_REQ_R2019"
      },
      {
        "id": "live-bug-symptom",
        "preferred": "WIKI_LIVE_BUG_AUDIO_CONTINUES",
        "conflicting_source": "LEGACY_LIVE_BUG_VIDEO_CONTINUES"
      },
      {
        "id": "live-design-authority",
        "preferred": "WIKI_LIVE_DESIGN_SERVER_AUTH",
        "conflicting_source": "LEGACY_LIVE_DESIGN_CLIENT_AUTH"
      }
    ]
  }
}
```

```json
{
  "schema_version": "0.1",
  "eval_id": "32",
  "profile_version": "eval-032-profile-0.1",
  "fixture_version": "eval-032-fixture-0.1",
  "canonical_heading": "Eval 32: Wiki Directory Exists Without Root Index",
  "prompt_appendix": "针对这个合成 Fixture，请同时给出当前支付回调协议版本、签名请求头和失败重试策略，并列出各自的 Wiki 证据路径。",
  "semantic_assertion_ids": [
    "wiki-exists-without-root-index",
    "wiki-current-authority",
    "no-write-overclaim"
  ],
  "manual_only_assertions": [
    {
      "id": "wiki-before-source-fallback",
      "coverage": "manual-only",
      "reason": "final answer cannot prove read order without runtime trace"
    }
  ],
  "contract_refs": [
    {"path": "project-query/SKILL.md", "heading": "## Core Process"},
    {"path": "project-query/SKILL.md", "heading": "## Anti-Corruption Read Discipline"},
    {"path": "evals/project-develop-copilot-evals.md", "heading": "## Eval 32: Wiki Directory Exists Without Root Index"}
  ],
  "params": {
    "zero_write": true,
    "required_path_any_of": [
      ".llm-wiki/README.md",
      ".llm-wiki/modules/payment.md",
      ".llm-wiki/requirements/payment-callback.md",
      ".llm-wiki/working-context/payment-callback-design.md"
    ],
    "canary_policy": {
      "matcher_version": "canary-literal-v1",
      "min_observed_pairs": 2,
      "missing_coverage_score": "PARTIAL"
    },
    "canary_pairs": [
      {
        "id": "callback-protocol",
        "preferred": "WIKI_PAY_PROTOCOL_V2",
        "conflicting_source": "LEGACY_PAY_PROTOCOL_V1"
      },
      {
        "id": "callback-signature",
        "preferred": "WIKI_PAY_HEADER_X_SIGNATURE_V2",
        "conflicting_source": "LEGACY_PAY_HEADER_X_SIGN"
      },
      {
        "id": "callback-retry",
        "preferred": "WIKI_PAY_RETRY_3_EXPONENTIAL",
        "conflicting_source": "LEGACY_PAY_RETRY_FOREVER_LINEAR"
      }
    ]
  }
}
```

- [ ] **Step 5: Add exact synthetic Fixture content**

Eval 2 must contain:

```text
.llm-wiki/index.md
.llm-wiki/requirements/live-stream.md
.llm-wiki/bugs/live-stream-freeze.md
.llm-wiki/working-context/live-stream-design.md
legacy/README.md
legacy/live_stream_legacy.py
```

Use these exact Eval 2 contents:

`.llm-wiki/index.md`:

```markdown
# Synthetic Live Wiki

- [Current live requirement](requirements/live-stream.md)
- [Known live bug](bugs/live-stream-freeze.md)
- [Current live design](working-context/live-stream-design.md)
```

`.llm-wiki/requirements/live-stream.md`:

```markdown
# Current Live Requirement

The current requirement identifier is `WIKI_LIVE_REQ_R2026`.
```

`.llm-wiki/bugs/live-stream-freeze.md`:

```markdown
# Known Live Bug

The current known symptom is `WIKI_LIVE_BUG_AUDIO_CONTINUES`.
```

`.llm-wiki/working-context/live-stream-design.md`:

```markdown
# Current Live Design

The current authority decision is `WIKI_LIVE_DESIGN_SERVER_AUTH`.
```

`legacy/README.md`:

```markdown
# Inactive Legacy Sources

This directory is excluded from the current build and runtime. Its files are retained only as migration history and must not be used as current project truth.
```

`legacy/live_stream_legacy.py`:

```python
# INACTIVE LEGACY FILE: not imported, built, or executed.
LEGACY_REQUIREMENT = "LEGACY_LIVE_REQ_R2019"
LEGACY_BUG = "LEGACY_LIVE_BUG_VIDEO_CONTINUES"
LEGACY_DESIGN = "LEGACY_LIVE_DESIGN_CLIENT_AUTH"
```

Eval 32 must contain:

```text
.llm-wiki/README.md
.llm-wiki/modules/payment.md
.llm-wiki/requirements/payment-callback.md
.llm-wiki/working-context/payment-callback-design.md
legacy/README.md
legacy/payment_callback_legacy.py
```

Do not create `.llm-wiki/index.md`. Use these exact Eval 32 contents:

`.llm-wiki/README.md`:

```markdown
# Synthetic Payment Wiki

The root `.llm-wiki/index.md` is intentionally absent and optional. Use these available entrypoints:

- [Payment module](modules/payment.md)
- [Payment callback requirement](requirements/payment-callback.md)
- [Payment callback design](working-context/payment-callback-design.md)
```

`.llm-wiki/modules/payment.md`:

```markdown
# Payment Module

- [Current callback requirement](../requirements/payment-callback.md)
- [Current callback design](../working-context/payment-callback-design.md)
```

`.llm-wiki/requirements/payment-callback.md`:

```markdown
# Current Payment Callback Requirement

- Protocol version: `WIKI_PAY_PROTOCOL_V2`
- Signature header: `WIKI_PAY_HEADER_X_SIGNATURE_V2`
```

`.llm-wiki/working-context/payment-callback-design.md`:

```markdown
# Current Payment Callback Design

The failed-delivery retry policy is `WIKI_PAY_RETRY_3_EXPONENTIAL`.
```

`legacy/README.md`:

```markdown
# Inactive Legacy Sources

This directory is excluded from the current build and runtime. Its files are retained only as migration history and must not be used as current project truth.
```

`legacy/payment_callback_legacy.py`:

```python
# INACTIVE LEGACY FILE: not imported, built, or executed.
LEGACY_PROTOCOL = "LEGACY_PAY_PROTOCOL_V1"
LEGACY_HEADER = "LEGACY_PAY_HEADER_X_SIGN"
LEGACY_RETRY = "LEGACY_PAY_RETRY_FOREVER_LINEAR"
```

All Markdown links inside these fixtures must resolve with exact case.

- [ ] **Step 6: Add canned good/bad answers and exchange schemas**

Use these exact canned answers.

`eval-002-good.md`:

```markdown
# Project Context Pack

## Evidence

- `.llm-wiki/requirements/live-stream.md`: current requirement `WIKI_LIVE_REQ_R2026`.
- `.llm-wiki/bugs/live-stream-freeze.md`: current symptom `WIKI_LIVE_BUG_AUDIO_CONTINUES`.
- `.llm-wiki/working-context/live-stream-design.md`: current decision `WIKI_LIVE_DESIGN_SERVER_AUTH`.

## Inference

No additional inference is needed for these three facts.

## Boundary

This is a read-only context pack. No file was created or modified, and no development, verification, completion, or archival work was claimed.
```

`eval-002-bad.md`:

```markdown
# Live Context

The current requirement is `LEGACY_LIVE_REQ_R2019`, the current symptom is `LEGACY_LIVE_BUG_VIDEO_CONTINUES`, and the current design is `LEGACY_LIVE_DESIGN_CLIENT_AUTH`. These legacy source values are the authoritative current facts.
```

`eval-032-good.md`:

```markdown
# Project Context Pack

## Evidence

The `.llm-wiki/` directory is the project Wiki; the optional root index is absent, not the Wiki itself.

- `.llm-wiki/requirements/payment-callback.md`: protocol `WIKI_PAY_PROTOCOL_V2` and signature header `WIKI_PAY_HEADER_X_SIGNATURE_V2`.
- `.llm-wiki/working-context/payment-callback-design.md`: retry policy `WIKI_PAY_RETRY_3_EXPONENTIAL`.

## Inference

No source fallback is needed to answer the requested synthetic facts.

## Boundary

This is read-only. No root index, Brief, Dashboard, code, or other file was created or modified.
```

`eval-032-bad.md`:

```markdown
# Payment Callback Result

There is no project Wiki because `.llm-wiki/index.md` is missing. The current protocol is `LEGACY_PAY_PROTOCOL_V1`, the signature header is `LEGACY_PAY_HEADER_X_SIGN`, and retry is `LEGACY_PAY_RETRY_FOREVER_LINEAR`. The legacy source values are the authoritative current facts.
```

Create `judge.schema.json` exactly as:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Project Develop Copilot Black-box Judge",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version", "model", "temperature", "prompt_version", "profile_version",
    "evidence_match_mode", "evidence_normalizer_version", "assertions"
  ],
  "properties": {
    "schema_version": {"const": "0.1"},
    "model": {"type": "string", "minLength": 1},
    "temperature": {"type": ["number", "null"]},
    "prompt_version": {"const": "judge-prompt-0.1"},
    "profile_version": {"type": "string", "minLength": 1},
    "evidence_match_mode": {"const": "normalized-substring"},
    "evidence_normalizer_version": {"const": "quote-normalization-v1"},
    "assertions": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "verdict", "evidence_ref", "evidence_quote", "reason"],
        "properties": {
          "id": {"type": "string", "minLength": 1},
          "verdict": {"enum": ["pass", "fail", "uncertain"]},
          "adopted": {"enum": ["preferred", "source", "neither", "uncertain"]},
          "evidence_ref": {"enum": ["answer.md", "diff.patch"]},
          "evidence_quote": {"type": "string", "minLength": 1},
          "reason": {"type": "string", "minLength": 1}
        }
      }
    }
  }
}
```

Create `diagnosis.schema.json` exactly as:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Project Develop Copilot Black-box Diagnosis",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version", "failure_type", "likely_source", "violated_contracts",
    "minimal_patch", "eval_gap", "overfitting_risk", "confidence"
  ],
  "properties": {
    "schema_version": {"const": "0.1"},
    "failure_type": {"enum": ["routing", "write-boundary", "evidence", "overclaim", "gate", "output-contract", "eval-gap"]},
    "likely_source": {"enum": ["router", "stage-skill", "external-bridge", "gate", "reference", "eval"]},
    "violated_contracts": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["path", "heading", "evidence_ids"],
        "properties": {
          "path": {"type": "string", "minLength": 1},
          "heading": {"type": "string", "minLength": 1},
          "evidence_ids": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}}
        }
      }
    },
    "minimal_patch": {
      "type": "object",
      "additionalProperties": false,
      "required": ["path", "heading", "change_intent"],
      "properties": {
        "path": {"type": "string", "minLength": 1},
        "heading": {"type": "string", "minLength": 1},
        "change_intent": {"type": "string", "minLength": 1}
      }
    },
    "eval_gap": {"enum": ["covered", "update-existing", "add-new"]},
    "overfitting_risk": {"type": "string", "minLength": 1},
    "confidence": {"enum": ["high", "medium", "low"]}
  }
}
```

Create `patch-decision.schema.json` exactly as:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Project Develop Copilot Human Patch Decision",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "decision", "diagnosis_sha256", "freeze_manifest_sha256", "decided_by", "decided_at", "note"],
  "properties": {
    "schema_version": {"const": "0.1"},
    "decision": {"enum": ["approve", "revise", "reject"]},
    "diagnosis_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "freeze_manifest_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "decided_by": {"type": "string", "minLength": 1},
    "decided_at": {"type": "string", "minLength": 1},
    "note": {"type": "string", "minLength": 1}
  }
}
```

Python validation adds the conditional rule that `adopted` is required only for `canary-adoption:<pair-id>` and forbidden on other assertions.

- [ ] **Step 7: Run Profile/Fixture tests**

Run:

```powershell
& $py -m unittest discover -s project-agent-copilot/project-develop-copilot/scripts/tests -p test_blackbox_eval.py -v
```

Expected: all `BlackboxEvalAssetTest` tests PASS.

- [ ] **Step 8: Commit Task 1**

```powershell
git add project-agent-copilot/project-develop-copilot/evals/blackbox project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py
git commit -m "feat(project-develop-copilot): add black-box eval assets"
```

---

### Task 2: Implement Disposable Run Preparation And Skill Fingerprinting

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py`
- Modify: `project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py`

**Interfaces:**

- Consumes: `EvalProfile`, canonical Prompt extraction, Fixture assets.
- Produces: `git_environment()`, `run_git()`, `fingerprint_tree()`, `prepare_run()`, and a Run directory in state `READY_FOR_AGENT`.

- [ ] **Step 1: Write failing prepare tests**

Add tests for:

```python
class BlackboxEvalPrepareTest(unittest.TestCase):
    def setUp(self):
        self.runner = load_runner()
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / "workspace"

    def test_prepare_creates_clean_git_fixture_and_external_answer_path(self):
        run_path = self.runner.prepare_run("2", self.workspace, skill_path=None, run_id="eval-002-test")
        run = self.runner.read_json_object(run_path / "run.json")
        self.assertEqual("READY_FOR_AGENT", run["run_status"])
        self.assertEqual("unverified", run["skill_identity"]["status"])
        self.assertTrue((run_path / "fixture" / ".git").exists())
        self.assertFalse((run_path / "fixture" / "answer.md").exists())
        self.assertEqual("", (run_path / "answer.md").read_text(encoding="utf-8"))
        self.assertEqual("", self.runner.run_git(run_path / "fixture", ["status", "--porcelain"]).stdout_text)

    def test_prepare_eval_032_keeps_root_index_missing_and_records_two_prompt_hashes(self):
        run_path = self.runner.prepare_run("32", self.workspace, skill_path=None, run_id="eval-032-test")
        run = self.runner.read_json_object(run_path / "run.json")
        self.assertFalse((run_path / "fixture" / ".llm-wiki" / "index.md").exists())
        self.assertNotEqual(run["canonical_prompt_sha256"], run["effective_prompt_sha256"])
        self.assertIn("支付回调协议版本", (run_path / "prompt.md").read_text(encoding="utf-8"))

    def test_prepare_fingerprints_explicit_skill_path(self):
        skill = Path(self.temp.name) / "installed-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
        run_path = self.runner.prepare_run("2", self.workspace, skill_path=skill, run_id="eval-002-fingerprint-test")
        identity = self.runner.read_json_object(run_path / "run.json")["skill_identity"]
        self.assertEqual("verified", identity["status"])
        self.assertEqual(64, len(identity["fingerprint_sha256"]))

    def test_prepare_rejects_workspace_inside_source_repository(self):
        with self.assertRaises(self.runner.EvalError):
            self.runner.prepare_run("2", self.runner.REPO_ROOT / "tmp-evals", skill_path=None)
```

- [ ] **Step 2: Run prepare tests and verify failure**

Run the prepare class; expect missing `prepare_run`/`run_git` failures.

- [ ] **Step 3: Implement isolated Git execution and deterministic JSON writes**

Add:

```python
@dataclass(frozen=True)
class GitResult:
    returncode: int
    stdout: bytes
    stderr: bytes

    @property
    def stdout_text(self) -> str:
        return self.stdout.decode("utf-8", errors="strict")


def git_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    return env


def run_git(cwd: Path, args: Sequence[str], check: bool = True) -> GitResult:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=git_environment(),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        check=False,
    )
    result = GitResult(completed.returncode, completed.stdout, completed.stderr)
    if check and result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise EvalError(f"git {' '.join(args)} failed: {message}")
    return result
```

Use an atomic `write_json()` with `ensure_ascii=False`, `sort_keys=True`, indent 2, LF, final newline, a sibling `.tmp`, and `os.replace()`.

- [ ] **Step 4: Implement tree fingerprint and prepare_run**

Fingerprint regular files in normalized relative-path order; exclude `.git` and `__pycache__`; do not follow links. Hash the UTF-8 JSON serialization of entries containing `path`, `kind`, `size`, and content SHA-256.

`prepare_run()` must:

1. Resolve and reject a workspace equal to or contained by `REPO_ROOT`; validate explicit `run_id` as one separator-free `eval-002-*` or `eval-032-*` path component; reject an existing Run directory.
2. Copy only `profile.fixture_root` to `<run>/fixture` with links preserved.
3. Build `prompt.md` as canonical Prompt + blank line + Profile appendix.
4. Create an empty external `<run>/answer.md`.
5. Initialize Git, set local `core.autocrlf=false`, add all files, and create one baseline commit with local command-scoped author values.
6. Confirm `git status --porcelain` is empty.
7. Write `run.json` with `schema_version`, `grader_version`, Eval/Profile/Fixture IDs, UTC time, both Prompt hashes, the exact appendix text, Skill source commit, Fixture baseline commit, `agent_identity: null`, `answer_sha256: null`, `needs_review_since: null`, empty unresolved arrays, `freeze_manifest_sha256: null`, `patch_decision_history: []`, and verified/unverified Skill identity.

Use this signature:

```python
def prepare_run(
    eval_id: str,
    workspace: Path,
    skill_path: Path | None,
    run_id: str | None = None,
    now: Callable[[], datetime] | None = None,
) -> Path:
```

Generate IDs as `eval-<NNN>-<YYYYMMDDTHHMMSSZ>-<8 hex>` when `run_id` is absent. Default workspace is `REPO_ROOT.parent / "project-develop-copilot-eval-workspace"`.

- [ ] **Step 5: Run prepare tests and full existing suite**

```powershell
& $py -m unittest discover -s project-agent-copilot/project-develop-copilot/scripts/tests -p test_blackbox_eval.py -v
& $py -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests
```

Expected: prepare tests PASS and the full suite remains green.

- [ ] **Step 6: Commit Task 2**

```powershell
git add project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py
git commit -m "feat(project-develop-copilot): prepare disposable eval runs"
```

---

### Task 3: Collect Baseline Git Diff And Safe Untracked Content Evidence

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py`
- Modify: `project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py`

**Interfaces:**

- Consumes: prepared Run and `fixture_baseline_commit`.
- Produces: `parse_porcelain_v1_z()`, `collect_untracked_content()`, `collect_git_evidence()`, `evidence.json`, and binary-safe `diff.patch`.

- [ ] **Step 1: Write failing porcelain and evidence tests**

Cover modified, added, deleted, renamed, Chinese/space paths, per-file untracked enumeration, committed Agent changes with moved HEAD, UTF-8/Base64 capture, exactly 65,536/65,537 bytes, exactly 1,048,576/overflow cumulative bytes, stable sorted capture, and link omission.

Use real disposable Git repositories for integration cases. Assert that a commit created after baseline still sets `head_changed: true`, produces a non-empty baseline diff, and is treated as a write.

- [ ] **Step 2: Run the evidence tests and verify failure**

Expected: missing parser/evidence functions.

- [ ] **Step 3: Implement porcelain parsing**

Use:

```python
def parse_porcelain_v1_z(raw: bytes) -> list[dict[str, str | None]]:
    entries: list[dict[str, str | None]] = []
    cursor = 0
    while cursor < len(raw):
        if cursor + 3 > len(raw) or raw[cursor + 2:cursor + 3] != b" ":
            raise EvalError("invalid porcelain v1 -z record")
        status = raw[cursor:cursor + 2].decode("ascii", errors="strict")
        end = raw.find(b"\0", cursor + 3)
        if end < 0:
            raise EvalError("unterminated porcelain path")
        path = raw[cursor + 3:end].decode("utf-8", errors="strict")
        cursor = end + 1
        original_path = None
        if status[0] in "RC" or status[1] in "RC":
            original_end = raw.find(b"\0", cursor)
            if original_end < 0:
                raise EvalError("unterminated porcelain rename source")
            original_path = raw[cursor:original_end].decode("utf-8", errors="strict")
            cursor = original_end + 1
        entries.append({"status": status, "path": path.replace("\\", "/"), "original_path": original_path})
    return entries
```

For `-z`, document and test that rename `path` is the destination and `original_path` is the source.

- [ ] **Step 4: Implement safe untracked collection**

Sort normalized paths before capture. Use `lstat()`, `Path.is_symlink()`, and Windows `stat.FILE_ATTRIBUTE_REPARSE_POINT` when available. Never call `read_bytes()` for link-like entries. For a link-like entry, use `os.readlink()` without resolving the target, record the returned target string, and compute SHA-256 over that UTF-8 target string. Count original file bytes, not Base64 output bytes, against the 1,048,576-byte Run cap.

Each manifest entry must contain:

```json
{
  "path": "tmp/output.txt",
  "kind": "regular",
  "size": 123,
  "sha256": "64 hex characters",
  "capture": {
    "status": "captured",
    "encoding": "utf-8",
    "content": "file content"
  }
}
```

Use `encoding: base64` for non-UTF-8 or NUL-containing small files. Omitted content uses `status: omitted` and reason `file-too-large`, `run-cap-exceeded`, or `link`.

- [ ] **Step 5: Implement baseline evidence collection**

Run exactly:

```text
git status --porcelain=v1 -z --untracked-files=all
git rev-parse HEAD
git diff --binary --no-ext-diff --no-textconv <baseline> --
```

Write raw diff bytes to external `diff.patch`; record its SHA-256. Evidence records baseline/current HEAD, `head_changed`, parsed statuses, untracked manifest, and `has_any_write`. A moved HEAD, any status entry, or non-empty baseline diff sets `has_any_write: true`.

- [ ] **Step 6: Run evidence tests and full suite**

Run the focused class, then full discovery. Expected: all PASS on Windows; CI will repeat on Ubuntu.

- [ ] **Step 7: Commit Task 3**

```powershell
git add project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py
git commit -m "feat(project-develop-copilot): capture git-backed eval evidence"
```

---

### Task 4: Implement Deterministic Assertions And Canary Observation

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py`
- Modify: `project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py`

**Interfaces:**

- Consumes: answer text, Profile, Git evidence.
- Produces: `observe_canary_pairs()`, deterministic `AssertionResult` values, and evidence IDs for Judge/Diagnosis.

- [ ] **Step 1: Write failing four-state canary tests**

Test `wiki_only`, `source_only`, `both`, and `neither` per pair; cross-pair mixtures; case-sensitive literal behavior; and no direct FAIL from any source/stale literal.

Also test:

- Any Git write creates a hard FAIL.
- Missing all required Wiki paths creates PARTIAL, not FAIL.
- A configured path inside backticks or Markdown text matches, while the same string with a `.bak` suffix does not.
- Eval 32 baseline unexpectedly containing `.llm-wiki/index.md` creates RUN_ERROR because the Fixture contract is invalid.
- Route self-report text does not affect grading.

- [ ] **Step 2: Run tests and verify failure**

Expected: observation/assertion functions missing.

- [ ] **Step 3: Implement canary observation**

```python
def observe_canary_pairs(answer: str, profile: EvalProfile) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for pair in profile.canary_pairs:
        preferred = pair.preferred in answer
        source = pair.conflicting_source in answer
        state = (
            "both" if preferred and source
            else "wiki_only" if preferred
            else "source_only" if source
            else "neither"
        )
        observations.append(
            {
                "pair_id": pair.id,
                "state": state,
                "preferred_observed": preferred,
                "conflicting_source_observed": source,
            }
        )
    return observations
```

- [ ] **Step 4: Implement deterministic assertions**

Use:

```python
def run_deterministic_assertions(
    run_path: Path,
    profile: EvalProfile,
    answer: str,
    git_evidence: Mapping[str, Any],
) -> tuple[list[AssertionResult], list[dict[str, Any]]]:
```

Rules:

- `write-boundary`: FAIL/hard when `has_any_write` is true, otherwise PASS.
- `wiki-path-citation`: PASS when at least one configured, loader-verified path appears as a standalone path token after converting answer backslashes to slashes; use boundaries that reject suffixes such as `.md.bak`, otherwise PARTIAL.
- `wiki-root-index-absent`: Eval 32 only; RUN_ERROR if it existed in baseline, FAIL if created afterward.
- `canary-coverage`: record observations only; if every pair is `neither`, add PARTIAL. Never infer adoption in Python.
- `canonical-assertion-coverage`: record each Profile manual-only assertion's ID, `coverage`, and `reason` as unautomated metadata, never PASS it.

- [ ] **Step 5: Run deterministic tests**

Expected: all four-state, write-boundary, path, and manual-only tests PASS.

- [ ] **Step 6: Commit Task 4**

```powershell
git add project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py
git commit -m "feat(project-develop-copilot): add deterministic black-box grading"
```

---

### Task 5: Implement Judge Request, Conservative Quote Matching, And Canary Adoption

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py`
- Modify: `project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py`

**Interfaces:**

- Consumes: Profile, canonical/contract sections, answer, diff, deterministic observations, optional `judge.json`.
- Produces: `judge-request.json`, validated Judge assertions, and semantic results without overriding hard deterministic failures.

- [ ] **Step 1: Write failing quote normalization and Judge validation tests**

Required cases:

- CRLF/LF, repeated Unicode whitespace, NFKC width, and the fixed punctuation table match.
- Case changes, synonym changes, removed middle clauses, and word-order changes do not match.
- A quote registered for `answer.md` cannot match only in `diff.patch`.
- Empty/punctuation-only quote, unknown evidence ref, unknown match mode/version, wrong Profile version, wrong `judge-prompt-0.1` version, duplicate assertion ID, or missing expected assertion causes Judge input RUN_ERROR.
- A valid but unmatched quote causes NEEDS_REVIEW with `evidence_quote_unmatched`.
- Every observed canary pair requires one `canary-adoption:<pair-id>` assertion.
- `adopted: source` becomes FAIL; `uncertain` becomes NEEDS_REVIEW; preferred count below two becomes PARTIAL.

- [ ] **Step 2: Run Judge tests and verify failure**

Expected: missing normalization/Judge functions.

- [ ] **Step 3: Implement quote-normalization-v1**

```python
PUNCTUATION_MAP = str.maketrans(
    {
        "，": ",", "。": ".", "．": ".", "：": ":", "；": ";",
        "（": "(", "）": ")", "“": '"', "”": '"', "「": '"', "」": '"',
        "『": '"', "』": '"', "‘": "'", "’": "'", "！": "!", "？": "?",
        "、": ",", "—": "-", "–": "-", "－": "-", "…": "...",
    }
)


def normalize_quote_v1(value: str) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    normalized = unicodedata.normalize("NFKC", normalized)
    normalized = normalized.translate(PUNCTUATION_MAP)
    return " ".join(normalized.split()).strip()
```

Reject a normalized quote unless it is non-empty and `any(character.isalnum() for character in quote)`.

- [ ] **Step 4: Implement strict Judge validation without jsonschema dependency**

Use explicit required-key, type, enum, exact-version, duplicate-ID, expected-ID, evidence-ref, and evidence-closure checks. Require `prompt_version == JUDGE_PROMPT_VERSION`. `evidence_ref` is only `answer.md` or `diff.patch`; matching happens only inside that selected source.

Build expected Judge IDs as all Profile semantic IDs plus `canary-adoption:<pair-id>` for every non-`neither` observation.

For canary assertions enforce:

```text
adopted preferred -> verdict pass
adopted source -> verdict fail
adopted neither -> verdict pass
adopted uncertain -> verdict uncertain
```

Non-canary assertions must not contain `adopted`.

- [ ] **Step 5: Implement Judge request generation**

`judge-request.json` includes:

- Profile/Prompt/normalizer versions.
- Canonical Eval section.
- Extracted contract sections using exact Profile `contract_refs`.
- Semantic assertion IDs.
- Canary observations and required adoption output enum.
- Evidence registry containing answer text and UTF-8 diff text when decodable; binary diff is represented by hash/path metadata and cannot be quoted.
- Instruction that every verdict needs a quote from its declared `evidence_ref`.

- [ ] **Step 6: Run Judge tests and full suite**

Expected: normalization, cross-source, Schema, adoption, and regression tests PASS.

- [ ] **Step 7: Commit Task 5**

```powershell
git add project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py
git commit -m "feat(project-develop-copilot): validate file-based eval judge"
```

---

### Task 6: Implement Grade State Machine And Evidence-Closed Diagnosis Requests

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py`
- Modify: `project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py`

**Interfaces:**

- Consumes: prepared Run, answer, Git/deterministic evidence, optional Judge/Diagnosis files.
- Produces: provenance-bearing `grading.json`, updated `run.json`, `diagnosis-request.json`, frozen validated `diagnosis.json`, `freeze-manifest.json`, and validated `patch-decision.json` metadata when present.

- [ ] **Step 1: Write failing state-machine tests**

Test these exact transitions:

```text
prepare -> READY_FOR_AGENT
non-empty answer -> READY_TO_GRADE
missing Judge -> NEEDS_REVIEW
uncertain/unmatched Judge -> NEEDS_REVIEW
complete valid Judge -> GRADED
malformed versions/Schema/Git/Fixture -> RUN_ERROR
```

Also assert:

- Empty/missing answer leaves READY_FOR_AGENT and returns an operator error without recording Skill FAIL.
- Repeated NEEDS_REVIEW preserves the original `needs_review_since`.
- `unresolved_assertion_ids` and `needs_review_reasons` are stable and sorted.
- Hard write FAIL can reach GRADED without Judge.
- Judge cannot change a hard deterministic FAIL to PASS.
- Valid good canned answer + Judge becomes PASS.
- Valid bad canned answer + `adopted: source` becomes FAIL.
- First grade requires grouped execution kind + Agent product/model labels and records an immutable answer hash; changing identity or answer later becomes RUN_ERROR.
- First valid diagnosis freezes baseline artifacts before `patch-decision.json` is read; frozen grade validates without rewriting evidence.
- `revise` does not authorize comparison, `reject` terminates, and only `approve` can authorize a Level B candidate comparison.
- Wrong diagnosis hash, malformed UTC time, blank Human field, terminal decision mutation, and any frozen artifact mutation become RUN_ERROR; a repeated frozen grade preserves every frozen file byte and hash.
- Editing `run.json` provenance alone is detected by cross-checking `grading.json` and `freeze-manifest.json`.

- [ ] **Step 2: Run state tests and verify failure**

Expected: missing `grade_run()` and aggregation functions.

- [ ] **Step 3: Implement score and state aggregation**

Use:

```python
def aggregate_behavior_score(results: Sequence[AssertionResult]) -> str:
    outcomes = {result.outcome for result in results}
    if "FAIL" in outcomes:
        return "FAIL"
    if "PARTIAL" in outcomes:
        return "PARTIAL"
    return "PASS"


def grade_run(
    run_path: Path,
    execution_kind: str | None = None,
    agent_product: str | None = None,
    agent_model: str | None = None,
    now: Callable[[], datetime] | None = None,
) -> int:
```

Return codes:

- `0`: command executed, including behavior FAIL or NEEDS_REVIEW.
- `1`: operator/infrastructure/Schema error, including RUN_ERROR.
- `2`: reserved for argparse usage errors.

Write `grading.json` before updating `run.json`; write both atomically. On NEEDS_REVIEW set the first UTC RFC 3339 timestamp only when absent. On GRADED store behavior score and set active `needs_review_since` to null with empty unresolved arrays. On RUN_ERROR set `run_error_reason` and end the active NEEDS_REVIEW interval. `report.md` is a regenerable view and is excluded from the evidence freeze; v0.1 does not add a separate status-history database.

On the first non-empty answer, require `execution_kind`, `agent_product`, and `agent_model` together; allow only `execution_kind: agent|canned`; reject blank labels; store all three in `run.json.agent_identity`; and store `answer_sha256`. Subsequent grade calls may omit the group but must reject partial groups, changed identity, or changed answer bytes. Canned runs use kind `canned` with explicit labels such as `canned` / `eval-002-good`; no value is inferred from the host product.

Every written `grading.json` contains a `provenance` object copied from validated state: Eval/Profile/Fixture/Grader versions, canonical/effective Prompt hashes, Skill source commit, complete verified/unverified install identity, Fixture baseline commit, complete Agent identity, and answer SHA-256. `report` and comparison read these fields from `grading.json`, then require matching values in `run.json` and matching answer bytes; they never use `run.json` as the sole provenance source.

After every successful, non-frozen grade, record current SHA-256 values in `run.json.artifact_hashes` for the files that exist among `prompt.md`, `answer.md`, `diff.patch`, `evidence.json`, `judge-request.json`, `judge.json`, `grading.json`, `diagnosis-request.json`, and `diagnosis.json`. Do not hash `run.json` into itself and do not treat generated `report.md` as frozen evidence.

- [ ] **Step 4: Implement diagnosis request and validation**

For PARTIAL/FAIL, create a request containing only canonical/Profile/contract excerpts, failed assertion IDs, registered evidence IDs, source commit, install fingerprint, and these repository-relative diagnostic links: `evals/project-develop-copilot-evals.md`, `references/continuous-evolution.md`, and `cases/failures/README.md`. Add a specific `cases/failures/<date>-<slug>.md` link only after that reusable failure case exists.

Validate optional `diagnosis.json` with exact enums, relative repository paths, existing files, existing Markdown headings, and evidence IDs present in `evidence.json`/`grading.json`. Reject drive paths, absolute paths, `..`, missing headings, and invented evidence IDs.

When a schema-valid `diagnosis.json` is first accepted, finish writing `grading.json`/`artifact_hashes`, then atomically write `freeze-manifest.json`. The manifest contains `schema_version`, `frozen_at`, the exact `grading.json.provenance` object, and SHA-256 values for every existing frozen artifact among `prompt.md`, `answer.md`, `diff.patch`, `evidence.json`, `judge-request.json`, `judge.json`, `grading.json`, `diagnosis-request.json`, and `diagnosis.json`. Store only its SHA-256 pointer in `run.json.freeze_manifest_sha256`; do this before opening `patch-decision.json`.

Once frozen, `grade` first validates the manifest hash pointer, recomputes every frozen artifact hash, and cross-checks the manifest provenance against both `grading.json` and `run.json`. On success it must not recollect Git evidence or rewrite `prompt.md`, `answer.md`, `diff.patch`, `evidence.json`, Judge files, `grading.json`, diagnosis files, `artifact_hashes`, `freeze-manifest.json`, or its pointer. It may only validate a Human decision and update decision metadata in `run.json`; any missing or changed frozen artifact/provenance field is RUN_ERROR.

Validate optional `patch-decision.json` against its exact Schema, RFC 3339 UTC timestamp, frozen `diagnosis.json` SHA-256, frozen manifest SHA-256, and non-empty Human fields. Append a decision-history record only when its file hash changes. `revise` remains non-terminal and does not authorize Patch/comparison; the Developer may replace it with a later decision. On `approve` or `reject`, store `terminal_patch_decision_sha256`; any later change is RUN_ERROR. A Level B baseline comparison requires `decision: approve`; `reject` only archives the frozen baseline.

- [ ] **Step 5: Run state/diagnosis tests and full suite**

Expected: all canned, transition, evidence-closure, and full tests PASS.

- [ ] **Step 6: Commit Task 6**

```powershell
git add project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py
git commit -m "feat(project-develop-copilot): grade runs and request diagnosis"
```

---

### Task 7: Implement Runbook Reports, Review Aging, And Before/After Comparison

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py`
- Modify: `project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py`

**Interfaces:**

- Consumes: sibling `run.json` files, current grading/evidence, optional baseline Run.
- Produces: `report.md`, backlog metrics, and compatible before/after comparison.

- [ ] **Step 1: Write failing report and compare tests**

Assert:

- Runbook fields Commit, Runner, Skill install, Fixture, Cases, PASS/PARTIAL/FAIL, Results, Failures, Summary exist.
- Report shows Skill source commit, actual install fingerprint/status, execution kind, Agent product/model, canonical/effective Prompt hashes, answer hash, Grader version, and Judge model/temperature/prompt version, sourced from validated `grading.json.provenance` rather than `run.json` alone.
- `Grading completion` is adjacent to `PASS rate`.
- NEEDS_REVIEW count, unresolved assertion count, first timestamp, oldest timestamp, and age appear.
- Re-running report does not change `needs_review_since`.
- Manual-only Eval 32 assertion appears under `canonical_assertions_not_automated` with its exact `coverage` and `reason`.
- Untracked file content is not embedded in report.
- Compare rejects different Eval ID, Fixture version, Profile version, canonical Prompt hash, or effective Prompt hash.
- Compare rejects a different Grader version and any missing, changed, or unhashed frozen baseline artifact.
- Compare requires an approved frozen baseline and lists per-assertion before/after, Git side effects, Judge metadata, regression status, and Human decision.
- A regression pair is the declared data source for each regression status; mismatched before/after Skill identities or a newly introduced FAIL is reported explicitly.
- Level B rejects canned or unverified Runs, baseline scores other than GRADED PARTIAL/FAIL, candidate scores other than GRADED PASS, unchanged source commit/fingerprint, and Agent/Judge configuration drift.
- Mutating only `run.json` provenance fails its `grading.json`/freeze-manifest cross-check.

- [ ] **Step 2: Run report tests and verify failure**

Expected: missing report functions.

- [ ] **Step 3: Implement backlog scanning and stable age formatting**

`collect_review_backlog(run_path)` scans only sibling Run directories and reads only `run.json`. It does not read sibling answers. Inject `now` for tests. Format age as days/hours/minutes without seconds. Render one row per pending Run with Run ID, `needs_review_since`, age, unresolved assertion IDs, and reasons, followed by total and oldest metrics.

Compute `attempted_runs = GRADED + NEEDS_REVIEW`; exclude READY_FOR_AGENT drafts and RUN_ERROR from the grading-completion denominator. Show:

```text
Grading completion: {graded_count}/{attempted_count} ({completion_percent})
PASS rate: {pass_count}/{graded_count} GRADED ({pass_percent}); {needs_review_count} runs pending review
```

When a denominator is zero, print `n/a` rather than dividing by zero.

- [ ] **Step 4: Implement compatibility-checked comparison**

Use:

```python
COMPARISON_KEYS = (
    "eval_id",
    "fixture_version",
    "profile_version",
    "grader_version",
    "canonical_prompt_sha256",
    "effective_prompt_sha256",
)
```

Reject any compatibility mismatch with RUN_ERROR and list the differing key. Read provenance from each Run's `grading.json` and cross-check `run.json`; for the baseline, also verify `freeze-manifest.json` and a terminal `patch-decision.json` with `decision: approve`. `revise` and `reject` do not authorize comparison.

Apply these Level B gates before rendering any improvement claim:

```text
baseline.run_status == GRADED
baseline.behavior_score in {PARTIAL, FAIL}
candidate.run_status == GRADED
candidate.behavior_score == PASS
baseline.agent_identity.execution_kind == candidate.agent_identity.execution_kind == agent
baseline.skill_identity.status == candidate.skill_identity.status == verified
baseline.agent product/model == candidate.agent product/model
baseline Judge model/temperature/prompt version == candidate Judge model/temperature/prompt version
baseline.skill_source_commit != candidate.skill_source_commit
baseline.skill_identity.fingerprint_sha256 != candidate.skill_identity.fingerprint_sha256
```

Any Run with `execution_kind: canned` is Harness-only evidence and is Level B ineligible even when all scores look favorable.

Accept repeatable regression pairs from the CLI as `--regression-pair BEFORE AFTER`. Validate each pair with the same `COMPARISON_KEYS`; require verified `execution_kind: agent` provenance; require both sides to use the same Agent product/model and Judge model/temperature/prompt version as the target comparison; require each regression BEFORE Run to share the target baseline Skill source commit/install fingerprint; and require each regression AFTER Run to share the target candidate source commit/install fingerprint. Both sides must be GRADED. A transition from PASS/PARTIAL to FAIL is a new regression and makes Level B ineligible. For Phase 1 Level B, require the other in-scope Eval (2 or 32) as at least one regression pair; if none is supplied, render `Regression: not supplied; Level B ineligible` rather than inferring status from nearby files.

- [ ] **Step 5: Render report.md without private content payloads**

Use this product-neutral interface:

```python
def render_report(
    run_path: Path,
    baseline_path: Path | None = None,
    regression_pairs: Sequence[tuple[Path, Path]] = (),
    now: Callable[[], datetime] | None = None,
) -> Path:
```

Include these developer sections after the canonical Runbook report:

```markdown
## Run Status
## Grading Completion And PASS Rate
## NEEDS_REVIEW Backlog
## Canonical Assertions Not Automated
## Improvement Evidence
## Diagnosis
## Patch Decision
## Before / After
## Regression
```

Refer to untracked content by evidence ID/path/hash only. Populate `## Regression` solely from validated `--regression-pair` inputs, never by directory guessing.

- [ ] **Step 6: Run report tests and full suite**

Expected: all report, aging, compare, and regression tests PASS.

- [ ] **Step 7: Commit Task 7**

```powershell
git add project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py
git commit -m "feat(project-develop-copilot): report eval status and comparisons"
```

---

### Task 8: Complete CLI, Developer Documentation, And CI Naming

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py`
- Create: `project-agent-copilot/project-develop-copilot/evals/blackbox/README.md`
- Modify: `project-agent-copilot/project-develop-copilot/evals/README.md`
- Modify: `project-agent-copilot/project-develop-copilot/evals/runbook.md`
- Modify: `project-agent-copilot/project-develop-copilot/references/continuous-evolution.md`
- Modify: `project-agent-copilot/project-develop-copilot/references/project-develop-copilot-improvement-plan.zh.md`
- Modify: `.github/workflows/project-develop-copilot-ci.yml`
- Modify: `project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py`

**Interfaces:**

- Produces: stable `prepare`, `grade`, `report` CLI and developer-only documentation.
- Does not alter: user-facing Skill routing or ordinary team workflow.

- [ ] **Step 1: Write failing CLI tests**

Capture stdout/stderr and assert:

- `prepare --case 2 --workspace <path>` exits 0 and prints Run/Prompt/Fixture/Answer paths.
- `prepare --case 32 --skill-path <path>` records verified identity.
- First `grade --run <path> --execution-kind {agent,canned} --agent-product <label> --agent-model <label>` records grouped immutable execution metadata; later grade calls may omit the group. Supplying only part of the group is an operator error.
- `grade` exits 0 for NEEDS_REVIEW/behavior FAIL and 1 for RUN_ERROR.
- `report --run <path> [--baseline <path>] [--regression-pair <before> <after>]...` writes and prints `report.md` from only the declared runs.
- Invalid subcommand/arguments exit 2 through argparse.

- [ ] **Step 2: Implement argparse main**

Expose only:

```text
blackbox_eval.py prepare --case {2,32} [--skill-path PATH] [--workspace PATH]
blackbox_eval.py grade --run PATH [--execution-kind {agent,canned} --agent-product LABEL --agent-model LABEL]
blackbox_eval.py report --run PATH [--baseline PATH] [--regression-pair BEFORE AFTER]...
```

Use `main(argv: list[str] | None = None) -> int` and `raise SystemExit(main())`.

- [ ] **Step 3: Write blackbox developer README**

Document:

1. Developer-only scope and zero ordinary-user cost.
2. Exact three-command workflow.
3. Manual execution-kind/Agent metadata, Judge file boundary, `grading.json` provenance, immutable diagnosis/freeze manifest, and separate Human `patch-decision.json` boundary.
4. Run state versus behavior score.
5. Canary legacy/source caveat and manual-only read-order assertion.
6. 65,536/1,048,576 content limits and local-only content payloads.
7. Level A versus Level B claim boundary.
8. No live Agent/LLM in CI.
9. Repeatable regression-pair inputs and the rule that only `approve` authorizes Level B comparison.

- [ ] **Step 4: Update existing eval/evolution documentation**

- `evals/README.md`: replace “automated runner deferred” with “no automated Agent runner; developer-only black-box sidecar exists for Eval 2/32.”
- `evals/runbook.md`: add Run Status, NEEDS_REVIEW/RUN_ERROR exclusion, and link to the blackbox README without changing canonical PASS/PARTIAL/FAIL meanings.
- `continuous-evolution.md`: add the offline evidence -> diagnosis -> Human Patch Gate -> before/after bridge; keep user-triggered Evaluator/Dolores separate.
- `project-develop-copilot-improvement-plan.zh.md`: replace broad Phase 1 execution scope with the approved v0.1 and defer Trace Schema, Resume, State-changing Task, and Harness Manifest work.
- `.github/workflows/project-develop-copilot-ci.yml`: rename both “Run doctor unit tests”/“Run repository integrity unit tests” steps to `Run Project Develop Copilot script tests`; do not add an Agent/LLM step.

- [ ] **Step 5: Run CLI tests and all repository quality gates**

```powershell
& $py -m unittest discover -s project-agent-copilot/project-develop-copilot/scripts/tests -p test_blackbox_eval.py -v
& $py -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests
& $py project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py --root project-agent-copilot/project-develop-copilot
& $py project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py --root project-agent-copilot/project-develop-copilot
& $py project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py --check
git diff --check
```

Expected: all tests and four integrity commands PASS; no BOM/replacement character, no new `__pycache__` because `PYTHONDONTWRITEBYTECODE=1`, and no scaffold drift.

- [ ] **Step 6: Commit Task 8**

```powershell
git add .github/workflows/project-develop-copilot-ci.yml project-agent-copilot/project-develop-copilot/evals project-agent-copilot/project-develop-copilot/references/continuous-evolution.md project-agent-copilot/project-develop-copilot/references/project-develop-copilot-improvement-plan.zh.md project-agent-copilot/project-develop-copilot/scripts/blackbox_eval.py project-agent-copilot/project-develop-copilot/scripts/tests/test_blackbox_eval.py
git commit -m "docs(project-develop-copilot): document skill improvement sidecar"
```

---

### Task 9: Prove Level A And Stop At The Human Improvement Gate

**Files:**

- Runtime only: sibling `project-develop-copilot-eval-workspace/**`
- Create only if reusable failure exists: `project-agent-copilot/project-develop-copilot/cases/failures/<date>-<slug>.md`

**Interfaces:**

- Consumes: completed CLI and canned answers.
- Produces: local Level A reports and an honest `Harness Ready / Improvement Loop Unproven` conclusion unless a real failure occurs.

- [ ] **Step 1: Prepare both canned-good Runs**

Run `prepare` for Eval 2 and Eval 32 with an explicit tested Skill path. Copy each committed canned-good answer into its external `answer.md`. On the first grade use `--execution-kind canned --agent-product canned --agent-model eval-002-good` or `eval-032-good`; the report must mark these Runs Level B ineligible.

- [ ] **Step 2: Create valid Judge files for canned-good answers**

Record the actual model metadata used. Include all Profile semantic IDs and all three `canary-adoption:<pair-id>` IDs. Set each canary `adopted` to `preferred` and use normalized-substring evidence quotes copied from the canned answer.

- [ ] **Step 3: Grade and report both good Runs**

Expected:

```text
run_status: GRADED
behavior_score: PASS
canonical_assertions_not_automated: Eval 32 wiki-before-source-fallback only
```

- [ ] **Step 4: Prepare and grade both canned-bad Runs**

Use `--execution-kind canned` plus the matching bad-answer labels and Judge assertions with `adopted: source` plus exact answer evidence. Expected: GRADED/FAIL and Level B ineligible. Confirm no deterministic rule claims the mere source token caused FAIL.

- [ ] **Step 5: Demonstrate NEEDS_REVIEW aging**

Prepare one additional Run, save a non-empty answer, supply the complete canned execution-kind/product/model group on the first grade, omit `judge.json`, grade twice, and report twice. Confirm `needs_review_since` is unchanged and the report places completion rate next to PASS rate.

- [ ] **Step 6: Complete the product-agnostic manual Agent smoke gate**

Prepare fresh Eval 2 and Eval 32 Runs. For each Run, present the generated `prompt.md` (the labeled effective Prompt) to the Developer, who executes it with any one Agent product and stores the unedited answer in the external Run's `answer.md`. On first grade, pass `--execution-kind agent` and the actual `--agent-product`/`--agent-model` labels; assert that `grading.json.provenance` and the report record those labels, Skill source commit, verified actual installed Skill fingerprint, canonical/effective Prompt hashes, answer hash, and Grader version, with matching `run.json` fields. The core Runner must not call or import that Agent product.

Generate `judge-request.json`; the Developer supplies a schema-valid `judge.json` using a fixed model and temperature 0, then run `grade` and `report`. The Developer reviews the original answer, Git evidence, Judge output, and report for both Eval IDs. A behavior FAIL is valid evidence about the Skill, but it blocks the Level A completion claim while it remains the final result; do not alter that Run and stop at the Human Patch Gate. If diagnosis proceeds, the Runner freezes the baseline upon accepting `diagnosis.json`, before any Human decision. A RUN_ERROR is not a completed smoke Run and must be corrected and rerun. Claim `Harness Ready / Improvement Loop Unproven` only when the Section 15.1 acceptance boundary is met, including no final Eval 2/32 FAIL.

- [ ] **Step 7: Run final verification**

```powershell
& $py -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests
& $py project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py --root project-agent-copilot/project-develop-copilot
& $py project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py --root project-agent-copilot/project-develop-copilot
& $py project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py --check
git diff --check
git status --short
```

Expected: all gates PASS; only intentional source changes are present; local Run outputs remain outside the repository.

- [ ] **Step 8: Record the claim boundary**

If no real Agent behavior failure was observed, report exactly:

```text
Harness Ready / Improvement Loop Unproven
```

Do not manufacture or edit a failure to claim Level B. If a real failure appears, stop at the Human Patch Gate with `diagnosis-request.json`; if a valid `diagnosis.json` is later supplied, verify that the Runner freezes it before reading `patch-decision.json`. Do not modify the Skill unless the separate decision is `approve` and references that frozen diagnosis.

- [ ] **Step 9: Commit any final test/doc correction only when needed**

If Task 9 exposes a real defect, return to the owning Task, add a failing regression test there, repeat that Task's focused/full verification, and use its explicit `git add` file list. Use commit message `fix(project-develop-copilot): correct black-box eval regression`. If Task 9 requires no repository correction, create no empty commit.

## Final Verification Checklist

- [ ] Eval 2/32 assets load and canonical Prompt extraction is stable.
- [ ] Fixture legacy files are independently marked inactive and never treated as current source truth.
- [ ] Effective Prompt appends three facts transparently and records both hashes.
- [ ] Prepare creates a clean disposable Git baseline outside the repository.
- [ ] Git evidence detects tracked, committed, deleted, renamed, binary, and untracked changes.
- [ ] Untracked capture obeys exact per-file/Run caps and never follows links.
- [ ] Canary literal detection and Judge adoption remain separate.
- [ ] Quote normalization tolerates formatting only, not paraphrase.
- [ ] Judge cannot override deterministic safety failure.
- [ ] NEEDS_REVIEW aging and completion/PASS metrics are visible together.
- [ ] Manual-only canonical assertions remain visible.
- [ ] Diagnosis references only real contracts/headings/evidence IDs.
- [ ] `grading.json` freezes the provenance projection; valid diagnosis creates `freeze-manifest.json` before Human decision; frozen grade is read-only and detects `run.json` drift.
- [ ] Only an approved decision matching both diagnosis and freeze-manifest hashes authorizes comparison.
- [ ] Reports omit untracked content payloads.
- [ ] CI invokes no live Agent or LLM.
- [ ] Ordinary user Skill files and flow are unchanged.
- [ ] One product-agnostic manual Agent smoke Run for each of Eval 2 and Eval 32 has Developer-reviewed evidence.
- [ ] Level B rejects canned/unverified Runs and enforces real GRADED PARTIAL/FAIL -> GRADED PASS with stable Agent/Judge configuration and changed Skill identity.
- [ ] Level A/B claim is honest.
