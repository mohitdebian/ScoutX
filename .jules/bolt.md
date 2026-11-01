## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2023-10-27 - SQLite Connection Pooling in Asyncio
**Learning:** Instantiating `aiosqlite.connect()` per query generates massive overhead and risks running out of file descriptors, crippling async application performance.
**Action:** Implement an `asyncio.Queue`-based connection pool injected via an `asynccontextmanager` to reuse connections safely and minimize DB connection setup/teardown costs.
