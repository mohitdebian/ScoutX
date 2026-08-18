## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-08-10 - aiosqlite Connection Pool Bottleneck
**Learning:** Creating a new `aiosqlite.connect()` on every query causes massive overhead and can block the event loop under heavy load, degrading application performance.
**Action:** Implemented an `asyncio.Queue`-based connection pool. Acquired connections are borrowed via a context manager (`get_db_connection`) and returned (with rollback if in transaction) upon completion.
