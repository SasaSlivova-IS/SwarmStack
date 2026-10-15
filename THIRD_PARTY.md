# Third-party material

See [Credits](CREDITS.md) for visible author attribution and the modifications to each adapted skill.

- **code-review and grill-with-docs:** user-customised local copies attributed to [Matt Pocock skills](https://github.com/mattpocock/skills). Their customised procedures are under skills/*/references/procedure.md; current and original hashes are recorded in provenance.json. Short entrypoints make loading task-triggered; attribution is centralised here rather than in loaded instructions. The review procedure replaces an unavailable setup command with confirmed tracker lookup. The customised procedures are not claimed to match current upstream. [Upstream MIT notice](licenses/matt-pocock.txt).
- **grill-with-docs format:** the customised version requires Explanation → Current state → Question → lettered options, stable question IDs, checking prior answers and recording actual decisions. The short entrypoint loads the preserved full procedure on invocation. It is not the unmodified upstream text.
- **adhd-output:** condensed adaptation of [Ayoub Ghriss's i-have-adhd](https://github.com/ayghri/i-have-adhd). Keeps action-first concise formatting; does not force ungrounded estimates, repeated narration or unnecessary questions. [MIT notice](licenses/i-have-adhd.txt).
- **swarmstack-help:** adapted from [Lauren Tan’s poteto-help](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/poteto-help/SKILL.md) and its prompting/recipes references. Replaces pstack routing with SwarmStack sources, keeps help read-only and omits Cursor-specific workflows. [MIT notice](licenses/pstack.txt).
- **swarm, unslop, setup-project and delivery:** original SwarmStack recipes. The unslop name describes the requested prose cleanup; no unknown-license local implementation is redistributed.
- Model evidence workflow refers to [Artificial Analysis](https://artificialanalysis.ai/), not bundled live scores. No ranking data is copied.

Pinned license revisions, source hashes and modifications are recorded in provenance.json. Only reusable material is included; private project details, secrets and raw session transcripts are excluded.

## Distribution

Full notices remain in licenses/. Bootstrap includes them with CREDITS.md, THIRD_PARTY.md and provenance.json under .swarmstack/, outside skill-loading paths. Keep the relevant notices with any separate skill distribution, even when the operational Markdown omits attribution. These records are not required reading for normal skill execution.
