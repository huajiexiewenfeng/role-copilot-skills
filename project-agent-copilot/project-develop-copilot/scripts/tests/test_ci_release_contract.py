import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
WORKFLOW_PATH = REPOSITORY_ROOT / ".github" / "workflows" / "project-develop-copilot-ci.yml"


class ProjectDevelopCopilotCiReleaseContractTest(unittest.TestCase):
    def test_linux_and_windows_jobs_run_task_dispatch_regressions(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        command = (
            "python -m unittest discover "
            "project-agent-copilot/project-develop-copilot/project-task-dispatch/tests"
        )

        self.assertEqual(workflow.count(command), 2)


if __name__ == "__main__":
    unittest.main()
