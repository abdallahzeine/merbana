# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Merbana** is an offline-first desktop Point of Sale (POS) and Order Management System. It runs entirely on a single machine: a Python/FastAPI backend serves a React SPA, all wrapped in a native OS window via pywebview. There is no cloud backend.

## Commands

### Frontend (React + TypeScript)

```bash
npm install              # Install dependencies
npm run dev              # Dev server at http://localhost:5173 (proxies /api/* to port 8741)
npm run build            # Production build → dist/
npm run lint             # ESLint
npm run test             # Vitest (single run)
npm run test:watch       # Vitest watch mode
npm run test:coverage    # Coverage report
npx vitest run src/path/to/test.ts   # Run a single test file
npm run test:e2e         # Playwright E2E
```

### Backend (Python + FastAPI)

```bash
pip install -r requirements.txt

# Run the backend dev server
uvicorn backend.app:app --host 127.0.0.1 --port 8741

# Run all tests
pytest backend/tests -v

# Run a single test
pytest backend/tests/test_orders.py::test_create_order -v

# Database migrations
python -m alembic -c Deployment/backend/alembic.ini upgrade head
python -m alembic -c Deployment/backend/alembic.ini current
python -m alembic -c Deployment/backend/alembic.ini revision --autogenerate -m "description"

# Migrate legacy JSON data to SQLite
python Deployment/migrate_json_to_sqlite.py --source data/db.json --overwrite
```

### Building Desktop Executables

```bash
python build_windows.py                  # Windows: produces Merbana.exe via PyInstaller
python build_windows.py --skip-frontend  # Reuse existing dist/
python Deployment/build_linux.py         # Linux: produces AppImage
```

## Architecture

### Runtime Flow

```
Deployment/merbana_launcher.py
  ├─ Starts FastAPI on http://127.0.0.1:8741
  ├─ Serves React SPA from dist/
  └─ Opens native window via pywebview
```

The React app communicates with the FastAPI backend over localhost. In development, Vite's proxy handles `/api/*` → `http://127.0.0.1:8741`.

### Backend (`backend/`)

- **`app.py`** — FastAPI application factory: mounts routers, CORS, lifespan (DB init), exception handlers
- **`models.py`** — 11 SQLAlchemy models: `User`, `Product`, `Category`, `ProductSize`, `Order`, `OrderItem`, `CashTransaction`, `Debtor`, `ActivityLog`, `StoreSettings`, `PasswordRequirements`
- **`database.py`** — SQLite engine with WAL mode and foreign key enforcement; `SessionLocal` factory
- **`routers/`** — 8 FastAPI routers under `/api/*`: users, products, categories, orders, register, debtors, settings, activity
- **`services/`** — Business logic (order creation, cash transactions, activity logging) kept separate from routers
- **`schemas/`** — Pydantic request/response models
- **`errors.py`** — `AppError` base class with structured error responses

### Frontend (`src/`)

- **`main.tsx`** — React root: wraps app in `QueryClientProvider`, `AuthProvider`, and `BrowserRouter`
- **`App.tsx`** — Route definitions: login, 9 protected POS pages, admin, receipt
- **`api/client.ts`** — Ky-based HTTP client singleton with shared error handling
- **`api/schema.ts`** — Zod schemas for all API response types
- **`api/*Api.ts`** — Endpoint-specific API functions (one file per resource)
- **`contexts/AuthContext`** — Active user state and login/logout logic
- **`queries/queryClient`** — React Query client for server-state caching

### Database

SQLite at `data/merbana.db`. Schema is managed by **Alembic** (`Deployment/backend/alembic/`). Migration files live in `Deployment/backend/alembic/versions/`. The legacy data format was JSON (`data/db.json`); `migrate_json_to_sqlite.py` handles conversion.

### Testing

- **Frontend:** Vitest + React Testing Library; MSW for API mocking (`src/test/`)
- **Backend:** pytest with an in-memory SQLite test database configured in `backend/tests/conftest.py`
- **E2E:** Playwright (`src/integration/`)

## Key Configuration

- Backend port: `8741` (override with `MERBANA_PORT` env var)
- Alembic config: `Deployment/backend/alembic.ini`
- Vite dev proxy and test config: `vite.config.ts`
- TypeScript: `tsconfig.json` (strict mode)
