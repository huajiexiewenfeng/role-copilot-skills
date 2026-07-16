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
from tempfile import TemporaryDirectory
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
DEFAULT_WORKSPACE = REPO_ROOT.parent / "project-develop-copilot-eval-workspace"
PUNCTUATION_MAP = str.maketrans(
    {
        "，": ",",
        "。": ".",
        "．": ".",
        "：": ":",
        "；": ";",
        "（": "(",
        "）": ")",
        "“": '"',
        "”": '"',
        "「": '"',
        "」": '"',
        "『": '"',
        "』": '"',
        "‘": "'",
        "’": "'",
        "！": "!",
        "？": "?",
        "、": ",",
        "—": "-",
        "–": "-",
        "－": "-",
        "…": "...",
    }
)


class EvalError(RuntimeError):
    pass


def normalize_quote_v1(value: str) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    normalized = unicodedata.normalize("NFKC", normalized)
    normalized = normalized.translate(PUNCTUATION_MAP)
    return " ".join(normalized.split()).strip()


def quote_matches_evidence(quote: str, evidence: str) -> bool:
    normalized_quote = normalize_quote_v1(quote)
    if not normalized_quote or not any(
        character.isalnum() for character in normalized_quote
    ):
        return False
    return normalized_quote in normalize_quote_v1(evidence)


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


@dataclass(frozen=True)
class GitResult:
    returncode: int
    stdout: bytes
    stderr: bytes

    @property
    def stdout_text(self) -> str:
        return self.stdout.decode("utf-8", errors="strict")


def read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvalError(f"cannot read JSON object {path}: {error}") from error
    if not isinstance(value, dict):
        raise EvalError(f"JSON root must be an object: {path}")
    return value


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_bytes((payload + "\n").encode("utf-8"))
    os.replace(temporary, path)


def git_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    return env


def run_git(
    cwd: Path,
    args: Sequence[str],
    check: bool = True,
    env_overrides: Mapping[str, str] | None = None,
) -> GitResult:
    env = git_environment()
    if env_overrides is not None:
        env.update(env_overrides)
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=env,
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


def parse_porcelain_v1_z(raw: bytes) -> list[dict[str, str | None]]:
    """Parse porcelain v1 -z records; rename paths are destination then source."""
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
        entries.append(
            {
                "status": status,
                "path": path.replace("\\", "/"),
                "original_path": original_path,
            }
        )
    return entries


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _is_reparse_point(file_stat: os.stat_result) -> bool:
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(getattr(file_stat, "st_file_attributes", 0) & reparse_flag)


def _normalize_untracked_path(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value.replace("\\", "/"))
    relative = Path(normalized)
    if (
        not normalized
        or relative.is_absolute()
        or ".." in relative.parts
        or any(part in {"", "."} for part in normalized.split("/"))
    ):
        raise EvalError(f"invalid untracked path: {value}")
    return normalized


def _read_regular_for_capture(
    path: Path, expected_stat: os.stat_result
) -> tuple[int, str, bytes | None]:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise EvalError(f"cannot open untracked file {path}: {error}") from error
    try:
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise EvalError(f"untracked entry is not a regular file: {path}")
        expected_identity = (expected_stat.st_dev, expected_stat.st_ino)
        opened_identity = (opened_stat.st_dev, opened_stat.st_ino)
        if expected_identity != opened_identity:
            raise EvalError(f"untracked entry changed while opening: {path}")
        digest = hashlib.sha256()
        size = 0
        captured: bytearray | None = bytearray()
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            for block in iter(lambda: stream.read(64 * 1024), b""):
                digest.update(block)
                size += len(block)
                if captured is not None:
                    if size <= MAX_UNTRACKED_FILE_BYTES:
                        captured.extend(block)
                    else:
                        captured = None
        return size, digest.hexdigest(), None if captured is None else bytes(captured)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def collect_untracked_content(
    fixture_path: Path, paths: Iterable[str]
) -> list[dict[str, Any]]:
    normalized_paths = sorted(_normalize_untracked_path(path) for path in paths)
    manifest: list[dict[str, Any]] = []
    captured_bytes = 0
    for relative_path in normalized_paths:
        parts = relative_path.split("/")
        path = fixture_path
        file_stat = None
        for index, part in enumerate(parts):
            path = path / part
            try:
                file_stat = path.lstat()
            except OSError as error:
                raise EvalError(
                    f"cannot stat untracked entry {path}: {error}"
                ) from error
            if (
                path.is_symlink() or _is_reparse_point(file_stat)
            ) and index < len(parts) - 1:
                raise EvalError(f"link-like untracked path component: {path}")
        assert file_stat is not None
        if path.is_symlink() or _is_reparse_point(file_stat):
            try:
                target = os.readlink(path)
            except OSError as error:
                raise EvalError(f"cannot read untracked link {path}: {error}") from error
            target_bytes = target.encode("utf-8")
            manifest.append(
                {
                    "capture": {"reason": "link", "status": "omitted"},
                    "kind": "link",
                    "path": relative_path,
                    "sha256": _sha256_bytes(target_bytes),
                    "size": len(target_bytes),
                    "target": target,
                }
            )
            continue
        if not stat.S_ISREG(file_stat.st_mode):
            raise EvalError(f"untracked entry is not a regular file: {path}")

        size, digest, content = _read_regular_for_capture(path, file_stat)
        entry: dict[str, Any] = {
            "kind": "regular",
            "path": relative_path,
            "sha256": digest,
            "size": size,
        }
        if content is None:
            entry["capture"] = {"reason": "file-too-large", "status": "omitted"}
        elif captured_bytes + size > MAX_UNTRACKED_TOTAL_BYTES:
            entry["capture"] = {"reason": "run-cap-exceeded", "status": "omitted"}
        else:
            captured_bytes += size
            try:
                text = content.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                encoding = "base64"
                captured_content = base64.b64encode(content).decode("ascii")
            else:
                if "\0" in text:
                    encoding = "base64"
                    captured_content = base64.b64encode(content).decode("ascii")
                else:
                    encoding = "utf-8"
                    captured_content = text
            entry["capture"] = {
                "content": captured_content,
                "encoding": encoding,
                "status": "captured",
            }
        manifest.append(entry)
    return manifest


def fingerprint_tree(root: Path) -> str:
    resolved_root = root.resolve(strict=True)
    if not resolved_root.is_dir():
        raise EvalError(f"fingerprint root must be a directory: {root}")

    files: list[tuple[str, Path, os.stat_result]] = []

    def visit(directory: Path, relative_parts: tuple[str, ...]) -> None:
        try:
            entries = list(os.scandir(directory))
        except OSError as error:
            raise EvalError(f"cannot scan fingerprint root {directory}: {error}") from error
        for entry in entries:
            if entry.name in {".git", "__pycache__"}:
                continue
            try:
                file_stat = entry.stat(follow_symlinks=False)
            except OSError as error:
                raise EvalError(f"cannot stat fingerprint entry {entry.path}: {error}") from error
            if stat.S_ISLNK(file_stat.st_mode) or _is_reparse_point(file_stat):
                continue
            parts = (*relative_parts, entry.name)
            path = Path(entry.path)
            if stat.S_ISDIR(file_stat.st_mode):
                visit(path, parts)
            elif stat.S_ISREG(file_stat.st_mode):
                normalized_path = unicodedata.normalize("NFC", "/".join(parts))
                files.append((normalized_path, path, file_stat))

    visit(resolved_root, ())
    serialized_entries = [
        {
            "kind": "file",
            "path": relative_path,
            "sha256": _sha256_file(path),
            "size": file_stat.st_size,
        }
        for relative_path, path, file_stat in sorted(files, key=lambda item: item[0])
    ]
    payload = json.dumps(
        serialized_entries,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256_bytes(payload)


def _require_string(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise EvalError(f"{key} must be a non-empty string")
    return item


def validate_judge_adoption_fields(judge: Mapping[str, Any]) -> None:
    assertions = judge.get("assertions", ())
    for assertion in assertions:
        assertion_id = assertion.get("id")
        is_canary_adoption = isinstance(assertion_id, str) and assertion_id.startswith(
            "canary-adoption:"
        )
        if is_canary_adoption and "adopted" not in assertion:
            raise EvalError("adopted is required for canary-adoption assertions")
        if not is_canary_adoption and "adopted" in assertion:
            raise EvalError("adopted is forbidden for non-canary assertions")


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


def _extract_contract_section(path: Path, heading: str) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(heading)
    except ValueError as error:
        raise EvalError(f"contract heading missing: {path} {heading}") from error
    heading_level = len(heading) - len(heading.lstrip("#"))
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = re.match(r"^(#+)\s", lines[index])
        if match is not None and len(match.group(1)) <= heading_level:
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def build_judge_request(
    run_path: Path,
    profile: EvalProfile,
    answer: str,
    diff: bytes,
    observations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    answer_bytes = answer.encode("utf-8")
    evidence_registry: dict[str, dict[str, Any]] = {
        "answer.md": {
            "kind": "text",
            "path": "answer.md",
            "encoding": "utf-8",
            "sha256": _sha256_bytes(answer_bytes),
            "size": len(answer_bytes),
            "quotable": True,
            "content": answer,
        }
    }
    diff_is_binary = any(
        marker in diff
        for marker in (b"\x00", b"GIT binary patch", b"Binary files ")
    )
    try:
        diff_text = None if diff_is_binary else diff.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        diff_text = None
    if diff_text is None:
        evidence_registry["diff.patch"] = {
            "kind": "binary",
            "path": "diff.patch",
            "sha256": _sha256_bytes(diff),
            "size": len(diff),
            "quotable": False,
        }
    else:
        evidence_registry["diff.patch"] = {
            "kind": "text",
            "path": "diff.patch",
            "encoding": "utf-8",
            "sha256": _sha256_bytes(diff),
            "size": len(diff),
            "quotable": True,
            "content": diff_text,
        }

    contract_sections = [
        {
            "path": contract_path,
            "heading": heading,
            "content": _extract_contract_section(SKILL_ROOT / contract_path, heading),
        }
        for contract_path, heading in profile.contract_refs
    ]
    request: dict[str, Any] = {
        "schema_version": JUDGE_SCHEMA_VERSION,
        "profile_version": profile.profile_version,
        "prompt_version": JUDGE_PROMPT_VERSION,
        "evidence_match_mode": QUOTE_MATCH_MODE,
        "evidence_normalizer_version": QUOTE_NORMALIZER_VERSION,
        "canonical_eval": extract_canonical_eval(profile),
        "contract_sections": contract_sections,
        "semantic_assertion_ids": list(profile.semantic_assertion_ids),
        "canary_observations": [dict(item) for item in observations],
        "canary_adoption": {
            "assertion_id_format": "canary-adoption:<pair-id>",
            "required_for_states": ["wiki_only", "source_only", "both"],
            "output_enum": ["preferred", "source", "neither", "uncertain"],
            "minimum_preferred": profile.min_observed_pairs,
            "pair_count": len(profile.canary_pairs),
        },
        "evidence_registry": evidence_registry,
        "instruction": (
            "Return every required semantic and canary-adoption assertion. "
            "Every verdict must include an evidence_quote from its declared "
            "evidence_ref. Quotes are checked only by case-sensitive "
            "normalized substring matching within that one evidence source."
        ),
    }
    write_json(run_path / "judge-request.json", request)
    return request


def _utc_timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise EvalError("Run time must be timezone-aware")
    utc = value.astimezone(timezone.utc).replace(microsecond=0)
    return utc.isoformat().replace("+00:00", "Z")


def _workspace_is_inside_repository(workspace: Path) -> bool:
    try:
        workspace.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return False
    return True


def _skill_identity(skill_path: Path | None) -> dict[str, Any]:
    if skill_path is None:
        return {
            "fingerprint_sha256": None,
            "path": None,
            "status": "unverified",
        }
    resolved = skill_path.expanduser().resolve(strict=True)
    if not resolved.is_dir():
        raise EvalError(f"Skill path must be a directory: {skill_path}")
    return {
        "fingerprint_sha256": fingerprint_tree(resolved),
        "path": str(resolved),
        "status": "verified",
    }


def prepare_run(
    eval_id: str,
    workspace: Path,
    skill_path: Path | None,
    run_id: str | None = None,
    now: Callable[[], datetime] | None = None,
) -> Path:
    profile = load_profile(eval_id)
    resolved_workspace = workspace.expanduser().resolve(strict=False)
    if _workspace_is_inside_repository(resolved_workspace):
        raise EvalError(f"Run workspace must be outside the source repository: {workspace}")

    instant = (now or (lambda: datetime.now(timezone.utc)))()
    timestamp = _utc_timestamp(instant)
    expected_prefix = f"eval-{int(profile.eval_id):03d}-"
    if run_id is None:
        run_id = (
            f"{expected_prefix}{instant.astimezone(timezone.utc):%Y%m%dT%H%M%SZ}-"
            f"{uuid.uuid4().hex[:8]}"
        )
    if not re.fullmatch(
        rf"{re.escape(expected_prefix)}[A-Za-z0-9][A-Za-z0-9._-]*", run_id
    ):
        raise EvalError(
            f"Run ID must be one separator-free {expected_prefix}* path component"
        )

    identity = _skill_identity(skill_path)
    skill_source_commit = run_git(REPO_ROOT, ["rev-parse", "HEAD"]).stdout_text.strip()
    run_path = resolved_workspace / run_id
    if run_path.exists():
        raise EvalError(f"Run directory already exists: {run_path}")

    resolved_workspace.mkdir(parents=True, exist_ok=True)
    run_path.mkdir()
    fixture_path = run_path / "fixture"
    shutil.copytree(profile.fixture_root, fixture_path, symlinks=True)

    canonical_prompt = extract_canonical_prompt(profile)
    effective_prompt = f"{canonical_prompt}\n\n{profile.prompt_appendix}\n"
    prompt_bytes = effective_prompt.encode("utf-8")
    (run_path / "prompt.md").write_bytes(prompt_bytes)
    (run_path / "answer.md").write_bytes(b"")

    run_git(fixture_path, ["init"])
    run_git(fixture_path, ["config", "core.autocrlf", "false"])
    run_git(fixture_path, ["add", "--all"])
    run_git(
        fixture_path,
        [
            "-c",
            "user.name=Blackbox Eval",
            "-c",
            "user.email=blackbox-eval@example.invalid",
            "-c",
            "commit.gpgSign=false",
            "commit",
            "-m",
            "Baseline fixture",
        ],
    )
    fixture_baseline_commit = run_git(
        fixture_path, ["rev-parse", "HEAD"]
    ).stdout_text.strip()
    if run_git(fixture_path, ["status", "--porcelain"]).stdout:
        raise EvalError("Fixture repository is not clean after baseline commit")

    write_json(
        run_path / "run.json",
        {
            "agent_identity": None,
            "answer_sha256": None,
            "canonical_prompt_sha256": _sha256_bytes(canonical_prompt.encode("utf-8")),
            "created_at": timestamp,
            "effective_prompt_sha256": _sha256_bytes(prompt_bytes),
            "eval_id": profile.eval_id,
            "fixture_baseline_commit": fixture_baseline_commit,
            "fixture_version": profile.fixture_version,
            "freeze_manifest_sha256": None,
            "grader_version": GRADER_VERSION,
            "needs_review_reasons": [],
            "needs_review_since": None,
            "patch_decision_history": [],
            "profile_version": profile.profile_version,
            "prompt_appendix": profile.prompt_appendix,
            "run_id": run_id,
            "run_status": "READY_FOR_AGENT",
            "schema_version": RUN_SCHEMA_VERSION,
            "skill_identity": identity,
            "skill_source_commit": skill_source_commit,
            "unresolved_assertion_ids": [],
        },
    )
    return run_path


def collect_git_evidence(run_path: Path) -> dict[str, Any]:
    run = read_json_object(run_path / "run.json")
    baseline = _require_string(run, "fixture_baseline_commit")
    fixture_path = run_path / "fixture"

    with TemporaryDirectory(prefix="evidence-index-", dir=run_path) as temporary:
        evidence_index = Path(temporary) / "index"
        shutil.copyfile(fixture_path / ".git" / "index", evidence_index)
        env_overrides = {"GIT_INDEX_FILE": str(evidence_index)}
        status_raw = run_git(
            fixture_path,
            ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
            env_overrides=env_overrides,
        ).stdout
        current_head = run_git(
            fixture_path,
            ["rev-parse", "HEAD"],
            env_overrides=env_overrides,
        ).stdout_text.strip()
        diff = run_git(
            fixture_path,
            [
                "diff",
                "--binary",
                "--no-ext-diff",
                "--no-textconv",
                baseline,
                "--",
            ],
            env_overrides=env_overrides,
        ).stdout

    statuses = parse_porcelain_v1_z(status_raw)
    untracked_paths = [
        entry["path"] for entry in statuses if entry["status"] == "??"
    ]
    untracked_manifest = collect_untracked_content(fixture_path, untracked_paths)
    (run_path / "diff.patch").write_bytes(diff)
    evidence = {
        "baseline_head": baseline,
        "current_head": current_head,
        "diff_patch_sha256": _sha256_bytes(diff),
        "diff_patch_size": len(diff),
        "has_any_write": current_head != baseline or bool(statuses) or bool(diff),
        "head_changed": current_head != baseline,
        "statuses": statuses,
        "untracked_manifest": untracked_manifest,
    }
    write_json(run_path / "evidence.json", evidence)
    return evidence


def observe_canary_pairs(
    answer: str, profile: EvalProfile
) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for pair in profile.canary_pairs:
        preferred = pair.preferred in answer
        source = pair.conflicting_source in answer
        state = (
            "both"
            if preferred and source
            else "wiki_only"
            if preferred
            else "source_only"
            if source
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


def _validate_judge_input(
    judge: Mapping[str, Any],
    profile: EvalProfile,
    evidence_registry: Mapping[str, Mapping[str, Any]],
    observations: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    required_keys = {
        "schema_version",
        "model",
        "temperature",
        "prompt_version",
        "profile_version",
        "evidence_match_mode",
        "evidence_normalizer_version",
        "assertions",
    }
    if set(judge) != required_keys:
        raise EvalError("Judge root keys must exactly match the v0.1 schema")
    if judge["schema_version"] != JUDGE_SCHEMA_VERSION:
        raise EvalError("unsupported Judge schema version")
    if not isinstance(judge["model"], str) or not judge["model"]:
        raise EvalError("Judge model must be a non-empty string")
    temperature = judge["temperature"]
    if temperature is not None and (
        isinstance(temperature, bool)
        or not isinstance(temperature, (int, float))
    ):
        raise EvalError("Judge temperature must be a number or null")
    if judge["prompt_version"] != JUDGE_PROMPT_VERSION:
        raise EvalError("unsupported Judge prompt version")
    if judge["profile_version"] != profile.profile_version:
        raise EvalError("Judge Profile version mismatch")
    if judge["evidence_match_mode"] != QUOTE_MATCH_MODE:
        raise EvalError("unsupported Judge evidence match mode")
    if judge["evidence_normalizer_version"] != QUOTE_NORMALIZER_VERSION:
        raise EvalError("unsupported Judge evidence normalizer version")

    profile_pair_ids = [pair.id for pair in profile.canary_pairs]
    observed_pair_ids = [item.get("pair_id") for item in observations]
    if (
        len(observations) != 3
        or len(profile_pair_ids) != 3
        or observed_pair_ids != profile_pair_ids
    ):
        raise EvalError("Judge requires exactly three ordered canary observations")
    allowed_states = {"wiki_only", "source_only", "both", "neither"}
    if any(item.get("state") not in allowed_states for item in observations):
        raise EvalError("unknown canary observation state")

    raw_assertions = judge["assertions"]
    if not isinstance(raw_assertions, list) or not raw_assertions:
        raise EvalError("Judge assertions must be a non-empty list")
    assertions: list[Mapping[str, Any]] = []
    required_assertion_keys = {
        "id",
        "verdict",
        "evidence_ref",
        "evidence_quote",
        "reason",
    }
    for raw_assertion in raw_assertions:
        if not isinstance(raw_assertion, dict):
            raise EvalError("every Judge assertion must be an object")
        assertion_id = raw_assertion.get("id")
        is_canary = isinstance(assertion_id, str) and assertion_id.startswith(
            "canary-adoption:"
        )
        allowed_keys = required_assertion_keys | ({"adopted"} if is_canary else set())
        if set(raw_assertion) != allowed_keys:
            raise EvalError("Judge assertion keys do not match the v0.1 schema")
        for key in required_assertion_keys:
            if not isinstance(raw_assertion[key], str) or not raw_assertion[key]:
                raise EvalError(f"Judge assertion {key} must be a non-empty string")
        if raw_assertion["verdict"] not in {"pass", "fail", "uncertain"}:
            raise EvalError("unknown Judge verdict")
        evidence_ref = raw_assertion["evidence_ref"]
        if evidence_ref not in {"answer.md", "diff.patch"}:
            raise EvalError("unknown Judge evidence ref")
        evidence = evidence_registry.get(evidence_ref)
        if not isinstance(evidence, Mapping):
            raise EvalError("Judge evidence ref is not registered")
        if evidence.get("kind") != "text" or evidence.get("quotable") is not True:
            raise EvalError("Judge evidence ref is not quotable text")
        if not isinstance(evidence.get("content"), str):
            raise EvalError("Judge text evidence has no string content")
        normalized_quote = normalize_quote_v1(raw_assertion["evidence_quote"])
        if not normalized_quote or not any(
            character.isalnum() for character in normalized_quote
        ):
            raise EvalError("Judge evidence quote must contain an alphanumeric character")
        if is_canary:
            adopted = raw_assertion["adopted"]
            expected_verdict = {
                "preferred": "pass",
                "source": "fail",
                "neither": "pass",
                "uncertain": "uncertain",
            }.get(adopted)
            if expected_verdict is None:
                raise EvalError("unknown Judge canary adoption value")
            if raw_assertion["verdict"] != expected_verdict:
                raise EvalError("Judge canary adoption and verdict disagree")
        assertions.append(raw_assertion)

    assertion_ids = [item["id"] for item in assertions]
    if len(assertion_ids) != len(set(assertion_ids)):
        raise EvalError("Judge assertion IDs must not contain duplicates")
    expected_ids = set(profile.semantic_assertion_ids)
    expected_ids.update(
        f"canary-adoption:{item['pair_id']}"
        for item in observations
        if item["state"] != "neither"
    )
    if set(assertion_ids) != expected_ids:
        raise EvalError("Judge assertion IDs do not exactly match expected IDs")
    validate_judge_adoption_fields(judge)
    return assertions


def grade_judge(
    judge: Mapping[str, Any],
    profile: EvalProfile,
    evidence_registry: Mapping[str, Mapping[str, Any]],
    observations: Sequence[Mapping[str, Any]],
    deterministic_assertions: Sequence[AssertionResult] = (),
) -> list[AssertionResult]:
    results = list(deterministic_assertions)
    try:
        assertions = _validate_judge_input(
            judge, profile, evidence_registry, observations
        )
    except (EvalError, KeyError, TypeError) as error:
        results.append(
            AssertionResult(
                id="judge-validation",
                layer="judge-validation",
                outcome="RUN_ERROR",
                severity="hard",
                message=f"judge_input_invalid: {error}",
            )
        )
        return results

    results.append(
        AssertionResult(
            id="judge-validation",
            layer="judge-validation",
            outcome="PASS",
            severity="info",
            message="Judge input satisfies the file-based v0.1 contract.",
        )
    )
    preferred_count = 0
    verdict_outcomes = {
        "pass": "PASS",
        "fail": "FAIL",
        "uncertain": "NEEDS_REVIEW",
    }
    for assertion in assertions:
        evidence_ref = assertion["evidence_ref"]
        evidence_text = evidence_registry[evidence_ref]["content"]
        matched = quote_matches_evidence(
            assertion["evidence_quote"], evidence_text
        )
        outcome = verdict_outcomes[assertion["verdict"]]
        message = assertion["reason"]
        if not matched:
            outcome = "NEEDS_REVIEW"
            message = f"evidence_quote_unmatched: {evidence_ref}"
        if assertion["id"].startswith("canary-adoption:"):
            preferred_count += assertion["adopted"] == "preferred"
        results.append(
            AssertionResult(
                id=assertion["id"],
                layer="judge",
                outcome=outcome,
                severity=(
                    "hard"
                    if outcome == "FAIL"
                    else "soft"
                    if outcome == "NEEDS_REVIEW"
                    else "info"
                ),
                message=message,
                evidence_ids=(f"{evidence_ref}:quote",),
            )
        )

    coverage_outcome = (
        "PASS" if preferred_count >= profile.min_observed_pairs else "PARTIAL"
    )
    results.append(
        AssertionResult(
            id="canary-adoption-coverage",
            layer="judge",
            outcome=coverage_outcome,
            severity="info" if coverage_outcome == "PASS" else "soft",
            message=(
                f"{preferred_count} of exactly {len(profile.canary_pairs)} "
                "canary pairs adopted preferred evidence; "
                f"minimum is {profile.min_observed_pairs}."
            ),
        )
    )
    return results


def _answer_has_standalone_path(answer: str, paths: Iterable[str]) -> bool:
    normalized_answer = answer.replace("\\", "/")
    token_character = r"[\w./-]"
    return any(
        re.search(
            rf"(?<!{token_character}){re.escape(path)}(?!{token_character})",
            normalized_answer,
        )
        is not None
        for path in paths
    )


def _baseline_contains_path(run_path: Path, relative_path: str) -> bool:
    run = read_json_object(run_path / "run.json")
    baseline = _require_string(run, "fixture_baseline_commit")
    listing = run_git(
        run_path / "fixture",
        ["ls-tree", "--name-only", "-z", baseline, "--", relative_path],
    ).stdout
    return bool(listing)


def run_deterministic_assertions(
    run_path: Path,
    profile: EvalProfile,
    answer: str,
    git_evidence: Mapping[str, Any],
) -> tuple[list[AssertionResult], list[dict[str, Any]]]:
    assertions: list[AssertionResult] = []
    has_any_write = git_evidence.get("has_any_write") is True
    assertions.append(
        AssertionResult(
            id="write-boundary",
            layer="deterministic",
            outcome="FAIL" if has_any_write else "PASS",
            severity="hard" if has_any_write else "info",
            message=(
                "Git evidence contains at least one fixture write."
                if has_any_write
                else "Git evidence contains no fixture writes."
            ),
            evidence_ids=("git-evidence:write-state",),
        )
    )

    cited_wiki_path = _answer_has_standalone_path(
        answer, profile.required_path_any_of
    )
    assertions.append(
        AssertionResult(
            id="wiki-path-citation",
            layer="deterministic",
            outcome="PASS" if cited_wiki_path else "PARTIAL",
            severity="info" if cited_wiki_path else "soft",
            message=(
                "Answer cites at least one configured Wiki evidence path."
                if cited_wiki_path
                else "Answer cites none of the configured Wiki evidence paths."
            ),
            evidence_ids=("answer:wiki-path-citation",),
        )
    )

    if profile.eval_id == "32":
        root_index = ".llm-wiki/index.md"
        existed_in_baseline = _baseline_contains_path(run_path, root_index)
        current_path = run_path / "fixture" / root_index
        exists_now = current_path.exists() or current_path.is_symlink()
        if existed_in_baseline:
            root_index_outcome = "RUN_ERROR"
            root_index_message = (
                "Eval 32 fixture contract is invalid: the baseline contains "
                f"{root_index}."
            )
        elif exists_now:
            root_index_outcome = "FAIL"
            root_index_message = f"The run created {root_index}."
        else:
            root_index_outcome = "PASS"
            root_index_message = f"The run did not create {root_index}."
        assertions.append(
            AssertionResult(
                id="wiki-root-index-absent",
                layer="deterministic",
                outcome=root_index_outcome,
                severity=(
                    "hard"
                    if root_index_outcome in {"RUN_ERROR", "FAIL"}
                    else "info"
                ),
                message=root_index_message,
                evidence_ids=(
                    "fixture-baseline:.llm-wiki/index.md",
                    "fixture-current:.llm-wiki/index.md",
                ),
            )
        )

    observations = observe_canary_pairs(answer, profile)
    has_observed_canary = any(
        item["state"] != "neither" for item in observations
    )
    assertions.append(
        AssertionResult(
            id="canary-coverage",
            layer="deterministic",
            outcome="PASS" if has_observed_canary else "PARTIAL",
            severity="info" if has_observed_canary else "soft",
            message=(
                "At least one canary pair has an observable literal."
                if has_observed_canary
                else "No canary pair has an observable literal."
            ),
            evidence_ids=tuple(
                f"answer:canary:{item['pair_id']}" for item in observations
            ),
        )
    )

    assertions.extend(
        AssertionResult(
            id=item.id,
            layer="manual-only",
            outcome="UNAUTOMATED",
            severity="info",
            message=f"coverage={item.coverage}; reason={item.reason}",
        )
        for item in profile.manual_only_assertions
    )
    return assertions, observations
