# SwarmStack

SwarmStack is a set of instructions, skills and small Python scripts for running a team of AI coding agents on one project. One orchestrator hands each GitHub issue to its own lead agent. The lead builds the change, tests it and fixes review findings. You get asked only when a decision is actually yours to make.

Install the skills in a project first, then use `/swarmstack setup` to configure its instructions. After that, your agents read them like any other project guidance. It isn't a service and doesn't run in the background.

**Start here:** [install the skills](INSTALL.md), then [configure the project](SETUP.md). **To understand it first:** [design](docs/design.md), [orchestrator guide](guides/orchestrator.md), [glossary](docs/glossary.md).

## What's included

1. **Role guides** for the orchestrator, issue tracking, issue leads (frontend, backend, debugging, other work), user-facing chats, reviewers and child agents. See [guides/](guides).
2. **Thread rules:** one orchestrator, one dedicated lead and thread per issue, colour-coded roles and a separate workspace for each writer.
3. **Model selection guidance**, plus an offline script that compares models on quality, cost and speed and drops any option that another one beats on every count.
4. **Skills:** interview the user before decisions ([grill-with-docs](skills/grill-with-docs/SKILL.md)), review code ([code-review](skills/code-review/SKILL.md)), set up a project, submit finished work, write short, plain replies, and find loose ends ([loose-ends](skills/loose-ends/SKILL.md)).
5. **GitHub templates** for [pull requests](.github/pull_request_template.md), [bug reports](.github/ISSUE_TEMPLATE/bug.yml) and [feature requests](.github/ISSUE_TEMPLATE/feature.yml). Each one starts with the problem, not the solution.
6. **An installer** that shows you every file it plans to write, and refuses to overwrite anything that already exists.

## Steering the swarm

Type these in your user-facing chat:

| Command | What it does |
| --- | --- |
| `/swarm backend`, `/swarm frontend` | Prioritise ready backend or frontend issues. |
| `/swarm <issue-link>` | Prioritise one issue. |
| `/swarm auto` | Let the orchestrator choose again. |
| `/swarm status`, `/swarm blockers` | Show progress, or what is waiting on you. |
| `/swarm pause` | Stop starting new work right away. Running work is saved at a safe point. |
| `/swarm resume` | Continue the same goal from where it paused. |

Changes of direction (backend, frontend, issue link and auto) are limited to one every five hours, so the swarm isn't pulled back and forth. Pause and resume ignore that limit.

A small Python script keeps track of these commands in a local SQLite file, so the limit survives chat restarts. It doesn't send messages or run as a service. Before relying on it, read the [command contract](skills/swarm/references/commands.md) and [what has been verified](docs/swarm-verification.md).

Lost track? `/loose-ends cover` goes back through the current conversation and lists unanswered questions, offers nobody confirmed, contradictions and missing pieces. `/loose-ends catchup` catches you up on the whole project after time away, and `/loose-ends good morning` covers the night since your last message. Neither changes anything; open decisions come back as A–D questions.

Not sure what to ask? `/swarmstack help <question>` answers from the documentation, suggests one prompt and links the source. It doesn't start work or message the orchestrator. Your chat tool must be able to find the skill first; check that during setup.

The command split is simple: `/swarm` controls the running team; `/swarmstack` manages the project through setup, help, status, health and update. Standalone skills such as `/grill-with-docs` stay separate. Each project command loads its own procedure.

## Project toolkit commands

| Command | Purpose | Changes anything? |
| --- | --- | --- |
| `/swarm status` | Work finished, current progress, next steps and stalled work. | No, report only. |
| `/swarm blockers` | What is blocked, why, who can unblock it and user decisions needed. | No, report only. |
| `/swarmstack status` | Local installed version, enabled skills, configured host and modifications. | No network or writes. |
| `/swarmstack health` | Missing files, broken local links, unsafe paths and incomplete updates. | No repairs or project tests. |
| `/swarmstack update` | Fetch an upstream candidate, preview the diff and preserve local customisations. | Applies only after approval of the exact preview. |

There is no `/swarm health`. Update uses a clean, reviewed checkout and an exact approval ID. Conflicts stop application; settings, decisions, project state and swarm state stay preserved. Backups and interruption receipts stay local. See [update procedure](skills/swarmstack/references/update.md) and [verification](docs/project-management-verification.md). Actual host discovery and native platform support remain separate checks.

## Add it to a project

**1. Install the skills locally.** Clone the toolkit outside your project, then preview and apply the installation:

```sh
git clone https://github.com/SasaSlivova-IS/SwarmStack.git /path/to/SwarmStack
python3 /path/to/SwarmStack/scripts/install.py --target /path/to/project --host both
# After reviewing the preview:
python3 /path/to/SwarmStack/scripts/install.py --target /path/to/project --host both --apply
```

Choose `codex`, `claude` or `both`. The installer adds project-local skill files and reusable resources with a draft configuration. It leaves your existing AGENTS.md and application files alone. No global installation or project commands. See [installation instructions and a copyable agent prompt](INSTALL.md).

**2. Fill in the project details.** Refresh the host's skill discovery, then type `/swarmstack setup`. It inspects your codebase, asks about unresolved requirements and permissions, and prepares the project configuration and AGENTS.md integration for approval. Installation alone does not configure or start the swarm.

Existing configured projects get a short "already set up" message. Existing instructions and templates are integrated through a reviewed change; the agent prepares that work rather than asking you to merge files by hand. [Setup procedure](SETUP.md).

Each installation records a toolkit commit. Use `/swarmstack update` for a reviewed upgrade after project setup is complete.

## Check the toolkit itself

```sh
python3 scripts/check.py
python3 -m unittest discover -s tests -v
python3 scripts/model_frontier.py examples/models.illustrative.json --allow-illustrative
```

Requires Python 3.10 or later and uses only the standard library. The model data in `examples/` is made up for testing. It isn't a real ranking.

To run these checks on GitHub, copy `templates/github/check.yml` to `.github/workflows/check.yml`. It isn't installed automatically, because it needs workflow permissions on your repository.

The issue and PR templates need GitHub. Everything else works with any chat tool that can read project files; see [host adapters](adapters/README.md) for what to check.

## Credits and licence

Some skills are adapted from other people's work: grill-with-docs and code-review from [Matt Pocock](https://github.com/mattpocock/skills), the reply-style skill from [Ayoub Ghriss](https://github.com/ayghri/i-have-adhd), and the help skill from [Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack). [CREDITS.md](CREDITS.md) lists what was changed.

Original SwarmStack material is MIT licensed. Adapted material keeps its original notices in [THIRD_PARTY.md](THIRD_PARTY.md).
