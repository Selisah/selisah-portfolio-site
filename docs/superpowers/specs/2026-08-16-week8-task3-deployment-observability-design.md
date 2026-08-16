# Week 8 Task 3 Deployment Observability Design

## Goal

Extend the existing DigitalOcean deployment workflow so it tests the portfolio before deployment, records the resulting container status, and sends Discord notifications for both successful and failed deployments. Preserve the dedicated deployment SSH key already established in Task 2.

## Scope

The change is limited to `.github/workflows/deploy.yml` and workflow-focused verification. It will not redesign the portfolio, modify application behavior, rotate the working deployment key, or refactor the separate `test.yml` workflow.

## Workflow Architecture

The workflow will contain two jobs. A `test` job will reproduce the repository's established Python 3.10 test procedure: check out the repository, create and activate a virtual environment, install `requirements.txt`, set `TESTING=true`, and run `run_test.sh`.

The existing `deploy` job will declare `needs: test`. GitHub Actions will therefore start deployment only after the test job succeeds. The deployment job will keep the existing SSH configuration and run `/root/redeploy-site.sh` on the DigitalOcean droplet.

After the redeployment command succeeds, the workflow will run a second SSH command in the configured project directory to print `docker compose -f docker-compose.prod.yml ps`. This uses the Compose v2 syntax already used by the server's redeployment script while satisfying MLH's requirement to retain container status in the workflow logs.

## Discord Notifications

The repository will reference an encrypted `DISCORD_WEBHOOK` secret and will never store or print the webhook URL in source code or logs. The deploy job will map that secret into a step-level environment variable and use `curl` to send a concise success message after deployment and container-status verification complete.

A final failure-notification step will use `if: ${{ failure() }}` so it runs when an earlier step in the deploy job fails. It will send a concise failure message containing the repository and workflow-run URL. Both notification steps will also check that the webhook variable is non-empty. This allows pull-request checks and initial setup to remain safe before the secret is created, while a real Discord notification can be verified after the secret is added.

Because the `deploy` job does not start when the prerequisite `test` job fails, a deploy-job failure step alone cannot report test failures. To cover the MLH requirement fully, the workflow will include a separate `notify-test-failure` job with `needs: test` and `if: ${{ always() && needs.test.result == 'failure' }}`. This job will send the same failure message through the encrypted webhook when testing prevents deployment.

## Error Handling

The workflow will use `curl --fail-with-body --silent --show-error` for Discord requests. A rejected webhook request will therefore be visible as a failed notification step instead of being silently ignored. Deployment remains test-gated, and container-status logging runs only after the deployment command succeeds.

If `DISCORD_WEBHOOK` is absent, notification steps will report that the notification was skipped without exposing any secret. The deployment and tests can still be verified independently, but Task 3 is not considered fully complete until the secret exists and at least one successful Discord notification has been observed.

## Verification

Before publishing, the workflow YAML will be parsed and checked for the required triggers, jobs, dependencies, conditions, SSH deployment command, Compose status command, and success/failure notification steps. The application test suite will also run to ensure the workflow-only change does not coincide with an application regression.

After the branch is published, the pull-request test check must pass. After merge, the push workflow must show a successful test job, deployment job, container-status output, and success-notification step. The live portfolio must still load and display the Task 2 GitHub Actions sentence. The user will confirm receipt of the Discord message because that external channel is not visible to the repository logs.

## Submission Evidence

The LMS response will contain URLs to the workflow files on the merged `main` branch, as requested by MLH. The first-person journal will record the job dependency design, the distinction between deployment and test failures, the webhook-secret handling decision, verification results, warnings, and relevant tradeoffs. The final LMS submission button remains for the user to click.
