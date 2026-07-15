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


def _find_unescaped(text: str, character: str, start: int) -> int:
    index = start
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == character:
            return index
        index += 1
    return -1


def _parse_inline_destination(line: str, opening_parenthesis: int) -> tuple[str, int] | None:
    start = opening_parenthesis + 1
    while start < len(line) and line[start] in " \t":
        start += 1
    if start < len(line) and line[start] == "<":
        closing_angle = _find_unescaped(line, ">", start + 1)
        if closing_angle < 0:
            return None
        closing_parenthesis = _find_unescaped(line, ")", closing_angle + 1)
        if closing_parenthesis < 0:
            return None
        return line[start : closing_angle + 1], closing_parenthesis + 1

    depth = 1
    index = start
    while index < len(line):
        if line[index] == "\\":
            index += 2
            continue
        if line[index] == "(":
            depth += 1
        elif line[index] == ")":
            depth -= 1
            if depth == 0:
                return line[start:index], index + 1
        index += 1
    return None


def _iter_inline_link_targets(line: str) -> list[str]:
    targets: list[str] = []
    index = 0
    while index < len(line):
        opening = line.find("[", index)
        if opening < 0:
            break
        closing = _find_unescaped(line, "]", opening + 1)
        if closing < 0:
            break
        if closing + 1 < len(line) and line[closing + 1] == "(":
            parsed = _parse_inline_destination(line, closing + 1)
            if parsed is not None:
                target, index = parsed
                targets.append(target)
                continue
        index = closing + 1
    return targets


def _normalize_reference_label(label: str) -> str:
    return " ".join(label.split()).casefold()


def _parse_reference_definition(line: str) -> tuple[str, str] | None:
    leading_spaces = len(line) - len(line.lstrip(" "))
    if leading_spaces > 3:
        return None
    content = line[leading_spaces:]
    if not content.startswith("["):
        return None
    closing = _find_unescaped(content, "]", 1)
    if closing < 0 or closing + 1 >= len(content) or content[closing + 1] != ":":
        return None
    label = _normalize_reference_label(content[1:closing])
    remainder = content[closing + 2 :].lstrip(" \t")
    if not label or not remainder:
        return None
    if remainder.startswith("<"):
        closing_angle = _find_unescaped(remainder, ">", 1)
        if closing_angle < 0:
            return None
        return label, remainder[: closing_angle + 1]

    depth = 0
    index = 0
    while index < len(remainder):
        if remainder[index] == "\\":
            index += 2
            continue
        if remainder[index] == "(":
            depth += 1
        elif remainder[index] == ")" and depth:
            depth -= 1
        elif remainder[index].isspace() and depth == 0:
            break
        index += 1
    target = remainder[:index]
    return (label, target) if target else None


def _collect_reference_definitions(lines: list[str]) -> dict[str, str]:
    definitions: dict[str, str] = {}
    for line in lines:
        definition = _parse_reference_definition(line)
        if definition is not None:
            label, target = definition
            definitions.setdefault(label, target)
    return definitions


def _iter_reference_link_targets(line: str, definitions: dict[str, str]) -> list[str]:
    if _parse_reference_definition(line) is not None:
        return []
    targets: list[str] = []
    index = 0
    while index < len(line):
        opening = line.find("[", index)
        if opening < 0:
            break
        closing = _find_unescaped(line, "]", opening + 1)
        if closing < 0:
            break
        label_text = line[opening + 1 : closing]
        next_index = closing + 1
        if next_index < len(line) and line[next_index] == "(":
            parsed = _parse_inline_destination(line, next_index)
            index = parsed[1] if parsed is not None else next_index + 1
            continue
        if next_index < len(line) and line[next_index] == "[":
            label_closing = _find_unescaped(line, "]", next_index + 1)
            if label_closing < 0:
                index = next_index + 1
                continue
            explicit_label = line[next_index + 1 : label_closing]
            label = explicit_label if explicit_label else label_text
            index = label_closing + 1
        else:
            label = label_text
            index = next_index
        target = definitions.get(_normalize_reference_label(label))
        if target is not None:
            targets.append(target)
    return targets


def check_local_links(root: Path, documents: dict[Path, str]) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    for source, text in sorted(
        documents.items(),
        key=lambda item: item[0].relative_to(root).as_posix(),
    ):
        relative = source.relative_to(root).as_posix()
        lines = strip_code(text).splitlines()
        definitions = _collect_reference_definitions(lines)
        for line_number, line in enumerate(lines, start=1):
            targets = _iter_inline_link_targets(line)
            targets.extend(_iter_reference_link_targets(line, definitions))
            for target in targets:
                if _local_link_is_broken(root, source, target):
                    findings.append(
                        Finding(
                            relative,
                            line_number,
                            "broken-local-link",
                            f"unresolvable local target: {target.strip()}",
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
