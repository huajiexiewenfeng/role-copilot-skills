import importlib.util
import json
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
        self.assertNotIn(("invalid-graph-edge", ".llm-wiki/requirements/foo.md"), keys)

    def test_invalid_project_graph_evidence_warns(self):
        fixture = self.with_fixture()
        fixture.write(
            ".llm-wiki/requirements/foo.md",
            "# Requirement\n\nsmart-go-device-mapping calls smarthub-mediakit.\n\n## Project Graph Evidence\n\n| Edge | Relation |\n|---|---|\n| `edge-20990101-999` | missing |\n",
        )

        self.assertIn(("invalid-graph-edge", ".llm-wiki/requirements/foo.md"), fixture.finding_keys())

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
