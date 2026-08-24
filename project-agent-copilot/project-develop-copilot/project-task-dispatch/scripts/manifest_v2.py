from __future__ import annotations

import copy
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


SCHEMA_VERSION = "2.0"
CACHE_SCHEMA_VERSION = "2.0-cache"
STABLE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{1,127}$")
WORK_ITEM_STATES = frozenset(
    {
        "READY",
        "WAITING_DEPENDENCY",
        "ASSIGNED",
        "SUBMITTED",
        "REVIEWING",
        "CHANGES_REQUESTED",
        "APPROVED",
        "BLOCKED",
        "STALE",
    }
)
BOUND_WORK_STATES = frozenset(
    {"ASSIGNED", "SUBMITTED", "REVIEWING", "CHANGES_REQUESTED", "APPROVED"}
)
DELIVERY_STATES = frozenset({"SUBMITTED", "REVIEWING", "APPROVED"})


class ManifestValidationError(ValueError):
    """Raised when durable PDC state violates the v2 contract."""


def _fail(path: str, message: str) -> None:
    raise ManifestValidationError(f"{path}: {message}")


def _object(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(path, "must be an object")
    return value


def _array(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(path, "must be an array")
    return value


def _required(obj: Mapping[str, Any], names: set[str], path: str) -> None:
    missing = names - set(obj)
    if missing:
        _fail(path, "missing fields: " + ", ".join(sorted(missing)))


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(path, "must be a non-empty string")
    return value


def _stable_id(value: Any, path: str) -> str:
    value = _text(value, path)
    if not STABLE_ID.fullmatch(value):
        _fail(path, "must be a stable identifier")
    return value


def _timestamp(value: Any, path: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    value = _text(value, path)
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ManifestValidationError(f"{path}: must be an ISO-8601 timestamp") from error
    return value


def _unique_ids(records: list[Any], field: str, path: str) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(records):
        record = _object(raw, f"{path}[{index}]")
        identifier = _stable_id(record.get(field), f"{path}[{index}].{field}")
        if identifier in indexed:
            _fail(path, f"duplicate {field}: {identifier}")
        indexed[identifier] = record
    return indexed


def _validate_binding(binding: Mapping[str, Any], path: str) -> None:
    _required(binding, {"state", "title", "threadId", "hostId", "clientThreadId"}, path)
    state = binding["state"]
    if state not in {"UNBOUND", "CREATE_PENDING", "BOUND", "MISSING"}:
        _fail(f"{path}.state", "unsupported binding state")
    _text(binding["title"], f"{path}.title")
    if state == "BOUND":
        _text(binding["threadId"], f"{path}.threadId")
        _text(binding["hostId"], f"{path}.hostId")
        if binding["clientThreadId"] is not None:
            _fail(f"{path}.clientThreadId", "must be null when BOUND")
    elif state == "CREATE_PENDING":
        _text(binding["clientThreadId"], f"{path}.clientThreadId")
        if binding["threadId"] is not None or binding["hostId"] is not None:
            _fail(path, "CREATE_PENDING cannot contain threadId or hostId")
    elif state == "UNBOUND":
        if any(binding[name] is not None for name in ("threadId", "hostId", "clientThreadId")):
            _fail(path, "UNBOUND identifiers must be null")


def _validate_dependency_graph(work_items: dict[str, Mapping[str, Any]]) -> None:
    graph: dict[str, list[str]] = {}
    for task_id, task in work_items.items():
        dependencies = _array(task.get("dependencies"), f"workItems[{task_id}].dependencies")
        seen: set[str] = set()
        graph[task_id] = []
        for index, raw in enumerate(dependencies):
            dependency = _object(raw, f"workItems[{task_id}].dependencies[{index}]")
            dependency_id = _stable_id(
                dependency.get("taskId"), f"workItems[{task_id}].dependencies[{index}].taskId"
            )
            if dependency.get("gate") != "APPROVED":
                _fail(f"workItems[{task_id}].dependencies[{index}].gate", "must be APPROVED")
            if dependency_id not in work_items:
                _fail(f"workItems[{task_id}].dependencies", f"unknown taskId: {dependency_id}")
            if dependency_id == task_id:
                _fail(f"workItems[{task_id}].dependencies", "self dependency is not allowed")
            if dependency_id in seen:
                _fail(f"workItems[{task_id}].dependencies", f"duplicate taskId: {dependency_id}")
            seen.add(dependency_id)
            graph[task_id].append(dependency_id)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            _fail("workItems.dependencies", f"dependency cycle includes {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency_id in graph[task_id]:
            visit(dependency_id)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in graph:
        visit(task_id)


def _validate_delivery(task_id: str, delivery: Mapping[str, Any], acceptance_ids: set[str]) -> None:
    path = f"workItems[{task_id}].delivery"
    _required(
        delivery,
        {"submittedAt", "summary", "acceptanceIds", "changedFiles", "tests", "branch", "head", "commit", "risks"},
        path,
    )
    _timestamp(delivery["submittedAt"], f"{path}.submittedAt")
    _text(delivery["summary"], f"{path}.summary")
    delivered_acceptance = set(_array(delivery["acceptanceIds"], f"{path}.acceptanceIds"))
    unknown = delivered_acceptance - acceptance_ids
    if unknown:
        _fail(f"{path}.acceptanceIds", "unknown IDs: " + ", ".join(sorted(unknown)))
    _text(delivery["branch"], f"{path}.branch")
    _text(delivery["head"], f"{path}.head")
    for index, raw_test in enumerate(_array(delivery["tests"], f"{path}.tests")):
        test = _object(raw_test, f"{path}.tests[{index}]")
        _required(test, {"command", "status", "summary"}, f"{path}.tests[{index}]")
        _text(test["command"], f"{path}.tests[{index}].command")
        if test["status"] not in {"PASS", "FAIL", "NOT_RUN", "WAIVED"}:
            _fail(f"{path}.tests[{index}].status", "unsupported test status")


def validate_manifest(manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    manifest = _object(manifest, "manifest")
    required_root = {
        "schemaVersion", "dispatchId", "revision", "executionMode", "status", "realityProject",
        "manager", "policies", "contract", "projectSessions", "workItems", "findings", "view",
        "createdAt", "updatedAt",
    }
    _required(manifest, required_root, "manifest")
    if manifest["schemaVersion"] != SCHEMA_VERSION:
        _fail("schemaVersion", f"must be {SCHEMA_VERSION}")
    _stable_id(manifest["dispatchId"], "dispatchId")
    if type(manifest["revision"]) is not int or manifest["revision"] < 0:
        _fail("revision", "must be a non-negative integer")
    if manifest["executionMode"] not in {"dispatch", "awaited-dispatch", "managed-development"}:
        _fail("executionMode", "unsupported mode")
    if manifest["status"] not in {"DRAFT", "ACTIVE", "BLOCKED", "APPROVED", "CLOSED"}:
        _fail("status", "unsupported dispatch status")
    _timestamp(manifest["createdAt"], "createdAt")
    _timestamp(manifest["updatedAt"], "updatedAt")

    manager = _object(manifest["manager"], "manager")
    _required(manager, {"baseGraphRoot", "threadId", "hostId", "projectId"}, "manager")
    _text(manager["baseGraphRoot"], "manager.baseGraphRoot")
    for field in ("threadId", "hostId", "projectId"):
        if manager[field] is not None:
            _text(manager[field], f"manager.{field}")

    policies = _object(manifest["policies"], "policies")
    _required(
        policies,
        {"environment", "singleWriterPerProject", "monitoring", "pin", "archive", "review", "approvalAuthority"},
        "policies",
    )
    expected_policy_values = {
        "environment": {"local"},
        "singleWriterPerProject": {True},
        "monitoring": {"attached", "heartbeat"},
        "pin": {"explicit-only", "active-unapproved"},
        "archive": {"explicit-only", "canary-dispatch-close"},
        "review": {"manager-direct", "risk-based-independent", "always-independent"},
        "approvalAuthority": {"manager", "user", "mixed"},
    }
    for field, allowed in expected_policy_values.items():
        if policies[field] not in allowed:
            _fail(f"policies.{field}", "unsupported policy value")

    reality = _object(manifest["realityProject"], "realityProject")
    _required(reality, {"realityProjectId", "baseGraphRoot", "repositoryIds"}, "realityProject")
    _stable_id(reality["realityProjectId"], "realityProject.realityProjectId")
    _text(reality["baseGraphRoot"], "realityProject.baseGraphRoot")
    repository_ids = set(_array(reality["repositoryIds"], "realityProject.repositoryIds"))
    if not repository_ids or len(repository_ids) != len(reality["repositoryIds"]):
        _fail("realityProject.repositoryIds", "must contain unique repository IDs")
    for repository_id in repository_ids:
        _stable_id(repository_id, "realityProject.repositoryIds[]")

    contract = _object(manifest["contract"], "contract")
    _required(contract, {"currentRevision", "sharedBaseline", "updatedAt"}, "contract")
    _stable_id(contract["currentRevision"], "contract.currentRevision")
    _text(contract["sharedBaseline"], "contract.sharedBaseline")
    _timestamp(contract["updatedAt"], "contract.updatedAt")

    sessions = _unique_ids(_array(manifest["projectSessions"], "projectSessions"), "projectSessionKey", "projectSessions")
    write_workers: set[str] = set()
    for key, session in sessions.items():
        path = f"projectSessions[{key}]"
        _required(
            session,
            {"projectSessionKey", "role", "writePolicy", "repositoryId", "repositoryRoot", "projectId",
             "expectedBranch", "baselineHead", "dirtyBoundary", "binding", "assignedWorkItemIds",
             "createdAt", "updatedAt"},
            path,
        )
        if session["role"] not in {"worker", "reviewer"}:
            _fail(f"{path}.role", "must be worker or reviewer")
        if session["writePolicy"] not in {"WRITE", "READ_ONLY"}:
            _fail(f"{path}.writePolicy", "must be WRITE or READ_ONLY")
        route_mode = session.get("routeMode", "VERIFIED_CODEX_PROJECT")
        if route_mode not in {"VERIFIED_CODEX_PROJECT", "BASE_PATH_FALLBACK"}:
            _fail(f"{path}.routeMode", "unsupported route mode")
        if route_mode == "BASE_PATH_FALLBACK":
            if session["writePolicy"] != "READ_ONLY" or session.get("readOnlyFallback") is not True:
                _fail(path, "BASE_PATH_FALLBACK must be explicitly READ_ONLY")
            _text(session.get("targetWorkdir"), f"{path}.targetWorkdir")
        elif session.get("readOnlyFallback") is True:
            _fail(path, "readOnlyFallback=true requires BASE_PATH_FALLBACK")
        if session["repositoryId"] not in repository_ids:
            _fail(f"{path}.repositoryId", "not registered in realityProject.repositoryIds")
        _text(session["repositoryRoot"], f"{path}.repositoryRoot")
        project_id = _text(session["projectId"], f"{path}.projectId")
        _text(session["expectedBranch"], f"{path}.expectedBranch")
        _text(session["baselineHead"], f"{path}.baselineHead")
        dirty = _object(session["dirtyBoundary"], f"{path}.dirtyBoundary")
        _required(dirty, {"mode", "paths", "fingerprint"}, f"{path}.dirtyBoundary")
        if dirty["mode"] not in {"CLEAN", "PRESERVE"}:
            _fail(f"{path}.dirtyBoundary.mode", "must be CLEAN or PRESERVE")
        dirty_paths = _array(dirty["paths"], f"{path}.dirtyBoundary.paths")
        if len(dirty_paths) != len(set(dirty_paths)):
            _fail(f"{path}.dirtyBoundary.paths", "must be unique")
        if dirty["mode"] == "CLEAN" and dirty_paths:
            _fail(f"{path}.dirtyBoundary", "CLEAN cannot contain paths")
        _validate_binding(_object(session["binding"], f"{path}.binding"), f"{path}.binding")
        assigned = _array(session["assignedWorkItemIds"], f"{path}.assignedWorkItemIds")
        if len(assigned) != len(set(assigned)):
            _fail(f"{path}.assignedWorkItemIds", "must be unique")
        if session["role"] == "worker" and session["writePolicy"] == "WRITE":
            if project_id in write_workers:
                _fail("projectSessions", f"multiple WRITE workers for projectId {project_id}")
            write_workers.add(project_id)

    work_items = _unique_ids(_array(manifest["workItems"], "workItems"), "taskId", "workItems")
    all_acceptance_ids: set[str] = set()
    for task_id, task in work_items.items():
        path = f"workItems[{task_id}]"
        _required(
            task,
            {"taskId", "title", "repositoryId", "projectSessionKey", "required", "state", "dependencies",
             "acceptanceCriteria", "contractRevision", "findingIds", "delivery", "review", "blocker",
             "staleReason", "lastTransition", "createdAt", "updatedAt"},
            path,
        )
        _text(task["title"], f"{path}.title")
        if task["repositoryId"] not in repository_ids:
            _fail(f"{path}.repositoryId", "not registered in realityProject.repositoryIds")
        session_key = task["projectSessionKey"]
        if session_key is not None and session_key not in sessions:
            _fail(f"{path}.projectSessionKey", f"unknown Project Session: {session_key}")
        state = task["state"]
        if state not in WORK_ITEM_STATES:
            _fail(f"{path}.state", "unsupported work item state")
        if state in BOUND_WORK_STATES and session_key is None:
            _fail(f"{path}.projectSessionKey", f"is required for state {state}")
        acceptance = _array(task["acceptanceCriteria"], f"{path}.acceptanceCriteria")
        if not acceptance:
            _fail(f"{path}.acceptanceCriteria", "must not be empty")
        acceptance_ids: set[str] = set()
        for index, raw in enumerate(acceptance):
            criterion = _object(raw, f"{path}.acceptanceCriteria[{index}]")
            acceptance_id = _stable_id(criterion.get("acceptanceId"), f"{path}.acceptanceCriteria[{index}].acceptanceId")
            if acceptance_id in all_acceptance_ids:
                _fail("workItems.acceptanceCriteria", f"duplicate acceptanceId: {acceptance_id}")
            all_acceptance_ids.add(acceptance_id)
            acceptance_ids.add(acceptance_id)
            if criterion.get("status") not in {"PENDING", "PASS", "FAIL", "WAIVED"}:
                _fail(f"{path}.acceptanceCriteria[{index}].status", "unsupported status")
            if type(criterion.get("required")) is not bool:
                _fail(f"{path}.acceptanceCriteria[{index}].required", "must be a boolean")
            _text(criterion.get("text"), f"{path}.acceptanceCriteria[{index}].text")
            _array(criterion.get("evidence"), f"{path}.acceptanceCriteria[{index}].evidence")
        if state in DELIVERY_STATES and task["delivery"] is None:
            _fail(f"{path}.delivery", f"is required for state {state}")
        if task["delivery"] is not None:
            _validate_delivery(task_id, _object(task["delivery"], f"{path}.delivery"), acceptance_ids)
        if state == "BLOCKED" and task["blocker"] is None:
            _fail(f"{path}.blocker", "is required for BLOCKED")
        if state == "STALE" and task["staleReason"] is None:
            _fail(f"{path}.staleReason", "is required for STALE")
        if task["blocker"] is not None:
            blocker = _object(task["blocker"], f"{path}.blocker")
            _required(blocker, {"category", "summary", "evidence", "owner", "exitCondition", "raisedAt"}, f"{path}.blocker")
            if blocker["category"] not in {"DEPENDENCY", "PROJECT_ROUTE", "GIT_STATE", "PERMISSION", "TECHNICAL", "USER_DECISION", "OTHER"}:
                _fail(f"{path}.blocker.category", "unsupported category")
            for field in ("summary", "owner", "exitCondition"):
                _text(blocker[field], f"{path}.blocker.{field}")
            _array(blocker["evidence"], f"{path}.blocker.evidence")
            _timestamp(blocker["raisedAt"], f"{path}.blocker.raisedAt")
        if task["staleReason"] is not None:
            stale = _object(task["staleReason"], f"{path}.staleReason")
            _required(stale, {"category", "expected", "actual", "detectedAt"}, f"{path}.staleReason")
            if stale["category"] not in {"CONTRACT_REVISION", "BASELINE_HEAD", "UPSTREAM_APPROVAL", "BRANCH", "OTHER"}:
                _fail(f"{path}.staleReason.category", "unsupported category")
            _timestamp(stale["detectedAt"], f"{path}.staleReason.detectedAt")
        transition = _object(task["lastTransition"], f"{path}.lastTransition")
        _required(transition, {"event", "from", "to", "at", "reason"}, f"{path}.lastTransition")
        if transition["to"] not in WORK_ITEM_STATES:
            _fail(f"{path}.lastTransition.to", "unsupported state")
        if transition["from"] is not None and transition["from"] not in WORK_ITEM_STATES:
            _fail(f"{path}.lastTransition.from", "unsupported state")
        _timestamp(transition["at"], f"{path}.lastTransition.at")
        _text(transition["reason"], f"{path}.lastTransition.reason")
        review = _object(task["review"], f"{path}.review")
        _required(review, {"policy", "round", "reviewerProjectSessionKey", "startedAt", "completedAt"}, f"{path}.review")
        if review["policy"] not in {"manager-direct", "independent"}:
            _fail(f"{path}.review.policy", "unsupported review policy")
        if type(review["round"]) is not int or review["round"] < 0:
            _fail(f"{path}.review.round", "must be a non-negative integer")
        _timestamp(review["startedAt"], f"{path}.review.startedAt", nullable=True)
        _timestamp(review["completedAt"], f"{path}.review.completedAt", nullable=True)
        reviewer_key = review.get("reviewerProjectSessionKey")
        if reviewer_key is not None:
            if reviewer_key not in sessions or sessions[reviewer_key]["role"] != "reviewer":
                _fail(f"{path}.review.reviewerProjectSessionKey", "must reference a reviewer Session")
        if state == "APPROVED":
            failed = [c["acceptanceId"] for c in acceptance if c.get("required") and c.get("status") not in {"PASS", "WAIVED"}]
            if failed:
                _fail(path, "APPROVED with unsatisfied acceptance: " + ", ".join(failed))

    _validate_dependency_graph(work_items)

    findings = _unique_ids(_array(manifest["findings"], "findings"), "findingId", "findings")
    for finding_id, finding in findings.items():
        finding_path = f"findings[{finding_id}]"
        _required(
            finding,
            {"findingId", "taskId", "severity", "acceptanceId", "location", "evidence", "requiredChange", "status", "createdAt", "resolvedAt"},
            finding_path,
        )
        if finding["severity"] not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
            _fail(f"{finding_path}.severity", "unsupported severity")
        if finding["status"] not in {"OPEN", "RESOLVED", "WAIVED"}:
            _fail(f"{finding_path}.status", "unsupported status")
        if not _array(finding["evidence"], f"{finding_path}.evidence"):
            _fail(f"{finding_path}.evidence", "must not be empty")
        _text(finding["requiredChange"], f"{finding_path}.requiredChange")
        _timestamp(finding["createdAt"], f"{finding_path}.createdAt")
        _timestamp(finding["resolvedAt"], f"{finding_path}.resolvedAt", nullable=True)
        task_id = finding.get("taskId")
        if task_id not in work_items:
            _fail(f"findings[{finding_id}].taskId", f"unknown taskId: {task_id}")
        if finding_id not in work_items[task_id].get("findingIds", []):
            _fail(f"findings[{finding_id}]", "missing reverse reference from work item")
        acceptance_id = finding.get("acceptanceId")
        if acceptance_id is not None:
            task_acceptance = {c["acceptanceId"] for c in work_items[task_id]["acceptanceCriteria"]}
            if acceptance_id not in task_acceptance:
                _fail(f"findings[{finding_id}].acceptanceId", "does not belong to the same task")
    for task_id, task in work_items.items():
        for finding_id in task["findingIds"]:
            if finding_id not in findings or findings[finding_id].get("taskId") != task_id:
                _fail(f"workItems[{task_id}].findingIds", f"invalid finding reference: {finding_id}")
        assigned_by = [key for key, session in sessions.items() if task_id in session["assignedWorkItemIds"]]
        if task["projectSessionKey"] is not None and task["state"] in BOUND_WORK_STATES:
            if assigned_by != [task["projectSessionKey"]]:
                _fail(f"workItems[{task_id}]", "assignedWorkItemIds reverse reference is inconsistent")
        if task["state"] == "APPROVED":
            open_findings = [finding_id for finding_id in task["findingIds"] if findings[finding_id].get("status") == "OPEN"]
            if open_findings:
                _fail(f"workItems[{task_id}]", "APPROVED with open findings")

    view = _object(manifest["view"], "view")
    if type(view.get("revision")) is not int or view["revision"] > manifest["revision"]:
        _fail("view.revision", "must be an integer not greater than manifest revision")
    source_svg = view.get("sourceSvg")
    if source_svg is not None:
        expected = f"status-r{view['revision']:04d}.svg"
        if Path(source_svg).name != expected:
            _fail("view.sourceSvg", f"must end with {expected}")
    preview_png = view.get("previewPng")
    if preview_png is not None:
        expected = f"status-r{view['revision']:04d}.png"
        if Path(preview_png).name != expected:
            _fail("view.previewPng", f"must end with {expected}")
    return manifest


def load_manifest(path: Path | str) -> dict[str, Any]:
    raw = Path(path).read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        _fail("manifest", "must be UTF-8 without BOM")
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ManifestValidationError("manifest: invalid UTF-8 JSON") from error
    validate_manifest(manifest)
    return manifest


def atomic_write_json(path: Path | str, value: Mapping[str, Any], *, expected_revision: int | None = None) -> None:
    destination = Path(path)
    if expected_revision is not None and destination.exists():
        current = load_manifest(destination)
        if current["revision"] != expected_revision:
            raise RuntimeError(
                f"optimistic revision mismatch: expected {expected_revision}, found {current['revision']}"
            )
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, destination)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def save_manifest(path: Path | str, manifest: Mapping[str, Any], *, expected_revision: int | None = None) -> None:
    validate_manifest(manifest)
    atomic_write_json(path, manifest, expected_revision=expected_revision)


def new_runtime_cache(dispatch_id: str, updated_at: str) -> dict[str, Any]:
    _stable_id(dispatch_id, "dispatchId")
    _timestamp(updated_at, "updatedAt")
    return {"schemaVersion": CACHE_SCHEMA_VERSION, "dispatchId": dispatch_id, "updatedAt": updated_at, "threads": {}}


def validate_runtime_cache(cache: Mapping[str, Any], dispatch_id: str | None = None) -> Mapping[str, Any]:
    cache = _object(cache, "runtime-cache")
    _required(cache, {"schemaVersion", "dispatchId", "updatedAt", "threads"}, "runtime-cache")
    if cache["schemaVersion"] != CACHE_SCHEMA_VERSION:
        _fail("runtime-cache.schemaVersion", f"must be {CACHE_SCHEMA_VERSION}")
    if dispatch_id is not None and cache["dispatchId"] != dispatch_id:
        _fail("runtime-cache.dispatchId", "does not match manifest")
    _timestamp(cache["updatedAt"], "runtime-cache.updatedAt")
    _object(cache["threads"], "runtime-cache.threads")
    return cache


def update_runtime_observation(
    cache: Mapping[str, Any], project_session_key: str, observation: Mapping[str, Any], updated_at: str
) -> dict[str, Any]:
    updated = copy.deepcopy(dict(cache))
    validate_runtime_cache(updated)
    _stable_id(project_session_key, "projectSessionKey")
    _timestamp(updated_at, "updatedAt")
    updated["threads"][project_session_key] = copy.deepcopy(dict(observation))
    updated["updatedAt"] = updated_at
    return updated


def observation_is_new(cache: Mapping[str, Any], project_session_key: str, observation: Mapping[str, Any]) -> bool:
    """Reject a replayed wait cursor/final before invoking the reducer."""
    previous = cache.get("threads", {}).get(project_session_key)
    if previous is None:
        return True
    cursor = observation.get("afterCursor")
    if cursor is not None and cursor == previous.get("afterCursor"):
        return False
    turn_id = observation.get("latestTurnId")
    phase = observation.get("latestAssistantPhase")
    if turn_id is not None and turn_id == previous.get("latestTurnId") and phase == previous.get("latestAssistantPhase"):
        return False
    return observation != previous
