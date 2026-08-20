## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.
## 2024-05-18 - aiosqlite connection bottleneck
**Learning:** Re-opening a new `aiosqlite.connect()` connection for every single database query creates a massive bottleneck for applications dealing with concurrent background execution (like the crawl/evaluate agents).
**Action:** Always implement an `asyncio.Queue`-based connection pool initialized within the active event loop for aiosqlite database access, and ensure connections are rolled back upon return.
