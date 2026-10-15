# Host adapters

These are capability checks, not permission to modify a harness.

| Host | Adoption check |
| --- | --- |
| T3 Code | Verify AGENTS.md/skill discovery for the current harness. Top-level threads differ from delegated children; bind worktrees at creation. Shell cd does not change binding. Use only exposed queue/snooze/goal APIs. |
| Codex | Verify project AGENTS.md and .agents/skills discovery. Native collaboration and worktree capabilities vary; do not invent ordinary top-level conversation APIs. |
| Claude Code | Verify instruction/skill loading. Some versions need a reviewed .claude/skills mapping. Do not assume T3 queues/scheduling exist. |

Metadata-only discovery and progressive loading are targets, not cross-host guarantees. Confirm actual discovery before calling adoption verified. If multi-thread management is absent, preserve ownership with an explicit task ledger and supported sessions.

This toolkit installs no global plugin, timer, adapter or config change. Host-specific installation beyond the generated project files needs an explicit reviewed plan.
