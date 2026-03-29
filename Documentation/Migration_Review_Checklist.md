# Migration Review Checklist

Use this checklist before accepting any Alembic revision.

## 1. Schema Diff Review
- Confirm revision is generated from current SQLAlchemy metadata.
- Confirm table/column names match code intent.
- Confirm index and constraint names are explicit and stable.
- Confirm SQLite-compatible operations are used.
- Confirm no accidental drops/renames.

## 2. Data-Impact Assessment
- List affected tables.
- Classify operation risk:
  - additive (low)
  - backfill/update (medium)
  - destructive/drop/change type (high)
- Document expected impact on existing production rows.
- Verify nullability/default transitions are safe for existing data.

## 3. Downgrade Strategy
- Provide a downgrade path for reversible changes.
- For destructive migrations, document that restore may require backup recovery.
- Validate downgrade commands in non-production environment where feasible.

## 4. Backup Gate
- Verify a timestamped backup exists before upgrade.
- Verify backup includes `merbana.db` and sidecar files (`-wal`, `-shm`) when present.
- Record backup path in operator notes/change ticket.

## 5. Verification Steps
- Run `alembic upgrade head` on a clean DB.
- Run smoke API checks on upgraded DB.
- If Task 5 migrated DB is used, run `alembic stamp 0001_initial_schema` once, then verify `alembic current`.
- Check key row-count parity for critical tables.

## 6. Commands Audit
- Linux command syntax documented.
- Windows PowerShell syntax documented.
- `MERBANA_DB_URL` usage documented and consistent.

## 7. Approval Criteria
- Revision reviewed by at least one additional reviewer.
- Risks and rollback path documented.
- Deployment instructions include explicit operator migration step.
- No manual SQLite schema edits performed.
