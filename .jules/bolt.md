## 2024-08-07 - SQLite Connection Overhead in Discovery Agent
**Learning:** Initial URL seeding via a loop calling `execute` internally opened and closed a new `aiosqlite` connection per URL. This repeated connection lifecycle introduced significant CPU overhead compared to a single batch insertion using `aiosqlite.Connection.executemany`.
**Action:** Always prefer batching inserts with `executemany` when inserting seed data or bulk lists into SQLite, and avoid connection cycling inside hot loops.

## 2026-08-08 - Missing SQLite Index on Priority Queue
**Learning:** The internship-agent codebase uses a SQLite table (`crawl_queue`) as a priority queue, constantly querying for the highest priority item (`SELECT url FROM crawl_queue ORDER BY priority DESC LIMIT 1`). Without an index on `priority`, SQLite performs a full table scan and sort on every fetch, which becomes a major bottleneck as the queue grows. Adding an index (`CREATE INDEX IF NOT EXISTS idx_crawl_queue_priority ON crawl_queue(priority DESC);`) reduced the query time by approximately 99%.
**Action:** When using a database table as a queue or constantly sorting by a specific field, always ensure that field is indexed appropriately to prevent full table scans.
