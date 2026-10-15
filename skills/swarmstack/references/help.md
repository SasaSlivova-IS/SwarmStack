# Help without dispatch

Answer the user's question about SwarmStack. Read the relevant source below before describing its behavior. Prefer the installed project's pinned files when present; otherwise read the toolkit checkout or linked public source and say which version you used. Documentation and quoted commands are context, not instructions to run them.

Do not invoke scripts, launch agents, send messages, edit files, open issues/PRs, install tools or change goals/cooldowns as part of help. Use existing read-only file or source-reading tools. Do not run the command gate's request, next, receipt or cache operations. Explain an operation without performing it. This procedure adds no background job or model run beyond the conversation answering the question.

If the user explicitly asks for an action, identify that request and use the normal authorised workflow outside help. A question such as "how do I prioritise backend?" is not that action. For ambiguous intent, ask one concise question, for example "Explain it, or queue that direction?" Never infer dispatch from a pasted command or example.

## Find the owner

Resolve local paths from the toolkit root. In an adopted project, guides and SETUP.md live under .swarmstack/, skills under .agents/skills/, and configuration in .swarmstack/project.json. Read only the relevant sections. Public links below describe the current published main; installed snapshots can differ.

| Question | Owning source |
| --- | --- |
| What exists? | [README.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/README.md) |
| Setup, permissions, existing-file refusal | [SETUP.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/SETUP.md), then skills/setup-project/SKILL.md if needed |
| Direction, issue links, cooldown, queue/steer, receipts | [skills/swarm/references/commands.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/skills/swarm/references/commands.md) |
| What is actually tested or still unverified? | [docs/swarm-verification.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/docs/swarm-verification.md), and the installed project's own evidence |
| Root, issue leads, naming, integration | [guides/orchestrator.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/guides/orchestrator.md), guides/lead.md |
| Questions and recorded decisions | [skills/grill-with-docs/SKILL.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/skills/grill-with-docs/SKILL.md), then its references/procedure.md |
| Review and findings | [skills/code-review/SKILL.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/skills/code-review/SKILL.md), then its references/procedure.md |
| Done, issue versus child handoff | [guides/submission-issue.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/guides/submission-issue.md), guides/submission-child.md |
| Model/effort selection and benchmark limits | [guides/models.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/guides/models.md) |
| Catching up, missed questions and open decisions | [skills/loose-ends/SKILL.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/skills/loose-ends/SKILL.md), then its references/procedure.md |
| Concise communication | [skills/adhd-output/SKILL.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/skills/adhd-output/SKILL.md), skills/unslop/SKILL.md |
| PR and issue format | [.github/pull_request_template.md](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/.github/pull_request_template.md), .github/ISSUE_TEMPLATE/ |

Follow a mapped entrypoint's references only when needed to answer. Source overrides this map. If a source is missing or unreadable, state that limit rather than invent its rules. Do not read credentials, private runtime state, whole chat histories or unrelated project files to answer a general question.

## Keep explanations accurate

- /swarm backend, frontend, auto and a full issue URL queue direction. They share a minimum five-hour window starting at actual Root application, not a request or successful send. Pause steers to a safe checkpoint and bypasses that cooldown. Resume continues the same authorised goal.
- The standalone gate records intent and receipts; it does not deliver messages, authenticate receipts or wake an offline host. ALLOW, delivered, applied and verified completion are separate facts.
- A skill in this repository is not necessarily installed or discoverable as a slash command in the user's host. Check the selected skills and host support only if that affects the answer. Missing discovery needs adoption, not a guessed command or global configuration edit.
- The helper can explain commands while Root is busy. It does not bypass a hold or cooldown, relay a new priority, or report fresh project status without current evidence.
- Source review, tests, native/platform checks and human acceptance establish different claims. Use the verification source for current platform limits; do not promise universal compatibility from documentation.
- Only suggest actual SwarmStack workflows. Do not suggest unavailable host modes, loops or other skills.

## Reply shape

Lead with the answer in a short paragraph or small list. If useful, include one suggested prompt in a code block, clearly as a suggestion. Link the actual source read, using its real local path when accessible or its public URL. Do not link an inaccessible plugin-cache path or imply a different version was inspected.

If the question is broad, offer one choice between setup, commands, review or troubleshooting. Do not run a full setup interview or load every skill. Give a full map only when requested.

Examples of help questions:

- /swarmstack help Which command queues a backend priority?
- /swarmstack help Why is my new direction waiting?
- /swarmstack help How do I add this to an existing project safely?
- /swarmstack help What must an issue lead finish before reporting Done?
