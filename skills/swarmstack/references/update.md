# Update the project toolkit

If the project is installed but still draft, direct the user to /swarmstack setup first.

Update SwarmStack instructions and tooling, not the project's application code or live swarm direction. An /swarmstack update request authorises retrieving a candidate and preparing a preview. It does not authorise applying an unseen update.

## Fetch and review a candidate

Use an isolated checkout outside the target project from https://github.com/SasaSlivova-IS/SwarmStack. Fetch the user's selected tag/commit, or main when none is specified. Record the exact commit and verify the repository URL. Do not switch an active toolkit checkout, alter global skill links, fetch private project data or recurse into submodules. This network lookup is explicit update work; status and health stay local.

Read the installed .swarmstack/project.json and lock.json, the public candidate diff and changes to scripts/update.py, bootstrap.py and stack.py before executing the fetched updater. Stop on unclear provenance or unexpected execution/data access. Do not execute project commands, hooks or a substituted repository's updater. If the installed pin is unavailable upstream, disclose the missing comparison and obtain the user's approval of the reviewed candidate code before executing it.

Run `python3 SOURCE/scripts/update.py --project PROJECT` from the clean, reviewed candidate. It renders that version's selected toolkit files and prints proposed additions/replacements/removals, diffs, local files preserved, conflicts and an approval ID. It does not write the project. Keep the full preview local; show a concise summary and relevant changes for the user to approve. Do not publish project-specific previews to the toolkit repository.

## Apply only the approved preview

Resolve conflicts with a separately reviewed merge. Do not overwrite local customisations or erase local deletions to make the preview green. The updater preserves project.json, state.md, decisions.md and local swarm state. Unsupported configuration/migrations remain blocked, not reset to defaults. Show any legacy skill-file removals in the preview.

After the user approves the exact preview, coordinate a safe boundary with the project's instruction writers. Run `python3 SOURCE/scripts/update.py --project PROJECT --apply APPROVAL_ID` against the same clean candidate. A changed source, project state or approval ID invalidates approval and needs a new preview. The updater refuses unresolved conflicts and backs up replaced/removed files plus the original lock under .swarmstack/local/updates/ before changes. Keep this directory private and out of version control.

If interrupted, preserve the backup/receipt, report actual changed files and stop. This is not an all-files atomic transaction. Do not automatically retry, roll back or claim completion from partial writes. Reconcile the exact receipt and project state before a separately approved recovery. Hostile concurrent writers and network filesystems are outside this local updater's guarantees.

After a complete receipt, run the local toolkit health report. Report the installed pin and preserved customisations. Host discovery and application runtime checks remain separate; do not restart sessions, change a goal, merge branches, install dependencies or claim a whole feature is verified.
