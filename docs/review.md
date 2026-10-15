# First-version review

## Requested outcome

A reusable standalone SwarmStack with a reviewable GitHub repository. Cover the eight design points in design.md, plus PR/issue formats and a grill-with-docs project setup guide. Do not install it globally or modify other projects or host tools.

## Review first

- [SETUP.md](../SETUP.md): inspect, interview, confirm, preview, apply, verify.
- [Orchestrator](../guides/orchestrator.md): naming, one issue per lead, queues, integration and closure.
- [PR format](../.github/pull_request_template.md) and [issue forms](../.github/ISSUE_TEMPLATE/bug.yml).
- [Model routing](../guides/models.md): measured comparable configurations, unknowns and effort cost.

## Claims and limits

The installer creates project-local guidance only, refuses overwrites and runs no project command. It is not a transactional or hostile-concurrent-writer installer; an I/O failure may leave a disclosed partial setup. Existing repositories require a separate migration if files conflict.

The Pareto tool is offline and has invented fixtures only. No current AA scores, live model evaluations, provider tests or spending are claimed. Host-specific skill discovery and UI behavior are documented adoption checks, not tested compatibility claims.

At first-version delivery, the customised review/interview procedures were preserved verbatim, with short entrypoints and portability notes. The subsequent attribution relocation removes operational credits and replaces the review procedure’s unavailable setup command with confirmed tracker lookup. Original/current hashes remain in provenance.json. First-version tests exercise local disposable projects, not the user's applications. An optional manual-dispatch CI template is provided under templates/github/check.yml; no workflow is installed or claimed green.

Independent review and actual check results are recorded in [review-results.md](review-results.md) after correction. No global/project rollout, paid integration, production merge or automatic update is included.
