

---

## Addendum — 2026-11-17 current-main refresh

This addendum supersedes the original baseline SHA for any new work. The original audit accurately described the repository as observed on 2026-11-10; current main has since advanced.

- Current main SHA rechecked on 2026-11-17: `da6ad692c011e12354a958063fed487aff095c27`.
- The old Academy branch remains at `3aa2f4271f5307d75a89f465391e871148cc4d68`.
- The original audit MR !55 is now merged (2026-11-15). The audit file is part of current main.
- A fresh validation branch `test/academy-intelligence-validation` was created from the current main SHA above.
- The original 30-image index and conversation archive are now present on current main; MR !52's content was incorporated after the original audit. This does not establish that video-derived setup tables were fully recovered.

### New adjacent platform knowledge contract

Current main now includes:
- `modules/tia_knowledge_router.py`
- `data/tia_platform_knowledge_registry.json`
- `tests/test_tia_knowledge_router.py`

This is a read-only cross-platform **research-guidance router** with a versioned registry of schools, route guidance, capability gates and limits. It is not a replacement for Academy's evidence/provenance record store. Any future integration must preserve the separation:
1. Academy Core owns durable source records, claims, review events and evidence governance.
2. TIA knowledge router provides read-only school/feature guidance and capability limitations.
3. Lab alone owns empirical strategy validation.
Do not create a second Academy database or duplicate the canonical school definitions in Workspace.

### Current Workspace build contract

The current owner instruction in `docs/MEETING_ROOM.md` confirms that `modules/workspace_app.html` is generated from the source parts under `modules/ws/` using `python3 scripts/build_workspace.py`. Never edit/copy the generated HTML directly; port only source-part changes, then regenerate the bundle and run `tests/test_workspace_parts_sync.py`.

### CI execution blocker — 2026-11-17

A real MR pipeline was requested for MR !55:
- Pipeline: `3078145427`
- Jobs: `mr_tests` and `risk_policy_tests`
- Both jobs failed before runner start with failure reason `ci_quota_exceeded`.
- Runner and job start timestamps are null; no test command executed.
- Therefore this is an infrastructure/quota blocker, not an application test failure and not a passing test.

No workaround, external runner, paid service, workflow change, or secret was used. Resolve the project's CI quota/runner entitlement through the owner/admin route before claiming CI validation.

### Issue tracking

Evidence-based recovery notes were added to Issues #3, #4, #5, #7 and #8 on 2026-11-17. All remain open.

### Current execution checkpoint

- Branch: `test/academy-intelligence-validation`
- Branch base: `da6ad692c011e12354a958063fed487aff095c27`
- No application files have been changed on this branch yet.
- No Academy or Meeting Room tests have been executed in this environment.
- Next safe step: finish a bounded source-level review of current Academy Core and the old Workspace widget diff, then port the widget only on a separate feature branch from the latest main. Keep CI blocked status explicit until quota/runner execution is restored.
