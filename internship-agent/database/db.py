import aiosqlite
import logging
import asyncio
import contextlib
from typing import Optional, List, Dict, Any
from config.settings import settings

logger = logging.getLogger(__name__)

DB_PATH = settings.database_url.replace("sqlite+aiosqlite:///", "")

SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    url TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    title TEXT NOT NULL,
    location TEXT,
    is_remote BOOLEAN,
    salary TEXT,
    apply_url TEXT UNIQUE NOT NULL,
    job_url TEXT,
    description TEXT,
    requirements TEXT,
    posting_date TEXT,
    match_score INTEGER,
    matched_skills TEXT,
    missing_skills TEXT,
    summary TEXT,
    status TEXT DEFAULT 'Found',
    date_found DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS visited_urls (
    url TEXT PRIMARY KEY,
    last_visited DATETIME DEFAULT CURRENT_TIMESTAMP,
    status_code INTEGER,
    etag TEXT,
    last_modified TEXT
);

CREATE TABLE IF NOT EXISTS crawl_queue (
    url TEXT PRIMARY KEY,
    source TEXT,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    priority INTEGER DEFAULT 0
);

-- Optimization: Index to speed up `ORDER BY priority DESC` in get_next_url()
CREATE INDEX IF NOT EXISTS idx_crawl_queue_priority ON crawl_queue(priority DESC);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    action TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS resume (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    skills TEXT,
    projects TEXT,
    technologies TEXT,
    experience TEXT,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""

async def init_db():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.executescript(SCHEMA)
            await db.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

_pool: Optional[asyncio.Queue] = None

async def init_db_pool(pool_size: int = 5):
    global _pool
    if _pool is None:
        _pool = asyncio.Queue(maxsize=pool_size)
        for _ in range(pool_size):
            conn = await aiosqlite.connect(DB_PATH)
            # Enable WAL mode and set a busy timeout to support concurrent writers and readers safely.
            await conn.execute("PRAGMA journal_mode=WAL;")
            await conn.execute("PRAGMA busy_timeout=5000;")
            await _pool.put(conn)

        # ⚡ Bolt Optimization: Replace recreating connections per-query with a persistent pool.
        # Expected Impact: Eliminates aiohttp+SQLite connection handshake overhead per query, reducing db latency and preventing event loop blocking.
        logger.info(f"Database connection pool initialized with {pool_size} connections.")

async def close_db_pool():
    global _pool
    if _pool is not None:
        while not _pool.empty():
            conn = await _pool.get()
            await conn.close()
        _pool = None
        logger.info("Database connection pool closed.")

@contextlib.asynccontextmanager
async def get_db_connection():
    global _pool
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")

    conn = await _pool.get()
    try:
        yield conn
    finally:
        if conn.in_transaction:
            await conn.rollback()
        await _pool.put(conn)

async def execute(query: str, parameters: tuple = ()) -> int:
    async with get_db_connection() as db:
        async with db.execute(query, parameters) as cursor:
            await db.commit()
            return cursor.lastrowid

async def execute_many(query: str, parameters: List[tuple]) -> None:
    async with get_db_connection() as db:
        await db.executemany(query, parameters)
        await db.commit()

async def fetch_one(query: str, parameters: tuple = ()) -> Optional[aiosqlite.Row]:
    async with get_db_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, parameters) as cursor:
            return await cursor.fetchone()

async def fetch_all(query: str, parameters: tuple = ()) -> List[aiosqlite.Row]:
    async with get_db_connection() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, parameters) as cursor:
            return await cursor.fetchall()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_db())
