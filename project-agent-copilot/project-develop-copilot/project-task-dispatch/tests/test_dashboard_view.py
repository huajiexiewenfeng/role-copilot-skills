from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import dashboard_view
import manifest_v2
from v2_fixture import make_dashboard_canary_cache, make_dashboard_canary_manifest, make_manifest


class DashboardViewTest(unittest.TestCase):
    def test_snapshot_keeps_native_and_pdc_state_separate(self) -> None:
        manifest = make_manifest()
        cache = {
            "threads": {
                "PS-a": {"nativeStatus": "active"},
                "PS-b": {"nativeStatus": "attention"},
            }
        }
        snapshot = dashboard_view.build_dashboard_snapshot(manifest, cache)
        by_key = {item["projectSessionKey"]: item for item in snapshot["sessions"]}
        self.assertEqual(by_key["PS-a"]["pdcState"], "READY")
        self.assertEqual(by_key["PS-a"]["nativeStatus"], "active")
        self.assertTrue(by_key["PS-b"]["attention"])
        self.assertEqual(snapshot["finalReview"]["label"], "等待最终复核")

    def test_html_is_one_to_n_to_one_and_escapes_worker_text(self) -> None:
        manifest = make_manifest()
        manifest["workItems"][0]["title"] = '<img src=x onerror="alert(1)">中文任务'
        snapshot = dashboard_view.build_dashboard_snapshot(manifest)
        rendered = dashboard_view.render_dashboard_html(snapshot)
        self.assertIn("Manager 最终复核", rendered)
        self.assertIn("2 Project Sessions", rendered)
        self.assertNotIn('<img src=x onerror="alert(1)">', rendered)
        self.assertIn("&lt;img", rendered)

    def test_render_writes_static_snapshot_and_local_assets_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            generated = dashboard_view.render_dashboard(temporary, make_manifest())
            for path in generated.values():
                self.assertTrue(Path(path).is_file())
            payload = json.loads(Path(generated["dashboardSnapshot"]).read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], "pdc-dashboard-2.0")
            self.assertEqual(payload["revision"], 0)
            script = Path(generated["dashboardScript"]).read_text(encoding="utf-8")
            self.assertIn("WebSocket", script)
            self.assertIn("revision-applied", script)
            self.assertIn("setInterval(refresh,3000)", script)

    def test_complex_canary_preserves_one_to_three_to_one_and_retry(self) -> None:
        manifest = make_dashboard_canary_manifest()
        manifest_v2.validate_manifest(manifest)
        snapshot = dashboard_view.build_dashboard_snapshot(manifest, make_dashboard_canary_cache())
        self.assertEqual(len(snapshot["sessions"]), 3)
        by_key = {item["projectSessionKey"]: item for item in snapshot["sessions"]}
        self.assertEqual(by_key["PS-a"]["pdcState"], "APPROVED")
        self.assertEqual(by_key["PS-b"]["pdcState"], "CHANGES_REQUESTED")
        self.assertEqual(by_key["PS-a"]["attempt"], 1)
        self.assertEqual(by_key["PS-b"]["attempt"], 1)
        self.assertEqual(by_key["PS-b"]["openFindings"], 1)
        self.assertEqual(by_key["PS-c"]["nativeStatus"], "active")
        self.assertEqual(snapshot["finalReview"]["label"], "等待最终复核")

        manifest["workItems"][1]["review"]["round"] = 2
        retried = dashboard_view.build_dashboard_snapshot(manifest, make_dashboard_canary_cache())
        retry_card = next(item for item in retried["sessions"] if item["projectSessionKey"] == "PS-b")
        self.assertEqual(retry_card["attempt"], 2)

    def test_atomic_projection_retries_transient_windows_file_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "snapshot.json"
            original_replace = dashboard_view.os.replace
            calls = 0

            def transient_lock(source: Path, target: Path) -> None:
                nonlocal calls
                calls += 1
                if calls < 3:
                    raise PermissionError("simulated reader lock")
                original_replace(source, target)

            with patch.object(dashboard_view.os, "replace", side_effect=transient_lock):
                dashboard_view._write_text(destination, '{"revision": 9}\n')
            self.assertEqual(calls, 3)
            self.assertEqual(destination.read_text(encoding="utf-8"), '{"revision": 9}\n')


if __name__ == "__main__":
    unittest.main()
