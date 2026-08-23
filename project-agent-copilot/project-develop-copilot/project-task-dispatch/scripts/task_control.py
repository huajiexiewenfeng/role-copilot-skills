from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any, Mapping

try:
    from manifest_v2 import load_manifest, validate_manifest
except ImportError:  # pragma: no cover
    from .manifest_v2 import load_manifest, validate_manifest


LEGAL_EVENTS = {
    "DEPENDENCIES_SATISFIED": {"WAITING_DEPENDENCY": "READY"},
    "WORK_ASSIGNED": {"READY": "ASSIGNED"},
    "WORKER_SUBMITTED": {"ASSIGNED": "SUBMITTED"},
    "REVIEW_STARTED": {"SUBMITTED": "REVIEWING"},
    "REVIEW_APPROVED": {"REVIEWING": "APPROVED"},
    "REVIEW_CHANGES_REQUESTED": {"REVIEWING": "CHANGES_REQUESTED"},
    "WORKER_RESUBMITTED": {"CHANGES_REQUESTED": "SUBMITTED"},
    "CONTRACT_INVALIDATED": {
        "ASSIGNED": "STALE", "SUBMITTED": "STALE", "REVIEWING": "STALE",
        "CHANGES_REQUESTED": "STALE", "APPROVED": "STALE",
    },
    "REQUEUE_STALE": {"STALE": None},
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _task(manifest: dict[str, Any], task_id: str) -> dict[str, Any]:
    matches = [task for task in manifest["workItems"] if task["taskId"] == task_id]
    if len(matches) != 1:
        raise ValueError(f"unknown taskId: {task_id}")
    return matches[0]


def _session(manifest: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    matches = [item for item in manifest["projectSessions"] if item["projectSessionKey"] == key]
    if len(matches) != 1:
        raise ValueError(f"unknown projectSessionKey: {key}")
    return matches[0]


def _dependencies_approved(manifest: Mapping[str, Any], task: Mapping[str, Any]) -> bool:
    states = {item["taskId"]: item["state"] for item in manifest["workItems"]}
    return all(states.get(dependency["taskId"]) == "APPROVED" for dependency in task["dependencies"])


def recompute_dependencies(manifest: Mapping[str, Any], at: str | None = None) -> dict[str, Any]:
    updated = copy.deepcopy(dict(manifest))
    changed_at = at or _now()
    for task in updated["workItems"]:
        if task["state"] not in {"READY", "WAITING_DEPENDENCY"}:
            continue
        target = "READY" if _dependencies_approved(updated, task) else "WAITING_DEPENDENCY"
        if target != task["state"]:
            previous = task["state"]
            task["state"] = target
            task["lastTransition"] = {
                "event": "DEPENDENCIES_SATISFIED" if target == "READY" else "INITIALIZED",
                "from": previous, "to": target, "at": changed_at,
                "reason": "Dependency approval state changed.",
            }
            task["updatedAt"] = changed_at
    return updated


def approval_issues(manifest: Mapping[str, Any], task_id: str, evidence: Mapping[str, Any] | None = None) -> list[str]:
    evidence = evidence or {}
    task = next((item for item in manifest["workItems"] if item["taskId"] == task_id), None)
    if task is None:
        return [f"unknown taskId: {task_id}"]
    issues: list[str] = []
    session = _session(manifest, task["projectSessionKey"])
    delivery = task.get("delivery")
    if delivery is None:
        return ["delivery is missing"]
    if delivery.get("branch") != session["expectedBranch"]:
        issues.append("delivery branch does not match expectedBranch")
    if task["contractRevision"] != manifest["contract"]["currentRevision"]:
        issues.append("contract revision is stale")
    if not _dependencies_approved(manifest, task):
        issues.append("required dependencies are not APPROVED")
    for criterion in task["acceptanceCriteria"]:
        if criterion["required"] and criterion["status"] not in {"PASS", "WAIVED"}:
            issues.append(f"acceptance {criterion['acceptanceId']} is not satisfied")
    findings = {finding["findingId"]: finding for finding in manifest["findings"]}
    if any(findings[finding_id]["status"] == "OPEN" for finding_id in task["findingIds"]):
        issues.append("open review finding remains")
    if any(test["status"] not in {"PASS", "WAIVED"} for test in delivery["tests"]):
        issues.append("required tests are not passing or waived")
    if evidence.get("gitVerified") is not True:
        issues.append("Git branch, HEAD, changed-file boundary, and commit are not independently verified")
    if evidence.get("testsVerified") is not True:
        issues.append("test evidence is not independently verified")
    if evidence.get("sideEffectsVerified") is not True:
        issues.append("cross-repository side effects are not verified")
    actual_head = evidence.get("actualHead")
    if actual_head is not None and actual_head != delivery["head"]:
        issues.append("delivery HEAD does not match Git")
    return issues


def recompute_dispatch_status(manifest: Mapping[str, Any]) -> str:
    if manifest["status"] == "CLOSED":
        return "CLOSED"
    required = [task for task in manifest["workItems"] if task["required"]]
    if required and all(task["state"] == "APPROVED" for task in required):
        return "APPROVED"
    unfinished = [task for task in required if task["state"] != "APPROVED"]
    if unfinished and all(task["state"] in {"BLOCKED", "WAITING_DEPENDENCY"} for task in unfinished) and any(
        task["state"] == "BLOCKED" for task in unfinished
    ):
        return "BLOCKED"
    return "ACTIVE" if manifest["workItems"] else "DRAFT"


def apply_event(
    manifest: Mapping[str, Any], event: Mapping[str, Any], evidence: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    validate_manifest(manifest)
    updated = copy.deepcopy(dict(manifest))
    evidence = copy.deepcopy(dict(evidence or {}))
    event_name = event.get("event")
    task_id = event.get("taskId")
    at = event.get("at") or _now()
    reason = event.get("reason") or str(event_name)
    if not isinstance(task_id, str):
        raise ValueError("event.taskId is required")
    task = _task(updated, task_id)
    previous = task["state"]

    if event_name == "BLOCKER_RAISED":
        if previous == "APPROVED":
            raise ValueError("APPROVED cannot be blocked without invalidation")
        blocker = evidence.get("blocker")
        if not isinstance(blocker, Mapping):
            raise ValueError("BLOCKER_RAISED requires blocker evidence")
        task["blocker"] = copy.deepcopy(dict(blocker))
        target = "BLOCKED"
    elif event_name == "BLOCKER_RESOLVED":
        if previous != "BLOCKED":
            raise ValueError("BLOCKER_RESOLVED requires BLOCKED")
        task["blocker"] = None
        if not _dependencies_approved(updated, task):
            target = "WAITING_DEPENDENCY"
        elif task.get("delivery") is not None:
            target = "SUBMITTED"
        elif task.get("projectSessionKey") is not None:
            session = _session(updated, task["projectSessionKey"])
            target = "ASSIGNED" if task_id in session["assignedWorkItemIds"] else "READY"
        else:
            target = "READY"
    else:
        transition = LEGAL_EVENTS.get(str(event_name), {})
        if previous not in transition:
            raise ValueError(f"illegal work item transition: {previous} --{event_name}--> ?")
        target = transition[previous]
        if event_name == "DEPENDENCIES_SATISFIED" and not _dependencies_approved(updated, task):
            raise ValueError("dependencies are not APPROVED")
        if event_name == "WORK_ASSIGNED":
            session_key = evidence.get("projectSessionKey") or task.get("projectSessionKey")
            if not isinstance(session_key, str):
                raise ValueError("WORK_ASSIGNED requires projectSessionKey")
            session = _session(updated, session_key)
            if session["binding"]["state"] != "BOUND":
                raise ValueError("WORK_ASSIGNED requires a BOUND Project Session")
            task["projectSessionKey"] = session_key
            if task_id not in session["assignedWorkItemIds"]:
                session["assignedWorkItemIds"].append(task_id)
        elif event_name in {"WORKER_SUBMITTED", "WORKER_RESUBMITTED"}:
            delivery = evidence.get("delivery")
            if not isinstance(delivery, Mapping):
                raise ValueError(f"{event_name} requires delivery evidence")
            task["delivery"] = copy.deepcopy(dict(delivery))
            task["blocker"] = None
            task["staleReason"] = None
            if event_name == "WORKER_RESUBMITTED":
                task["review"]["round"] += 1
                task["review"]["startedAt"] = None
                task["review"]["completedAt"] = None
        elif event_name == "REVIEW_STARTED":
            task["review"]["round"] = max(1, task["review"]["round"])
            task["review"]["startedAt"] = at
            task["review"]["completedAt"] = None
        elif event_name == "REVIEW_CHANGES_REQUESTED":
            new_findings = evidence.get("findings")
            if not isinstance(new_findings, list) or not new_findings:
                raise ValueError("REVIEW_CHANGES_REQUESTED requires at least one finding")
            for finding in new_findings:
                if finding.get("taskId") != task_id or finding.get("status") != "OPEN":
                    raise ValueError("review findings must be OPEN and belong to the task")
                if any(existing["findingId"] == finding["findingId"] for existing in updated["findings"]):
                    raise ValueError(f"duplicate findingId: {finding['findingId']}")
                updated["findings"].append(copy.deepcopy(finding))
                task["findingIds"].append(finding["findingId"])
            task["review"]["completedAt"] = at
        elif event_name == "REVIEW_APPROVED":
            issues = approval_issues(updated, task_id, evidence)
            if issues:
                raise ValueError("approval gate failed: " + "; ".join(issues))
            task["review"]["completedAt"] = at
        elif event_name == "CONTRACT_INVALIDATED":
            stale_reason = evidence.get("staleReason")
            if not isinstance(stale_reason, Mapping):
                raise ValueError("CONTRACT_INVALIDATED requires staleReason")
            task["staleReason"] = copy.deepcopy(dict(stale_reason))
        elif event_name == "REQUEUE_STALE":
            requested_target = evidence.get("targetState", "READY")
            if requested_target not in {"READY", "ASSIGNED"}:
                raise ValueError("REQUEUE_STALE targetState must be READY or ASSIGNED")
            if requested_target == "ASSIGNED" and task.get("projectSessionKey") is None:
                raise ValueError("cannot requeue as ASSIGNED without a Project Session")
            target = requested_target
            task["staleReason"] = None
            task["delivery"] = None

    task["state"] = target
    task["updatedAt"] = at
    task["lastTransition"] = {"event": event_name, "from": previous, "to": target, "at": at, "reason": reason}
    updated = recompute_dependencies(updated, at)
    updated["status"] = recompute_dispatch_status(updated)
    updated["revision"] += 1
    updated["updatedAt"] = at
    validate_manifest(updated)
    return updated


def invalidate_contract(
    manifest: Mapping[str, Any], new_revision: str, shared_baseline: str, at: str, reason: str
) -> dict[str, Any]:
    updated = copy.deepcopy(dict(manifest))
    previous_revision = updated["contract"]["currentRevision"]
    updated["contract"] = {"currentRevision": new_revision, "sharedBaseline": shared_baseline, "updatedAt": at}
    affected = [task["taskId"] for task in updated["workItems"] if task["state"] in LEGAL_EVENTS["CONTRACT_INVALIDATED"]]
    for task_id in affected:
        updated = apply_event(
            updated,
            {"event": "CONTRACT_INVALIDATED", "taskId": task_id, "at": at, "reason": reason},
            {"staleReason": {"category": "CONTRACT_REVISION", "expected": new_revision, "actual": previous_revision, "detectedAt": at}},
        )
    if not affected:
        updated["revision"] += 1
        updated["updatedAt"] = at
    validate_manifest(updated)
    return updated


def select_ready_batches(
    manifest: Mapping[str, Any], native_observations: Mapping[str, Mapping[str, Any]] | None = None
) -> list[dict[str, Any]]:
    validate_manifest(manifest)
    observations = native_observations or {}
    grouped: dict[str, list[str]] = {}
    for task in manifest["workItems"]:
        if task["state"] != "READY" or task["projectSessionKey"] is None:
            continue
        grouped.setdefault(task["projectSessionKey"], []).append(task["taskId"])
    batches: list[dict[str, Any]] = []
    for session_key in sorted(grouped):
        session = _session(manifest, session_key)
        binding = session["binding"]
        native_status = observations.get(session_key, {}).get("nativeStatus", "idle")
        if binding["state"] in {"CREATE_PENDING", "MISSING"} or native_status in {"active", "attention", "error"}:
            continue
        action = "CREATE_THREAD" if binding["state"] == "UNBOUND" else "SEND_MESSAGE"
        batches.append(
            {
                "projectSessionKey": session_key, "projectId": session["projectId"],
                "repositoryId": session["repositoryId"], "workItemIds": sorted(grouped[session_key]),
                "action": action, "threadId": binding["threadId"] if action == "SEND_MESSAGE" else None,
                "hostId": binding["hostId"] if action == "SEND_MESSAGE" else None,
            }
        )
    return batches


def resolve_route(
    *,
    write_policy: str,
    exact_project_id: str | None,
    explicit_read_only_fallback: bool = False,
    fallback_project_id: str | None = None,
    target_workdir: str | None = None,
) -> dict[str, Any]:
    if exact_project_id:
        return {"mode": "VERIFIED_CODEX_PROJECT", "projectId": exact_project_id, "readOnlyFallback": False}
    if write_policy == "READ_ONLY" and explicit_read_only_fallback and fallback_project_id and target_workdir:
        return {
            "mode": "BASE_PATH_FALLBACK", "projectId": fallback_project_id,
            "readOnlyFallback": True, "targetWorkdir": target_workdir,
        }
    return {
        "mode": "BLOCKED", "projectId": None, "readOnlyFallback": False,
        "reason": "Writable work requires an exact saved Codex Project; read-only fallback requires explicit acceptance, a session Project, and targetWorkdir.",
    }


def build_status_snapshot(
    manifest: Mapping[str, Any], runtime_cache: Mapping[str, Any] | None = None, git_evidence: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    cache_threads = (runtime_cache or {}).get("threads", {})
    sessions = {session["projectSessionKey"]: session for session in manifest["projectSessions"]}
    rows = []
    for task in manifest["workItems"]:
        session_key = task["projectSessionKey"]
        native = cache_threads.get(session_key, {}) if session_key else {}
        rows.append(
            {
                "taskId": task["taskId"], "title": task["title"], "repositoryId": task["repositoryId"],
                "projectSessionKey": session_key, "pdcState": task["state"],
                "nativeStatus": native.get("nativeStatus", "unobserved"),
                "bindingState": sessions[session_key]["binding"]["state"] if session_key else "UNASSIGNED",
                "openFindings": sum(1 for finding in manifest["findings"] if finding["taskId"] == task["taskId"] and finding["status"] == "OPEN"),
            }
        )
    return {
        "dispatchId": manifest["dispatchId"], "revision": manifest["revision"], "status": manifest["status"],
        "attention": any(row["nativeStatus"] == "attention" or row["openFindings"] for row in rows),
        "rows": rows, "gitEvidence": copy.deepcopy(dict(git_evidence or {})),
    }
