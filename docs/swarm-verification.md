# Swarm command verification

## Requested behavior

A core user-facing swarm skill backed by a standalone Python/SQLite gate, outside any chat host. Direction commands use a shared minimum five-hour window, full issue links and normal queue delivery. Pause steers without cooldown; status/blockers read facts; resume continues the same goal. Durable state must survive process restarts without a scheduler or automatic LLM wake.

## Candidate verification

All42 local tests pass on macOS with Python3.11 and3.14. A Python3.10 grammar check passes; it is not a3.10 runtime test. Test coverage includes initial apply/delivery separation; five-hour expiry; pending coalescing and cancellation; repeated receipts/IDs; cross-project URL refusal; cache expiry/invalidation; pause/resume ordering; corrupt/busy state pause fallback; concurrent claims; process-exit recovery; actual abrupt exits before and after SQLite commit; configuration/binding refusal; symlink refusal; and paths containing spaces/non-ASCII characters. The existing setup tests exercise installed skill/script links, unchanged default-false effects, no overwrite and command nonexecution.

The helper performs no network call or bot operation. Host message delivery, receipt authentication, live goal resume and offline wake are outside its guarantees and need the adapter contract.

## Platforms

The implementation targets Python3.10+ with sqlite3 on Windows10+, macOS and Linux using pathlib, subprocess argument lists and SQLite transactions. No shell-specific command, host SDK or third-party package is required.

Actual native execution is currently macOS only. A bounded Windows SSH version probe could not authenticate with the existing route; no credentials were requested, reset or installed. No local Linux container runtime was available and the previously known Linux peer was offline. No other hosts were scanned. These are native-test limits, not claimed compatibility passes.

The optional manual CI template covers ubuntu-latest, macos-latest and windows-latest. It is not installed or run automatically and needs the repository's workflow publishing authority. A host unable to create the symlink test fixture reports that one test as skipped, never as a tested refusal.

## Review and publication

Independent fixed-candidate Standards, Spec and Security correction reviews PASS with zero open findings at62a323e. [Separate reports](reviews/swarm-core-reviews.json) preserve each original severity and correction verdict. Three new regression scenarios genuinely failed before correction: repeated inflight direction was offered again, whitespace pause lost its unavailable-state fallback, and legacy six-skill adoption installed missing links. They pass after correction. The duplicated-options maintainability finding was addressed by one shared validator. Original source and review findings remain distinguishable from actual host/runtime proof. The command gate is a trusted local convenience layer, not a security permission system or exactly-once distributed transaction. Unknown delivery remains held for supported host-key reconciliation.
