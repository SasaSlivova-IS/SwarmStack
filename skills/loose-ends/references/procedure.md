# Loose ends procedure

The user moves between ideas faster than any one thread can close them. This procedure finds what was left behind and turns it into a short list the user can act on. It never does the follow-up work itself.

## Choose the window

- **cover:** the current conversation, from its start or from the point the user names. Include messages relayed from other agents.
- **catchup:** the project since the user last engaged with it. Use, in order: the starting point the user gives; the user's last message in the channel where agents report to them; otherwise ask the user for a date. Say which starting point you used.

## Gather

Read before writing. Check every fact against its source; if a source is unavailable, say so instead of guessing.

**cover** reads the conversation itself, then the records it points to: pending decisions, the decisions record and any file a question or offer names. Ask the project configuration where these live; do not assume paths.

**catchup** reads the project's current state and accepted decisions, the issue tracker, open pull requests, active threads or agents and their last reports, and the release or integration branch. Ask the project configuration where these live; do not assume paths.

## Find loose ends

Look for each kind. Skip a kind when nothing applies; never invent an item to fill it.

1. **Unanswered questions.** Questions put to the user with no answer, including ones asked earlier and pushed out of view.
2. **Unconfirmed offers.** Things an agent offered to do ("should I…?") that the user never accepted or declined.
3. **Partial answers.** Answers that settled one part and left another open, or that an agent recorded differently from what the user said.
4. **Contradictions.** Two decisions that cannot both hold, or a decision that conflicts with an earlier one or with a stated constraint. Example: "deploys run from the build server" next to "the build server is being retired".
5. **Missing pieces.** A decision with no screen for it, no tests, no owner, no record, or no route to the person who must act.
6. **Stale or wrong facts.** Something said in the conversation that the records now show is out of date.
7. **Opportunities.** At most three. A cheap step that would remove a recurring problem, reuse something that already exists, or merge two pieces of work.

In **catchup**, first sort what changed into: finished, newly blocked, waiting on the user, and still running. Finished means it meets the project's agreed done criteria, not that a step passed.

## Report

Open with one sentence: how many things need the user, or that nothing does.

- **catchup** then gives what changed in short plain lines, one per piece of work, saying whether it is finished, running, blocked or unchecked. Keep this part under about 150 words.
- Both modes then list **waiting on you**. Ask the 3–5 most important as full grill-with-docs questions, ranked by importance. List the rest as one line each: identifier, topic and what is needed.
- Then contradictions, missing pieces and stale facts, each with a proposed fix as A–D when the user must choose, or one line when an agent can fix it.
- Then up to three opportunities.
- End with one line naming the work an agent can do without the user, and an answer example that pairs each identifier with its topic.

Say which mode and starting point you used. Write in plain words. Leave out hashes, paths and run numbers unless the user needs one to act. Keep existing identifiers, and always pair them with the topic. Do not mark anything done, approved or verified that is not.

## After the report

The report itself writes nothing. When the user answers, follow grill-with-docs' "After answers" section: route each answer to its owner and record it in the owning record.
