## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-05-24 - Async SQLite Connection Pooling
**Learning:** Using `aiosqlite.connect()` for every single query is slow (0.22s for 200 reads). Caching standard connections doesn't map well to concurrency. An `asyncio.Queue` based connection pool provides significantly faster throughput.
**Action:** Always wrap concurrent `aiosqlite` databases with a queue-based connection pool (`get_db_connection` async context manager) to maximize IO performance.
