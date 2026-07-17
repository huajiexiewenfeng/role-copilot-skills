from pathlib import Path
import re
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[2]
ROLE_ROOT = SKILL_ROOT.parent
REPO_ROOT = ROLE_ROOT.parent


class TechnicalVisualCompanionContractTest(unittest.TestCase):
    def test_role_and_skill_files_exist(self):
        for path in (
            ROLE_ROOT / "README.md",
            ROLE_ROOT / "README.zh.md",
            SKILL_ROOT / "SKILL.md",
        ):
            self.assertTrue(path.is_file(), path)

    def test_frontmatter_identity_and_trigger_boundary(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^name: technical-visual-companion$")
        description = re.search(r"(?m)^description: (.+)$", text)
        self.assertIsNotNone(description)
        for phrase in (
            "confirmed technical",
            "static HTML",
            "architecture",
            "sequence",
            "state",
        ):
            self.assertIn(phrase, description.group(1))

    def test_diagram_selection_covers_required_relationships(self):
        text = (SKILL_ROOT / "references" / "diagram-selection.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "System boundary",
            "Sequence or swimlane",
            "State machine",
            "Deployment topology",
            "Data flow",
            "Comparison matrix",
            "Timeline",
        ):
            self.assertIn(phrase, text)
        self.assertIn("one to three", text.lower())
        self.assertIn("one diagram", text.lower())

    def test_visual_language_is_adaptive_not_template_driven(self):
        text = (SKILL_ROOT / "references" / "visual-language.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "Superpowers Visual Companion",
            "semantic color",
            "desktop",
            "mobile",
            "cards alone",
            "Do not use a fixed page template",
        ):
            self.assertIn(phrase, text)

    def test_workflow_preserves_sources_and_requires_visual_verification(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "Confirmed Input Gate",
            "Visual Fact Model",
            "Diagram Selection",
            "Generate One HTML",
            "Deterministic Validation",
            "Desktop Visual Review",
            "390px Mobile Review",
            "Completion Gate",
            "docs/visuals/<topic-slug>.html",
            "do not scan",
            "do not overwrite",
            "visual verification pending",
        ):
            self.assertIn(phrase, text)

    def test_repository_readmes_discover_visual_role(self):
        expected_install = (
            "npx skills add huajiexiewenfeng/role-copilot-skills/"
            "visual-agent-copilot/technical-visual-companion"
        )
        for name in ("README.md", "README.zh.md"):
            text = (REPO_ROOT / name).read_text(encoding="utf-8")
            self.assertIn("visual-agent-copilot", text)
            self.assertIn("technical-visual-companion", text)
            self.assertIn(expected_install, text)

    def test_visual_role_has_focused_ci(self):
        path = REPO_ROOT / ".github" / "workflows" / "visual-agent-copilot-ci.yml"
        self.assertTrue(path.is_file(), path)
        text = path.read_text(encoding="utf-8")
        for phrase in (
            "name: Visual Agent Copilot CI",
            "visual-agent-copilot/**",
            "actions/checkout@v4",
            "actions/setup-python@v5",
            "python-version: '3.11'",
            "Run visual companion tests",
            "python -m unittest discover visual-agent-copilot/technical-visual-companion/scripts/tests",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
