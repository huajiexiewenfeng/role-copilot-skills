import importlib.util
import base64
import hashlib
import json
import os
import subprocess
import sys
import unittest
from datetime import datetime, timezone
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


class BlackboxEvalDeterministicAssertionsTest(unittest.TestCase):
    def setUp(self):
        self.runner = load_runner()
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.profile = self.runner.load_profile("2")

    def assertion_by_id(self, assertions, assertion_id):
        return next(item for item in assertions if item.id == assertion_id)

    def run_assertions(self, answer, profile=None, has_any_write=False, run_path=None):
        selected_profile = profile or self.profile
        selected_run_path = run_path or self.root / "unused-run"
        return self.runner.run_deterministic_assertions(
            selected_run_path,
            selected_profile,
            answer,
            {"has_any_write": has_any_write},
        )

    def make_eval_032_run(self, baseline_has_root_index):
        run_path = self.root / (
            "eval-032-invalid-baseline" if baseline_has_root_index else "eval-032-run"
        )
        fixture = run_path / "fixture"
        fixture.mkdir(parents=True)
        readme = fixture / ".llm-wiki" / "README.md"
        readme.parent.mkdir(parents=True)
        readme.write_text("# Fixture Wiki\n", encoding="utf-8")
        if baseline_has_root_index:
            (readme.parent / "index.md").write_text(
                "# Invalid baseline index\n", encoding="utf-8"
            )
        self.runner.run_git(fixture, ["init"])
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
        return run_path, fixture

    def test_observe_canary_pairs_reports_all_four_states_for_each_pair(self):
        for pair in self.profile.canary_pairs:
            cases = {
                "wiki_only": pair.preferred,
                "source_only": pair.conflicting_source,
                "both": f"{pair.preferred} {pair.conflicting_source}",
                "neither": "no canary facts",
            }
            for expected_state, answer in cases.items():
                with self.subTest(pair=pair.id, state=expected_state):
                    observation = next(
                        item
                        for item in self.runner.observe_canary_pairs(
                            answer, self.profile
                        )
                        if item["pair_id"] == pair.id
                    )
                    self.assertEqual(expected_state, observation["state"])
                    self.assertEqual(
                        expected_state in {"wiki_only", "both"},
                        observation["preferred_observed"],
                    )
                    self.assertEqual(
                        expected_state in {"source_only", "both"},
                        observation["conflicting_source_observed"],
                    )

    def test_observe_canary_pairs_keeps_cross_pair_states_independent(self):
        first, second, third = self.profile.canary_pairs
        answer = " ".join(
            (
                first.preferred,
                second.conflicting_source,
                third.preferred,
                third.conflicting_source,
            )
        )

        observations = self.runner.observe_canary_pairs(answer, self.profile)

        self.assertEqual(
            ["wiki_only", "source_only", "both"],
            [item["state"] for item in observations],
        )
        self.assertEqual(
            2, sum(item["preferred_observed"] for item in observations)
        )

    def test_observe_canary_pairs_is_case_sensitive(self):
        pair = self.profile.canary_pairs[0]

        observations = self.runner.observe_canary_pairs(
            f"{pair.preferred.lower()} {pair.conflicting_source.lower()}",
            self.profile,
        )

        self.assertEqual("neither", observations[0]["state"])

    def test_source_only_canaries_never_create_a_deterministic_fail(self):
        answer = " ".join(
            pair.conflicting_source for pair in self.profile.canary_pairs
        )

        assertions, observations = self.run_assertions(answer)

        self.assertEqual(
            ["source_only", "source_only", "source_only"],
            [item["state"] for item in observations],
        )
        self.assertNotIn("FAIL", [item.outcome for item in assertions])

    def test_any_git_write_is_a_hard_fail(self):
        assertions, _ = self.run_assertions("", has_any_write=True)

        result = self.assertion_by_id(assertions, "write-boundary")
        self.assertEqual("FAIL", result.outcome)
        self.assertEqual("hard", result.severity)

    def test_missing_all_required_wiki_paths_is_partial_not_fail(self):
        assertions, _ = self.run_assertions("No configured Wiki path is cited.")

        result = self.assertion_by_id(assertions, "wiki-path-citation")
        self.assertEqual("PARTIAL", result.outcome)
        self.assertNotEqual("FAIL", result.outcome)

    def test_wiki_path_matches_markdown_and_backslash_tokens_but_not_suffixes(self):
        path = self.profile.required_path_any_of[0]
        answers = (
            f"Evidence: `{path}`.",
            f"Evidence: {path.replace('/', chr(92))}",
            f"See [{path}]({path}).",
        )
        for answer in answers:
            with self.subTest(answer=answer):
                assertions, _ = self.run_assertions(answer)
                self.assertEqual(
                    "PASS",
                    self.assertion_by_id(
                        assertions, "wiki-path-citation"
                    ).outcome,
                )

        assertions, _ = self.run_assertions(f"Evidence: `{path}.bak`.")
        self.assertEqual(
            "PARTIAL",
            self.assertion_by_id(assertions, "wiki-path-citation").outcome,
        )

    def test_eval_032_rejects_fixture_baseline_that_contains_root_index(self):
        profile = self.runner.load_profile("32")
        run_path, _ = self.make_eval_032_run(baseline_has_root_index=True)

        assertions, _ = self.run_assertions(
            profile.required_path_any_of[0], profile=profile, run_path=run_path
        )

        result = self.assertion_by_id(assertions, "wiki-root-index-absent")
        self.assertEqual("RUN_ERROR", result.outcome)
        self.assertEqual("hard", result.severity)

    def test_eval_032_fails_when_root_index_is_created_after_baseline(self):
        profile = self.runner.load_profile("32")
        run_path, fixture = self.make_eval_032_run(baseline_has_root_index=False)
        (fixture / ".llm-wiki" / "index.md").write_text(
            "# Agent-created index\n", encoding="utf-8"
        )

        assertions, _ = self.run_assertions(
            profile.required_path_any_of[0], profile=profile, run_path=run_path
        )

        result = self.assertion_by_id(assertions, "wiki-root-index-absent")
        self.assertEqual("FAIL", result.outcome)
        self.assertEqual("hard", result.severity)

    def test_all_neither_canaries_create_partial_coverage_without_adoption(self):
        assertions, observations = self.run_assertions("No observable facts.")

        result = self.assertion_by_id(assertions, "canary-coverage")
        self.assertEqual("PARTIAL", result.outcome)
        self.assertTrue(all(item["state"] == "neither" for item in observations))
        self.assertFalse(any(hasattr(item, "adopted") for item in assertions))
        self.assertTrue(all("adopted" not in item for item in observations))

    def test_manual_only_assertion_is_recorded_as_unautomated_metadata(self):
        profile = self.runner.load_profile("32")
        run_path, _ = self.make_eval_032_run(baseline_has_root_index=False)

        assertions, _ = self.run_assertions(
            profile.required_path_any_of[0], profile=profile, run_path=run_path
        )

        result = self.assertion_by_id(assertions, "wiki-before-source-fallback")
        self.assertEqual("UNAUTOMATED", result.outcome)
        self.assertEqual("manual-only", result.layer)
        self.assertIn("coverage=manual-only", result.message)
        self.assertIn(profile.manual_only_assertions[0].reason, result.message)
        self.assertNotEqual("PASS", result.outcome)

    def test_route_self_report_text_does_not_affect_deterministic_grading(self):
        pair = self.profile.canary_pairs[0]
        facts = f"{self.profile.required_path_any_of[0]} {pair.preferred}"

        plain = self.run_assertions(facts)
        self_reported = self.run_assertions(
            "I routed through project-query in read-only mode. " + facts
        )

        self.assertEqual(plain, self_reported)


class BlackboxEvalJudgeTest(unittest.TestCase):
    def setUp(self):
        self.runner = load_runner()
        self.profile = self.runner.load_profile("2")
        self.answer = (
            "Canonical answer clause. "
            + " ".join(pair.preferred for pair in self.profile.canary_pairs)
        )
        self.observations = self.runner.observe_canary_pairs(
            self.answer, self.profile
        )
        self.evidence_registry = {
            "answer.md": {
                "kind": "text",
                "content": self.answer,
                "quotable": True,
            },
            "diff.patch": {
                "kind": "text",
                "content": "diff-only evidence clause",
                "quotable": True,
            },
        }

    def valid_judge(self):
        assertions = [
            {
                "id": assertion_id,
                "verdict": "pass",
                "evidence_ref": "answer.md",
                "evidence_quote": "Canonical answer clause.",
                "reason": "The answer supplies the required semantic behavior.",
            }
            for assertion_id in self.profile.semantic_assertion_ids
        ]
        assertions.extend(
            {
                "id": f"canary-adoption:{pair.id}",
                "verdict": "pass",
                "adopted": "preferred",
                "evidence_ref": "answer.md",
                "evidence_quote": pair.preferred,
                "reason": "The preferred authority was adopted.",
            }
            for pair in self.profile.canary_pairs
        )
        return {
            "schema_version": self.runner.JUDGE_SCHEMA_VERSION,
            "model": "fixture-judge",
            "temperature": 0,
            "prompt_version": self.runner.JUDGE_PROMPT_VERSION,
            "profile_version": self.profile.profile_version,
            "evidence_match_mode": self.runner.QUOTE_MATCH_MODE,
            "evidence_normalizer_version": (
                self.runner.QUOTE_NORMALIZER_VERSION
            ),
            "assertions": assertions,
        }

    def grade(self, judge, deterministic_assertions=()):
        return self.runner.grade_judge(
            judge,
            self.profile,
            self.evidence_registry,
            self.observations,
            deterministic_assertions,
        )

    @staticmethod
    def by_id(results, assertion_id):
        return next(item for item in results if item.id == assertion_id)

    def test_quote_normalization_matches_only_fixed_transformations(self):
        evidence = (
            "ＡＢＣ，第一句。\r\n\u2003\u2003第二句：“值”——完成！"
        )
        quote = 'ABC,第一句. \n 第二句:"值"--完成!'

        self.assertEqual(
            'ABC,第一句. 第二句:"值"--完成!',
            self.runner.normalize_quote_v1(evidence),
        )
        self.assertTrue(self.runner.quote_matches_evidence(quote, evidence))

    def test_quote_matching_rejects_nonliteral_transformations(self):
        evidence = "Alpha first clause, exact middle clause, final clause."
        rejected = (
            "alpha first clause, exact middle clause, final clause.",
            "Alpha first clause, synonymous middle clause, final clause.",
            "Alpha first clause, final clause.",
            "final clause. Alpha first clause, exact middle clause",
        )

        for quote in rejected:
            with self.subTest(quote=quote):
                self.assertFalse(
                    self.runner.quote_matches_evidence(quote, evidence)
                )

    def test_valid_quote_is_matched_only_in_its_declared_evidence_source(self):
        judge = self.valid_judge()
        judge["assertions"][0]["evidence_quote"] = (
            "diff-only evidence clause"
        )

        results = self.grade(judge)

        result = self.by_id(results, self.profile.semantic_assertion_ids[0])
        self.assertEqual("NEEDS_REVIEW", result.outcome)
        self.assertIn("evidence_quote_unmatched", result.message)

    def test_invalid_judge_inputs_produce_run_error_validation_result(self):
        cases = {}
        invalid_quote = self.valid_judge()
        invalid_quote["assertions"][0]["evidence_quote"] = "，。！？"
        cases["punctuation-only quote"] = invalid_quote
        empty_quote = self.valid_judge()
        empty_quote["assertions"][0]["evidence_quote"] = ""
        cases["empty quote"] = empty_quote
        wrong_schema = self.valid_judge()
        wrong_schema["schema_version"] = "9.9"
        cases["wrong schema"] = wrong_schema
        unknown_ref = self.valid_judge()
        unknown_ref["assertions"][0]["evidence_ref"] = "evidence.json"
        cases["unknown evidence ref"] = unknown_ref
        unknown_mode = self.valid_judge()
        unknown_mode["evidence_match_mode"] = "fuzzy"
        cases["unknown match mode"] = unknown_mode
        unknown_normalizer = self.valid_judge()
        unknown_normalizer["evidence_normalizer_version"] = "future-v2"
        cases["unknown normalizer"] = unknown_normalizer
        wrong_profile = self.valid_judge()
        wrong_profile["profile_version"] = "wrong-profile"
        cases["wrong profile"] = wrong_profile
        wrong_prompt = self.valid_judge()
        wrong_prompt["prompt_version"] = "judge-prompt-9.9"
        cases["wrong prompt"] = wrong_prompt
        missing_required = self.valid_judge()
        del missing_required["model"]
        cases["missing required key"] = missing_required
        duplicate_id = self.valid_judge()
        duplicate_id["assertions"][-1]["id"] = duplicate_id["assertions"][0]["id"]
        cases["duplicate ID"] = duplicate_id
        missing_expected = self.valid_judge()
        missing_expected["assertions"].pop()
        cases["missing expected ID"] = missing_expected

        for name, judge in cases.items():
            with self.subTest(name=name):
                result = self.by_id(self.grade(judge), "judge-validation")
                self.assertEqual("RUN_ERROR", result.outcome)

    def test_every_observed_canary_pair_requires_an_adoption_assertion(self):
        judge = self.valid_judge()
        judge["assertions"] = [
            item
            for item in judge["assertions"]
            if item["id"] != f"canary-adoption:{self.profile.canary_pairs[1].id}"
        ]

        result = self.by_id(self.grade(judge), "judge-validation")

        self.assertEqual("RUN_ERROR", result.outcome)

    def test_canary_adoption_maps_to_results_and_requires_two_preferred(self):
        judge = self.valid_judge()
        canary_assertions = [
            item
            for item in judge["assertions"]
            if item["id"].startswith("canary-adoption:")
        ]
        canary_assertions[0].update(adopted="source", verdict="fail")
        canary_assertions[1].update(adopted="uncertain", verdict="uncertain")
        canary_assertions[2].update(adopted="preferred", verdict="pass")

        results = self.grade(judge)

        self.assertEqual("FAIL", self.by_id(results, canary_assertions[0]["id"]).outcome)
        self.assertEqual(
            "NEEDS_REVIEW",
            self.by_id(results, canary_assertions[1]["id"]).outcome,
        )
        self.assertEqual(
            "PARTIAL",
            self.by_id(results, "canary-adoption-coverage").outcome,
        )

    def test_judge_results_do_not_override_deterministic_hard_failures(self):
        hard_fail = self.runner.AssertionResult(
            id="write-boundary",
            layer="deterministic",
            outcome="FAIL",
            severity="hard",
            message="Fixture was modified.",
        )

        results = self.grade(self.valid_judge(), (hard_fail,))

        self.assertEqual("FAIL", self.by_id(results, "write-boundary").outcome)
        self.assertEqual("hard", self.by_id(results, "write-boundary").severity)

    def test_build_judge_request_records_versions_contract_and_text_evidence(self):
        with TemporaryDirectory() as temp:
            run_path = Path(temp)
            request = self.runner.build_judge_request(
                run_path,
                self.profile,
                self.answer,
                b"diff --git a/file b/file\n+text change\n",
                self.observations,
            )

            self.assertEqual(self.profile.profile_version, request["profile_version"])
            self.assertEqual(self.runner.JUDGE_PROMPT_VERSION, request["prompt_version"])
            self.assertEqual(self.runner.QUOTE_MATCH_MODE, request["evidence_match_mode"])
            self.assertEqual(
                self.runner.QUOTE_NORMALIZER_VERSION,
                request["evidence_normalizer_version"],
            )
            self.assertIn(self.profile.canonical_heading, request["canonical_eval"])
            self.assertEqual(
                list(self.profile.semantic_assertion_ids),
                request["semantic_assertion_ids"],
            )
            self.assertEqual(
                list(self.profile.contract_refs),
                [
                    (item["path"], item["heading"])
                    for item in request["contract_sections"]
                ],
            )
            self.assertEqual(
                self.answer,
                request["evidence_registry"]["answer.md"]["content"],
            )
            self.assertTrue(request["evidence_registry"]["diff.patch"]["quotable"])
            self.assertEqual(
                request,
                self.runner.read_json_object(run_path / "judge-request.json"),
            )

    def test_binary_diff_request_is_hash_only_and_not_quotable(self):
        diffs = (
            b"\x00\xffbinary patch",
            b"diff --git a/image.png b/image.png\nGIT binary patch\nliteral 1\n",
        )
        for diff in diffs:
            with self.subTest(diff=diff), TemporaryDirectory() as temp:
                request = self.runner.build_judge_request(
                    Path(temp),
                    self.profile,
                    self.answer,
                    diff,
                    self.observations,
                )

                entry = request["evidence_registry"]["diff.patch"]
                self.assertEqual("binary", entry["kind"])
                self.assertFalse(entry["quotable"])
                self.assertNotIn("content", entry)
                self.assertEqual(hashlib.sha256(diff).hexdigest(), entry["sha256"])


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

    def test_untracked_capture_rejects_link_in_parent_path(self):
        fixture = self.root / "fixture-nested-link"
        fixture.mkdir()
        target = self.root / "outside-directory"
        target.mkdir()
        (target / "secret.txt").write_text(
            "must not be captured through a parent link\n", encoding="utf-8"
        )
        link = fixture / "link-dir"
        if os.name == "nt":
            completed = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                check=False,
            )
            if completed.returncode != 0:
                self.fail(
                    "junction unavailable: "
                    + completed.stderr.decode("utf-8", errors="replace")
                )
            self.addCleanup(os.rmdir, link)
        else:
            os.symlink(target, link, target_is_directory=True)
            self.addCleanup(link.unlink)

        with self.assertRaisesRegex(
            self.runner.EvalError, "link-like untracked path component"
        ):
            self.runner.collect_untracked_content(
                fixture, ["link-dir/secret.txt"]
            )

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

    def test_evidence_disables_optional_locks_and_preserves_git_index(self):
        run_path, fixture, _ = self.make_run({"tracked.txt": b"unchanged\n"})
        tracked = fixture / "tracked.txt"
        tracked_stat = tracked.stat()
        os.utime(
            tracked,
            ns=(tracked_stat.st_atime_ns, tracked_stat.st_mtime_ns + 2_000_000_000),
        )
        index = fixture / ".git" / "index"
        fixed_time_ns = 946_684_800_000_000_000
        os.utime(index, ns=(fixed_time_ns, fixed_time_ns))
        before = (index.read_bytes(), index.stat().st_mtime_ns)

        self.runner.collect_git_evidence(run_path)

        after = (index.read_bytes(), index.stat().st_mtime_ns)
        self.assertEqual("0", self.runner.git_environment()["GIT_OPTIONAL_LOCKS"])
        self.assertEqual(before, after)

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


class BlackboxEvalRunStateTest(unittest.TestCase):
    def setUp(self):
        self.runner = load_runner()
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / "workspace"
        self.profile = self.runner.load_profile("2")

    def make_run(self, suffix="state"):
        return self.runner.prepare_run(
            "2",
            self.workspace,
            skill_path=None,
            run_id=f"eval-002-{suffix}",
            now=lambda: datetime(2026, 7, 16, 1, 2, 3, tzinfo=timezone.utc),
        )

    def good_answer(self):
        return (
            f"Canonical answer clause. {self.profile.required_path_any_of[0]} "
            + " ".join(pair.preferred for pair in self.profile.canary_pairs)
        )

    def valid_judge(self, answer, adopted="preferred"):
        verdict = {"preferred": "pass", "source": "fail"}[adopted]
        assertions = [
            {
                "id": assertion_id,
                "verdict": "pass",
                "evidence_ref": "answer.md",
                "evidence_quote": "Canonical answer clause.",
                "reason": "The answer supplies the required semantic behavior.",
            }
            for assertion_id in self.profile.semantic_assertion_ids
        ]
        literal_by_adoption = {
            "preferred": lambda pair: pair.preferred,
            "source": lambda pair: pair.conflicting_source,
        }
        assertions.extend(
            {
                "id": f"canary-adoption:{pair.id}",
                "verdict": verdict,
                "adopted": adopted,
                "evidence_ref": "answer.md",
                "evidence_quote": literal_by_adoption[adopted](pair),
                "reason": "The cited authority was adopted.",
            }
            for pair in self.profile.canary_pairs
        )
        return {
            "schema_version": self.runner.JUDGE_SCHEMA_VERSION,
            "model": "fixture-judge",
            "temperature": 0,
            "prompt_version": self.runner.JUDGE_PROMPT_VERSION,
            "profile_version": self.profile.profile_version,
            "evidence_match_mode": self.runner.QUOTE_MATCH_MODE,
            "evidence_normalizer_version": self.runner.QUOTE_NORMALIZER_VERSION,
            "assertions": assertions,
        }

    def grade(self, run_path, **overrides):
        values = {
            "execution_kind": "canned",
            "agent_product": "canned",
            "agent_model": "eval-002-good",
            "now": lambda: datetime(2026, 7, 16, 2, 3, 4, tzinfo=timezone.utc),
        }
        values.update(overrides)
        return self.runner.grade_run(run_path, **values)

    def write_good_judge(self, run_path, answer=None):
        answer = answer or self.good_answer()
        self.runner.write_json(run_path / "judge.json", self.valid_judge(answer))

    def test_aggregate_behavior_score_keeps_run_states_separate(self):
        result = self.runner.AssertionResult
        self.assertEqual("PASS", self.runner.aggregate_behavior_score([]))
        self.assertEqual(
            "PARTIAL",
            self.runner.aggregate_behavior_score(
                [result("a", "deterministic", "PARTIAL", "soft", "partial")]
            ),
        )
        self.assertEqual(
            "FAIL",
            self.runner.aggregate_behavior_score(
                [
                    result("a", "judge", "NEEDS_REVIEW", "soft", "review"),
                    result("b", "deterministic", "FAIL", "hard", "failed"),
                ]
            ),
        )

    def test_empty_answer_stays_ready_without_recording_skill_fail(self):
        run_path = self.make_run("empty")

        self.assertEqual(1, self.grade(run_path))

        run = self.runner.read_json_object(run_path / "run.json")
        self.assertEqual("READY_FOR_AGENT", run["run_status"])
        self.assertIsNone(run["answer_sha256"])
        self.assertFalse((run_path / "grading.json").exists())

        missing = self.make_run("missing")
        (missing / "answer.md").unlink()
        self.assertEqual(1, self.grade(missing))
        missing_run = self.runner.read_json_object(missing / "run.json")
        self.assertEqual("READY_FOR_AGENT", missing_run["run_status"])
        self.assertIn("answer.md", missing_run["operator_error"])
        self.assertIsNone(missing_run["answer_sha256"])

    def test_locked_answer_missing_or_empty_is_run_error(self):
        for suffix, mutate in (
            ("locked-answer-missing", lambda path: (path / "answer.md").unlink()),
            ("locked-answer-empty", lambda path: (path / "answer.md").write_bytes(b"")),
        ):
            with self.subTest(suffix=suffix):
                run_path = self.make_run(suffix)
                answer = self.good_answer()
                (run_path / "answer.md").write_text(answer, encoding="utf-8")
                self.write_good_judge(run_path, answer)
                self.assertEqual(0, self.grade(run_path))

                mutate(run_path)

                self.assertEqual(
                    1,
                    self.grade(
                        run_path,
                        execution_kind=None,
                        agent_product=None,
                        agent_model=None,
                    ),
                )
                locked = self.runner.read_json_object(run_path / "run.json")
                self.assertEqual("RUN_ERROR", locked["run_status"])

    def test_missing_and_uncertain_judge_need_review_with_stable_sorted_state(self):
        run_path = self.make_run("review")
        answer = self.good_answer()
        (run_path / "answer.md").write_text(answer, encoding="utf-8")

        self.assertEqual(0, self.grade(run_path))
        first = self.runner.read_json_object(run_path / "run.json")
        self.assertEqual("NEEDS_REVIEW", first["run_status"])
        self.assertEqual(sorted(first["unresolved_assertion_ids"]), first["unresolved_assertion_ids"])
        self.assertEqual(sorted(first["needs_review_reasons"]), first["needs_review_reasons"])
        self.assertEqual(0, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))
        repeated = self.runner.read_json_object(run_path / "run.json")
        self.assertEqual(first["needs_review_since"], repeated["needs_review_since"])

        judge = self.valid_judge(answer)
        judge["assertions"][0]["verdict"] = "uncertain"
        self.runner.write_json(run_path / "judge.json", judge)
        self.assertEqual(0, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))
        uncertain = self.runner.read_json_object(run_path / "run.json")
        self.assertEqual("NEEDS_REVIEW", uncertain["run_status"])
        self.assertEqual(first["needs_review_since"], uncertain["needs_review_since"])

    def test_complete_judge_grades_canned_pass_and_locks_identity_and_answer(self):
        run_path = self.make_run("pass")
        answer = self.good_answer()
        (run_path / "answer.md").write_text(answer, encoding="utf-8")
        self.write_good_judge(run_path, answer)

        self.assertEqual(0, self.grade(run_path))
        run = self.runner.read_json_object(run_path / "run.json")
        grading = self.runner.read_json_object(run_path / "grading.json")
        self.assertEqual("GRADED", run["run_status"])
        self.assertEqual("PASS", run["behavior_score"])
        self.assertEqual("PASS", grading["behavior_score"])
        self.assertEqual("canned", grading["provenance"]["agent_identity"]["execution_kind"])
        self.assertEqual(run["answer_sha256"], grading["provenance"]["answer_sha256"])
        self.assertEqual(
            {
                "model": "fixture-judge",
                "temperature": 0,
                "prompt_version": self.runner.JUDGE_PROMPT_VERSION,
            },
            grading["provenance"]["judge_identity"],
        )

        self.assertEqual(
            1,
            self.grade(
                run_path,
                execution_kind="agent",
                agent_product="other",
                agent_model="other",
            ),
        )
        self.assertEqual("RUN_ERROR", self.runner.read_json_object(run_path / "run.json")["run_status"])

        run_path = self.make_run("answer-mutation")
        (run_path / "answer.md").write_text(answer, encoding="utf-8")
        self.write_good_judge(run_path, answer)
        self.assertEqual(0, self.grade(run_path))
        (run_path / "answer.md").write_text(answer + " changed", encoding="utf-8")
        self.assertEqual(1, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))

    def test_existing_grading_binds_run_identity_and_answer_locks(self):
        cases = (
            ("identity-null", True, False, False),
            ("answer-hash-missing", False, True, False),
            ("both-missing-answer-changed", True, True, True),
        )
        for suffix, clear_identity, clear_answer_hash, change_answer in cases:
            with self.subTest(suffix=suffix):
                run_path = self.make_run(suffix)
                answer = self.good_answer()
                (run_path / "answer.md").write_text(answer, encoding="utf-8")
                self.write_good_judge(run_path, answer)
                self.assertEqual(0, self.grade(run_path))
                grading_bytes = (run_path / "grading.json").read_bytes()
                run = self.runner.read_json_object(run_path / "run.json")
                if clear_identity:
                    run["agent_identity"] = None
                if clear_answer_hash:
                    run.pop("answer_sha256")
                self.runner.write_json(run_path / "run.json", run)
                if change_answer:
                    (run_path / "answer.md").write_text(
                        answer + " changed", encoding="utf-8"
                    )

                self.assertEqual(
                    1,
                    self.grade(
                        run_path,
                        execution_kind="agent",
                        agent_product="replacement-agent",
                        agent_model="replacement-model",
                    ),
                )
                failed = self.runner.read_json_object(run_path / "run.json")
                self.assertEqual("RUN_ERROR", failed["run_status"])
                self.assertEqual(grading_bytes, (run_path / "grading.json").read_bytes())

    def test_hard_write_fail_grades_without_judge_and_cannot_be_overridden(self):
        for suffix, with_judge in (("hard-no-judge", False), ("hard-with-judge", True)):
            with self.subTest(with_judge=with_judge):
                run_path = self.make_run(suffix)
                answer = self.good_answer()
                (run_path / "answer.md").write_text(answer, encoding="utf-8")
                (run_path / "fixture" / "agent-write.txt").write_text("write\n", encoding="utf-8")
                if with_judge:
                    self.write_good_judge(run_path, answer)
                self.assertEqual(0, self.grade(run_path))
                run = self.runner.read_json_object(run_path / "run.json")
                self.assertEqual("GRADED", run["run_status"])
                self.assertEqual("FAIL", run["behavior_score"])

    def test_source_adoption_is_behavior_fail_and_malformed_judge_is_run_error(self):
        run_path = self.make_run("source")
        answer = (
            f"Canonical answer clause. {self.profile.required_path_any_of[0]} "
            + " ".join(pair.conflicting_source for pair in self.profile.canary_pairs)
        )
        (run_path / "answer.md").write_text(answer, encoding="utf-8")
        self.runner.write_json(run_path / "judge.json", self.valid_judge(answer, adopted="source"))
        self.assertEqual(0, self.grade(run_path))
        self.assertEqual("FAIL", self.runner.read_json_object(run_path / "run.json")["behavior_score"])

        malformed = self.make_run("malformed")
        (malformed / "answer.md").write_text(self.good_answer(), encoding="utf-8")
        judge = self.valid_judge(self.good_answer())
        judge["schema_version"] = "9.9"
        self.runner.write_json(malformed / "judge.json", judge)
        self.assertEqual(1, self.grade(malformed))
        self.assertEqual("RUN_ERROR", self.runner.read_json_object(malformed / "run.json")["run_status"])

    def diagnosis(self, grading):
        contract_path, heading = self.profile.contract_refs[0]
        evidence_id = grading["registered_evidence_ids"][0]
        return {
            "schema_version": self.runner.DIAGNOSIS_SCHEMA_VERSION,
            "failure_type": "evidence",
            "likely_source": "stage-skill",
            "violated_contracts": [
                {"path": contract_path, "heading": heading, "evidence_ids": [evidence_id]}
            ],
            "minimal_patch": {
                "path": contract_path,
                "heading": heading,
                "change_intent": "Clarify the evidence boundary without naming fixture literals.",
            },
            "eval_gap": "covered",
            "overfitting_risk": "Keep the rule general and avoid fixture-specific values.",
            "confidence": "high",
        }

    def make_failing_run(self, suffix):
        run_path = self.make_run(suffix)
        answer = (
            f"Canonical answer clause. {self.profile.required_path_any_of[0]} "
            + " ".join(pair.conflicting_source for pair in self.profile.canary_pairs)
        )
        (run_path / "answer.md").write_text(answer, encoding="utf-8")
        self.runner.write_json(run_path / "judge.json", self.valid_judge(answer, adopted="source"))
        self.assertEqual(0, self.grade(run_path))
        return run_path

    def make_terminal_run(self, suffix):
        run_path = self.make_failing_run(suffix)
        grading = self.runner.read_json_object(run_path / "grading.json")
        self.runner.write_json(run_path / "diagnosis.json", self.diagnosis(grading))
        self.assertEqual(
            0,
            self.grade(
                run_path,
                execution_kind=None,
                agent_product=None,
                agent_model=None,
            ),
        )
        run = self.runner.read_json_object(run_path / "run.json")
        decision = {
            "schema_version": self.runner.PATCH_DECISION_SCHEMA_VERSION,
            "decision": "reject",
            "diagnosis_sha256": self.runner._sha256_file(run_path / "diagnosis.json"),
            "freeze_manifest_sha256": run["freeze_manifest_sha256"],
            "decided_by": "Human Reviewer",
            "decided_at": "2026-07-16T03:04:05Z",
            "note": "Reject this candidate.",
        }
        self.runner.write_json(run_path / "patch-decision.json", decision)
        self.assertEqual(
            0,
            self.grade(
                run_path,
                execution_kind=None,
                agent_product=None,
                agent_model=None,
            ),
        )
        return run_path, decision

    def make_revised_terminal_run(self, suffix):
        run_path = self.make_failing_run(suffix)
        grading = self.runner.read_json_object(run_path / "grading.json")
        self.runner.write_json(run_path / "diagnosis.json", self.diagnosis(grading))
        self.assertEqual(
            0,
            self.grade(
                run_path,
                execution_kind=None,
                agent_product=None,
                agent_model=None,
            ),
        )
        run = self.runner.read_json_object(run_path / "run.json")
        decision = {
            "schema_version": self.runner.PATCH_DECISION_SCHEMA_VERSION,
            "decision": "revise",
            "diagnosis_sha256": self.runner._sha256_file(run_path / "diagnosis.json"),
            "freeze_manifest_sha256": run["freeze_manifest_sha256"],
            "decided_by": "Human Reviewer",
            "decided_at": "2026-07-16T03:04:05Z",
            "note": "Revise before reaching a terminal decision.",
        }
        self.runner.write_json(run_path / "patch-decision.json", decision)
        self.assertEqual(
            0,
            self.grade(
                run_path,
                execution_kind=None,
                agent_product=None,
                agent_model=None,
            ),
        )
        decision["decision"] = "reject"
        decision["decided_at"] = "2026-07-16T04:05:06Z"
        decision["note"] = "Reject after requested revision."
        self.runner.write_json(run_path / "patch-decision.json", decision)
        self.assertEqual(
            0,
            self.grade(
                run_path,
                execution_kind=None,
                agent_product=None,
                agent_model=None,
            ),
        )
        return run_path

    def test_first_valid_diagnosis_freezes_evidence_before_human_decision(self):
        run_path = self.make_failing_run("freeze")
        grading = self.runner.read_json_object(run_path / "grading.json")
        self.runner.write_json(run_path / "diagnosis.json", self.diagnosis(grading))

        self.assertEqual(0, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))
        run = self.runner.read_json_object(run_path / "run.json")
        manifest = self.runner.read_json_object(run_path / "freeze-manifest.json")
        self.assertEqual(self.runner._sha256_file(run_path / "freeze-manifest.json"), run["freeze_manifest_sha256"])
        self.assertEqual(grading["provenance"], manifest["provenance"])
        frozen_bytes = {name: (run_path / name).read_bytes() for name in manifest["artifact_hashes"]}
        self.assertEqual(
            1,
            self.grade(
                run_path,
                execution_kind="canned",
                agent_product=None,
                agent_model=None,
            ),
        )

        diagnosis_sha = self.runner._sha256_file(run_path / "diagnosis.json")
        revise = {
            "schema_version": self.runner.PATCH_DECISION_SCHEMA_VERSION,
            "decision": "revise",
            "diagnosis_sha256": diagnosis_sha,
            "freeze_manifest_sha256": run["freeze_manifest_sha256"],
            "decided_by": "Human Reviewer",
            "decided_at": "2026-07-16T03:04:05Z",
            "note": "Revise the general contract mapping.",
        }
        self.runner.write_json(run_path / "patch-decision.json", revise)
        self.assertEqual(0, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))
        revised = self.runner.read_json_object(run_path / "run.json")
        self.assertFalse(revised["level_b_comparison_authorized"])

        revise["decision"] = "approve"
        revise["note"] = "Approve a human-authored candidate for comparison."
        self.runner.write_json(run_path / "patch-decision.json", revise)
        self.assertEqual(0, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))
        approved = self.runner.read_json_object(run_path / "run.json")
        self.assertTrue(approved["level_b_comparison_authorized"])
        self.assertEqual(2, len(approved["patch_decision_history"]))
        self.assertEqual(frozen_bytes, {name: (run_path / name).read_bytes() for name in manifest["artifact_hashes"]})

        (run_path / "patch-decision.json").unlink()
        self.assertEqual(1, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))
        revise["note"] = "Mutated terminal decision."
        self.runner.write_json(run_path / "patch-decision.json", revise)
        self.assertEqual(1, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))

    def test_freeze_detects_artifact_and_provenance_mutation(self):
        for suffix, mutate in (
            ("artifact-tamper", lambda path: (path / "answer.md").write_text("tampered", encoding="utf-8")),
            (
                "provenance-tamper",
                lambda path: self.runner.write_json(
                    path / "run.json",
                    {
                        **self.runner.read_json_object(path / "run.json"),
                        "agent_identity": {
                            "execution_kind": "canned",
                            "agent_product": "canned",
                            "agent_model": "tampered",
                        },
                    },
                ),
            ),
        ):
            with self.subTest(suffix=suffix):
                run_path = self.make_failing_run(suffix)
                grading = self.runner.read_json_object(run_path / "grading.json")
                self.runner.write_json(run_path / "diagnosis.json", self.diagnosis(grading))
                self.assertEqual(0, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))
                mutate(run_path)
                self.assertEqual(1, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))

    def test_freeze_manifest_artifacts_forbid_missing_run_pointer_rollback(self):
        for suffix, mutate in (
            (
                "freeze-pointer-null",
                lambda run: run.__setitem__("freeze_manifest_sha256", None),
            ),
            (
                "freeze-pointer-delete",
                lambda run: run.pop("freeze_manifest_sha256"),
            ),
        ):
            with self.subTest(suffix=suffix):
                run_path = self.make_failing_run(suffix)
                grading = self.runner.read_json_object(run_path / "grading.json")
                self.runner.write_json(run_path / "diagnosis.json", self.diagnosis(grading))
                self.assertEqual(
                    0,
                    self.grade(
                        run_path,
                        execution_kind=None,
                        agent_product=None,
                        agent_model=None,
                    ),
                )
                manifest = self.runner.read_json_object(run_path / "freeze-manifest.json")
                frozen_bytes = {
                    name: (run_path / name).read_bytes()
                    for name in manifest["artifact_hashes"]
                }
                manifest_bytes = (run_path / "freeze-manifest.json").read_bytes()
                run = self.runner.read_json_object(run_path / "run.json")
                mutate(run)
                self.runner.write_json(run_path / "run.json", run)

                self.assertEqual(
                    1,
                    self.grade(
                        run_path,
                        execution_kind=None,
                        agent_product=None,
                        agent_model=None,
                    ),
                )
                failed = self.runner.read_json_object(run_path / "run.json")
                self.assertEqual("RUN_ERROR", failed["run_status"])
                self.assertEqual(
                    manifest_bytes, (run_path / "freeze-manifest.json").read_bytes()
                )
                self.assertEqual(
                    frozen_bytes,
                    {
                        name: (run_path / name).read_bytes()
                        for name in manifest["artifact_hashes"]
                    },
                )

    def test_diagnosis_and_patch_decision_validation_reject_bad_closure(self):
        run_path = self.make_failing_run("bad-diagnosis")
        grading = self.runner.read_json_object(run_path / "grading.json")
        diagnosis = self.diagnosis(grading)
        diagnosis["violated_contracts"][0]["evidence_ids"] = ["invented:evidence"]
        self.runner.write_json(run_path / "diagnosis.json", diagnosis)
        self.assertEqual(1, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))
        self.assertFalse((run_path / "freeze-manifest.json").exists())

    def test_run_versions_git_and_fixture_are_validated_before_grading(self):
        run_path = self.make_run("invalid-run")
        run = self.runner.read_json_object(run_path / "run.json")
        for key, invalid in (
            ("schema_version", "9.9"),
            ("profile_version", "wrong-profile"),
            ("fixture_baseline_commit", "0" * 40),
            ("fixture_baseline_commit", "HEAD"),
            ("skill_source_commit", "0" * 40),
        ):
            with self.subTest(key=key):
                changed = dict(run)
                changed[key] = invalid
                with self.assertRaises(self.runner.EvalError):
                    self.runner._validate_prepared_run(run_path, changed, self.profile)

        fixture_git = run_path / "fixture" / ".git"
        hidden_git = run_path / "fixture" / ".git-hidden"
        fixture_git.rename(hidden_git)
        try:
            with self.assertRaises(self.runner.EvalError):
                self.runner._validate_prepared_run(run_path, run, self.profile)
        finally:
            hidden_git.rename(fixture_git)

    def test_verified_skill_identity_requires_live_path_and_matching_fingerprint(self):
        skill_path = Path(self.temp.name) / "verified-skill"
        skill_path.mkdir()
        (skill_path / "SKILL.md").write_text("# Verified skill\n", encoding="utf-8")
        run_path = self.runner.prepare_run(
            "2",
            self.workspace,
            skill_path=skill_path,
            run_id="eval-002-verified-provenance",
            now=lambda: datetime(2026, 7, 16, 1, 2, 3, tzinfo=timezone.utc),
        )
        run = self.runner.read_json_object(run_path / "run.json")

        missing = json.loads(json.dumps(run))
        missing["skill_identity"]["path"] = str(Path(self.temp.name) / "missing-skill")
        with self.assertRaises(self.runner.EvalError):
            self.runner._validate_prepared_run(run_path, missing, self.profile)

        (skill_path / "SKILL.md").write_text("# Tampered skill\n", encoding="utf-8")
        with self.assertRaises(self.runner.EvalError):
            self.runner._validate_prepared_run(run_path, run, self.profile)

    def test_terminal_decision_uses_independent_anchor_and_rejects_pointer_bypass(self):
        run_path, decision = self.make_terminal_run("terminal-anchor")
        anchor_path = run_path / "terminal-patch-decision.json"
        self.assertTrue(anchor_path.is_file())

        tampered_run = self.runner.read_json_object(run_path / "run.json")
        tampered_run["terminal_patch_decision_sha256"] = None
        self.runner.write_json(run_path / "run.json", tampered_run)
        decision["decision"] = "approve"
        decision["note"] = "Attempt to re-authorize after terminal rejection."
        self.runner.write_json(run_path / "patch-decision.json", decision)

        self.assertEqual(
            1,
            self.grade(
                run_path,
                execution_kind=None,
                agent_product=None,
                agent_model=None,
            ),
        )
        failed = self.runner.read_json_object(run_path / "run.json")
        self.assertEqual("RUN_ERROR", failed["run_status"])
        self.assertFalse(failed.get("level_b_comparison_authorized", False))

    def test_terminal_anchor_and_pointers_are_individually_immutable(self):
        mutations = (
            (
                "anchor-delete",
                lambda path: (path / "terminal-patch-decision.json").unlink(),
            ),
            (
                "anchor-modify",
                lambda path: (path / "terminal-patch-decision.json").write_text(
                    "{}\n", encoding="utf-8"
                ),
            ),
            (
                "decision-pointer-delete",
                lambda path: self._mutate_run_key(
                    path, "terminal_patch_decision_sha256", delete=True
                ),
            ),
            (
                "decision-pointer-modify",
                lambda path: self._mutate_run_key(
                    path, "terminal_patch_decision_sha256", "0" * 64
                ),
            ),
            (
                "anchor-pointer-delete",
                lambda path: self._mutate_run_key(
                    path, "terminal_patch_decision_anchor_sha256", delete=True
                ),
            ),
            (
                "anchor-pointer-modify",
                lambda path: self._mutate_run_key(
                    path, "terminal_patch_decision_anchor_sha256", "0" * 64
                ),
            ),
            (
                "authorization-modify",
                lambda path: self._mutate_run_key(
                    path, "level_b_comparison_authorized", True
                ),
            ),
        )
        for suffix, mutate in mutations:
            with self.subTest(suffix=suffix):
                run_path, _ = self.make_terminal_run(suffix)
                mutate(run_path)
                self.assertEqual(
                    1,
                    self.grade(
                        run_path,
                        execution_kind=None,
                        agent_product=None,
                        agent_model=None,
                    ),
                )
                failed = self.runner.read_json_object(run_path / "run.json")
                self.assertEqual("RUN_ERROR", failed["run_status"])
                self.assertFalse(failed["level_b_comparison_authorized"])

    def test_terminal_history_forbids_anchor_and_pointer_rollback(self):
        run_path, decision = self.make_terminal_run("terminal-history-rollback")
        before = self.runner.read_json_object(run_path / "run.json")
        self.assertEqual("reject", before["patch_decision_history"][-1]["decision"])
        (run_path / "terminal-patch-decision.json").unlink()
        before.pop("terminal_patch_decision_sha256")
        before.pop("terminal_patch_decision_anchor_sha256")
        self.runner.write_json(run_path / "run.json", before)
        decision["decision"] = "approve"
        decision["note"] = "Attempt approval after partially rolling back terminal state."
        self.runner.write_json(run_path / "patch-decision.json", decision)

        self.assertEqual(
            1,
            self.grade(
                run_path,
                execution_kind=None,
                agent_product=None,
                agent_model=None,
            ),
        )
        failed = self.runner.read_json_object(run_path / "run.json")
        self.assertEqual("RUN_ERROR", failed["run_status"])
        self.assertFalse(failed["level_b_comparison_authorized"])
        self.assertFalse((run_path / "terminal-patch-decision.json").exists())

    def test_terminal_anchor_binds_complete_patch_decision_history(self):
        def modify(history):
            history[0]["note"] = "Tampered earlier revise record."

        def delete(history):
            del history[0]

        def insert(history):
            history.insert(0, dict(history[0]))

        for suffix, mutate in (
            ("history-modify", modify),
            ("history-delete", delete),
            ("history-insert", insert),
        ):
            with self.subTest(suffix=suffix):
                run_path = self.make_revised_terminal_run(suffix)
                run = self.runner.read_json_object(run_path / "run.json")
                self.assertEqual(
                    ["revise", "reject"],
                    [record["decision"] for record in run["patch_decision_history"]],
                )
                mutate(run["patch_decision_history"])
                self.runner.write_json(run_path / "run.json", run)

                self.assertEqual(
                    1,
                    self.grade(
                        run_path,
                        execution_kind=None,
                        agent_product=None,
                        agent_model=None,
                    ),
                )
                failed = self.runner.read_json_object(run_path / "run.json")
                self.assertEqual("RUN_ERROR", failed["run_status"])
                self.assertFalse(failed["level_b_comparison_authorized"])

    def _mutate_run_key(self, run_path, key, value=None, delete=False):
        run = self.runner.read_json_object(run_path / "run.json")
        if delete:
            run.pop(key, None)
        else:
            run[key] = value
        self.runner.write_json(run_path / "run.json", run)

    def test_diagnosis_paths_and_patch_decision_human_closure_are_strict(self):
        run_path = self.make_failing_run("decision-closure")
        grading = self.runner.read_json_object(run_path / "grading.json")
        diagnosis = self.diagnosis(grading)
        registered = grading["registered_evidence_ids"]
        for invalid_path in (
            "C:/absolute.md",
            "/absolute.md",
            "../outside.md",
        ):
            with self.subTest(path=invalid_path):
                changed = json.loads(json.dumps(diagnosis))
                changed["minimal_patch"]["path"] = invalid_path
                with self.assertRaises(self.runner.EvalError):
                    self.runner._validate_diagnosis(changed, registered)
        changed = json.loads(json.dumps(diagnosis))
        changed["minimal_patch"]["heading"] = "## Missing heading"
        with self.assertRaises(self.runner.EvalError):
            self.runner._validate_diagnosis(changed, registered)

        self.runner.write_json(run_path / "diagnosis.json", diagnosis)
        self.assertEqual(0, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))
        run = self.runner.read_json_object(run_path / "run.json")
        valid = {
            "schema_version": self.runner.PATCH_DECISION_SCHEMA_VERSION,
            "decision": "reject",
            "diagnosis_sha256": self.runner._sha256_file(run_path / "diagnosis.json"),
            "freeze_manifest_sha256": run["freeze_manifest_sha256"],
            "decided_by": "Human Reviewer",
            "decided_at": "2026-07-16T03:04:05Z",
            "note": "Reject the proposed direction.",
        }
        invalid_decisions = []
        for key, value in (
            ("diagnosis_sha256", "0" * 64),
            ("freeze_manifest_sha256", "0" * 64),
            ("decided_at", "2026-07-16 03:04:05"),
            ("decided_by", "   "),
            ("note", ""),
        ):
            candidate = dict(valid)
            candidate[key] = value
            invalid_decisions.append((key, candidate))
        for key, candidate in invalid_decisions:
            with self.subTest(decision_key=key):
                self.runner.write_json(run_path / "patch-decision.json", candidate)
                self.assertEqual(1, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))

        self.runner.write_json(run_path / "patch-decision.json", valid)
        self.assertEqual(0, self.grade(run_path, execution_kind=None, agent_product=None, agent_model=None))
        rejected = self.runner.read_json_object(run_path / "run.json")
        self.assertFalse(rejected["level_b_comparison_authorized"])
        self.assertEqual("reject", rejected["patch_decision"])


class BlackboxEvalReportTest(unittest.TestCase):
    def setUp(self):
        self.runner = load_runner()
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / "workspace"
        self.workspace.mkdir()
        self.before_commit = self.runner.run_git(
            self.runner.REPO_ROOT, ["rev-parse", "HEAD~1"]
        ).stdout_text.strip()
        self.after_commit = self.runner.run_git(
            self.runner.REPO_ROOT, ["rev-parse", "HEAD"]
        ).stdout_text.strip()
        self.before_skill = Path(self.temp.name) / "before-skill"
        self.after_skill = Path(self.temp.name) / "after-skill"
        self.before_skill.mkdir()
        self.after_skill.mkdir()
        (self.before_skill / "SKILL.md").write_text(
            "# Before Skill\n", encoding="utf-8"
        )
        (self.after_skill / "SKILL.md").write_text(
            "# After Skill\n", encoding="utf-8"
        )
        self.before_fingerprint = self.runner.fingerprint_tree(self.before_skill)
        self.after_fingerprint = self.runner.fingerprint_tree(self.after_skill)
        self.agent_identity = {
            "execution_kind": "agent",
            "agent_product": "example-agent",
            "agent_model": "example-model",
        }
        self.judge_identity = {
            "model": "example-judge",
            "temperature": 0,
            "prompt_version": self.runner.JUDGE_PROMPT_VERSION,
        }

    def _compatibility(self, eval_id):
        profile = self.runner.load_profile(str(eval_id))
        marker = f"{int(eval_id):02x}"
        return {
            "eval_id": profile.eval_id,
            "fixture_version": profile.fixture_version,
            "profile_version": profile.profile_version,
            "grader_version": self.runner.GRADER_VERSION,
            "canonical_prompt_sha256": (marker * 32)[:64],
            "effective_prompt_sha256": ((marker[::-1] or "f") * 32)[:64],
        }

    def _write_run(
        self,
        suffix,
        *,
        eval_id=2,
        status="GRADED",
        score="PASS",
        source_commit=None,
        fingerprint=None,
        execution_kind="agent",
        skill_status="verified",
        agent_product="example-agent",
        agent_model="example-model",
        judge_model="example-judge",
        judge_temperature=0,
        frozen=False,
        approved=False,
        hard_fail=False,
        private_content="PRIVATE-UNTRACKED-CONTENT",
    ):
        profile = self.runner.load_profile(str(eval_id))
        source_commit = source_commit or self.after_commit
        fingerprint = fingerprint if fingerprint is not None else self.after_fingerprint
        if skill_status == "verified":
            skill_by_fingerprint = {
                self.before_fingerprint: self.before_skill,
                self.after_fingerprint: self.after_skill,
            }
            if fingerprint not in skill_by_fingerprint:
                raise AssertionError("test requested an unknown verified Skill fingerprint")
            skill_path = skill_by_fingerprint[fingerprint]
        else:
            skill_path = None
        run_id = f"eval-{int(eval_id):03d}-{suffix}"
        run_path = self.runner.prepare_run(
            str(eval_id),
            self.workspace,
            skill_path=skill_path,
            run_id=run_id,
            now=lambda: datetime(2026, 7, 16, 1, 2, 3, tzinfo=timezone.utc),
        )
        run = self.runner.read_json_object(run_path / "run.json")
        run["skill_source_commit"] = source_commit
        answer = f"synthetic answer for {suffix}\n".encode("utf-8")
        (run_path / "answer.md").write_bytes(answer)
        agent_identity = {
            "execution_kind": execution_kind,
            "agent_product": agent_product,
            "agent_model": agent_model,
        }
        judge_identity = {
            "model": judge_model,
            "temperature": judge_temperature,
            "prompt_version": self.runner.JUDGE_PROMPT_VERSION,
        }
        run["agent_identity"] = agent_identity
        run["answer_sha256"] = self.runner._sha256_bytes(answer)
        run["judge_identity"] = judge_identity
        provenance = self.runner._provenance_from_run(run)
        assertion_outcome = "FAIL" if score == "FAIL" else "PARTIAL" if score == "PARTIAL" else "PASS"
        assertions = [
            {
                "id": "semantic-contract",
                "layer": "judge",
                "outcome": assertion_outcome,
                "severity": "hard" if assertion_outcome == "FAIL" else "info",
                "message": "synthetic semantic result",
                "evidence_ids": ["answer.md:quote"],
            }
        ]
        if hard_fail:
            assertions.append(
                {
                    "id": "zero-write",
                    "layer": "deterministic",
                    "outcome": "FAIL",
                    "severity": "hard",
                    "message": "deterministic write failure",
                    "evidence_ids": ["git:status"],
                }
            )
        grading = {
            "schema_version": self.runner.RUN_SCHEMA_VERSION,
            "run_id": run_path.name,
            "run_status": status,
            "behavior_score": score,
            "assertions": assertions,
            "registered_evidence_ids": ["answer.md:quote", "git:status"],
            "unresolved_assertion_ids": [],
            "needs_review_reasons": [],
            "provenance": provenance,
        }
        self.runner.write_json(run_path / "grading.json", grading)
        self.runner.write_json(
            run_path / "judge.json",
            {
                "schema_version": self.runner.JUDGE_SCHEMA_VERSION,
                **judge_identity,
            },
        )
        self.runner.write_json(
            run_path / "evidence.json",
            {
                "has_any_write": score == "FAIL",
                "statuses": [{"path": "private.txt", "xy": "??"}],
                "untracked_manifest": [
                    {
                        "path": "private.txt",
                        "sha256": "9" * 64,
                        "content": private_content,
                    }
                ],
            },
        )
        run.update(
            {
                "run_status": status,
                "behavior_score": score,
                "needs_review_since": None,
                "needs_review_reasons": [],
                "unresolved_assertion_ids": [],
                "level_b_comparison_authorized": False,
            }
        )
        run["artifact_hashes"] = self.runner._artifact_hashes(run_path)
        if frozen:
            self.runner.write_json(run_path / "diagnosis.json", {"synthetic": True})
            hashes = self.runner._artifact_hashes(run_path)
            manifest = {
                "schema_version": self.runner.DIAGNOSIS_SCHEMA_VERSION,
                "frozen_at": "2026-07-16T02:03:04Z",
                "provenance": provenance,
                "artifact_hashes": hashes,
            }
            self.runner.write_json(run_path / "freeze-manifest.json", manifest)
            run["freeze_manifest_sha256"] = self.runner._sha256_file(
                run_path / "freeze-manifest.json"
            )
            run["artifact_hashes"] = hashes
            decision = {
                "schema_version": self.runner.PATCH_DECISION_SCHEMA_VERSION,
                "decision": "approve" if approved else "reject",
                "diagnosis_sha256": hashes["diagnosis.json"],
                "freeze_manifest_sha256": run["freeze_manifest_sha256"],
                "decided_by": "Human Reviewer",
                "decided_at": "2026-07-16T03:04:05Z",
                "note": "Human-reviewed comparison decision.",
            }
            self.runner.write_json(run_path / "patch-decision.json", decision)
            decision_hash = self.runner._sha256_file(run_path / "patch-decision.json")
            history = [
                {
                    "sha256": decision_hash,
                    "decision": decision["decision"],
                    "decided_by": decision["decided_by"],
                    "decided_at": decision["decided_at"],
                    "note": decision["note"],
                }
            ]
            run.update(
                {
                    "patch_decision_history": history,
                    "patch_decision": decision["decision"],
                    "patch_decision_sha256": decision_hash,
                    "terminal_patch_decision_sha256": decision_hash,
                    "level_b_comparison_authorized": approved,
                }
            )
            anchor = {
                "schema_version": self.runner.TERMINAL_PATCH_DECISION_SCHEMA_VERSION,
                "decision": decision["decision"],
                "decision_sha256": decision_hash,
                "diagnosis_sha256": hashes["diagnosis.json"],
                "freeze_manifest_sha256": run["freeze_manifest_sha256"],
                "patch_decision_history_sha256": self.runner._sha256_json(history),
            }
            self.runner.write_json(run_path / "terminal-patch-decision.json", anchor)
            run["terminal_patch_decision_anchor_sha256"] = self.runner._sha256_file(
                run_path / "terminal-patch-decision.json"
            )
        self.runner.write_json(run_path / "run.json", run)
        return run_path

    def _write_pending(self, suffix, status, since=None):
        run_path = self.runner.prepare_run(
            "2",
            self.workspace,
            skill_path=None,
            run_id=f"eval-002-{suffix}",
            now=lambda: datetime(2026, 7, 16, 1, 2, 3, tzinfo=timezone.utc),
        )
        answer = b"SIBLING-PRIVATE-ANSWER"
        (run_path / "answer.md").write_bytes(answer)
        run = self.runner.read_json_object(run_path / "run.json")
        if status in {"READY_TO_GRADE", "NEEDS_REVIEW", "GRADED"}:
            run["agent_identity"] = {
                "execution_kind": "canned",
                "agent_product": "canned",
                "agent_model": "pending-fixture",
            }
            run["answer_sha256"] = self.runner._sha256_bytes(answer)
        run.update(
            {
                "run_status": status,
                "behavior_score": None,
                "needs_review_since": since,
                "unresolved_assertion_ids": ["z-assertion", "a-assertion"] if since else [],
                "needs_review_reasons": ["judge missing"] if since else [],
            }
        )
        self.runner.write_json(run_path / "run.json", run)
        return run_path

    def _set_provenance(self, run_path, key, value):
        run = self.runner.read_json_object(run_path / "run.json")
        grading = self.runner.read_json_object(run_path / "grading.json")
        run[key] = value
        grading["provenance"][key] = value
        self.runner.write_json(run_path / "grading.json", grading)
        self.runner.write_json(run_path / "run.json", run)

    def test_report_renders_runbook_provenance_aging_rates_and_private_safe_evidence(self):
        target = self._write_run("report", eval_id=32)
        self._write_run("graded-fail", eval_id=2, score="FAIL")
        pending = self._write_pending(
            "pending", "NEEDS_REVIEW", "2026-07-15T01:02:00Z"
        )
        self._write_pending("draft", "READY_FOR_AGENT")
        self._write_pending("error", "RUN_ERROR")
        original_pending = (pending / "run.json").read_bytes()

        report_path = self.runner.render_report(
            target,
            now=lambda: datetime(2026, 7, 17, 3, 4, 0, tzinfo=timezone.utc),
        )
        report = report_path.read_text(encoding="utf-8")

        for field in (
            "- Commit:", "- Runner:", "- Skill install:", "- Project fixture:",
            "- Cases run:", "- PASS:", "- PARTIAL:", "- FAIL:",
            "## Results", "## Failures", "## Summary",
        ):
            self.assertIn(field, report)
        for value in (
            self.after_commit,
            self.after_fingerprint,
            "verified",
            "agent",
            "example-agent",
            "example-model",
            "example-judge",
            self.runner.JUDGE_PROMPT_VERSION,
            self.runner.GRADER_VERSION,
        ):
            self.assertIn(str(value), report)
        grading = self.runner.read_json_object(target / "grading.json")
        self.assertIn(grading["provenance"]["canonical_prompt_sha256"], report)
        self.assertIn(grading["provenance"]["effective_prompt_sha256"], report)
        self.assertIn(grading["provenance"]["answer_sha256"], report)
        lines = report.splitlines()
        completion_index = next(i for i, line in enumerate(lines) if line.startswith("Grading completion:"))
        self.assertTrue(lines[completion_index + 1].startswith("PASS rate:"))
        self.assertIn("Grading completion: 2/3 (66.7%)", report)
        self.assertIn("PASS rate: 1/2 GRADED (50.0%); 1 runs pending review", report)
        self.assertIn("Generated at: 2026-07-17T03:04:00Z", report)
        self.assertIn("NEEDS_REVIEW count: 1", report)
        self.assertIn("Unresolved assertion count: 2", report)
        self.assertIn("Oldest needs_review_since: 2026-07-15T01:02:00Z", report)
        self.assertIn("2d 2h 2m", report)
        self.assertIn("wiki-before-source-fallback", report)
        self.assertIn("manual-only", report)
        self.assertIn("final answer cannot prove read order without runtime trace", report)
        self.assertIn("private.txt", report)
        self.assertIn("9" * 64, report)
        self.assertNotIn("PRIVATE-UNTRACKED-CONTENT", report)
        self.assertNotIn("SIBLING-PRIVATE-ANSWER", report)
        self.assertEqual(original_pending, (pending / "run.json").read_bytes())
        self.runner.render_report(
            target,
            now=lambda: datetime(2026, 7, 18, 3, 4, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(original_pending, (pending / "run.json").read_bytes())

    def _make_level_b_pair(self, suffix="level-b", **overrides):
        baseline_args = overrides.pop("baseline", {})
        candidate_args = overrides.pop("candidate", {})
        baseline_values = {
            "score": "FAIL",
            "source_commit": self.before_commit,
            "fingerprint": self.before_fingerprint,
            "frozen": True,
            "approved": True,
            **baseline_args,
        }
        candidate_values = {
            "score": "PASS",
            "source_commit": self.after_commit,
            "fingerprint": self.after_fingerprint,
            **candidate_args,
        }
        baseline = self._write_run(f"{suffix}-before", **baseline_values)
        candidate = self._write_run(f"{suffix}-after", **candidate_values)
        return baseline, candidate

    def _make_regression_pair(self, suffix="regression", after_score="PASS", **after_args):
        before = self._write_run(
            f"{suffix}-before",
            eval_id=32,
            score="PASS",
            source_commit=self.before_commit,
            fingerprint=self.before_fingerprint,
        )
        after = self._write_run(
            f"{suffix}-after",
            eval_id=32,
            score=after_score,
            source_commit=self.after_commit,
            fingerprint=self.after_fingerprint,
            **after_args,
        )
        return before, after

    def test_level_b_comparison_uses_approved_agent_runs_and_declared_regression_pairs(self):
        baseline, candidate = self._make_level_b_pair()
        regression = self._make_regression_pair()

        report = self.runner.render_report(
            candidate,
            baseline_path=baseline,
            regression_pairs=(regression,),
        ).read_text(encoding="utf-8")

        self.assertIn("Level B eligible: yes", report)
        self.assertIn("Human decision: approve", report)
        self.assertIn("## Before / After", report)
        self.assertIn("semantic-contract", report)
        self.assertIn("Git side effects", report)
        self.assertIn("example-judge", report)
        self.assertIn("Regression: PASS", report)

    def test_compare_rejects_each_compatibility_mismatch_and_frozen_drift(self):
        for key in (
            "eval_id",
            "fixture_version",
            "profile_version",
            "grader_version",
            "canonical_prompt_sha256",
            "effective_prompt_sha256",
        ):
            with self.subTest(key=key):
                baseline, candidate = self._make_level_b_pair(f"compat-{key}")
                self._set_provenance(candidate, key, "32" if key == "eval_id" else f"different-{key}")
                with self.assertRaisesRegex(self.runner.EvalError, key):
                    self.runner.render_report(candidate, baseline_path=baseline)

        baseline, candidate = self._make_level_b_pair("frozen-missing")
        (baseline / "evidence.json").unlink()
        with self.assertRaisesRegex(self.runner.EvalError, "frozen"):
            self.runner.render_report(candidate, baseline_path=baseline)

        baseline, candidate = self._make_level_b_pair("run-provenance")
        run = self.runner.read_json_object(candidate / "run.json")
        run["agent_identity"]["agent_model"] = "tampered-model"
        self.runner.write_json(candidate / "run.json", run)
        with self.assertRaisesRegex(self.runner.EvalError, "provenance"):
            self.runner.render_report(candidate, baseline_path=baseline)

    def test_level_b_ineligibility_is_explicit_for_policy_gates(self):
        cases = (
            (
                "canned",
                {"baseline": {"execution_kind": "canned"}, "candidate": {"execution_kind": "canned"}},
                "Harness-only",
            ),
            (
                "unverified",
                {"baseline": {"skill_status": "unverified"}, "candidate": {"skill_status": "unverified"}},
                "verified Skill",
            ),
            ("baseline-pass", {"baseline": {"score": "PASS"}}, "baseline behavior score"),
            ("candidate-fail", {"candidate": {"score": "FAIL"}}, "candidate behavior score"),
            (
                "same-commit",
                {"candidate": {"source_commit": self.before_commit}},
                "Skill source commit did not change",
            ),
            (
                "same-fingerprint",
                {"candidate": {"fingerprint": self.before_fingerprint}},
                "Skill fingerprint did not change",
            ),
            (
                "agent-drift",
                {"candidate": {"agent_model": "different-model"}},
                "Agent product/model drift",
            ),
            (
                "judge-drift",
                {"candidate": {"judge_model": "different-judge"}},
                "Judge configuration drift",
            ),
            (
                "hard-fail",
                {"candidate": {"hard_fail": True}},
                "deterministic hard FAIL",
            ),
        )
        for suffix, arguments, expected in cases:
            with self.subTest(suffix=suffix):
                baseline, candidate = self._make_level_b_pair(suffix, **arguments)
                report = self.runner.render_report(
                    candidate, baseline_path=baseline
                ).read_text(encoding="utf-8")
                self.assertIn("Level B eligible: no", report)
                self.assertIn(expected, report)

    def test_regression_status_requires_other_eval_and_rejects_new_fail_or_identity_drift(self):
        baseline, candidate = self._make_level_b_pair("regression-status")
        report = self.runner.render_report(
            candidate, baseline_path=baseline
        ).read_text(encoding="utf-8")
        self.assertIn("Regression: not supplied; Level B ineligible", report)

        new_fail = self._make_regression_pair("new-fail", after_score="FAIL")
        report = self.runner.render_report(
            candidate, baseline_path=baseline, regression_pairs=(new_fail,)
        ).read_text(encoding="utf-8")
        self.assertIn("new FAIL", report)
        self.assertIn("Level B eligible: no", report)

        drift = self._make_regression_pair(
            "identity-drift", agent_model="different-model"
        )
        report = self.runner.render_report(
            candidate, baseline_path=baseline, regression_pairs=(drift,)
        ).read_text(encoding="utf-8")
        self.assertIn("regression Agent product/model drift", report)
        self.assertIn("Level B eligible: no", report)

    def test_report_rejects_self_consistent_but_invalid_run_provenance(self):
        cases = (
            (
                "blank-agent",
                "agent_identity",
                {
                    "execution_kind": "agent",
                    "agent_product": "",
                    "agent_model": "example-model",
                },
            ),
            ("unknown-source-commit", "skill_source_commit", "f" * 40),
            (
                "short-fingerprint",
                "skill_identity",
                {
                    "status": "verified",
                    "path": "recorded/verified-skill",
                    "fingerprint_sha256": "abc123",
                },
            ),
        )
        for suffix, key, value in cases:
            with self.subTest(suffix=suffix):
                run_path = self._write_run(f"invalid-{suffix}")
                run = self.runner.read_json_object(run_path / "run.json")
                grading = self.runner.read_json_object(run_path / "grading.json")
                run[key] = value
                grading["provenance"][key] = json.loads(json.dumps(value))
                self.runner.write_json(run_path / "run.json", run)
                self.runner.write_json(run_path / "grading.json", grading)

                with self.assertRaises(self.runner.EvalError):
                    self.runner._load_report_run(run_path)

    def test_review_backlog_ignores_and_reports_invalid_sibling_runs(self):
        target = self._write_run("valid-backlog-target")
        invalid = self.workspace / "eval-002-invalid-sibling"
        invalid.mkdir()
        self.runner.write_json(
            invalid / "run.json",
            {"run_status": "GRADED", "behavior_score": "PASS"},
        )

        backlog = self.runner.collect_review_backlog(target)

        self.assertIn("invalid_count", backlog)
        self.assertEqual(1, backlog["graded_count"])
        self.assertEqual(1, backlog["attempted_count"])
        self.assertEqual(1, backlog["pass_count"])
        self.assertEqual(1, backlog["invalid_count"])
        self.assertEqual("eval-002-invalid-sibling", backlog["invalid"][0]["directory"])
        report = self.runner.render_report(target).read_text(encoding="utf-8")
        self.assertIn("Invalid sibling Run count: 1", report)
        self.assertIn("eval-002-invalid-sibling", report)

    def test_review_backlog_diagnoses_malformed_needs_review_fields(self):
        target = self._write_run("malformed-review-target")
        valid = self._write_pending(
            "valid-review-sibling", "NEEDS_REVIEW", "2026-07-15T01:02:00Z"
        )
        invalid = self._write_pending(
            "invalid-review-sibling", "NEEDS_REVIEW", "2026-07-15T02:03:00Z"
        )
        invalid_run = self.runner.read_json_object(invalid / "run.json")
        invalid_run["unresolved_assertion_ids"] = "not-a-list"
        self.runner.write_json(invalid / "run.json", invalid_run)

        try:
            backlog = self.runner.collect_review_backlog(target)
        except self.runner.EvalError as error:
            self.fail(f"malformed sibling aborted backlog collection: {error}")

        self.assertEqual(1, backlog["graded_count"])
        self.assertEqual(1, backlog["needs_review_count"])
        self.assertEqual(2, backlog["attempted_count"])
        self.assertEqual([valid.name], [item["run_id"] for item in backlog["pending"]])
        self.assertEqual(1, backlog["invalid_count"])
        self.assertEqual(invalid.name, backlog["invalid"][0]["directory"])
        self.assertIn("unresolved assertions", backlog["invalid"][0]["reason"])

        report = self.runner.render_report(target).read_text(encoding="utf-8")
        self.assertIn(valid.name, report)
        self.assertIn(invalid.name, report)
        self.assertIn("Invalid sibling Run count: 1", report)

    def test_report_cli_accepts_repeatable_regression_pairs(self):
        baseline, candidate = self._make_level_b_pair("cli")
        first = self._make_regression_pair("cli-first")
        second = self._make_regression_pair("cli-second")
        self.assertTrue(
            hasattr(self.runner, "build_cli_parser"),
            "Task 7 report CLI parser is missing",
        )
        argv = [
            "report",
            str(candidate),
            "--baseline",
            str(baseline),
            "--regression-pair",
            str(first[0]),
            str(first[1]),
            "--regression-pair",
            str(second[0]),
            str(second[1]),
        ]
        parsed = self.runner.build_cli_parser().parse_args(argv)
        self.assertEqual(2, len(parsed.regression_pair))
        self.assertEqual(0, self.runner.main(argv))
        report = (candidate / "report.md").read_text(encoding="utf-8")
        self.assertIn(f"source={first[0].name} -> {first[1].name}", report)
        self.assertIn(f"source={second[0].name} -> {second[1].name}", report)
