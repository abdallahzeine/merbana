# Task 3 - Build FastAPI + SQLAlchemy API Layer

## Objective
Replace the current single-endpoint JSON persistence launcher with a structured FastAPI backend that becomes the only write path for application data.

## Prerequisite
- [ ] Task 2 Decision Locks are completed and approved.
- [ ] Route and service design must not re-open unresolved schema questions.

## Codebase Anchors
- `Deployment/merbana_launcher.py`
- `requirements.txt`
- `build_windows.py`
- `Deployment/build_linux.py`

## API Layer Rules
- [ ] Use a synchronous SQLAlchemy engine/session model; do not introduce async database plumbing for this desktop app.
- [ ] Keep backend as the source of truth. Frontend must never write the SQLite file directly.
- [ ] Put business rules that mutate multiple entities behind backend services, not ad-hoc inside route handlers.
- [ ] All write routes must have explicit transaction boundaries and rollback behavior.
- [ ] Do not expose user-facing `/api/db/export` or `/api/db/import` endpoints even though the original transformation plan mentioned them; migration and parity tooling stay internal only.
- [ ] Do not introduce `window.__API_URL__` unless same-origin routing proves impossible. Preferred design is SPA and API served from the same localhost origin and port.

## Checklist
- [ ] Add backend dependencies to `requirements.txt`: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic`.
- [ ] Create backend package (for example `Deployment/backend/`) with app, models, schemas, session, services, routers.
- [ ] Move launcher path resolution into a reusable SQLite path helper beside the launcher data folder, preserving packaged-vs-script behavior currently provided by `get_data_path()`.
- [ ] Replace `/api/save-db` behavior in `Deployment/merbana_launcher.py` with FastAPI app startup and mounted SPA serving.
- [ ] Define API routing boundary: all backend routes under `/api/*`, static SPA mounted at `/` after routers.
- [ ] Keep SPA static serving behavior for `dist/` with catch-all fallback to `index.html`.
- [ ] Implement entity routers for users, categories, products, orders, register transactions, debtors, settings, and activity log.
- [ ] Create a service layer for multi-entity workflows, at minimum: create order, delete order, deposit/withdraw cash, close shift, daily stock reset.
- [ ] Create route contract documentation with fixed columns: `entity`, `method`, `path`, `request_schema`, `response_schema`, `error_codes`, `side_effects`.
- [ ] Define a standard error response shape and apply it consistently across routers (for example: `{"error":"...","code":"...","details":...}`).
- [ ] Define stable error codes for at least: validation failure, missing entity, relation conflict, duplicate ID, migration-only route rejection, and internal error.
- [ ] Enable SQLite connect-event pragmas: `foreign_keys=ON`, `journal_mode=WAL`.
- [ ] Move daily stock reset behavior from frontend `checkDailyReset()` into backend startup or first-request guard and document its exact once-per-day semantics.
- [ ] Add CORS origins for both `http://127.0.0.1:{port}` and `http://localhost:{port}`.
- [ ] Ensure pywebview mode and browser fallback still work with dynamic free-port behavior.
- [ ] Update packaging assumptions in `build_windows.py` and `Deployment/build_linux.py` so backend files and migration assets are bundled correctly.

## Acceptance Criteria
- [ ] `/api/save-db` no longer exists as an active persistence path.
- [ ] Every frontend-required mutation has a documented backend route or service contract.
- [ ] Route handlers are thin enough that business invariants remain enforceable and testable outside HTTP.
- [ ] Launcher still serves the SPA locally in packaged and non-packaged modes.

## Deliverable
- [ ] Launcher serves SPA + FastAPI on localhost with SQL persistence, documented route contract, standardized error responses, and backend-owned business workflows.

## Library Choices with Justification
- `FastAPI` for the HTTP layer because typed route contracts and dependency injection fit the API-first migration better than `Flask`.
- `SQLAlchemy 2.x` for synchronous ORM and transaction management because it works cleanly with SQLite pragmas and the later Alembic workflow unlike lighter ORMs such as Peewee.
- `Pydantic v2` for request and response schemas because it integrates directly with FastAPI and provides stronger typed validation than hand-written serializer logic.
- `Uvicorn` for ASGI serving because this is a local desktop-hosted app and `Uvicorn` keeps the serving stack simpler than `Hypercorn`.
- `Starlette` static-file mounting via FastAPI for SPA hosting because serving API and frontend from the same ASGI app avoids a split between backend routes and a custom `http.server` implementation.

## Concrete File/Folder Structure
- `Tasks/`
  - `Task_3.md` (modified)
- `Deployment/`
  - `merbana_launcher.py` (modified)
  - `build_linux.py` (modified)
  - `backend/`
    - `__init__.py` (new)
    - `app.py` (new)
    - `config.py` (new)
    - `database.py` (new)
    - `paths.py` (new)
    - `errors.py` (new)
    - `dependencies.py` (new)
    - `models.py` (modified or reused from Task 2)
    - `schemas/`
      - `__init__.py` (new)
      - `users.py` (new)
      - `categories.py` (new)
      - `products.py` (new)
      - `orders.py` (new)
      - `register.py` (new)
      - `debtors.py` (new)
      - `settings.py` (new)
      - `activity.py` (new)
      - `errors.py` (new)
    - `routers/`
      - `__init__.py` (new)
      - `users.py` (new)
      - `categories.py` (new)
      - `products.py` (new)
      - `orders.py` (new)
      - `register.py` (new)
      - `debtors.py` (new)
      - `settings.py` (new)
      - `activity.py` (new)
    - `services/`
      - `__init__.py` (new)
      - `orders.py` (new)
      - `register.py` (new)
      - `inventory.py` (new)
      - `settings.py` (new)
      - `activity.py` (new)
- `Documentation/`
  - `API_Route_Contract.md` (new)
- `requirements.txt` (modified)
- `build_windows.py` (modified)

## Architecture Decisions
- Chosen: one same-origin FastAPI application serving both `/api/*` routes and the SPA. Rejected: a split backend service plus separate static server. Why: same-origin serving removes avoidable configuration complexity for a desktop-local app.
- Chosen: a service layer for multi-entity workflows such as order creation and daily reset. Rejected: embedding business rules directly inside route handlers. Why: those workflows need transactionally testable behavior outside the HTTP boundary.
- Chosen: internal-only migration and parity tooling. Rejected: public `/api/db/export` and `/api/db/import` endpoints. Why: operational tooling should not become a user-facing data-exfiltration surface.
