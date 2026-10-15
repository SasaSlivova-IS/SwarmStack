# Attribution placement

Research checked on 2026-10-15. Scope: the pinned MIT-licensed upstream material recorded in `provenance.json` and its distribution with this toolkit.

## Finding

Keep creator credits, provenance and complete upstream license notices outside operational skills and guides. For a complete toolkit distribution, central accompanying notice files are a reasonable way to preserve attribution without putting it in model instructions. This is an interpretation of the license text, not a legal guarantee about every distribution.

MIT permits modification and redistribution, subject to retaining the copyright and permission notices in copies or substantial portions. Its text does not prescribe a filename, require author biographies or credits inside every source file, or require an LLM to read the notices. Preserve the complete upstream license text, including the disclaimer, rather than trying to shorten the required material. [MIT license, OSI](https://opensource.org/license/mit)

GitHub documents a root license file as the usual placement and recommends including the license file with the project. That guidance supports repository-level placement; it does not establish that a license left behind on GitHub accompanies a separately copied skill. [GitHub licensing documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)

## Pinned upstream notices

All three checked snapshots use MIT and retain distinct copyright holders. Keep these exact notices, rather than replacing them with the toolkit author's copyright.

| Adapted material | Copyright holder | Checked upstream license |
| --- | --- | --- |
| code-review, grill-with-docs | Matt Pocock, 2026 | [skills at 49dd158d1076134a641b33efb035946536778336](https://raw.githubusercontent.com/mattpocock/skills/49dd158d1076134a641b33efb035946536778336/LICENSE) |
| adhd-output | Ayoub Ghriss, 2026 | [i-have-adhd at 1ecea1993b7fce257ffbd686c070948b5e07eda6](https://raw.githubusercontent.com/ayghri/i-have-adhd/1ecea1993b7fce257ffbd686c070948b5e07eda6/LICENSE) |
| swarmstack-help | Lauren Tan, 2026 | [pstack at e5136d82418d2db3165ea1050d17577cd618cc05](https://raw.githubusercontent.com/cursor/plugins/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/LICENSE) |

These findings cover the listed notices. They do not establish the origin or licensing of every change in customised local procedures. Keep that provenance qualification visible in the central records.

## Recommended packaging

1. Keep the toolkit's own `LICENSE` and the complete upstream notices in root-level `licenses/`. Use `CREDITS.md` for human-facing creator attribution, `THIRD_PARTY.md` to map adapted components to notices, and `provenance.json` for pinned revisions, hashes and modifications. A root license bearing only the toolkit author's name cannot substitute for the upstream notices. [MIT license](https://opensource.org/license/mit)
2. Remove attribution prose and attribution-only links from `SKILL.md`, operational references, guides and templates. Do not add automatic loading instructions for the central records. Those files remain available to people browsing the repository. This separation is a packaging recommendation, not an MIT requirement.
3. Ship the central records and complete license notices in every whole-toolkit archive and installation. The current bootstrap plans copies into `.swarmstack/`, alongside the installed skills. Preserve that behavior when removing skill-local notice files. This is a source inspection of [bootstrap.py](../../scripts/bootstrap.py), not a runtime check.
4. For an individually distributed skill, ship an archive containing `skills/<name>/` plus a sibling `licenses/` directory with the applicable full notices and a small component mapping outside the skill. Keep these files outside skill discovery and operational reading paths. Any future exporter should include notices by construction. This is a recommended implementation of MIT's inclusion condition. [MIT license](https://opensource.org/license/mit)

## Standalone copying limitation

Central notices work only while they accompany the distributed material. Copying just `SKILL.md`, a procedure, or a skill directory after removing its local notice can leave the recipient without the required notices. A credit URL, source URL or SPDX identifier alone does not include the actual copyright and permission text. Do not promise that arbitrary bare-file copying remains compliant; distribute the notice bundle with substantial copied material. MIT provides no numeric threshold for a substantial portion. [MIT license](https://opensource.org/license/mit)

Keeping notices outside operational text prevents this toolkit from instructing the model to load them. It cannot guarantee that every host avoids indexing or reading them; verify host discovery behavior separately. Any additional upstream licenses or uncertain provenance need their own review before redistribution.

## Applied change and verification

Operational skill entrypoints, references and required guides now omit creator credits. Central records and complete MIT notices remain distributed by bootstrap. Historical source hashes are retained alongside current hashes; the review procedure now uses confirmed tracker lookup instead of an unavailable setup command.

Independent Standards and Spec reviews initially found one remaining operational credit and two stale descriptions. All findings were validated, corrected and independently closed. Final Source reviews PASS with zero unresolved findings. Implementer verification: scripts/check.py PASS and44unittest cases PASS, including complete installed links, central notice bytes and absence of skill-local licence files. No live host/model-loading behavior was tested or claimed. No global installation or other project was changed.
