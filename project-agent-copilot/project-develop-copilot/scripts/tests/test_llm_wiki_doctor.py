import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


MODULE_PATH = Path(__file__).resolve().parents[1] / "llm_wiki_doctor.py"


def load_doctor():
    spec = importlib.util.spec_from_file_location("llm_wiki_doctor", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_doctor_cli(root: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(MODULE_PATH), *args, "--root", str(root)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class DoctorFixture:
    def __init__(self, root: Path):
        self.root = root

    def write(self, relative_path: str, content: str):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def seed_registry(self):
        self.write(
            ".llm-wiki/project-ids.json",
            json.dumps(
                {
                    "local_projects": ["smart-go-device-mapping", "smart-go-file"],
                    "projects": [
                        {"id": "smart-go-device-mapping", "aliases": []},
                        {"id": "smart-go-file", "aliases": []},
                        {"id": "smarthub-mediakit", "aliases": ["smarthub-mediakit-server"]},
                        {"id": "drone-cloud-api", "aliases": []},
                        {"id": "smarthub", "aliases": []},
                    ],
                },
                indent=2,
            ),
        )
        self.write(
            ".llm-wiki/project-graph/edges.md",
            "\n".join(
                [
                    "# Project Graph Edges",
                    "",
                    "| edge_id | from_project | to_project |",
                    "|---|---|---|",
                    "| edge-20260623-001 | smart-go-device-mapping | smarthub-mediakit |",
                ]
            ),
        )

    def findings(self):
        doctor = load_doctor()
        return doctor.run_checks(self.root, paths=None)

    def finding_keys(self):
        return {(finding.check, finding.path) for finding in self.findings()}

    def finding_checks(self):
        return {finding.check for finding in self.findings()}


class LlmWikiDoctorTest(unittest.TestCase):
    def with_fixture(self):
        temp = TemporaryDirectory()
        root = Path(temp.name)
        fixture = DoctorFixture(root)
        fixture.seed_registry()
        self.addCleanup(temp.cleanup)
        return fixture

    def test_reports_orphan_design_doc_under_docs_plans(self):
        fixture = self.with_fixture()
        fixture.write("docs/plans/foo.md", "# Foo design\n")

        findings = fixture.findings()

        self.assertIn(
            ("orphan-design-doc", "docs/plans/foo.md"),
            {(finding.check, finding.path) for finding in findings},
        )

    def test_ignore_comment_suppresses_orphan_design_doc(self):
        fixture = self.with_fixture()
        fixture.write(
            "docs/plans/foo.md",
            '<!-- llm-wiki-ignore: orphan-design-doc reason="historical archive" -->\n# Foo design\n',
        )

        self.assertNotIn(("orphan-design-doc", "docs/plans/foo.md"), fixture.finding_keys())

    def test_exact_ingest_source_path_registers_doc(self):
        fixture = self.with_fixture()
        fixture.write("docs/plans/foo.md", "# Foo design\n")
        fixture.write(
            ".llm-wiki/ingest/index.md",
            "\n".join(
                [
                    "# Ingest Index",
                    "",
                    "| Source id | Source | Type | Proxy | Status | Note |",
                    "|---|---|---|---|---|---|",
                    "| `20260623-001-001` | `docs/plans/foo.md` | design | `.llm-wiki/sources/proxies/20260623-001/001-foo.md` | summarized | ok |",
                ]
            ),
        )

        self.assertNotIn(("orphan-design-doc", "docs/plans/foo.md"), fixture.finding_keys())

    def test_filename_only_does_not_register_doc(self):
        fixture = self.with_fixture()
        fixture.write("docs/plans/foo.md", "# Foo design\n")
        fixture.write(
            ".llm-wiki/ingest/index.md",
            "| Source id | Source | Type | Proxy | Status | Note |\n|---|---|---|---|---|---|\n| `x` | `other/foo.md` | design | `p` | summarized | same filename |\n",
        )

        self.assertIn(("orphan-design-doc", "docs/plans/foo.md"), fixture.finding_keys())

    def test_original_path_metadata_registers_doc(self):
        fixture = self.with_fixture()
        fixture.write("docs/plans/foo.md", "# Foo design\n")
        fixture.write(
            ".llm-wiki/sources/proxies/20260623-001/001-foo.md",
            "# Source Proxy\n\n- original_path: `docs/plans/foo.md`\n",
        )

        self.assertNotIn(("orphan-design-doc", "docs/plans/foo.md"), fixture.finding_keys())

    def test_missing_graph_evidence_warns_for_known_project_without_edge(self):
        fixture = self.with_fixture()
        fixture.write(
            ".llm-wiki/requirements/foo.md",
            "# Requirement\n\nsmart-go-device-mapping will notify smarthub over MQTT.\n",
        )

        self.assertIn(("missing-graph-evidence", ".llm-wiki/requirements/foo.md"), fixture.finding_keys())

    def test_project_graph_gaps_satisfies_missing_graph_evidence(self):
        fixture = self.with_fixture()
        fixture.write(
            ".llm-wiki/requirements/foo.md",
            "# Requirement\n\nsmart-go-device-mapping will notify smarthub.\n\n## Project Graph Gaps\n\n- No confirmed edge yet.\n",
        )

        self.assertNotIn(("missing-graph-evidence", ".llm-wiki/requirements/foo.md"), fixture.finding_keys())

    def test_valid_project_graph_evidence_satisfies_missing_graph_evidence(self):
        fixture = self.with_fixture()
        fixture.write(
            ".llm-wiki/requirements/foo.md",
            "# Requirement\n\nsmart-go-device-mapping calls smarthub-mediakit.\n\n## Project Graph Evidence\n\n| Edge | Relation |\n|---|---|\n| `edge-20260623-001` | ok |\n",
        )

        keys = fixture.finding_keys()
        self.assertNotIn(("missing-graph-evidence", ".llm-wiki/requirements/foo.md"), keys)
        self.assertNotIn(("invalid-edge-id", ".llm-wiki/requirements/foo.md"), keys)

    def test_invalid_project_graph_evidence_is_error(self):
        fixture = self.with_fixture()
        fixture.write(
            ".llm-wiki/requirements/foo.md",
            "# Requirement\n\nsmart-go-device-mapping calls smarthub-mediakit.\n\n## Project Graph Evidence\n\n| Edge | Relation |\n|---|---|\n| `edge-20990101-999` | missing |\n",
        )

        findings = fixture.findings()
        self.assertIn(("invalid-edge-id", ".llm-wiki/requirements/foo.md"), fixture.finding_keys())
        self.assertEqual("ERROR", next(finding.severity for finding in findings if finding.check == "invalid-edge-id"))

    def test_validate_subcommand_warn_only_exits_zero(self):
        fixture = self.with_fixture()
        fixture.write("docs/plans/foo.md", "# Foo design\n")

        result = run_doctor_cli(fixture.root, "validate", "--all", "--format", "json", "--fail-on", "error")

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(["orphan-design-doc"], [item["check"] for item in payload])

    def test_legacy_validate_arguments_still_work(self):
        fixture = self.with_fixture()
        fixture.write("docs/plans/foo.md", "# Foo design\n")

        result = run_doctor_cli(fixture.root, "--all", "--format", "json", "--fail-on", "error")

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(["orphan-design-doc"], [item["check"] for item in payload])

    def test_dangling_cross_ref_is_error(self):
        fixture = self.with_fixture()
        fixture.write(
            ".llm-wiki/cross-refs/index.md",
            "| Topic | Project | Edge |\n|---|---|---|\n| Stream | smarthub | `edge-20990101-999` |\n",
        )

        findings = fixture.findings()

        self.assertIn(("dangling-cross-ref", ".llm-wiki/cross-refs/index.md"), fixture.finding_keys())
        self.assertEqual("ERROR", next(finding.severity for finding in findings if finding.check == "dangling-cross-ref"))

    def test_duplicate_edge_fingerprint_is_error(self):
        fixture = self.with_fixture()
        fixture.write(
            ".llm-wiki/project-graph/edges.md",
            "\n".join(
                [
                    "# Project Graph Edges",
                    "",
                    "| edge_id | from_project | to_project | fingerprint |",
                    "|---|---|---|---|",
                    "| edge-20260623-001 | smart-go-device-mapping | smarthub-mediakit | same |",
                    "| edge-20260623-002 | smart-go-device-mapping | smarthub | same |",
                ]
            ),
        )

        findings = fixture.findings()

        self.assertIn(("duplicate-edge-fingerprint", ".llm-wiki/project-graph/edges.md"), fixture.finding_keys())
        self.assertEqual("ERROR", next(finding.severity for finding in findings if finding.check == "duplicate-edge-fingerprint"))

    def test_leaked_local_path_is_error(self):
        fixture = self.with_fixture()
        fixture.write(".llm-wiki/requirements/foo.md", "# Requirement\n\nSee C:\\Users\\admin\\secret\\note.md\n")

        findings = fixture.findings()

        self.assertIn(("leaked-local-path", ".llm-wiki/requirements/foo.md"), fixture.finding_keys())
        self.assertEqual("ERROR", next(finding.severity for finding in findings if finding.check == "leaked-local-path"))

    def test_validate_fail_on_error_returns_one_for_blocking_findings(self):
        fixture = self.with_fixture()
        fixture.write(".llm-wiki/requirements/foo.md", "# Requirement\n\nSee C:\\Users\\admin\\secret\\note.md\n")

        result = run_doctor_cli(fixture.root, "validate", "--all", "--format", "json", "--fail-on", "error")

        self.assertEqual(1, result.returncode)
        self.assertIn("leaked-local-path", result.stdout)

    def test_unresolved_project_id_warns_only_for_structured_fields(self):
        fixture = self.with_fixture()
        fixture.write(
            ".llm-wiki/project-graph/edges.md",
            "| edge_id | from_project | to_project |\n|---|---|---|\n| edge-20260623-001 | unknown-project | smarthub |\n",
        )

        self.assertIn(("unresolved-project-id", ".llm-wiki/project-graph/edges.md"), fixture.finding_keys())

    def test_unresolved_project_id_does_not_scan_free_prose(self):
        fixture = self.with_fixture()
        fixture.write(
            ".llm-wiki/requirements/foo.md",
            "# Requirement\n\nunknown-project appears in a prose note, but no structured field names it.\n",
        )

        self.assertNotIn(("unresolved-project-id", ".llm-wiki/requirements/foo.md"), fixture.finding_keys())

    def test_score_json_reports_low_score_for_empty_wiki(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".llm-wiki").mkdir()

            result = run_doctor_cli(root, "score", "--format", "json")

            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(1, payload["score_version"])
            self.assertLess(payload["score"], 60)
            self.assertIn("fact_ids", payload["signals"])
            self.assertTrue(any(".llm-wiki/README.md" in step for step in payload["next_steps"]))

    def test_score_marks_project_graph_not_applicable_for_single_project(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            fixture = DoctorFixture(root)
            fixture.write(
                ".llm-wiki/project-ids.json",
                json.dumps(
                    {
                        "local_projects": ["single-project"],
                        "projects": [{"id": "single-project", "aliases": []}],
                    }
                ),
            )
            fixture.write(".llm-wiki/README.md", "# Single project\n\nThis wiki has enough prose for orientation.\n")
            fixture.write(".llm-wiki/modules/index.md", "| Module | Status |\n|---|---|\n| app | active |\n")
            fixture.write(".llm-wiki/sources/registry.md", "| Source | Status |\n|---|---|\n| pom.xml | active |\n")

            result = run_doctor_cli(root, "score", "--format", "json")

            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            graph_dimension = next(item for item in payload["dimensions"] if item["name"] == "Project Graph / cross-refs")
            self.assertEqual("not-applicable", graph_dimension["applicability"])
            self.assertIsNone(graph_dimension["score"])

    def test_report_text_is_chinese_and_always_exits_zero(self):
        fixture = self.with_fixture()
        fixture.write(".llm-wiki/requirements/foo.md", "# Requirement\n\nSee C:\\Users\\admin\\secret\\note.md\n")

        result = run_doctor_cli(fixture.root, "report", "--format", "text")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("# LLM Wiki Doctor 报告", result.stdout)
        self.assertIn("## 建议行动计划", result.stdout)
        self.assertIn("leaked-local-path", result.stdout)

    def test_report_json_contains_findings_and_score(self):
        fixture = self.with_fixture()
        fixture.write("docs/plans/foo.md", "# Foo design\n")

        result = run_doctor_cli(fixture.root, "report", "--format", "json")

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("findings", payload)
        self.assertIn("score", payload)
        self.assertEqual(1, payload["score"]["score_version"])

    def test_project_id_matching_uses_token_boundaries_and_aliases(self):
        fixture = self.with_fixture()
        doctor = load_doctor()
        registry = doctor.load_registry(fixture.root)

        self.assertEqual({"smarthub-mediakit"}, doctor.extract_project_mentions("smarthub-mediakit-server", registry))
        self.assertEqual(set(), doctor.extract_project_mentions("xxx-smarthub-mediakit-extra", registry))

    def test_local_project_mentions_do_not_warn_without_cross_service_signal(self):
        fixture = self.with_fixture()
        fixture.write(
            ".llm-wiki/requirements/foo.md",
            "# Requirement\n\nsmart-go-device-mapping and smart-go-file share this repo context.\n",
        )

        self.assertNotIn(("missing-graph-evidence", ".llm-wiki/requirements/foo.md"), fixture.finding_keys())


if __name__ == "__main__":
    unittest.main()
