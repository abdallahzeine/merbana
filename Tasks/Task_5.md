# Task 5 - Execute One-Time Data Migration

## Objective
Import legacy JSON data into SQLite in a reproducible, auditable, and failure-safe way.

## Prerequisite
- [ ] Tasks 2 and 3 are complete.
- [ ] All schema Decision Locks that affect relation handling during import are closed.

## Codebase Anchors
- `public/data/db.json`
- `Deployment/merbana_launcher.py`
- `src/types/types.ts`
- backend schemas/models from Tasks 2 and 3

## Migration Rules
- [ ] Migration must operate on a copied source file, never on the original live JSON in place.
- [ ] Migration must be reproducible: same input copy and same code should produce the same row counts and same parity dump.
- [ ] Migration must be atomic: no partial database should survive a failed run.
- [ ] Migration policy for bad data must be explicit per failure class: reject, quarantine, or normalize.
- [ ] Script must not silently coerce relation errors or duplicate IDs.

## Checklist
- [ ] Implement migration script (for example `Deployment/migrate_json_to_sqlite.py`).
- [ ] Add a dry-run mode that validates and reports without writing to the SQLite database.
- [ ] Add a safety gate that refuses to run against a non-empty target DB unless an explicit reset/overwrite flag is provided.
- [ ] Validate payload against Pydantic schemas aligned with the Task 3 API/backend contracts, not only the loose JSON shape.
- [ ] Run pre-insert duplicate-ID checks per entity and fail fast on collisions.
- [ ] Resolve dependency order explicitly: categories/users/products/settings -> orders -> order items/register transactions/activity/debtors, unless finalized schema requires a different proven order.
- [ ] Run migration inside one DB transaction; on any error, rollback the full migration.
- [ ] Preserve existing IDs to avoid breaking references and receipt links.
- [ ] Preserve `orderNumber` and source date values exactly unless a documented normalization rule was approved earlier.
- [ ] Log validation failures with entity name, record ID (if present), and field path.
- [ ] Apply the Task 6 quarantine policy for broken references and emit `migration_quarantine.json` when required.
- [ ] Emit row-count report per table and compare against source array lengths, including explanation for any mismatch.
- [ ] Produce a script-only JSON parity dump from SQLite and diff it against the source structure; do not implement an API export endpoint for this.
- [ ] Record sample spot checks for at least one record per entity type and one full order workflow chain.

## Acceptance Criteria
- [ ] Failed runs leave no partially imported database state.
- [ ] Every source-to-target mismatch is classified and explained.
- [ ] Migration report is strong enough to support Task 7 parity validation and Task 10 rollback decisions.

## Deliverable
- [ ] Migration script, dry-run mode, parity dump tooling, and migration report containing counts, mismatches, errors, quarantined records, and sample checks.

## Library Choices with Justification
- `Pydantic v2` for input validation during import because it provides field-level error reporting that is more maintainable than custom dictionary checks.
- `SQLAlchemy 2.x` for transactional inserts because it uses the same model definitions as runtime persistence and avoids drift that raw `sqlite3` scripts would introduce.
- `DeepDiff` for parity-dump comparison because nested JSON structure mismatches are easier to audit than with handwritten recursive diff logic.

## Concrete File/Folder Structure
- `Tasks/`
  - `Task_5.md` (modified)
- `Deployment/`
  - `migrate_json_to_sqlite.py` (new)
  - `backend/`
    - `migration/`
      - `__init__.py` (new)
      - `loader.py` (new)
      - `validators.py` (new)
      - `importer.py` (new)
      - `parity_dump.py` (new)
      - `reporting.py` (new)
- `Documentation/`
  - `Migration_Report.md` (new)
  - `Migration_Parity_Diff.md` (new)
- `artifacts/`
  - `migration_quarantine.json` (generated when needed)
  - `migration_counts.json` (generated)
  - `migration_parity_dump.json` (generated)

## Architecture Decisions
- Chosen: a standalone migration script outside the public API surface. Rejected: importing legacy JSON through a user-facing backend endpoint. Why: one-time operational migration should not become a permanent application capability.
- Chosen: whole-run transactionality with dry-run support. Rejected: per-entity partial commits. Why: parity verification and rollback become unreliable if failed runs leave residue in the database.
- Chosen: explicit reject-or-quarantine handling for bad records. Rejected: silent coercion of duplicates or broken references. Why: migration must preserve trust in the imported dataset, not merely maximize import count.
