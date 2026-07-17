import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_text_quality.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_text_quality", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TextQualityTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checker = load_checker()

    def write(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_bytes(self, relative_path: str, content: bytes) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def test_clean_simplified_traditional_and_legal_single_characters_pass(self):
        content = "正常中文與繁體中文 " + " ".join(chr(value) for value in (0x6769, 0x7ED4, 0x7039, 0x9359))
        self.write("clean.md", content)
        self.assertEqual([], self.checker.run_checks(self.root))

    def test_invalid_utf8_and_utf8_bom_are_blocking(self):
        self.write_bytes("bad.md", b"line one\n\xff")
        self.write_bytes("bom.md", b"\xef\xbb\xbf# heading\n")
        self.write("locked.md", "content")
        original_read_bytes = Path.read_bytes

        def guarded_read_bytes(path):
            if path.name == "locked.md":
                raise OSError("denied")
            return original_read_bytes(path)

        with mock.patch.object(Path, "read_bytes", guarded_read_bytes):
            rules = {finding.rule_id for finding in self.checker.run_checks(self.root)}
        self.assertEqual({"file-read-error", "invalid-utf8", "utf8-bom"}, rules)

    def test_replacement_character_is_blocking(self):
        self.write("replacement.md", "clean\n" + chr(0xFFFD) + "\n")
        self.assertEqual("unicode-replacement-character", self.checker.run_checks(self.root)[0].rule_id)

    def test_known_multichar_mojibake_is_blocking(self):
        value = "".join(chr(codepoint) for codepoint in (0x6769, 0x6B0E, 0x91DC))
        self.write("mojibake.md", value)
        self.assertEqual("known-mojibake-sequence", self.checker.run_checks(self.root)[0].rule_id)

    def test_binary_and_generated_directories_are_ignored(self):
        self.write_bytes("image.png", b"\xff\x00")
        self.write_bytes("build/generated.md", b"\xff")
        self.assertEqual([], self.checker.run_checks(self.root))

    def test_findings_continue_across_files_and_sort_stably(self):
        self.write("z.md", chr(0xFFFD))
        self.write_bytes("a.md", b"\xef\xbb\xbftext")
        findings = self.checker.run_checks(self.root)
        self.assertEqual(["a.md", "z.md"], [finding.path for finding in findings])

    def test_cli_exit_and_output_contract(self):
        self.write("clean.md", "clean")
        clean_output = io.StringIO()
        with contextlib.redirect_stdout(clean_output):
            clean_status = self.checker.main(["--root", str(self.root)])
        self.assertEqual(0, clean_status)
        self.assertEqual("text quality: no findings\n", clean_output.getvalue())
        self.write("bad.md", chr(0xFFFD))
        bad_output = io.StringIO()
        with contextlib.redirect_stdout(bad_output):
            bad_status = self.checker.main(["--root", str(self.root)])
        self.assertEqual(1, bad_status)
        self.assertIn("bad.md:1: unicode-replacement-character:", bad_output.getvalue())
