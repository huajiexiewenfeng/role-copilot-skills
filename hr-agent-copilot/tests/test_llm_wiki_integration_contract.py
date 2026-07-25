import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CHILDREN = (
    "hr-resume-screening-copilot",
    "hr-candidate-detail-report-copilot",
    "hr-interview-question-generator-copilot",
)


class HrLlmWikiIntegrationContractTest(unittest.TestCase):
    def test_profile_and_shared_contract_are_source_controlled(self):
        for relative in (
            "SKILL.md",
            "llm-wiki-profile.yml",
            "graph-adapter.yml",
            "ingest-mapping.yml",
            "references/llm-wiki-integration.md",
            "references/llm-wiki-ingest.md",
        ):
            self.assertTrue((PACKAGE_ROOT / relative).is_file(), relative)

    def test_package_root_routes_to_exactly_one_child(self):
        text = (PACKAGE_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("exactly one child skill", text.lower())
        self.assertIn("does not run `resolve-config`", text)
        for child in CHILDREN:
            self.assertIn(f"{child}/SKILL.md", text)
        self.assertFalse((PACKAGE_ROOT / "scp.yml").exists())

    def test_each_child_has_scp_and_runtime_fallback(self):
        for child in CHILDREN:
            root = PACKAGE_ROOT / child
            text = (root / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue((root / "scp.yml").is_file())
            self.assertIn("../references/llm-wiki-integration.md", text)
            self.assertIn("resolve-config", text)
            self.assertIn("fallback", text.lower())

    def test_original_sources_and_meta_are_excluded(self):
        profile = (PACKAGE_ROOT / "llm-wiki-profile.yml").read_text(encoding="utf-8")
        self.assertIn("exclude: [sources/originals/**, .meta/**]", profile)

    def test_candidate_lookup_is_declared_with_minimal_return_fields(self):
        profile = (PACKAGE_ROOT / "llm-wiki-profile.yml").read_text(encoding="utf-8")
        for fragment in (
            "record_lookup:",
            "candidate_profile:",
            "identity_field: candidate_id",
            "display_field: display_name",
            "match_fields: [display_name, aliases]",
            "current_resume_version_id",
            "max_results: 20",
        ):
            self.assertIn(fragment, profile)

    def test_shared_query_contract_uses_lookup_without_graph_or_shell_search(self):
        text = (
            PACKAGE_ROOT / "references/llm-wiki-integration.md"
        ).read_text(encoding="utf-8")
        self.assertIn("find-records", text)
        self.assertIn("multiple_matches", text)
        self.assertIn("not_found", text)
        self.assertIn("candidate_id", text)
        self.assertIn("aliases", text)
        self.assertNotIn("graph.json", text)
        self.assertNotIn("run `rg`", text)
        self.assertIn("Never infer candidate identity from Graph output", text)

    def test_readmes_document_optional_runtime(self):
        for name in ("README.md", "README.zh.md"):
            text = (PACKAGE_ROOT / name).read_text(encoding="utf-8")
            self.assertIn("references/llm-wiki-integration.md", text)


if __name__ == "__main__":
    unittest.main()
