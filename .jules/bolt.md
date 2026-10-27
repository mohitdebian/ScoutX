## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2023-10-27 - [SQLite Connection Pool]
**Learning:** Creating a new `aiosqlite.connect()` connection per query in async applications incurs a large performance overhead, slowing down database-heavy operations.
**Action:** Use an `asyncio.Queue`-based connection pool globally to share active connections. When initializing connections in the pool, utilize `PRAGMA journal_mode=WAL;` and `PRAGMA busy_timeout=5000;` to significantly improve concurrency handling and reduce I/O wait times in SQLite.
