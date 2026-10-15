# Project management command verification

The approved interface keeps /swarm status and blockers for coordination, and adds /swarmstack status, health and update for the project's installed toolkit. There is no /swarm health command. Each project command loads a separate procedure.

Status and health use a local, read-only standard-library helper. They report installed manifest facts, local modifications, missing files, links and unfinished update receipts. They do not fetch upstream versions, run configured project commands or establish host discovery/runtime acceptance.

Update retrieves a reviewed upstream checkout through the command procedure. Its helper previews changes and conflicts, then requires the exact approval ID. Project settings, decisions, execution state and local swarm data are preserved. Changed source/project state invalidates the preview. Backups and receipts remain local; interrupted updates require reconciliation and are not automatically retried or rolled back. Application is not atomic across all files and excludes hostile concurrent writers/network filesystems.

## Results

Against base46aff2e2811d9fc7859291e08acab81d0177f576, local static checks and63unittest cases PASS on macOS. Disposable real Git sources/projects exercise installed standalone health, clean-source update preview and approved apply, local-only edits, conflicting edits, stale source/project approvals, backups, addition/removal, symlink refusal, private-data path rejection and injected disk failure with blocked retry. Configured project commands are not executed.

Independent Standards, Spec and Security Source reviews finish PASS with zero unresolved findings. Initial review found incomplete configuration validation, protected-record case aliases, and repeated receipt serialization. Correction review found a malformed optional-host edge. Findings were validated and corrected; shared validation is used by installation, reports and the gate. Regression cases first failed for nine configuration/path subcases and then four optional-host subcases before passing. The initial path allowlist also rejected the installer's local ignore file; its exact canonical path is now admitted. Original failures are not represented as passes.

Case-alias rejection is tested before mutation; no native case-alias deletion exploit was claimed. Native Windows/Linux, actual online update retrieval and live host slash-command invocation remain unverified. Fetching/reviewing a public revision is specified by the update procedure; the updater itself uses that reviewed local checkout and makes no network request. No running project or global host configuration was updated.
