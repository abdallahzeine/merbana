# Task 4 - Migrate Frontend Data Layer

## Objective
Replace the current in-memory singleton and full-blob persistence model with explicit API-driven server state and predictable cache invalidation.

## Prerequisite
- [ ] Task 3 route contract, error response schema, and service boundaries are finalized.

## Codebase Anchors
- `src/services/database.ts`
- `src/hooks/useDatabase.ts`
- `src/main.tsx`
- `src/App.tsx`
- `src/pages/*.tsx`
- `src/utils/reportUtils.ts`

## Frontend Migration Rules
- [ ] Backend is the single source of truth; no shadow `db` object may remain in the client.
- [ ] Replace feature-by-feature, not by partially wrapping the old singleton in async calls.
- [ ] Query keys and invalidation rules must be defined centrally before page refactors begin.
- [ ] Avoid optimistic updates unless a page explicitly needs them and rollback behavior is defined.
- [ ] Do not preserve legacy import/export UI, `sendBeacon` persistence, or global injection bridges.

## Checklist
- [ ] Split `src/services/database.ts` into entity-based API client modules matching backend routers: `usersApi`, `categoriesApi`, `productsApi`, `ordersApi`, `registerApi`, `debtorsApi`, `settingsApi`, `activityApi`.
- [ ] Add a shared HTTP client utility for base request handling, error decoding, and typed responses.
- [ ] Remove the `db` singleton, `listeners`, `subscribe()`, `notify()`, `persistToDisk()`, and `/api/save-db` calls.
- [ ] Remove `loadDatabase()` full-blob `/data/db.json` hydration logic.
- [ ] Add TanStack Query dependency to `package.json` and initialize query client/provider in app bootstrap.
- [ ] Replace `useDatabase` in `src/hooks/useDatabase.ts` with focused TanStack Query hooks per entity and per workflow.
- [ ] Define canonical query keys and invalidation map for at least: products, categories, orders, register, debtors, settings, users, activity log, dashboard/report summaries.
- [ ] Refactor mutation call sites in `ProductsPage.tsx`, `OrdersPage.tsx`, `NewOrderPage.tsx`, `RegisterPage.tsx`, `AdminPage.tsx`, `DebtorsPage.tsx`, and `SettingsPage.tsx` to async mutations.
- [ ] Convert report pages and helpers to consume queried server state without direct singleton reads.
- [ ] Remove download/upload database UI actions from `SettingsPage.tsx`.
- [ ] Remove `window.injectDatabase` global bridge and related import flow.
- [ ] Define UI error-handling rules for failed mutations, failed queries, and unavailable backend state, including whether retries are automatic, manual, or disabled per action.
- [ ] Ensure loading, empty, and stale states are intentionally handled rather than accidentally inherited from synchronous singleton reads.

## Acceptance Criteria
- [ ] No production page reads from or mutates a local in-memory database singleton.
- [ ] All writes travel through API mutations and refresh the minimum necessary query state.
- [ ] Import/export and JSON hydration code paths are fully removed from the UI.
- [ ] UI state transitions for loading, mutation pending, and server error are defined and testable.

## Deliverable
- [ ] Frontend uses API clients + TanStack Query as the only data layer, with explicit cache rules and no legacy singleton persistence behavior.

## Library Choices with Justification
- `@tanstack/react-query` for server-state management because cache invalidation, loading states, and mutation tracking are the core need and fit this app better than `Redux Toolkit Query`.
- `ky` for the shared HTTP client because it keeps a small `fetch`-based footprint and simpler error hooks than `axios` for a same-origin desktop API.
- `zod` for client-side API boundary parsing where needed because it catches response-shape drift more explicitly than relying on TypeScript types alone.

## Concrete File/Folder Structure
- `Tasks/`
  - `Task_4.md` (modified)
- `src/`
  - `main.tsx` (modified)
  - `App.tsx` (modified)
  - `api/`
    - `client.ts` (new)
    - `usersApi.ts` (new)
    - `categoriesApi.ts` (new)
    - `productsApi.ts` (new)
    - `ordersApi.ts` (new)
    - `registerApi.ts` (new)
    - `debtorsApi.ts` (new)
    - `settingsApi.ts` (new)
    - `activityApi.ts` (new)
  - `queries/`
    - `queryClient.ts` (new)
    - `queryKeys.ts` (new)
    - `users.ts` (new)
    - `categories.ts` (new)
    - `products.ts` (new)
    - `orders.ts` (new)
    - `register.ts` (new)
    - `debtors.ts` (new)
    - `settings.ts` (new)
    - `activity.ts` (new)
  - `hooks/`
    - `useDatabase.ts` (modified or removed after replacement)
  - `pages/`
    - `AdminPage.tsx` (modified)
    - `DebtorsPage.tsx` (modified)
    - `NewOrderPage.tsx` (modified)
    - `OrdersPage.tsx` (modified)
    - `ProductsPage.tsx` (modified)
    - `RegisterPage.tsx` (modified)
    - `ReportsPage.tsx` (modified)
    - `SettingsPage.tsx` (modified)
  - `services/`
    - `database.ts` (removed or reduced to compatibility shims during migration only)
- `package.json` (modified)

## Architecture Decisions
- Chosen: TanStack Query as the only server-state layer. Rejected: keeping the custom singleton and wrapping it with async calls. Why: the singleton model bakes in stale state, full-blob assumptions, and manual re-render wiring.
- Chosen: thin API clients plus query modules. Rejected: calling `fetch` directly from every page. Why: route contracts, errors, and invalidation rules need a central boundary.
- Chosen: explicit query keys for entity and summary views. Rejected: broad “refresh everything” behavior after each mutation. Why: the new architecture should minimize unnecessary refetches while keeping state coherent.
