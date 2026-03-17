# Testing and Quality Assurance

Merbana incorporates a rigorous testing and linting environment to guarantee stability within its React codebase, emphasizing TypeScript strictness and automated unit testing rather than relying solely on manual testing.

## Unit Testing with Vitest
The application uses Vitest as its primary test runner (`vitest: "^4.0.18"`), configured inside `vite.config.ts` to run within a simulated Node environment.
- **Run Command:** `npm run test` or `npm run test:watch`.
- **Key Test Files:**
  - `database.test.ts`: Verifies the core logical functions of the in-memory database singleton (e.g., ensuring `addOrder` deducts stock accurately, calculating totals, or enforcing correct ID generation).
  - `database.persistence.test.ts`: Specifically targets the file saving operations to guarantee `persistToDisk()` triggers under the correct conditions without throwing unhandled exceptions.
  - `usePasswordGate.test.ts`: Validates the custom React hook responsible for security, ensuring sensitive actions are properly blocked when the `StoreSettings` require a password.

## Linting and Type Checking

### ESLint & Strict Type Checking
The project enforces strict, type-aware linting rules utilizing the new ESLint Flat Config (`eslint.config.js`). 
- It leverages `@typescript-eslint/recommended-type-checked` to analyze TypeScript paths (`tsconfig.node.json` and `tsconfig.app.json`).
- It extends specific React linting rules.
- **Run Command:** `npm run lint`.

### React Compiler
To automatically optimize rendering performance without requiring manual `useMemo` or `useCallback` implementations, the Vite build pipeline is configured with the experimental `babel-plugin-react-compiler`. This ensures the POS interface remains snappy even when dealing with massive order histories or complex product arrays.
