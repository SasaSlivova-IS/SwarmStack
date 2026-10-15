# Issue tracking

Load when creating, splitting, updating or closing issues, milestones or board items, and at every coordination checkpoint that changes an issue's state. The tracker shows the user what is happening without asking a chat.

## One place for status

The issue tracker owns each issue's status, scope, open questions and acceptance checklist. Requirements, decisions and designs stay in their repository records; link them from the issue instead of copying them. When a repository record and the issue disagree about status, fix the issue.

## Issues

- One issue is one outcome a single lead can finish and close in days. Larger work is a parent issue with sub-issues. Close each sub-issue when its change is integrated, even while the parent stays open.
- Write the title as the outcome in plain words. Put internal tracking codes in the body, not the title.
- Every issue body keeps the sections from the issue forms: what it is about, where it stands, what needs to be done, answered questions, open questions, acceptance checklist and dependencies.
- User acceptance is one checklist item on the issue or parent, not a reason to keep finished sub-issues open.

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

The Needs user column is the user's daily view. Every item there links the exact question in grill-with-docs format, and the same question goes to the user through the user-facing channel. Move an item out as soon as the answer is recorded.

Record the lead in a board field or label, such as `lead: 🔵 12`. Agents cannot be GitHub assignees; keep assignees for people.

## Labels

Keep a small fixed set: role, scope, type, source and `needs:` labels. `needs:user-decision`, `needs:user-acceptance` and `needs:authority` must match the Needs user column.

## Pull requests and evidence

- A pull request is the way a change reaches the integration branch. Link it to its issue with "Fixes #N" for a whole issue or "Part of #N" for a slice, so merging updates the issue.
- Put review findings and check results on the pull request. Keep large logs, captures and receipts out of the repository; attach them to the pull request or check run, or store them outside Git and link them. Commit only short summaries that later work needs.
- Tag each build the user is asked to test and publish short release notes of the merged pull requests since the last tag. That list is what the user tests.

## Who updates what

The orchestrator creates and triages issues, sets milestones, moves board items and closes issues. Leads update their issue's "where it stands" section and checklist at milestones, and open pull requests. The user-facing agent keeps the Needs user column in step with the questions it asks.
