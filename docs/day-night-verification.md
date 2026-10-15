# Day/night availability verification

## Requested behavior

`/swarm day` and `/swarm night` change user availability while preserving work priorities, model budgets, permissions and pause state. They bypass the five-hour direction cooldown without resetting it. `/loose-ends good morning` remains a read-only brief, with no mode switch or dispatch. Night prepares a bounded handoff and checks already-authorised auto-resume arrangements, without adding monitoring or spending.

## Local checks

The 80-test suite passes on macOS with Python 3.14. The local documentation checker passes. Eight added tests cover process-persistent request/delivery/application, late receipts, repeat/uncertain/failed delivery, unchanged direction/cooldown/pause, pending direction preservation, cache invalidation, corrupt-state refusal and execution of the installed helper in a temporary project. The existing 72 tests remain in the suite. An additional run with the system Python 3.9 also passed, but the supported minimum remains Python 3.10.

Two isolated fault controls failed as intended: the old helper lacks day/night support; removing the latest-availability guard lets a late night receipt overwrite day. The delivered implementation passes both corresponding regression tests. Fault variants were confined to temporary fixtures.

## Limits

No live agent, goal, provider, account, timer or auto-resume setting was changed during these checks. Native Windows/Linux execution and host slash-command discovery were not tested. SQLite persistence is not evidence of host delivery or application. Root must check the latest intent before applying it and record actual receipts. Host continuation and native auto-resume require supported host controls and existing project authority.

Projects pinned to an earlier toolkit revision need a reviewed `/swarmstack update`; publishing the toolkit does not silently replace their installed files or activate a mode.

## Independent review

The initial Standards and Spec reviews passed with no findings. Security identified one Important instruction mismatch: the night handoff could enable an auto-resume setting while checking it. The correction makes day/night inspection-only for those settings; any toggle requires a separate explicitly authorised setup action. The original finding remains retained in the [review record](reviews/day-night-reviews.json).

The corrected candidate `e723f1c` passed independent Security review with C0/I0/M0; the original Important finding is closed. The final helper also passed all 33 command-gate tests on Python 3.14. Standards and Spec each remain C0/I0/M0 on the initial implementation; the correction changes only the auto-resume wording and review records.
