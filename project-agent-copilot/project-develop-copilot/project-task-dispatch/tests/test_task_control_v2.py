from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import task_control
from v2_fixture import NOW, delivery, make_manifest, task


class TaskControlV2Test(unittest.TestCase):
    def assign(self, manifest: dict, task_id: str = "T-a", session_key: str = "PS-a") -> dict:
        return task_control.apply_event(
            manifest, {"event": "WORK_ASSIGNED", "taskId": task_id, "at": NOW}, {"projectSessionKey": session_key}
        )

    def submit(self, manifest: dict, task_id: str = "T-a", branch: str = "feature/a") -> dict:
        return task_control.apply_event(
            manifest, {"event": "WORKER_SUBMITTED", "taskId": task_id, "at": NOW}, {"delivery": delivery(task_id, branch)}
        )

    def test_worker_final_only_reaches_submitted(self) -> None:
        manifest = self.submit(self.assign(make_manifest()))
        self.assertEqual(manifest["workItems"][0]["state"], "SUBMITTED")
        with self.assertRaisesRegex(ValueError, "illegal work item transition"):
            task_control.apply_event(manifest, {"event": "REVIEW_APPROVED", "taskId": "T-a", "at": NOW}, {})

    def test_review_gate_approves_and_unlocks_dependency(self) -> None:
        manifest = self.submit(self.assign(make_manifest()))
        manifest = task_control.apply_event(manifest, {"event": "REVIEW_STARTED", "taskId": "T-a", "at": NOW})
        manifest["workItems"][0]["acceptanceCriteria"][0].update({"status": "PASS", "evidence": ["verified"]})
        manifest = task_control.apply_event(
            manifest, {"event": "REVIEW_APPROVED", "taskId": "T-a", "at": NOW},
            {"gitVerified": True, "testsVerified": True, "sideEffectsVerified": True, "actualHead": "2" * 40},
        )
        self.assertEqual(manifest["workItems"][0]["state"], "APPROVED")
        self.assertEqual(manifest["workItems"][1]["state"], "READY")

    def test_failed_tests_and_open_findings_block_approval(self) -> None:
        manifest = self.assign(make_manifest())
        manifest = task_control.apply_event(
            manifest, {"event": "WORKER_SUBMITTED", "taskId": "T-a", "at": NOW},
            {"delivery": delivery("T-a", "feature/a", tests="FAIL")},
        )
        manifest = task_control.apply_event(manifest, {"event": "REVIEW_STARTED", "taskId": "T-a", "at": NOW})
        manifest["workItems"][0]["acceptanceCriteria"][0]["status"] = "PASS"
        issues = task_control.approval_issues(manifest, "T-a", {"gitVerified": True, "testsVerified": True, "sideEffectsVerified": True})
        self.assertIn("required tests are not passing or waived", issues)

    def test_no_change_submission_still_requires_explicit_review_evidence(self) -> None:
        manifest = self.assign(make_manifest())
        candidate = delivery("T-a", "feature/a")
        candidate["changedFiles"] = []
        candidate["commit"] = None
        candidate["risks"] = ["NO_CHANGE_REQUIRED: current code already satisfies AC-T-a"]
        manifest = task_control.apply_event(
            manifest, {"event": "WORKER_SUBMITTED", "taskId": "T-a", "at": NOW}, {"delivery": candidate}
        )
        self.assertEqual(manifest["workItems"][0]["state"], "SUBMITTED")
        self.assertIn("Git branch", "; ".join(task_control.approval_issues(manifest, "T-a")))

    def test_finding_rework_reuses_state_and_increments_round(self) -> None:
        manifest = self.submit(self.assign(make_manifest()))
        manifest = task_control.apply_event(manifest, {"event": "REVIEW_STARTED", "taskId": "T-a", "at": NOW})
        finding = {
            "findingId": "F-a-1", "taskId": "T-a", "severity": "HIGH", "acceptanceId": "AC-T-a",
            "location": {"file": "src/T-a.txt", "line": 1}, "evidence": ["bug"], "requiredChange": "Fix it",
            "status": "OPEN", "createdAt": NOW, "resolvedAt": None,
        }
        manifest = task_control.apply_event(
            manifest, {"event": "REVIEW_CHANGES_REQUESTED", "taskId": "T-a", "at": NOW}, {"findings": [finding]}
        )
        self.assertEqual(manifest["workItems"][0]["state"], "CHANGES_REQUESTED")
        manifest["findings"][0].update({"status": "RESOLVED", "resolvedAt": NOW})
        manifest = task_control.apply_event(
            manifest, {"event": "WORKER_RESUBMITTED", "taskId": "T-a", "at": NOW}, {"delivery": delivery("T-a", "feature/a")}
        )
        self.assertEqual(manifest["workItems"][0]["state"], "SUBMITTED")
        self.assertEqual(manifest["workItems"][0]["review"]["round"], 2)

    def test_blocker_resolution_and_contract_invalidation(self) -> None:
        manifest = task_control.apply_event(
            make_manifest(), {"event": "BLOCKER_RAISED", "taskId": "T-a", "at": NOW},
            {"blocker": {"category": "TECHNICAL", "summary": "blocked", "evidence": [], "owner": "manager", "exitCondition": "fixed", "raisedAt": NOW}},
        )
        self.assertEqual(manifest["workItems"][0]["state"], "BLOCKED")
        manifest = task_control.apply_event(manifest, {"event": "BLOCKER_RESOLVED", "taskId": "T-a", "at": NOW})
        self.assertEqual(manifest["workItems"][0]["state"], "READY")
        manifest = self.assign(manifest)
        invalidated = task_control.invalidate_contract(manifest, "CR-2", "new baseline", NOW, "Contract changed")
        self.assertEqual(invalidated["workItems"][0]["state"], "STALE")


if __name__ == "__main__":
    unittest.main()
