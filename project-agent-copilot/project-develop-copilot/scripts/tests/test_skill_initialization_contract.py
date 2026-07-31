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
    BOOTSTRAP_STAGES = {
        "project-base-init",
        "project-init",
    }
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
    SPECIALIZED_STAGES = {
        "llm-wiki-doctor",
        "project-query",
        "project-review",
        "project-session-extract",
        "project-task-dispatch",
    }
    MECHANICAL_STAGES = {
        "project-graph-visualize",
    }

    def test_every_child_skill_has_an_initialization_policy_classification(self):
        discovered = {
            skill_path.parent.name for skill_path in SKILL_ROOT.glob("*/SKILL.md")
        }
        required = (
            self.BOOTSTRAP_STAGES
            | set(self.STATEFUL_STAGES)
            | self.SPECIALIZED_STAGES
            | self.MECHANICAL_STAGES
        )
        self.assertSetEqual(discovered, required)

    def test_router_runs_initialization_gate_before_lifecycle_session(self):
        router = read("SKILL.md")
        gate = section(router, "## Initialization Gate")
        for token in (
            "`wiki_required_for: full-lifecycle-or-wiki-backed`",
            "`on_missing_wiki: route project-init`",
            "`pending_intent`",
            "`pending_primary_stage`",
            "`missing_wiki_bootstrap_mode: automatic-minimal`",
            "`explicit_no_write_missing_wiki: confirm-before-init`",
        ):
            with self.subTest(token=token):
                self.assertIn(token, gate)
        self.assertTrue(
            "`excluded_mode: lightweight-answer`" in gate
            or "`excluded_mode: lightweight-answer-or-mechanical-artifact`" in gate
        )

        first_check = section(router, "## Required First Check")
        self.assertIn(
            "If full lifecycle or any wiki-backed route applies, resolve",
            first_check,
        )
        first_check_lower = first_check.lower()
        self.assertLess(
            first_check_lower.index("run the initialization gate"),
            first_check_lower.index("create or resume a lifecycle session"),
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
            "`missing_wiki_bootstrap_mode: automatic-minimal`",
            "`explicit_no_write_missing_wiki: confirm-before-init`",
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
        self.assertIn("bootstrap_mode: automatic-minimal", gate)
        self.assertIn("current_gate: Initialization Gate", gate)
        self.assertIn(
            "`direct_invocation_missing_wiki: dispatch-project-init`",
            gate,
        )
        self.assertIn(
            "internal routing message, not a terminal user-facing response",
            gate,
        )
        self.assertIn(
            "continue through `project-init` in the same turn",
            gate,
        )

    def test_wiki_query_and_lifecycle_review_have_narrow_read_only_boundary(self):
        query_gate = section(read("project-query/SKILL.md"), "## Initialization Gate")
        self.assertIn("`on_missing_wiki: route project-init`", query_gate)
        self.assertIn("`source-only_without_wiki: lightweight-answer`", query_gate)
        self.assertIn(
            "`explicit_no_write_missing_wiki: confirm-before-init`",
            query_gate,
        )
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

    def test_graph_visualizer_is_a_mechanical_artifact_route(self):
        router = read("SKILL.md")
        self.assertIn(
            "`excluded_mode: lightweight-answer-or-mechanical-artifact`",
            section(router, "## Initialization Gate"),
        )
        self.assertIn(
            "| User asks to generate, refresh, rebuild, preview, or validate "
            "Base Graph / Project Graph `graph.html` or another interactive graph "
            "HTML | mechanical-artifact | `project-graph-visualize` |",
            section(router, "## Mode / Entry Selection"),
        )
        self.assertIn(
            "`mechanical-artifact` routes such as `project-graph-visualize`",
            section(router, "## Boundaries"),
        )

        visualizer = read("project-graph-visualize/SKILL.md")
        mechanical = section(visualizer, "## Mechanical generation mode")
        self.assertIn("Do not create Change Brief", mechanical)
        self.assertIn("Do not commit unless the user explicitly asks", mechanical)
        self.assertIn(
            "Allowed writes:\n\n- the requested HTML output only.",
            section(visualizer, "## Write boundary"),
        )
        self.assertIn(
            '"graph_role": "base"',
            section(visualizer, "## Preconditions"),
        )

        required_files = {
            "SKILL.md",
            "assets/template.html",
            "evals/evals.json",
            "scripts/build-graph-visualization.ps1",
            "scripts/GraphVisualization.psm1",
            "scripts/validate-graph-visualization.ps1",
            "tests/skill-smoke.Tests.ps1",
        }
        visualizer_root = SKILL_ROOT / "project-graph-visualize"
        actual_files = {
            path.relative_to(visualizer_root).as_posix()
            for path in visualizer_root.rglob("*")
            if path.is_file()
        }
        self.assertSetEqual(actual_files, required_files)

    def test_doctor_refuses_missing_wiki_with_bootstrap_handoff(self):
        gate = section(read("llm-wiki-doctor/SKILL.md"), "## Initialization Gate")
        self.assertIn("`wiki_required: true`", gate)
        self.assertIn("`on_missing_wiki: route project-init`", gate)
        self.assertIn("`pending_primary_stage: llm-wiki-doctor`", gate)
        self.assertIn("`pending_intent`", gate)
        self.assertIn("Do not run the Doctor", gate)
        self.assertIn(
            "Default read-only diagnosis does not mean the user forbids bootstrap writes",
            gate,
        )
        self.assertIn(
            "Only an explicit no-write constraint pauses for confirmation",
            gate,
        )
        self.assert_bootstrap_handoff(gate, "llm-wiki-doctor")

    def test_session_extract_allows_preview_but_bootstraps_before_writes(self):
        session = read("project-session-extract/SKILL.md")
        gate = section(session, "## Initialization Gate")
        self.assertIn(
            "`wiki_required_for: save-context-digest-or-promote-to-lifecycle`",
            gate,
        )
        self.assertIn(
            "`allowed_without_wiki: brief-candidates-or-draft-context-digest`",
            gate,
        )
        self.assertIn("`on_missing_wiki: route project-init`", gate)
        self.assertIn("`pending_primary_stage: project-session-extract`", gate)
        self.assertIn("`pending_intent`", gate)
        self.assert_bootstrap_handoff(gate, "project-session-extract")

        preview = section(session, "## Without Wiki Preview Boundary")
        self.assertIn("must not write files", preview)
        self.assertIn("must not claim a Session Digest was imported", preview)
        self.assertIn("preserve the candidate selection", preview)

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

    def test_automatic_bootstrap_writes_only_inside_llm_wiki(self):
        init = read("project-init/SKILL.md")
        automatic = section(init, "## Automatic Minimal Bootstrap Mode")
        for token in (
            "`bootstrap_mode: automatic-minimal`",
            "writes only under `<project_root>/.llm-wiki/**`",
            "`.gitignore`",
            "`.pre-commit-config.yaml`",
            "`.github/workflows/llm-wiki-doctor.yml`",
            "`root_integrations_pending`",
        ):
            with self.subTest(token=token):
                self.assertIn(token, automatic)
        self.assertIn(
            "must not create or modify",
            automatic,
        )

        explicit = section(init, "## Explicit Full Init / Refresh Mode")
        self.assertIn("`bootstrap_mode: explicit-full`", explicit)
        self.assertIn(
            "may install or merge the project-root integrations",
            explicit,
        )

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
        self.assertIn("bootstrap_mode: automatic-minimal", eval_case)
        self.assertIn("only under `.llm-wiki/**`", eval_case)
        self.assertIn("`.pre-commit-config.yaml`", eval_case)

        acceptance_case = section(
            acceptance,
            "## Case 37: Uninitialized Business Repository Bootstraps Before Development",
        )
        acceptance_prompt = acceptance_case.split("Fixture:", 1)[0]
        self.assertIn("PROJECT_READ_TIMEOUT_SECONDS", acceptance_prompt)
        self.assertIn("业务代码改动", acceptance_prompt)
        self.assertNotIn(".llm-wiki", acceptance_prompt)
        self.assertNotIn("project init", acceptance_prompt.lower())
        self.assertIn("bootstrap_mode: automatic-minimal", acceptance_case)
        self.assertIn("only under `.llm-wiki/**`", acceptance_case)

    def test_manual_eval_and_acceptance_cover_doctor_and_session_extract_gates(self):
        evals = read("evals/project-develop-copilot-evals.md")
        acceptance = read("references/acceptance-cases.md")

        doctor_eval = section(
            evals,
            "## Eval 34: Uninitialized Repository Bootstraps Before Doctor",
        )
        self.assertIn("pending_primary_stage: llm-wiki-doctor", doctor_eval)
        self.assertIn("bootstrap_stage: project-init", doctor_eval)
        self.assertIn("must not run", doctor_eval)
        self.assertIn("default read-only diagnosis", doctor_eval)
        self.assertIn("explicit no-write constraint", doctor_eval)

        session_eval = section(
            evals,
            "## Eval 35: Session Preview Is Allowed But Save Requires Init",
        )
        self.assertIn("brief-candidates", session_eval)
        self.assertIn("save-context-digest", session_eval)
        self.assertIn("pending_primary_stage: project-session-extract", session_eval)
        self.assertIn("bootstrap_mode: automatic-minimal", session_eval)
        self.assertIn(
            "must not end at the bootstrap handoff",
            session_eval,
        )

        doctor_case = section(
            acceptance,
            "## Case 38: Uninitialized Repository Bootstraps Before Doctor",
        )
        self.assertIn("pending_primary_stage: llm-wiki-doctor", doctor_case)
        self.assertIn("must not run", doctor_case)
        self.assertIn("default read-only diagnosis", doctor_case)
        self.assertIn("explicit no-write constraint", doctor_case)

        session_case = section(
            acceptance,
            "## Case 39: Session Preview Is Allowed But Save Requires Init",
        )
        self.assertIn("brief-candidates", session_case)
        self.assertIn("save-context-digest", session_case)
        self.assertIn("pending_primary_stage: project-session-extract", session_case)
        self.assertIn("bootstrap_mode: automatic-minimal", session_case)
        self.assertIn(
            "must not end at the bootstrap handoff",
            session_case,
        )


if __name__ == "__main__":
    unittest.main()
