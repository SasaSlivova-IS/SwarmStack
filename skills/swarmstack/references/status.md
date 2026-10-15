# Project toolkit status

Report the project's installed toolkit state, not its issue progress. Use the current target project, or the explicit project the user names.

Run the installed .swarmstack/scripts/stack.py with `--project PROJECT status`, or the [checkout helper](../../../scripts/stack.py) if the installation predates it. This reads local configuration, manifest hashes and update receipts. It makes no network request, writes no cache and runs no configured project command.

Lead with not installed, installed but setup required, configured, or incomplete, the pinned revision, installed skills, selected host mappings and the configured orchestration host when available. A draft installation has not enabled the swarm. Mention local modifications and unfinished updates when present. Host configuration is not proof of actual skill discovery. Do not claim upstream is current; report "not checked" unless the user explicitly requests an upstream lookup. Show observation time when reporting stored or external facts.

Do not message Root, open a goal, refresh the toolkit or repair anything. For work progress and blockers, direct the user to /swarm status and /swarm blockers. For installation problems, suggest /swarmstack health without running it automatically. Keep the answer short rather than dumping the helper JSON.
