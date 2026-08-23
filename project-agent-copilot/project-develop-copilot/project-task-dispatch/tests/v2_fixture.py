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
        "policies": {"environment": "local", "singleWriterPerProject": True, "monitoring": "attached", "pin": "active-unapproved", "archive": "dispatch-close", "review": "manager-direct", "approvalAuthority": "manager"},
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
