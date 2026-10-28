## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-05-18 - Connection Pooling for SQLite in asyncio environments
**Learning:** Initializing a new `aiosqlite` connection on every query causes significant connection overhead and can break transaction isolation in concurrent environments. In an asyncio setup, utilizing an `asyncio.Queue`-based connection pool avoids this overhead. Additionally, setting properties like `conn.row_factory` at initialization rather than per-query limits state leakage.
**Action:** Always employ connection pooling with pre-configured connection attributes (like `PRAGMA journal_mode=WAL;` and row factories) when building asynchronous applications backed by SQLite, and make sure connections are gracefully closed during application shutdown to prevent event loop errors.
