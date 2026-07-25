import importlib.util
import sys
import types
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "extract_resumes.py"
sys.modules.setdefault("pypdf", types.SimpleNamespace(PdfReader=object))
SPEC = importlib.util.spec_from_file_location("extract_resumes", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ResumeTextSanitizationTest(unittest.TestCase):
    def test_removes_only_forbidden_controls(self):
        cleaned, count = MODULE.remove_forbidden_controls(
            "中文\tJava\nProject\rHistory\x00\x01\x0b\x7fDone"
        )

        self.assertEqual(cleaned, "中文\tJava\nProject\rHistoryDone")
        self.assertEqual(count, 4)

    def test_clean_text_is_unchanged(self):
        text = "中文 English\nSecond line"
        self.assertEqual(MODULE.remove_forbidden_controls(text), (text, 0))


if __name__ == "__main__":
    unittest.main()
