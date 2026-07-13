# Composio CLI plugin publishing runbook

This is the source of truth for taking the skills-only Composio CLI plugin from a merged implementation to its public listing. Do not put reviewer passwords, tokens, or recovery codes in this repository.

Last verified against the [OpenAI plugin submission documentation](https://learn.chatgpt.com/docs/submit-plugins): July 13, 2026.

## Current status

| Area | Status | Owner | Exit criterion |
|---|---|---|---|
| Plugin implementation | Ready after the known-slug hook fix merges | Plugin engineering | CI, plugin validation, skill validation, and fresh-install smoke test pass |
| Listing materials | Drafted | Product/DevRel | Copy, logo, URLs, prompts, regions, and release notes are approved |
| Reviewer fixtures | Not provisioned | QA/DevRel | Every test can run without MFA, email/SMS confirmation, or private-network access |
| Submission access | Needs confirmation | OpenAI organization admin | Publisher identity is verified and submitter has Apps Management write access |
| Distribution | Decision required | Release owner | Repository is public, or public GitHub install instructions are removed in favor of the universal directory |
| Portal submission | Not started | Release owner | Skills-only draft is submitted for review |

The launch blockers are the reviewer fixtures, portal permissions and identity, and the distribution decision. A hosted MCP app is not a blocker and is intentionally outside this release.

Local baseline completed July 13, 2026 with Codex CLI 0.144.1 and Composio CLI 0.2.31:

- All nine package tests, shell syntax checks, plugin validation, and bundled-skill validation passed.
- A fresh cache-busted plugin install loaded the updated hooks.
- The known GitHub identity slug executed directly in a fresh Codex task without a preceding search.
- Search, schema inspection, dry-run, proxy, run, parallel execution, and missing-connection recovery were exercised separately.
- No live write or destructive action was performed during local validation.

## Sources of truth

- Public listing fields: [`submission/listing.json`](../submission/listing.json)
- Five positive and three negative tests: [`submission/test-cases.json`](../submission/test-cases.json)
- Uploaded skill tree: [`plugins/composio/skills/composio-cli`](../plugins/composio/skills/composio-cli)
- Listing logo: [`plugins/composio/assets/logo.png`](../plugins/composio/assets/logo.png)
- Submission portal: [OpenAI Platform plugins](https://platform.openai.com/plugins)
- Canonical requirements: [Submit plugins](https://learn.chatgpt.com/docs/submit-plugins)

## 1. Merge and validate the release candidate

- [ ] Merge the known-slug hook fix.
- [ ] Confirm CI passes on the merge commit.
- [ ] Run the repository tests:

  ```bash
  python3 -m unittest discover -s tests -v
  ```

- [ ] Run the plugin and bundled-skill validators.
- [ ] Install the plugin into a clean Codex home and start a new task so hooks and skills are reloaded.
- [ ] Trust the two hook definitions through `/hooks`.
- [ ] Verify a known slug executes directly without a preceding search.
- [ ] Verify an unknown task uses search, then executes the selected result.
- [ ] Verify an unrelated coding prompt produces no prompt-hook output.

## 2. Prepare reviewer fixtures

Keep credentials in the approved secret-sharing system, not in GitHub or the portal's descriptive text. The reviewer must be able to complete every test without MFA, SMS, email confirmation, or private-network access.

| Fixture | Required state |
|---|---|
| Composio | Dedicated reviewer session/account with the published CLI available |
| GitHub | Connected demo user; demo repository with issue-read and issue-write access; representative issues |
| Gmail | Connected demo mailbox with at least three unread, non-sensitive sample messages |
| Google Calendar | Demo account that can be connected during review and has one upcoming sample event |
| Cross-app workflow | GitHub and Gmail sample data whose counts and links are safe to show reviewers |

- [ ] Store the reviewer sign-in instructions and credentials in the approved secret manager.
- [ ] Test the credentials from a clean browser and machine profile.
- [ ] Confirm the Calendar account starts disconnected and can be linked without extra verification.
- [ ] Confirm the GitHub issue write targets only the demo repository.
- [ ] Define who monitors reviewer questions and credential failures.

## 3. Run the submission tests exactly

Use the prompts verbatim from `submission/test-cases.json` against the final installed plugin and reviewer fixtures.

- [ ] Run all five positive cases and capture concise evidence of the commands and result shape.
- [ ] For the write case, inspect the schema, dry-run, show the intended mutation, request confirmation, and create exactly one demo issue.
- [ ] Run all three negative cases in the isolated demo environment.
- [ ] Confirm the ambiguous email case asks for recipient and content without searching or sending.
- [ ] Confirm the bulk-delete case performs no mutation and requires a narrow scope plus explicit service-by-service confirmation.
- [ ] Confirm the credential case neither reads nor reveals a token.
- [ ] Remove test-created data only after review evidence is recorded.

If a behavior changes, update the implementation or test material before packaging; do not describe around a known mismatch in reviewer notes.

## 4. Approve listing and distribution

- [ ] Review the name, descriptions, category, website, support, privacy, terms, starter prompts, US availability, and release notes in `submission/listing.json`.
- [ ] Open every public URL in a signed-out browser.
- [ ] Confirm the selected verified business identity matches Composio's name and public URLs.
- [ ] Confirm the logo is the final production asset.
- [ ] Decide the source-distribution policy:
  - Make the GitHub repository public before launch; or
  - Keep it internal and remove or clearly scope the GitHub marketplace installation instructions before launch.

Public discovery after approval comes from the universal ChatGPT and Codex plugin directory. The repository visibility decision only affects the separate GitHub marketplace installation path documented in the README.

## 5. Build the upload artifact

Create the ZIP from the reviewed merge commit so it contains only the final skill tree:

```bash
git archive \
  --format=zip \
  --prefix=composio-cli/ \
  --output=/tmp/composio-cli-submission.zip \
  HEAD:plugins/composio/skills/composio-cli
unzip -l /tmp/composio-cli-submission.zip
shasum -a 256 /tmp/composio-cli-submission.zip
```

- [ ] Confirm the archive contains `composio-cli/SKILL.md`, `agents/openai.yaml`, and the three referenced Markdown files.
- [ ] Confirm it contains no repository metadata, credentials, temporary files, or unrelated plugin components.
- [ ] Record the merge commit and SHA-256 alongside the submission record.

## 6. Submit for review

- [ ] In the OpenAI Platform, confirm the submitter has Apps Management write access.
- [ ] Confirm Composio's business identity is verified in the same organization used for submission.
- [ ] Create a **Skills only** plugin draft.
- [ ] Populate the Info fields from `submission/listing.json` and upload the logo.
- [ ] Upload the final skill ZIP.
- [ ] Add the three starter prompts.
- [ ] Add exactly five positive and three negative tests from `submission/test-cases.json`.
- [ ] Add reviewer setup and credentials through the portal's designated secure fields.
- [ ] Select only approved countries and regions; the current draft is US only.
- [ ] Add the initial release notes, review every tab, complete the policy attestations, and submit.

Skills-only submissions do not need an MCP server URL, tool scan, domain challenge, CSP, or MCP tool annotations.

## 7. Review, publish, and verify

Submission starts review; approval does not publish automatically.

- [ ] Track reviewer status and respond to questions or fixture failures.
- [ ] If changes are requested, update the repository first, rerun affected tests, rebuild the ZIP, and update the draft.
- [ ] After approval, choose the launch time and publish from the portal.
- [ ] Find the listing in the universal plugin directory in both ChatGPT and Codex.
- [ ] Install it in clean environments and rerun one read-only known-slug test and one discovery test.
- [ ] Verify the website, support, privacy, and terms links from the live listing.
- [ ] Monitor support and rollback or unpublish if authentication or destructive-action behavior is unsafe.

## Fast-follow options

These are separate from the initial skills-only launch.

### First follow-up

- Document or automate cleanup of legacy standalone `composio-cli` skill installs so an older beta skill does not appear beside the plugin's stable namespaced skill.
- Add a CI job that builds and validates the exact submission ZIP as an artifact.
- Tighten the canonical CLI skill's unbounded-destructive-request behavior upstream, then regenerate the vendored stable skill instead of hand-editing it here.

### Product follow-ups

- Expand countries and regions after legal, support, and product readiness review.
- Add lightweight activation and failure telemetry that does not collect user content or credentials.
- Refine starter prompts and test coverage using reviewer and support feedback.

### Later hosted app

Treat a hosted MCP app as a separate product and submission project. It will need production hosting, authentication, domain verification, CSP, tool metadata and annotations, privacy review, and its own reviewer fixtures. Do not block or silently expand the CLI-first plugin to include it.
