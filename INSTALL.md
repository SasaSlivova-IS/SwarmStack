# Install the project-local skills

Installation makes the commands available. Setup fills in the project's details afterward. You need Git and Python 3.10 or later; no Python packages are required.

## Install from a checkout

Clone the public toolkit outside your project, or use an existing reviewed checkout:

```sh
git clone https://github.com/SasaSlivova-IS/SwarmStack.git /path/to/SwarmStack
python3 /path/to/SwarmStack/scripts/install.py --target /path/to/project --host both
# Inspect the preview, then install those project-local files:
python3 /path/to/SwarmStack/scripts/install.py --target /path/to/project --host both --apply
```

Choose `--host codex`, `--host claude` or `--host both`. On Windows, use `py -3` instead of `python3` if needed. The target must already exist and be separate from the toolkit checkout. For a reproducible install, select a reviewed tag or commit in the toolkit checkout before running the installer.

The installer copies the canonical skills into .agents/skills/. Selecting Claude also creates project-local copies under .claude/skills/. It adds reusable guides, helpers, full licence notices and a draft project.json under .swarmstack/. It preserves existing AGENTS.md, application files and active GitHub templates. It installs no dependencies, changes no global settings and creates no branches or agents. Existing skill-file collisions or an existing .swarmstack installation stop the operation without overwriting them. Installation records the toolkit revision; it does not grant the swarm permission to run.

If a write fails, preserve the reported partial files and stop. Do not rerun installation over them or remove unrelated files. Review an exact recovery plan.

## Then configure the project

Refresh or restart the chat's skill discovery if necessary. Check that the project-local `/swarmstack` is available, then type:

```text
/swarmstack setup
```

Setup inspects the project, asks only unresolved questions, prepares its configuration and AGENTS.md integration, and applies the reviewed changes after approval. A project with files installed but setup unfinished reports **setup required**. Later setup invocations return a short message when configuration already exists. See [setup](SETUP.md).

Copying files does not establish that a host discovers or invokes them. Codex and Claude mappings are supplied as local files; verify discovery in the actual host. T3 uses the capabilities of its selected harness. No change to the host application or global skill folders is required.

## Let an agent do the installation

Paste this into the target project's chat if you prefer an agent to install it:

```text
Install the project-local skills from https://github.com/SasaSlivova-IS/SwarmStack in this project. Read its INSTALL.md first. Use a reviewed checkout outside this project and choose the local mappings for my current host. Show me the installer preview and obtain approval before applying it. Preserve existing files and global settings. Verify whether this host discovers /swarmstack, then stop; I will use /swarmstack setup to configure the project afterward.
```

The agent can inspect which host is in use and ask only if the mapping is ambiguous. Existing instructions or skill collisions require a reviewed integration, not blind replacement or a request that the user merge files by hand.
