from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SKILL_ROOT / "scripts" / "task_package.py"
SPEC = importlib.util.spec_from_file_location("task_package", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load {MODULE_PATH}")
task_package = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = task_package
SPEC.loader.exec_module(task_package)


class TaskPackageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.input_dir = self.root / "input"
        self.input_dir.mkdir()
        self.manifest_path = self.root / "manifest.json"
        self.output_dir = self.root / "output"

    def build(self, chunk_size: int = 8) -> dict:
        return task_package.build_package(
            self.input_dir,
            self.manifest_path,
            chunk_size,
        )

    def write_manifest(self, manifest: dict) -> None:
        self.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    def test_round_trips_chinese_text_without_bom_and_with_lf(self) -> None:
        source = "\ufeff# 共享基线\r\n\r\n云端与机库日志。\r\n"
        (self.input_dir / "00-shared-baseline.md").write_bytes(
            source.encode("utf-8")
        )

        manifest = self.build(chunk_size=5)
        task_package.verify_package(self.manifest_path, self.output_dir)

        rebuilt = (self.output_dir / "00-shared-baseline.md").read_bytes()
        self.assertEqual(
            rebuilt,
            "# 共享基线\n\n云端与机库日志。\n".encode("utf-8"),
        )
        self.assertFalse(rebuilt.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\r\n", rebuilt)
        manifest_bytes = self.manifest_path.read_bytes()
        self.assertFalse(manifest_bytes.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\r\n", manifest_bytes)
        self.assertEqual(manifest["encoding"], "utf-8")
        self.assertEqual(manifest["lineEndings"], "lf")

    def test_hashes_and_document_order_are_stable(self) -> None:
        (self.input_dir / "b.md").write_text(
            "第二份\r\n",
            encoding="utf-8",
            newline="",
        )
        (self.input_dir / "a.md").write_text(
            "first\n",
            encoding="utf-8",
            newline="\n",
        )

        first = self.build(chunk_size=3)
        first_bytes = self.manifest_path.read_bytes()
        second = self.build(chunk_size=3)

        self.assertEqual(first, second)
        self.assertEqual(first_bytes, self.manifest_path.read_bytes())
        self.assertEqual(
            [document["name"] for document in first["documents"]],
            ["a.md", "b.md"],
        )

        expected_bundle_input = bytearray()
        canonical = {
            "a.md": b"first\n",
            "b.md": "第二份\n".encode("utf-8"),
        }
        for document in first["documents"]:
            expected_sha = hashlib.sha256(
                canonical[document["name"]]
            ).hexdigest().upper()
            self.assertEqual(document["sha256"], expected_sha)
            self.assertEqual(
                document["byteLength"],
                len(canonical[document["name"]]),
            )
            expected_bundle_input.extend(document["name"].encode("utf-8"))
            expected_bundle_input.extend(b"\0")
            expected_bundle_input.extend(expected_sha.encode("utf-8"))
            expected_bundle_input.extend(b"\0")
            expected_bundle_input.extend(canonical[document["name"]])

        self.assertEqual(
            first["bundleSha256"],
            hashlib.sha256(expected_bundle_input).hexdigest().upper(),
        )

    def test_chunks_reassemble_exactly(self) -> None:
        text = "0123456789中文ABC\n"
        (self.input_dir / "01-project-design.md").write_text(
            text,
            encoding="utf-8",
            newline="\n",
        )

        manifest = self.build(chunk_size=4)
        document = manifest["documents"][0]
        self.assertGreater(len(document["chunks"]), 1)
        self.assertEqual(
            "".join(chunk["text"] for chunk in document["chunks"]),
            text,
        )

        task_package.verify_package(self.manifest_path, self.output_dir)
        self.assertEqual(
            (self.output_dir / "01-project-design.md").read_text(
                encoding="utf-8"
            ),
            text,
        )

    def test_rejects_non_positive_chunk_size(self) -> None:
        (self.input_dir / "a.md").write_text("a", encoding="utf-8")

        for invalid in (0, -1):
            with self.subTest(chunk_size=invalid):
                with self.assertRaisesRegex(
                    ValueError,
                    "chunk size must be positive",
                ):
                    self.build(chunk_size=invalid)

    def test_rejects_missing_duplicate_and_reordered_chunks(self) -> None:
        (self.input_dir / "a.md").write_text(
            "abcdefghij",
            encoding="utf-8",
        )
        original = self.build(chunk_size=3)

        mutations = {
            "missing": lambda chunks: chunks.pop(1),
            "duplicate": lambda chunks: chunks.insert(1, dict(chunks[0])),
            "reordered": lambda chunks: chunks.reverse(),
        }
        for name, mutate in mutations.items():
            with self.subTest(case=name):
                manifest = json.loads(json.dumps(original))
                mutate(manifest["documents"][0]["chunks"])
                self.write_manifest(manifest)
                with self.assertRaisesRegex(
                    ValueError,
                    "chunk sequence",
                ):
                    task_package.verify_package(
                        self.manifest_path,
                        self.output_dir,
                    )

    def test_rejects_path_traversal_and_absolute_document_names(self) -> None:
        (self.input_dir / "a.md").write_text("safe", encoding="utf-8")
        original = self.build()

        for unsafe in ("../escape.md", "/absolute.md", "C:/escape.md"):
            with self.subTest(name=unsafe):
                manifest = json.loads(json.dumps(original))
                manifest["documents"][0]["name"] = unsafe
                self.write_manifest(manifest)
                with self.assertRaisesRegex(
                    ValueError,
                    "unsafe document name",
                ):
                    task_package.verify_package(
                        self.manifest_path,
                        self.output_dir,
                    )

    def test_cli_builds_and_verifies_package(self) -> None:
        (self.input_dir / "00-shared-baseline.md").write_text(
            "完整方案\n",
            encoding="utf-8",
            newline="\n",
        )

        build = subprocess.run(
            [
                sys.executable,
                str(MODULE_PATH),
                "build",
                "--input",
                str(self.input_dir),
                "--output",
                str(self.manifest_path),
                "--chunk-size",
                "4",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(build.returncode, 0, build.stderr)
        self.assertTrue(self.manifest_path.is_file())

        verify = subprocess.run(
            [
                sys.executable,
                str(MODULE_PATH),
                "verify",
                "--manifest",
                str(self.manifest_path),
                "--output-dir",
                str(self.output_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(verify.returncode, 0, verify.stderr)
        self.assertEqual(
            (self.output_dir / "00-shared-baseline.md").read_text(
                encoding="utf-8"
            ),
            "完整方案\n",
        )


if __name__ == "__main__":
    unittest.main()
