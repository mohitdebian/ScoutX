## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2023-10-26 - Implement Async Connection Pooling for SQLite
**Learning:** In heavily concurrent applications using async SQLite, creating a new connection for every query can lead to resource exhaustion, database locks, and performance bottlenecks, especially when crawling or processing many items simultaneously.
**Action:** Implemented an `asyncio.Queue` based connection pool in `database/db.py` to reuse connections. Used `PRAGMA journal_mode=WAL;` and `PRAGMA busy_timeout=5000;` on pool connections to handle concurrency properly. Ensured transactions are safely rolled back and connections are gracefully closed during shutdown to prevent event loop leaks.
