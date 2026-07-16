import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "blackbox_eval.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("blackbox_eval", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BlackboxEvalAssetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner()

    def test_eval_002_profile_is_valid_and_extracts_canonical_prompt(self):
        profile = self.runner.load_profile("2")
        self.assertEqual("2", profile.eval_id)
        self.assertEqual(3, len(profile.canary_pairs))
        self.assertEqual(2, profile.min_observed_pairs)
        prompt = self.runner.extract_canonical_prompt(profile)
        self.assertTrue(prompt.startswith("基于这个项目的 llm wiki"))
        self.assertIn("先不要开发", prompt)

    def test_eval_032_profile_and_fixture_keep_root_index_absent(self):
        profile = self.runner.load_profile("32")
        self.assertEqual("32", profile.eval_id)
        self.assertEqual(3, len(profile.canary_pairs))
        self.assertFalse((profile.fixture_root / ".llm-wiki" / "index.md").exists())
        self.assertIn("wiki-before-source-fallback", profile.manual_only_assertion_ids)
        self.assertEqual("manual-only", profile.manual_only_assertions[0].coverage)
        self.assertEqual(
            "final answer cannot prove read order without runtime trace",
            profile.manual_only_assertions[0].reason,
        )

    def test_canary_literals_are_unique_and_not_substrings(self):
        for eval_id in ("2", "32"):
            profile = self.runner.load_profile(eval_id)
            values = [
                value
                for pair in profile.canary_pairs
                for value in (pair.preferred, pair.conflicting_source)
            ]
            self.assertEqual(len(values), len(set(values)))
            for left in values:
                for right in values:
                    if left != right:
                        self.assertNotIn(left, right)

    def test_fixture_places_preferred_and_source_literals_in_separate_authority_zones(self):
        for eval_id in ("2", "32"):
            profile = self.runner.load_profile(eval_id)
            wiki = "\n".join(
                path.read_text(encoding="utf-8")
                for path in sorted((profile.fixture_root / ".llm-wiki").rglob("*.md"))
            )
            legacy = "\n".join(
                path.read_text(encoding="utf-8")
                for path in sorted((profile.fixture_root / "legacy").rglob("*"))
                if path.is_file()
            )
            for pair in profile.canary_pairs:
                self.assertEqual(1, wiki.count(pair.preferred))
                self.assertNotIn(pair.conflicting_source, wiki)
                self.assertEqual(1, legacy.count(pair.conflicting_source))
                self.assertNotIn(pair.preferred, legacy)

    def test_judge_adoption_fields_accept_the_conditional_contract(self):
        judge = {
            "assertions": [
                {
                    "id": "canary-adoption:live-requirement",
                    "adopted": "preferred",
                },
                {"id": "read-only-context-pack"},
            ]
        }

        self.runner.validate_judge_adoption_fields(judge)

    def test_judge_adoption_fields_reject_missing_adoption_for_canary_assertion(self):
        judge = {
            "assertions": [
                {"id": "canary-adoption:live-requirement"},
            ]
        }

        with self.assertRaisesRegex(
            self.runner.EvalError,
            "adopted is required for canary-adoption assertions",
        ):
            self.runner.validate_judge_adoption_fields(judge)

    def test_judge_adoption_fields_reject_adoption_for_other_assertion(self):
        judge = {
            "assertions": [
                {
                    "id": "read-only-context-pack",
                    "adopted": "preferred",
                },
            ]
        }

        with self.assertRaisesRegex(
            self.runner.EvalError,
            "adopted is forbidden for non-canary assertions",
        ):
            self.runner.validate_judge_adoption_fields(judge)
