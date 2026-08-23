from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import status_view
import task_control
from v2_fixture import make_manifest


class StatusViewTest(unittest.TestCase):
    def test_markdown_and_svg_share_revision_and_states(self) -> None:
        snapshot = task_control.build_status_snapshot(make_manifest())
        markdown = status_view.render_markdown(snapshot)
        svg = status_view.render_svg(snapshot)
        for token in ("D-test-001", "READY", "WAITING_DEPENDENCY"):
            self.assertIn(token, markdown)
            self.assertIn(token, svg)
        self.assertIn("Revision `0`", markdown)
        self.assertIn("Revision 0", svg)

    def test_generated_management_directory_contains_human_views(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            generated = status_view.render_generated_documents(temporary, make_manifest())
            root = Path(temporary)
            self.assertTrue(Path(generated["managerMarkdown"]).is_file())
            self.assertTrue((root / "views" / "status-r0000.svg").is_file())
            self.assertTrue((root / "project-sessions" / "PS-a" / "session.md").is_file())
            self.assertTrue((root / "work-items" / "T-a.md").is_file())
            self.assertTrue((root / "notes.md").is_file())

    def test_render_updates_manifest_view_to_same_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = make_manifest()
            manifest["revision"] = 7
            updated, _ = status_view.render_and_update_manifest(temporary, manifest, None, "2026-08-23T15:00:00+08:00")
            self.assertEqual(updated["view"]["revision"], 7)
            self.assertEqual(updated["view"]["sourceSvg"], "views/status-r0007.svg")

    def test_unchanged_native_timeout_is_not_meaningful(self) -> None:
        snapshot = task_control.build_status_snapshot(make_manifest())
        self.assertFalse(status_view.meaningful_change(snapshot, snapshot))
        changed = dict(snapshot)
        changed["attention"] = True
        self.assertTrue(status_view.meaningful_change(snapshot, changed))


if __name__ == "__main__":
    unittest.main()
