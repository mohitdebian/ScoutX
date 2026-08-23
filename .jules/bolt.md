## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.
## 2024-08-23 - Async SQLite Connection Overhead
**Learning:** Establishing a new `aiosqlite` connection on every single query (e.g., polling a queue frequently) creates significant overhead due to repeated file locking and initialization. Setting up `asyncio.Queue` based connection pool avoids this overhead.
**Action:** Always implement connection pooling with `get_db_connection` context managers instead of creating short-lived individual connections per query, and make sure `PRAGMA journal_mode=WAL;` is enabled to reduce lock contention.
