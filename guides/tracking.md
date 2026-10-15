# Issue tracking

Load when creating, splitting, updating or closing issues, milestones or board items, and at every coordination checkpoint that changes an issue's state. The tracker shows the user what is happening without asking a chat.

## One place for status

The issue tracker owns each issue's status, scope, open questions and acceptance checklist. Requirements, decisions and designs stay in their repository records; link them from the issue instead of copying them. When a repository record and the issue disagree about status, fix the issue.

## Issues

- One issue is one outcome a single lead can finish and close in days. Larger work is a parent issue with sub-issues. Close each sub-issue when its change is integrated, even while the parent stays open.
- Write the title as the outcome in plain words. Put internal tracking codes in the body, not the title.
- Every issue body keeps the sections from the issue forms: what it is about, where it stands, what needs to be done, answered questions, open questions, acceptance checklist and dependencies.
- User acceptance is one checklist item on the issue or parent, not a reason to keep finished sub-issues open.
- A sub-issue closes when its change is merged into the integration branch and its checks pass. A parent closes when every sub-issue is closed and the user has ticked its acceptance item. Promotion to beta or production is tracked by the milestone, not by reopening issues.

## Milestones

Use one milestone per release stage the project has agreed, for example Beta and 1.0. Every in-scope issue belongs to exactly one. A milestone's open count is the honest answer to "what is left".

## Board

Keep one board for the project with these status columns:

| Column | Meaning |
| --- | --- |
| Inbox | New, not yet triaged by the orchestrator. |
| Ready | Scope and dependencies clear; can be dispatched. |
| In progress | A lead owns it and is working. |
| Needs user | Waiting on a decision, access or acceptance only the user can give. |
| Blocked | Waiting on something other than the user; the item says what. |
| In review | Delivered; independent review or integration is under way. |
| Done | Integrated and accepted; the issue is closed. |

The Needs user column is the user's daily view. Every item there links the exact question in grill-with-docs format. Unless the project chooses otherwise, the board is a read-only overview: questions are asked and answered in the user-facing channel, and the agent there moves the item out as soon as the answer is recorded.

Record the lead in a board field or label, such as `lead: 🔵 12`. Agents cannot be GitHub assignees; keep assignees for people.

## Labels

Keep a small fixed set: role, scope, type, source and `needs:` labels. `needs:user-decision`, `needs:user-acceptance` and `needs:authority` must match the Needs user column.

## Pull requests and evidence

- A pull request is the way a change reaches the integration branch. Each lead opens one per issue or slice; the orchestrator checks combined changes, then merges pull requests in order through the host, not by publishing a privately combined tree. Link it to its issue with "Fixes #N" for a whole issue or "Part of #N" for a slice, so merging updates the issue.
- Run fast checks (lint, types, unit tests, record checks) automatically on every pull request into the integration branch; native, platform and server tests stay with the orchestrator's normal allocation.
- Put review findings and check results on the pull request. Keep large logs, captures and receipts out of the repository; attach them to the pull request or check run, or store them outside Git and link them. Commit only short summaries that later work needs.
- Title every pull request so the user knows what changes without opening it: the user-visible result in plain words, then the issue number. Good: "Settings sidebar stays visible in narrow windows (#32)". Bad: "#32 slice A R4 composition", "Fix", "HUI-074 follow-up".
- Write evidence for a person reading the pull request page:
  1. One sentence on what was checked and the result.
  2. A short table: check or user flow, result, link to detail.
  3. Failures, skips and anything not checked, in plain words.
  4. Links to full logs, hashes and receipts, never the content itself.
  Keep the pull request body readable in under two minutes.
- Tag each build the user is asked to test and publish short release notes of the merged pull requests since the last tag. That list is what the user tests.

## Who updates what

The orchestrator creates and triages issues, sets milestones, moves board items and closes issues. Leads update their issue's "where it stands" section and checklist at milestones, and open pull requests. The user-facing agent keeps the Needs user column in step with the questions it asks.
