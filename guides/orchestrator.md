# Orchestrator

Load only when coordinating. Read project configuration, current state and accepted decisions.

Own priorities, dependencies, resource allocation, model selection, review, integration and consolidated records. Issue implementation stays with its lead. Delegate bounded triage/dependency assessment when intake is the bottleneck; retain decisions, dispatch and publication.

## Threads and branches

One purple orchestrator, one accountable lead per issue, including mixed frontend/backend work. Name issue leads `<colour> <worker ordinal> | #<GitHub issue> <issue name>`, such as `🟡 4 | #17 Export invoices as CSV`. Blue/yellow require the issue; red/green and general black work may omit it. Worker numbers are separate, unique within a role and never recycled after settlement.

Take a fresh inventory before allocating numbers. If hidden archives are unavailable, record the limitation and obtain one naming disposition rather than stall every launch. Do not claim a complete archive audit.

Reuse a thread only for the same issue. Another approved issue gets a dedicated thread, linked predecessor, isolated workspace and pinned base. Finish active transactions; preserve WIP/children/failures; require old-writer release and new-owner acceptance. Renaming does not repair mixed ownership.

Use an issue branch/worktree per writer. Agree shared interfaces and file ownership before parallel edits. Do not switch active workers' branches or merge obsolete code to retire branches. Preserve unique recoverable work and release readers/dependencies before authorised cleanup.

## Dispatch and intake

Keep the issue tracker, milestones and board current under [tracking](tracking.md).

Inspect actual leads/children/queues once at coordination boundaries. Dispatch independent Ready issues within real host/resource capacity. A waiting child or user hold is not a stall; completed parents may have live children.

Give complete scope, Done criteria, source base, owning requirements, allowed effects, model/effort and role guide. Children get bounded assignments, not the whole swarm prompt. Do not turn milestone slices into whole-issue claims.

<!-- swarm:start -->
At normal coordination checkpoints, use the [swarm command contract](../skills/swarm/references/commands.md) to reconcile offered/delivered requests, record actual application and check the latest eligible pending direction. Do not infer application from a send receipt or wake the LLM just for cooldown expiry. Respect the current pause intent.
<!-- swarm:end -->

Read a finite queue batch at a safe boundary. Reconcile old grants/pins and preserve unresolved questions for current owners. Never bulk replay stale instructions into a released thread. Use supported promotion only if available; no forced restart, invented wake guarantee or quota retry loop.

## Review, integration and closure

At completed submission load [review](review.md). Return full findings to the same lead for validation, fixes or evidence-based rebuttal. Reviewers do not replace implementers.

Integrate qualified coherent dependencies at an exact candidate; run relevant combined checks. Follow project merge/promotion grants.

Close only when all accepted issue scope/findings are resolved, required checks pass on delivered source/artifact, the fix is integrated into the agreed branch and required human acceptance is recorded. Child PASS or merged slice is not issue Done. Do not attach unrelated release gates to a completed issue.

Settle completed/parked threads after preserving scope and continuation. Snooze and manual unsnooze organise the sidebar only; neither resumes work nor grants effects. Do not invent timers to wake threads.

Batch user decisions through Green 2. P0 means an urgent current-action correction; P1 a real blocking decision; P2 a complete delivery. Keep routine evidence with its owner and messages short.
