from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillContractTest(unittest.TestCase):
    expected_files = {
        "templates/shared-baseline.md",
        "templates/project-task-spec.md",
        "templates/handoff.md",
        "references/routing.md",
        "references/task-package-protocol.md",
        "references/development-receipt.md",
        "references/task-control-plane.md",
    }

    def read(self, relative_path: str) -> str:
        path = SKILL_ROOT / relative_path
        self.assertTrue(path.is_file(), f"missing required file: {relative_path}")
        raw = path.read_bytes()
        self.assertFalse(
            raw.startswith(b"\xef\xbb\xbf"),
            f"{relative_path} must not contain a UTF-8 BOM",
        )
        self.assertNotIn(
            b"\r\n",
            raw,
            f"{relative_path} must use LF line endings",
        )
        return raw.decode("utf-8")

    def assert_contains_all(
        self,
        relative_path: str,
        required: tuple[str, ...],
    ) -> str:
        text = self.read(relative_path)
        for item in required:
            self.assertIn(item, text, f"{relative_path} must contain {item!r}")
        return text

    def test_all_templates_and_references_exist_and_are_finished(self) -> None:
        unfinished = re.compile(
            r"\b(?:TODO|TBD|FIXME)\b|implementation incomplete|not ready",
            re.IGNORECASE,
        )
        for relative_path in sorted(self.expected_files):
            with self.subTest(path=relative_path):
                text = self.read(relative_path)
                self.assertIsNone(
                    unfinished.search(text),
                    f"{relative_path} contains an unfinished-work marker",
                )

    def test_shared_baseline_template_is_language_aware_and_concise(self) -> None:
        self.assert_contains_all(
            "templates/shared-baseline.md",
            (
                "# {{shared_title}}",
                "{{objective_heading}}",
                "{{required_outcomes_heading}}",
                "{{non_goals_heading}}",
                "{{participants_and_flow_heading}}",
                "{{shared_contracts_heading}}",
                "{{ownership_heading}}",
                "{{confirmed_decisions_heading}}",
                "{{global_acceptance_heading}}",
                "{{technical_appendix_heading}}",
            ),
        )

    def test_project_task_template_prioritizes_human_readability(self) -> None:
        self.assert_contains_all(
            "templates/project-task-spec.md",
            (
                "# {{task_title}}",
                "{{why_heading}}",
                "{{what_to_do_heading}}",
                "{{what_not_to_do_heading}}",
                "{{context_heading}}",
                "{{interfaces_heading}}",
                "{{execution_heading}}",
                "{{verification_heading}}",
                "{{completion_heading}}",
                "{{deliverables_heading}}",
                "{{technical_appendix_heading}}",
            ),
        )

    def test_handoff_template_keeps_machine_metadata_in_appendix(self) -> None:
        text = self.assert_contains_all(
            "templates/handoff.md",
            (
                "# {{handoff_title}}",
                "{{handoff_summary}}",
                "{{destination_heading}}",
                "{{execution_boundary_heading}}",
                "{{result_heading}}",
                "{{technical_appendix_heading}}",
                "dispatchId",
                "subtaskId",
                "mode",
                "awaitResult",
                "taskKind",
                "routeMode",
                "sessionProject",
                "targetProject",
                "targetWorkdir",
                "currentBranchPolicy",
                "dependencies",
                "deliveryProtocol",
                "expectedOutput",
            ),
        )
        appendix_index = text.index("{{technical_appendix_heading}}")
        for machine_field in (
            "targetProject",
            "targetWorkdir",
            "routeMode",
            "codexProjectId",
        ):
            self.assertGreater(
                text.index(machine_field),
                appendix_index,
                f"{machine_field} must appear only after the technical appendix",
            )

    def test_templates_do_not_leak_authoring_boilerplate(self) -> None:
        forbidden = (
            "Replace every",
            "If a section does not apply",
            "Supported task kinds",
            "Not applicable",
            "Task-kind Instructions",
        )
        for relative_path in (
            "templates/shared-baseline.md",
            "templates/project-task-spec.md",
            "templates/handoff.md",
        ):
            with self.subTest(path=relative_path):
                text = self.read(relative_path)
                for item in forbidden:
                    self.assertNotIn(item, text)

    def test_routing_reference_defines_all_routes_and_local_checkout_policy(self) -> None:
        self.assert_contains_all(
            "references/routing.md",
            (
                "VERIFIED_CODEX_PROJECT",
                "BASE_PATH_FALLBACK",
                "BLOCKED",
                "normalized path",
                "environment.type = local",
                "current checkout",
                "current branch",
                "Do not create a worktree",
                "Do not switch branches",
            ),
        )

    def test_package_protocol_defines_lossless_envelope_and_abort(self) -> None:
        self.assert_contains_all(
            "references/task-package-protocol.md",
            (
                "Lightweight Direct Message",
                "Do not create package files",
                "user's language",
                "Parent Visibility Boundary",
                "child-task transport, not default parent-task display",
                "explicitly requests a full package or audit preview",
                "Human-readable Task Header",
                "# {{parent_task_name}} - {{child_task_name}}",
                "TASK_PACKAGE_BEGIN",
                "appears below it",
                "a semantic mismatch blocks delivery",
                "UTF-8 without BOM",
                "LF line endings",
                "TASK_PACKAGE_BEGIN",
                "DOCUMENT_BEGIN",
                "CHUNK 1/N",
                "DOCUMENT_END",
                "TASK_PACKAGE_END",
                "TASK_PACKAGE_ABORT",
                "bundleChecksum",
                "Do not begin execution",
            ),
        )

    def test_protocol_places_readable_title_before_package_marker(self) -> None:
        text = self.read("references/task-package-protocol.md")
        title_index = text.index("# {{parent_task_name}} - {{child_task_name}}")
        marker_index = text.index("TASK_PACKAGE_BEGIN")
        self.assertLess(title_index, marker_index)

    def test_development_receipt_defines_statuses_commit_and_test_rules(self) -> None:
        self.assert_contains_all(
            "references/development-receipt.md",
            (
                "status: COMPLETED | BLOCKED | FAILED | NO_CHANGE_REQUIRED",
                "project:",
                "target_workdir:",
                "branch:",
                "commits:",
                "changes:",
                "tests:",
                "contract_changes:",
                "artifacts:",
                "blockers:",
                "local commit",
                "No commit is pushed",
                "No cross-project integration tests",
            ),
        )

    def test_task_control_plane_defines_receipt_first_json_envelope(self) -> None:
        self.assert_contains_all(
            "references/task-control-plane.md",
            (
                "TASK_CONTROL_RECEIPT_BEGIN",
                "TASK_CONTROL_RECEIPT_END",
                '"schemaVersion": 1',
                "receipt must be the first content",
                "parse_receipt_text",
                "awaitResult=true",
            ),
        )

    def test_skill_entrypoint_defines_complete_safe_orchestration(self) -> None:
        self.assert_contains_all(
            "SKILL.md",
            (
                "stable design spans two or more projects",
                "Lightweight direct message",
                "Do not generate the",
                "Keep it under 30 lines",
                "Formal package",
                "follows the user's current language",
                "Templates are structural guidance, not literal text",
                "Task Naming and First Line",
                "# <parent task name> - <child task name>",
                "Never start a child prompt with `TASK_PACKAGE_BEGIN`",
                "任务分发测试 - 回复你好",
                "A mismatch between the header and the task body is a",
                "Dispatch is the default",
                "awaitResult=true",
                "Dispatch remains the selected mode",
                "does not require project-local tests or a local commit",
                "Do not force an A/B choice",
                "Do not add a confirmation gate",
                "Full Markdown belongs in the child task",
                "Do not show full Markdown documents",
                "one short sentence",
                "Project Graph",
                "Base Graph",
                "list_projects",
                "VERIFIED_CODEX_PROJECT",
                "BASE_PATH_FALLBACK",
                "target.environment.type = local",
                "current checkout",
                "current branch",
                "Do not create a worktree",
                "Do not switch branches",
                "Do not push",
                "No cross-project integration tests",
                "generate all three complete Markdown documents",
                "create_thread",
                "send_message_to_thread",
                "wait_threads",
                "dependency",
                "local commit",
                "project-local tests",
                "dry-run",
                "must never create a real Codex task",
            ),
        )

    def test_parent_interaction_is_minimal_by_default(self) -> None:
        text = self.read("SKILL.md")
        for required in (
            "objective;",
            "target project and one-line responsibility;",
            "dependency order, only when present;",
            "unresolved decisions or material risks.",
            "Only when explicitly requested",
        ):
            self.assertIn(required, text)
        for obsolete in (
            "A: Dispatch mode (default)",
            "B: Development mode",
            "every complete document for every child",
            "one batch confirmation",
            "authorized only after",
        ):
            self.assertNotIn(obsolete, text)

    def test_skill_entrypoint_links_progressive_disclosure_resources(self) -> None:
        self.assert_contains_all(
            "SKILL.md",
            (
                "templates/shared-baseline.md",
                "templates/project-task-spec.md",
                "templates/handoff.md",
                "references/routing.md",
                "references/task-package-protocol.md",
                "references/development-receipt.md",
                "scripts/task_package.py",
                "scripts/task_control.py",
                "references/task-control-plane.md",
            ),
        )


if __name__ == "__main__":
    unittest.main()
