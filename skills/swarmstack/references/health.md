# Project toolkit health

Inspect installation problems without repairing them. Run the installed .swarmstack/scripts/stack.py with `--project PROJECT health`, or the [checkout helper](../../../scripts/stack.py) if needed.

An installation awaiting setup reports setup_required; that is not permission to run the swarm.

The local helper checks managed files, manifest paths/hashes, Markdown links and unfinished update receipts. Missing/unsafe files, invalid configuration and broken links need attention. Changed files are reported as local modifications, not automatically called defects. A source-dirty installation is a provenance limitation. Never execute commands stored in configuration to check them.

Check actual skill discovery through read-only host metadata when available. Distinguish configured integration, files present and a skill actually discovered. If the host exposes no supported inspection, mark discovery unverified rather than invent a result. Do not open or drive another app to perform this check.

Report the concrete problem, consequence and next repair step. Do not edit files, install mappings, send Root messages, restart agents or run project tests. A healthy installation does not establish runtime/native/provider/UX acceptance. /swarm status and /swarm blockers own coordination questions; there is no /swarm health command.
