# Project command split

The accepted split assigns team controls to /swarm, project setup/help to /swarmstack and independent workflows such as /grill-with-docs to standalone skills. The project router loads only the selected reference. This delivery completes setup consolidation against base67cfd2472d218f10bc8153a79f1bc0f9348c7a90.

The installer normalises legacy setup-project and swarmstack-help selections to one swarmstack selection. It preserves input configuration, rejects raw duplicates and installs no duplicate command directory. Existing installations remain untouched and require a reviewed migration.

Verification: scripts/check.py and46unittest cases PASS. Temporary projects exercise legacy six/seven-skill configurations, combined aliases, canonical installed configuration, local links, notice distribution, output hashes, invalid selections and caller-input preservation. Two initial legacy-fixture failures were corrected by supplying the actual former setup-project selection; explicit alias-output checks now verify its replacement.

Independent read-only Standards and Spec reviews both PASS, zero Critical/Important/Minor findings. Reviewers inspected the source; they did not rerun installer tests. No separate Security axis was triggered because execution grants and filesystem-write boundaries are unchanged.

Actual host slash discovery and model routing behavior remain unverified. No global skill installation, live swarm control, other-project adoption or broader guide sync was performed. Public attribution remains in central credit/licence records.
