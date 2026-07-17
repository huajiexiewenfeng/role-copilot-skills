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


if __name__ == "__main__":
    unittest.main()
