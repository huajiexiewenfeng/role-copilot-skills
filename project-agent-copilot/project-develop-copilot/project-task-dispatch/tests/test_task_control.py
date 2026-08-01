from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SKILL_ROOT / "scripts" / "task_control.py"


def load_module():
    if not MODULE_PATH.is_file():
        raise AssertionError(f"missing task control module: {MODULE_PATH}")
    spec = importlib.util.spec_from_file_location("task_control", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load task control module: {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TaskControlTest(unittest.TestCase):
    def setUp(self) -> None:
        self.control = load_module()

    def receipt(
        self,
        task_id: str,
        requested_state: str,
        *,
        summary: str = "Implemented the owned change.",
        evidence_refs: list[str] | None = None,
        next_step: str = "Parent validates the evidence.",
        blocked: bool = False,
        needs_parent_decision: bool = False,
        blocker: str | None = None,
    ):
        return self.control.parse_receipt(
            {
                "taskId": task_id,
                "requestedState": requested_state,
                "summary": summary,
                "evidenceRefs": evidence_refs or [f"thread:{task_id}#latest"],
                "nextStep": next_step,
                "blocked": blocked,
                "needsParentDecision": needs_parent_decision,
                "blocker": blocker,
            }
        )

    def test_exposes_only_four_authoritative_states(self) -> None:
        self.assertEqual(
            {state.value for state in self.control.TaskState},
            {"PENDING", "IN_PROGRESS", "BLOCKED", "COMPLETED"},
        )

    def test_applies_the_finite_legal_transition_sequence(self) -> None:
        task = self.control.create_task("backend", "smarthub", "BFF task")
        task = self.control.apply_receipt(
            task,
            self.receipt("backend", "IN_PROGRESS"),
        )
        task = self.control.apply_receipt(
            task,
            self.receipt(
                "backend",
                "BLOCKED",
                blocked=True,
                needs_parent_decision=True,
                blocker="SDK contract requires a parent decision.",
            ),
        )
        task = self.control.apply_receipt(
            task,
            self.receipt("backend", "IN_PROGRESS"),
        )
        task = self.control.apply_receipt(
            task,
            self.receipt("backend", "COMPLETED"),
        )

        self.assertEqual(task.state, self.control.TaskState.COMPLETED)

    def test_allows_progress_and_blocker_snapshot_refreshes(self) -> None:
        task = self.control.create_task("frontend", "smarthub-web", "Web task")
        task = self.control.apply_receipt(
            task,
            self.receipt("frontend", "IN_PROGRESS", summary="First update."),
        )
        task = self.control.apply_receipt(
            task,
            self.receipt("frontend", "IN_PROGRESS", summary="Second update."),
        )
        self.assertEqual(task.summary, "Second update.")

        task = self.control.apply_receipt(
            task,
            self.receipt(
                "frontend",
                "BLOCKED",
                summary="Waiting for an API field.",
                blocked=True,
                blocker="Missing API field.",
            ),
        )
        task = self.control.apply_receipt(
            task,
            self.receipt(
                "frontend",
                "BLOCKED",
                summary="Still waiting for the API field.",
                blocked=True,
                blocker="Missing API field.",
            ),
        )
        self.assertEqual(task.summary, "Still waiting for the API field.")

    def test_rejects_illegal_and_post_completion_transitions(self) -> None:
        pending = self.control.create_task("api", "drone-cloud-api", "API task")
        with self.assertRaisesRegex(ValueError, "illegal task transition"):
            self.control.apply_receipt(
                pending,
                self.receipt("api", "COMPLETED"),
            )

        active = self.control.apply_receipt(
            pending,
            self.receipt("api", "IN_PROGRESS"),
        )
        completed = self.control.apply_receipt(
            active,
            self.receipt("api", "COMPLETED"),
        )
        with self.assertRaisesRegex(ValueError, "terminal"):
            self.control.apply_receipt(
                completed,
                self.receipt("api", "COMPLETED"),
            )

    def test_receipt_schema_rejects_global_state_and_unknown_fields(self) -> None:
        payload = {
            "taskId": "frontend",
            "requestedState": "IN_PROGRESS",
            "summary": "Working.",
            "evidenceRefs": ["thread:frontend#1"],
            "nextStep": "Continue.",
            "blocked": False,
            "needsParentDecision": False,
            "blocker": None,
            "globalOverview": {"frontend": "COMPLETED"},
        }
        with self.assertRaisesRegex(ValueError, "unknown receipt fields"):
            self.control.parse_receipt(payload)

    def test_receipt_schema_enforces_blocker_and_parent_decision_consistency(self) -> None:
        with self.assertRaisesRegex(ValueError, "blocked must match"):
            self.receipt("api", "BLOCKED", blocked=False)
        with self.assertRaisesRegex(ValueError, "requires a blocker"):
            self.receipt("api", "BLOCKED", blocked=True, blocker=None)
        with self.assertRaisesRegex(ValueError, "parent decision"):
            self.receipt(
                "api",
                "IN_PROGRESS",
                needs_parent_decision=True,
            )

    def test_parent_reducer_does_not_mutate_the_original_record(self) -> None:
        original = self.control.create_task(
            "frontend",
            "smarthub-web",
            "Web task",
        )
        updated = self.control.apply_receipt(
            original,
            self.receipt("frontend", "IN_PROGRESS"),
        )

        self.assertEqual(original.state, self.control.TaskState.PENDING)
        self.assertEqual(updated.state, self.control.TaskState.IN_PROGRESS)
        self.assertIsNot(original, updated)

    def test_builds_a_deterministic_blocker_first_cross_project_projection(self) -> None:
        frontend = self.control.create_task(
            "frontend",
            "smarthub-web",
            "Implement the log task page",
        )
        frontend = self.control.apply_receipt(
            frontend,
            self.receipt(
                "frontend",
                "IN_PROGRESS",
                evidence_refs=["thread:frontend#42", "test:frontend:15-passed"],
                next_step="Finish the download interaction.",
            ),
        )
        backend = self.control.create_task(
            "backend",
            "drone-cloud-api",
            "Implement the log task API",
        )
        backend = self.control.apply_receipt(
            backend,
            self.receipt(
                "backend",
                "BLOCKED",
                summary="Device lookup contract is missing.",
                evidence_refs=["thread:backend#17", "source:device-client"],
                next_step="Parent chooses the lookup contract.",
                blocked=True,
                needs_parent_decision=True,
                blocker="No source-verified device lookup API.",
            ),
        )

        first = self.control.build_projection([frontend, backend])
        second = self.control.build_projection([backend, frontend])

        self.assertEqual(first, second)
        self.assertEqual(
            first["counts"],
            {
                "PENDING": 0,
                "IN_PROGRESS": 1,
                "BLOCKED": 1,
                "COMPLETED": 0,
            },
        )
        self.assertEqual(first["blockedCount"], 1)
        self.assertEqual(first["needsParentDecisionCount"], 1)
        self.assertEqual(
            [item["taskId"] for item in first["tasks"]],
            ["backend", "frontend"],
        )
        self.assertEqual(first["tasks"][0]["state"], "BLOCKED")
        self.assertEqual(
            first["tasks"][0]["nextStep"],
            "Parent chooses the lookup contract.",
        )


if __name__ == "__main__":
    unittest.main()
