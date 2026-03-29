# Performance Query Plans

## Environment

- Generated at: 2026-03-20T16:48:57Z
- Database path: C:\Users\abdallahzeine\Desktop\repo-kimi\data\merbana.db
- SQLite journal mode: wal

## Query Plan Evidence

| Query Key | Description | Plan Details |
|---|---|---|
| orders_date_range_desc | Orders filtered by date range and sorted descending | SEARCH orders USING INDEX ix_orders_date (date>? AND date<?) |
| orders_search_order_number | Orders search by order number text pattern | SCAN orders USING INDEX ix_orders_date |
| products_search_name_category | Product search by name wildcard and category filter | SCAN products USING INDEX ix_products_name |
| debtors_unpaid | Debtors unpaid filter sorted by created_at desc | SEARCH debtors USING INDEX ix_debtors_paid_at (paid_at=?)<br>USE TEMP B-TREE FOR ORDER BY |
| debtors_paid | Debtors paid filter sorted by created_at desc | SCAN debtors USING INDEX ix_debtors_created_at |
| activity_user_date_range | Activity logs filtered by user and date range | SEARCH activity_log USING INDEX ix_activity_log_timestamp (timestamp>? AND timestamp<?) |
| register_balance_python_equivalent | Register balance source scan used by current service path | SCAN cash_transactions |
| register_balance_sql_aggregate_candidate | Register balance SQL aggregate candidate for future optimization | SCAN cash_transactions |
| reports_daily_breakdown_server_candidate | Server-side daily breakdown candidate replacing client aggregation | SEARCH orders USING INDEX ix_orders_date (date>? AND date<?)<br>USE TEMP B-TREE FOR GROUP BY |

## Notes

- This report is observational for Task 8 and is not a release gate by default.
- Any FULL SCAN entries should be reviewed as optimization candidates in follow-up tasks.
