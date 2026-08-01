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

    def test_shared_baseline_template_has_complete_cross_project_contract(self) -> None:
        self.assert_contains_all(
            "templates/shared-baseline.md",
            (
                "# Shared Baseline",
                "## Parent Objective",
                "## Non-goals",
                "## End-to-end Architecture",
                "## Shared Contracts",
                "## Data and Naming Formats",
                "## Ownership Boundaries",
                "## Confirmed Decisions",
                "## Evidence and Confidence",
                "## Global Acceptance",
            ),
        )

    def test_project_task_template_is_executable_for_every_task_kind(self) -> None:
        self.assert_contains_all(
            "templates/project-task-spec.md",
            (
                "# Project Task Specification",
                "discussion",
                "design",
                "development",
                "test",
                "review",
                "deployment",
                "## Current State",
                "## Problem and Target Behavior",
                "## Owned Scope",
                "## Excluded Scope",
                "## Components and Flow",
                "## Interfaces and Contracts",
                "## Data and State",
                "## Configuration and Deployment",
                "## Compatibility and Failure Semantics",
                "## Project-local Verification",
                "## Acceptance",
            ),
        )

    def test_handoff_template_carries_routing_execution_and_output_context(self) -> None:
        self.assert_contains_all(
            "templates/handoff.md",
            (
                "# Task Handoff",
                "dispatchId",
                "subtaskId",
                "mode",
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

    def test_task_control_plane_defines_parent_authority_and_future_boundary(self) -> None:
        self.assert_contains_all(
            "references/task-control-plane.md",
            (
                "PENDING",
                "IN_PROGRESS",
                "BLOCKED",
                "COMPLETED",
                "sole authority",
                "requestedState",
                "summary",
                "evidenceRefs",
                "nextStep",
                "needsParentDecision",
                "deterministic",
                "WALK",
                "graphical interface",
                "no database",
            ),
        )

    def test_skill_entrypoint_defines_complete_safe_orchestration(self) -> None:
        self.assert_contains_all(
            "SKILL.md",
            (
                "stable design spans two or more projects",
                "A: Dispatch mode (default)",
                "B: Development mode",
                "Dispatch is the default",
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
                "every complete document for every child",
                "one batch confirmation",
                "create_thread",
                "authorized only after",
                "send_message_to_thread",
                "wait_threads",
                "dependency",
                "local commit",
                "project-local tests",
                "dry-run",
                "must never create a real Codex task",
            ),
        )

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
                "references/task-control-plane.md",
                "scripts/task_package.py",
                "scripts/task_control.py",
            ),
        )


if __name__ == "__main__":
    unittest.main()
