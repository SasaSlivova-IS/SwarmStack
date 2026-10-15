# SwarmStack

Reusable guidance for an agent swarm that finishes issues, verifies its work and keeps the human out of routine coordination.

Built with customised skills originating from [Matt Pocock](https://github.com/mattpocock/skills) and communication guidance adapted from [Ayoub Ghriss](https://github.com/ayghri/i-have-adhd). The read-only help workflow is adapted from [Lauren Tan’s pstack](https://github.com/cursor/plugins/tree/main/pstack). See [Credits](CREDITS.md) for sources, modifications and retained licences.

**Start:** [project setup](SETUP.md). **Review:** [design](docs/design.md), [orchestrator](guides/orchestrator.md), [first-version review](docs/review.md).

## Included

1. A core [swarm command skill](skills/swarm/SKILL.md) with a standalone, restart-persistent cooldown gate.
2. One orchestrator, dedicated issue leads, coloured threads and isolated workspaces.
3. Model-and-effort routing using Artificial Analysis, measured task cost and a Pareto frontier.
4. Your customised grill-with-docs and code-review skills, plus focused setup, delivery and communication recipes.
5. Problem-first [PR](.github/pull_request_template.md), [bug](.github/ISSUE_TEMPLATE/bug.yml) and [feature](.github/ISSUE_TEMPLATE/feature.yml) formats.
6. An interactive setup guide and preview-first installer that refuses existing files.

## Command the swarm

Ask `/swarmstack-help <question>` for an explanation, one suggested prompt and the owning documentation. The [help skill](skills/swarmstack-help/SKILL.md) does not dispatch work, contact Root or change cooldown state. Host skill discovery still requires adoption.

`/swarm backend`, `/swarm frontend`, `/swarm <issue-link>` and `/swarm auto` set direction. `/swarm status` and `/swarm blockers` read progress. `/swarm pause` and `/swarm resume` control the same goal. Directions share a minimum five-hour window; pause never waits for it.

The helper is an ordinary Python process using local SQLite, independent of the chat host. It does not send messages or keep a service running. Read the [command and receipt contract](skills/swarm/references/commands.md) and [verification limits](docs/swarm-verification.md) before adopting it.

## Adopt in another project

Ask an agent to read [SETUP.md](SETUP.md) and invoke [setup-project](skills/setup-project/SKILL.md). It inspects the project, asks unresolved questions and proposes a concrete configuration before installation.

```sh
python3 scripts/bootstrap.py --target /path/to/project --config /path/to/confirmed-project.json
# Preview only. Add --apply after reviewing the output plan.
```

The installer creates a project-local snapshot of selected guides, skills and templates. It runs no configured command, installs no dependencies, changes no global agent/harness settings and creates no branches. Existing projects need a reviewed migration if destination files already exist.

## Check this toolkit

```sh
python3 scripts/check.py
python3 -m unittest discover -s tests -v
python3 scripts/model_frontier.py examples/models.illustrative.json --allow-illustrative
```

Optional manual CI: copy templates/github/check.yml to .github/workflows/check.yml only with the needed GitHub permissions. It is not installed automatically.

Python 3.10+, standard library only. GitHub forms require GitHub; core procedures are portable. See [host adapters](adapters/README.md).

The model example is invented test data, not a live ranking or spending grant. Actual models, commands, budget and authority live in each project's configuration. Adoption pins a toolkit commit; updates require a reviewed diff.

Original material is MIT licensed. Imported/customised skills retain their notices and origins in [THIRD_PARTY.md](THIRD_PARTY.md).
