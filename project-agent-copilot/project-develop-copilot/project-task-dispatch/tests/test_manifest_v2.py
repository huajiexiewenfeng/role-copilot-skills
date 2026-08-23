from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import manifest_v2
from v2_fixture import NOW, make_manifest


class ManifestV2Test(unittest.TestCase):
    def test_accepts_valid_manifest(self) -> None:
        self.assertEqual(manifest_v2.validate_manifest(make_manifest())["schemaVersion"], "2.0")

    def test_rejects_duplicate_and_dangling_ids(self) -> None:
        duplicate = make_manifest()
        duplicate["workItems"].append(copy.deepcopy(duplicate["workItems"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate taskId"):
            manifest_v2.validate_manifest(duplicate)
        dangling = make_manifest()
        dangling["workItems"][1]["dependencies"][0]["taskId"] = "T-missing"
        with self.assertRaisesRegex(ValueError, "unknown taskId"):
            manifest_v2.validate_manifest(dangling)

    def test_rejects_dependency_cycle_and_duplicate_write_worker(self) -> None:
        cycle = make_manifest()
        cycle["workItems"][0]["dependencies"] = [{"taskId": "T-b", "gate": "APPROVED"}]
        with self.assertRaisesRegex(ValueError, "dependency cycle"):
            manifest_v2.validate_manifest(cycle)
        duplicate_writer = make_manifest()
        extra = copy.deepcopy(duplicate_writer["projectSessions"][0])
        extra["projectSessionKey"] = "PS-a-second"
        duplicate_writer["projectSessions"].append(extra)
        with self.assertRaisesRegex(ValueError, "multiple WRITE workers"):
            manifest_v2.validate_manifest(duplicate_writer)

    def test_binding_guards(self) -> None:
        missing_thread = make_manifest()
        missing_thread["projectSessions"][0]["binding"]["threadId"] = None
        with self.assertRaisesRegex(ValueError, "threadId"):
            manifest_v2.validate_manifest(missing_thread)
        pending = make_manifest()
        pending["projectSessions"][0]["binding"].update({"state": "CREATE_PENDING", "threadId": None, "hostId": None, "clientThreadId": None})
        with self.assertRaisesRegex(ValueError, "clientThreadId"):
            manifest_v2.validate_manifest(pending)

    def test_read_only_fallback_is_explicit_and_never_writable(self) -> None:
        fallback = make_manifest()
        fallback["projectSessions"][0].update(
            {"writePolicy": "READ_ONLY", "routeMode": "BASE_PATH_FALLBACK", "readOnlyFallback": True, "targetWorkdir": "D:/projects/edge-agent"}
        )
        manifest_v2.validate_manifest(fallback)
        fallback["projectSessions"][0]["writePolicy"] = "WRITE"
        with self.assertRaisesRegex(ValueError, "explicitly READ_ONLY"):
            manifest_v2.validate_manifest(fallback)

    def test_cache_can_be_rebuilt_and_updated(self) -> None:
        cache = manifest_v2.new_runtime_cache("D-test-001", NOW)
        updated = manifest_v2.update_runtime_observation(cache, "PS-a", {"nativeStatus": "idle", "afterCursor": "c1"}, NOW)
        self.assertEqual(updated["threads"]["PS-a"]["afterCursor"], "c1")
        manifest_v2.validate_runtime_cache(updated, "D-test-001")
        self.assertFalse(manifest_v2.observation_is_new(updated, "PS-a", {"nativeStatus": "idle", "afterCursor": "c1"}))
        self.assertTrue(manifest_v2.observation_is_new(updated, "PS-a", {"nativeStatus": "idle", "afterCursor": "c2"}))

    def test_atomic_write_enforces_optimistic_revision(self) -> None:
        path = Path(__file__).resolve().parent / ".tmp-manifest-v2.json"
        try:
            manifest = make_manifest()
            manifest_v2.save_manifest(path, manifest)
            with self.assertRaisesRegex(RuntimeError, "optimistic revision mismatch"):
                manifest_v2.save_manifest(path, manifest, expected_revision=9)
            self.assertFalse(path.read_bytes().startswith(b"\xef\xbb\xbf"))
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
