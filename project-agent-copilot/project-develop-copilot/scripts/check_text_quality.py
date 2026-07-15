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
