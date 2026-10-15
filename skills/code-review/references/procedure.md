---
name: code-review
description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards and Spec — with a third Security reviewer for security-related issues or PRs. Runs read-only reviews in parallel sub-agents and reports severity-labelled findings side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
---

Two-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the originating issue / PRD / spec?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

For a security-related issue or PR, add **Security** as a third axis. Keep the ordinary review at two axes; do not add a security reviewer to every change.

The issue tracker should have been provided to you — run `/setup-matt-pocock-skills` if `docs/agents/issue-tracker.md` is missing.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point — a commit SHA, branch name, tag, `main`, `HEAD~5`, etc. If they didn't specify one, ask for it.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here — not inside two parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. Issue references in the commit messages (`#123`, `Closes #45`, GitLab `!67`, etc.) — fetch via the workflow in `docs/agents/issue-tracker.md`.
2. A path the user passed as an argument.
3. A PRD/spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** sub-agent will skip and report "no spec available".

### 3. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below — a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation — and, like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 4. Spawn the review sub-agents in parallel

Send a single message with two `Agent` tool calls, or three when Security applies. Use the `general-purpose` subagent for each, with the caller's approved models and orchestration tools.

**When Security applies:** the issue/PR explicitly concerns security, or its actual changes affect a security boundary such as authentication, permissions, private data, credentials, untrusted input, sandboxing or network exposure. Check the originating request and diff, then state the trigger in one sentence. Ordinary presentation changes do not need this reviewer merely because the repository contains security-sensitive code.

**Shared rules for every sub-agent** — include:

- Read-only review: do not edit source, tests or records; change the index, HEAD or branches; fix findings; or post GitHub comments. Inspect code, history and existing evidence. Any execution needs a separately authorised isolated fixture and must not mutate the delivered source. Do not spawn additional reviewers.
- Label every finding **Critical**, **Important** or **Minor**, based on its actual consequence. **Critical**: severe security compromise, data loss or a widespread failure requiring immediate correction. **Important**: a material defect, missing requirement or verification gap that must be resolved before acceptance. **Minor**: a small improvement or nonblocking judgement call. Do not promote a code smell to a serious defect without evidence.
- Give the location, requirement or rule, concrete trigger, consequence and supporting evidence for each finding. Distinguish observed defects from unverified risks; mark required but unavailable checks explicitly.

**Standards sub-agent prompt** — include:

- The full diff command and commit list.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full — the sub-agent has no other access to it.
- The brief: "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent prompt** — include:

- The diff command and commit list.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

**Security sub-agent prompt** — include only when Security applies:

- The full diff command and commit list, the originating security issue/PR and the trigger identified above.
- Relevant security requirements, threat model and trust boundaries already documented in the repository.
- The brief: "Review the changed security boundary and its affected callers. Check whether authentication, permissions, private-data handling and failure/recovery behavior preserve the documented guarantees. Identify concrete bypasses or missing required controls, including relevant edge cases. Do not invent requirements or perform live exploits. Follow the shared read-only and severity rules; cite source and evidence for every finding. Under 400 words."

### 5. Aggregate

Present the reports under `## Standards` and `## Spec` headings, plus `## Security` when that reviewer ran, verbatim or lightly cleaned. Preserve each finding's severity and evidence. Do **not** merge or rerank findings across axes — the axes are deliberately separate (see _Why separate axes_). If Security did not apply, say so briefly.

End with a one-line summary: finding counts by severity per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes — that's the reranking the separation exists to prevent. A source-review verdict does not prove an unrun end-to-end workflow.

### 6. Resolve findings

Return the full reports to the implementer. The implementer checks each bug claim against the requirements, source and reproduction, then fixes valid Critical/Important findings or rebuts them with concrete evidence. A rebuttal is not dismissal: the reviewer checks the counter-evidence before the finding is closed. Record Minor findings without silently turning them into new scope.

After corrections, review the changed candidate and affected findings. Keep the original request, prior findings, fixes and rebuttals in the next review brief. Reviewers remain read-only; the implementer owns fixes. Unresolved material findings or missing required proof prevent acceptance.

## Why separate axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**
- Code that meets the written feature requirements but breaks an affected trust boundary → **Spec pass, Security fail.**

Reporting them separately stops one axis from masking the other.
