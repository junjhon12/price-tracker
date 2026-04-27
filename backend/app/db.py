import os
import aiosqlite
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

# Vercel's filesystem is read-only except /tmp
DB_PATH = Path("/tmp/prices.db") if os.environ.get("VERCEL") else Path(__file__).parent.parent / "prices.db"


@asynccontextmanager
async def get_db() -> AsyncIterator[aiosqlite.Connection]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT,
                image_url TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS price_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                price REAL,
                scraped_at TEXT NOT NULL DEFAULT (datetime('now')),
                error TEXT
            )
        """)
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_price_points_item ON price_points(item_id, scraped_at)"
        )
        await db.commit()


async def insert_item(db: aiosqlite.Connection, url: str, title: str | None, image_url: str | None) -> int:
    cursor = await db.execute(
        "INSERT OR IGNORE INTO items (url, title, image_url) VALUES (?, ?, ?)",
        (url, title, image_url),
    )
    if cursor.lastrowid and cursor.lastrowid > 0:
        await db.commit()
        return cursor.lastrowid
    row = await db.execute_fetchall("SELECT id FROM items WHERE url = ?", (url,))
    return row[0]["id"]


async def update_item_meta(db: aiosqlite.Connection, item_id: int, title: str | None, image_url: str | None) -> None:
    await db.execute(
        "UPDATE items SET title = ?, image_url = ? WHERE id = ?",
        (title, image_url, item_id),
    )
    await db.commit()


async def insert_price_point(db: aiosqlite.Connection, item_id: int, price: float | None, error: str | None) -> None:
    await db.execute(
        "INSERT INTO price_points (item_id, price, error) VALUES (?, ?, ?)",
        (item_id, price, error),
    )
    await db.commit()


async def get_all_items(db: aiosqlite.Connection) -> list[dict]:
    rows = await db.execute_fetchall("""
        SELECT
            i.id, i.url, i.title, i.image_url, i.created_at,
            pp.price AS latest_price,
            pp.scraped_at AS latest_scraped_at,
            pp.error AS latest_error
        FROM items i
        LEFT JOIN price_points pp ON pp.id = (
            SELECT id FROM price_points
            WHERE item_id = i.id
            ORDER BY scraped_at DESC
            LIMIT 1
        )
        ORDER BY i.created_at DESC
    """)
    return [dict(r) for r in rows]


async def get_item_by_id(db: aiosqlite.Connection, item_id: int) -> dict | None:
    rows = await db.execute_fetchall("SELECT * FROM items WHERE id = ?", (item_id,))
    return dict(rows[0]) if rows else None


async def get_price_history(db: aiosqlite.Connection, item_id: int) -> list[dict]:
    rows = await db.execute_fetchall(
        "SELECT price, error, scraped_at FROM price_points WHERE item_id = ? ORDER BY scraped_at ASC",
        (item_id,),
    )
    return [dict(r) for r in rows]


async def get_all_item_ids(db: aiosqlite.Connection) -> list[int]:
    rows = await db.execute_fetchall("SELECT id FROM items ORDER BY id")
    return [r["id"] for r in rows]
