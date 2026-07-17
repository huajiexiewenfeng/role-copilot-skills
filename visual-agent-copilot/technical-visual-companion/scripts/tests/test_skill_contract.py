from pathlib import Path
import re
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[2]
ROLE_ROOT = SKILL_ROOT.parent


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


if __name__ == "__main__":
    unittest.main()
