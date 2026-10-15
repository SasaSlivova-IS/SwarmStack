# Project setup

Set SwarmStack up in the current project, or the project the user names. Read [the setup guide](../../../SETUP.md), then use [grill-with-docs](../../grill-with-docs/SKILL.md). Inspect first, interview in short batches, record exact answers, propose concrete configuration, preview the installer output and obtain confirmation before apply. Defaults and silence are not grants.

## Find the toolkit

Setup needs a SwarmStack checkout for its installer. Use the checkout this skill belongs to, a user-supplied path, or ~/SwarmStack if present. An adopted project's .swarmstack directory contains a snapshot, not the complete toolkit. If no checkout exists, report that prerequisite and offer to clone the public repository into a location the user confirms. Do not clone or install without confirmation.

## Existing projects

If .swarmstack already exists, inspect its project configuration and pinned revision if recorded. Its presence alone does not prove a complete installation. Any updates or partial-install recovery need a reviewed migration preserving existing files, not a blind fresh install.

Legacy configuration names setup-project and swarmstack-help map to swarmstack during new adoption. They do not create additional slash commands. Existing installed skill directories are not deleted or overwritten by bootstrap; propose their removal only as part of an explicitly approved migration.

Follow the full setup guide through verification. Toolkit installation is separate from actual host skill discovery and the adopted project's runtime checks. Do not change live swarm direction or Root state as a side effect of setup.
