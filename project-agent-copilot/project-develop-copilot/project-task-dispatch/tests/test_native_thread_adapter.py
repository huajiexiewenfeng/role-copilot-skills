from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import native_thread_adapter as adapter
from v2_fixture import make_manifest, session


class NativeThreadAdapterTest(unittest.TestCase):
    def test_create_uses_exact_project_local_title_and_omits_model_defaults(self) -> None:
        target = session("PS-new", "repo-a", "project-a", "feature/a", binding="UNBOUND")
        request = adapter.build_create_request(target, "work")
        self.assertEqual(request["target"], {"type": "project", "projectId": "project-a", "environment": {"type": "local"}})
        self.assertEqual(request["title"], target["binding"]["title"])
        self.assertNotIn("model", request)
        self.assertNotIn("thinking", request)

    def test_pending_create_is_not_waited_or_recreated(self) -> None:
        target = session("PS-new", "repo-a", "project-a", "feature/a", binding="UNBOUND")
        pending = adapter.apply_create_result(target, {"clientThreadId": "client-1"})
        self.assertEqual(pending["binding"]["state"], "CREATE_PENDING")
        self.assertEqual(adapter.build_wait_batches([pending], {}), [])
        with self.assertRaisesRegex(ValueError, "UNBOUND"):
            adapter.build_create_request(pending, "duplicate")

    def test_explicit_read_only_fallback_uses_session_project_and_target_workdir(self) -> None:
        target = session("PS-query", "repo-a", "project-base", "feature/a", binding="UNBOUND")
        target.update(
            {"writePolicy": "READ_ONLY", "routeMode": "BASE_PATH_FALLBACK", "readOnlyFallback": True, "targetWorkdir": "D:/projects/edge-agent"}
        )
        request = adapter.build_create_request(target, "Read only in D:/projects/edge-agent")
        self.assertEqual(request["target"]["projectId"], "project-base")
        self.assertEqual(target["targetWorkdir"], "D:/projects/edge-agent")

    def test_wait_batches_are_capped_at_eight_and_include_cursor(self) -> None:
        sessions = [session(f"PS-{index}", "repo-a", f"project-{index}", "feature/a") for index in range(9)]
        cache = {"PS-0": {"afterCursor": "cursor-0"}}
        batches = adapter.build_wait_batches(sessions, cache, timeout_ms=0)
        self.assertEqual([len(batch["targets"]) for batch in batches], [8, 1])
        self.assertEqual(batches[0]["targets"][0]["afterCursor"], "cursor-0")

    def test_deep_read_only_at_boundaries_and_rework_uses_original_thread(self) -> None:
        self.assertFalse(adapter.should_deep_read({"nativeStatus": "active", "latestTurnStatus": "running"}))
        self.assertTrue(adapter.should_deep_read({"nativeStatus": "idle", "latestTurnStatus": "completed"}))
        target = session("PS-a", "repo-a", "project-a", "feature/a")
        request = adapter.build_continue_request(target, "fix finding")
        self.assertEqual(request["threadId"], target["binding"]["threadId"])
        self.assertEqual(request["prompt"], "fix finding")
        self.assertNotIn("message", request)

    def test_lifecycle_does_not_pin_or_archive_by_default(self) -> None:
        manifest = make_manifest()
        manifest["projectSessions"][0]["assignedWorkItemIds"] = ["T-a"]
        self.assertEqual(adapter.lifecycle_actions(manifest), [])
        manifest["workItems"][0]["state"] = "APPROVED"
        self.assertEqual(adapter.lifecycle_actions(manifest), [])
        manifest["status"] = "CLOSED"
        self.assertEqual(adapter.lifecycle_actions(manifest), [])

    def test_lifecycle_pin_and_archive_require_explicit_requests(self) -> None:
        manifest = make_manifest()
        pin_actions = adapter.lifecycle_actions(manifest, explicit_pin_requested=True)
        self.assertTrue(all(item["operation"] == "set_thread_pinned" and item["pinned"] for item in pin_actions))

        unpin_actions = adapter.lifecycle_actions(manifest, explicit_pin_requested=False)
        self.assertTrue(all(item["operation"] == "set_thread_pinned" and not item["pinned"] for item in unpin_actions))

        self.assertEqual(adapter.lifecycle_actions(manifest, explicit_archive_requested=True), [])
        manifest["status"] = "CLOSED"
        explicit_actions = adapter.lifecycle_actions(manifest, explicit_archive_requested=True)
        self.assertTrue(any(item["operation"] == "set_thread_archived" for item in explicit_actions))

    def test_recovery_uses_thread_id_not_title_and_navigation_is_explicit(self) -> None:
        manifest = make_manifest()
        plan = adapter.recovery_plan(manifest, {"thread-PS-a"}, set())
        self.assertEqual(plan[0]["action"], "REBUILD_CACHE")
        self.assertEqual(plan[1]["action"], "MARK_MISSING")
        self.assertIsNone(adapter.user_navigation_request(manifest["projectSessions"][0], explicitly_requested=False))


if __name__ == "__main__":
    unittest.main()
