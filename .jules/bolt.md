## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-08-09 - Asyncio SQLite Connection Pooling
**Learning:** Recreating `aiosqlite` connections on every database query is extremely slow and leaks connections over time under high concurrent loads. The application suffered significant overhead from redundant `aiosqlite.connect()` calls per operation.
**Action:** Use an `asyncio.Queue`-based connection pool globally to share connection objects. Always initialize the pool lazily inside an active event loop to prevent event loop attachment errors, and use `finally:` blocks (like in `get_db_connection()`) to handle cleanup and rollback dangling transactions.
