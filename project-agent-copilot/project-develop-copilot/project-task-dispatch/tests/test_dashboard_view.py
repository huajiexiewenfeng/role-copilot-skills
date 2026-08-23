from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import dashboard_view
from v2_fixture import make_manifest


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


if __name__ == "__main__":
    unittest.main()
