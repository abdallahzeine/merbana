# Merbana - System Overview

## Introduction
Merbana is a bespoke Point of Sale (POS) and Order Management System designed primarily for retail or food-service use. It enables store employees to manage products, accept daily orders, generate receipts, handle debtors, and track cash register details and business statistics.

## Technology Stack
The application is structured as a standalone desktop-like application using web technologies.

- **Frontend:**
  - React 19
  - Vite (for bundling and React Compiler setup)
  - TypeScript
  - TailwindCSS v4
  - React Router DOM v7
- **Backend / Container:**
  - Python 3
  - `http.server` (running locally via Python standard library)
  - `pywebview` (for creating a native desktop OS window wrapper without a heavy Electron dependency)
  - PyInstaller (for packaging the Python script into a standalone executable across Windows and Linux)

## Key Features
- **User Authentication:** Simple user switching mechanism to log activity accurately without complex cloud user accounts.
- **Order Management:** Takeaway or dine-in orders with dynamic product lookup and subtotal calculations.
- **Product & Stock Management:** Fully controlled inventory, daily stock resetting capabilities.
- **Cash Register:** Tracking of sales, deposits, withdrawals, and end-of-shift cash balancing.
- **Debtors Management:** Keep track of customers who owe money, track amounts, and mark them as paid.
- **Settings & Security:** Configure store policies, enforce passwords for sensitive actions (e.g., withdrawing cash, closing a shift).
- **Reports:** Generate daily, weekly, or specific custom timeframe reports for revenue and stats.

## Deployment Strategy
The system functions entirely offline on the local machine where it's deployed. A user simply runs a `.bat` launcher wrapper that executes a compiled standalone binary (e.g., `Merbana.exe` on Windows). The compiled binary then starts a local Python HTTP server instance, serves the React `dist/` folder, and opens a `pywebview` window pointing to localhost.
