## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2025-02-12 - aiosqlite Connection Pool Bottleneck
**Learning:** Initializing connections per-query dynamically breaks down heavily under load and leads to unshared SQLite connection states. Moreover, connections pool items must be managed safely through contexts (`try...finally` with shielded rollbacks) and properly shut down.
**Action:** Use an `asyncio.Queue` based connection pool initialized inside the event loop for `aiosqlite` and properly tear down the connections globally on application exit.
