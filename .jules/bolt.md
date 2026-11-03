## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-05-19 - SQLite Connection Pooling with WAL
**Learning:** Establishing a new aiosqlite connection for every single database query incurs massive overhead, especially with high concurrency (e.g. from LangGraph nodes executing rapidly). While wrapping connection initialization with PRAGMAs can enable WAL mode, repeating it per query defeats the purpose and introduces event loop blocking and locking regressions.
**Action:** Always utilize an asynchronous connection pool (like via `asyncio.Queue`) initialized inside the event loop, and configure properties like `row_factory` and PRAGMAs globally once upon connection creation. Use `asyncio.shield` when returning connections to the pool on rollback to prevent deadlocks.
