## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-05-18 - aiosqlite Connection Pooling
**Learning:** Re-opening a new `aiosqlite` connection on every query introduces substantial overhead in SQLite-heavy applications. Using an `asyncio.Queue` as a connection pool significantly speeds up database interactions (measured a ~60% reduction in execution time for batches of simple queries). Also, we need to ensure local databases and `__pycache__` artifacts are not inadvertently committed.
**Action:** Implement connection pooling for `aiosqlite` instead of instantiating `aiosqlite.connect()` per query, and aggressively clean up temporary benchmarking and testing files.
