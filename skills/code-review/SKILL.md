---
name: code-review
description: Run independent read-only Standards/Spec review, conditional Security and severity-labelled findings.
disable-model-invocation: true
---

# Code review

Based on [Matt Pocock’s code-review](https://github.com/mattpocock/skills/tree/main/skills/engineering/code-review), with the documented SwarmStack customisations. [Retained MIT notice](LICENSE.txt).

Load [the preserved customised procedure](references/procedure.md) when this skill is invoked. Do not load it for unrelated work.

Resolve the fixed point and originating requirement before delegating. The installed project supplies docs/agents/issue-tracker.md. If it is missing, read project configuration or the user-supplied tracker; do not assume an external setup command exists.

The preserved source is retained byte-for-byte. SwarmStack's entrypoint adds portability notes; the source procedure may mention optional tools from its original environment. Follow host authority and the project's configured workflow.
