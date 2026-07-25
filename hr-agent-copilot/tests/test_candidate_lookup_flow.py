import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from llm_wiki_runtime.runtime import init_profile


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def candidate_record(
    candidate_id: str,
    display_name: str,
    aliases: list[str],
) -> str:
    alias_text = ", ".join(json.dumps(item) for item in aliases)
    return "\n".join(
        [
            "---",
            "record_type: candidate_profile",
            f"candidate_id: {candidate_id}",
            f"display_name: {json.dumps(display_name)}",
            f"aliases: [{alias_text}]",
            "current_resume_version_id: resume-example-001",
            'phone: "000-0000"',
            "---",
            "# Synthetic profile",
            "",
        ]
    )


class CandidateLookupFlowTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.scope = Path(self.temporary.name)
        init_profile(
            self.scope,
            PACKAGE_ROOT / "llm-wiki-profile.yml",
            "local",
            "hr-test",
        )
        records = (
            ("candidate-example-001", "Example Candidate", ["E Candidate"]),
            ("candidate-example-002", "Shared Candidate", []),
            ("candidate-example-003", "Shared Candidate", []),
        )
        for candidate_id, display_name, aliases in records:
            path = (
                self.scope
                / ".llm-wiki"
                / "domains"
                / "hr"
                / "candidates"
                / candidate_id
                / "profile.md"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                candidate_record(candidate_id, display_name, aliases),
                encoding="utf-8",
            )

    def tearDown(self):
        self.temporary.cleanup()

    def lookup(self, value: str) -> dict:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "llm_wiki_runtime.cli",
                "find-records",
                "--scope-root",
                str(self.scope),
                "--record-type",
                "candidate_profile",
                "--lookup-value-json",
                json.dumps(value),
                "--caller-domain",
                "hr",
                "--target-domain",
                "hr",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return json.loads(result.stdout)

    def test_found_multiple_and_not_found_are_deterministic(self):
        found = self.lookup("E Candidate")
        multiple = self.lookup("Shared Candidate")
        missing = self.lookup("Missing Candidate")

        self.assertEqual(found["status"], "found")
        self.assertEqual(found["matches"][0]["identity"], "candidate-example-001")
        self.assertNotIn("phone", found["matches"][0]["fields"])
        self.assertEqual(multiple["status"], "multiple_matches")
        self.assertEqual(len(multiple["matches"]), 2)
        self.assertEqual(missing["status"], "not_found")
        self.assertFalse((self.scope / ".llm-wiki/.meta/graph").exists())


if __name__ == "__main__":
    unittest.main()
