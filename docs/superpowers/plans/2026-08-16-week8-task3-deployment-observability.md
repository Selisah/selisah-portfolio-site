# Week 8 Task 3 Deployment Observability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test the portfolio before deployment, record production container status, and notify Discord when testing or deployment succeeds or fails.

**Architecture:** Add a Python 3.10 `test` job to `deploy.yml`, gate the existing SSH deployment job with `needs: test`, and add a separate test-failure notification job because a failed prerequisite prevents the deploy job from starting. Keep webhook data in the encrypted `DISCORD_WEBHOOK` secret and validate the workflow through a repository-local contract test plus the application suite.

**Tech Stack:** GitHub Actions YAML, Bash, SSH, Docker Compose v2, Discord webhook API, Python `unittest`.

## Global Constraints

- Keep the webhook URL exclusively in the encrypted `DISCORD_WEBHOOK` GitHub secret.
- Keep the existing dedicated deployment SSH key and current SSH configuration.
- Deploy only after the Python 3.10 test job succeeds.
- Print `docker compose -f docker-compose.prod.yml ps` after deployment.
- Notify Discord about test failures, deployment failures, and successful deployments.
- Do not change portfolio application behavior.
- Leave the final MLH submission click to the user.

---

### Task 1: Add a Failing Workflow Contract Test

**Files:**
- Create: `tests/test_deploy_workflow.py`
- Test: `tests/test_deploy_workflow.py`

**Interfaces:**
- Consumes: `.github/workflows/deploy.yml` as UTF-8 text.
- Produces: `DeployWorkflowContractTests`, which documents the MLH Task 3 workflow contract without adding runtime dependencies.

- [ ] **Step 1: Write the failing contract test**

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest tests.test_deploy_workflow -v`

Expected: failures for the absent test gate, status command, and Discord notification contract.

- [ ] **Step 3: Commit the failing contract**

```bash
git add tests/test_deploy_workflow.py
git commit -m "Test Task 3 deployment workflow contract"
```

### Task 2: Implement Test-Gated Deployment and Notifications

**Files:**
- Modify: `.github/workflows/deploy.yml`
- Test: `tests/test_deploy_workflow.py`

**Interfaces:**
- Consumes: `SSH_PRIVATE_KEY`, `SSH_IP`, `SSH_USER`, `PROJECT_ROOT`, and `DISCORD_WEBHOOK` GitHub secrets.
- Produces: `test`, `deploy`, and `notify-test-failure` jobs with explicit dependency and failure conditions.

- [ ] **Step 1: Add the Python 3.10 test job**

Copy the established checkout, setup-python, virtual-environment, dependency-install, and `./run_test.sh` sequence from `.github/workflows/test.yml`. Set `TESTING: "true"` at job level.

- [ ] **Step 2: Gate deployment and record container status**

Add `needs: test` to `deploy`. After `ssh my-vps "~/redeploy-site.sh"`, add:

```yaml
      - name: Print container status
        run: >-
          ssh my-vps
          "cd ${{ secrets.PROJECT_ROOT }} &&
          docker compose -f docker-compose.prod.yml ps"
```

- [ ] **Step 3: Add success and deployment-failure notifications**

Use a step-level `DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}` environment variable. Send JSON with `curl --fail-with-body --silent --show-error`, `Content-Type: application/json`, and a repository/run URL. The success step runs normally after container status. The deployment-failure step uses `if: ${{ failure() }}`.

- [ ] **Step 4: Add the test-failure notification job**

Create `notify-test-failure` with `needs: test` and `if: ${{ always() && needs.test.result == 'failure' }}`. Send the same failure payload using `DISCORD_WEBHOOK` from the encrypted secret.

- [ ] **Step 5: Run the contract test to verify it passes**

Run: `python -m unittest tests.test_deploy_workflow -v`

Expected: three passing tests.

- [ ] **Step 6: Commit the workflow implementation**

```bash
git add .github/workflows/deploy.yml
git commit -m "Add deployment checks and Discord notifications"
```

### Task 3: Verify the Repository and Prepare Publication

**Files:**
- Verify: `.github/workflows/deploy.yml`
- Verify: `tests/test_deploy_workflow.py`
- Verify: `tests/test_app.py` and the existing application suite

**Interfaces:**
- Consumes: the completed workflow and repository test suite.
- Produces: local verification evidence suitable for the pull-request description and journal.

- [ ] **Step 1: Run the workflow contract and application tests**

Run: `python -m unittest tests.test_deploy_workflow -v`

Run in the existing compatible isolated environment: `python -m unittest discover -s tests -v`

Expected: workflow contract passes; the existing 24 application tests pass.

- [ ] **Step 2: Check formatting and changed-file scope**

Run: `git diff --check origin/main...HEAD`

Run: `git status --short`

Expected: no whitespace errors; only the specification, plan, contract test, and deployment workflow are changed by this branch.

- [ ] **Step 3: Commit the implementation plan**

```bash
git add docs/superpowers/plans/2026-08-16-week8-task3-deployment-observability.md
git commit -m "Plan Week 8 Task 3 implementation"
```

### Task 4: Publish, Merge, and Verify Production

**Files:**
- Publish: branch `agent/week8-task3-automation`
- Submit: `.github/workflows/deploy.yml` and `.github/workflows/test.yml` URLs on merged `main`

**Interfaces:**
- Consumes: verified commits and the encrypted repository secrets.
- Produces: a reviewed pull request, successful GitHub Actions run, live-site verification, Discord notification evidence, journal entry, and prepared LMS response.

- [ ] **Step 1: Push the branch and open a draft pull request**

Use a first-person description covering changes, decisions, tradeoffs, and local verification.

- [ ] **Step 2: Verify pull-request checks, then merge**

Require the existing `Run Tests` check to pass and confirm no merge conflict before merging.

- [ ] **Step 3: Verify the post-merge workflow**

Confirm the `test` job passes, deployment runs afterward, container status appears in logs, notification step succeeds, and the full workflow completes successfully.

- [ ] **Step 4: Verify external outcomes**

Confirm `https://selisah.duckdns.org` loads and still displays the GitHub Actions sentence. Confirm the user received the Discord success message.

- [ ] **Step 5: Update the journal and prepare the LMS response**

Add a clearly separated first-person paragraph section documenting implementation, failure routing, secret handling, verification, and tradeoffs. Enter the merged workflow URLs in the LMS response, but do not click the final submission button.
