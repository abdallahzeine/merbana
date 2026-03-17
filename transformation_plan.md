# JSON → SQLite Migration Plan (Option A)

---

## Phase 1 — Audit Current Data Structure

1. List every top-level key in the JSON document
2. For each key, determine its type: scalar, object, or array
3. For arrays, identify:
   - What fields each item contains
   - Which fields are always present vs optional
   - What data types each field holds (string, number, boolean, nested object, nested array)
4. For nested objects within arrays, flag them separately — they will need their own tables
5. Identify all relationships: does any item reference another item by an ID field?
6. Identify all fields that are queried, filtered, or sorted on in the frontend
7. Document every mutation function and what fields it reads or writes

**Output:** A complete field inventory with types, optionality, and relationships — no schema yet, just facts.

---

## Phase 2 — Design the SQLite Schema

Only after Phase 1 is complete:

1. Map each array to a table
2. Map each scalar/object at the root level to either a single-row config table or columns in an existing table
3. For nested arrays within items, create a child table with a foreign key back to the parent
4. For nested objects within items (not arrays), decide: flatten into parent table columns, or separate table with a one-to-one foreign key
5. Define primary keys for every table
6. Define foreign key constraints for every relationship identified in Phase 1
7. Map each field's data type to an appropriate SQLite type (`TEXT`, `INTEGER`, `REAL`, `BLOB`, `NUMERIC`)
8. Mark optional fields as `NULL`-able, required fields as `NOT NULL`
9. Add indexes on every field identified in step 6 of Phase 1 as queried/filtered/sorted
10. For boolean fields, decide on convention (`0`/`1` integers) and apply consistently
11. Review the schema against every mutation function from step 7 of Phase 1 — ensure every write operation maps cleanly to an `INSERT`, `UPDATE`, or `DELETE`

**Output:** Finalized `CREATE TABLE` statements, not yet executed.

---



## Phase 3 — Build the Python API Layer (FastAPI)

1. Replace `http.server` with FastAPI. Add dependencies:
   ```
   fastapi
   uvicorn
   ```

2. Initialize the SQLite connection on startup using Python's stdlib `sqlite3` inside a FastAPI `lifespan` context manager — create all tables if they don't exist, and set `PRAGMA foreign_keys=ON` and `PRAGMA journal_mode=WAL` on every connection

3. Define a router per entity (e.g. `routers/orders.py`, `routers/products.py`) keeping the codebase organized and mirroring the table structure from Phase 2

4. For each entity, implement the standard endpoints using FastAPI route decorators:
   - `GET /api/{entity}` — list all
   - `GET /api/{entity}/{id}` — get by ID
   - `POST /api/{entity}` — create
   - `PUT /api/{entity}/{id}` — update
   - `DELETE /api/{entity}/{id}` — delete

5. Define Pydantic models for every entity's request and response — these replace the TypeScript interfaces as the source of truth for data validation on the backend side

6. Wrap every write route in an explicit SQLite transaction using a context manager — this replaces the atomic rename mechanic

7. Implement `GET /api/db/export` — queries all tables and returns a JSON structure matching the original `db.json` shape

8. Implement `POST /api/db/import` — accepts the JSON payload, validates via Pydantic, and bulk-inserts in dependency order inside a single transaction

9. Replace the `pywebview` / `http.server` startup in `merbana_launcher.py` with:
   ```python
   import uvicorn
   uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")
   ```
   Keep the `pywebview` window spawn logic unchanged — it still just points to `http://127.0.0.1:{port}`

10. Keep static file serving for the React `dist/` folder using FastAPI's `StaticFiles` mount:
    ```python
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
    ```
    Mount this **after** all API routers to avoid the catch-all overriding API routes

11. Add FastAPI's built-in CORS middleware scoped to `127.0.0.1` only — no external origin should ever be whitelisted given the local-only deployment model


---

## Phase 4 — Migrate the Frontend

1. Remove the `loadDatabase()` boot call that fetches and hydrates the full JSON blob
2. Remove the `persistToDisk()` / `sendBeacon` / full-db POST mechanism entirely
3. For each mutation function in `services/database.ts`, replace the direct object mutation + `notify()` pattern with an `async` API call to the corresponding new endpoint
4. Re-evaluate the pub-sub singleton: decide whether to keep it as a local cache synced by API responses, or remove it entirely and let React Query / SWR / manual `useState` handle server state
5. Update every component that reads from the in-memory `db` singleton to either:
   - Fetch data on mount from the API, or
   - Read from a local cache that is invalidated after each mutation
6. Update `checkDailyReset()` — move this logic to the Python layer, triggered on server startup or first request of the day
7. Remove the `window.injectDatabase` hook if the full-blob injection model is no longer applicable

---

## Phase 5 — Data Migration (One-Time)

1. Write a migration script (Python) that:
   - Reads the existing `db.json`
   - Validates every field against the schema from Phase 2
   - Inserts each entity into the correct SQLite table in dependency order (parent tables before child tables)
   - Logs any field that fails validation or cannot be mapped
2. Run the script against a **copy** of `db.json`, never the original
3. After insertion, run row counts per table and compare against array lengths in the original JSON
4. Spot-check a sample of records from each table against the source JSON manually

---

## Phase 6 — Edge Case Handling

Address these before going live:

1. **Null / missing fields:** Decide per field — default value, `NULL`, or reject and log
2. **Empty arrays:** Tables should simply have zero rows, not cause errors
3. **Orphaned references:** Any item referencing a foreign key ID that doesn't exist in the parent table — log and quarantine, do not silently drop
4. **Duplicate IDs:** If any array in the JSON has duplicate ID values, resolve before inserting
5. **Boolean representation:** Normalize all booleans to `0`/`1` consistently during migration
6. **Date/time fields:** Standardize all date strings to ISO 8601 format before storing as `TEXT`
7. **Nested objects stored as blobs:** If any field is a JSON sub-object with no clear relational mapping, store as `TEXT` (serialized JSON) with a documented plan to normalize later

---

## Phase 7 — Integrity Validation

After migration and after going live:

1. Run `PRAGMA foreign_key_check;` — must return zero violations
2. Run `PRAGMA integrity_check;` — must return `ok`
3. For every table, verify row count matches source data
4. Re-run every existing unit test in `database.test.ts` and `database.persistence.test.ts` against the new API layer
5. Write new integration tests: for each endpoint, test create → read → update → delete cycle
6. Test the daily reset logic end-to-end
7. Test the export endpoint output against the original `db.json` structure to confirm no data loss

---

## Phase 8 — Performance Baseline

1. Measure response time for the most frequently called endpoints under realistic data volumes
2. Confirm indexes from Phase 2 step 9 are being used via `EXPLAIN QUERY PLAN`
3. For report-style queries that aggregate large tables, test with a realistic historical data size
4. Enable `PRAGMA journal_mode=WAL;` on the SQLite connection for better read/write concurrency and crash resilience
5. Enable `PRAGMA foreign_keys=ON;` on every connection — SQLite disables this by default

---

## Phase 9 — Rollback Plan

1. Keep `db.json` untouched until the system is fully validated in production
2. The `/api/db/export` endpoint from Phase 3 step 6 is your rollback mechanism — it regenerates a valid `db.json` from SQLite at any time
3. If a rollback is needed: run export, revert Python launcher to the original single-endpoint version, point it back at the exported `db.json`
4. Before any future schema change, always export a JSON snapshot first
5. Document the SQLite file location in the deployment directory alongside where `db.json` previously lived