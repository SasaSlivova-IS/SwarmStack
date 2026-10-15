# Working on {{PROJECT_NAME}}

Shared development instructions, not the runtime prompt. Follow the user and higher-priority host instructions. Read this file, your role guide and applicable nested AGENTS.md before edits.

Read [.swarmstack/project.json](.swarmstack/project.json) for scope, models, commands, branches and effects. Inspect status and preserve WIP. Keep secrets/real data out of synthetic fixtures. No implicit spending, account, deployment or production authority.

One purple orchestrator coordinates. Each issue has one dedicated lead thread, reused only for that issue. Names use `<colour> <worker ordinal> | #<GitHub issue> <issue name>`, for example `🟡 4 | #42 NDA egress and text anonymization`. Blue/yellow require issues; red/green and general black work may omit them. Preserve worker identity and explicit workspace binding.

Load only your role: [orchestrator](.swarmstack/guides/orchestrator.md), [frontend](.swarmstack/guides/frontend.md), [backend](.swarmstack/guides/backend.md), [debugging](.swarmstack/guides/debugging.md), [other](.swarmstack/guides/other.md) or [user-facing](.swarmstack/guides/user-facing.md). Issue leads also load [lead](.swarmstack/guides/lead.md). Children receive bounded assignments, not every role's instructions.

Continue complete authorised outcomes through checks, review and corrections. A child PASS, source review or merged slice is not issue Done. Required checks, resolved findings, agreed integration and required human acceptance determine closure. Escalate real blockers, not routine next steps.

Read [models](.swarmstack/guides/models.md) only for intake/delegation and [review](.swarmstack/guides/review.md) at submission. Keep temporary limits in the task and requirements/terminology in their owning project files.

<!-- swarm:start -->
Use [swarm](.agents/skills/swarm/SKILL.md) only for user-facing commands and normal pending-command checkpoints; it grants no new effects.
<!-- swarm:end -->

Current state: [.swarmstack/state.md](.swarmstack/state.md). Accepted setup: [.swarmstack/decisions.md](.swarmstack/decisions.md). Issue workflow: [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md).
