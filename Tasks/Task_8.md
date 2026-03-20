# Task 8 - Performance Baseline

## Objective
Measure the real performance characteristics of the new backend and query paths using representative UI-driven workloads.

## Prerequisite
- [x] Task 7 integrity validation is complete.

## Codebase Anchors
- `src/pages/ReportsPage.tsx`
- `src/pages/OrdersPage.tsx`
- `src/pages/ProductsPage.tsx`
- `src/pages/DashboardPage.tsx`
- `src/utils/reportUtils.ts`

## Benchmark Rules
- [x] This task is observational, not a release gate by default, unless later release criteria adopt specific thresholds.
- [x] Benchmark the flows users actually trigger, not only isolated SQL statements.
- [x] Record environment, dataset size, and warm-vs-cold run conditions for every reported metric.

## Checklist
- [x] Identify top call patterns from current UI flows: orders list, reports filters, product search/filter, dashboard summaries, receipt lookup, and register views.
- [x] Map each call pattern to its replacement API route or backend service query.
- [x] Create tooling to generate a fixed benchmark dataset: 200 products, 1000 orders, 5000 activity-log entries, 1000 register transactions, 300 debtors.
- [x] Benchmark endpoints replacing heavy in-memory operations now done in reports/orders/dashboard pages.
- [x] Verify indexes with `EXPLAIN QUERY PLAN` for: orders by date range/date-desc sorting, order search by order number, product search by name/category filter, debtors paid/unpaid filtering, and any report query introduced in Task 3/4.
- [x] Confirm WAL mode is enabled and measure read/write behavior under realistic desktop usage patterns.
- [x] Measure migration-script insert throughput on the benchmark dataset.
- [x] Record p50/p95 latency for key reads and writes.
- [x] Record any query or endpoint that still performs large in-memory post-processing and decide whether it is acceptable, should move server-side, or needs future optimization.

## Acceptance Criteria
- [x] Benchmark results are reproducible with the documented dataset and environment.
- [x] Index usage claims are backed by query-plan evidence.
- [x] Known slow paths are identified with proposed next steps, even if not fixed in this phase.

## Deliverable
- [x] Performance baseline document with dataset definition, methodology, p50/p95 metrics, query plans, and optimization candidates.

## Implementation Notes
- Baseline was rerun after fixing orders search casting in `backend/routers/orders.py`, and the `orders_search_order_number` scenario now executes and reports p50/p95 like the rest of the suite.

## Library Choices with Justification
- `pytest-benchmark` for latency measurement because it provides repeatable timing statistics that are more trustworthy than ad-hoc manual timers.
- `Faker` for synthetic benchmark data generation because realistic varied records better approximate actual usage than hand-authored fixture sets.
- `sqlite3` from Python standard library for scripted `EXPLAIN QUERY PLAN` and DB inspection because the benchmark workflow should be automatable without a GUI tool such as DB Browser for SQLite.

## Concrete File/Folder Structure
- `Tasks/`
  - `Task_8.md` (modified)
- `Deployment/`
  - `backend/`
    - `benchmark/`
      - `__init__.py` (new)
      - `generate_dataset.py` (new)
      - `run_api_benchmarks.py` (new)
      - `query_plan_report.py` (new)
      - `benchmark_dataset_manifest.json` (new)
- `Documentation/`
  - `Performance_Baseline.md` (new)
  - `Performance_Query_Plans.md` (new)

## Architecture Decisions
- Chosen: benchmark real user flows and their backing routes. Rejected: benchmarking only isolated SQL statements. Why: the migration changes application behavior at the API and cache layers, not just inside SQLite.
- Chosen: a fixed generated dataset for reproducibility. Rejected: benchmarking against whatever local dev data happens to exist. Why: performance claims are not comparable without stable input sizes and shapes.
- Chosen: observational reporting with identified hot spots. Rejected: inventing hard thresholds before baseline data exists. Why: this phase is meant to establish evidence for later optimization decisions.
