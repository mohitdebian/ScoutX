## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2026-10-30 - aiosqlite Connection Pooling
**Learning:** Creating a new `aiosqlite.connect()` for every database operation introduces significant overhead due to file descriptor allocation and connection handshake latency, severely degrading throughput in a high-concurrency event loop.
**Action:** Implement an `asyncio.Queue`-based connection pool to reuse database connections across async tasks, ensuring the queue is initialized inside the active event loop to avoid attachment errors.
