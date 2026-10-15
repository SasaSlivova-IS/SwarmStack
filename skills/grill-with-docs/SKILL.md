---
name: grill-with-docs
description: Ask grounded decision questions with explanation, current state and lettered choices.
disable-model-invocation: true
---

# Grill with docs

Load [the preserved customised procedure](references/procedure.md) when this skill is invoked. Do not load it for unrelated work.

Keep accepted answers and question IDs stable. Use the project glossary for shared terminology; use a domain-modeling skill only if actually available. A missing optional skill is not a reason to fabricate a definition.

The preserved source is retained byte-for-byte. SwarmStack's entrypoint adds portability notes; the source procedure may mention optional tools from its original environment. Follow host authority and the project's configured workflow.
