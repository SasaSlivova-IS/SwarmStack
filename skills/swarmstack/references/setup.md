# Configure the project

This command fills in a project after the project-local skills are installed. It does not perform initial installation.

## Check the phase first

Read only the target's .swarmstack/lock.json and project.json first. If both describe a configured installation, or a legacy confirmed setup, reply:

> SwarmStack setup already exists in this project. Nothing was changed.

Then stop without an interview, checks or an automatic migration offer. This reports recorded setup, not runtime readiness.

If the package has an installed-phase lock and a draft configuration, continue with [the setup guide](../../../SETUP.md) and [grill-with-docs](../../grill-with-docs/SKILL.md). Inspect the project, reuse checked facts, interview in short batches, record exact answers, propose project settings and AGENTS.md integration, and obtain approval before applying the configuration. Defaults and silence are not grants.

If no local installation exists, direct the user to [installation](../../../INSTALL.md) and stop. If records are incomplete or inconsistent, report that prerequisite without guessing, reinstalling or calling the project configured. Inspection or repair is separate authorised work.

## Use the installed revision

Configuration uses a clean toolkit checkout at the revision in the installation lock, not an arbitrary newer checkout. Find that checkout through the current skill source, a user-supplied path or ~/SwarmStack. The installed .swarmstack directory is a snapshot, not a complete checkout. Obtain permission before creating a missing checkout; preserve any existing checkout and active work.

Follow the setup guide through a configuration preview, exact approval, recorded application and verification. Preserve the Codex/Claude mappings selected at installation. For existing AGENTS.md or templates, the agent prepares and reviews the integration; --keep-existing is only for explicitly approved retained files and is not proof of a complete integration. Never reset project rules, run application commands or change live swarm direction just to configure the toolkit.
