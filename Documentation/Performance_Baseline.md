# Performance Baseline

## Environment

- Generated at: 2026-03-20T16:48:52Z
- Database path: C:\Users\abdallahzeine\Desktop\repo-kimi\data\merbana.db
- Journal mode: wal
- Dataset source: C:\Users\abdallahzeine\Desktop\repo-kimi\artifacts\benchmark_source_dataset.json
- Warm runs per scenario: 5
- Cold runs per scenario: 2

## Migration Throughput

- Duration: 3520.709 ms
- Command: C:\Users\abdallahzeine\Desktop\repo-kimi\.venv\Scripts\python.exe Deployment/migrate_json_to_sqlite.py --source C:\Users\abdallahzeine\Desktop\repo-kimi\artifacts\benchmark_source_dataset.json --overwrite

## API Latency (p50/p95)

| Scenario | Method | Warm p50 (ms) | Warm p95 (ms) | Cold p50 (ms) | Cold p95 (ms) |
|---|---|---:|---:|---:|---:|
| orders_list | GET | 3.415 | 7.633 | 3.834 | 4.135 |
| orders_date_range | GET | 3.834 | 29.212 | 3.989 | 3.992 |
| orders_search_order_number | GET | 3.746 | 5.71 | 4.54 | 4.687 |
| products_search_filter | GET | 1.95 | 3.773 | 2.457 | 2.462 |
| dashboard_inputs_register | GET | 8.045 | 41.638 | 8.72 | 9.174 |
| receipt_lookup | GET | 2.239 | 4.363 | 3.352 | 3.802 |
| debtors_unpaid | GET | 2.682 | 4.526 | 3.443 | 3.552 |
| activity_view | GET | 3.935 | 5.822 | 6.044 | 6.66 |
| order_create_write | POST | 4.49 | 7.742 | 7.871 | 9.968 |
| register_deposit_write | POST | 3.184 | 4.709 | 3.324 | 3.419 |
| register_withdrawal_write | POST | 8.873 | 9.49 | 29.574 | 47.822 |

## Notes

- This baseline is observational and intended for trend tracking.
- Known heavy paths should be tracked as optimization candidates in follow-up tasks.
