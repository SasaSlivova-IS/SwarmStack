# Host adapters

These are capability checks, not permission to modify a harness.

| Host | Adoption check |
| --- | --- |
| T3 Code | Verify AGENTS.md/skill discovery for the current harness. Top-level threads differ from delegated children; bind worktrees at creation. Shell cd does not change binding. Use only exposed queue/snooze/goal APIs. |
| Codex | Verify project AGENTS.md and .agents/skills discovery. Native collaboration and worktree capabilities vary; do not invent ordinary top-level conversation APIs. |
| Claude Code | Verify instruction/skill loading. The installer’s claude/both option creates project-local .claude/skills copies. Do not assume T3 queues/scheduling exist. |

Metadata-only discovery and progressive loading are targets, not cross-host guarantees. Confirm actual discovery before calling adoption verified. If multi-thread management is absent, preserve ownership with an explicit task ledger and supported sessions.

This toolkit installs no global plugin, timer, adapter or config change. Host-specific installation beyond the generated project files needs an explicit reviewed plan.

Installation uses `scripts/install.py --host codex|claude|both`, with preview before --apply. It copies files and records a draft; /swarmstack setup configures the project afterward. Canonical .agents/skills files are always present, and Claude mappings are also recorded in the installation manifest so updates preserve them. Actual discovery still needs verification in the host.

## Standalone command gate

The swarm helper is Python/SQLite, not a host plugin or in-process timer. Project-local state survives host restarts. The adapter must map queue/steer/wake/read to supported APIs, pass stable idempotency keys, and distinguish delivery from actual application. Unknown delivery remains held when lookup/dedup is unsupported. No offline wake or pause/resume capability is invented. Use the [command contract](../skills/swarm/references/commands.md).
