## 2024-08-09 - SQLite Queue Polling Bottleneck
**Learning:** Polling a queue in SQLite (`SELECT * FROM crawl_queue ORDER BY priority DESC LIMIT 1`) degrades severely as the table grows because it causes a full table scan and sort on every poll.
**Action:** Always verify that tables acting as queues have indexes on the columns used in their `ORDER BY` clauses to ensure O(1) lookups.

## 2024-05-24 - Hoisting List Allocations and String Operations
**Learning:** In Python, defining lists `["a", "b"]` inside a function body or performing invariant string operations like `.replace().split()` inside a loop causes memory allocation and computation on every execution. In high-throughput paths like crawler filters, this overhead becomes a measurable bottleneck.
**Action:** Always hoist invariant lists, tuples, and string derivations to module-level constants or pre-compute them during initialization.
