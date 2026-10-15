---
name: swarmstack
description: "Entry point for SwarmStack itself. \"/swarmstack setup\" sets SwarmStack up in a project after inspecting it and interviewing the owner; \"/swarmstack help <question>\" answers questions about SwarmStack. Use for /swarmstack commands."
disable-model-invocation: true
---

# SwarmStack

Route the first word after `/swarmstack`:

- **setup:** set SwarmStack up in the current project, or in the project the user names. Follow [setup-project](../setup-project/SKILL.md) completely: inspect first, interview with grill-with-docs, preview, and install only after the user confirms.
- **help:** follow the `swarmstack-help` skill with the rest of the message as the question. If that skill is not installed, say so and point to the README instead.
- Nothing or anything else: list these commands in two lines and ask which one is meant.

## Finding the toolkit

Setup needs a SwarmStack checkout to read SETUP.md and run its installer. Use, in order: the checkout this skill is part of; a path the user gives; `~/SwarmStack` if it exists. If none is found, say so and offer to clone https://github.com/SasaSlivova-IS/SwarmStack into a location the user confirms. Never clone, install or write without that confirmation.

If the project already contains `.swarmstack/`, it is already set up. Say so, show which toolkit commit it pins if recorded, and treat any change as a reviewed migration, not a fresh install.
