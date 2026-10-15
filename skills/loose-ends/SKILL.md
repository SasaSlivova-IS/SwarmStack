---
name: loose-ends
description: Find what the user missed and what is still open. "/loose-ends cover" reviews this conversation for unanswered questions, unconfirmed offers, contradictions and missing pieces; "/loose-ends catchup" catches the user up on the project after time away; "/loose-ends good morning" covers the night since the user's last message.
disable-model-invocation: true
---

# Loose ends

Load [the procedure](references/procedure.md) on invocation.

Modes:

- **cover:** go back through this conversation and find what the user may have missed while moving between ideas.
- **catchup:** catch the user up on the whole project after they have been away, then find what is still open.
- **good morning:** a catchup that starts at the user's last message of the previous day and ends now, followed by every decision or question still waiting on them, however old.

Either mode accepts a starting point, such as `/loose-ends cover since the pricing discussion` or `/loose-ends catchup since 1 March`. With no mode given, ask which one in a single short question.

The report is read-only: do not dispatch agents, message other threads, run builds or tests, or change records. Load [grill-with-docs](../grill-with-docs/SKILL.md) and its procedure before asking open decisions. Keep existing question identifiers and always add the topic.
