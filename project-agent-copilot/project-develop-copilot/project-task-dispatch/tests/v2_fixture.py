from __future__ import annotations

import copy


NOW = "2026-08-23T15:00:00+08:00"


def session(key: str, repository: str, project: str, branch: str, *, binding: str = "BOUND") -> dict:
    bound = binding == "BOUND"
    return {
        "projectSessionKey": key,
        "role": "worker",
        "writePolicy": "WRITE",
        "repositoryId": repository,
        "repositoryRoot": f"D:/projects/{repository}",
        "projectId": project,
        "expectedBranch": branch,
        "baselineHead": "1" * 40,
        "dirtyBoundary": {"mode": "CLEAN", "paths": [], "fingerprint": None},
        "binding": {
            "state": binding,
            "title": f"[PDC][D-test][{repository}][Worker] Test",
            "threadId": f"thread-{key}" if bound else None,
            "hostId": "local" if bound else None,
            "clientThreadId": "client-pending" if binding == "CREATE_PENDING" else None,
        },
        "assignedWorkItemIds": [],
        "createdAt": NOW,
        "updatedAt": NOW,
    }


def task(task_id: str, repository: str, session_key: str, state: str, dependencies: list[str] | None = None) -> dict:
    acceptance_id = f"AC-{task_id}"
    return {
        "taskId": task_id,
        "title": f"Implement {task_id}",
        "repositoryId": repository,
        "projectSessionKey": session_key,
        "required": True,
        "state": state,
        "dependencies": [{"taskId": item, "gate": "APPROVED"} for item in dependencies or []],
        "acceptanceCriteria": [{"acceptanceId": acceptance_id, "text": "Works", "required": True, "status": "PENDING", "evidence": []}],
        "contractRevision": "CR-1",
        "findingIds": [],
        "delivery": None,
        "review": {"policy": "manager-direct", "round": 0, "reviewerProjectSessionKey": None, "startedAt": None, "completedAt": None},
        "blocker": None,
        "staleReason": None,
        "lastTransition": {"event": "INITIALIZED", "from": None, "to": state, "at": NOW, "reason": "Initialized"},
        "createdAt": NOW,
        "updatedAt": NOW,
    }


def make_manifest() -> dict:
    return {
        "schemaVersion": "2.0",
        "dispatchId": "D-test-001",
        "revision": 0,
        "executionMode": "managed-development",
        "status": "ACTIVE",
        "realityProject": {"realityProjectId": "RP-test", "baseGraphRoot": "D:/projects/base", "baseGraphProjectId": "project-base", "repositoryIds": ["repo-a", "repo-b"]},
        "manager": {"baseGraphRoot": "D:/projects/base", "threadId": "manager-thread", "hostId": "local", "projectId": "project-base"},
        "policies": {"environment": "local", "singleWriterPerProject": True, "monitoring": "attached", "pin": "explicit-only", "archive": "explicit-only", "review": "manager-direct", "approvalAuthority": "manager"},
        "contract": {"currentRevision": "CR-1", "sharedBaseline": "Shared contract", "updatedAt": NOW},
        "projectSessions": [
            session("PS-a", "repo-a", "project-a", "feature/a"),
            session("PS-b", "repo-b", "project-b", "feature/b"),
        ],
        "workItems": [
            task("T-a", "repo-a", "PS-a", "READY"),
            task("T-b", "repo-b", "PS-b", "WAITING_DEPENDENCY", ["T-a"]),
        ],
        "findings": [],
        "view": {"revision": 0, "sourceSvg": None, "previewPng": None, "currentSvg": None, "currentPng": None, "renderedAt": None},
        "createdAt": NOW,
        "updatedAt": NOW,
    }


def delivery(task_id: str, branch: str, *, tests: str = "PASS") -> dict:
    return {
        "submittedAt": NOW,
        "summary": f"Completed {task_id}",
        "acceptanceIds": [f"AC-{task_id}"],
        "changedFiles": [f"src/{task_id}.txt"],
        "tests": [{"command": "test command", "status": tests, "summary": "passed" if tests == "PASS" else "failed"}],
        "branch": branch,
        "head": "2" * 40,
        "commit": "2" * 40,
        "risks": [],
    }


def cloned_manifest() -> dict:
    return copy.deepcopy(make_manifest())


def make_dashboard_canary_manifest() -> dict:
    manifest = make_manifest()
    manifest["dispatchId"] = "CANARY-HTML-20260823"
    manifest["revision"] = 4
    manifest["updatedAt"] = NOW
    manifest["realityProject"]["realityProjectId"] = "RP-dashboard-canary"
    manifest["realityProject"]["repositoryIds"].append("repo-c")
    manifest["projectSessions"].append(session("PS-c", "repo-c", "project-c", "feature/c"))
    manifest["workItems"].append(task("T-c", "repo-c", "PS-c", "ASSIGNED"))

    task_a, task_b, task_c = manifest["workItems"]
    task_a["title"] = "接口契约实现与单元测试"
    task_a["state"] = "APPROVED"
    task_a["delivery"] = delivery("T-a", "feature/a")
    task_a["acceptanceCriteria"][0]["status"] = "PASS"
    task_a["acceptanceCriteria"][0]["evidence"] = ["tests passed"]
    task_a["review"] = {"policy": "manager-direct", "round": 1, "reviewerProjectSessionKey": None, "startedAt": NOW, "completedAt": NOW}
    task_a["lastTransition"] = {"event": "REVIEW_APPROVED", "from": "REVIEWING", "to": "APPROVED", "at": NOW, "reason": "Manager 已核实代码、测试和提交"}
    manifest["projectSessions"][0]["assignedWorkItemIds"] = ["T-a"]

    task_b["title"] = "风险策略联调与失败重试"
    task_b["state"] = "CHANGES_REQUESTED"
    task_b["delivery"] = delivery("T-b", "feature/b", tests="FAIL")
    task_b["acceptanceCriteria"][0]["status"] = "FAIL"
    task_b["acceptanceCriteria"][0]["evidence"] = ["retry boundary case failed"]
    task_b["findingIds"] = ["F-T-b-01"]
    task_b["review"] = {"policy": "manager-direct", "round": 1, "reviewerProjectSessionKey": None, "startedAt": NOW, "completedAt": NOW}
    task_b["lastTransition"] = {"event": "REVIEW_CHANGES_REQUESTED", "from": "REVIEWING", "to": "CHANGES_REQUESTED", "at": NOW, "reason": "边界用例失败，已要求原 Session 修改"}
    manifest["projectSessions"][1]["assignedWorkItemIds"] = ["T-b"]
    manifest["findings"] = [{
        "findingId": "F-T-b-01", "taskId": "T-b", "severity": "HIGH", "acceptanceId": "AC-T-b",
        "location": {"acceptanceId": "AC-T-b"}, "evidence": ["retry boundary case failed"],
        "requiredChange": "修正重试边界并重新运行验收测试", "status": "OPEN", "createdAt": NOW, "resolvedAt": None,
    }]

    task_c["title"] = "前端状态映射与集成验证"
    task_c["lastTransition"] = {"event": "WORK_ASSIGNED", "from": "READY", "to": "ASSIGNED", "at": NOW, "reason": "Project Session 正在开发"}
    manifest["projectSessions"][2]["assignedWorkItemIds"] = ["T-c"]
    return manifest


def make_dashboard_canary_cache() -> dict:
    return {
        "schemaVersion": "2.0-cache",
        "dispatchId": "CANARY-HTML-20260823",
        "updatedAt": NOW,
        "threads": {
            "PS-a": {"nativeStatus": "final", "afterCursor": "cursor-a", "latestTurnId": "turn-a", "latestAssistantPhase": "final"},
            "PS-b": {"nativeStatus": "idle", "afterCursor": "cursor-b", "latestTurnId": "turn-b", "latestAssistantPhase": "final"},
            "PS-c": {"nativeStatus": "active", "afterCursor": "cursor-c", "latestTurnId": "turn-c", "latestAssistantPhase": "commentary"},
        },
    }
