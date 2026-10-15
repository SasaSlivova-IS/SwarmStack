# User-facing command contract

## Public commands

| Command | Intent | Host delivery |
| --- | --- | --- |
| `/swarm backend` | Prioritise ready backend work; Root selects issues. | Queue |
| `/swarm frontend` | Prioritise ready frontend work within current model/capacity grants. | Queue |
| `/swarm https://github.com/owner/repository/issues/42` | Prioritise that issue through its existing owner; Root verifies scope/readiness. | Queue |
| `/swarm auto` | Clear the manual priority; Root selects work within the existing goal. | Queue |
| `/swarm status` | Brief verified completed/current/next state, with observation time. | Read |
| `/swarm blockers` | Decisions or external prerequisites requiring the user. | Read |
| `/swarm pause` | Stop new dispatch and checkpoint active work safely. | Steer now |
| `/swarm resume` | Continue the same authorised goal/checkpoint. | Wake idle Root; queue if already running |

Use a full HTTPS issue URL in the configured GitHub repository, not a bare number, PR, arbitrary domain or another project. The helper normalises trailing slash/query/fragment into the same issue target. It does not fetch the issue or grant implementation authority.

Natural language can map to these intents when clear. Ambiguous changes need one concise clarification. Root retains issue decomposition, lead ownership, workspaces, review, tests, corrections and authorised integration. The user need not dispatch those steps manually.

## Local gate

Requires Python 3.10+ with standard-library sqlite3. No T3 SDK, network, global configuration or server process is used. From an adopted project's root:

```sh
python3 .swarmstack/scripts/swarm.py --project . request "/swarm backend" --request-id ORIGINAL_USER_MESSAGE_ID
python3 .swarmstack/scripts/swarm.py --project . receipt COMMAND_ID delivered --external-id ACTUAL_HOST_MESSAGE_ID
python3 .swarmstack/scripts/swarm.py --project . receipt COMMAND_ID applied
python3 .swarmstack/scripts/swarm.py --project . inspect
python3 .swarmstack/scripts/swarm.py --project . next
```

In the toolkit checkout, use scripts/swarm.py instead. Project setup must confirm `swarm.host`, the actual `swarm.orchestrator` identity, a direction cooldown of at least18000seconds and the report cache TTL. Older configurations remain usable for their original six skills; they need an explicit configuration/skill update before using this new router. Do not overwrite installed guidance automatically.

State is `.swarmstack/local/swarm.sqlite3`, protected from accidental Git publication by its directory-local .gitignore. Keep the state on a local disk; shared network filesystems and hostile concurrent file replacement are outside v1's guarantees. SQLite transactions serialize ordinary concurrent invocations. State is bound to the configured project path, repository, host and Root identity; do not copy it between projects.

One compact JSON response names status, route, command ID and stable transport key. ALLOW authorises only the next relay within existing project grants. READ asks Green to inspect facts, not message Root routinely. CACHED includes its observation time. ALREADY_ACTIVE and ALREADY_RECORDED send nothing. DEFER retains the latest pending direction; EMPTY has nothing ready. ERROR is a refusal, not permission to bypass the gate.

## Five-hour direction window

Backend, frontend, auto and issue-link directions share one project-wide window. Root records `applied` only after it actually changes direction. The gate begins the cooldown at that acknowledgement, conservatively no earlier than application. Merely requesting or delivering a message starts no cooldown.

Repeated active directions do not reset the window. A new pending direction replaces only an unsent pending direction; it cannot erase an offered/delivered message whose outcome may be unknown. Returning to the active direction cancels a different unsent pending priority. `next` offers the latest eligible pending direction once, at an ordinary coordination checkpoint. No timer sleeps or scheduled LLM messages are added. After a chat restart, inspect/reconcile state and continue from it; state persistence is not a promise that an offline host wakes itself.

The window uses persisted UTC wall time. Backward clock movement defers automatic directions and avoids using a stale cached report. A forward adjustment can advance expiry; this is a convenience cooldown, not a clock-jump-proof security/resource limit. It grants no more work or authority. Pause and urgent safety instructions always bypass cooldowns. Paused goals stay paused until actual resume; a direction request is not resume.

## Delivery and crash recovery

An offered command is durably claimed before the helper returns. Relay once with `transport_key` as the host's idempotency key when supported. In T3 use the existing message API's clientRequestId and the configured Root thread; this skill does not change T3 or create threads.

After a real host receipt, record delivered with its actual message ID. Root checks the current command/project/user authority and latest control intent before applying it, then records applied. Do not manufacture application from a successful send. Duplicate application receipts do not extend the cooldown.

If a process dies between relay and receipt, inspect the host by the same key and reconcile the original receipt. A host with idempotent delivery may replay that SAME key. Without supported idempotency or lookup, retain uncertainty; do not resend under another ID or assume no effect. `receipt ... uncertain` holds later directions. Use failed only after verifying that the message was rejected or no requested effect occurred; silence/timeouts are not failure proof.

The script records trusted local facts; it cannot authenticate the user or Root's receipts, verify a remote side effect or enforce host permissions. The adapter must verify the actual response. It never sends messages, starts work, grants spending or changes a goal by itself.

Pause sets a local pause request before relay. It remains a stop-dispatch intent until actual resume. If SQLite is busy/corrupt/unavailable but project/Root binding is valid, pause still returns ALLOW with persisted=false. Use the same transport key and report that local bookkeeping failed. Invalid/missing project binding is not permission to guess a Root. Human safety corrections sent in plain language also bypass this router.

## Reporting cache

Status/blockers never claim to start a job. Read actual records. If only Root can provide missing information, queue one consolidated request and preserve its receipt. Cache a current, concise JSON snapshot with `cache status --json-file FILE`, or blockers likewise; maximum16KiB. `invalidate` clears it when meaningful work changes. Applied commands invalidate both reports. On every read show observation time; the TTL alone cannot detect external changes, so the caller must invalidate or refresh when it knows facts changed.

## Boundaries

Queue means a bounded safe coordination checkpoint, not waiting for an entire issue to finish. Pause requests safe suspension, not a process-name kill or aborted transaction. Resume needs a real host goal-resume capability; if absent, report the exact prerequisite once, never replace the goal. Root selects issues without duplicate leads and honours holds, current writers, budgets, real-data boundaries and configured merge/promotion authority.

Platform target is Windows10+/macOS/Linux with supported Python and SQLite. Tests on one host do not certify the others. Shell examples use quoted arguments; PowerShell can use py -3 instead of python3. Existing host tools provide the final message/goal action.
