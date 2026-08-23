from __future__ import annotations

import copy
import html
import os
from pathlib import Path
from typing import Any, Mapping

try:
    from manifest_v2 import atomic_write_json
    from task_control import build_status_snapshot
except ImportError:  # pragma: no cover
    from .manifest_v2 import atomic_write_json
    from .task_control import build_status_snapshot


STATE_COLORS = {
    "READY": "#2563eb", "WAITING_DEPENDENCY": "#64748b", "ASSIGNED": "#7c3aed",
    "SUBMITTED": "#d97706", "REVIEWING": "#ea580c", "CHANGES_REQUESTED": "#dc2626",
    "APPROVED": "#16a34a", "BLOCKED": "#b91c1c", "STALE": "#475569",
}


def render_markdown(snapshot: Mapping[str, Any]) -> str:
    lines = [
        f"# PDC Dispatch {snapshot['dispatchId']}", "",
        f"Revision `{snapshot['revision']}` · Status `{snapshot['status']}`" + (" · **ATTENTION**" if snapshot["attention"] else ""),
        "", "| Work item | Repository | Project Session | PDC state | Native | Findings |",
        "|---|---|---|---|---|---:|",
    ]
    for row in snapshot["rows"]:
        title = str(row["title"]).replace("|", "\\|")
        lines.append(
            f"| `{row['taskId']}` {title} | `{row['repositoryId']}` | `{row['projectSessionKey'] or '-'}"
            f"` | `{row['pdcState']}` | `{row['nativeStatus']}` | {row['openFindings']} |"
        )
    return "\n".join(lines) + "\n"


def render_svg(snapshot: Mapping[str, Any]) -> str:
    rows = snapshot["rows"]
    width = 1180
    row_height = 74
    height = 150 + max(1, len(rows)) * row_height
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<style>text{font-family:Segoe UI,Arial,sans-serif}.title{font-size:25px;font-weight:700;fill:#0f172a}.meta{font-size:14px;fill:#475569}.label{font-size:14px;font-weight:600;fill:#0f172a}.small{font-size:12px;fill:#475569}.badge{font-size:12px;font-weight:700;fill:white}</style>',
        f'<text x="32" y="42" class="title">PDC Dispatch {html.escape(str(snapshot["dispatchId"]))}</text>',
        f'<text x="32" y="70" class="meta">Revision {snapshot["revision"]} · {html.escape(str(snapshot["status"]))}</text>',
        '<line x1="32" y1="94" x2="1148" y2="94" stroke="#cbd5e1"/>',
    ]
    if not rows:
        elements.append('<text x="32" y="134" class="meta">No work items</text>')
    for index, row in enumerate(rows):
        y = 112 + index * row_height
        color = STATE_COLORS.get(row["pdcState"], "#334155")
        elements.extend(
            [
                f'<rect x="32" y="{y}" width="1116" height="56" rx="10" fill="white" stroke="#e2e8f0"/>',
                f'<circle cx="55" cy="{y + 28}" r="9" fill="{color}"/>',
                f'<text x="78" y="{y + 23}" class="label">{html.escape(str(row["taskId"]))} · {html.escape(str(row["title"]))}</text>',
                f'<text x="78" y="{y + 43}" class="small">{html.escape(str(row["repositoryId"]))} · {html.escape(str(row["projectSessionKey"] or "unassigned"))}</text>',
                f'<rect x="800" y="{y + 15}" width="145" height="27" rx="13" fill="{color}"/>',
                f'<text x="872" y="{y + 33}" text-anchor="middle" class="badge">{html.escape(str(row["pdcState"]))}</text>',
                f'<text x="970" y="{y + 25}" class="small">native: {html.escape(str(row["nativeStatus"]))}</text>',
                f'<text x="970" y="{y + 43}" class="small">findings: {row["openFindings"]}</text>',
            ]
        )
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def render_generated_documents(root: Path | str, manifest: Mapping[str, Any], runtime_cache: Mapping[str, Any] | None = None) -> dict[str, str]:
    root = Path(root)
    snapshot = build_status_snapshot(manifest, runtime_cache)
    markdown = render_markdown(snapshot)
    svg = render_svg(snapshot)
    revision = int(manifest["revision"])
    revision_name = f"status-r{revision:04d}.svg"
    manager_path = root / "manager.md"
    revision_svg = root / "views" / revision_name
    current_svg = root / "views" / "current-status.svg"
    notes_path = root / "notes.md"
    _write_text(manager_path, markdown)
    _write_text(revision_svg, svg)
    _write_text(current_svg, svg)
    if not notes_path.exists():
        _write_text(notes_path, "# Manager Notes\n\n")

    sessions = {session["projectSessionKey"]: session for session in manifest["projectSessions"]}
    for key, session in sessions.items():
        binding = session["binding"]
        assigned = ", ".join(session["assignedWorkItemIds"]) or "none"
        content = (
            f"# Project Session {key}\n\n- Role: `{session['role']}`\n- Repository: `{session['repositoryId']}`\n"
            f"- Project: `{session['projectId']}`\n- Binding: `{binding['state']}`\n- Thread: `{binding['threadId'] or '-'}`\n"
            f"- Assigned work items: {assigned}\n"
        )
        _write_text(root / "project-sessions" / key / "session.md", content)
    findings = {finding["findingId"]: finding for finding in manifest["findings"]}
    for task in manifest["workItems"]:
        criteria = "\n".join(
            f"- [{criterion['status']}] `{criterion['acceptanceId']}` {criterion['text']}" for criterion in task["acceptanceCriteria"]
        )
        content = (
            f"# {task['taskId']} · {task['title']}\n\n- State: `{task['state']}`\n- Repository: `{task['repositoryId']}`\n"
            f"- Project Session: `{task['projectSessionKey'] or '-'}`\n- Review round: {task['review']['round']}\n\n"
            f"## Acceptance\n\n{criteria}\n"
        )
        _write_text(root / "work-items" / f"{task['taskId']}.md", content)
    for finding_id, finding in findings.items():
        content = (
            f"# Finding {finding_id}\n\n- Work item: `{finding['taskId']}`\n- Severity: `{finding['severity']}`\n"
            f"- Status: `{finding['status']}`\n\n## Required change\n\n{finding['requiredChange']}\n"
        )
        _write_text(root / "findings" / f"{finding_id}.md", content)
    return {"managerMarkdown": str(manager_path), "revisionSvg": str(revision_svg), "currentSvg": str(current_svg)}


def render_and_update_manifest(
    root: Path | str,
    manifest: Mapping[str, Any],
    runtime_cache: Mapping[str, Any] | None,
    rendered_at: str,
    *,
    png_available: bool = False,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Render one revision and return matching durable view metadata."""
    generated = render_generated_documents(root, manifest, runtime_cache)
    revision = int(manifest["revision"])
    updated = copy.deepcopy(dict(manifest))
    updated["view"] = {
        "revision": revision,
        "sourceSvg": f"views/status-r{revision:04d}.svg",
        "previewPng": f"views/status-r{revision:04d}.png" if png_available else None,
        "currentSvg": "views/current-status.svg",
        "currentPng": "views/current-status.png" if png_available else None,
        "renderedAt": rendered_at,
    }
    return updated, generated


def meaningful_change(previous_snapshot: Mapping[str, Any] | None, current_snapshot: Mapping[str, Any]) -> bool:
    if previous_snapshot is None:
        return True
    relevant = ("status", "attention", "rows")
    return any(previous_snapshot.get(key) != current_snapshot.get(key) for key in relevant)
