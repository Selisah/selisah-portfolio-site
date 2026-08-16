from pathlib import Path
import unittest


WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "deploy.yml"


class DeployWorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_deployment_is_gated_by_tests(self):
        self.assertIn("test:", self.workflow)
        self.assertIn('python-version: "3.10"', self.workflow)
        self.assertIn("./run_test.sh", self.workflow)
        self.assertIn("needs: test", self.workflow)

    def test_container_status_is_recorded(self):
        self.assertIn("Print container status", self.workflow)
        self.assertIn("docker compose -f docker-compose.prod.yml ps", self.workflow)

    def test_discord_notifications_cover_success_and_failure(self):
        self.assertGreaterEqual(self.workflow.count("secrets.DISCORD_WEBHOOK"), 3)
        self.assertIn("Deployment Successful", self.workflow)
        self.assertIn("Deployment Failed", self.workflow)
        self.assertIn("if: ${{ failure() }}", self.workflow)
        self.assertIn("needs.test.result == 'failure'", self.workflow)


if __name__ == "__main__":
    unittest.main()
