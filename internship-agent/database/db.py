import aiosqlite
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from config.settings import settings

logger = logging.getLogger(__name__)

DB_PATH = settings.database_url.replace("sqlite+aiosqlite:///", "")

_pool: Optional[asyncio.Queue] = None
_all_connections: List[aiosqlite.Connection] = []
POOL_SIZE = 5

async def init_pool():
    global _pool, _all_connections
    if _pool is not None:
        return
    _pool = asyncio.Queue(maxsize=POOL_SIZE)
    _all_connections = []
    for _ in range(POOL_SIZE):
        conn = await aiosqlite.connect(DB_PATH)
        await conn.execute("PRAGMA journal_mode=WAL;")
        await conn.execute("PRAGMA busy_timeout=5000;")
        conn.row_factory = aiosqlite.Row  # Global row factory for all connections
        await _pool.put(conn)
        _all_connections.append(conn)
    logger.info(f"Database connection pool initialized with {POOL_SIZE} connections.")

async def close_db_pool():
    global _pool, _all_connections
    if _pool is None:
        return
    for conn in _all_connections:
        await conn.close()
    _all_connections.clear()

    while not _pool.empty():
        _pool.get_nowait()
    _pool = None
    logger.info("Database connection pool closed.")

@asynccontextmanager
async def get_db_connection():
    global _pool
    if _pool is None:
        raise RuntimeError("Database pool is not initialized. Call init_pool() first.")

    conn = await _pool.get()
    try:
        yield conn
    finally:
        try:
            if conn.in_transaction:
                # Use shield to ensure rollback completes even if task is cancelled
                await asyncio.shield(conn.rollback())
        except asyncio.CancelledError:
            pass # Suppress CancelledError here to ensure connection is returned
        finally:
            # Use put_nowait to ensure return even during cancellation
            _pool.put_nowait(conn)

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
        async with get_db_connection() as db:
            await db.executescript(SCHEMA)
            await db.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

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
        async with db.execute(query, parameters) as cursor:
            return await cursor.fetchone()

async def fetch_all(query: str, parameters: tuple = ()) -> List[aiosqlite.Row]:
    async with get_db_connection() as db:
        async with db.execute(query, parameters) as cursor:
            return await cursor.fetchall()

async def _main():
    await init_pool()
    await init_db()
    await close_db_pool()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(_main())
