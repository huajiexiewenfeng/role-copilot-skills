from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillContractTest(unittest.TestCase):
    def read(self, relative: str) -> str:
        path = ROOT / relative
        self.assertTrue(path.is_file(), f"missing {relative}")
        raw = path.read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), f"BOM in {relative}")
        return raw.decode("utf-8")

    def assert_contains(self, relative: str, tokens: list[str]) -> None:
        content = self.read(relative)
        for token in tokens:
            self.assertIn(token, content, f"{relative} missing {token!r}")

    def test_entrypoint_uses_peer_project_sessions_and_native_tools(self) -> None:
        self.assert_contains(
            "SKILL.md",
            [
                "Manager Session", "Project Worker Sessions", "Reviewer Sessions",
                "not Agent Team Subagents", "list_projects", "create_thread", "wait_threads",
                "read_thread", "send_message_to_thread", "set_thread_pinned",
                "set_thread_archived", "list_threads", "list_archived_threads",
                "target.environment.type = local", "threadId + hostId", "clientThreadId",
                "automation_update", "open_in_codex",
            ],
        )

    def test_entrypoint_enforces_review_gate_and_single_project_writer(self) -> None:
        self.assert_contains(
            "SKILL.md",
            [
                "one write Project Worker Session per saved Project per Dispatch",
                "Worker final → SUBMITTED → REVIEWING → APPROVED",
                "SUBMITTED → APPROVED` is forbidden", "original Worker `threadId`",
                "not a hard mid-turn interrupt", "does not need JSON",
            ],
        )

    def test_writable_fallback_is_forbidden(self) -> None:
        self.assert_contains(
            "references/routing.md",
            ["Writable `WRITE` Project Worker Sessions require this route", "explicitly accepts fallback", "cannot be upgraded to Development", "Do not create a Worker in the Base"],
        )

    def test_control_plane_defines_nine_states_and_authorities(self) -> None:
        self.assert_contains(
            "references/task-control-plane.md",
            ["WAITING_DEPENDENCY", "CHANGES_REQUESTED", "APPROVED", "STALE", "runtime-cache.json", "Approval Gate", "SUBMITTED→APPROVED"],
        )

    def test_runtime_defines_wait_recovery_and_lifecycle(self) -> None:
        self.assert_contains(
            "references/manager-runtime.md",
            ["1–8 targets", "afterCursor", "timeoutMs=0", "Match only by `threadId`", "Pin active-unapproved", "explicit-only", "Archive is not cancel", "hard turn-interrupt"],
        )
        self.assert_contains(
            "references/manager-runtime.md",
            ["uses the `prompt` field", "without `hostId`", "fork_thread", "handoff_thread", "share_thread", "identity remains threadId"],
        )

    def test_management_views_use_secure_external_html_and_degrade_safely(self) -> None:
        self.assert_contains(
            "SKILL.md",
            ["loopback runtime", "Windows default external browser", "Manager 1 → Project Sessions N", "WebSocket", "Markdown remains", "failure never blocks"],
        )
        self.assert_contains("references/manifest-v2.md", ["manager.md", "views/live", "server-state.json", "only human-editable", "os.replace"])
        self.assert_contains(
            "references/dashboard-runtime.md",
            ["read-only human projection", "one-time bootstrap", "HttpOnly", "revision-applied", "set_thread_archived", "raw HTML"],
        )

    def test_schema_and_all_progressive_resources_exist(self) -> None:
        resources = [
            "references/routing.md", "references/task-control-plane.md", "references/development-receipt.md",
            "references/task-package-protocol.md", "references/manager-runtime.md", "references/manifest-v2.md",
            "references/dashboard-runtime.md",
            "templates/shared-baseline.md", "templates/project-task-spec.md", "templates/handoff.md",
            "templates/worker-initial-message.md", "templates/worker-rework-message.md", "templates/reviewer-message.md",
            "scripts/manifest_v2.py", "scripts/task_control.py", "scripts/legacy_receipt.py",
            "scripts/native_thread_adapter.py", "scripts/status_view.py", "scripts/render_status_png.mjs",
            "scripts/dashboard_view.py", "scripts/dashboard_runtime.py",
            "schemas/dispatch-manifest-v2.schema.json",
        ]
        for resource in resources:
            self.read(resource)
        schema = json.loads(self.read("schemas/dispatch-manifest-v2.schema.json"))
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], "2.0")

    def test_templates_encode_project_session_batch_and_delivery(self) -> None:
        self.assert_contains("templates/shared-baseline.md", ["realityProjectId", "contractRevision", "upstreamApprovalEvidence"])
        self.assert_contains("templates/project-task-spec.md", ["projectSessionKey", "workItemIds", "acceptanceIds", "sameProjectBatchPolicy"])
        self.assert_contains("templates/handoff.md", ["writePolicy", "expectedBranch", "baselineHead", "allowNestedDelegation: false", "development-delivery-checklist"])
        self.assert_contains("templates/worker-initial-message.md", ["使用当前 Project 已配置的 PDC", "不输出 JSON progress receipt", "Final 只是提交候选"])

    def test_legacy_receipt_is_not_normal_worker_protocol(self) -> None:
        skill = self.read("SKILL.md")
        self.assertIn("New v2 Workers never receive the 1.x receipt-first", skill)
        self.assert_contains("scripts/legacy_receipt.py", ["only a delivery candidate", '"targetState": "SUBMITTED"'])

    def test_transport_and_runtime_manifests_are_distinct(self) -> None:
        self.assert_contains("references/task-package-protocol.md", ["task-package-manifest.json", "Dispatch control plane's `manifest.json`", "Do not embed the legacy receipt-first"])

    def test_v2_evals_cover_release_scenarios(self) -> None:
        payload = json.loads(self.read("evals/evals.json"))
        self.assertEqual(payload["version"], "2.0")
        ids = {case["id"] for case in payload["evals"]}
        self.assertEqual(ids, {f"E-{index:02d}" for index in range(1, 13)})
        combined = json.dumps(payload, ensure_ascii=False)
        for token in ("same-project-multiple-work-items", "manager-recovery", "in-window-status-view", "no-hard-interrupt"):
            self.assertIn(token, combined)


if __name__ == "__main__":
    unittest.main()
