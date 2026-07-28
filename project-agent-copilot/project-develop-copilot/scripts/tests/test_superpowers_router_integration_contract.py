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


class SuperpowersRouterIntegrationContractTest(unittest.TestCase):
    def test_uninitialized_project_defers_advisory_bridges_until_pdc_is_ready(self):
        router = read("SKILL.md")
        first_check = section(router, "## Required First Check").lower()
        self.assertLess(
            first_check.index("run the initialization gate"),
            first_check.index("invoke one primary stage skill"),
        )

        bridge_boundary = section(
            read("references/superpowers-bridge.md"),
            "## Boundary",
        )
        self.assertIn(
            "Project Develop Copilot initialization and lifecycle gates take "
            "precedence over Superpowers advisory workflow routing.",
            bridge_boundary,
        )
        self.assertIn(
            "Do not resolve or invoke an advisory workflow Skill before the "
            "Initialization Gate and Context Recovery Gate allow it.",
            bridge_boundary,
        )

    def test_bug_route_scopes_pdc_evidence_before_systematic_debugging(self):
        project_fix = read("project-fix/SKILL.md")
        debugging_rule = section(
            project_fix,
            "## Anti-Corruption Debugging Rule",
        )
        self.assertLess(
            debugging_rule.index("Run Context Recovery Gate."),
            debugging_rule.index(
                "Bridge to systematic-debugging only after evidence and scoped "
                "context are captured."
            ),
        )

        handoff = project_fix[
            project_fix.index("## Context Handoff") :
            project_fix.index("## Return Handoff")
        ]
        for field in (
            "- active_sources:",
            "- active_scope:",
            "- read_only_scope:",
            "- candidate_scope:",
            "- excluded_scope:",
            "- current_gate:",
            "- requested_stage_or_bridge:",
        ):
            with self.subTest(field=field):
                self.assertIn(field, handoff)

        bridge_points = section(
            read("references/superpowers-bridge.md"),
            "## Bridge Points",
        )
        self.assertIn(
            "After bug evidence and scoped context are captured, use "
            "systematic-debugging.",
            bridge_points,
        )

    def test_lightweight_architecture_discussion_creates_no_advisory_artifacts(self):
        router = read("SKILL.md")
        no_child_mode = section(router, "## No Child Skill Mode")
        self.assertIn("Do not call an external bridge skill.", no_child_mode)
        self.assertIn(
            "Do not create Change Brief, Bug Brief, Flow Record, handoff, "
            "artifact registry rows, dashboard updates, or code changes.",
            no_child_mode,
        )

        bridge_boundary = section(
            read("references/superpowers-bridge.md"),
            "## Boundary",
        )
        self.assertIn(
            "When PDC selects `lightweight-answer`, do not invoke brainstorming "
            "and do not create any Superpowers artifact.",
            bridge_boundary,
        )


if __name__ == "__main__":
    unittest.main()
