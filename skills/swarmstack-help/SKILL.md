---
name: swarmstack-help
description: Answer questions about SwarmStack setup, skills and swarm commands without dispatching work. Invoke /swarmstack-help with a question.
disable-model-invocation: true
---

# SwarmStack help

Adapted from [Lauren Tan's /poteto-help](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/poteto-help/SKILL.md). [Retained MIT notice](LICENSE.txt).

Load [the help procedure and source map](references/help.md) on invocation. Read only the owning documentation needed for the question.

Answer first, offer at most one suggested prompt or command, and link the source you actually read. Suggestions are text, not permission to execute them.

Help is read-only. Do not dispatch agents, message the orchestrator, run commands, change cooldown state or start another skill's workflow to explain it. It can answer while the swarm works.

An explicit request to perform work leaves help mode and requires the normal workflow and existing grants. If intent is unclear, ask one short question before taking effects.
