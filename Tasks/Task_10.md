# Task 10 - Rollback Plan

## Objective
Provide a tested, low-risk path back to the legacy JSON launcher behavior if the SQL migration fails in development or deployment.

## Prerequisite
- [ ] Tasks 3 through 9 are complete enough to perform a real rollback dry run.

## Codebase Anchors
- `Deployment/merbana_launcher.py`
- `public/data/db.json`
- `build_windows.py`
- `Deployment/build_linux.py`

## Rollback Rules
- [ ] Rollback must rely on stored snapshots and packaged artifacts, not on a live API export endpoint.
- [ ] Rollback plan must define both technical restore steps and the decision criteria for when rollback is mandatory.
- [ ] Rollback verification must include business smoke tests, not only process startup.

## Checklist
- [ ] Keep pre-migration `db.json` snapshots for each deployment environment.
- [ ] Keep the last-known-good legacy launcher/package artifact alongside the SQL-based build artifact.
- [ ] Keep timestamped SQLite DB backups for every migration/upgrade event.
- [ ] Define rollback triggers explicitly: startup crash, migration failure, row-count mismatch, broken auth flow, failed critical checkout/order flow, or unrecoverable data integrity error.
- [ ] Document rollback switch steps:
  1. Stop the FastAPI-based launcher.
  2. Archive the current SQLite DB and logs for forensic analysis.
  3. Restore the previous launcher version that still supports `/api/save-db`.
  4. Restore the correct `db.json` snapshot to the exact path resolved by the legacy `get_data_path()` behavior.
  5. Relaunch the app.
  6. Run smoke-test flows: create an order, complete payment/register flow, view reports, confirm login/settings behavior.
- [ ] Define forensic diff tooling for rollback analysis: `sqldiff`, schema dumps, data dumps, row-count comparison, and log capture.
- [ ] Define version-pairing record for each release: app build version, Alembic head revision, SQLite backup name, and matching JSON snapshot.
- [ ] Test rollback in development, packaged Windows build output, and Linux deployment build output.

## Acceptance Criteria
- [ ] Rollback can be executed without relying on undocumented tribal knowledge.
- [ ] Dry-run rollback is verified in every supported deployment path.
- [ ] Forensic artifacts are sufficient to explain why rollback was required.

## Deliverable
- [ ] Executable rollback runbook with verified dry-run results, trigger matrix, artifact locations, and forensic checklist.

## Library Choices with Justification
- `shutil` from Python standard library for snapshot and artifact restore operations because file-copy and archive tasks do not justify a third-party filesystem dependency.
- `sqlite3` from Python standard library for offline validation queries against rollback candidates because rollback must remain possible even when the live backend is unavailable.
- `DeepDiff` for comparing forensic JSON and structured rollback artifacts because nested change reporting is clearer and less error-prone than manual comparison.

## Concrete File/Folder Structure
- `Tasks/`
  - `Task_10.md` (modified)
- `Documentation/`
  - `Rollback_Runbook.md` (new)
  - `Rollback_Dry_Run_Report.md` (new)
  - `Rollback_Artifact_Matrix.md` (new)
- `artifacts/`
  - `rollback/`
    - `json_snapshots/` (stored snapshots)
    - `sqlite_backups/` (stored backups)
    - `logs/` (captured forensic logs)

## Architecture Decisions
- Chosen: rollback from stored artifacts and known-good packages. Rejected: regenerating rollback inputs from a live API endpoint during an incident. Why: the system being rolled back may be the very thing that is failing.
- Chosen: trigger-based rollback with mandatory smoke tests after restore. Rejected: operator discretion without defined failure thresholds. Why: rollback needs objective criteria and verification steps to avoid partial recovery.
- Chosen: preserving both JSON snapshots and SQLite forensic evidence. Rejected: deleting failed-state artifacts once service is restored. Why: understanding why rollback happened is part of making future migrations safe.
