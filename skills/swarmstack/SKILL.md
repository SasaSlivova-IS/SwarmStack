---
name: swarmstack
description: Manage project setup with /swarmstack setup, or ask documentation questions with /swarmstack help <question>. Swarm controls live team activity separately.
disable-model-invocation: true
---

# SwarmStack

Route only the first word after `/swarmstack` and load only its procedure:

- **setup:** [project setup](references/setup.md). Inspect, interview, preview and obtain confirmation before installation.
- **help:** [documentation help](references/help.md). Answer without running commands, dispatching work or messaging Root.
- Nothing or an unknown command: list setup and help briefly, then ask which is intended. Do not guess an action.

`/swarm` handles team direction, status, blockers, pause and resume. Standalone skills such as `/grill-with-docs` remain independent. A setup or help question does not steer the running swarm.
