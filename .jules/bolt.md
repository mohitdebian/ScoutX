## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.
## 2024-05-24 - Async SQLite Connection Pooling Pitfall
**Learning:** In an asynchronous application (using LangGraph/asyncio), sharing a single global `aiosqlite` connection object across the entire application breaks transaction isolation. A commit triggered by one asynchronous task will inadvertently commit any pending, uncommitted changes made by other concurrent tasks.
**Action:** Do not implement shared global connection singletons for `aiosqlite` in this architecture. Stick to query-specific optimizations like adding indexes (e.g., `idx_jobs_sort`) or use a proper async connection pool manager if connection overhead becomes a proven bottleneck.
