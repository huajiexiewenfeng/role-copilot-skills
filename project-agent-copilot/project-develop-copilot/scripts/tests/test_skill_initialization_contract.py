import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]


def read(relative_path: str) -> str:
    return (SKILL_ROOT / relative_path).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        raise AssertionError(f"missing section: {heading}")
    body_start = start + len(heading)
    next_heading = text.find("\n## ", body_start)
    return text[body_start:] if next_heading < 0 else text[body_start:next_heading]


class SkillInitializationContractTest(unittest.TestCase):
    STATEFUL_STAGES = {
        "project-develop": "project-develop/SKILL.md",
        "project-fix": "project-fix/SKILL.md",
        "project-ingest": "project-ingest/SKILL.md",
        "project-finish": "project-finish/SKILL.md",
        "project-maintain": "project-maintain/SKILL.md",
        "project-graph-candidates-scan": "project-graph-candidates-scan/SKILL.md",
        "project-graph-auto-edge": "project-graph-auto-edge/SKILL.md",
        "project-graph-human-edge": "project-graph-human-edge/SKILL.md",
    }

    def test_router_runs_initialization_gate_before_lifecycle_session(self):
        router = read("SKILL.md")
        gate = section(router, "## Initialization Gate")
        for token in (
            "`wiki_required_for: full-lifecycle-or-wiki-backed`",
            "`on_missing_wiki: route project-init`",
            "`pending_intent`",
            "`pending_primary_stage`",
            "`excluded_mode: lightweight-answer`",
            "`read_only_missing_wiki: confirm-before-init`",
        ):
            with self.subTest(token=token):
                self.assertIn(token, gate)

        first_check = section(router, "## Required First Check")
        self.assertIn(
            "If full lifecycle or any wiki-backed route applies, resolve",
            first_check,
        )
        self.assertLess(
            first_check.index("Run the Initialization Gate"),
            first_check.index("Create or resume a Lifecycle Session"),
        )
        handoff = router[
            router.index("## Context Handoff") : router.index("## Return Handoff")
        ]
        self.assertIn("- project_root:", handoff)
        self.assertIn("- pending_intent:", handoff)
        self.assertIn("- pending_primary_stage:", handoff)

    def test_lifecycle_router_defines_bootstrap_and_delayed_persistence(self):
        lifecycle = read("references/lifecycle-router.md")
        gate = section(lifecycle, "## Initialization Gate")
        for token in (
            "`wiki_required_for: full-lifecycle-or-wiki-backed`",
            "`on_missing_wiki: route project-init`",
            "`pending_intent`",
            "`pending_primary_stage`",
            "`read_only_missing_wiki: confirm-before-init`",
            "before invoking the pending stage",
            "before creating or resuming lifecycle state",
        ):
            with self.subTest(token=token):
                self.assertIn(token, gate)
        self.assertIn("keep the routing handoff in memory", lifecycle)

    def test_stateful_children_refuse_missing_wiki_direct_invocation(self):
        for stage, relative_path in self.STATEFUL_STAGES.items():
            with self.subTest(stage=stage):
                gate = section(read(relative_path), "## Initialization Gate")
                self.assertIn("`wiki_required: true`", gate)
                self.assertIn("`on_missing_wiki: route project-init`", gate)
                self.assertIn(f"`pending_primary_stage: {stage}`", gate)
                self.assertIn("`pending_intent`", gate)
                self.assertIn("Do not create a partial `.llm-wiki/`", gate)
                self.assert_bootstrap_handoff(gate, stage)

    def assert_bootstrap_handoff(self, gate: str, stage: str):
        self.assertIn("bootstrap_handoff:", gate)
        self.assertIn("project_root:", gate)
        self.assertIn("pending_intent:", gate)
        self.assertIn(f"pending_primary_stage: {stage}", gate)
        self.assertIn("requested_stage_or_bridge: project-init", gate)
        self.assertIn("current_gate: Initialization Gate", gate)

    def test_wiki_query_and_lifecycle_review_have_narrow_read_only_boundary(self):
        query_gate = section(read("project-query/SKILL.md"), "## Initialization Gate")
        self.assertIn("`on_missing_wiki: route project-init`", query_gate)
        self.assertIn("`source-only_without_wiki: lightweight-answer`", query_gate)
        self.assertIn("`read_only_missing_wiki: confirm-before-init`", query_gate)
        self.assert_bootstrap_handoff(query_gate, "project-query")

        review = read("project-review/SKILL.md")
        review_gate = section(review, "## Initialization Gate")
        self.assertIn("`on_missing_wiki: route project-init`", review_gate)
        self.assertIn("`allowed_without_wiki: quick-diff-review`", review_gate)
        self.assertIn("must not claim lifecycle or wiki integrity", review_gate)
        self.assert_bootstrap_handoff(review_gate, "project-review")
        review_exception = section(review, "## Source / Diff Only Review")
        self.assertIn("When `review_mode: quick-diff-review`", review_exception)
        self.assertIn("skip wiki, artifact, dashboard, and Flow Record", review_exception)
        self.assertIn("lifecycle and wiki integrity were not assessed", review_exception)

    def test_project_init_preserves_pending_route_without_overclaiming_readiness(self):
        init = read("project-init/SKILL.md")
        init_contract = section(init, "## Bootstrap Return Contract")
        for token in (
            "`pending_intent`",
            "`pending_primary_stage`",
            "`initialization_level`",
            "`next_gate`",
            "must not automatically invoke",
        ):
            with self.subTest(token=token):
                self.assertIn(token, init_contract)
        self.assertGreaterEqual(init.count("- project_root:"), 2)

    def test_manual_eval_and_acceptance_case_cover_uninitialized_repository(self):
        evals = read("evals/project-develop-copilot-evals.md")
        acceptance = read("references/acceptance-cases.md")
        eval_case = section(
            evals,
            "## Eval 33: Uninitialized Business Repository Bootstraps Before Development",
        )
        eval_prompt = eval_case.split("Fixture:", 1)[0]
        self.assertIn("PROJECT_READ_TIMEOUT_SECONDS", eval_prompt)
        self.assertIn("业务代码改动", eval_prompt)
        self.assertNotIn(".llm-wiki", eval_prompt)
        self.assertNotIn("project init", eval_prompt.lower())
        self.assertIn("bootstrap_stage: project-init", eval_case)
        self.assertIn("pending_primary_stage: project-develop", eval_case)
        self.assertIn(
            "checkpoint_order: root-check -> project-init -> lifecycle-anchor -> implementation",
            eval_case,
        )

        acceptance_case = section(
            acceptance,
            "## Case 37: Uninitialized Business Repository Bootstraps Before Development",
        )
        acceptance_prompt = acceptance_case.split("Fixture:", 1)[0]
        self.assertIn("PROJECT_READ_TIMEOUT_SECONDS", acceptance_prompt)
        self.assertIn("业务代码改动", acceptance_prompt)
        self.assertNotIn(".llm-wiki", acceptance_prompt)
        self.assertNotIn("project init", acceptance_prompt.lower())


if __name__ == "__main__":
    unittest.main()
