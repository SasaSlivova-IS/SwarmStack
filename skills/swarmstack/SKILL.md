---
name: swarmstack
description: Manage project setup, local status and health, previewed toolkit updates, or documentation help. Use /swarmstack setup, status, health, update or help <question>.
disable-model-invocation: true
---

# SwarmStack

Route only the first word after `/swarmstack` and load only its procedure:

- **setup:** [project setup](references/setup.md). Inspect, interview, preview and obtain confirmation before installation.
- **help:** [documentation help](references/help.md). Answer without running commands, dispatching work or messaging Root.
- **status:** [installed state](references/status.md). Read local version, selected skills and configuration.
- **health:** [installation checks](references/health.md). Find missing files and broken mappings without repairs.
- **update:** [reviewed toolkit update](references/update.md). Fetch a candidate, preview differences and obtain approval before apply.
- Nothing or an unknown command: list setup, help, status, health and update briefly, then ask which is intended. Do not guess an action.

`/swarm` handles team direction, status, blockers, pause and resume. Standalone skills such as `/grill-with-docs` remain independent. A setup or help question does not steer the running swarm.
