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
