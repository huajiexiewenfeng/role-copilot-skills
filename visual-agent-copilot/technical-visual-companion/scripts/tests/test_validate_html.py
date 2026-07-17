from importlib import util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_html.py"

VALID_HTML = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><style>
@media (max-width: 720px) { section { display: block; } }
@media (prefers-reduced-motion: reduce) { * { animation: none; } }
@media (prefers-color-scheme: dark) { :root { color-scheme: dark; } }
</style></head><body><section><h2>系统边界</h2>
<svg role="img"><title>边界图</title><desc>服务关系</desc></svg>
</section></body></html>"""


class ValidateHtmlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = util.spec_from_file_location("technical_visual_validate_html", MODULE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load validator: {MODULE_PATH}")
        cls.validator = util.module_from_spec(spec)
        spec.loader.exec_module(cls.validator)

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def write_bytes(self, content):
        path = Path(self.temp_dir.name) / "visual.html"
        path.write_bytes(content)
        return path

    def test_valid_offline_html_passes(self):
        path = self.write_bytes(VALID_HTML.encode("utf-8"))
        report = self.validator.validate_html(path, ("系统边界",), 2_000_000)
        self.assertEqual("passed", report["overall"])
        self.assertEqual([], report["errors"])
        self.assertEqual(1, report["metrics"]["sectionCount"])
        self.assertEqual(1, report["metrics"]["svgCount"])

    def test_bom_script_iframe_and_external_resource_fail(self):
        invalid = VALID_HTML.replace(
            "</body>",
            '<script></script><iframe></iframe><img src="https://example.com/a.png"></body>',
        )
        path = self.write_bytes(b"\xef\xbb\xbf" + invalid.encode("utf-8"))
        errors = self.validator.validate_html(path, (), 2_000_000)["errors"]
        for code in (
            "utf8-bom",
            "script-forbidden",
            "iframe-forbidden",
            "external-resource-forbidden",
            "network-reference-forbidden",
        ):
            self.assertIn(code, errors)

    def test_missing_svg_accessibility_and_responsive_rules_fail(self):
        invalid = "<!doctype html><html><body><section><svg></svg></section></body></html>"
        path = self.write_bytes(invalid.encode("utf-8"))
        errors = self.validator.validate_html(path, (), 2_000_000)["errors"]
        for code in (
            "svg-accessibility-incomplete",
            "responsive-rule-missing",
            "reduced-motion-rule-missing",
            "color-scheme-rule-missing",
        ):
            self.assertIn(code, errors)

    def test_required_terms_are_enforced(self):
        path = self.write_bytes(VALID_HTML.encode("utf-8"))
        errors = self.validator.validate_html(path, ("missing-service",), 2_000_000)[
            "errors"
        ]
        self.assertIn("required-term-missing:missing-service", errors)

    def test_invalid_utf8_structure_size_and_raw_network_tokens_fail(self):
        path = self.write_bytes(b"\xff")
        errors = self.validator.validate_html(path, (), 0)["errors"]
        self.assertIn("invalid-utf8", errors)
        self.assertIn("size-limit-exceeded", errors)

        invalid = (
            "<!doctype html><!doctype html><html><html><body>"
            "fetch('/api'); XMLHttpRequest WebSocket @import url('/x.css')"
            "</body></html></html>"
        )
        path = self.write_bytes(invalid.encode("utf-8"))
        errors = self.validator.validate_html(path, (), 2_000_000)["errors"]
        for code in (
            "doctype-count",
            "html-root-count",
            "section-missing",
            "svg-missing",
            "network-reference-forbidden",
        ):
            self.assertIn(code, errors)

    def test_cli_returns_failed_json_and_exit_one(self):
        path = self.write_bytes(b"<html></html>")
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--html", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(1, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("failed", report["overall"])


if __name__ == "__main__":
    unittest.main()
