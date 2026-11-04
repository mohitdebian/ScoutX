## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-11-04 - SQLite Connection Pooling
**Learning:** Initializing an SQLite database object for every individual query is highly inefficient.
**Action:** Implement connection pooling (e.g., using `asyncio.Queue`) for SQLite to cache and reuse active connections. Avoid staging any `.db`, `*.pyc`, or temporary testing files when finalizing a pull request.
