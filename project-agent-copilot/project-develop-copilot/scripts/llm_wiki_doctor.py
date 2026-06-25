#!/usr/bin/env python3
"""Repo-local .llm-wiki validator.

This script intentionally uses only Python's standard library so it can run in
local hooks and CI without preparing a toolchain.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


TOKEN_LEFT = r"(?<![A-Za-z0-9_-])"
TOKEN_RIGHT = r"(?![A-Za-z0-9_-])"
EDGE_ID_RE = re.compile(r"edge-\d{8}-\d{3,}")
CROSS_SERVICE_RE = re.compile(
    r"\b(Feign|MQTT|HTTP|WebSocket|API gateway|shared config|shared db)\b|共享\s*(DB|配置)",
    re.IGNORECASE,
)
DOC_SIGNAL_RE = re.compile(r"\b(design|requirement|bug|plan)\b|设计|需求|缺陷|方案|计划", re.IGNORECASE)
ORIGINAL_PATH_RE = re.compile(r"^\s*-?\s*original_path\s*:\s*`?([^`\r\n]+?)`?\s*$", re.IGNORECASE | re.MULTILINE)
IGNORE_RE_TEMPLATE = r"<!--\s*llm-wiki-ignore:\s*{check}\s+reason\s*=\s*['\"][^'\"]+['\"]\s*-->"


@dataclass(frozen=True)
class Finding:
    check: str
    severity: str
    path: str
    message: str
    line: int | None = None
    hint: str | None = None


@dataclass(frozen=True)
class ProjectRegistry:
    project_ids: set[str]
    local_projects: set[str]
    aliases: dict[str, str]
    edge_ids: set[str]


def normalize_path(path: str | Path) -> str:
    value = str(path).replace("\\", "/").strip()
    while value.startswith("./"):
        value = value[2:]
    return value


def repo_relative(root: Path, path: Path) -> str:
    try:
        return normalize_path(path.relative_to(root))
    except ValueError:
        return normalize_path(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return ""


def load_registry(root: Path) -> ProjectRegistry:
    project_ids: set[str] = set()
    local_projects: set[str] = set()
    aliases: dict[str, str] = {}
    project_ids_path = root / ".llm-wiki" / "project-ids.json"
    if project_ids_path.exists():
        data = json.loads(read_text(project_ids_path))
        local_projects = {item.strip() for item in data.get("local_projects", []) if item.strip()}
        for item in data.get("projects", []):
            project_id = item.get("id", "").strip()
            if not project_id:
                continue
            project_ids.add(project_id)
            for alias in item.get("aliases", []):
                if alias:
                    aliases[alias.strip()] = project_id
    project_ids.update(local_projects)

    edges_text = read_text(root / ".llm-wiki" / "project-graph" / "edges.md")
    edge_ids = set(EDGE_ID_RE.findall(edges_text))
    return ProjectRegistry(project_ids=project_ids, local_projects=local_projects, aliases=aliases, edge_ids=edge_ids)


def project_pattern(project_id: str) -> re.Pattern[str]:
    return re.compile(rf"{TOKEN_LEFT}{re.escape(project_id)}{TOKEN_RIGHT}")


def extract_project_mentions(text: str, registry: ProjectRegistry) -> set[str]:
    mentions: set[str] = set()
    for project_id in sorted(registry.project_ids, key=len, reverse=True):
        if project_pattern(project_id).search(text):
            mentions.add(project_id)
    for alias, canonical in sorted(registry.aliases.items(), key=lambda item: len(item[0]), reverse=True):
        if project_pattern(alias).search(text):
            mentions.add(canonical)
    return mentions


def has_ignore(text: str, check: str) -> bool:
    return bool(re.search(IGNORE_RE_TEMPLATE.format(check=re.escape(check)), text, re.IGNORECASE))


def iter_markdown_files(root: Path) -> list[Path]:
    ignored_dirs = {".git", "target", "node_modules", ".gradle"}
    result: list[Path] = []
    for path in root.rglob("*.md"):
        if any(part in ignored_dirs for part in path.relative_to(root).parts):
            continue
        result.append(path)
    return result


def collect_changed_paths(root: Path, base: str | None = None) -> list[Path]:
    commands = []
    if base:
        commands.append(["git", "diff", "--name-only", base, "--", "*.md"])
    commands.append(["git", "diff", "--cached", "--name-only", "--", "*.md"])
    commands.append(["git", "diff", "--name-only", "--", "*.md"])
    seen: set[Path] = set()
    for command in commands:
        try:
            output = subprocess.check_output(command, cwd=root, text=True, stderr=subprocess.DEVNULL)
        except Exception:
            continue
        for line in output.splitlines():
            path = root / normalize_path(line)
            if path.exists():
                seen.add(path)
    return sorted(seen) if seen else iter_markdown_files(root)


def is_conventional_doc_path(relative_path: str) -> bool:
    return relative_path.startswith(
        ("docs/plans/", "docs/designs/", "docs/requirements/", "docs/bugs/")
    )


def should_check_orphan(relative_path: str, text: str, registry: ProjectRegistry) -> bool:
    if is_conventional_doc_path(relative_path):
        return True
    return bool(DOC_SIGNAL_RE.search(text) or CROSS_SERVICE_RE.search(text) or extract_project_mentions(text, registry))


def parse_markdown_table_rows(text: str) -> Iterable[list[str]]:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip().strip("`") for cell in stripped.strip("|").split("|")]
        if cells:
            yield cells


def registered_source_paths(root: Path) -> set[str]:
    paths: set[str] = set()
    ingest_text = read_text(root / ".llm-wiki" / "ingest" / "index.md")
    for cells in parse_markdown_table_rows(ingest_text):
        if len(cells) >= 2 and cells[0].lower() != "source id":
            paths.add(normalize_path(cells[1]))
    for base in [root / ".llm-wiki" / "sources" / "proxies", root / ".llm-wiki" / "requirements"]:
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            for match in ORIGINAL_PATH_RE.findall(read_text(path)):
                paths.add(normalize_path(match))
    return paths


def check_orphan_design_doc(root: Path, paths: list[Path], registry: ProjectRegistry) -> list[Finding]:
    registered = registered_source_paths(root)
    findings: list[Finding] = []
    for path in paths:
        relative_path = repo_relative(root, path)
        if not relative_path.startswith("docs/") or path.suffix.lower() != ".md":
            continue
        text = read_text(path)
        if has_ignore(text, "orphan-design-doc"):
            continue
        if not should_check_orphan(relative_path, text, registry):
            continue
        if relative_path in registered:
            continue
        findings.append(
            Finding(
                check="orphan-design-doc",
                severity="WARN",
                path=relative_path,
                message=f"{relative_path} is not registered in .llm-wiki by exact source path or original_path.",
                hint="Ingest the source into .llm-wiki or add llm-wiki-ignore with reason.",
            )
        )
    return findings


def is_wiki_artifact(relative_path: str) -> bool:
    return relative_path.startswith(
        (".llm-wiki/requirements/", ".llm-wiki/sources/proxies/", ".llm-wiki/working-context/")
    )


def has_graph_section(text: str) -> bool:
    return "## Project Graph Evidence" in text or "## Project Graph Gaps" in text


def has_cross_service_context(text: str, registry: ProjectRegistry) -> bool:
    mentions = extract_project_mentions(text, registry)
    external_mentions = mentions - registry.local_projects
    if external_mentions:
        return True
    return bool(CROSS_SERVICE_RE.search(text) and mentions)


def check_missing_graph_evidence(root: Path, paths: list[Path], registry: ProjectRegistry) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        relative_path = repo_relative(root, path)
        if not is_wiki_artifact(relative_path):
            continue
        text = read_text(path)
        if has_ignore(text, "missing-graph-evidence"):
            continue
        if not has_cross_service_context(text, registry):
            continue
        if not has_graph_section(text):
            findings.append(
                Finding(
                    check="missing-graph-evidence",
                    severity="WARN",
                    path=relative_path,
                    message=f"{relative_path} mentions a cross-project relation without Project Graph Evidence or Gaps.",
                    hint="Add ## Project Graph Evidence with valid edge ids or ## Project Graph Gaps.",
                )
            )
            continue
        if "## Project Graph Evidence" in text:
            for edge_id in set(EDGE_ID_RE.findall(text)):
                if edge_id not in registry.edge_ids:
                    findings.append(
                        Finding(
                            check="invalid-graph-edge",
                            severity="WARN",
                            path=relative_path,
                            message=f"{relative_path} references unknown Project Graph edge {edge_id}.",
                            hint="Use an existing edge id or move the relation to Project Graph Gaps.",
                        )
                    )
    return findings


def run_checks(root: str | Path, paths: list[str | Path] | None = None) -> list[Finding]:
    root_path = Path(root).resolve()
    registry = load_registry(root_path)
    if paths is None:
        candidate_paths = iter_markdown_files(root_path)
    else:
        candidate_paths = [(root_path / normalize_path(path)).resolve() for path in paths]
    findings: list[Finding] = []
    findings.extend(check_orphan_design_doc(root_path, candidate_paths, registry))
    findings.extend(check_missing_graph_evidence(root_path, candidate_paths, registry))
    return findings


def format_text(findings: list[Finding]) -> str:
    if not findings:
        return "llm-wiki doctor: no findings"
    lines = ["llm-wiki doctor findings:"]
    for finding in findings:
        location = f"{finding.path}:{finding.line}" if finding.line else finding.path
        lines.append(f"[{finding.severity}] {finding.check} {location} - {finding.message}")
        if finding.hint:
            lines.append(f"  hint: {finding.hint}")
    return "\n".join(lines)


def exit_code(findings: list[Finding], fail_on: str) -> int:
    if fail_on == "warn" and findings:
        return 1
    return 1 if any(finding.severity == "ERROR" for finding in findings) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate repo-local .llm-wiki artifacts.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--all", action="store_true", help="Scan all Markdown files")
    parser.add_argument("--changed", action="store_true", help="Scan changed Markdown files")
    parser.add_argument("--base", help="Git base ref for changed scan")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--fail-on", choices=["error", "warn"], default="error")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    paths = None
    if args.changed or args.base:
        paths = collect_changed_paths(root, args.base)
    findings = run_checks(root, paths)
    if args.format == "json":
        print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))
    else:
        print(format_text(findings))
    return exit_code(findings, args.fail_on)


if __name__ == "__main__":
    sys.exit(main())
