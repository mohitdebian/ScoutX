## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-05-18 - Async SQLite Connection Pooling
**Learning:** Initializing a new `aiosqlite.connect` connection for every single database operation introduces a significant performance bottleneck. When utilizing a shared connection object across concurrent tasks to fix this, it breaks transaction isolation.
**Action:** Implemented an `asyncio.Queue`-based connection pool via `get_db_connection` context manager, explicitly checking and rolling back dangling transactions (`if conn.in_transaction: await conn.rollback()`) to prevent dirty connection leaks. Also ensured `close_db_pool()` is called in the application shutdown flow to prevent event loop errors.
