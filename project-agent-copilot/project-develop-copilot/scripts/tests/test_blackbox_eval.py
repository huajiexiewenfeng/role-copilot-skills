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
