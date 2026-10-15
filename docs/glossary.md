# Glossary

Terms the guides use without explaining them.

See [command language](../CONTEXT.md) for swarm controls, project commands and standalone skills.

## People and threads

**Root.** The single orchestrator thread, shown in purple. It chooses which issues run, assigns leads, picks models, reviews submissions and merges finished work. It doesn't implement issues itself.

**Lead.** The one agent thread responsible for an issue from start to finish. Colours show the kind of work: yellow for frontend, blue for backend, black for debugging, red for other work.

**Child.** An agent a lead (or Root) starts for one bounded task, such as a review or a single fix. It reports to whoever started it. A child passing its task doesn't mean the issue is done.

**Worker number.** The number in a thread name, such as the `4` in `🟡 4 | #17 Export invoices as CSV`. Numbers are counted separately for each colour and are never reused.

**Green 1, Green 2.** The two user-facing (green) chats. Green 1 is your own workspace; agents never message it. Green 2 is where agents send you decisions to make and finished results, in batches.

## Work states

**Done.** Everything the issue asked for works, the required checks pass on the delivered code, review findings are resolved, the change is merged into the agreed branch, and any required human sign-off is recorded.

**Pinned base.** The exact commit an issue branch starts from, written down so everyone works from the same code.

**Settle.** Close out a finished or parked thread once its state and any follow-up are recorded. Settled threads are not reused for other issues.

**Safe checkpoint.** A point between steps where Root can take new instructions without interrupting work in progress, for example after finishing a dispatch. It doesn't mean waiting until a whole issue is finished.

## Messages to Root

**P0, P1, P2.** Priority labels on reports to Root. P0: an urgent correction to what Root is doing right now (delivered immediately). P1: a decision that blocks work. P2: a finished delivery (queued until Root is ready).

## /swarm command states

The swarm script records each command in three separate steps:

1. **ALLOW.** The script approved the command, so the chat may send it to Root once. Nothing has been sent yet.
2. **Delivered.** The chat tool confirmed that Root received the message.
3. **Applied.** Root actually changed what it is doing. The five-hour limit on direction changes starts here.

Each step can happen without the next. A sent message may never be delivered, and a delivered one may never be applied.

## Authority

**Grant.** Permission, recorded in the project's configuration or given by the user, to do something with outside effects: push code, open or merge PRs, spend money on paid models, deploy, touch real data or delete things.

**Effects.** Those outside actions. Finishing a step never adds a grant: a passing review doesn't allow anyone to deploy, and a finished setup doesn't allow paid model calls. The project's AGENTS.md states this rule once, so the guides don't repeat it.
