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
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


TOKEN_LEFT = r"(?<![A-Za-z0-9_-])"
TOKEN_RIGHT = r"(?![A-Za-z0-9_-])"
EDGE_ID_RE = re.compile(r"edge-\d{8}-\d{3,}")
LOCAL_PATH_RE = re.compile(
    r"(?i)(?:[A-Z]:\\Users\\[^`\s|]+|/Users/[^`\s|]+|/home/[^`\s|]+|registry\.local\.json|scan-state\.local\.json)"
)
STRUCTURED_PROJECT_FIELD_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(project|from_project|to_project|remote_project)\s*:\s*`?([A-Za-z0-9_.-]+)`?\s*$",
    re.IGNORECASE,
)
CROSS_SERVICE_RE = re.compile(
    r"\b(Feign|MQTT|HTTP|WebSocket|API gateway|shared config|shared db)\b|共享\s*(DB|配置)",
    re.IGNORECASE,
)
DOC_SIGNAL_RE = re.compile(r"\b(design|requirement|bug|plan)\b|设计|需求|缺陷|方案|计划", re.IGNORECASE)
ORIGINAL_PATH_RE = re.compile(r"^\s*-?\s*original_path\s*:\s*`?([^`\r\n]+?)`?\s*$", re.IGNORECASE | re.MULTILINE)
IGNORE_RE_TEMPLATE = r"<!--\s*llm-wiki-ignore:\s*{check}\s+reason\s*=\s*['\"][^'\"]+['\"]\s*-->"
STANDARD_MODULE_CONTEXT_FILES = ("README.md", "source-map.md", "architecture.md", "rules.md", "verification.md")
READY_MODULE_STATUSES = {"active", "ready", "source-backed", "scoped-context-ready", "complete", "completed"}


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


def split_markdown_table_row(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return False
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def table_rows_with_header(text: str) -> Iterable[tuple[list[str], list[str], int]]:
    lines = text.splitlines()
    for index in range(len(lines) - 2):
        header_line = lines[index].strip()
        if not header_line.startswith("|") or not is_table_separator(lines[index + 1]):
            continue
        headers = [header.lower().replace(" ", "_") for header in split_markdown_table_row(header_line)]
        row_index = index + 2
        while row_index < len(lines) and lines[row_index].strip().startswith("|"):
            if not is_table_separator(lines[row_index]):
                yield headers, split_markdown_table_row(lines[row_index]), row_index + 1
            row_index += 1


def cell_by_header(headers: list[str], row: list[str], name: str) -> str:
    normalized = name.lower().replace(" ", "_")
    try:
        index = headers.index(normalized)
    except ValueError:
        return ""
    return row[index].strip().strip("`") if index < len(row) else ""


def parse_maven_modules(root: Path) -> list[str]:
    pom = root / "pom.xml"
    if not pom.exists():
        return []
    try:
        document = ET.fromstring(read_text(pom))
    except ET.ParseError:
        return []

    modules: list[str] = []
    for element in document.iter():
        if element.tag.split("}")[-1] != "module":
            continue
        module = (element.text or "").strip().strip("/\\")
        if module:
            modules.append(normalize_path(module))
    return modules


def list_wiki_module_contexts(root: Path) -> set[str]:
    modules_root = root / ".llm-wiki" / "modules"
    if not modules_root.exists():
        return set()
    return {path.name for path in modules_root.iterdir() if path.is_dir()}


def ready_modules_from_index(root: Path) -> dict[str, int]:
    index_path = root / ".llm-wiki" / "modules" / "index.md"
    text = read_text(index_path)
    ready: dict[str, int] = {}
    if not text:
        return ready
    for headers, row, line in table_rows_with_header(text):
        module = cell_by_header(headers, row, "module") or cell_by_header(headers, row, "name")
        status = cell_by_header(headers, row, "status") or cell_by_header(headers, row, "state")
        if module and status.strip().lower() in READY_MODULE_STATUSES:
            ready[normalize_path(module)] = line
    return ready


def module_context_coverage(root: Path) -> dict[str, object]:
    pom_modules = parse_maven_modules(root)
    wiki_modules = list_wiki_module_contexts(root)
    missing_modules = [module for module in pom_modules if Path(module).name not in wiki_modules]
    return {
        "pom_modules": pom_modules,
        "wiki_modules": sorted(wiki_modules),
        "missing_modules": missing_modules,
        "coverage_ratio": (len(pom_modules) - len(missing_modules)) / len(pom_modules) if pom_modules else None,
    }


def check_module_context_coverage(root: Path) -> list[Finding]:
    pom_modules = parse_maven_modules(root)
    if not pom_modules:
        return []

    wiki_modules = list_wiki_module_contexts(root)
    ready_modules = ready_modules_from_index(root)
    findings: list[Finding] = []

    for module in pom_modules:
        context_dir_name = Path(module).name
        context_path = root / ".llm-wiki" / "modules" / context_dir_name
        relative_context = f".llm-wiki/modules/{context_dir_name}"
        missing_files = [name for name in STANDARD_MODULE_CONTEXT_FILES if not (context_path / name).exists()]
        ready_line = ready_modules.get(context_dir_name) or ready_modules.get(module)

        if context_dir_name not in wiki_modules:
            if ready_line:
                findings.append(
                    Finding(
                        check="contradictory-module-context",
                        severity="ERROR",
                        path=".llm-wiki/modules/index.md",
                        line=ready_line,
                        message=f"Module index marks `{context_dir_name}` as ready, but `{relative_context}/` is missing.",
                        hint="Downgrade the module index status or create the missing scoped context files.",
                    )
                )
            findings.append(
                Finding(
                    check="missing-module-context",
                    severity="WARN",
                    path=relative_context,
                    message=f"Enabled Maven module `{module}` has no `{relative_context}/` scoped context.",
                    hint="Create the module scoped context skeleton or explicitly document why this module is intentionally out of scope.",
                )
            )
            continue

        if missing_files:
            if ready_line:
                findings.append(
                    Finding(
                        check="contradictory-module-context",
                        severity="ERROR",
                        path=".llm-wiki/modules/index.md",
                        line=ready_line,
                        message=(
                            f"Module index marks `{context_dir_name}` as ready, but `{relative_context}/` "
                            f"is missing {', '.join(f'`{name}`' for name in missing_files)}."
                        ),
                        hint="Downgrade the module index status or add the missing standard scoped-context files.",
                    )
                )
            findings.append(
                Finding(
                    check="incomplete-module-context",
                    severity="WARN",
                    path=relative_context,
                    message=f"`{relative_context}/` is missing {', '.join(f'`{name}`' for name in missing_files)}.",
                    hint="Add the missing standard scoped-context files, even if their content starts as source-backed stub notes.",
                )
            )

    return findings


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
                            check="invalid-edge-id",
                            severity="ERROR",
                            path=relative_path,
                            message=f"{relative_path} references unknown Project Graph edge {edge_id}.",
                            hint="Use an existing edge id or move the relation to Project Graph Gaps.",
                        )
                    )
    return findings


def check_dangling_cross_refs(root: Path, registry: ProjectRegistry) -> list[Finding]:
    path = root / ".llm-wiki" / "cross-refs" / "index.md"
    text = read_text(path)
    if not text:
        return []
    relative_path = repo_relative(root, path)
    findings: list[Finding] = []
    seen: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for edge_id in EDGE_ID_RE.findall(line):
            if edge_id in seen or edge_id in registry.edge_ids:
                continue
            seen.add(edge_id)
            findings.append(
                Finding(
                    check="dangling-cross-ref",
                    severity="ERROR",
                    path=relative_path,
                    line=line_number,
                    message=f"{relative_path} references missing Project Graph edge {edge_id}.",
                    hint="Create the confirmed edge in project-graph/edges.md or remove the cross-ref pin.",
                )
            )
    return findings


def check_duplicate_edge_fingerprints(root: Path) -> list[Finding]:
    path = root / ".llm-wiki" / "project-graph" / "edges.md"
    text = read_text(path)
    if not text:
        return []
    relative_path = repo_relative(root, path)
    first_seen: dict[str, int] = {}
    findings: list[Finding] = []
    reported: set[str] = set()
    for headers, row, line_number in table_rows_with_header(text):
        fingerprint = (
            cell_by_header(headers, row, "fingerprint")
            or cell_by_header(headers, row, "edge_fingerprint")
            or cell_by_header(headers, row, "relation_fingerprint")
        )
        fingerprint = fingerprint.strip()
        if not fingerprint or fingerprint in {"-", "n/a", "N/A"}:
            continue
        if fingerprint in first_seen and fingerprint not in reported:
            reported.add(fingerprint)
            findings.append(
                Finding(
                    check="duplicate-edge-fingerprint",
                    severity="ERROR",
                    path=relative_path,
                    line=line_number,
                    message=f"Project Graph edge fingerprint `{fingerprint}` is duplicated.",
                    hint=f"Keep one confirmed relationship per fingerprint; first seen near line {first_seen[fingerprint]}.",
                )
            )
        else:
            first_seen[fingerprint] = line_number
    return findings


def check_leaked_local_paths(root: Path, paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        relative_path = repo_relative(root, path)
        if not relative_path.startswith(".llm-wiki/") or path.suffix.lower() != ".md":
            continue
        text = read_text(path)
        if has_ignore(text, "leaked-local-path"):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if LOCAL_PATH_RE.search(line):
                findings.append(
                    Finding(
                        check="leaked-local-path",
                        severity="ERROR",
                        path=relative_path,
                        line=line_number,
                        message=f"{relative_path} contains local-only path or registry data.",
                        hint="Move workstation-specific paths into local-only registry files and keep committed docs portable.",
                    )
                )
                break
    return findings


def known_project_token(value: str, registry: ProjectRegistry) -> bool:
    value = value.strip().strip("`")
    return not value or value in {"-", "n/a", "N/A"} or value in registry.project_ids or value in registry.aliases


def add_unresolved_project(
    findings: list[Finding],
    root: Path,
    path: Path,
    value: str,
    line: int | None,
):
    findings.append(
        Finding(
            check="unresolved-project-id",
            severity="WARN",
            path=repo_relative(root, path),
            line=line,
            message=f"Structured project id `{value}` is not present in .llm-wiki/project-ids.json.",
            hint="Add the project id or alias to .llm-wiki/project-ids.json, or correct the structured field.",
        )
    )


def check_unresolved_project_ids(root: Path, paths: list[Path], registry: ProjectRegistry) -> list[Finding]:
    findings: list[Finding] = []
    if not registry.project_ids and not registry.aliases:
        return findings

    structured_table_paths = [
        root / ".llm-wiki" / "project-graph" / "edges.md",
        root / ".llm-wiki" / "cross-refs" / "index.md",
    ]
    for path in structured_table_paths:
        text = read_text(path)
        if not text:
            continue
        for headers, row, line_number in table_rows_with_header(text):
            for header in headers:
                if "project" not in header:
                    continue
                value = cell_by_header(headers, row, header)
                if value and not known_project_token(value, registry):
                    add_unresolved_project(findings, root, path, value, line_number)

    for path in paths:
        relative_path = repo_relative(root, path)
        if not relative_path.startswith(".llm-wiki/") or path in structured_table_paths:
            continue
        text = read_text(path)
        for line_number, line in enumerate(text.splitlines(), start=1):
            match = STRUCTURED_PROJECT_FIELD_RE.match(line)
            if match and not known_project_token(match.group(2), registry):
                add_unresolved_project(findings, root, path, match.group(2), line_number)
            if "|" not in line:
                continue
            for headers, row, table_line in table_rows_with_header(text):
                for header in headers:
                    if "project" in header or header == "relation":
                        value = cell_by_header(headers, row, header)
                        for token in re.findall(r"`([A-Za-z0-9_.-]+)`|project:\s*([A-Za-z0-9_.-]+)", value):
                            project_id = token[0] or token[1]
                            if project_id and not known_project_token(project_id, registry):
                                add_unresolved_project(findings, root, path, project_id, table_line)
                break
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
    findings.extend(check_dangling_cross_refs(root_path, registry))
    findings.extend(check_duplicate_edge_fingerprints(root_path))
    findings.extend(check_leaked_local_paths(root_path, candidate_paths))
    findings.extend(check_unresolved_project_ids(root_path, candidate_paths, registry))
    findings.extend(check_module_context_coverage(root_path))
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


PLACEHOLDER_RE = re.compile(
    r"\b(TODO|TBD|placeholder|fill this|to be completed)\b|待补充|占位|稍后完善|请输入",
    re.IGNORECASE,
)


def effective_markdown_length(text: str) -> int:
    useful_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|") or set(stripped) <= {"-", ":", "|", " "}:
            continue
        stripped = PLACEHOLDER_RE.sub("", stripped)
        if stripped:
            useful_lines.append(stripped)
    return len("\n".join(useful_lines))


def has_cross_project_signal(root: Path, registry: ProjectRegistry) -> bool:
    for path in iter_markdown_files(root):
        text = read_text(path)
        if has_cross_service_context(text, registry):
            return True
    return False


def graph_is_applicable(root: Path, registry: ProjectRegistry) -> bool:
    external_projects = registry.project_ids - registry.local_projects
    return bool(external_projects or has_cross_project_signal(root, registry))


def score_level(score: int) -> str:
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 60:
        return "usable"
    return "needs-work"


def build_score_report(root: str | Path) -> ScoreReport:
    root_path = Path(root).resolve()
    registry = load_registry(root_path)
    findings = run_checks(root_path)
    validator_errors = sum(1 for finding in findings if finding.severity == "ERROR")
    validator_warnings = sum(1 for finding in findings if finding.severity == "WARN")

    wiki_root = root_path / ".llm-wiki"
    readme = wiki_root / "README.md"
    modules_index = wiki_root / "modules" / "index.md"
    source_index = wiki_root / "sources" / "registry.md"
    graph_edges = wiki_root / "project-graph" / "edges.md"
    cross_refs = wiki_root / "cross-refs" / "index.md"
    module_coverage = module_context_coverage(root_path)
    pom_modules = module_coverage["pom_modules"]
    missing_modules = module_coverage["missing_modules"]
    coverage_ratio = module_coverage["coverage_ratio"]

    readme_effective_length = effective_markdown_length(read_text(readme))
    module_index_exists = modules_index.exists()
    source_index_exists = source_index.exists()
    wiki_exists = wiki_root.exists()
    graph_applicable = graph_is_applicable(root_path, registry)
    graph_file_presence = {
        "edges": graph_edges.exists(),
        "cross_refs": cross_refs.exists(),
    }

    dimensions: list[ScoreDimension] = []
    structure_score = 0
    structure_score += 10 if wiki_exists else 0
    structure_score += 10 if readme.exists() else 0
    structure_score += 10 if module_index_exists else 0
    structure_score += 10 if source_index_exists else 0
    dimensions.append(
        ScoreDimension(
            name="基础结构",
            max_score=40,
            score=structure_score,
            applicability="applicable",
            source=".llm-wiki standard files",
            message="检查 README、modules index 和 sources registry 是否存在。",
        )
    )

    if coverage_ratio is not None:
        covered_module_count = len(pom_modules) - len(missing_modules)
        dimensions.append(
            ScoreDimension(
                name="模块上下文覆盖率",
                max_score=20,
                score=round(20 * coverage_ratio),
                applicability="applicable",
                source="root pom.xml and .llm-wiki/modules/",
                message=(
                    f"Maven modules={len(pom_modules)}, wiki_module_contexts={covered_module_count}, "
                    f"missing={len(missing_modules)}。"
                ),
            )
        )

    content_score = 30 if readme_effective_length >= 120 else 15 if readme_effective_length >= 40 else 0
    dimensions.append(
        ScoreDimension(
            name="内容有效性",
            max_score=30,
            score=content_score,
            applicability="applicable",
            source=".llm-wiki/README.md",
            message=f"README 有效正文长度为 {readme_effective_length}。",
        )
    )

    if graph_applicable:
        graph_score = 20 if graph_edges.exists() and cross_refs.exists() else 10 if graph_edges.exists() or cross_refs.exists() else 0
        dimensions.append(
            ScoreDimension(
                name="Project Graph / cross-refs",
                max_score=20,
                score=graph_score,
                applicability="applicable",
                source=".llm-wiki/project-graph and cross-refs",
                message="项目存在跨项目信号，需要 Project Graph / cross-refs 支撑。",
            )
        )
    else:
        dimensions.append(
            ScoreDimension(
                name="Project Graph / cross-refs",
                max_score=20,
                score=None,
                applicability="not-applicable",
                source=".llm-wiki/project-ids.json and Markdown cross-service signals",
                message="未发现外部 project-id 或跨服务信号，简单项目不扣 Project Graph 分。",
            )
        )

    validator_score = 30
    if validator_errors:
        validator_score = 0
    elif validator_warnings:
        validator_score = 20
    dimensions.append(
        ScoreDimension(
            name="Validator 健康度",
            max_score=30,
            score=validator_score,
            applicability="applicable",
            source="llm_wiki_doctor validate",
            message=f"validator_errors={validator_errors}, validator_warnings={validator_warnings}。",
        )
    )

    applicable = [dimension for dimension in dimensions if dimension.applicability == "applicable"]
    max_total = sum(dimension.max_score for dimension in applicable) or 1
    raw_total = sum(dimension.score or 0 for dimension in applicable)
    total_score = round(raw_total * 100 / max_total)

    fact_ids: list[str] = []
    next_steps: list[str] = []
    if not readme.exists() or readme_effective_length < 40:
        fact_ids.append("readme-missing-or-thin")
        next_steps.append("完善 .llm-wiki/README.md，写清项目目标、入口、当前上下文状态和关键资料。")
    if not module_index_exists:
        fact_ids.append("modules-index-missing")
        next_steps.append("补齐 .llm-wiki/modules/index.md，用源码证据列出当前活跃模块。")
    if coverage_ratio is not None and missing_modules:
        fact_ids.append("module-context-coverage-incomplete")
        next_steps.append("补齐 Maven module 对应的 .llm-wiki/modules/<module>/ scoped context，不要只依赖 modules/index.md。")
    if not source_index_exists:
        fact_ids.append("sources-registry-missing")
        next_steps.append("补齐 .llm-wiki/sources/registry.md，登记已摄入的 PRD、设计、日志或源码代理。")
    if graph_applicable and not (graph_edges.exists() and cross_refs.exists()):
        fact_ids.append("graph-files-missing")
        next_steps.append("补齐 Project Graph / cross-refs 结构，但只登记已确认或明确待验证的跨项目关系。")
    if validator_errors:
        fact_ids.append("validator-errors")
        next_steps.append("先修复 validate 的 ERROR findings，再把 WARN 作为后续维护项。")
    elif validator_warnings:
        fact_ids.append("validator-warnings")
        next_steps.append("处理 validate 的 WARN findings，或写明 ignore reason。")

    signals = {
        "wiki_exists": wiki_exists,
        "readme_effective_length": readme_effective_length,
        "module_index_exists": module_index_exists,
        "pom_module_count": len(pom_modules),
        "wiki_module_context_count": len(pom_modules) - len(missing_modules) if coverage_ratio is not None else None,
        "missing_module_context_count": len(missing_modules),
        "missing_module_context_modules": missing_modules,
        "module_context_coverage_ratio": coverage_ratio,
        "source_index_exists": source_index_exists,
        "validator_errors": validator_errors,
        "validator_warnings": validator_warnings,
        "graph_applicable": graph_applicable,
        "graph_file_presence": graph_file_presence,
        "fact_ids": fact_ids,
    }
    return ScoreReport(
        score_version=SCORE_VERSION,
        score=total_score,
        level=score_level(total_score),
        dimensions=dimensions,
        signals=signals,
        next_steps=next_steps[:10],
    )


def score_report_to_dict(report: ScoreReport) -> dict[str, object]:
    return {
        "score_version": report.score_version,
        "score": report.score,
        "level": report.level,
        "dimensions": [asdict(dimension) for dimension in report.dimensions],
        "signals": report.signals,
        "next_steps": report.next_steps,
    }


def format_score_report_text(report: ScoreReport, findings: list[Finding] | None = None) -> str:
    findings = findings or []
    lines = [
        "# LLM Wiki Doctor 报告",
        "",
        "## 关键结论",
        f"- 当前评分：{report.score}/100（{report.level}）",
        f"- Validator：{report.signals.get('validator_errors', 0)} 个 ERROR，{report.signals.get('validator_warnings', 0)} 个 WARN",
        "",
        "## 建议行动计划",
    ]
    if report.next_steps:
        lines.extend(f"{index}. {step}" for index, step in enumerate(report.next_steps, start=1))
    else:
        lines.append("- 暂无必须动作，保持 project-finish 时继续运行 validate。")
    lines.extend(["", "## 总体评分", f"- score_version：{report.score_version}", f"- score：{report.score}", f"- level：{report.level}", "", "## 成熟度维度"])
    for dimension in report.dimensions:
        score = "N/A" if dimension.score is None else f"{dimension.score}/{dimension.max_score}"
        lines.append(f"- {dimension.name}：{score}，{dimension.applicability}。{dimension.message}")
    lines.extend(["", "## Validator 发现"])
    if findings:
        for finding in findings:
            location = f"{finding.path}:{finding.line}" if finding.line else finding.path
            lines.append(f"- [{finding.severity}] {finding.check} {location} - {finding.message}")
    else:
        lines.append("- 无 findings。")
    return "\n".join(lines)


def normalize_argv(argv: list[str] | None) -> list[str]:
    values = list(sys.argv[1:] if argv is None else argv)
    if not values or values[0] not in {"validate", "score", "report"}:
        return ["validate", *values]
    return values


def add_validate_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--all", action="store_true", help="Scan all Markdown files")
    parser.add_argument("--changed", action="store_true", help="Scan changed Markdown files")
    parser.add_argument("--base", help="Git base ref for changed scan")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--fail-on", choices=["error", "warn"], default="error")


def run_validate_command(args: argparse.Namespace) -> int:
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


def run_score_command(args: argparse.Namespace) -> int:
    report = build_score_report(args.root)
    if args.format == "json":
        print(json.dumps(score_report_to_dict(report), ensure_ascii=False, indent=2))
    else:
        print(format_score_report_text(report))
    return 0


def run_report_command(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = collect_changed_paths(root, args.base) if args.changed or args.base else None
    findings = run_checks(root, paths)
    score_report = build_score_report(root)
    if args.format == "json":
        print(
            json.dumps(
                {
                    "findings": [asdict(finding) for finding in findings],
                    "score": score_report_to_dict(score_report),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(format_score_report_text(score_report, findings))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate repo-local .llm-wiki artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Run deterministic validators")
    add_validate_arguments(validate_parser)
    validate_parser.set_defaults(handler=run_validate_command)

    score_parser = subparsers.add_parser("score", help="Score .llm-wiki maturity")
    score_parser.add_argument("--root", default=".", help="Repository root")
    score_parser.add_argument("--format", choices=["text", "json"], default="text")
    score_parser.set_defaults(handler=run_score_command)

    report_parser = subparsers.add_parser("report", help="Generate advisory .llm-wiki report")
    report_parser.add_argument("--root", default=".", help="Repository root")
    report_parser.add_argument("--all", action="store_true", help="Scan all Markdown files")
    report_parser.add_argument("--changed", action="store_true", help="Scan changed Markdown files")
    report_parser.add_argument("--base", help="Git base ref for changed scan")
    report_parser.add_argument("--format", choices=["text", "json"], default="text")
    report_parser.set_defaults(handler=run_report_command)

    args = parser.parse_args(normalize_argv(argv))
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
