## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-05-24 - aiosqlite Connection Pool for LangGraph Workers
**Learning:** Initializing new `aiosqlite` connections for every database query (like in `fetch_one` or `execute`) within highly concurrent workflows (like LangGraph agent nodes) creates immense overhead and risks database locking issues in SQLite. While async SQLite (`aiosqlite`) allows non-blocking DB calls, establishing connections is still expensive. In this specific app architecture, the agent triggers many rapid queries to save jobs and crawl queues.
**Action:** Implemented a connection pool using `asyncio.Queue` that initializes connections globally within the event loop (to avoid attachment errors). All connections execute `PRAGMA journal_mode=WAL;` and `PRAGMA busy_timeout=5000;` on startup to properly handle concurrent readers/writers. Rollbacks are safely caught in a `finally` block before returning to the pool.
