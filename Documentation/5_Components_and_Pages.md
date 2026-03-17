# Components & Pages

The user interface spans several top-level logical flows isolated within `src/pages/` and leverages primitive re-usable building blocks present in `src/components/`.

## Application Architecture (`App.tsx` & Router)
The application acts precisely like a classic SPA, utilizing `react-router-dom` for component switching seamlessly without page reloads. The router incorporates a fundamental `<ProtectedRoutes />` component wrapper enforcing that URLs require an authenticated user; failing to comply redirects unauthenticated requests immediately to `<LoginPage />`.

## Key Pages
- **`DashboardPage`**: Display of high-level analytics, quick links to standard operations, and a summarized view of daily statistics relying on the database's `orders`.
- **`NewOrderPage`**: The primary point-of-sale terminal layout enabling adding, subtracting, and categorizing cart products, resulting in a finalized `addOrder` call.
- **`RegisterPage`**: Focuses heavily on managing the physical cash drawer state tracking deposits, withdrawals, and ending shifts.
- **`ProductsPage`**: CRUD operations on the stock items providing detailed table layouts to edit variables or trigger bulk stock resets.
- **`ReportsPage`**: Heavier analytical display that processes the entire global `db.orders` history and projects visualizations of cash inflow and product velocity over targeted bounds.

## Common Components
- **`Sidebar` & `Layout`**: Persisted navigational wrappers rendering available tabs based precisely on user permissions.
- **`Modal`**: Base backdrop and container mechanism to draw focus (used heavily by forms and detail pop-ups).
- **`PasswordConfirmDialog`**: A highly specialized security barrier. Tightly coupled with `src/hooks/usePasswordGate.ts` and `StoreSettings`, it prompts a modal intercepting specific functions unless matched against the executing `StoreUser`'s password.
- **`Chart` Components (e.g. `BarChart.tsx`)**: Renders internal statistical SVGs directly mapped to Report queries.
