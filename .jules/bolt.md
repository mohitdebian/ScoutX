## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-08-10 - Recreating SQLite Connections on Every Query
**Learning:** Recreating `aiosqlite` connections for every database query introduces massive overhead because of file lock and connection initialization delays. Using a single shared connection globally is bad for concurrency since it breaks transaction isolation.
**Action:** Implemented an `asyncio.Queue`-based connection pool for SQLite to reuse active connections while respecting concurrency constraints and transaction boundaries.
