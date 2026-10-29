## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.
## 2023-10-27 - SQLite Connection Pool Event Loop Error
**Learning:** Instantiating `asyncio.Queue` for an `aiosqlite` connection pool at the module level in Python 3.10+ throws an error because there is no running event loop yet.
**Action:** Always instantiate `asyncio` primitives like `asyncio.Queue` lazily inside an `async def` function that is called after the event loop has started.
