# Credits

SwarmStack combines original tooling and guidance with adapted work by other authors. Imported skills are not presented as original SwarmStack inventions.

## Matt Pocock

[Matt Pocock's skills](https://github.com/mattpocock/skills) are the source of two customised workflows:

- **grill-with-docs:** [original skill](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs), [our entrypoint](skills/grill-with-docs/SKILL.md). The customised procedure adds the explicit Explanation → Current state → Question → lettered-options format, stable IDs, checked previous answers and exact decision recording.
- **code-review:** [original skill](https://github.com/mattpocock/skills/tree/main/skills/engineering/code-review), [our entrypoint](skills/code-review/SKILL.md). Our customised version keeps separate Standards/Spec reviews, adds a conditional Security specialist, severity labels, read-only reviewers and an evidence-based fix/rebuttal loop.

The workflow-improvement checklist also draws on his list of common agent-workflow mistakes supplied during toolkit design.

The customised procedures live in each skill's references/procedure.md. They are adaptations, not claims to match current upstream verbatim. Operational files omit attribution prose; code-review also replaces an unavailable setup command with project tracker lookup. Original and current procedure hashes are recorded in provenance.json. [Retained Matt Pocock MIT notice](licenses/matt-pocock.txt).

## Ayoub Ghriss

[Ayoub Ghriss's i-have-adhd](https://github.com/ayghri/i-have-adhd) informs [adhd-output](skills/adhd-output/SKILL.md). Our condensed adaptation keeps concise, action-oriented communication while avoiding forced timing estimates, repetitive narration and unnecessary user tasks. [Retained MIT notice](licenses/i-have-adhd.txt).

## Lauren Tan

[Lauren Tan / poteto](https://github.com/poteto) authored pstack’s [poteto-help](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/poteto-help/SKILL.md). Our [swarmstack-help](https://github.com/SasaSlivova-IS/SwarmStack/blob/main/skills/swarmstack-help/SKILL.md) adapts its read-only question routing, source-backed answers and suggested-prompt format to SwarmStack’s actual workflows. Cursor-specific setup, modes and unavailable skills are omitted. [Retained MIT notice](licenses/pstack.txt).

## Conceptual references

The imported code-review workflow's smell baseline uses the vocabulary of Martin Fowler's [Refactoring](https://martinfowler.com/books/refactoring.html), as identified in the original customised procedure. This credit is for the underlying concepts, not a bundled copy of the book.

[Artificial Analysis](https://artificialanalysis.ai/) is a referenced model-evaluation source. SwarmStack does not bundle live scores or claim authorship of its benchmarks.

## Original and future work

The standalone swarm command gate, setup installer, offline Pareto helper, project templates and setup/delivery/editing recipes were authored for SwarmStack. Shared ideas do not imply that their creators endorsed this toolkit.

When adapting another source, add the author, exact source, licence and modifications before publication. Keep [THIRD_PARTY.md](THIRD_PARTY.md), [provenance.json](provenance.json) and distributed central notices consistent. Do not include private-project examples, names or identifying context in attribution.

Creator credits and legal notices live in this file, THIRD_PARTY.md, provenance.json and licenses/. They are not part of skill-loading instructions. Project adoption carries these records under .swarmstack/. Distribute those records with copied skills; do not redistribute a standalone imported skill without its applicable copyright and licence notice.
