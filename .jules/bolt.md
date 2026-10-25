## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-10-25 - SQLite Connection Pooling
**Learning:** Initializing a new `aiosqlite` connection on every query causes massive overhead and limits scalability in concurrent applications.
**Action:** Always use an `asyncio.Queue`-based connection pool for SQLite and ensure proper rollback and close operations during context exit and application shutdown.
