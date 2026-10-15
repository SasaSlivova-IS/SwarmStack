---
name: grill-with-docs
description: Interview the user about unresolved plan or design decisions after checking documentation and code; explain the context, offer lettered choices, and record accepted answers.
disable-model-invocation: true
---

# Grill with docs

Use the project's records and source to identify decisions that still need the user. Keep the interview grounded in concrete workflows. Use `domain-modeling` when an answer changes terminology or a durable architectural decision; update the existing owning records rather than creating a document for every answer.

## Before asking

- Check previous answers, accepted decisions, requirements, glossary, relevant issue/design records and current source. An old open-question label is not proof that a question remains unanswered.
- Apply accepted rules and make reversible technical choices yourself. Ask about unresolved product behavior, authority, money or an explicit conflict between accepted records.
- Separate accepted requirements, proposals, implementation and verified behavior. A screenshot or authored test does not prove the workflow works.
- Consolidate questions from collaborating agents. Remove duplicates and answered questions; preserve existing numbers or chat-specific identifiers. Do not restart numbering at 1 or silently renumber pending questions.

## Question format

Use these four parts, in this order, for every question:

### <existing number or identifier>. <short topic>

**Explanation:** Explain the workflow and why the decision matters. Define unfamiliar terms and use a short example when it helps.

**Current state:** State what is already decided, what is implemented or verified, and the exact remaining gap. Name or link the specific records/code checked in one short sentence. Do not bury this in an audit narrative.

**Question:** Ask for one independent decision in a direct sentence.

- **A — Recommended:** A concrete choice and its practical consequence.
- **B:** A distinct alternative and its practical consequence.
- **C:** A distinct alternative and its practical consequence.
- **D:** A distinct alternative, or a demonstration/defer option when that is useful.

Keep the recommendation first when one is justified. Preserve original letters when restating an existing question; mark the recommended existing choice instead of changing its letter. Do not invent incompatible or meaningless choices just to fill four slots. The user may answer in free text. Avoid unexplained implementation jargon and rhetorical questions.

Default to 3–5 independent questions per batch unless the user requests another amount or all remaining questions. End with a compact answer example using the actual identifiers. Continue work that does not depend on the answers.

## After answers

Record the user's actual choice and corrections in the owning decision/issue record, respecting its writer ownership. Keep deferred decisions pending. Do not describe an answer as implemented or verified. Recheck remaining questions before the next batch, and create ADRs only for durable tradeoffs that need their reasoning preserved.
