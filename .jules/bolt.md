## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-11-05 - SQLite Connection Overhead
**Learning:** Recreating `aiosqlite.connect(DB_PATH)` for every database operation introduces significant latency (e.g., doubling the time taken for queries). Shared connections improve throughput dramatically.
**Action:** Use an `asyncio.Queue` connection pool to maintain and reuse a pool of database connections across concurrent tasks. Manage connections using context managers.
