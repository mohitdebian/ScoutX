## 2024-08-07 - SQLite Connection Overhead in Discovery Agent
**Learning:** Initial URL seeding via a loop calling `execute` internally opened and closed a new `aiosqlite` connection per URL. This repeated connection lifecycle introduced significant CPU overhead compared to a single batch insertion using `aiosqlite.Connection.executemany`.
**Action:** Always prefer batching inserts with `executemany` when inserting seed data or bulk lists into SQLite, and avoid connection cycling inside hot loops.
