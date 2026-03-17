# State Management

Merbana intentionally avoids complex external React state management libraries (like Redux, Zustand, or Jotai). Instead, it establishes its own deeply integrated Pub-Sub system mapped inside `src/services/database.ts` and context providers.

## The Database Singleton (`services/database.ts`)

A global in-memory variable `let db: Database` exists outside the React rendering tree encompassing the POS system's current reality.

### Subscription System
React hooks tie into the external `db` state via classical subscriptions.
1. `subscribe(listener)` exposes a way to receive callbacks whenever changes happen.
2. Under the hood, the `useDatabase` hook registers itself, effectively converting this external store into native reactive state within functional React components.

### Reactive Mutations
Helper functions serve as action dispatchers directly modifying the `db` variable:
- `addProduct()`
- `updateSettings()`
- `addOrder()`

When these complete execution, they manually call `notify()`. 
`notify()` serves two critical functions concurrently:
1. **Network Sync:** Directly pushes `persistToDisk()`, triggering a POST request (either via `navigator.sendBeacon` or a `fetch` fallback) to the backend to atomically save the state.
2. **UI Updates:** Loops through the registered `listeners` causing React components to re-render in their fresh state.

### Handling Unloads (Beacon API vs Fetch)
Because data serialization acts as the primary datastore, guaranteeing data writes even if an employee shuts the window suddenly is critical. `persistToDisk()` conditionally chooses its transport method:
- It uses `navigator.sendBeacon` for payloads under ~63 KB (`BEACON_MAX_BYTES`). This ensures the browser completes the POST to `merbana_launcher.py` even as the React thread evaporates during unloads.
- For payloads that exceed this limit, it seamlessly falls back to using standard `fetch` with the `keepalive: true` flag set, which achieves a similar connection persistence guarantee during navigation.

## The Auth Context
`AuthContext.tsx` handles `StoreUser` identity. While "users" exist in the DB, "who is logged in right now" lives exclusively inside `sessionStorage`. If the user shuts down the window, the session clears, effectively logging them out.
- Implements basic login and logout functionality paired alongside generic activity logs pushing `logActivity()` mutations.
