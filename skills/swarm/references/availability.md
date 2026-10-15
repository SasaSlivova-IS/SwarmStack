# Day and night availability

Load only for `/swarm day` or `/swarm night`. Availability describes whether to expect the user's replies. It does not change priorities or permissions.

## Request and delivery

1. Read confirmed project configuration, current goal/checkpoint and accepted limits. Keep model budgets, protected resources, merge authority and issue owners unchanged. Do not ask the user to repeat settled instructions.
2. Submit the exact command through the existing helper with the original user-message ID. State is in the canonical project's local SQLite file, outside the chat host. Both commands queue at a safe coordination checkpoint and bypass the direction cooldown without resetting it.
3. Relay an ALLOW once using its transport key. Record the actual delivery receipt. A failed or uncertain send is not application; reconcile the same key through the host rather than creating a second command. Report a genuine host blocker once.
4. Before applying, Root inspects `latest_availability` and `availability_request`. Apply only the matching command. A newer day/night intent supersedes an older queued intent; retain old receipts. Record `applied` only after the corresponding handoff is adopted in Root's owning state.

`inspect` reports the latest requested mode/state separately from `availability`, the last mode whose current-command application was recorded, plus its application command/time. No mode is assumed for an older installation. A late receipt for an older mode cannot overwrite the latest mode. A repeated same-mode request returns ALREADY_REQUESTED or ALREADY_ACTIVE without another relay. Failed requests permit a fresh explicit request; uncertainty is not failure.

## Night handoff

Root records one compact checkpoint containing the existing goal, priorities, ready issue owners/dependencies, model/provider limits, protected resources and where pending questions go. Reference existing records rather than copy histories. Night is not a new goal or a larger grant.

- Continue independent authorised work through existing issue leads, review, correction and permitted integration. A user-blocked issue must not block unrelated ready work.
- Send questions to the configured user-facing channel when discovered, retaining stable topic IDs and Needs-user tracking. Expect no prompt reply. Silence never approves an action.
- Inspect real running/waiting work before concluding that coordination has stalled. A live child, known quota reset or explicit hold is not itself a stall.
- Inspect existing permitted native quota auto-resume arrangements for admitted threads. Report the actual provider/account, visible setting and reset if exposed; an enabled setting is not proof a later run started. Day/night never toggles a setting. Missing setup is a separate action requiring explicit authorisation outside this command. Checkpoint on exhaustion; no repeated quota retries, subscription purchases or account changes.
- If the host cannot continue or auto-resume is unavailable, record the limitation honestly. Do not add timers, watchers, a daemon or reset-time messages. This command does not keep a stopped app or offline computer running.

Day/night do not create owners, change models or spending grants, unlock resources, start tests/builds, merge without existing authority or override a pause. A paused goal stays paused; Root may record the handoff without resuming product work. Use `/swarm resume` separately when authorised. No work is dispatched by the local helper.

## Day handoff

Mark the user available for batched decisions, meaningful updates and review-ready work through the configured channel. Do not interrupt every active lead or assume the user will reply immediately. Continue the same priorities, model limits and protected-resource rules. Day does not disable existing approved auto-resume settings or undo night-time work.

Do not generate a catch-up report automatically. The user can separately invoke `/loose-ends good morning`, which only reports completed/current work, pending decisions and verification limits. It never switches mode, messages Root or dispatches work.

## Restart recovery

At ordinary coordination checkpoints, inspect the canonical gate and reconcile requested/delivered/applied state with actual host receipts and Root's checkpoint. The last applied mode remains across process/chat restarts; unresolved delivery stays unresolved. Read the latest availability directly instead of relying on a cached status report. Do not copy the database into another worktree or infer a mode from the clock.

Morning example: `/swarm day`, followed by `/loose-ends good morning`. Without the first command, a morning brief leaves night mode unchanged.
