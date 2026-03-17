# Advanced Mechanics & Linux Deployment

While the primary documentation focused heavily on the Windows architecture, Merbana includes customized behaviors for cross-platform support and internal logic workarounds.

## Custom React Hooks (`src/hooks/`)
The frontend contains several critical custom hooks bridging the gap between raw data and UI execution.
- `useDatabase.ts`: Ties React components to the external `db` state. It utilizes the `subscribe()` and `notify()` mechanic to trigger re-renders exactly when the global singleton changes.
- `useAuth.ts`: Wraps `sessionStorage` into a reactive context module handling active user sessions and activity logging directly.
- `usePasswordGate.ts`: A High-Order operational hook that takes an action wrapper and safely intercepts the call with a UI Modal if `StoreSettings` specify a password requirement for that exact action.

## Clever Logic: Cronless Daily Stock Reset
Traditional POS systems rely on server-side background "cron jobs" to wipe daily metrics at midnight. Because Merbana's backend is a passive file server, the UI triggers this manually.
The `checkDailyReset()` function compares the current `new Date().toDateString()` against `db.lastStockReset` every time the database initializes. If it is a new calendar day, the frontend instantly zeros out tracking stock and issues a save before the user even clicks anything.

## Desktop Container Integration (`window.injectDatabase`)
`pywebview` provides a way to pass data dynamically into the running web container.
Inside `src/services/database.ts`, the frontend exposes a global API hook:
```typescript
declare global {
  interface Window {
    injectDatabase: (jsonString: string) => Promise<{ success: boolean; error?: string }>;
  }
}
```
If future iterations of the Python wrapper need to manually inject or sync local state from the OS layer, this hook overwrites the entire in-memory `db` state dynamically without forcing a traditional REST GET.

## Linux Deployment Pipeline (`Deployment/build_linux.py`)
Merbana fully supports Debian/Ubuntu environments mimicking the Windows pywebview wrapper logic.
- Requires system packages: `python3-gi`, `gir1.2-webkit2-4.1` (or `webkitgtk-6.0`).
- The build script packages it similarly using `--onefile` PyInstaller logic, tying `merbana_launcher.py` along with GTK or PyQt5 bindings dynamically based on the argument `--backend gtk|qt`.
- Distributed as a shell-executed payload `update_merbana.sh` that pulls the latest `git` repository, runs `npm ci` and `npm run build`, and copies the `dist/` payload directly to an active `~/Desktop/POS` directory while maintaining the previous `db.json` safety net.
