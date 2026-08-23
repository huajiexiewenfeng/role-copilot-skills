import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ProjectTaskDispatchIntegrationContractTest(unittest.TestCase):
    def test_child_skill_ships_complete_lossless_task_package_contract(self):
        child = SKILL_ROOT / "project-task-dispatch"
        required = {
            "SKILL.md",
            "templates/shared-baseline.md",
            "templates/project-task-spec.md",
            "templates/handoff.md",
            "templates/worker-initial-message.md",
            "templates/worker-rework-message.md",
            "templates/reviewer-message.md",
            "references/routing.md",
            "references/task-package-protocol.md",
            "references/development-receipt.md",
            "references/task-control-plane.md",
            "references/manager-runtime.md",
            "references/manifest-v2.md",
            "schemas/dispatch-manifest-v2.schema.json",
            "scripts/task_package.py",
            "scripts/task_control.py",
            "scripts/legacy_receipt.py",
            "scripts/manifest_v2.py",
            "scripts/native_thread_adapter.py",
            "scripts/status_view.py",
            "scripts/render_status_png.mjs",
            "tests/test_task_package.py",
            "tests/test_task_control.py",
            "tests/test_task_control_v2.py",
            "tests/test_legacy_receipt_v2.py",
            "tests/test_manifest_v2.py",
            "tests/test_native_thread_adapter.py",
            "tests/test_scheduler.py",
            "tests/test_status_view.py",
            "tests/test_skill_contract.py",
            "tests/v2_fixture.py",
            "evals/evals.json",
            "evals/trigger-evals.json",
        }
        actual = {
            path.relative_to(child).as_posix()
            for path in child.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
        }
        self.assertSetEqual(actual, required)

    def test_parent_router_proactively_offers_dispatch_and_development_modes(self):
        router = read(SKILL_ROOT / "SKILL.md")
        for token in (
            "`project-task-dispatch`",
            "Dispatch mode",
            "Development mode",
            "stable design",
            "two or more projects",
            "one batch confirmation",
        ):
            with self.subTest(token=token):
                self.assertIn(token, router)

    def test_english_and_chinese_readmes_publish_the_child_skill(self):
        for path in (
            REPOSITORY_ROOT / "README.md",
            REPOSITORY_ROOT / "README.zh.md",
            SKILL_ROOT / "README.md",
            SKILL_ROOT / "README.zh.md",
        ):
            with self.subTest(path=path):
                self.assertIn("project-task-dispatch", read(path))


if __name__ == "__main__":
    unittest.main()
