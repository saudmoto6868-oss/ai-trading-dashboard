---
name: context-hygiene
description: Minimize repeated repository reading and oversized context while preserving the evidence needed for correct work.
---

# Context hygiene

- Start from the project map, task index, relevant commit, and existing handoff.
- Verify the source revision before reusing an earlier summary or test result.
- Search exact symbols/paths and inspect only the necessary line ranges.
- Do not reread unchanged files or recursively dump the repository without a concrete reason.
- For large files, use targeted search and bounded excerpts; do not paste full generated files, logs, or datasets into context.
- Reuse prior tool output within the same task when it remains valid.
- Load specialist documentation only when the task touches that subsystem.
- Before creating a new index, log, cache, hook, dashboard, or Skill, check whether the repository already has one.
- Record the reason whenever a broad rescan or repeated read is necessary.

Do not skip a read that is required to verify a safety-critical assumption.
