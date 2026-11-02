## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-08-15 - SQLite Connection per Query Bottleneck
**Learning:** Opening a new `aiosqlite` connection per query causes severe performance issues in async applications due to context switching and filesystem locks. Additionally, initializing async primitives like `asyncio.Queue` globally causes "got Future <Future pending> attached to a different loop" errors if done outside an active event loop.
**Action:** Implement an `aiosqlite` connection pool using a lazily initialized `asyncio.Queue` (e.g. `init_pool()` inside the first `get_connection()` call). Ensure transactions are rolled back via `asyncio.shield(conn.rollback())` inside the `finally` block before returning connections to the queue. Ensure Graceful shutdown via `close_db_pool()`.
