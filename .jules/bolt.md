## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-08-19 - SQLite Connection Overhead & Pooling
**Learning:** Instantiating a new `aiosqlite.connect()` for every single query causes massive overhead, exhausting connections and increasing query latency, especially with LangGraph concurrent tasks.
**Action:** Implement an `asyncio.Queue`-based connection pool initialized lazily inside an active event loop, using `get_db_connection` context manager for reusing connections, checking `in_transaction` to prevent leaks, and ensuring graceful shutdown via `close_db_pool()`.
