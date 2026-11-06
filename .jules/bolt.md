## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-11-06 - Lazy Instantiation of asyncio Primitives
**Learning:** In Python 3.10+, asyncio primitives like `asyncio.Queue()` must be instantiated lazily inside an active event loop (e.g., within an `async def` function) rather than at the module level. Initializing them at the module level causes event loop attachment errors because the primitive gets bound to a loop that isn't the one running the application.
**Action:** Always instantiate `asyncio.Queue`, `asyncio.Lock`, and similar primitives inside an asynchronous function or method (like a pool initialization function) that is guaranteed to be called from within the running event loop.
