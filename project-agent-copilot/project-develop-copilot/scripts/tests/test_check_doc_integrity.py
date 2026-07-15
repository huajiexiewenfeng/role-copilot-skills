import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_doc_integrity.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_doc_integrity", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DocIntegrityTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checker = load_checker()
        self.write("references/acceptance-cases.md", "")
        self.write("evals/project-develop-copilot-evals.md", "")

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

    def findings(self):
        return self.checker.run_checks(self.root)

    def test_valid_file_image_anchor_query_and_fragment_pass(self):
        self.write("docs/target file.md", "# Target\n")
        self.write_bytes("docs/image.png", b"PNG")
        self.write(
            "docs/source.md",
            "[target](target%20file.md?view=1#target)\n![image](image.png)\n[anchor](#local)\n",
        )
        self.assertEqual([], self.findings())

    def test_missing_or_outside_root_local_link_fails(self):
        self.write("docs/Target.md", "# Target\n")
        self.write(
            "docs/source.md",
            "[missing](missing.md)\n[wrong case](target.md)\n[outside](../../escape.md)\n[drive](C:/temp.md)\n",
        )
        self.assertEqual(
            ["broken-local-link"] * 4,
            [finding.rule_id for finding in self.findings()],
        )

    def test_external_uri_and_links_inside_fenced_or_inline_code_are_ignored(self):
        self.write(
            "docs/source.md",
            "[web](https://example.com)\n[mail](mailto:test@example.com)\n`[inline](missing.md)`\n```text\n[fenced](missing.md)\n```\n",
        )
        self.assertEqual([], self.findings())

    def test_reference_style_usage_with_missing_local_target_fails(self):
        self.write(
            "docs/source.md",
            "[guide][phase-zero]\n\n[phase-zero]: missing.md \"Phase Zero\"\n",
        )
        self.assertEqual(
            ["broken-local-link"],
            [finding.rule_id for finding in self.findings()],
        )

    def test_balanced_parentheses_and_angle_bracket_destinations_pass(self):
        self.write("docs/plans/(draft).md", "# Draft\n")
        self.write("docs/target file.md", "# Target\n")
        self.write(
            "docs/source.md",
            "[balanced](plans/(draft).md)\n[angle](<target file.md>)\n",
        )
        self.assertEqual([], self.findings())

    def test_duplicate_case_id_fails(self):
        self.write(
            "references/acceptance-cases.md",
            "## Case 1: First\n## Case 1: Duplicate\n",
        )
        self.assertIn("duplicate-case-id", {finding.rule_id for finding in self.findings()})

    def test_duplicate_eval_id_fails(self):
        self.write(
            "evals/project-develop-copilot-evals.md",
            "## Eval 1: First\n## Eval 1: Duplicate\n",
        )
        self.assertIn("duplicate-eval-id", {finding.rule_id for finding in self.findings()})

    def test_plural_completion_rule_and_capability_missing_case_fail(self):
        self.write(
            "references/acceptance-cases.md",
            "## Case 1: Defined\n## Completion Rule\nPass Cases 1, 2, and 9A.\n",
        )
        self.write("references/capability-gap-audit.md", "Run Case 2 before release.\n")
        missing = [finding.message for finding in self.findings() if finding.rule_id == "missing-case-reference"]
        self.assertTrue(any("2" in message for message in missing))
        self.assertTrue(any("9A" in message for message in missing))

    def test_missing_eval_reference_fails(self):
        self.write("evals/project-develop-copilot-evals.md", "## Eval 1: Defined\n")
        self.write("evals/README.md", "Run Eval 2 before changing the rule.\n")
        self.assertIn("missing-eval-reference", {finding.rule_id for finding in self.findings()})

    def test_reference_parser_ignores_totals_and_dates(self):
        self.write(
            "references/acceptance-cases.md",
            "## Case 9A: Lettered A\n## Case 9B: Lettered B\n## Case 10: Fixture\n",
        )
        self.write(
            "references/summary.md",
            "Case 9A/9B/9C has 39 definitions. Acceptance Case 10 passed on 2026-06-04.\n",
        )
        missing = [
            finding.message
            for finding in self.findings()
            if "missing-case-reference" == finding.rule_id
        ]
        self.assertEqual(["Case 9C has no canonical definition"], missing)
        self.assertFalse(any(value in message for message in missing for value in ("39", "2026", "06", "04")))
        self.write(
            "references/acceptance-cases.md",
            "## Case 9A: Lettered A\n## Case 9B: Lettered B\n## Case 9C: Lettered C\n"
            "## Case 10: Fixture\n",
        )
        missing = [finding for finding in self.findings() if "missing-case-reference" == finding.rule_id]
        self.assertEqual([], missing)

    def test_invalid_utf8_and_file_read_error_are_blocking(self):
        self.write_bytes("docs/bad.md", b"line one\n\xff")
        self.write("docs/locked.md", "content")
        self.assertIn("invalid-utf8", {finding.rule_id for finding in self.findings()})
        original_read_bytes = Path.read_bytes

        def guarded_read_bytes(path):
            if path.name == "locked.md":
                raise OSError("denied")
            return original_read_bytes(path)

        with mock.patch.object(Path, "read_bytes", guarded_read_bytes):
            _, read_findings = self.checker.read_markdown_files(self.root)
        self.assertIn("file-read-error", {finding.rule_id for finding in read_findings})

    def test_non_contiguous_and_9a_9b_9c_ids_pass_with_stable_cli_output(self):
        self.write(
            "references/acceptance-cases.md",
            "## Case 9: Base\n## Completion Rule\nPass Cases 9, 9A, 9B, and 9C.\n"
            "## Case 9A: A\n## Case 9B: B\n## Case 9C: C\n",
        )
        self.write("evals/project-develop-copilot-evals.md", "## Eval 1: Defined\n## Eval 3: Gap Allowed\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = self.checker.main(["--root", str(self.root)])
        self.assertEqual(0, status)
        self.assertEqual("document integrity: no findings\n", output.getvalue())
