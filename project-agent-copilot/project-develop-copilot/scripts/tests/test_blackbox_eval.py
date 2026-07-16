import importlib.util
import base64
import hashlib
import json
import os
import subprocess
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


class BlackboxEvalPrepareTest(unittest.TestCase):
    def setUp(self):
        self.runner = load_runner()
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / "workspace"

    def test_prepare_creates_clean_git_fixture_and_external_answer_path(self):
        run_path = self.runner.prepare_run(
            "2", self.workspace, skill_path=None, run_id="eval-002-test"
        )
        run = self.runner.read_json_object(run_path / "run.json")
        self.assertEqual("READY_FOR_AGENT", run["run_status"])
        self.assertEqual("unverified", run["skill_identity"]["status"])
        self.assertTrue((run_path / "fixture" / ".git").exists())
        self.assertFalse((run_path / "fixture" / "answer.md").exists())
        self.assertEqual("", (run_path / "answer.md").read_text(encoding="utf-8"))
        self.assertEqual(
            "",
            self.runner.run_git(
                run_path / "fixture", ["status", "--porcelain"]
            ).stdout_text,
        )

    def test_prepare_eval_032_keeps_root_index_missing_and_records_two_prompt_hashes(self):
        run_path = self.runner.prepare_run(
            "32", self.workspace, skill_path=None, run_id="eval-032-test"
        )
        run = self.runner.read_json_object(run_path / "run.json")
        self.assertFalse((run_path / "fixture" / ".llm-wiki" / "index.md").exists())
        self.assertNotEqual(
            run["canonical_prompt_sha256"], run["effective_prompt_sha256"]
        )
        self.assertIn(
            "支付回调协议版本",
            (run_path / "prompt.md").read_text(encoding="utf-8"),
        )

    def test_prepare_fingerprints_explicit_skill_path(self):
        skill = Path(self.temp.name) / "installed-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
        run_path = self.runner.prepare_run(
            "2",
            self.workspace,
            skill_path=skill,
            run_id="eval-002-fingerprint-test",
        )
        identity = self.runner.read_json_object(run_path / "run.json")[
            "skill_identity"
        ]
        self.assertEqual("verified", identity["status"])
        self.assertEqual(64, len(identity["fingerprint_sha256"]))

    def test_prepare_rejects_workspace_inside_source_repository(self):
        with self.assertRaises(self.runner.EvalError):
            self.runner.prepare_run(
                "2", self.runner.REPO_ROOT / "tmp-evals", skill_path=None
            )


class BlackboxEvalEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.runner = load_runner()
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def make_run(self, files):
        run_path = self.root / f"run-{len(list(self.root.glob('run-*')))}"
        fixture = run_path / "fixture"
        fixture.mkdir(parents=True)
        for relative_path, content in files.items():
            path = fixture / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.runner.run_git(fixture, ["init"])
        self.runner.run_git(fixture, ["config", "core.autocrlf", "false"])
        self.runner.run_git(fixture, ["add", "--all"])
        self.runner.run_git(
            fixture,
            [
                "-c",
                "user.name=Blackbox Eval",
                "-c",
                "user.email=blackbox-eval@example.invalid",
                "-c",
                "commit.gpgSign=false",
                "commit",
                "-m",
                "Baseline fixture",
            ],
        )
        baseline = self.runner.run_git(
            fixture, ["rev-parse", "HEAD"]
        ).stdout_text.strip()
        self.runner.write_json(
            run_path / "run.json", {"fixture_baseline_commit": baseline}
        )
        (run_path / "answer.md").write_text("external answer\n", encoding="utf-8")
        return run_path, fixture, baseline

    def test_porcelain_from_real_git_captures_all_statuses_and_rename_order(self):
        run_path, fixture, _ = self.make_run(
            {
                "modified.txt": b"before\n",
                "deleted.txt": b"delete me\n",
                "旧 名称.txt": "旧内容\n".encode("utf-8"),
            }
        )
        (fixture / "modified.txt").write_text("after\n", encoding="utf-8")
        (fixture / "deleted.txt").unlink()
        (fixture / "added.txt").write_text("added\n", encoding="utf-8")
        self.runner.run_git(fixture, ["add", "added.txt"])
        self.runner.run_git(fixture, ["mv", "旧 名称.txt", "新 名称.txt"])
        untracked = fixture / "tmp" / "未 跟踪.txt"
        untracked.parent.mkdir()
        untracked.write_text("未跟踪\n", encoding="utf-8")

        raw = self.runner.run_git(
            fixture,
            ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
        ).stdout
        entries = self.runner.parse_porcelain_v1_z(raw)
        by_path = {entry["path"]: entry for entry in entries}

        self.assertEqual(" M", by_path["modified.txt"]["status"])
        self.assertEqual("A ", by_path["added.txt"]["status"])
        self.assertEqual(" D", by_path["deleted.txt"]["status"])
        self.assertEqual("??", by_path["tmp/未 跟踪.txt"]["status"])
        self.assertEqual("R ", by_path["新 名称.txt"]["status"])
        self.assertEqual("旧 名称.txt", by_path["新 名称.txt"]["original_path"])
        self.assertFalse((fixture / "run.json").exists())
        self.assertTrue((run_path / "run.json").exists())

    def test_untracked_capture_uses_utf8_base64_and_exact_file_limit(self):
        fixture = self.root / "fixture-capture"
        fixture.mkdir()
        contents = {
            "z-too-large.bin": b"z" * 65_537,
            "c-exact.txt": b"x" * 65_536,
            "b-binary.bin": b"\x00\xffbinary",
            "a-中文.txt": "你好，证据\n".encode("utf-8"),
        }
        for relative_path, content in contents.items():
            (fixture / relative_path).write_bytes(content)

        manifest = self.runner.collect_untracked_content(
            fixture, list(reversed(contents))
        )
        by_path = {entry["path"]: entry for entry in manifest}

        self.assertEqual(sorted(contents), [entry["path"] for entry in manifest])
        self.assertEqual("utf-8", by_path["a-中文.txt"]["capture"]["encoding"])
        self.assertEqual(
            "你好，证据\n", by_path["a-中文.txt"]["capture"]["content"]
        )
        self.assertEqual("base64", by_path["b-binary.bin"]["capture"]["encoding"])
        self.assertEqual(
            contents["b-binary.bin"],
            base64.b64decode(by_path["b-binary.bin"]["capture"]["content"]),
        )
        self.assertEqual("captured", by_path["c-exact.txt"]["capture"]["status"])
        self.assertEqual(
            {"status": "omitted", "reason": "file-too-large"},
            by_path["z-too-large.bin"]["capture"],
        )
        for path, entry in by_path.items():
            self.assertEqual(len(contents[path]), entry["size"])
            self.assertEqual(hashlib.sha256(contents[path]).hexdigest(), entry["sha256"])

    def test_untracked_capture_allows_exact_run_cap_then_omits_overflow(self):
        fixture = self.root / "fixture-run-cap"
        fixture.mkdir()
        paths = []
        for index in range(16):
            relative_path = f"chunk-{index:02d}.txt"
            (fixture / relative_path).write_bytes(b"x" * 65_536)
            paths.append(relative_path)
        overflow_path = "chunk-16-overflow.txt"
        (fixture / overflow_path).write_bytes(b"x")
        paths.append(overflow_path)

        manifest = self.runner.collect_untracked_content(
            fixture, list(reversed(paths))
        )

        self.assertEqual(paths, [entry["path"] for entry in manifest])
        self.assertTrue(
            all(entry["capture"]["status"] == "captured" for entry in manifest[:16])
        )
        self.assertEqual(
            {"status": "omitted", "reason": "run-cap-exceeded"},
            manifest[16]["capture"],
        )

    def test_untracked_link_is_hashed_from_target_text_without_following(self):
        fixture = self.root / "fixture-link"
        fixture.mkdir()
        if os.name == "nt":
            target = self.root / "outside-secret"
            target.mkdir()
            (target / "secret.txt").write_text(
                "must not be captured\n", encoding="utf-8"
            )
            link = fixture / "outside-link"
            completed = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                check=False,
            )
            if completed.returncode != 0:
                self.skipTest(
                    "junction unavailable: "
                    + completed.stderr.decode("utf-8", errors="replace")
                )
            self.addCleanup(os.rmdir, link)
        else:
            target = self.root / "outside-secret.txt"
            target.write_text("must not be captured\n", encoding="utf-8")
            link = fixture / "outside-link.txt"
            try:
                os.symlink(target, link)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"symlink unavailable: {error}")

        manifest = self.runner.collect_untracked_content(
            fixture, [link.name]
        )
        entry = manifest[0]
        target_text = os.readlink(link)

        self.assertEqual("link", entry["kind"])
        self.assertEqual(target_text, entry["target"])
        self.assertEqual(len(target_text.encode("utf-8")), entry["size"])
        self.assertEqual(
            hashlib.sha256(target_text.encode("utf-8")).hexdigest(), entry["sha256"]
        )
        self.assertEqual(
            {"status": "omitted", "reason": "link"}, entry["capture"]
        )
        self.assertNotIn("must not be captured", json.dumps(entry))

    def test_evidence_keeps_status_and_untracked_content_outside_fixture(self):
        run_path, fixture, baseline = self.make_run({"tracked.txt": b"before\n"})
        (fixture / "tracked.txt").write_text("after\n", encoding="utf-8")
        untracked = fixture / "tmp" / "output.txt"
        untracked.parent.mkdir()
        untracked.write_bytes(b"captured output\n")

        evidence = self.runner.collect_git_evidence(run_path)
        by_path = {entry["path"]: entry for entry in evidence["statuses"]}

        self.assertEqual(baseline, evidence["baseline_head"])
        self.assertFalse(evidence["head_changed"])
        self.assertTrue(evidence["has_any_write"])
        self.assertEqual(" M", by_path["tracked.txt"]["status"])
        self.assertEqual("??", by_path["tmp/output.txt"]["status"])
        self.assertEqual(
            "captured output\n",
            evidence["untracked_manifest"][0]["capture"]["content"],
        )
        self.assertEqual(
            hashlib.sha256((run_path / "diff.patch").read_bytes()).hexdigest(),
            evidence["diff_patch_sha256"],
        )
        self.assertEqual(
            evidence,
            self.runner.read_json_object(run_path / "evidence.json"),
        )
        for artifact in ("answer.md", "run.json", "evidence.json", "diff.patch"):
            self.assertTrue((run_path / artifact).exists())
            self.assertFalse((fixture / artifact).exists())

    def test_evidence_uses_baseline_diff_after_agent_moves_head(self):
        run_path, fixture, baseline = self.make_run({"binary.bin": b"\x00before\n"})
        (fixture / "binary.bin").write_bytes(b"\x00after\n")
        self.runner.run_git(fixture, ["add", "binary.bin"])
        self.runner.run_git(
            fixture,
            [
                "-c",
                "user.name=Agent",
                "-c",
                "user.email=agent@example.invalid",
                "-c",
                "commit.gpgSign=false",
                "commit",
                "-m",
                "Agent write",
            ],
        )

        evidence = self.runner.collect_git_evidence(run_path)
        expected_diff = self.runner.run_git(
            fixture,
            [
                "diff",
                "--binary",
                "--no-ext-diff",
                "--no-textconv",
                baseline,
                "--",
            ],
        ).stdout

        self.assertEqual([], evidence["statuses"])
        self.assertNotEqual(baseline, evidence["current_head"])
        self.assertTrue(evidence["head_changed"])
        self.assertTrue(evidence["has_any_write"])
        self.assertTrue(expected_diff)
        self.assertIn(b"GIT binary patch", expected_diff)
        self.assertEqual(expected_diff, (run_path / "diff.patch").read_bytes())
