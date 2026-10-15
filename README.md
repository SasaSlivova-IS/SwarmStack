# SwarmStack

SwarmStack is a set of instructions, skills and small Python scripts for running a team of AI coding agents on one project. One orchestrator hands each GitHub issue to its own lead agent. The lead builds the change, tests it and fixes review findings. You get asked only when a decision is actually yours to make.

You copy SwarmStack into a project once. After that, your agents read it like any other project instructions. It isn't a service and doesn't run in the background.

**Start here:** [set up a project](SETUP.md). **To understand it first:** [design](docs/design.md), [orchestrator guide](guides/orchestrator.md), [glossary](docs/glossary.md).

## What's included

1. **Role guides** for the orchestrator, issue leads (frontend, backend, debugging, other work), user-facing chats, reviewers and child agents. See [guides/](guides).
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

Changes of direction (the first four rows) are limited to one every five hours, so the swarm isn't pulled back and forth. Pause and resume ignore that limit.

A small Python script keeps track of these commands in a local SQLite file, so the limit survives chat restarts. It doesn't send messages or run as a service. Before relying on it, read the [command contract](skills/swarm/references/commands.md) and [what has been verified](docs/swarm-verification.md).

Lost track? `/loose-ends cover` goes back through the current conversation and lists unanswered questions, offers nobody confirmed, contradictions and missing pieces. `/loose-ends catchup` catches you up on the whole project after time away, and `/loose-ends good morning` covers the night since your last message. Neither changes anything; open decisions come back as A–D questions.

Not sure what to ask? `/swarmstack-help <question>` answers from the documentation, suggests one prompt and links the source. It doesn't start work or message the orchestrator. Your chat tool must be able to find the skill first; check that during setup.

## Add it to a project

Ask an agent to read [SETUP.md](SETUP.md) and run the [setup-project](skills/setup-project/SKILL.md) skill. It reads your project, asks about anything it can't work out, and shows you a configuration to approve before installing anything.

```sh
python3 scripts/bootstrap.py --target /path/to/project --config /path/to/confirmed-project.json
# This only previews. Add --apply once you have reviewed the plan.
```

The installer copies the guides, skills and templates you selected into the project. It doesn't run project commands, install dependencies, change global agent settings or create branches. If the project already has files at those paths, the installer stops, and you have to merge them by hand.

Each project uses a fixed SwarmStack commit. To update, review the diff and install the new version.

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
