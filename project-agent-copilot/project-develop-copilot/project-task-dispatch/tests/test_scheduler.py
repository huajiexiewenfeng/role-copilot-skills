from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import task_control
from v2_fixture import make_manifest, task


class SchedulerTest(unittest.TestCase):
    def test_same_project_ready_items_are_one_batch(self) -> None:
        manifest = make_manifest()
        manifest["workItems"].append(task("T-a-2", "repo-a", "PS-a", "READY"))
        batches = task_control.select_ready_batches(manifest)
        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0]["workItemIds"], ["T-a", "T-a-2"])

    def test_active_session_does_not_receive_second_batch(self) -> None:
        manifest = make_manifest()
        self.assertEqual(task_control.select_ready_batches(manifest, {"PS-a": {"nativeStatus": "active"}}), [])

    def test_independent_projects_are_selected_in_parallel(self) -> None:
        manifest = make_manifest()
        manifest["workItems"][1]["dependencies"] = []
        manifest["workItems"][1]["state"] = "READY"
        self.assertEqual(len(task_control.select_ready_batches(manifest)), 2)

    def test_unbound_and_bound_sessions_choose_create_or_send(self) -> None:
        manifest = make_manifest()
        self.assertEqual(task_control.select_ready_batches(manifest)[0]["action"], "SEND_MESSAGE")
        manifest["projectSessions"][0]["binding"].update(
            {"state": "UNBOUND", "threadId": None, "hostId": None, "clientThreadId": None}
        )
        self.assertEqual(task_control.select_ready_batches(manifest)[0]["action"], "CREATE_THREAD")

    def test_writable_fallback_is_blocked_but_explicit_read_only_is_allowed(self) -> None:
        blocked = task_control.resolve_route(write_policy="WRITE", exact_project_id=None)
        self.assertEqual(blocked["mode"], "BLOCKED")
        fallback = task_control.resolve_route(
            write_policy="READ_ONLY", exact_project_id=None, explicit_read_only_fallback=True,
            fallback_project_id="project-base", target_workdir="D:/projects/edge-agent",
        )
        self.assertEqual(
            fallback,
            {"mode": "BASE_PATH_FALLBACK", "projectId": "project-base", "readOnlyFallback": True, "targetWorkdir": "D:/projects/edge-agent"},
        )


if __name__ == "__main__":
    unittest.main()
